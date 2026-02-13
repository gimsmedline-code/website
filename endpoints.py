from collections import defaultdict
from locale import normalize
import traceback

import pytz
from app.dependencies import get_metadata_manager
from app.service.impl.emp_clearance import EmployeeClearanceComplianceServiceImpl
from app.service.impl.emp_credential import EmployeeCredentialComplianceServiceImpl
from app.service.impl.emp_equalification import EmployeeQualificationComplianceServiceImpl
from app.service.impl.employee_service_impl import EmployeeServiceImpl
from app.utils.chain_of_thoughts import PROCESS_CLIENT
from app.utils.dynamic_query_builder.empcredential import EmpCredentialQueryBuilder
from app.utils.dynamic_query_builder.empclearance import EmpClearanceTypeQueryBuilder
from app.utils.dynamic_query_builder.employee_details import EmployeeInfo
from app.service.impl.availability_service_impl import AvailabilityServiceImpl
from app.utils.dynamic_query_builder.empqualification import EmpQualificationTypeQueryBuilder
from app.utils.dynamic_query_builder.excluded_employee import ExcludedEmployeeQueryBuilder
from app.utils.dynamic_query_builder.validate_treatement_team import ValidateTreatmentTeamQueryBuilder
from fastapi import HTTPException
from app.utils.dynamic_query_builder.common_location import CommonLocationQueryBuilder
import aiohttp
import Levenshtein
import json
from datetime import timedelta
from dateutil.parser import isoparse
import asyncio
from fastapi import BackgroundTasks
import datetime
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from rapidfuzz import fuzz
import socketio
from app.config.logger_config import logger
from app.app import ContinueException
from app.config.redis_configuration import redis_client
from app.database.manager import DatabaseManager
from app.exceptions.continue_exception import ContinueException 
from app.utils.data_filtering import Datafilter
from app.utils.dynamic_query_builder.auth_detail_with_service import AuthDetailWithServiceQueryBuilder
from app.utils.dynamic_query_builder.client_id_with_details import PatientDetailQueryBuilder
from app.utils.trigger_model import TriggerModel
from app.config.json_configuration import prompt
from app.utils.dynamic_query_builder.search_patients import SearchPatients
from app.utils.dynamic_query_builder.patient_location_detail import PatientLocationQueryBuilder
from app.config.env_configuration import settings
from typing import List, Dict
from app.config.database_config import db_config
from app.utils.summarization import get_friendly_client_message, get_friendly_service_message,get_friendly_location_message
MAX_RETRIES = 5

@dataclass
class APIResponse:
    """Standard response wrapper for API calls"""
    success: bool
    data: Optional[Dict[Any, Any]]
    status_code: int
    error: Optional[str] = None

class MeasurePMAsyncClient:
    """Async client for MeasurePM API operations"""
    
    def __init__(self, 
                 ai_support_base_url: str = "https://mpmbusinessstest.measurepm.com",
                 sessionId: Optional[str] = None,
                 db_manager: Optional[DatabaseManager] = None,
                 token: Optional[str] = None,
                 user_query: Optional[str] = None):
        self.sio: Optional[socketio.AsyncServer] = None
        self.ai_support_base_url = ai_support_base_url.rstrip('/')
        self.token: Optional[str] = token
        self.session: Optional[aiohttp.ClientSession] = None
        self.sessionId: Optional[str] = sessionId
        self.db_manager: Optional[DatabaseManager] = db_manager
        self.background_tasks: Optional[BackgroundTasks] = BackgroundTasks
        self.user_query = user_query
        self.metadata = None
        self.redis_client = redis_client
        self.siteid = None
        self.weight = settings.weights
        self.database_name = db_config.database
        self.range = settings.max_range
        self.min_range = settings.min_range
        self.weights = None
        self.function = None
        self.sid = None

    def setdb_instance(self, db_manager: DatabaseManager):
        """Set the database manager instance for dependency injection"""
        self.db_manager = db_manager

    async def _emit_and_cache(self, event_suffix: str, payload: Any):
        """
        Emits a socket event and simultaneously appends it to a Redis List
        for potential recovery of ALL missed steps (Chain of Thought + Results).
        """
        event_name = f"{self.sessionId}_{event_suffix}"
        
        # Ensure payload is a dictionary so we can add msg_index.
        # If it's a string or other primitive, wrap it.
        if not isinstance(payload, dict):
            payload = {"content": payload}
        
        # 1. Caching in Redis List (Queue Mode)
        try:
            # We use a List to preserve the order of multiple missed messages
            redis_key = f"pending_messages:{self.sessionId}"
            
            # Get current length to determine the index of the new message
            msg_index = redis_client.llen(redis_key)
            
            # Add index to payload so the frontend can track progress
            payload["msg_index"] = msg_index

            cache_data = {
                "event": event_name,
                "payload": payload
            }
            # Append to the end of the list
            redis_client.rpush(redis_key, json.dumps(cache_data))
            # Set/Update expiration to 15 minutes
            redis_client.expire(redis_key, 900)
            logger.info("Message appended to Redis queue for session %s (index: %d, event: %s)", self.sessionId, msg_index, event_name)
        except Exception as e:
            logger.error("Failed to queue result in Redis: %s", e)

        # 2. Real-time emit
        if self.sio:
            try:
                await self.sio.emit(event_name, payload, to=self.sessionId)
                logger.info("Real-time emit successful for event: %s", event_name)
            except Exception as e:
                logger.error("Real-time emit failed for event %s: %s", event_name, e)
        else:
            logger.warning("SocketIO server not available for real-time emit of %s", event_name)
        

    async def get_employee_credentials(
        self,
        employee_list_with_service_suggestion,
        start_date,
        metadata,
        database
    ):
        """
        Retrieve all employee credentials, qualifications, and clearances.

        Parameters:
            employee_list_with_service_suggestion (List[Dict[str, Any]]): List of employee objects with service suggestions
            start_date (Union[datetime, date, str]): Start date for the employee credentials
            metadata (Dict[str, Any]): Metadata for the request
            database (str): Database name

        Returns:
            List[Dict[str, Any]]: List of employee objects with credentials, qualifications, and clearances
        """
        try:
            employee_ids = [
                emp["EmployeeId"]
                for emp in employee_list_with_service_suggestion
                if emp.get("EmployeeId") is not None
            ]

            emp_id_list = [int(eid) for eid in employee_ids if str(eid).isdigit()]
            logger.info("Employee IDs: %s", emp_id_list)


            if isinstance(start_date, (datetime, date)):
                start_date = start_date.strftime("%Y-%m-%d")
            else:
                start_date = datetime.fromisoformat(str(start_date)).strftime("%Y-%m-%d")

            service_id = metadata.get("service_id")

            qualification_service = EmployeeQualificationComplianceServiceImpl()
            credential_service = EmployeeCredentialComplianceServiceImpl()
            clearance_service = EmployeeClearanceComplianceServiceImpl()

            clearance_result, credential_result, qualification_result = await asyncio.gather(
                clearance_service.process_employee_clearance_compliance(
                    emp_id_list, start_date, service_id, database
                ),
                credential_service.process_employee_credential_compliance(
                    emp_id_list, start_date, service_id, database
                ),
                qualification_service.process_employee_qualification_compliance(
                    emp_id_list, start_date, service_id, database
                ),
            )

            clearance_dict = defaultdict(list)
            for c in clearance_result or []:
                clearance_dict[str(c["EmployeeID"])].append({
                    "id": c.get("EmpClearanceTypeId", "None"),
                    "name": c.get("ClearanceName", "None"),
                    "billrateid": c.get("BillRateID", "None"),
                    "cptserviceid": c.get("CptServiceCodeId", "None"),
                })

            credential_dict = defaultdict(list)
            for c in credential_result or []:
                credential_dict[str(c["EmployeeID"])].append({
                    "id": c.get("EmpCredentialTypeId", "None"),
                    "name": c.get("CredentialName", "None"),
                    "billrateid": c.get("BillRateID", "None"),
                    "cptserviceid": c.get("CptServiceCodeId", "None"),
                })

            qualification_dict = defaultdict(list)
            for q in qualification_result or []:
                qualification_dict[str(q["EmployeeID"])].append({
                    "id": q.get("EmpQualificationTypeId", "None"),
                    "name": q.get("QualificationName", "None"),
                    "billrateid": q.get("BillRateID", "None"),
                    "cptserviceid": q.get("CptServiceCodeId", "None"),
                })


            merged_employees = []

            for e in employee_list_with_service_suggestion:
                emp_id_str = str(e["EmployeeId"])

                merged_employees.append({
                    **e,
                    "Clearance": clearance_dict.get(emp_id_str, []),
                    "Credential": credential_dict.get(emp_id_str, []),
                    "Qualification": qualification_dict.get(emp_id_str, []),
                })

            logger.info(
                "Merged employee credentials, qualifications, and clearances: %s",
                merged_employees
            )

            return merged_employees
        except Exception as e:
            logger.exception("Error in get_employee_credentials: %s", e)
            await self._emit_and_cache(
                    "final_suggestion_provider",
                    {
                        "content": "An unexpected error occurred while fetching employee credentials. Please try again later.",
                        "response": None,
                        "tag_name": "error",    
                    })

        
    async def fuzzy_string_compare(self, str1, str2, threshold=0.9):
        """
        Compare two strings with minor typos, case differences, and extra spaces.
        
        Parameters:
            str1, str2 (str): Strings to compare
            threshold (float): Similarity threshold (0 to 1)
            
        Returns:
            bool: True if strings are similar enough, False otherwise
        """
        if not str1 or not str2:
            return False
        def normalize(s):
            return ' '.join(s.lower().strip().split())
        
        s1 = normalize(str1)
        s2 = normalize(str2)
        
        similarity = Levenshtein.ratio(s1, s2)
        
        return similarity >= threshold

    async def get_Exclusion_employee_id(self, metadata: dict, employees_in_service):
        try:
            service_id = metadata.get("service_id")
            auth_id = metadata.get("auth_id")
            patient_id = metadata.get("client_id")
            excluded_patient_emp = metadata.get("excluded_employees") or []

            logger.info(
                "Fetching exclusion employees for service_id=%s, auth_id=%s, patient_id=%s",
                service_id, auth_id, patient_id
            )

            # Safety fallback
            if not service_id or not auth_id or not patient_id:
                logger.warning("Missing exclusion metadata. Returning original employee list.")
                return employees_in_service

            exclusion_employee = ExcludedEmployeeQueryBuilder()
            employee_exclusion_sql = exclusion_employee.get_excluded_employees(
                service_type_id=service_id,
                auth_id=auth_id,
                patient_id=patient_id,
                database=self.database_name
            )

            employee_exclusion_result = await self.db_manager.execute_query(
                query=employee_exclusion_sql
            )

            # 🔑 FIX: extract EmployeeId values from DB result
            db_excluded = {
                row["EmployeeId"]
                for row in (employee_exclusion_result.data or [])
                if "EmployeeId" in row
            }

            metadata_excluded = set(excluded_patient_emp)

            all_excluded = db_excluded | metadata_excluded

            logger.info("Excluded employees from DB (IDs): %s", db_excluded)
            logger.info("Excluded employees from metadata (IDs): %s", metadata_excluded)
            logger.info("All excluded employees: %s", all_excluded)

            filtered_ids = [
                emp_id for emp_id in employees_in_service
                if emp_id not in all_excluded
            ]

            logger.info("Filtered employees after exclusion: %s", filtered_ids)

            return filtered_ids    
        except Exception as e:
            await self._emit_and_cache(
                    "final_suggestion_provider",
                    {
                        "content": "An unexpected error occurred while fetching data. Please try again later.",
                        "response": None,
                        "followedBy": self.function,
                        "tag_name": "error",    
                    })
            
    async def get_client_id(
        self,
        metadata: dict,
        client_name: str,
        selected_client: Optional[str] = None,
        user_message: Optional[str] = None
    ) -> Optional[int]:
        """
        Fetch the client ID from the database based on the client name provided.
        """
        try:
            if selected_client:
                logger.info("selected_client provided: %s", selected_client)
                client_data = Datafilter.split_string(selected_client)
                metadata["client_name"] = client_data.get("field_2")
                metadata["client_id"] = client_data.get("field_1")

                self.metadata.write_metadata(session_id=self.sessionId, data=metadata)

                logger.info(
                    "Selected client used. Client name: %s, Client ID: %s",
                    metadata["client_name"],
                    metadata["client_id"]
                )
                selected_client_string = f"{metadata['client_id']}|{metadata['client_name']}"
                return metadata["client_id"], selected_client_string

            await self._emit_and_cache(
                "process",
                PROCESS_CLIENT["get_client_id"]
            )

            if user_message:
                client_name = user_message
                logger.info("client_name overridden by user_message: %s", client_name)

            if (
                metadata.get("client_id") is not None
                and fuzz.WRatio(metadata.get("client_name"), client_name) >= 90
            ):
                logger.info(
                    "Client ID %s found in metadata for client name '%s'",
                    metadata["client_id"],
                    client_name
                )
                selected_client_string = f"{metadata['client_id']}|{metadata['client_name']}"
                return metadata["client_id"], selected_client_string

            search_client = SearchPatients()
            sql = search_client.search_patient_name(
                site_id=metadata.get("siteId"),
                search_name=client_name
            )
            logger.info("Generated SQL for client search: %s", sql)

            query_result = await self.db_manager.execute_query(query=sql)
            filtered_names = query_result.data

            def normalize_name(name: Optional[str]) -> str:
                return " ".join(name.split()).lower() if name else ""

            def calculate_max_score(client, search_name: str) -> int:
                scores = []
                if client.get("FirstName"):
                    scores.append(fuzz.token_sort_ratio(normalize_name(client["FirstName"]), search_name))
                if client.get("MiddleName"):
                    scores.append(fuzz.token_sort_ratio(normalize_name(client["MiddleName"]), search_name))
                if client.get("LastName"):
                    scores.append(fuzz.token_sort_ratio(normalize_name(client["LastName"]), search_name))
                if client.get("fullName"):
                    scores.append(fuzz.token_sort_ratio(normalize_name(client["fullName"]), search_name))
                return max(scores) if scores else 0

            search_normalized = normalize_name(client_name)
            results = [
                client for client in filtered_names
                if calculate_max_score(client, search_normalized) >= 85
            ]

            if not results:
                await self._emit_and_cache(
                    "client_name",
                    {
                        "content": f"No Clients found with name: {client_name}",
                        "response": None,
                        "final_response": "False", 
                        "followedBy": self.function
                    }
                )
                raise ContinueException(
                    content=f"No Clients found with name: {client_name}",
                    response=None
                )

            if len(results) > 1:
                client_name_merger = Datafilter(filtered_items=results)
                new_client_list = client_name_merger.merge_keys(
                    ["PatientId", "fullName"],
                    merged_key="nameWithPatientId"
                )
                similar_client_names = [
                    item["nameWithPatientId"] for item in new_client_list
                ]

                redis_message_key = f"{self.sessionId}_assistant_message"
                try:
                    cached_message = self.redis_client.get(redis_message_key)
                    if isinstance(cached_message, bytes):
                        cached_message = cached_message.decode("utf-8")
                except Exception as e:
                    logger.warning("Redis fetch failed: %s", e)
                    cached_message = None

                friendly_message = cached_message or get_friendly_client_message(
                    len(similar_client_names)
                )

                if cached_message:
                    try:
                        self.redis_client.delete(redis_message_key)
                    except Exception as e:
                        logger.warning("Redis delete failed: %s", e)

                await self._emit_and_cache(
                    "client_name",
                    {
                        "content": friendly_message,
                        "response": similar_client_names,
                        "tag_name": "selected_client",
                        "followedBy": self.function,
                        "final_response": "False"
                    }
                )
                raise ContinueException(
                    content=friendly_message,
                    response=similar_client_names,
                    tag_name="selected_client"
                )

            patient_id = results[0]["PatientId"]
            metadata["client_name"] = user_message or client_name
            metadata["client_id"] = patient_id
            metadata["patient_name"] = results[0]["fullName"]
            self.metadata.write_metadata(session_id=self.sessionId, data=metadata)

            selected_client_string = f"{patient_id}|{client_name}"
            return patient_id, selected_client_string

        except ContinueException:
            raise

        except Exception as e:
            # 🔥 DO NOT treat ContinueException as an error
            if isinstance(e, ContinueException):
                raise

            logger.exception(
                "Unexpected error in get_client_id | session=%s | client_name=%s",
                self.sessionId,
                client_name
            )

            await self._emit_and_cache(
                "client_name",
                {
                    "content": "Something went wrong while fetching client details. Please try again.",
                    "response": None,
                    "final_response": "False",
                    "followedBy": self.function
                }
            )

            raise ContinueException(
                content="Error occurred while fetching client details.",
                response=None
            )


    async def process_auth_and_service(
            self,
            metadata: dict,
            authorisation: Optional[str] = None,
            service_type: Optional[str] = None,
            selected_auth: Optional[str] = None,
            selected_service: Optional[str] = None,
            start_date: Optional[str] = None,
            selected_client: Optional[str] = None, 
            user_service_name: Optional[str] = None
        ):
            """
                Process the authorization and service selection for a client.

                Args:
                    metadata (dict): Metadata containing client_id
                    authorisation (str): Authorization name
                    service_type (str): Service type name
                    selected_auth (str): Selected authorization name
                    selected_service (str): Selected service name
                    start_date (str): Start date string in %Y-%m-%d format
                    selected_client (str): Selected client name
                    user_service_name (str): User-typed service name

                Returns:
                    dict: Metadata containing authorization and service information
                """  
           
            try: 
                client_name = metadata.get("client_name")
                logger.info("client name in process_auth_and_service: %s", client_name)
                #  Fetch authorization + service data
                logger.info("Start date for auth/service fetch: %s", start_date)
                auth_and_service = await self.fetch_auth_service_list(metadata, start_date)
                if not auth_and_service:
                    await self._emit_and_cache(
                        "auth_service",
                        {
                            "content": f"No Authorizations found for {client_name}.",
                            "response": None,
                            "final_response": "False", 
                            "followedBy": self.function, 
                            "selected_client": selected_client
                        }
                    )
                    raise ContinueException(content="No Authorizations found for this client.", response=None)

                # Build mapping authId -> auth/description/services
                auth_map: Dict[Any, Dict[str, Any]] = {}
                for item in auth_and_service:
                    aid = item.get("AuthId")
                    if aid not in auth_map:
                        auth_map[aid] = {
                            "auth": item.get("auth"),
                            "description": item.get("Description") or item.get("description"),
                            "services": []
                        }

                    svc_id = item.get("ServiceTypeId")
                    svc_name = item.get("serviceList")
                    auth_detail_id = item.get("AuthDetailId")
                    treatmentType = item.get("TreatmentTypeDesc")
                    sub_svc_id = item.get("ServiceSubTypeId")
                    sub_svc_name = item.get("servicetype")

                    if svc_id and svc_name:
                        service_entry = {
                            "id": svc_id,
                            "name": svc_name,
                            "auth_detail_id": auth_detail_id,
                            "treatmentType": treatmentType,
                            "sub_service_id": sub_svc_id,
                            "sub_service_name": sub_svc_name,
                            "CptServiceCodeId": item.get("CptServiceCodeId")  ,
                            "fundingscoreid": item.get("FundingScore")
                        }

                        existing_service = next(
                            (s for s in auth_map[aid]["services"]
                                if s["id"] == svc_id and s["auth_detail_id"] == auth_detail_id),
                            None
                        )
                        if not existing_service:
                            auth_map[aid]["services"].append(service_entry)

                # 3️⃣ If user already selected a specific service (dropdown selection)
                if selected_service and "|" in selected_service:
                    try:
                        parts = selected_service.split("|")
                        if len(parts) == 2:
                            auth_id = int(parts[0])
                            service_id = int(parts[1])
                            auth_detail_id = None
                        elif len(parts) == 3:
                            auth_id = int(parts[0])
                            service_id = int(parts[1])
                            auth_detail_id = int(parts[2])
                        else:
                            raise ValueError("Invalid format")
                    except Exception:
                        raise ContinueException(
                            content=f"Invalid service selection format: {selected_service}",
                            response=None
                        )

                    if auth_id not in auth_map:
                        await self._emit_and_cache(
                            "auth_service",
                            {
                                "content": f"No authorization found with ID {auth_id}",
                                "response": None,
                                "final_response": "False", 
                                "followedBy": self.function, 
                                "selected_client": selected_client
                            }
                        )
                        raise ContinueException(
                            content=f"No authorization found with ID {auth_id}.",
                            response=None
                        )

                    service_obj = next(
                        (s for s in auth_map[auth_id]["services"]
                            if s["id"] == service_id and (auth_detail_id is None or s["auth_detail_id"] == auth_detail_id)),
                        None
                    )
                    if not service_obj:
                        available_services = [s["name"] for s in auth_map[auth_id]["services"]]
                        await self._emit_and_cache(
                            "auth_service",
                            {
                                "content": f"No service found under the selected authorization. Available Services: {available_services}",
                                "response": None,
                                "final_response": "False", 
                                "followedBy": self.function, 
                                "selected_client": selected_client
                            }
                        )
                        raise ContinueException(
                            content=f"No service found under the selected authorization. Available Services: {available_services}",
                            response=None
                        )

                    metadata.update({
                        "auth_id": auth_id,
                        "auth_name": auth_map[auth_id]["auth"],
                        "service_id": service_obj["id"],
                        "service_name": service_obj["name"],
                        "auth_detail_id": service_obj["auth_detail_id"],
                        "treatmentType": service_obj["treatmentType"],
                        "sub_service_id": service_obj.get("sub_service_id"),
                        "sub_service_name": service_obj.get("sub_service_name"),
                        "CptServiceCodeId": service_obj.get("CptServiceCodeId") , 
                        "fundingscoreid": service_obj.get("fundingscoreid")
                    })
                    self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
                    logger.info(
                        "✅ Flattened selection parsed and stored: auth_id=%s, service_id=%s, auth_detail_id=%s",
                        auth_id, service_id, auth_detail_id
                    )
                    selected_service_value = f"{auth_id}|{service_obj['id']}|{service_obj['auth_detail_id']}"
                    metadata["selected_service"] = selected_service_value
                    return metadata, selected_service_value
                
                patient_name = metadata.get("patient_name") or metadata.get("client_name")
                message = f"Fetching authentication and service details for {patient_name}"

                await self._emit_and_cache(
                    "process",
                    message
                )
                

                # 4️⃣ User typed service name (user_service_name)
                if user_service_name:
                    logger.debug("user_service_name provided: %s", user_service_name)
                    normalized_input = normalize(user_service_name)
                    all_services = [
                        {**s, "AuthId": aid, "AuthName": info["auth"]}
                        for aid, info in auth_map.items()
                        for s in info.get("services", [])
                    ]

                    # Exact match
                    exact_matches = [
                        s for s in all_services
                        if normalize(s["sub_service_name"]) == normalized_input
                    ]

                    if len(exact_matches) == 1:
                        svc = exact_matches[0]
                        aid = svc["AuthId"]
                        selected_service_value = f"{aid}|{svc['id']}|{svc['auth_detail_id']}"
                        
                        metadata.update({
                            "auth_id": aid,
                            "auth_name": auth_map[aid]["auth"],
                            "service_id": svc["id"],
                            "service_name": svc["name"],
                            "auth_detail_id": svc["auth_detail_id"],
                            "treatmentType": svc["treatmentType"],
                            "sub_service_id": svc["sub_service_id"],
                            "sub_service_name": svc["sub_service_name"],
                            "selected_service": selected_service_value,
                            "CptServiceCodeId": svc.get("CptServiceCodeId") ,
                            "fundingscoreid": svc.get("fundingscoreid") 
                        })
                        self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
                        return metadata , selected_service_value

                    # Fuzzy match
                    fuzzy_matches = [
                        s for s in all_services
                        if await self.fuzzy_string_compare(normalized_input,
                                                        normalize(s["sub_service_name"]),
                                                        threshold=0.7)
                    ]

                    if fuzzy_matches:
                        if len(fuzzy_matches) == 1:
                            svc = fuzzy_matches[0]
                            aid = svc["AuthId"]
                            selected_service_value = f"{aid}|{svc['id']}|{svc['auth_detail_id']}"
                            metadata.update({
                                "auth_id": aid,
                                "auth_name": auth_map[aid]["auth"],
                                "service_id": svc["id"],
                                "service_name": svc["name"],
                                "auth_detail_id": svc["auth_detail_id"],
                                "treatmentType": svc["treatmentType"],
                                "sub_service_id": svc["sub_service_id"],
                                "sub_service_name": svc["sub_service_name"],
                                "selected_service": selected_service_value,
                                "CptServiceCodeId": svc.get("CptServiceCodeId") ,
                                "fundingscoreid": svc.get("fundingscoreid")
                            })
                            self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
                            return metadata, selected_service_value

                        # Multiple fuzzy → ask user to select
                        response = [
                            {
                                "name": f"{svc['AuthName']} => {svc['name']}",
                                "value": f"{svc['AuthId']}|{svc['id']}|{svc['auth_detail_id']}",
                                "authId": svc['AuthId']
                            }
                            for svc in fuzzy_matches
                        ]
                        unique_values = {item["value"] for item in response}
                        length_of_auth_service_response = len(unique_values)

                        redis_message_key = f"{self.sessionId}_assistant_message"
                        cached_message = None

                        try:
                            cached_message = self.redis_client.get(redis_message_key)
                        except Exception as e:
                            logger.warning(
                                "Failed to fetch message from Redis key %s: %s",
                                redis_message_key,
                                e
                            )

                        if cached_message:
                            # Decode if Redis returns bytes
                            if isinstance(cached_message, bytes):
                                cached_message = cached_message.decode("utf-8")

                            friendly_message = cached_message
                            logger.info("Using cached message from Redis for client selection")

                            # ✅ DELETE after consuming
                            try:
                                self.redis_client.delete(redis_message_key)
                                logger.debug("Deleted Redis key after consumption: %s", redis_message_key)
                            except Exception as e:
                                logger.warning(
                                    "Failed to delete Redis key %s after consumption: %s",
                                    redis_message_key,
                                    e
                                )

                        else:
                            logger.info("Generated new message for client selection (Redis was empty)")
                            friendly_message = get_friendly_service_message(
                                length_of_auth_service_response
                            )

                        await self._emit_and_cache(
                            "auth_service",
                            {
                                "content": friendly_message,
                                "response": response,
                                "tag_name": "selected_service",
                                "selected_client": selected_client,
                                "followedBy": self.function,
                                "must_select": "True",
                                "client_name": client_name,
                                "final_response": "False"
                            }
                        )

                        raise ContinueException(
                            content=friendly_message,
                            response=response,
                            tag_name="selected_service"
                        )

                # 5️⃣ Auto-matching logic based on service_type
                if service_type:
                    normalized_input = normalize(service_type)

                    all_services = [
                        {**s, "AuthId": aid, "AuthName": info["auth"]}
                        for aid, info in auth_map.items()
                        for s in info.get("services", [])
                    ]

                    exact_matches = [
                        s for s in all_services
                        if normalize(s["sub_service_name"]) == normalized_input
                    ]

                    if len(exact_matches) == 1:
                        svc = exact_matches[0]
                        aid = svc["AuthId"]
                        selected_service_value = f"{aid}|{svc['id']}|{svc['auth_detail_id']}"
                        metadata["selected_service"] = selected_service_value

                        metadata.update({
                            "auth_id": aid,
                            "auth_name": auth_map[aid]["auth"],
                            "service_id": svc["id"],
                            "service_name": svc["name"],
                            "auth_detail_id": svc["auth_detail_id"],
                            "treatmentType": svc["treatmentType"],
                            "sub_service_id": svc["sub_service_id"],
                            "sub_service_name": svc["sub_service_name"],
                            "CptServiceCodeId": svc.get("CptServiceCodeId"),
                            "fundingscoreid": svc.get("fundingscoreid")
                        })
                        self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
                        return metadata, selected_service_value 

                    fuzzy_matches = [
                        s for s in all_services
                        if await self.fuzzy_string_compare(normalized_input,
                                                        normalize(s["sub_service_name"]),
                                                        threshold=0.7)
                    ]

                    if fuzzy_matches:
                        if len(fuzzy_matches) == 1:
                            svc = fuzzy_matches[0]
                            aid = svc["AuthId"]
                            selected_service_value = f"{aid}|{svc['id']}|{svc['auth_detail_id']}"
                            metadata["selected_service"] = selected_service_value

                            metadata.update({
                                "auth_id": aid,
                                "auth_name": auth_map[aid]["auth"],
                                "service_id": svc["id"],
                                "service_name": svc["name"],
                                "auth_detail_id": svc["auth_detail_id"],
                                "treatmentType": svc["treatmentType"],
                                "sub_service_id": svc["sub_service_id"],
                                "sub_service_name": svc["sub_service_name"],
                                "CptServiceCodeId": svc.get("CptServiceCodeId"),
                                "fundingscoreid": svc.get("fundingscoreid")
                            })
                            self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
                            return metadata, selected_service_value

                        # Multiple fuzzy matched services
                        response = [
                            {
                                "name": f"{svc['AuthName']} => {svc['name']}",
                                "value": f"{svc['AuthId']}|{svc['id']}|{svc['auth_detail_id']}",
                                "authId": svc['AuthId']
                            }
                            for svc in fuzzy_matches
                        ]

                        unique_values = {item["value"] for item in response}
                        length_of_auth_service_response = len(unique_values)

                        redis_message_key = f"{self.sessionId}_assistant_message"
                        cached_message = None

                        try:
                            cached_message = self.redis_client.get(redis_message_key)
                        except Exception as e:
                            logger.warning(
                                "Failed to fetch message from Redis key %s: %s",
                                redis_message_key,
                                e
                            )

                        if cached_message:
                            # Decode if Redis returns bytes
                            if isinstance(cached_message, bytes):
                                cached_message = cached_message.decode("utf-8")

                            friendly_message = cached_message
                            logger.info("Using cached message from Redis for client selection")

                            # ✅ DELETE after consuming
                            try:
                                self.redis_client.delete(redis_message_key)
                                logger.debug("Deleted Redis key after consumption: %s", redis_message_key)
                            except Exception as e:
                                logger.warning(
                                    "Failed to delete Redis key %s after consumption: %s",
                                    redis_message_key,
                                    e
                                )

                        else:
                            logger.info("Generated new message for client selection (Redis was empty)")
                            friendly_message = get_friendly_service_message(
                                length_of_auth_service_response
                            )
                        await self._emit_and_cache(
                            "auth_service",
                            {
                                "content": friendly_message,
                                "response": response,
                                "tag_name": "selected_service",
                                "selected_client": selected_client,
                                "followedBy": self.function,
                                "must_select": "True",
                                "client_name": client_name,
                                "final_response": "False"
                            }
                        )


                        raise ContinueException(
                            content=friendly_message,
                            response=response,
                            tag_name="selected_service"
                        )

                # 6️⃣ No typed service → normal selection flow
                all_auths = list(auth_map.keys())
                auth_service_summary = [
                    {
                        "auth_id": aid,
                        "auth": auth_map[aid]["auth"],
                        "auth_details_id": auth_map[aid].get("auth_details_id"),
                        "services": [s["name"] for s in auth_map[aid]["services"]],
                        "services_full": auth_map[aid]["services"]
                    }
                    for aid in all_auths
                ]

                # No auths
                if not auth_service_summary:
                    await self._emit_and_cache(
                        "auth_service",
                        {
                            "content": "No Authorizations or Services found for this client.",
                            "response": None,
                            "final_response": "False", 
                            "followedBy": self.function, 
                            "selected_client": selected_client
                        }
                    )
                    raise ContinueException(
                        content="No Authorizations or Services found for this client.",
                        response=None
                    )

                # Single authorization
                if len(all_auths) == 1:
                    aid = all_auths[0]
                    auth_name = auth_map[aid]["auth"]
                    services = auth_map[aid]["services"]

                    if not services:
                        await self._emit_and_cache(
                            "auth_service",
                            {
                                "content": "No Services found for the selected authorization.",
                                "response": None,
                                "final_response": "False", 
                                "followedBy": self.function, 
                                "selected_client": selected_client
                            }
                        )
                        raise ContinueException(
                            content="No Services found for the selected authorization.",
                            response=None
                        )

                    if len(services) == 1:
                        logger.debug("service %s", services[0])
                        svc = services[0]

                        # DO NOT reassign aid here — it already exists
                        selected_service_value = f"{aid}|{svc['id']}|{svc['auth_detail_id']}"
                        metadata["selected_service"] = selected_service_value

                        metadata.update({
                            "auth_id": aid,
                            "auth_name": auth_name,
                            "service_id": svc["id"],
                            "service_name": svc["name"],
                            "auth_detail_id": svc["auth_detail_id"],
                            "treatmentType": svc["treatmentType"],
                            "sub_service_id": svc.get("sub_service_id"),
                            "sub_service_name": svc.get("sub_service_name"),
                            "CptServiceCodeId": svc.get("CptServiceCodeId"),
                            "fundingscoreid": svc.get("fundingscoreid")
                        })
                        self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
                        return metadata, selected_service_value


                # Multiple authorizations → produce selectable list
                response_services = []
                for item in auth_service_summary:
                    aid = item["auth_id"]
                    for svc in item["services_full"]:
                        response_services.append({
                            "name": f"{item['auth']} => {svc['name']}",
                            "value": f"{aid}|{svc['id']}|{svc['auth_detail_id']}",
                        })

                unique_values = {svc["value"] for svc in response_services}  # set removes duplicates
                length_of_auth_service_response = len(unique_values)


                redis_message_key = f"{self.sessionId}_assistant_message"
                cached_message = None

                try:
                    cached_message = self.redis_client.get(redis_message_key)
                except Exception as e:
                    logger.warning(
                        "Failed to fetch message from Redis key %s: %s",
                        redis_message_key,
                        e
                    )

                if cached_message:
                    # Decode if Redis returns bytes
                    if isinstance(cached_message, bytes):
                        cached_message = cached_message.decode("utf-8")

                    friendly_message = cached_message
                    logger.info("Using cached message from Redis for client selection")

                    # ✅ DELETE after consuming
                    try:
                        self.redis_client.delete(redis_message_key)
                        logger.debug("Deleted Redis key after consumption: %s", redis_message_key)
                    except Exception as e:
                        logger.warning(
                            "Failed to delete Redis key %s after consumption: %s",
                            redis_message_key,
                            e
                        )

                else:
                    logger.info("Generated new message for client selection (Redis was empty)")
                    friendly_message = get_friendly_service_message(
                        length_of_auth_service_response
                    )
                await self._emit_and_cache(
                    "auth_service",
                    {
                        "content": friendly_message,
                        "response": response_services,
                        "tag_name": "selected_service",
                        "selected_client": selected_client,
                        "followedBy": self.function,
                        "must_select": "True",
                        "client_name": client_name,
                        "final_response": "False"
                    }
                )


                raise ContinueException(
                    content=friendly_message,
                    response=response_services,
                    tag_name="selected_service"
                )
            except ContinueException:
                raise

            except Exception as e:
                logger.exception(
                    "Unexpected error in process_auth_and_service | session=%s | client_name=%s",
                    self.sessionId, metadata.get("client_name")
                )

                await self._emit_and_cache(
                    "auth_service",
                    {
                        "content": "Something went wrong while fetching authorization and service details. Please try again.",
                        "response": None,
                        "final_response": "False",
                        "followedBy": self.function, 
                        "selected_client": selected_client
                    }
                )
                return

 
    async def fetch_auth_service_list(self, metadata: dict, start_date) -> list:
        """
        Fetch all auth+service pairs for a client using metadata and db_manager.
        
        Args:
            metadata (dict): Metadata containing client_id
            start_date (str): Date string in %Y-%m-%d format
        Returns:
            list: A list of dictionaries containing auth and service details
        """
        try:
            client_id = metadata.get("client_id")
            logger.info("Fetching auth+service list for client_id=%s", client_id)

            # Fetch all auth+service pairs for the client
            patient_auth = AuthDetailWithServiceQueryBuilder()
            patient_auth_sql = patient_auth.get_auth_detail_with_service(patient_id=client_id,date = start_date)
            logger.info("Generated SQL for auth+service fetch: %s", patient_auth_sql)
            patient_auth_query_result = await self.db_manager.execute_query(query=patient_auth_sql)
            auth_service_list = patient_auth_query_result.data
            logger.info("Auth+service list fetched for client_id=%s: %s", client_id, auth_service_list)

            return auth_service_list
        except ContinueException:
                return
        except Exception as e:
                logger.exception(
                    "Unexpected error in process_auth_and_service | session=%s | client_name=%s",
                    self.sessionId, metadata.get("client_name")
                )

                await self._emit_and_cache(
                    "auth_service",
                    {
                        "content": "Something went wrong while fetching authorization and service details. Please try again.",
                        "response": None,
                        "final_response": "False", 
                        "followedBy": self.function
                    }
                )

                raise ContinueException(
                    content="Error occurred while fetching authorization and service details.",
                    response=None
                )

    async def get_ranked_employees(self, response: List[Dict], metadata: Dict, preferred_gender: str, miles: int, selected_service: Optional[str], selected_location: Optional[str], selected_client:Optional[str]) -> List[Dict]:
        """
        Rank employees based on:
        1. TreatmentTeam match (highest priority)
        2. Language match
        3. Gender match

        Adds SuggestCriteria tags: LanguageMatch, GenderMatch, TreatmentTeamMatch.
        Adds metadata fields: AuthID, AuthName, SubServiceName, ServiceID, TreatmentTeam, TreatmentTypeName.
        """
        try:
            logger.info(f"response before ranking: {response}")
            try:
                redis_key = f"{self.sessionId}_weights"
                redis_weights = self.redis_client.get(redis_key)
                logger.info("Fetched weights from Redis for session %s: %s", self.sessionId, redis_weights)
            except Exception as e:  
                logger.exception("Redis error while fetching %s", redis_key)
                await self._emit_and_cache(
                    "final_suggested_provider",
                    {
                        "content": "Something went wrong while fetching employee rankings. Please try again.",
                        "response": None,
                        "tag_name": "error",
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                return [], None, None
            
            if not redis_weights:
                await self._emit_and_cache(
                    "final_suggested_provider",
                    {
                        "content": "Your session has expired. Kindly open a new chat to continue.",
                        "response": None,
                        "tag_name": "expiry",
                        "success" : False, 
                        "followedBy": self.function
                    }
                )
                return [], None, None
            
            redis_data = json.loads(redis_weights)
            logger.debug("Redis weights data: %s", redis_data)
            miles_from_redis = redis_data.get("maxDistanceInMiles") 
            default_status = redis_data.get("makeDefault")
            logger.debug("Default status fetched from redis: %s", default_status)
            effective_miles = miles if miles else miles_from_redis

            if effective_miles:
                response = [
                    emp for emp in response
                    if emp.get("DistanceInMiles") is not None
                    and emp.get("DistanceInMiles") <= effective_miles
                ]
            else:
                response = response.copy()

            if effective_miles and len(response) < 1:
                await self._emit_and_cache(
                    "final_suggested_provider",
                    {
                        "content": "No employees found within the selected miles range. Please increase the miles.",
                        "response": None,
                        "tag_name":"selected_suggested_provider",
                        "selected_client": selected_client,
                        "selected_service": selected_service,
                        "selected_location": selected_location,
                        "final_response": "True", 
                        "followedBy": self.function
                    }
                )
                return [], None, None

            if preferred_gender:
                if preferred_gender.lower() == "female":
                    response = [emp for emp in response if emp.get("GenderType", "").lower() == "female" or emp.get("GenderName", "").lower() == "female"]
                elif preferred_gender.lower() == "male":
                    response = [emp for emp in response if emp.get("GenderType", "").lower() == "male" or emp.get("GenderName", "").lower() == "male"]
                logger.info(f"response after gender filtering: {response}")
                
                if len(response) < 1:
                    await self._emit_and_cache(
                        "final_suggested_provider",
                        {
                            "content": "No employees found for the selected gender",
                            "response": None,
                            "tag_name":"selected_suggested_provider",
                            "final_response": "True", 
                            "followedBy": self.function
                        }
                    )
                    return [], None, None
                
            try:
                redis_key = f"{self.sessionId}_weights"
                redis_weights = self.redis_client.get(redis_key)
                logger.info("Fetched weights from Redis for session %s: %s", self.sessionId, redis_weights)
            except Exception as e:  
                logger.exception("Error fetching weights from Redis: %s", e)
                await self._emit_and_cache(
                    "final_suggested_provider",
                    {
                        "content": "Something went wrong while fetching employee rankings. Please try again.",
                        "response": None,
                        "tag_name": "error",
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                return [], None, None
            
            redis_data = json.loads(redis_weights)
            miles_from_redis = redis_data.get("maxDistanceInMiles") 
            default_status = redis_data.get("makeDefault")
            logger.debug("Default status fetched from redis: %s", default_status)

            # Determine which weight source to use
            use_default = default_status is True

            effective_miles = miles if miles else miles_from_redis
            try:
                effective_miles = int(effective_miles) if effective_miles else None
            except:
                effective_miles = None

            # use  default weights
            if use_default:
                logger.info("default_status=True → Forcing use of default .env weights")
                self.weights = self.weight
                self.flags = {"criteria": True, "language": True, "gender": True, "distance": True}

            # use redis weights
            elif redis_weights:
                try:
                    redis_data = json.loads(redis_weights)
                    logger.info("Using weights from Redis for session %s: %s", self.sessionId, redis_data)

                    self.flags = {
                        "criteria": redis_data.get("isCriteriaEnabled"),
                        "language": redis_data.get("isLanguageEnabled"),
                        "gender": redis_data.get("isGenderEnabled"),
                        "distance": redis_data.get("isDistanceEnabled"),
                    }

                    self.weights = {
                        "criteria": redis_data.get("criteria"),
                        "language": redis_data.get("language"),
                        "gender": redis_data.get("gender"),
                        "distance": redis_data.get("distance"),
                    }

                except Exception as e:
                    logger.warning("Invalid Redis JSON; using default .env weights. Error: %s", e)
                    self.weights = self.weight
                    self.flags = {"criteria": True, "language": True, "gender": True, "distance": True}

            else:
                logger.info("No Redis weights found; using default .env weights")
                self.weights = self.weight
                self.flags = {"criteria": True, "language": True, "gender": True, "distance": True}
                await self._emit_and_cache(
                    "final_suggested_provider",
                    {
                        "content": "Your session has expired. Kindly open a new chat to continue.",
                        "response": None,
                        "tag_name": "expiry",
                        "success" : False, 
                        "followedBy": self.function
                    }
                )
                return [], None, None



            ranked_employees = []

            user_languages = [lang.lower() for lang in metadata.get("language_ids", [])]
            user_gender = str(metadata.get("gender_id", "")).strip()
            user_team_ids = [str(t).strip() for t in metadata.get("treatment_team", "").split(",") if t]
            logger.info("User preferences: %s, %s, %s", user_languages, user_gender, user_team_ids)
            
            for emp in response:
                emp_criteria = emp.get("SuggestCriteria", [])

                # Language match
                emp_language_field = emp.get("LanguageName", [])
                if isinstance(emp_language_field, list):
                    emp_languages = [lang.strip().lower() for item in emp_language_field for lang in item.split('/') if lang]
                else:
                    emp_languages = [emp_language_field.strip().lower()] if emp_language_field else []

                language_score = 1 if set(emp_languages) & set(user_languages) else 0
                if language_score and "LanguageMatch" not in emp_criteria:
                    emp_criteria.append("LanguageMatch")

                # Gender match
                if preferred_gender:
                    gender_to_use = preferred_gender.strip().lower()
                    gender_map = {"male": "1", "female": "2"}
                    gender_to_use = gender_map.get(gender_to_use)
                else:
                    gender_to_use = user_gender.strip().lower()

                emp_gender = str(emp.get("GenderID", "")).strip()
                gender_score = 1 if emp_gender == gender_to_use else 0
                if gender_score and "GenderMatch" not in emp_criteria:
                    emp_criteria.append("GenderMatch")

                # TreatmentTeam match
                emp_id_str = str(emp.get("EmployeeId", "")).strip()
                criteria_score = 1 if emp_id_str in user_team_ids else 0
                if criteria_score and "TreatmentTeam" not in emp_criteria:
                    emp_criteria.append("TreatmentTeam")

                # Apply weight only if enabled
                criteria_weight = self.weights["criteria"] if self.flags["criteria"] else 0
                language_weight = self.weights["language"] if self.flags["language"] else 0
                gender_weight = self.weights["gender"] if self.flags["gender"] else 0
                distance_weight = self.weights["distance"] if self.flags["distance"] else 0
                logger.info("Weights applied criteria, language, gender,distance: %s, %s, %s, %s", criteria_weight, language_weight, gender_weight, distance_weight)
                max_distance = max(r["DistanceInMiles"] for r in response)
                emp_distance = emp.get("DistanceInMiles", 0)

                # Use miles from param or redis
                if max_distance == 0 or len(response) == 1:
                    # Only one employee or all distances are zero → full distance match
                    dist_score = 1
                else:
                    if effective_miles and effective_miles > 0:
                        if emp_distance > effective_miles:
                            dist_score = 0
                        else:
                            dist_score = max(0, 1 - (emp_distance / max_distance))
                    else:
                        dist_score = max(0, 1 - (emp_distance / max_distance))


                total_score = (
                    criteria_weight * criteria_score +
                    language_weight * language_score +
                    gender_weight * gender_score +
                    dist_score * distance_weight
                )
                emp["match_score"] = total_score
                emp["SuggestCriteria"] = emp_criteria

                # Add metadata
                emp.update({
                    "AuthID": metadata.get("auth_id"),
                    "AuthName": metadata.get("auth_name"),
                    "SubServiceName": metadata.get("sub_service_name"),
                    "ServiceID": metadata.get("service_id"),
                    "TreatmentTeam": emp.get("TreatmentTeam") or metadata.get("treatment_team"),
                    "TreatmentTypeName": metadata.get("treatmentType"),
                })

                ranked_employees.append(emp)
            
            ranked_employees.sort(key=lambda x: x["match_score"], reverse=True)
           
            top_ranked = ranked_employees[:self.range]
           
            sorted_employees = sorted(
                        top_ranked,
                        key=lambda x: (-x["match_score"], x["DistanceInMiles"])
                    )
            logger.info("Sorted employees after ranking: %s", sorted_employees)
            
            suggest_employee_dict = Datafilter(filtered_items=sorted_employees).merge_keys(
                keys=["EmployeeId", "EmployeeFullName"],
                merged_key="employeeNameWithId"
            )
            # Create a deep-ish copy for model payload (avoid mutating sorted_employees)
            employees = [emp.copy() for emp in sorted_employees]

            # 🔥 Convert match_score → percentage string (e.g. "63%")
            for emp in employees:
                score = emp.get("match_score")
                if isinstance(score, (int, float)):
                    emp["match_score_percent"] = f"{int(round(score * 100))}%"


            suggest_employee_list = [item["employeeNameWithId"] for item in suggest_employee_dict]

            try:
                summerized_suggest_employee = [
                    {"role": "system", "content": f"{prompt.suggestion_provider_with_filter}"},
                    {"role": "user", "content": json.dumps(employees)}
                ]
                summerized_suggestion_process = TriggerModel(message=summerized_suggest_employee)
                summerized_suggestion_response = await summerized_suggestion_process.excecute_hf()
                summerized_suggestion_response = json.loads(summerized_suggestion_response).get(
                    "content", "Error in suggestion provider summarization"
                )
            except Exception as e:
                logger.exception("Error in suggestion provider summarization: %s", e)
                await self._emit_and_cache(
                    "final_suggested_provider",
                    {
                        "content": "Something went wrong while summarizing employee suggestions. Please try again.",
                        "response": None,
                        "tag_name": "error",
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                return [], None, None

            try:
                redis_key = f"{self.sessionId}_appointment_payload"
                payload = redis_client.get(redis_key)
                payload = json.loads(payload)
                logger.debug("Payload fetched from Redis: %s", payload)
            except Exception as e:
                    logger.exception("Error fetching appointment payload: %s", e)
                    await self._emit_and_cache(
                        "final_suggested_provider",
                        {
                            "content": "Something went wrong while fetching appointment details. Please try again.",
                            "response": None,
                            "tag_name": "error",
                            "success": False, 
                            "followedBy": self.function
                        }
                    )
                    return [], None, None
            
            date = payload.get("start")
            start_date = date.rstrip("Z")

            metadata = {
                         "client_name": payload.get("clientName"),
                        "service_name": payload.get("serviceName"),
                        "location_name": payload.get("locationName"),
                        "duration": payload.get("scheduled_minutes"),
                        "auth_name": payload.get("AuthorizationName"),
                        "date":  start_date
                    }
                

            return sorted_employees, summerized_suggestion_response, metadata
        
        except Exception as e:
            logger.exception("Unexpected error in get_ranked_employees: %s", e)
            await self._emit_and_cache(
                "final_suggested_provider",
                {
                    "content": "Something went wrong while processing employee rankings. Please try again.",
                    "response": None,
                    "tag_name": "error",
                    "success": False, 
                    "followedBy": self.function
                }
            )
            return [], None, None
    
    async def fetch_patient_details_once(self, metadata: dict, start_time:str):
        """
        Parameters:
        - metadata: dictionary containing client_id and potentially other metadata.
        - start_time: ISO 8601 datetime string representing the start date of the session.

        Returns:
        - None if no patient_id is found in metadata, otherwise a dictionary containing the patient details.
        """
        try:
            patient_id = metadata.get("client_id")
            if not patient_id:
                logger.info("No patient_id found in metadata")
                return None

            try:
                sql = PatientDetailQueryBuilder().get_patient_details(patient_id, database= self.database_name, date = start_time)
                logger.info("Generated SQL for patient details: %s", sql)
            except Exception as e:
                logger.exception("Error generating SQL for patient details: %s", e)
                await self._emit_and_cache(
                    "error",
                    {
                        "content": "Something went wrong while fetching patient details. Please try again.",
                        "response": None,
                        "tag_name": "error",
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                return None

            try:
                patient_details = await self.db_manager.execute_query(sql)
                logger.info("Patient details fetched: %s", patient_details.data)
            except Exception as e:
                logger.exception("Error fetching patient details from database: %s", e)
                await self._emit_and_cache(
                    "error",
                    {
                        "content": "Something went wrong while retrieving patient information. Please try again.",
                        "response": None,
                        "tag_name": "error",
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                return None

            patient_details_list = patient_details.data
            if patient_details_list:
                try:
                    row = patient_details_list[0]

                    # Convert languageIDs from comma-separated string to list
                    language_ids_raw = row.get("languageIDs")
                    if language_ids_raw and isinstance(language_ids_raw, str):
                        language_ids = [lang.strip() for lang in language_ids_raw.split(",") if lang.strip()]
                    else:
                        language_ids = []

                    preference = {
                        "gender_id": row.get("gender"),
                        "zipcode": row.get("zipcode"),
                        "treatment_team": row.get("treatmentTeam"),
                        "excluded_employees": row.get("excludedEmployees"),
                        "language_ids": language_ids,
                    }
                    metadata.update({k: v for k, v in preference.items() if v is not None})
                    logger.info("Updated metadata with preferences: %s", metadata)

                except Exception as e:
                    logger.exception("Error processing patient preferences: %s", e)
                    await self._emit_and_cache(
                        "error",
                        {
                            "content": "Something went wrong while processing patient preferences. Please try again.",
                            "response": None,
                            "tag_name": "error",
                            "success": False, 
                            "followedBy": self.function
                        }
                    )
                    return None

                try:
                    key = f"{self.sessionId}_preferences"
                    self.redis_client.set(key, json.dumps(preference), ex=settings.expiry_time)
                    logger.info("Saved preference to Redis under key=%s: %s", key, preference)
                except Exception as e:
                    logger.exception("Error saving preferences to Redis: %s", e)
                    await self._emit_and_cache(
                        "error",
                        {
                            "content": "Something went wrong while saving patient preferences. Please try again.",
                            "response": None,
                            "tag_name": "error",
                            "success": False, 
                            "followedBy": self.function
                        }
                    )
                    return None

        except Exception as e:
            logger.exception("Unexpected error in fetch_patient_details_once: %s", e)
            await self._emit_and_cache(
                "error",
                {
                    "content": "Something went wrong while fetching patient details. Please try again.",
                    "response": None,
                    "tag_name": "error",
                    "success": False
                }
            )
            return None

    async def fetch_suggestion_employees_by_service_and_location(
        self,
        metadata: dict,
        miles: int,
        database : str
    ) -> List[Dict[str, Any]]:
        """
        Fetch employees near a location filtered by service type and site.

        Parameters:
        - metadata: dict containing service_type_id, site_id, etc.
        - miles: (optional) distance radius to filter employees.
                 If not provided, defaults to settings.maximum_miles.

        Returns:
        - List of employee dicts with EmployeeId, Latitude, Longitude, DistanceInMiles
        """
        try:
            logger.info("Fetching suggestion employees with metadata: %s, miles: %s, database: %s", metadata, miles, database)
            
            try:
                result = EmployeeServiceImpl()
                logger.info("EmployeeServiceImpl instance created successfully")
            except Exception as e:
                logger.exception("Error instantiating EmployeeServiceImpl: %s", e)
                await self._emit_and_cache(
                    "location",
                    {
                        "content": "Something went wrong while initializing employee service. Please try again.",
                        "response": None,
                        "tag_name": "error",
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                return []

            try:
                response = await result.process_employee(metadata, miles, database)
                logger.info("Employees fetched successfully: %s", response)
                return response
            except Exception as e:
                logger.exception("Error processing employees: %s", e)
                await self._emit_and_cache(
                    "location",
                    {
                        "content": "Something went wrong while fetching employee suggestions. Please try again.",
                        "response": None,
                        "tag_name": "error",
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                return []
        
        except Exception as e:
            logger.exception("Unexpected error in fetch_suggestion_employees_by_service_and_location: %s", e)
            await self._emit_and_cache(
                "location",
                {
                    "content": "Something went wrong while fetching employee suggestions. Please try again.",
                    "response": None,
                    "tag_name": "error",
                    "success": False, 
                    "followedBy": self.function
                }
            )
            return []
    
    def _fuzzy_match_locations(self, locations: list, location_name: str) -> list:
        """Apply fuzzy match on locations"""
        location_filter = Datafilter(
            filtered_items=locations,
            search_key="Name",
            match_method=fuzz.token_set_ratio, 
            search_score_cutoff=80
        )
        return location_filter.filter_by_name(search_name=location_name)


    async def _fetch_all_locations(self, patient_id: int, site_id: int) -> list:
        """Fetch patient-specific + common locations"""
        try:
            try:
                search_location = PatientLocationQueryBuilder()
                common_location = CommonLocationQueryBuilder()
                logger.info("Query builders created successfully")
            except Exception as e:
                logger.exception("Error creating location query builders: %s", e)
                

            try:
                await self._emit_and_cache("process", "Fetching patient-specific locations")
                await self._emit_and_cache("process", "Fetching site-specific common locations")
                patient_sql = search_location.get_patient_location(patient_id=patient_id)
                common_sql = common_location.get_patient_location(
                    site_id=site_id,
                    database=self.database_name
                )
                logger.info("Generated SQL for patient locations: %s", patient_sql)
                logger.info("Generated SQL for common locations: %s", common_sql)
            except Exception as e:
                logger.exception("Error generating location SQL: %s", e)

            try:
                patient_result = await self.db_manager.execute_query(query=patient_sql)
                logger.info("Patient locations fetched: %s", patient_result.data)
            except Exception as e:
                logger.exception("Error fetching patient-specific locations: %s", e)
                

            try:
                common_result = await self.db_manager.execute_query(query=common_sql)
                logger.info("Common locations fetched: %s", common_result.data)
            except Exception as e:
                logger.exception("Error fetching common locations: %s", e)
                

            locations = (patient_result.data or []) + (common_result.data or [])
            logger.info("Fetched total locations: %d", len(locations))
            return locations

        except Exception as e:
            logger.exception("Unexpected error in _fetch_all_locations: %s", e)
            
            


    async def get_location_id(
        self,
        metadata: dict,
        location_name: Optional[str] = None,
        selected_location: Optional[str] = None,
        selected_service: Optional[str] = None,
        selected_client: Optional[str] = None,
        user_location_name: Optional[str] = None,
        checkable: bool = False
    ):
        """
        Get location_id from metadata if available and matches location_name.
        Otherwise, search the database, update metadata, and return location_id.
        """
        try:
            logger.info("Checking metadata for location...")

            if user_location_name:
                location_name = user_location_name
                logger.info("location_name overridden by user_location_name: %s", location_name)

            if selected_location:
                logger.info("Using selected_location provided by user: %s", selected_location)
                location_data = Datafilter.split_string(selected_location)
                metadata["location_name"] = location_data.get("field_1")
                metadata["location_id"] = location_data.get("field_2")
                self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
                logger.info("Metadata updated with selected location: %s", metadata)
                selected_location_string = f"{metadata['location_name']}|{metadata['location_id']}"
                return metadata["location_id"], selected_location_string

            if metadata.get("location_id") is not None and metadata.get("location_name") == location_name:
                logger.info("Metadata already has the location: %s", metadata)
                selected_location_string = f"{metadata['location_name']}|{metadata['location_id']}"
                return metadata["location_id"], selected_location_string

            # ✅ Fetch locations ONCE (used by both checkable + normal path)
            patient_id = metadata.get("client_id")
            site_id = metadata.get("siteId")
            all_locations = await self._fetch_all_locations(patient_id, site_id)
            logger.info("Total locations fetched: %d", len(all_locations))

            # =========================
            # ✅ CHECKABLE MODE (Silent)
            # =========================
            if checkable:
                if not location_name:
                    return False, None

                matches = self._fuzzy_match_locations(all_locations, location_name)
                if matches:
                    row = matches[0]
                    location_id = row.get("locationId")
                    location_label = row.get("Name") or location_name
                    formatted_location = f"{location_label}|{location_id}"

                    logger.info(
                        "Checkable match found for location: %s (ID: %s)",
                        location_label,
                        location_id
                    )
                    return True, formatted_location

                logger.info("Checkable match NOT found for location: %s", location_name)
                return False, None

            # =========================
            # ✅ NORMAL MODE
            # =========================
            if location_name:
                results = self._fuzzy_match_locations(all_locations, location_name)
            else:
                results = all_locations

            logger.info("Matching results for location_name '%s': %s", location_name, results)

            if len(results) < 1:
                logger.warning("No locations found%s", f" with name: {location_name}" if location_name else "")
                await self._emit_and_cache(
                    "location",
                    {
                        "content": f"No Locations found with the {location_name}",
                        "response": None,
                        "final_response": "False", 
                        "tag_name": "selected_location",
                        "selected_client": selected_client,
                        "selected_service": selected_service,
                        "success": False, 
                        "followedBy": self.function
                    }
                )
                raise ContinueException(
                    content=f"No Locations found{f' with name: {location_name}' if location_name else ''}",
                    response=None
                )

            if len(results) > 1:
                location_merger = Datafilter(filtered_items=results)
                new_location_list = location_merger.merge_keys(
                    ["Name", "locationId", "displayAddress"],
                    merged_key="nameWithLocationId"
                )

                similar_location_names = [item["nameWithLocationId"] for item in new_location_list]
                unique_locations = set(similar_location_names)
                length_of_location_response = len(unique_locations)

                redis_message_key = f"{self.sessionId}_assistant_message"
                cached_message = None

                try:
                    cached_message = self.redis_client.get(redis_message_key)
                except Exception as e:
                    logger.warning("Failed to fetch message from Redis key %s: %s", redis_message_key, e)

                if cached_message:
                    if isinstance(cached_message, bytes):
                        cached_message = cached_message.decode("utf-8")

                    friendly_location_message = cached_message
                    logger.info("Using cached message from Redis for client selection")

                    try:
                        self.redis_client.delete(redis_message_key)
                        logger.debug("Deleted Redis key after consumption: %s", redis_message_key)
                    except Exception as e:
                        logger.warning("Failed to delete Redis key %s after consumption: %s", redis_message_key, e)
                else:
                    logger.info("Generated new message for client selection (Redis was empty)")
                    friendly_location_message = get_friendly_location_message(length_of_location_response)

                logger.info("Multiple locations found, asking user to select from: %s", similar_location_names)

                await self._emit_and_cache(
                    "location",
                    {
                        "content": friendly_location_message,
                        "response": similar_location_names,
                        "selected_service": selected_service,
                        "selected_client": selected_client,
                        "followedBy": self.function,
                        "tag_name": "selected_location",
                        "final_response": "False"
                    }
                )

                raise ContinueException(
                    content=friendly_location_message,
                    response=similar_location_names,
                    tag_name="selected_location"
                )

            row = results[0]
            location_id = row.get("locationId")
            location_label = location_name or row.get("Name") or row.get("displayAddress")

            metadata["location_name"] = location_label
            metadata["location_id"] = location_id
            self.metadata.write_metadata(session_id=self.sessionId, data=metadata)
            logger.info("Metadata updated with location: %s", metadata)

            selected_location_string = f"{metadata['location_name']}|{metadata['location_id']}"
            return location_id, selected_location_string

        except ContinueException:
            raise
        except Exception as e:
            logger.exception("Unexpected error in get_location_id: %s", e)
          
            await self._emit_and_cache(
                "location",
                {
                    "content":  "Something went wrong while fetching location details. Please try again.",
                    "response": None,
                    "tag_name": "error",
                    "success": False,
                    "followedBy": self.function, 
                    "selected_client": selected_client,
                    "selected_service": selected_service
                }
            )
            raise ContinueException(
                content="Error occurred while processing location.",
                response=None
            )


    
    async def get_clean_availability(self, employeesWith_selected_service, available_emp_ids, treatment_team_emp_ids):
        """
        Filters employeesWith_selected_service based on available_emp_ids and adds SuggestCriteria.

        Parameters:
        - employeesWith_selected_service: List[Dict] containing EmployeeId, empName, distanceInMiles.
        - available_emp_ids: List of employee IDs who are available.
        - treatment_team_emp_ids: List of employee IDs who are part of the treatment team.

        Returns:
        - Filtered and updated list of employees.
        """

        logger.info("Filtering employees based on availability and treatment team criteria.")

        # Create a set for faster lookup
        available_emp_ids_set = set([emp_id['EmployeeId'] for emp_id in available_emp_ids if 'EmployeeId' in emp_id])
        treatment_team_emp_ids_set = set(treatment_team_emp_ids)

        # Filter and update employees
        filtered_employees = []
        for employee in employeesWith_selected_service:
            emp_id = employee.get("EmployeeId")

            if emp_id in available_emp_ids_set:
                employee["SuggestCriteria"] = []

                if emp_id in treatment_team_emp_ids_set:
                    employee["SuggestCriteria"].append("TreatmentTeam")

                filtered_employees.append(employee)

        logger.info("Filtered employees: %s", filtered_employees)
        return filtered_employees
    async def book_appointment(
            self,
            client_name: str,
            date:str,
            time:str,
            scheduled_minutes: int = 0,
            authorisation: str = None,
            service_type: str = None,
            location: str = None,
            selected_suggested_provider: str = None,
            selected_client: str = None,
            selected_auth: str = None,
            selected_service: str = None,
            selected_location: str = None,
            preferred_gender: str = None,
            user_client_message:str= None,
            user_service_name: str = None, 
            service_name: Optional[str] = None,
            location_name: Optional[str] = None,
            user_location_name:str = None ,
            miles:str = None 
        ):
            """Book an appointment for a client with available providers.
            This function handles the complete appointment booking flow including:
            - Client identification and validation
            - Authorization and service processing
            - Location selection
            - Provider search and filtering based on:
                * Treatment team requirements
                * Service and location compatibility
                * Compliance/credentials check
                * Availability for the scheduled time
                * Gender preferences
            - Provider ranking and final recommendations
            
            Returns provider suggestions to the client for selection.
            """
            try:
                patient_id = None
                location_id = None
                language_ids = None
                try:
                    formated_time = datetime.fromisoformat(f"{date}T{time}")
                    start_time = formated_time.strftime("%Y-%m-%dT%H:%M")
                except (ValueError, TypeError) as e:
                    logger.error("Invalid date/time format. date=%s time=%s error=%s", date, time, str(e))

                    await self._emit_and_cache(
                                "final_suggested_provider",
                                {
                                    "content": "I couldn't process the data. Please start a new chat and try again.",
                                    "response": None,
                                    "tag_name": "expiry",
                                    "followedBy": self.function,
                                    "success" : False
                                    
                                }
                            )
                    return 
                logger.info("Session ID: %s", self.sessionId)
                login_data_redis_key = f"{self.sessionId}_login_data"
                #get auth token from redis to verify
                stored_login_data = redis_client.get(login_data_redis_key)
                logger.info("stored_login_data fetched from redis: %s", stored_login_data)
                if stored_login_data:
                    stored_login_data = json.loads(stored_login_data)
                    logger.debug(f"Retrieved login data from Redis for session {self.sessionId}: {stored_login_data}")
                if stored_login_data:
                    auth_token = stored_login_data.get("authorization")
                else:
                    auth_token = None
                logger.info("auth_token: %s", auth_token)
                if not stored_login_data:
                    raise ValueError("No login data found in Redis")
                
                logger.info("Time %s", start_time)

                existing_meta = self.metadata.read_metadata(session_id=self.sessionId) or {}

                # Only set siteId if it does not already exist
                if "siteId" not in existing_meta or existing_meta["siteId"] is None:
                    existing_meta["siteId"] = self.siteid

                # Add start date & time if not already present
                if start_time:
                    if existing_meta.get("start_date") != start_time:
                        existing_meta["start_date"] = start_time
                        logger.info("Updated metadata start_date → %s", start_time)

                # Update duration if missing OR different
                if scheduled_minutes is not None:
                    if existing_meta.get("duration") != scheduled_minutes:
                        existing_meta["duration"] = scheduled_minutes
                        logger.info("Updated metadata duration → %s", scheduled_minutes)

                if preferred_gender and "preferred_gender" not in existing_meta:
                    existing_meta["preferred_gender"] = preferred_gender.strip().lower()
                    logger.info(
                        "Updated metadata with preferred gender '%s' for session %s",
                        preferred_gender,
                        self.sessionId
                    )

                self.metadata.write_metadata(session_id=self.sessionId, data=existing_meta)

                metadata = self.metadata.read_metadata(session_id=self.sessionId)
                logger.info("Metadata for session %s: %s", self.sessionId, metadata)

                if client_name or selected_client:
                    patient_id , selected_client= await self.get_client_id(metadata, client_name, selected_client, user_client_message)
                    logger.info("Fetched patient_id: %s", patient_id)

                logger.info("Metadata before processing auth/service/location: %s", metadata)
                if user_client_message:
                    selected_client = metadata.get("client_name") 
                    selected_client_id = metadata.get("client_id")
                    selected_client = f"{selected_client_id}|{selected_client}"
                    logger.debug("Selected client after user_client_message: %s", selected_client)
                    
                selected_service = selected_service or None
                logger.debug("selected_service in book appointment: %s", selected_service)
                result , selected_service= await self.process_auth_and_service(metadata, authorisation, service_type, selected_auth, selected_service,start_time, selected_client, user_service_name )
                logger.info("Auth/service processing result: %s", result)
                start_time = metadata.get("start_date")
                await self.fetch_patient_details_once(metadata, start_time)

                # await self.sio.emit(f"{self.sessionId}_process", PROCESS_CLIENT["get_location_id"], to=self.sid)
                result, selected_location = await self.get_location_id(metadata, location, selected_location, selected_service,selected_client , user_location_name,)
                location_id = metadata.get("location_id")
                logger.info("Location processed, location_id: %s", location_id)
                logger.info("Metadata after processing location: %s", metadata)

                # Convert start_time ("YYYY-MM-DDTHH:MM") into a datetime
                start_time = metadata.get("start_date")
                start_dt = datetime.fromisoformat(start_time)
                logger.info("Parsed start datetime: %s", start_dt)
                # Compute end datetime using scheduled_minutes
                end_dt = start_dt + timedelta(minutes=scheduled_minutes or 30)
                logger.info("Computed end datetime: %s", end_dt)
                # Format both as ISO strings with seconds + Z suffix
                formatted_start = start_dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
                formatted_end = end_dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
                payload = {
                    "clientName": metadata.get("client_name"),
                    "AuthorizationName": metadata.get("auth_name"),
                    "serviceName": metadata.get("service_name"),
                    "locationName": metadata.get("location_name"),
                    "patientId": metadata.get("client_id"),
                    "authId": metadata.get("auth_id"),
                    "authDetailId": metadata.get("auth_detail_id"),
                    "serviceTypeId": metadata.get("service_id"),
                    "serviceSubTypeId": metadata.get("sub_service_id"),
                    "locationId": metadata.get("location_id"),
                    "start": formatted_start,
                    "endDate": formatted_end,
                    "scheduled_minutes": scheduled_minutes, 
                    "siteId": metadata.get("siteId")
                }
                logger.debug("appointment payload: %s", payload)
                redis_key = f"{self.sessionId}_appointment_payload"
                self.redis_client.set(redis_key, json.dumps(payload))

                if not selected_suggested_provider:
                    try:
                        # ===============================
                        # STEP 0: DETERMINE SEARCH MILES 
                        # ===============================
                        weights_key = f"{self.sessionId}_weights"
                        datamiles = redis_client.get(weights_key)
                        if isinstance(datamiles, str):
                            datamiles = json.loads(datamiles)
                        logger.debug("Fetched weights from Redis: %s", datamiles)    
                        if not datamiles:
                            await self._emit_and_cache(
                                "final_suggested_provider",
                                {
                                    "content": "This session expired , kindly open new chat to continue",
                                    "response": None,
                                    "tag_name": "expiry",
                                    "success" : False, 
                                    'followedBy': self.function , 
                                    "selected_client": selected_client,
                                    "selected_service": selected_service,
                                    "selected_location": selected_location
                                    
                                }
                            )
                            return [], None, None

                        miles_in_weight = datamiles.get("maxDistanceInMiles") if datamiles else None

                        if miles is not None:
                            base_miles = miles
                        elif miles_in_weight is not None:
                            base_miles = miles_in_weight
                        # else:
                        #     base_miles = settings.avarage_miles

                        search_miles = base_miles + settings.add_onn_miles

                        logger.info("Employee search will run once with miles=%s", search_miles)

                        # =================================
                        # STEP 1: TREATMENT TEAM VALIDATION 
                        # ==================================
                        treatment = metadata.get("treatment_team")
                        service_type_id = metadata.get("service_id")
                        site_id = metadata.get("siteId")
                                            
                        validation = ValidateTreatmentTeamQueryBuilder()
                        sql = validation.validate_treatment_team(
                            treatment_team=treatment,
                            service_type_id=service_type_id,
                            site_id=site_id,
                            metadata=metadata
                        )

                        query_result = await self.db_manager.execute_query(query=sql)
                        rows = query_result.data or []

                        merged_treatment_team = {}
                        for row in rows:
                            if row.get("DistanceInMiles") is None:
                                continue

                            emp_id = row["EmployeeId"]
                            language_ids = [int(x) for x in (row.get("LanguageIDs") or "").split(",") if x.strip()]
                            language_names = [x.strip() for x in (row.get("LanguageNames") or "").split(",") if x.strip()]

                            if emp_id not in merged_treatment_team:
                                merged_treatment_team[emp_id] = row.copy()
                                merged_treatment_team[emp_id]["LanguageIDs"] = language_ids
                                merged_treatment_team[emp_id]["LanguageNames"] = language_names
                            else:
                                merged_treatment_team[emp_id]["LanguageIDs"] = list(
                                    set(merged_treatment_team[emp_id]["LanguageIDs"] + language_ids)
                                )
                                merged_treatment_team[emp_id]["LanguageNames"] = list(
                                    set(merged_treatment_team[emp_id]["LanguageNames"] + language_names)
                                )

                        treatment_team_list = list(merged_treatment_team.values())
                        valid_employee_ids = [
                                e["EmployeeId"]
                                for e in treatment_team_list
                                if e.get("isValidForService")
                            ]


                        # ============================================================
                        # STEP 2: EMPLOYEE SEARCH (SERVICE + LOCATION) — SINGLE PASS
                        # ============================================================
                        await self._emit_and_cache(
                            "process",
                            PROCESS_CLIENT["fetch_suggestion_employees_by_service_and_location"] % base_miles
                        )

                        employee_list_with_service_suggestion = await self.fetch_suggestion_employees_by_service_and_location(
                            metadata,
                            miles=search_miles,
                            database=self.database_name
                        )
                        logger.info(" Found %s employees within %s miles",
                                        len(employee_list_with_service_suggestion), search_miles)
                        

                        if not employee_list_with_service_suggestion:
                            await self._emit_and_cache(
                                "final_suggested_provider",
                                {
                                    "content": "No employees available for the selected service within search radius.",
                                    "response": None,
                                    "final_response": "True", 
                                    "selected_service": selected_service,
                                    "selected_client": selected_client,
                                    "selected_location": selected_location, 
                                    "followedBy": self.function,
                                }
                            )
                            raise ContinueException(
                                "No employees found for the selected service within search radius.",
                                response=None
                            )
                        

                        merged_service_location = {}
                        for emp in employee_list_with_service_suggestion:
                            emp_id = emp["EmployeeId"]
                            if emp_id not in merged_service_location:
                                merged_service_location[emp_id] = emp.copy()
                                merged_service_location[emp_id]["LanguageID"] = [emp["LanguageID"]]
                                merged_service_location[emp_id]["LanguageName"] = [emp["LanguageName"]]
                            else:
                                if emp["LanguageID"] not in merged_service_location[emp_id]["LanguageID"]:
                                    merged_service_location[emp_id]["LanguageID"].append(emp["LanguageID"])
                                if emp["LanguageName"] not in merged_service_location[emp_id]["LanguageName"]:
                                    merged_service_location[emp_id]["LanguageName"].append(emp["LanguageName"])

                        service_location_list = list(merged_service_location.values())
                        logger.debug("Merged service/location list: %s", service_location_list)

                        merged_list = treatment_team_list.copy()
                        existing_ids = {e["EmployeeId"] for e in merged_list}

                        for emp in service_location_list:
                            if emp["EmployeeId"] not in existing_ids:
                                merged_list.append(emp)
                        if not merged_list:
                            await self._emit_and_cache(
                                "final_suggested_provider",
                                {"content":"No employees available for the selected service within search radius", "response": None, "tag_name":"selected_suggested_provider", "final_response": "True", "selected_service": selected_service,"selected_client": selected_client, "selected_location": selected_location, "followedBy": self.function}
                            )
                            return
                            

                        combined_count = len(merged_list)
                        logger.info("LEVEL 1: Combined count (treatment team + service/location) at %s miles: %s",
                                    search_miles, combined_count)
                        logger.debug("Combined merged list: %s", merged_list)
                        await self._emit_and_cache(
                            "process",
                            PROCESS_CLIENT["processing_retrived_employees"]
                        )
                        # STEP 3: COMPLIANCE / CQC CHECK (NO RETRY)
                        complaince = await self.get_employee_credentials(merged_list, start_time, metadata, database=self.database_name)
                        

                        funding_source_id = metadata.get("fundingscoreid")
                        sub_service_type_id = metadata.get("sub_service_id")
                        logger.info("funding_source_id: %s, sub_service_type_id: %s",funding_source_id, sub_service_type_id)
                        crendital = EmpCredentialQueryBuilder()
                        qualification = EmpQualificationTypeQueryBuilder()
                        clearance = EmpClearanceTypeQueryBuilder()
                        
                        clearance_result, credential_result, qualification_result = await asyncio.gather(
                            clearance.get_emp_clearance_type_ids(
                                service_type_id=metadata.get("service_id"),
                                service_sub_type_id=metadata.get("sub_service_id"),
                                funding_source_id=metadata.get("fundingscoreid"),
                                database=self.database_name,
                                site_id=metadata.get("siteId")
                            ),
                            crendital.get_emp_credential_types(
                                service_type_id=metadata.get("service_id"),
                                sub_service_type_id=metadata.get("sub_service_id"),
                                funding_source_id=metadata.get("fundingscoreid"),
                                database=self.database_name,
                                site_id=metadata.get("siteId")
                            ),
                            qualification.get_emp_qualification_type_ids(
                                service_type_id=metadata.get("service_id"),
                                service_sub_type_id=metadata.get("sub_service_id"),
                                funding_source_id=metadata.get("fundingscoreid"),
                                database=self.database_name,
                                site_id=metadata.get("siteId")
                            )
                        )

                        logger.info("Credential SQL: %s", credential_result)
                        query_result = await self.db_manager.execute_query(query=credential_result)
                        logger.debug("Bill rate credential query result: %s", query_result.data)
                        crendital_billrate = query_result.data or []


                        logger.info("Qualification SQL: %s", qualification_result)
                        query_result = await self.db_manager.execute_query(query=qualification_result)
                        logger.debug("Bill rate qualification query result: %s", query_result.data)
                        qualification_billrate = query_result.data or []

                       
                        logger.info("Clearance SQL: %s", clearance_result)
                        query_result = await self.db_manager.execute_query(query=clearance_result)
                        logger.debug("Bill rate clearance query result: %s", query_result.data)
                        clearnce_billrate = query_result.data or []
        
                        # Safely extract required IDs from SQL query results
                        clearance_required = {str(c['EmpClearanceTypeId']) for c in (clearnce_billrate or [])}
                        credential_required = {str(c['EmpCredentialTypeId']) for c in (crendital_billrate or [])}
                        qualification_required = {str(q['EmpQualificationTypeId']) for q in (qualification_billrate or [])}

                        target_service_id = metadata.get("CptServiceCodeId")

                        def is_valid_employee(emp):

                            # Clearance validation
                            if clearance_required:
                                clearance_match = any(
                                    str(c.get("id")) in clearance_required and
                                    c.get("cptserviceid") == target_service_id
                                    for c in emp.get("Clearance", [])
                                )
                                if not clearance_match:
                                    return False

                            # Credential validation
                            if credential_required:
                                credential_match = any(
                                    str(c.get("id")) in credential_required and
                                    c.get("cptserviceid") == target_service_id
                                    for c in emp.get("Credential", [])
                                )
                                if not credential_match:
                                    return False

                            # Qualification validation
                            if qualification_required:
                                qualification_match = any(
                                    str(q.get("id")) in qualification_required and
                                    q.get("cptserviceid") == target_service_id
                                    for q in emp.get("Qualification", [])
                                )
                                if not qualification_match:
                                    return False

                            return True

                        employee_list_with_service_suggestion = [
                            e for e in complaince if is_valid_employee(e)
                        ]
                        logger.info("Employees after compliance exclusion %s", employee_list_with_service_suggestion)

                        if len(employee_list_with_service_suggestion) == 0:
                            await self._emit_and_cache(
                                "final_suggested_provider",
                                {"content":"We couldn’t find any employees who meet all the required service, clearance, credential, and qualification criteria for your selection.", "response": None, "tag_name":"selected_suggested_provider", "final_response": "True", "selected_service": selected_service,"selected_client": selected_client, "selected_location": selected_location, "followedBy": self.function}
                            )
                            return
                    
                   
                        # STEP 4: EXCLUSION + AVAILABILITY (SINGLE PASS)
                        employees_in_service = [e["EmployeeId"] for e in employee_list_with_service_suggestion]
                        filtered_employee_ids = await self.get_Exclusion_employee_id(metadata, employees_in_service)
                        
                        await self._emit_and_cache(
                        
                            "process",
                        
                            PROCESS_CLIENT["process_availability"]
                        
                        )

                        availabilityservice = AvailabilityServiceImpl()
                        start_time = metadata.get("start_date")
                        start_dt = start_time if isinstance(start_time, datetime) else datetime.fromisoformat(start_time)
                        end_dt = start_dt + timedelta(minutes=scheduled_minutes)

                        available_ids = await availabilityservice.process_availability(
                            employeeIds=filtered_employee_ids,
                            startDate=start_dt.isoformat(),
                            endDate=end_dt.isoformat()
                        )

                        availability = await self.get_clean_availability(
                            employeesWith_selected_service=employee_list_with_service_suggestion,
                            available_emp_ids=available_ids,
                            treatment_team_emp_ids=valid_employee_ids
                        )

                        if not availability:
                            await self._emit_and_cache(
                                    "final_suggested_provider",
                                    {"content":"No employees available for the selected service and time range within the maximum search radius.", "response": None, "tag_name":"selected_suggested_provider", "final_response": "True", "selected_service": selected_service,"selected_client": selected_client, "selected_location": selected_location, "followedBy": self.function}
                                )
                            return

                        # ============================================================
                        # STEP 5: RANKING & FINAL RESPONSE
                        # ============================================================
                        metadata["miles"] = search_miles
                        try:
                            final_key = f"{self.sessionId}_final_scored_emp"
                            self.redis_client.set(final_key, json.dumps(availability), ex=settings.expiry_time)
                            logger.info("Stored final ranked employees for session %s in Redis key %s", self.sessionId, final_key)
                        except Exception as e:
                            logger.error("Failed to store ranked employees in Redis for session %s: %s", self.sessionId, e)

                        weights_key = f"{self.sessionId}_weights"
                        datamiles = redis_client.get(weights_key)
                        if isinstance(datamiles, str):
                            datamiles = json.loads(datamiles)
                        if miles is None and not datamiles:
                                await self._emit_and_cache(
                                    "final_suggested_provider",
                                    {
                                        "content": "Your session has expired. Kindly open a new chat to continue.",
                                        "response": None,
                                        "tag_name": "expiry",
                                        "success" : False, 
                                        "followedBy": self.function,
                                        "selected_client": selected_client,
                                        "selected_service": selected_service,
                                        "selected_location": selected_location,
                                    }
                                )
                                return [], None, None
                        effective_miles = miles if miles is not None else datamiles.get("maxDistanceInMiles")

                        availability_with_rank,summary, metadata = await self.get_ranked_employees(
                            response=availability,
                            metadata=metadata,
                            preferred_gender=preferred_gender,
                            miles=effective_miles, 
                            selected_service=selected_service,
                            selected_client=selected_client,
                            selected_location=selected_location
                        )
                        
                        await self._emit_and_cache(
                            "final_suggested_provider",
                            {
                                "content": summary,
                                "response": availability_with_rank,
                                "metadata": metadata,
                                "tag_name": "selected_suggested_provider",
                                "final_response": "True", 
                                "followedBy": self.function, 
                                "selected_client": selected_client,
                                "selected_service": selected_service,
                                "selected_location": selected_location,                          }
                        )

                        raise ContinueException(
                            content=summary,
                            response=availability_with_rank,
                            tag_name="selected_suggested_provider"
                        )

                    except ContinueException as e:
                        raise ContinueException(content=e.content, response=e.output, tag_name=e.tag_name)

            except Exception as e:
                traceback.print_exc()
                logger.error(f"------------------Error booking appointment: {e}")
                raise e
            


client = MeasurePMAsyncClient()
def getclient() -> MeasurePMAsyncClient:
    return client