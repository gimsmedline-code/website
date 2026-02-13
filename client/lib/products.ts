export interface Product {
    id: string;
    name: string;
    description: string;
    image: string;
    category: string; // matches the route paths (e.g., 'cardiac-surgery')
}

export const PRODUCTS: Product[] = [
    // Cardiac Surgery
    {
        id: "cs-1",
        name: "Heart Lung Machine Tubing Pack",
        description: "Customizable tubing packs for cardiopulmonary bypass procedures, ensuring biocompatibility and safety.",
        image: "https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&q=80&w=2000",
        category: "cardiac-surgery",
    },
    {
        id: "cs-2",
        name: "Coronary Artery Ostial Cannula",
        description: "Designed for precise delivery of cardioplegia solution directly into the coronary arteries.",
        image: "https://images.unsplash.com/photo-1579684385180-60b8b2cb1e3e?auto=format&fit=crop&q=80&w=2000",
        category: "cardiac-surgery",
    },
    {
        id: "cs-3",
        name: "Aortic Punch",
        description: "High-precision aortic punches for creating clean, round aortotomies during bypass surgery.",
        image: "https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&q=80&w=2000",
        category: "cardiac-surgery",
    },

    // Critical Care
    {
        id: "cc-1",
        name: "High Concentration Oxygen Mask",
        description: "Non-rebreathing mask designed for high concentration oxygen delivery in critical situations.",
        image: "https://images.unsplash.com/photo-1584036561566-b93a50208c3c?auto=format&fit=crop&q=80&w=2000",
        category: "critical-care",
    },
    {
        id: "cc-2",
        name: "Ventilator Circuit",
        description: "Double water trap circuit with humidifier limb for adult and pediatric ventilation support.",
        image: "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&q=80&w=2000",
        category: "critical-care",
    },
    {
        id: "cc-3",
        name: "ICU Patient Monitor",
        description: "Advanced multi-parameter monitoring for real-time tracking of patient vitals.",
        image: "https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&q=80&w=2000",
        category: "critical-care",
    },
    {
        id: "cc-4",
        name: "Anti-Embolism Stockings",
        description: "Thigh-length compression stockings to prevent DVT in bedridden patients.",
        image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=2000",
        category: "critical-care",
    },

    // Cardiology
    {
        id: "cd-1",
        name: "Angiography Catheter",
        description: "Diagnostic catheters designed for excellent torque control and radiopacity.",
        image: "https://images.unsplash.com/photo-1579684385180-60b8b2cb1e3e?auto=format&fit=crop&q=80&w=2000",
        category: "cardiology",
    },
    {
        id: "cd-2",
        name: "PTCA Balloon Catheter",
        description: "High-pressure balloon catheters for percutaneous transluminal coronary angioplasty.",
        image: "https://images.unsplash.com/photo-1631815589968-fdb09a223b1e?auto=format&fit=crop&q=80&w=2000",
        category: "cardiology",
    },
    {
        id: "cd-3",
        name: "ECG Electrodes",
        description: "High-conductivity foam electrodes for stable and clear ECG monitoring.",
        image: "https://images.unsplash.com/photo-1584036561566-b93a50208c3c?auto=format&fit=crop&q=80&w=2000",
        category: "cardiology",
    },

    // Urology
    {
        id: "ur-1",
        name: "Foley Catheter",
        description: "Silicone-coated 2-way Foley catheter for long-term urinary drainage.",
        image: "https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&q=80&w=2000",
        category: "urology",
    },
    {
        id: "ur-2",
        name: "Urine Collection Bag",
        description: "2000ml drainage bag with anti-reflux valve and efficient drainage outlet.",
        image: "https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&q=80&w=2000",
        category: "urology",
    },
    {
        id: "ur-3",
        name: "Ureteral Stunt",
        description: "Double-J ureteral stent sets for temporary internal drainage.",
        image: "https://images.unsplash.com/photo-1579684385180-60b8b2cb1e3e?auto=format&fit=crop&q=80&w=2000",
        category: "urology",
    },

    // Nephrology
    {
        id: "np-1",
        name: "Hemodialysis Catheter Kit",
        description: "Dual-lumen catheter kits designed for short-term vascular access for dialysis.",
        image: "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&q=80&w=2000",
        category: "nephrology",
    },
    {
        id: "np-2",
        name: "Dialyzer",
        description: "High-flux hollow fiber dialyzers for efficient toxin removal.",
        image: "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&q=80&w=2000",
        category: "nephrology",
    },
    {
        id: "np-3",
        name: "Blood Tubing Set for Hemodialysis",
        description: "Universal blood tubing sets compatible with standard dialysis machines.",
        image: "https://images.unsplash.com/photo-1583947215259-38e31be8751f?auto=format&fit=crop&q=80&w=2000",
        category: "nephrology",
    },

    // Interventional Radiology
    {
        id: "ir-1",
        name: "Biopsy Needle",
        description: "Semi-automatic biopsy needles for soft tissue sampling.",
        image: "https://images.unsplash.com/photo-1584036561566-b93a50208c3c?auto=format&fit=crop&q=80&w=2000",
        category: "interventional-radiology",
    },
    {
        id: "ir-2",
        name: "Drainage Catheter",
        description: "Pigtail drainage catheters for abscess and fluid collection drainage.",
        image: "https://images.unsplash.com/photo-1631815589968-fdb09a223b1e?auto=format&fit=crop&q=80&w=2000",
        category: "interventional-radiology",
    },

    // Anesthesiology
    {
        id: "an-1",
        name: "Laryngeal Mask Airway (LMA)",
        description: "Silicone laryngeal masks for secure airway management during anesthesia.",
        image: "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=2000",
        category: "anesthesiology",
    },
    {
        id: "an-2",
        name: "Endotracheal Tube",
        description: "Cuffed and plain endotracheal tubes with murphy eye.",
        image: "https://images.unsplash.com/photo-1631815588090-d4bfec5b1ccb?auto=format&fit=crop&q=80&w=2000",
        category: "anesthesiology",
    },
    {
        id: "an-3",
        name: "Spinal Needle",
        description: "Pencil-point spinal needles for atraumatic dural puncture.",
        image: "https://images.unsplash.com/photo-1584036561566-b93a50208c3c?auto=format&fit=crop&q=80&w=2000",
        category: "anesthesiology",
    },
    {
        id: "an-4",
        name: "Bain Circuit",
        description: "Coaxial anesthesia breathing circuit for controlled ventilation.",
        image: "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&q=80&w=2000",
        category: "anesthesiology",
    },

    // Gastroenterology
    {
        id: "ge-1",
        name: "Endoscopic Biopsy Forceps",
        description: "Disposable biopsy forceps for precise tissue sampling during endoscopy.",
        image: "https://images.unsplash.com/photo-1581594693702-fbdc51b2763b?auto=format&fit=crop&q=80&w=2000",
        category: "gastroenterology",
    },
    {
        id: "ge-2",
        name: "Polypectomy Snare",
        description: "Rotatable snares for effective polyp removal.",
        image: "https://images.unsplash.com/photo-1631815589968-fdb09a223b1e?auto=format&fit=crop&q=80&w=2000",
        category: "gastroenterology",
    },
    {
        id: "ge-3",
        name: "Biliary Stent",
        description: "Plastic biliary stents for reliable drainage.",
        image: "https://images.unsplash.com/photo-1579684385180-60b8b2cb1e3e?auto=format&fit=crop&q=80&w=2000",
        category: "gastroenterology",
    },
];

export const CATEGORY_IMAGES: Record<string, string> = {
    "cardiac-surgery": "https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&q=80&w=2000", // Surgery/OR
    "critical-care": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=2000", // ICU/Monitor
    cardiology: "https://images.unsplash.com/photo-1628348068343-c6a848d2b6dd?auto=format&fit=crop&q=80&w=2000", // Heart structure/ECG
    urology: "https://images.unsplash.com/photo-1631815589968-fdb09a223b1e?auto=format&fit=crop&q=80&w=2000", // Lab/Clean
    nephrology: "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&q=80&w=2000", // Dialysis feel
    "interventional-radiology": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&q=80&w=2000", // MRI/Imaging
    anesthesiology: "https://images.unsplash.com/photo-1631815588090-d4bfec5b1ccb?auto=format&fit=crop&q=80&w=2000", // Mask/Breathing
    gastroenterology: "https://images.unsplash.com/photo-1584036561566-b93a50208c3c?auto=format&fit=crop&q=80&w=2000", // Scope/Clean
};
