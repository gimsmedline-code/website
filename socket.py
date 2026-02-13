from ast import Dict
import datetime
import json
from fastapi import Depends
import requests
from app.utils.trigger_model import TriggerModel
from app.utils.update_metadata import process_metadata_update
import socketio
import pytz
from typing import Optional
from datetime import datetime
from app.config.logger_config import logger, set_session
from app.config.redis_configuration import redis_client
from app.database.dependencies import get_db_manager
from app.database.manager import DatabaseManager
from app.service.impl.chat_service_impl import ChatServiceImpl
from app.utils.endpoints import MeasurePMAsyncClient
from app.utils.metadata import SessionMetadataManager
from app.config.env_configuration import settings
from app.dependencies import get_metadata_manager

def register_socketio_events(sio: socketio.AsyncServer):
    async def process_client_selection(
        sid: Optional[str] = None,
        selected: Optional[str] = None,
        tag: Optional[str] = None,
        followedBy: Optional[Dict] = None,
        session: Optional[str] = None,
        user_message: Optional[str] = None, 
        selected_client: Optional[str] = None,
        selected_service: Optional[str] = None,
        selected_location: Optional[str] = None,
    ) -> dict:

        logger.info(f"Processing client selection: selected={selected}, tag={tag}")

        if session:
            set_session(str(session))

        followedBy = followedBy or {}
        tool_args = dict(followedBy.get("arguments", {}))

        # Process metadata update if user_message exists
        if user_message:
            tool_args = dict(followedBy.get("arguments", {}))
            
            metadata_manager = SessionMetadataManager()
            current_metadata = metadata_manager.read_metadata(session)

            metadata_result, tool_args, updated_keys, updated_metadata = await process_metadata_update(
                metadata=tool_args,
                user_message=user_message,
                followedBy=followedBy,
                tag=tag,
                selected=selected,
                sio=sio,         
                session=session,  
                sid=sid,
                # selected_client=selected_client,
                # selected_service=selected_service,
                # selected_location=selected_location,
                emit_name="selected_client"
                )

            # If no metadata was updated and message was emitted, return early
            if not updated_keys and not updated_metadata:
                logger.info("Assistant message emitted, skipping function call")
                return

            required_keys = {"miles", "language", "gender", "distance", "treatment_team"}
            if required_keys.intersection(updated_keys):
                await sio.emit(
                    f"{session}_final_suggested_provider",
                    {
                        "content": (
                            "To update miles, language, gender, distance, or treatment team, "
                            "please use the settings bar."
                        ), 
                        "followedBy": followedBy, 
                        "tag_name":"selected_suggested_provider", 
                        "final_response": "True",
                        "selected_service": selected_service,
                        "selected_client": selected_client, 
                        "selected_location": selected_location
                    },
                    to=sid,
                )
                logger.info(
                    "Restricted field update detected. Informed user to use the settings bar."
                )
                return
                    

            logger.info(
                "followedBy.arguments updated from metadata: %s",
                tool_args
            )
        else:
            if tag and selected:
                tool_args[tag] = selected


        site_id_key = f"{session}_site_id"
        site_id_value = redis_client.get(site_id_key)
        logger.info(f"Fetched site_id from Redis key {site_id_key}: {site_id_value}")
        # Initialize client
        db: DatabaseManager = await get_db_manager()
        metadata = SessionMetadataManager()
        client = MeasurePMAsyncClient(sessionId=session, db_manager=db)
        client.sio = sio
        client.metadata = metadata
        client.siteid = site_id_value
        client.sid = sid
        client.function = followedBy

        # Define and call function
        tool_name = followedBy.get("name")
        available_functions = {
            "book_appointment": client.book_appointment,
        }

        if tool_name not in available_functions:
            raise Exception(f"Function {tool_name} not found")

        function_to_call = available_functions[tool_name]
        logger.info(f"Calling {tool_name} with args: {tool_args}")

        result = await function_to_call(**tool_args)


        logger.info(f"✅ Completed {tool_name} for session {session}")
        return result

    @sio.event
    async def selected_client(sid, data):
        logger.info("client selection called: %s", data)
        logger.info("Starting appointment with the sid id %s", sid)

        try:
            return await process_client_selection(
                sid=sid,
                selected=data.get("selected"),
                tag=data.get("tag"),
                followedBy=data.get("followedBy", {}),
                session=data.get("sessionId") or data.get("session_id"),
                user_message=data.get("user_message"), 
                selected_client=data.get("selected_client"),
                selected_service=data.get("selected_service"),
                selected_location=data.get("selected_location"),
            )
        except Exception as e:
            logger.exception("Error in selected_client: %s", e)
            session_id = data.get("sessionId") or data.get("session_id")

    @sio.event
    async def rejoin_sid(sid, data):
        """
        Re-attach a reconnecting socket to rooms and session data from a previous socket id.

        Expects payload: {"oldSid": "<old>", "newSid": "<new>"}
        Returns an ack dict {"success": True/False, "error": "..."}

        This makes the new socket join every room the old socket was in (including
        per-session rooms). That way background tasks which still emit to the
        old sid (or rooms) will reach the new connection.
        """
        old_sid = None
        new_sid = None
        logger.info("Rejoining socket:::::::::::::::::::::::::")
        try:
            old_sid = data.get("oldSid") or data.get("old_sid") or data.get("old")
            new_sid = sid # Use current sid
            session_id = data.get("sessionId") or data.get("session_id")
        except Exception:
            pass

        if session_id:
            await sio.enter_room(sid, session_id)
            logger.info("Socket %s joined session room %s", sid, session_id)

        if not old_sid:
            # If no oldSid is provided, we just joined the session room and we are done
            return {"success": True}

        try:
            # Copy session data if available
            try:
                old_session = await sio.get_session(old_sid)
            except Exception:
                old_session = None

            if old_session:
                try:
                    await sio.save_session(new_sid, old_session)
                except Exception:
                    logger.debug("Could not copy session from %s to %s", old_sid, new_sid)

            # Get rooms for the old sid and add the new sid to them.
            try:
                old_rooms = sio.rooms(old_sid) or []
            except Exception:
                old_rooms = []

            for room in list(old_rooms):
                # skip the internal room that's the new sid itself
                if room == new_sid or room == old_sid:
                    continue
                try:
                    await sio.enter_room(new_sid, room)
                except Exception:
                    logger.exception("Failed to add new sid %s to room %s", new_sid, room)

            # Optionally, remove the old sid from non-sid rooms to avoid duplicates
            for room in list(old_rooms):
                if room == old_sid:
                    # keep the per-sid room for the old id if needed; leaving it is fine
                    continue
                try:
                    await sio.leave_room(old_sid, room)
                except Exception:
                    # not critical
                    pass

            logger.info("Reattached rooms from %s -> %s", old_sid, new_sid)
            return {"success": True}
        except Exception as e:
            logger.exception("Error handling rejoin_sid: %s", e)
            return {"success": False, "error": str(e)}

    @sio.event
    async def join_sid(sid, data):
        """
        Backwards-compatible alias for 'rejoin_sid'.
        """
        return await rejoin_sid(sid, data)

    @sio.event
    async def pickup_results(sid, data):
        """
        Checks Redis for any missed results and delivers them once.
        Expects: {"sessionId": "...", "last_index": -1}
        """
        session_id = data.get("sessionId") or data.get("session_id")
        last_index = data.get("last_index", -1)
        
        if not session_id:
            return {"success": False, "error": "missing sessionId"}
        
        try:
            # We use the key aligned with MeasurePMAsyncClient._emit_and_cache
            redis_key = f"pending_messages:{session_id}"
            
            # Fetch messages from the next index onwards
            # last_index + 1 to -1 fetches everything after what client already saw
            missed_messages_raw = redis_client.lrange(redis_key, last_index + 1, -1)
            
            if missed_messages_raw:
                logger.info("Delivering %d missed messages from Redis to %s", len(missed_messages_raw), sid)
                
                for msg_raw in missed_messages_raw:
                    msg = json.loads(msg_raw)
                    event_name = msg.get("event")
                    payload = msg.get("payload")
                    
                    if event_name and payload:
                        await sio.emit(event_name, payload, to=sid)
                
                # Note: We don't necessarily delete the list here if we want 
                # to allow multiple re-pickups, but usually for CoT, 
                # we might want to expire it after a while or after final result.
                # For now, we keep it so if they disconnect again they can still catch up.
                return {"success": True, "delivered_count": len(missed_messages_raw)}
            
            return {"success": True, "delivered_count": 0}
        except Exception as e:
            logger.exception("Error in pickup_results: %s", e)
            return {"success": False, "error": str(e)}

    async def process_auth_service(
        sid: Optional[str] = None,
        selected: Optional[str] = None,
        tag: Optional[str] = None,
        followedBy: Optional[Dict] = None,
        session: Optional[str] = None,
        user_message: Optional[str] = None,
        selected_client: Optional[str] = None,
        selected_service: Optional[str] = None, 
        selected_location: Optional[str] = None,
    ) -> dict:
        """
        Unified auth + service processor (mirrors process_client_selection pattern)
        """

        logger.info(
            "Processing auth service: selected=%s tag=%s session=%s",
            selected,
            tag,
            session
        )

        if session:
            set_session(str(session))

        followedBy = followedBy or {}        
        updated_keys: set = set()

        # Handle metadata updates from user_message
        if user_message:
            tool_args = dict(followedBy.get("arguments", {}))
            logger.debug("tool_args before metadata update: %s", tool_args)

            metadata_manager = SessionMetadataManager()
            current_metadata = metadata_manager.read_metadata(session)

            metadata_result, tool_args, updated_keys, updated_metadata = await process_metadata_update(
                metadata=tool_args,
                user_message=user_message,
                followedBy=followedBy,
                tag=tag,
                selected=selected,
                sio=sio,         
                session=session,  
                sid=sid, 
                emit_name="auth_service"   ,
                selected_client=selected_client,
                selected_service=selected_service,
                selected_location=selected_location,      
            )

            # If no metadata was updated and message was emitted, return early
            if not updated_keys and not updated_metadata:
                logger.info("Assistant message emitted, skipping function call")
                return

            required_keys = {"miles", "language", "gender", "distance", "treatment_team"}
            if required_keys.intersection(updated_keys):
                    await sio.emit(
                        f"{session}_final_suggested_provider",
                        {
                            "content": (
                                "To update miles, language, gender, distance, or treatment team, "
                                "please use the settings bar."
                            ), 
                        "followedBy": followedBy, 
                        "tag_name":"selected_suggested_provider", 
                        "final_response": "True",
                        "selected_service": selected_service,
                        "selected_client": selected_client, 
                        "selected_location": selected_location
                        },
                        to=sid,
                    )
                    logger.info(
                        "Restricted field update detected. Informed user to use the settings bar."
                    )
                    return
            # if updated_metadata:
            #     tool_args.update(updated_metadata)

            # # Remove all null / None values
            # tool_args = {
            #     k: v
            #     for k, v in tool_args.items()
            #     if v is not None and (not isinstance(v, str) or v.strip() != "")
            # }

            # # Keep followedBy.arguments in sync
            # followedBy["arguments"] = tool_args

            logger.info(
                "followedBy.arguments updated from metadata: %s",
                tool_args
            )
        else:
            tool_args = dict(followedBy.get("arguments", {}))
            if tag and selected:
                tool_args[tag] = selected
            
            # Add selected_client if client_name not updated
            if "client_name" not in updated_keys and selected_client:
                tool_args["selected_client"] = selected_client
            
            if selected_service:
                tool_args["selected_service"] = selected_service
            
        # Initialize MeasurePM client
        db: DatabaseManager = await get_db_manager()
        metadata = SessionMetadataManager()
        site_id_key = f"{session}_site_id"
        site_id_value = redis_client.get(site_id_key)
        logger.info(f"Fetched site_id from Redis key {site_id_key}: {site_id_value}")
        client = MeasurePMAsyncClient(sessionId=session, db_manager=db)
        client.sio = sio
        client.metadata = metadata
        client.siteid = site_id_value
        client.sid = sid
        client.function = followedBy

        # Define and call function
        tool_name = followedBy.get("name")
        available_functions = {
            "book_appointment": client.book_appointment,
        }

        if tool_name not in available_functions:
            raise Exception(f"Function {tool_name} not found")

        function_to_call = available_functions[tool_name]
        logger.info("Calling %s with args: %s", tool_name, tool_args)

        result = await function_to_call(**tool_args)

        logger.info("✅ Completed %s for session %s", tool_name, session)
        return result
    
    @sio.event
    async def auth_service(sid, data):
        logger.info("auth_service called: %s", data)
        session_id = data.get("sessionId") or data.get("session_id")
        if session_id:
            await sio.enter_room(sid, session_id)
        try:
            logger.info("Starting appointment with the sid id %s",sid)
            return await process_auth_service(
                sid=sid,
                selected=data.get("selected"),
                tag=data.get("tag"),
                followedBy=data.get("followedBy", {}),
                session=data.get("sessionId") or data.get("session_id"),
                user_message=data.get("user_message"),
                selected_client=data.get("selected_client"),
                selected_service=data.get("selected_service"),
                selected_location=data.get("selected_location"),
            )
        except Exception as e:
            logger.exception("Error in auth_service: %s", e)
            session_id = data.get("sessionId") or data.get("session_id")
    
    async def process_location_selection(
        *,
        sid: Optional[str] = None,
        selected: Optional[str] = None,
        tag: Optional[str] = None,
        followedBy: Optional[Dict] = None,
        session: Optional[str] = None,
        user_message: Optional[str] = None,
        selected_client: Optional[str] = None,
        selected_service: Optional[str] = None,
        selected_location: Optional[str] = None,
    ) -> dict:

        logger.info(
            "Processing location selection: selected=%s tag=%s session=%s",
            selected,
            tag,
            session,
        )

        if session:
            set_session(str(session))

        followedBy = followedBy or {}
        tool_args = dict(followedBy.get("arguments", {}))
        updated_keys: set = set()

        # 🔐 Initialize guards
        matched = False
        data = None
        skip_metadata_processing = False

        # =========================
        # Auto location detection
        # =========================
        if user_message:
            metadata_manager = SessionMetadataManager()
            metadata = metadata_manager.read_metadata(session)

            db = await get_db_manager()
            client = MeasurePMAsyncClient()
            client.setdb_instance(db)
            client.redis_client = redis_client
            client.metadata = metadata_manager
            client.sessionId = session
            client.sid = sid
            client.sio = sio

            matched, data = await client.get_location_id(
                metadata=metadata,
                user_location_name=user_message,
                checkable=True,
            )

        # =========================
        # Handle user_message
        # =========================
        if user_message:
            if matched:
                logger.info("Location resolved via checkable mode, skipping metadata processing")

                if selected_client:
                    tool_args["selected_client"] = selected_client
                if selected_service:
                    tool_args["selected_service"] = selected_service

                tool_args["selected_location"] = data  # "Name|ID"
                followedBy["arguments"] = tool_args
                skip_metadata_processing = True

            if not skip_metadata_processing:
                metadata_manager = SessionMetadataManager()

                metadata_result, tool_args, updated_keys, updated_metadata = await process_metadata_update(
                    metadata=tool_args,
                    user_message=user_message,
                    followedBy=followedBy,
                    tag=tag,
                    selected=selected,
                    sio=sio,
                    session=session,
                    sid=sid,
                    emit_name="location",
                    selected_client=selected_client,
                    selected_service=selected_service,
                    selected_location=selected_location,
                )

                if not updated_keys and not updated_metadata:
                    logger.info("Assistant message emitted, skipping function call")
                    return

                restricted_keys = {"miles", "language", "gender", "distance", "treatment_team"}
                if restricted_keys.intersection(updated_keys):
                    await sio.emit(
                        f"{session}_final_suggested_provider",
                        {
                            "content": (
                                "To update miles, language, gender, distance, or treatment team, "
                                "please use the settings bar."
                            ),
                            "followedBy": followedBy,
                            "tag_name": "selected_suggested_provider",
                            "final_response": "True",
                            "selected_service": selected_service,
                            "selected_client": selected_client,
                            "selected_location": selected_location,
                        },
                        to=sid,
                    )
                    logger.info("Restricted field update detected.")
                    return

            logger.info("followedBy.arguments updated: %s", tool_args)

        else:
            if tag and selected:
                tool_args[tag] = selected
            if selected_client:
                tool_args["selected_client"] = selected_client
            if selected_service:
                tool_args["selected_service"] = selected_service

        # =========================
        # Call final function
        # =========================
        db: DatabaseManager = await get_db_manager()
        metadata = SessionMetadataManager()

        site_id_key = f"{session}_site_id"
        site_id_value = redis_client.get(site_id_key)

        client = MeasurePMAsyncClient(sessionId=session, db_manager=db)
        client.sio = sio
        client.metadata = metadata
        client.siteid = site_id_value
        client.sid = sid
        client.function = followedBy

        tool_name = followedBy.get("name")
        available_functions = {
            "book_appointment": client.book_appointment,
        }

        if tool_name not in available_functions:
            raise ValueError(f"Function '{tool_name}' not found")

        logger.info("Calling %s with args: %s", tool_name, tool_args)
        result = await available_functions[tool_name](**tool_args)

        logger.info("✅ Completed location selection for session %s", session)
        return result

    @sio.event
    async def location(sid, data):
        logger.info("location selection called: %s", data)
        session_id = data.get("sessionId") or data.get("session_id")
        if session_id:
            await sio.enter_room(sid, session_id)
        try:
            logger.info("Starting appointment with the sid id %s", sid)
            return await process_location_selection(
                sid=sid,
                selected=data.get("selected"),
                tag=data.get("tag"),
                followedBy=data.get("followedBy", {}),
                session=data.get("sessionId") or data.get("session_id"),
                user_message=data.get("user_message"),
                selected_client=data.get("selected_client"),
                selected_service=data.get("selected_service"),
            )
        except Exception as e:
            logger.exception("Error in location: %s", e)
            session_id = data.get("sessionId") or data.get("session_id")

    def has_distance_changed(old_weights: dict, new_weights: dict) -> bool:
        return (
            old_weights.get("maxDistanceInMiles") != new_weights.get("maxDistanceInMiles")
            or old_weights.get("isDistanceEnabled") != new_weights.get("isDistanceEnabled")
        )

    async def handle_distance_change(
        *,
        sid,
        session_id,
        data,
        metadata,
    ):
        """
        Handles side-effects when distance preference changes:
        - Persist updated weights
        - Execute followedBy function (e.g. book_appointment)
        """

        # ✅ Persist updated weights FIRST (single source of truth)
        logger.info("updated weights: %s", data["weights"])
        redis_key_weights = f"{session_id}_weights"
        redis_client.set(
            redis_key_weights,
            json.dumps(data["weights"]),
            ex=settings.expiry_time
        )
        logger.info(
            "Updated distance-related weights saved for session %s",
            session_id
        )

        followedBy = data.get("followedBy")
        if not followedBy or not isinstance(followedBy, dict):
            logger.warning("followedBy not provided for distance change")
            return

        tool_name = followedBy.get("name")
        tool_args = followedBy.get("arguments", {}).copy()

        # Inject optional selections
        for key in ("selected_client", "selected_service", "selected_location"):
            if data.get(key):
                tool_args[key] = data[key]

        # --- Initialize client ---
        db = await get_db_manager()
        client = MeasurePMAsyncClient(sessionId=session_id, db_manager=db)
        client.sio = sio
        client.redis_client = redis_client
        client.metadata = metadata
        client.sid = sid
        client.function = followedBy

        available_functions = {
            "book_appointment": client.book_appointment,
        }

        if tool_name not in available_functions:
            raise ValueError(f"Function '{tool_name}' not found")

        logger.info("Calling %s with args: %s", tool_name, tool_args)

        await available_functions[tool_name](**tool_args)

    @sio.event
    async def updated_weight(sid, data):
        logger.info("Starting appointment with the sid id %s",sid)
        logger.info(f"Received updated_weight event: {data}")
        session_id = data.get("session_id") or data.get("sessionId")
        weights = data.get("weights")
        if not session_id or not weights:
            logger.error("Missing session_id or weights in updated_weight event")
            return
        if session_id:
            set_session(str(session_id))    

        try:
            # ✅ Store weights directly in Redis
            weights_key = f"{session_id}_weights"
            redis_client.set(weights_key, json.dumps(weights), ex=settings.expiry_time)
            logger.info(f"Stored weights for session {session_id} in Redis key {weights_key}")
            await sio.emit(f"{session_id}_weights_updated",{"content":"Weights are been updated"}, to=sid)
        except Exception as e:
            logger.exception(f"Error processing updated_weight event: {e}")
            await sio.emit(
                f"{session_id}_weights_updated",
                {"status": "error", "message": str(e)},
                to=sid
            )



    @sio.on("recalculating_weight")
    async def recalculating_weight(sid, data):
        logger.info("Starting appointment with the sid id %s",sid)
        logger.info("Received recalculating_weight event: %s", data)

        session_id = data.get("session_id") or data.get("sessionId")
        updated_weights = data.get("weights")

        if not session_id or not isinstance(updated_weights, dict):
            await sio.emit(
                f"{session_id}_error",
                {"detail": "Invalid session_id or weights"},
                to=sid
            )
            return

        set_session(str(session_id))
        metadata = get_metadata_manager()

        # Fetch old weights
        redis_key_weights = f"{session_id}_weights"
        old_weights_raw = redis_client.get(redis_key_weights)
        old_weights = {}

        if old_weights_raw:
            try:
                old_weights = json.loads(old_weights_raw)
            except json.JSONDecodeError:
                logger.warning("Invalid old weights JSON for session %s", session_id)

        # Distance change → delegate and exit
        if has_distance_changed(old_weights, updated_weights):
            await handle_distance_change(
                sid=sid,
                session_id=session_id,
                data=data,
                metadata=metadata
            )
            return

        # Persist updated weights
        redis_client.set(
            redis_key_weights,
            json.dumps(updated_weights),
            ex=settings.expiry_time
        )

        await sio.emit(
            f"{session_id}_process",
            "Hang tight! We're updating the rankings with the new weights.",
            to=sid
        )

        # Fetch previously scored employees
        redis_employees = redis_client.get(f"{session_id}_final_scored_emp")
        if not redis_employees:
            await sio.emit(
                f"{session_id}_error",
                {"detail": "No previous results found"},
                to=sid
            )
            return

        response = json.loads(redis_employees)

        # Metadata
        session_metadata = metadata.read_metadata(session_id=session_id)
        preferred_gender = session_metadata.get("preferred_gender")

        # Ranking
        db = await get_db_manager()
        client = MeasurePMAsyncClient()
        client.setdb_instance(db)
        client.redis_client = redis_client
        client.metadata = metadata
        client.sessionId = session_id
        client.sid = sid

        availability, summary, meta = await client.get_ranked_employees(
            response=response,
            metadata=session_metadata,
            preferred_gender=preferred_gender,
            miles=None
        )

        await sio.emit(
            f"{session_id}_final_suggested_provider",
            {
                "content": summary,
                "response": availability,
                "metadata": meta,
                "final_response": "True"
            },
            to=sid
        )

    @sio.event
    async def follow_up(sid, data):
        """
        Handles chat messages via SocketIO.
        Expects payload structure matching ChatRequest DTO:
        {
            "messages": {"message": "Hello!"},
            "weights": {
                "criteria": 0.5,
                "gender": 0.2,
                "language": 0.2,
                "distance": 0.1,
                "isCriteriaEnabled": true,
                "isGenderEnabled": true,
                "isLanguageEnabled": true,
                "isDistanceEnabled": true
            },
            "sessionId": "user-session-id"
        }
        """
        try:
            logger.info("Starting appointment with the sid id %s",sid)
            logger.info(f"chat service called with data: {data}")
            weights = data.get("weights", {})
            session = data.get("sessionId") 
            if session:
                set_session(str(session))
                await sio.enter_room(sid, session)

            user_tz_name = data.get("timezone")
            zone_key = f"{session}_zone"
            redis_client.set(zone_key,user_tz_name, ex=settings.expiry_time)
            
            if not session:
                raise ValueError("Missing sessionId in incoming socket payload.")
            

            weights_key = f"{session}_weights"
            redis_client.set(weights_key, json.dumps(weights), ex=settings.expiry_time)
            logger.info("Stored weights for session %s in Redis key %s", session, weights_key)
            logger.info("Stored timezone for session %s in Redis key %s", session, zone_key)
            
            payload = data.get("user_message") or {}
            

            site_id_key = f"{session}_site_id"
            site_id_value = redis_client.get(site_id_key)
            logger.info(f"Fetched site_id from Redis key {site_id_key}: {site_id_value}")
            # ✅ Initialize dependencies
            db = await get_db_manager()
            metadata = get_metadata_manager()
            client = MeasurePMAsyncClient(sessionId=session, db_manager=db)
            client.sio = sio
            client.metadata = metadata
            client.siteid = site_id_value
            client.sid = sid
            chat_service = ChatServiceImpl(sio=sio, db=db, metadata=metadata)

            await sio.emit(f"{session}_process", "Chat processing started", to=sid)

            await chat_service.process_chat(payload=payload, session=session, client=client, sid=sid )

            logger.debug(f"chat_service completed for session {session}")
        except Exception as e:
            logger.error(f"chat_service error: {str(e)}")



    async def process_book_appointment(
            *,
            sid: Optional[str] = None,
            user_message: Optional[str] = None,
            session: Optional[str] = None,
            tag: Optional[str] = None,
            selected_location: Optional[str] = None,
            followedBy: Optional[Dict] = None,
            employee_id: Optional[str] = None,
            employee_name: Optional[str] = None,
            selected_client: Optional[str] = None,
            selected_service: Optional[str] = None,
        ) -> dict:

            logger.info(
                "Processing book appointment: session=%s employee_id=%s",
                session,
                employee_id,
            )

            if session:
                set_session(str(session))

            
            
            # Handle metadata updates from user_message
            if user_message:
                followedBy = followedBy or {}
                updated_keys: set = set()            
                tool_args = dict(followedBy.get("arguments", {}))
                metadata_manager = SessionMetadataManager()
                current_metadata = metadata_manager.read_metadata(session)

                metadata_result, tool_args, updated_keys, updated_metadata = await process_metadata_update(
                    metadata=tool_args,
                    user_message=user_message,
                    followedBy=followedBy,
                    tag=tag,
                    selected=None,
                    sio=sio,        
                    session=session,
                    sid=sid, 
                    emit_name="book_appointment"      , 
                    selected_client=selected_client,
                    selected_service=selected_service,
                    selected_location=selected_location,    
                )
                logger.info("Metadata update result: %s", metadata_result)
                logger.info("Updated keys: %s", updated_keys)
                logger.info("Updated metadata: %s", updated_metadata)
                logger.info("Tool args: %s", tool_args)

                if not updated_keys and not updated_metadata:
                    logger.info("Assistant message emitted, skipping function call")
                    return
                
                required_keys = {"miles", "language", "gender", "distance", "treatment_team"}
                if required_keys.intersection(updated_keys):
                    await sio.emit(
                        f"{session}_final_suggested_provider",
                        {
                            "content": (
                                "To update miles, language, gender, distance, or treatment team, "
                                "please use the settings bar."
                            ), 
                            "followedBy": followedBy, 
                            "tag_name":"selected_suggested_provider", 
                            "final_response": "True",
                            "selected_service": selected_service,
                            "selected_client": selected_client, 
                            "selected_location": selected_location
                                },
                        to=sid,
                    )
                    logger.info(
                        "Restricted field update detected. Informed user to use the settings bar."
                    )
                    return

                # if updated_metadata:
                #     tool_args.update(updated_metadata)

                # # Remove all null / None values
                # tool_args = {
                #     k: v
                #     for k, v in tool_args.items()
                #     if v is not None and (not isinstance(v, str) or v.strip() != "")
                # }

                # # Keep followedBy.arguments in sync
                # followedBy["arguments"] = tool_args

                logger.info(
                    "followedBy.arguments updated from metadata: %s",
                    tool_args
                )

                # Initialize and call the function
                db: DatabaseManager = await get_db_manager()
                metadata = SessionMetadataManager()

                site_id_key = f"{session}_site_id"
                site_id_value = redis_client.get(site_id_key)
                logger.info(f"Fetched site_id from Redis key {site_id_key}: {site_id_value}")
                client = MeasurePMAsyncClient(sessionId=session, db_manager=db)
                client.sio = sio
                client.metadata = metadata
                client.siteid = site_id_value
                client.sid = sid
                client.function = followedBy

                tool_name = followedBy.get("name")
                available_functions = {
                    "book_appointment": client.book_appointment,
                }

                if tool_name not in available_functions:
                    raise ValueError(f"Function '{tool_name}' not found")

                function_to_call = available_functions[tool_name]

                logger.info("Calling %s with args: %s", tool_name, tool_args)

                result = await function_to_call(**tool_args)
                return result

            # No user_message - proceed with booking API call
            # Fetch payload & timezone

            await sio.emit(
            f"{session}_process",
            "Almost there! We're confirming your appointment info",
            to=sid
                )
            redis_key = f"{session}_appointment_payload"
            payload = json.loads(redis_client.get(redis_key))
            logger.debug("Fetched appointment payload from Redis: %s", payload)
            # If payload exists but is empty
            if not payload:
                await sio.emit(
                    f"{session}_book_appointment",
                    {
                        "success": False,
                        "detail": "Appointment payload is empty.Please Try again",
                    },
                    to=sid,
                )
                return

            logger.debug("Fetched appointment payload from Redis: %s", payload)

            # Convert times
            date = payload.get("start")
            start_utc = date.rstrip("Z")
            end_date = payload.get("endDate")
            end_utc = end_date.rstrip("Z")
            logger.debug("Converted start time to UTC: %s", start_utc)
            logger.debug("Converted end time to UTC: %s", end_utc)
            # Build request body
            try:
                request_body = {
                    "request": [
                        {
                            "siteId": int(payload["siteId"]),
                            "appointmentId": 0,
                            "patientId": int(payload["patientId"]),
                            "authId": int(payload["authId"]),
                            "authDetailId": int(payload["authDetailId"]),
                            "employeeId": int(employee_id),
                            "serviceTypeId": int(payload["serviceTypeId"]),
                            "serviceSubTypeId": int(payload.get("serviceSubTypeId") or 0),
                            "appointmentStatusId": 1315,
                            "appointmentStatusCategoryId": 2,
                            "locationId": int(payload["locationId"]),
                            "timeZoneOffset": 0,

                            # ✅ UTC timestamps
                            "start": start_utc,
                            "startDate": start_utc,
                            "scheduledDate": start_utc,
                            "endDate": end_utc,

                            "scheduledMinutes": int(
                                payload.get("scheduledMinutes")
                                or payload.get("scheduled_minutes")
                                or 0
                            ),
                            "miles": 0,
                            "notes": payload.get("notes", ""),
                            "isBillable": True,
                            "isNonPayable": False,
                            "isInternalAppointment": False,
                            "hasPayroll": False,
                            "hasBilling": False,
                            "appointmentStatus": "Confirmed",
                            "message": "",
                            "isSuccess": True
                        }
                    ],
                    "pageSize": 0,
                    "pageNumber": 0
                }
                logger.info("request body %s", request_body)
                logger.debug("Constructed request body: %s", request_body)
            except Exception as e:
                logger.exception("Error sending booking request")
                return {
                    "success": False,
                    "message": "Failed to connect to booking service. Please try again later.",
                }
            try:
                url = settings.booking_api_url
                login_data_redis_key = f"{session}_login_data"
                login_data = redis_client.get(login_data_redis_key)

                if not login_data:
                    raise ValueError("No login data found in Redis")

                login_data = json.loads(login_data)
                authorization = login_data.get("authorization")

                if not authorization:
                    raise ValueError("Authorization token missing")
                
                logger.debug("Request body to be sent: %s", json.dumps(request_body, indent=2))
                logger.debug("Booking API URL used: %s", url)
                logger.debug("Authorization token: %s", authorization)
                headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {authorization}", 
                        "SiteId": payload["siteId"]
                    }
                logger.debug("Headers: %s", headers)
                response = requests.post(
                    url,
                    json=request_body,
                    headers=headers
                )
                logger.info("authorization: %s" , authorization)
                logger.info("Booking response before the json loading: %s", response)
                logger.info("Status code: %s", response.status_code)
                if response.status_code != 200:

                    logger.error(
                        "Booking API returned non-200 status: %s, body: %s",
                        response.status_code,
                        response.text,
                    )

                    fallback_message = (
                        "Something went wrong while booking the appointment. "
                        "Please try again later."
                    )

                    try:
                        summarized_suggest_employee = [
                            {
                                "role": "user",
                                "content": "Rewrite the following message to be polite, clear, and user-friendly.  Do not mention internal errors or technical details.\n\n Message:\n Something went wrong while booking the appointment. Please try again later."
                            },
                        ]

                        summarized_suggestion_process = TriggerModel(
                            message=summarized_suggest_employee
                        )
                        summarized_suggestion_response = (
                            await summarized_suggestion_process.excecute_hf()
                        )

                        model_content = json.loads(summarized_suggestion_response).get(
                            "content", fallback_message
                        )

                        user_message = model_content.strip() or fallback_message

                    except Exception as e:
                        logger.exception(
                            "Error while generating model-based error message: %s", e
                        )
                        user_message = fallback_message

                    await sio.emit(
                        f"{session}_book_appointment",
                        {"detail": user_message},
                        to=sid,
                    )
                    return


                logger.info("Raw response text: %r", response.text)
                response_json = response.json()
                logger.debug("Booking actual response after json loading: %s",response_json )
                item = response_json["items"][0]
                logger.info("booking API response: %s ", item)
                logger.debug("Booking API response: %s", item)
            except Exception as e:
                logger.error("Error sending request: %s", e)
                return
            return {
                "success": item.get("isSuccess"),
                "message": item.get("message"),
                "payload": payload,
                "employee_name": employee_name,
                "start_utc": start_utc,
            }

    @sio.event
    async def book_appointment(sid, data):
        logger.info("book_appointment called: %s", data)
        session=data.get("sessionId") or data.get("session_id")
        logger.info("Starting appointment with the sid id %s",sid)
        result = await process_book_appointment(
            sid=sid,
            user_message=data.get("user_message"),
            session=data.get("sessionId") or data.get("session_id"),
            followedBy=data.get("followedBy", {}),
            tag=data.get("tag"),
            employee_id=data.get("EmployeeId"),
            selected_client=data.get("selected_client"),
            selected_service=data.get("selected_service"),
            selected_location=data.get("selected_location"),
            employee_name=data.get("EmployeeFullName"),
        )

        session = data.get("sessionId") or data.get("session_id")
        if not result:
            logger.warning("process_book_appointment returned None")
            return
        if result and result.get("success"):
            date = result["payload"].get("start")
            start_date = date.rstrip("Z")
            await sio.emit(
                f"{session}_book_appointment",
                {
                    "sucess": True,
                    "detail": result["message"],
                    "client_name": result["payload"].get("clientName"), 
                    "Employee_name": result["employee_name"],
                    "service_name": result["payload"].get("serviceName"),
                    "location_name": result["payload"].get("locationName"),
                    "duration": result["payload"].get("scheduled_minutes"),
                    "auth_name": result["payload"].get("AuthorizationName"),
                    "date": start_date,
                    "clearSession": True,   
                },
                to=sid,
            )
        else:
            await sio.emit(
                f"{session}_book_appointment",
                {"detail": result["message"], "sucess": False},
                to=sid,
            )

        return result
    
    @sio.on('*')
    def catch_all(event, data):
        logger.debug("Catch-all event received: %s with data: %s", event, data)