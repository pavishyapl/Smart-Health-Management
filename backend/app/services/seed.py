import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.waste import WasteRecord
from app.models.pickup import PickupRequest
from app.models.location import CollectorLocation
from app.auth.security import hash_password
from app.ml.predictor import predictor
from app.services.distance import calculate_haversine_distance

def seed_database(db: Session):
    # 1. Admin Seed
    admin = db.query(User).filter(User.email == "admin@smartmedwaste.org").first()
    if not admin:
        admin = User(
            name="State Biowaste Authority (Admin)",
            email="admin@smartmedwaste.org",
            phone="+91 98765 43210",
            password_hash=hash_password("Admin@123456"),
            role="admin",
            address="Central Medical Waste Regulatory Directorate, Sector 12",
            latitude=28.6139,
            longitude=77.2090
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("[Database Seed] Created primary Admin account (admin@smartmedwaste.org)")

    # 2. Sample Hospitals
    hospitals_data = [
        {
            "name": "Apollo Care Multispecialty Hospital",
            "email": "apollo@medcare.org",
            "phone": "+91 91234 56781",
            "password": "Password@123",
            "role": "hospital",
            "address": "Ring Road Healthcare Hub, Block A",
            "latitude": 28.6289,
            "longitude": 28.6289 and 77.2180 or 77.2180
        },
        {
            "name": "City Life Trauma & Surgical Clinic",
            "email": "citylife@clinic.org",
            "phone": "+91 91234 56782",
            "password": "Password@123",
            "role": "hospital",
            "address": "South Avenue Medical Enclave, Plot 4",
            "latitude": 28.5800,
            "longitude": 77.2300
        },
        {
            "name": "St. Jude Mother & Child Hospital",
            "email": "stjude@hospitals.org",
            "phone": "+91 91234 56783",
            "password": "Password@123",
            "role": "hospital",
            "address": "East End Institutional Area, Gate 2",
            "latitude": 28.6400,
            "longitude": 77.2800
        }
    ]

    hosp_objs = []
    for hd in hospitals_data:
        h = db.query(User).filter(User.email == hd["email"]).first()
        if not h:
            h = User(
                name=hd["name"],
                email=hd["email"],
                phone=hd["phone"],
                password_hash=hash_password(hd["password"]),
                role=hd["role"],
                address=hd["address"],
                latitude=hd["latitude"],
                longitude=hd["longitude"]
            )
            db.add(h)
            db.commit()
            db.refresh(h)
        hosp_objs.append(h)

    # 3. Sample Collectors
    collectors_data = [
        {
            "name": "Rajesh Kumar (Bioclean Rapid Fleet #1)",
            "email": "rajesh.collector@bioclean.in",
            "phone": "+91 98111 22334",
            "password": "Password@123",
            "role": "collector",
            "address": "Central Logistics Depot, Unit 10",
            "latitude": 28.6200,
            "longitude": 77.2120
        },
        {
            "name": "Vikram Singh (EcoSafe Waste Logistics #2)",
            "email": "vikram.collector@ecosafe.in",
            "phone": "+91 98222 33445",
            "password": "Password@123",
            "role": "collector",
            "address": "South Logistics Hub, Sector 5",
            "latitude": 28.5750,
            "longitude": 77.2250
        },
        {
            "name": "Amit Sharma (EnviroMed Van #3)",
            "email": "amit.collector@enviromed.in",
            "phone": "+91 98333 44556",
            "password": "Password@123",
            "role": "collector",
            "address": "North Transport Terminal, Bay 4",
            "latitude": 28.6500,
            "longitude": 77.2700
        }
    ]

    collector_objs = []
    for cd in collectors_data:
        c = db.query(User).filter(User.email == cd["email"]).first()
        if not c:
            c = User(
                name=cd["name"],
                email=cd["email"],
                phone=cd["phone"],
                password_hash=hash_password(cd["password"]),
                role=cd["role"],
                address=cd["address"],
                latitude=cd["latitude"],
                longitude=cd["longitude"]
            )
            db.add(c)
            db.commit()
            db.refresh(c)
        collector_objs.append(c)

    # 4. Sample Waste Records & Initial Pickups for rich initial demo
    existing_waste = db.query(WasteRecord).count()
    if existing_waste == 0 and len(hosp_objs) > 0 and len(collector_objs) > 0:
        h1, h2, h3 = hosp_objs[0], hosp_objs[1], hosp_objs[2]
        c1, c2, c3 = collector_objs[0], collector_objs[1], collector_objs[2]

        samples = [
            # Pending pickup request 1
            {
                "hospital": h1,
                "category": "Red",
                "waste_type": "Contaminated Gloves & IV Tubing",
                "quantity": 28.5,
                "notes": "Stored in cold staging room since morning.",
                "storage_hours": 16.0,
                "status": "Pending",
                "collector": None
            },
            # Pending pickup request 2 (High priority anatomical)
            {
                "hospital": h2,
                "category": "Yellow",
                "waste_type": "Human Anatomical & Soiled Dressing Waste",
                "quantity": 42.0,
                "notes": "Pathology laboratory batch, urgent pickup required.",
                "storage_hours": 26.0,
                "status": "Pending",
                "collector": None
            },
            # Assigned pickup
            {
                "hospital": h1,
                "category": "White",
                "waste_type": "Puncture-Proof Sharps Containers & Scalpels",
                "quantity": 14.0,
                "notes": "Surgical ward sharps.",
                "storage_hours": 10.0,
                "status": "Assigned",
                "collector": c1
            },
            # Historical completed collection 1
            {
                "hospital": h2,
                "category": "Blue",
                "waste_type": "Broken Medicine Ampoules & Vials",
                "quantity": 18.0,
                "notes": "Pharmacy discard glassware.",
                "storage_hours": 24.0,
                "status": "Collected",
                "collector": c2
            },
            # Historical completed collection 2
            {
                "hospital": h3,
                "category": "Yellow",
                "waste_type": "Infectious Laboratory Media & Swabs",
                "quantity": 35.0,
                "notes": "Microbiology department waste.",
                "storage_hours": 30.0,
                "status": "Collected",
                "collector": c3
            },
            # Recorded waste without scheduled pickup
            {
                "hospital": h1,
                "category": "Red",
                "waste_type": "Dialysis Tubing and Catheters",
                "quantity": 15.0,
                "notes": "Generated in Nephrology unit.",
                "storage_hours": 4.0,
                "status": None,
                "collector": None
            }
        ]

        for s in samples:
            w = WasteRecord(
                hospital_id=s["hospital"].id,
                category=s["category"],
                waste_type=s["waste_type"],
                quantity=s["quantity"],
                unit="kg",
                notes=s["notes"],
                is_scheduled=(s["status"] is not None),
                created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=s["storage_hours"])
            )
            db.add(w)
            db.commit()
            db.refresh(w)

            if s["status"] is not None:
                # Run ML Prediction
                dist = calculate_haversine_distance(
                    s["hospital"].latitude, s["hospital"].longitude,
                    s["collector"].latitude if s["collector"] else 28.6139,
                    s["collector"].longitude if s["collector"] else 77.2090
                )
                ml_res = predictor.predict_delay_risk(
                    waste_category=s["category"],
                    waste_quantity=s["quantity"],
                    storage_duration_hours=s["storage_hours"],
                    request_waiting_hours=3.0,
                    pickup_distance_km=dist
                )

                req_time = datetime.datetime.utcnow() - datetime.timedelta(hours=s["storage_hours"] * 0.6)
                assigned_time = req_time + datetime.timedelta(minutes=30) if s["collector"] else None
                accepted_time = assigned_time + datetime.timedelta(minutes=15) if s["status"] in ["Accepted", "Collected"] else None
                completed_time = accepted_time + datetime.timedelta(minutes=45) if s["status"] == "Collected" else None

                p = PickupRequest(
                    hospital_id=s["hospital"].id,
                    collector_id=s["collector"].id if s["collector"] else None,
                    waste_record_id=w.id,
                    status=s["status"],
                    delay_risk=ml_res["risk_level"], # "High", "Medium", "Low"
                    delay_probability=ml_res["delay_probability"],
                    prediction_timestamp=req_time,
                    model_version=ml_res.get("model_version", "rf-delay-v1.0"),
                    priority=ml_res["risk_level"], # Backward compatibility
                    priority_confidence=ml_res["delay_probability"],
                    pickup_address=s["hospital"].address,
                    hospital_latitude=s["hospital"].latitude,
                    hospital_longitude=s["hospital"].longitude,
                    storage_duration_hours=s["storage_hours"],
                    requested_at=req_time,
                    assigned_at=assigned_time,
                    accepted_at=accepted_time,
                    completed_at=completed_time
                )
                db.add(p)
                db.commit()
                db.refresh(p)
        print("[Database Seed] Seeded realistic demo waste records and pickup workflows.")
