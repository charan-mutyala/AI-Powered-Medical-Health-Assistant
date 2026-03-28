import chromadb
import os
import json
from datetime import datetime

# Create folder to store our database
DB_FOLDER = "health_db"
os.makedirs(DB_FOLDER, exist_ok=True)

# Connect to ChromaDB - saves data permanently on your computer
chroma_client = chromadb.PersistentClient(path=DB_FOLDER)

# Two collections - think of these as two tables in a database
patient_collection = chroma_client.get_or_create_collection(name="patients")
reports_collection = chroma_client.get_or_create_collection(name="reports")


def create_patient_profile(
    name,
    age,
    gender,
    blood_group,
    date_of_birth=None,
    phone=None,
    email=None,
    address=None,

    # Emergency contact
    emergency_contact_name=None,
    emergency_contact_phone=None,
    emergency_contact_relation=None,

    # Medical background
    known_allergies=None,
    current_medications=None,
    chronic_conditions=None,
    past_surgeries=None,
    past_hospitalizations=None,
    family_medical_history=None,
    vaccination_history=None,

    # Lifestyle
    smoking_status=None,
    alcohol_consumption=None,
    exercise_frequency=None,
    diet_type=None,
    sleep_hours=None,
    stress_level=None,
    occupation=None,

    # Physical stats
    height_cm=None,
    weight_kg=None,

    # Insurance
    insurance_provider=None,
    insurance_id=None,
    insurance_validity=None,

    # Doctor info
    primary_doctor_name=None,
    primary_doctor_contact=None,
    hospital_name=None,
    hospital_address=None
):
    """
    Creates a complete patient profile
    Saves everything to ChromaDB
    """

    # Generate unique patient ID
    patient_id = f"patient_{name.lower().replace(' ', '_')}_{age}"

    # Auto calculate BMI if height and weight provided
    bmi = None
    bmi_category = None
    if height_cm and weight_kg:
        height_m = float(height_cm) / 100
        bmi = round(float(weight_kg) / (height_m ** 2), 1)

        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

    # Store ALL patient data
    patient_data = {
        # Basic info
        "patient_id": patient_id,
        "name": str(name) if name else "",
        "age": str(age) if age else "",
        "gender": str(gender) if gender else "",
        "blood_group": str(blood_group) if blood_group else "",
        "date_of_birth": str(date_of_birth) if date_of_birth else "",
        "phone": str(phone) if phone else "",
        "email": str(email) if email else "",
        "address": str(address) if address else "",

        # Emergency contact
        "emergency_contact_name": str(emergency_contact_name) if emergency_contact_name else "",
        "emergency_contact_phone": str(emergency_contact_phone) if emergency_contact_phone else "",
        "emergency_contact_relation": str(emergency_contact_relation) if emergency_contact_relation else "",

        # Medical background
        "known_allergies": str(known_allergies) if known_allergies else "None reported",
        "current_medications": str(current_medications) if current_medications else "None reported",
        "chronic_conditions": str(chronic_conditions) if chronic_conditions else "None reported",
        "past_surgeries": str(past_surgeries) if past_surgeries else "None reported",
        "past_hospitalizations": str(past_hospitalizations) if past_hospitalizations else "None reported",
        "family_medical_history": str(family_medical_history) if family_medical_history else "None reported",
        "vaccination_history": str(vaccination_history) if vaccination_history else "None reported",

        # Lifestyle
        "smoking_status": str(smoking_status) if smoking_status else "Not specified",
        "alcohol_consumption": str(alcohol_consumption) if alcohol_consumption else "Not specified",
        "exercise_frequency": str(exercise_frequency) if exercise_frequency else "Not specified",
        "diet_type": str(diet_type) if diet_type else "Not specified",
        "sleep_hours": str(sleep_hours) if sleep_hours else "Not specified",
        "stress_level": str(stress_level) if stress_level else "Not specified",
        "occupation": str(occupation) if occupation else "Not specified",

        # Physical stats
        "height_cm": str(height_cm) if height_cm else "",
        "weight_kg": str(weight_kg) if weight_kg else "",
        "bmi": str(bmi) if bmi else "",
        "bmi_category": str(bmi_category) if bmi_category else "",

        # Insurance
        "insurance_provider": str(insurance_provider) if insurance_provider else "",
        "insurance_id": str(insurance_id) if insurance_id else "",
        "insurance_validity": str(insurance_validity) if insurance_validity else "",

        # Doctor info
        "primary_doctor_name": str(primary_doctor_name) if primary_doctor_name else "",
        "primary_doctor_contact": str(primary_doctor_contact) if primary_doctor_contact else "",
        "hospital_name": str(hospital_name) if hospital_name else "",
        "hospital_address": str(hospital_address) if hospital_address else "",

        # System timestamps
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Searchable document string
    document_text = f"""
    Patient: {name} | Age: {age} | Gender: {gender} | Blood Group: {blood_group}
    DOB: {date_of_birth} | Phone: {phone} | Email: {email}
    Address: {address}
    Emergency: {emergency_contact_name} ({emergency_contact_relation}) - {emergency_contact_phone}
    Allergies: {known_allergies}
    Medications: {current_medications}
    Conditions: {chronic_conditions}
    Surgeries: {past_surgeries}
    Family History: {family_medical_history}
    Lifestyle: Smoking-{smoking_status} | Alcohol-{alcohol_consumption} | Exercise-{exercise_frequency}
    Diet: {diet_type} | Sleep: {sleep_hours}hrs | Stress: {stress_level}
    Height: {height_cm}cm | Weight: {weight_kg}kg | BMI: {bmi} ({bmi_category})
    Insurance: {insurance_provider} - {insurance_id}
    Doctor: {primary_doctor_name} | Hospital: {hospital_name}
    """

    # Save to ChromaDB
    patient_collection.upsert(
        ids=[patient_id],
        documents=[document_text],
        metadatas=[patient_data]
    )

    return patient_id


def update_patient_profile(patient_id, **kwargs):
    """
    Updates specific fields in patient profile
    Only updates what you pass in
    Everything else stays the same
    """
    existing = get_patient_profile(patient_id)

    if not existing:
        return False

    for key, value in kwargs.items():
        if value is not None:
            existing[key] = str(value)

    existing["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    patient_collection.upsert(
        ids=[patient_id],
        documents=[f"Patient: {existing.get('name')}"],
        metadatas=[existing]
    )

    return True


def get_patient_profile(patient_id):
    """
    Gets complete patient profile from database
    """
    try:
        result = patient_collection.get(ids=[patient_id])
        if result and result["metadatas"]:
            return result["metadatas"][0]
        return None
    except:
        return None


def check_patient_exists(name, age):
    """
    Checks if patient already registered
    Returns patient_id if exists, None if not
    """
    patient_id = f"patient_{name.lower().replace(' ', '_')}_{age}"
    profile = get_patient_profile(patient_id)
    return patient_id if profile else None


def save_report(patient_id, report_text, explanation, advisor_notes, report_type=None):
    """
    Saves COMPLETE medical report to database
    Nothing gets cut off - full content saved
    Uses JSON files for large content
    ChromaDB used for fast searching
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_id = f"report_{patient_id}_{timestamp}"

    # Create folder for this patient reports
    report_folder = f"health_db/reports/{patient_id}"
    os.makedirs(report_folder, exist_ok=True)

    # Complete report data - nothing cut off
    full_report = {
        "report_id": report_id,
        "patient_id": patient_id,
        "report_type": report_type or "General",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "timestamp": timestamp,

        # Full content saved completely
        "full_report_text": report_text,
        "full_explanation": explanation,
        "full_advisor_notes": advisor_notes
    }

    # Save as JSON file - no size limit
    json_path = f"{report_folder}/{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)

    # Also index in ChromaDB for searching
    reports_collection.upsert(
        ids=[report_id],
        documents=[explanation],
        metadatas=[{
            "patient_id": patient_id,
            "report_type": report_type or "General",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": timestamp,
            "json_path": json_path
        }]
    )

    return report_id


def get_full_report(report_id):
    """
    Gets complete report with all details
    """
    try:
        result = reports_collection.get(ids=[report_id])

        if result and result["metadatas"]:
            json_path = result["metadatas"][0].get("json_path")

            if json_path and os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None
    except:
        return None


def get_patient_reports(patient_id):
    """
    Gets ALL reports for a patient
    Full content included
    Sorted newest first
    """
    try:
        results = reports_collection.get(
            where={"patient_id": patient_id}
        )

        if not results or not results["metadatas"]:
            return []

        full_reports = []

        for metadata in results["metadatas"]:
            json_path = metadata.get("json_path")

            if json_path and os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    full_reports.append(json.load(f))
            else:
                full_reports.append(metadata)

        # Sort newest first
        full_reports.sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        return full_reports

    except:
        return []


def get_latest_report(patient_id):
    """
    Gets most recent report for patient
    """
    reports = get_patient_reports(patient_id)
    return reports[0] if reports else None


def get_report_count(patient_id):
    """
    Returns total number of reports for patient
    """
    return len(get_patient_reports(patient_id))


def search_reports(patient_id, search_query):
    """
    Search through patient reports using natural language
    Example: search for 'high blood sugar' or 'kidney function'
    """
    try:
        results = reports_collection.query(
            query_texts=[search_query],
            n_results=5,
            where={"patient_id": patient_id}
        )

        if results and results["ids"] and results["ids"][0]:
            full_reports = []
            for report_id in results["ids"][0]:
                report = get_full_report(report_id)
                if report:
                    full_reports.append(report)
            return full_reports

        return []
    except:
        return []


def get_all_patients():
    """
    Returns list of all registered patients
    """
    try:
        results = patient_collection.get()
        if results and results["metadatas"]:
            return results["metadatas"]
        return []
    except:
        return []


def delete_patient(patient_id):
    """
    Deletes a patient and all their reports
    """
    try:
        # Delete patient profile
        patient_collection.delete(ids=[patient_id])

        # Delete all their reports from ChromaDB
        results = reports_collection.get(
            where={"patient_id": patient_id}
        )

        if results and results["ids"]:
            reports_collection.delete(ids=results["ids"])

        # Delete their report folder
        import shutil
        report_folder = f"health_db/reports/{patient_id}"
        if os.path.exists(report_folder):
            shutil.rmtree(report_folder)

        return True
    except:
        return False

# **What is new in this version:**

# Full content saved → Report text, explanation and advisor notes saved completely using JSON files. No size limits.

# Auto BMI calculation → Calculates BMI and category automatically from height and weight

# Search reports → Search through past reports using natural language

# Delete patient → Removes patient and all their reports cleanly

# JSON + ChromaDB combo → JSON handles large content storage, ChromaDB handles fast searching



# **Your health_db folder structure after saving:**

# health_db/
# ├── reports/
# │   └── patient_john_25/
# │       ├── 20240301_143022.json  ← complete report 1
# │       ├── 20240401_091545.json  ← complete report 2
# │       └── 20240501_112233.json  ← complete report 3