import streamlit as st
from extractor import extract_content, get_file_info
from crew import run_medical_crew
from database import (
    create_patient_profile,
    check_patient_exists,
    get_patient_profile,
    save_report,
    get_patient_reports,
    get_report_count,
    get_latest_report,
    get_all_patients
)
from health_records import (
    compare_reports,
    get_health_summary,
    answer_health_question,
    get_medication_check,
    get_lifestyle_recommendations
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Medical Report Explainer",
    page_icon="🏥",
    layout="wide"
)

# ============================================================
# CUSTOM CSS FOR BETTER LOOK
# ============================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="main-header">🏥 Medical Report Explainer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Upload your medical report and understand it in simple language</div>', unsafe_allow_html=True)

st.warning("⚠️ This tool is for educational purposes only. Always consult a qualified doctor for medical advice.")

st.divider()

# ============================================================
# SIDEBAR - PATIENT MANAGEMENT
# ============================================================

with st.sidebar:
    st.header("👤 Patient Management")

    # Show all registered patients
    all_patients = get_all_patients()

    if all_patients:
        st.subheader(f"Registered Patients ({len(all_patients)})")
        for patient in all_patients:
            if st.button(
                f"👤 {patient.get('name')} - Age {patient.get('age')}",
                key=f"select_{patient.get('patient_id')}"
            ):
                st.session_state.patient_id = patient.get("patient_id")
                st.session_state.patient_loaded = True
                st.rerun()

    st.divider()
    st.caption("Built with CrewAI + LangChain + OpenAI")


# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 New Patient",
    "🔍 Analyze Report",
    "📊 Health Records",
    "💬 Ask Questions"
])


# ============================================================
# TAB 1 - NEW PATIENT REGISTRATION
# ============================================================

with tab1:
    st.header("Register New Patient")
    st.write("Fill in patient details. Only Name, Age, Gender and Blood Group are required. Rest is optional but helps give better advice.")

    with st.form("patient_form"):

        st.subheader("Basic Information")
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *", placeholder="John Smith")
            age = st.number_input("Age *", min_value=1, max_value=120, value=25)
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
            blood_group = st.selectbox("Blood Group *", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])

        with col2:
            date_of_birth = st.text_input("Date of Birth", placeholder="DD-MM-YYYY")
            phone = st.text_input("Phone Number", placeholder="+91 9999999999")
            email = st.text_input("Email", placeholder="john@email.com")
            address = st.text_area("Address", placeholder="Full address", height=100)

        st.divider()
        st.subheader("Emergency Contact")
        col3, col4, col5 = st.columns(3)

        with col3:
            emergency_name = st.text_input("Emergency Contact Name", placeholder="Jane Smith")
        with col4:
            emergency_phone = st.text_input("Emergency Contact Phone", placeholder="+91 9999999999")
        with col5:
            emergency_relation = st.text_input("Relation", placeholder="Spouse / Parent / Sibling")

        st.divider()
        st.subheader("Medical Background")
        col6, col7 = st.columns(2)

        with col6:
            allergies = st.text_area("Known Allergies", placeholder="Penicillin, Peanuts etc or None", height=80)
            medications = st.text_area("Current Medications", placeholder="Medicine name and dosage or None", height=80)
            conditions = st.text_area("Chronic Conditions", placeholder="Diabetes, Hypertension etc or None", height=80)
            surgeries = st.text_area("Past Surgeries", placeholder="Appendix removal 2019 etc or None", height=80)

        with col7:
            hospitalizations = st.text_area("Past Hospitalizations", placeholder="Any past hospital stays", height=80)
            family_history = st.text_area("Family Medical History", placeholder="Father had diabetes etc or None", height=80)
            vaccinations = st.text_area("Vaccination History", placeholder="COVID, Flu etc", height=80)

        st.divider()
        st.subheader("Lifestyle")
        col8, col9, col10 = st.columns(3)

        with col8:
            smoking = st.selectbox("Smoking Status", ["Non Smoker", "Ex Smoker", "Smoker", "Not specified"])
            alcohol = st.selectbox("Alcohol Consumption", ["Never", "Occasionally", "Regularly", "Not specified"])
            exercise = st.selectbox("Exercise Frequency", ["Daily", "3-4 times/week", "Once a week", "Rarely", "Never"])

        with col9:
            diet = st.selectbox("Diet Type", ["Vegetarian", "Non Vegetarian", "Vegan", "Mixed", "Not specified"])
            sleep = st.number_input("Sleep Hours per Night", min_value=1, max_value=12, value=7)
            stress = st.selectbox("Stress Level", ["Low", "Moderate", "High", "Very High"])

        with col10:
            occupation = st.text_input("Occupation", placeholder="Software Engineer, Teacher etc")

        st.divider()
        st.subheader("Physical Stats")
        col11, col12 = st.columns(2)

        with col11:
            height = st.number_input("Height (cm)", min_value=0, max_value=250, value=0)
            weight = st.number_input("Weight (kg)", min_value=0, max_value=300, value=0)

        with col12:
            insurance_provider = st.text_input("Insurance Provider", placeholder="Star Health, LIC etc")
            insurance_id = st.text_input("Insurance ID", placeholder="Your policy number")

        st.divider()
        st.subheader("Doctor Information")
        col13, col14 = st.columns(2)

        with col13:
            doctor_name = st.text_input("Primary Doctor Name", placeholder="Dr. Sharma")
            doctor_contact = st.text_input("Doctor Contact", placeholder="Phone or clinic number")

        with col14:
            hospital_name = st.text_input("Hospital / Clinic Name", placeholder="Apollo Hospital")
            hospital_address = st.text_input("Hospital Address", placeholder="Full address")

        st.divider()

        submitted = st.form_submit_button("✅ Register Patient", type="primary", use_container_width=True)

        if submitted:
            if not name or not age or not gender or not blood_group:
                st.error("❌ Please fill in Name, Age, Gender and Blood Group at minimum.")
            else:
                # Check if patient already exists
                existing_id = check_patient_exists(name, age)

                if existing_id:
                    st.warning(f"⚠️ Patient {name} already registered. Loading their profile.")
                    st.session_state.patient_id = existing_id
                    st.session_state.patient_loaded = True
                else:
                    # Create new patient
                    patient_id = create_patient_profile(
                        name=name,
                        age=age,
                        gender=gender,
                        blood_group=blood_group,
                        date_of_birth=date_of_birth,
                        phone=phone,
                        email=email,
                        address=address,
                        emergency_contact_name=emergency_name,
                        emergency_contact_phone=emergency_phone,
                        emergency_contact_relation=emergency_relation,
                        known_allergies=allergies,
                        current_medications=medications,
                        chronic_conditions=conditions,
                        past_surgeries=surgeries,
                        past_hospitalizations=hospitalizations,
                        family_medical_history=family_history,
                        vaccination_history=vaccinations,
                        smoking_status=smoking,
                        alcohol_consumption=alcohol,
                        exercise_frequency=exercise,
                        diet_type=diet,
                        sleep_hours=sleep,
                        stress_level=stress,
                        occupation=occupation,
                        height_cm=height if height > 0 else None,
                        weight_kg=weight if weight > 0 else None,
                        insurance_provider=insurance_provider,
                        insurance_id=insurance_id,
                        primary_doctor_name=doctor_name,
                        primary_doctor_contact=doctor_contact,
                        hospital_name=hospital_name,
                        hospital_address=hospital_address
                    )

                    st.session_state.patient_id = patient_id
                    st.session_state.patient_loaded = True
                    st.success(f"✅ Patient {name} registered successfully!")
                    st.balloons()


# ============================================================
# TAB 2 - ANALYZE REPORT
# ============================================================

with tab2:
    st.header("🔍 Analyze Medical Report")

    # Check if patient is selected
    if "patient_id" not in st.session_state:
        st.info("👈 Please register a new patient in the first tab or select an existing patient from the sidebar.")
    else:
        patient = get_patient_profile(st.session_state.patient_id)
        report_count = get_report_count(st.session_state.patient_id)

        st.success(f"✅ Patient: {patient.get('name')} | Age: {patient.get('age')} | Reports on file: {report_count}")

        st.divider()

        # Report type selector
        report_type = st.selectbox(
            "What type of report are you uploading?",
            [
                "Blood Test",
                "Urine Test",
                "X-Ray Report",
                "MRI Report",
                "CT Scan Report",
                "ECG Report",
                "Ultrasound Report",
                "Discharge Summary",
                "Prescription",
                "Other"
            ]
        )

        # File upload
        uploaded_file = st.file_uploader(
            "Upload Medical Report (PDF or Image)",
            type=["pdf", "png", "jpg", "jpeg"]
        )

        if uploaded_file:
            file_info = get_file_info(uploaded_file)
            st.info(f"📄 File: {file_info['filename']} | Size: {file_info['size']} | Type: {file_info['type']}")

            if st.button("🚀 Analyze Report", type="primary", use_container_width=True):

                # Step 1 - Extract content
                with st.status("Processing your report...", expanded=True) as status:

                    st.write("📄 Reading your report...")
                    extracted_content = extract_content(uploaded_file)

                    if extracted_content["type"] == "error":
                        st.error(f"❌ {extracted_content['content']}")
                        status.update(label="Failed", state="error")

                    else:
                        if extracted_content.get("total_pages"):
                            st.write(f"✅ Read {extracted_content['total_pages']} pages successfully")

                        if extracted_content.get("has_tables"):
                            st.write(f"✅ Found {extracted_content.get('table_count')} tables in report")

                        # Step 2 - Run CrewAI agents
                        st.write("🤖 Agent 1 extracting and organizing data...")
                        st.write("🧠 Agent 2 explaining all values...")
                        st.write("💡 Agent 3 preparing health advice...")

                        crew_result = run_medical_crew(extracted_content)

                        if not crew_result["success"]:
                            st.error(f"❌ Error: {crew_result['error']}")
                            status.update(label="Failed", state="error")

                        else:
                            # Step 3 - Save to database
                            st.write("💾 Saving to health records...")

                            report_text = extracted_content.get("content", "")
                            if isinstance(report_text, bytes):
                                report_text = "Image report"

                            save_report(
                                patient_id=st.session_state.patient_id,
                                report_text=report_text,
                                explanation=crew_result["explanation"],
                                advisor_notes=crew_result["advice"],
                                report_type=report_type
                            )

                            # Save to session
                            st.session_state.crew_result = crew_result
                            st.session_state.report_analyzed = True

                            status.update(label="✅ Analysis Complete!", state="complete")

        # Show results
        if "crew_result" in st.session_state and st.session_state.get("report_analyzed"):

            result = st.session_state.crew_result

            st.divider()

            # Three sections for three agent outputs
            with st.expander("📊 Extracted & Organized Data (Agent 1)", expanded=False):
                st.markdown(result["extraction"])

            with st.expander("📋 Simple Explanation (Agent 2)", expanded=True):
                st.markdown(result["explanation"])

            with st.expander("💡 Health Advice & Next Steps (Agent 3)", expanded=True):
                st.markdown(result["advice"])

            st.success("✅ Report saved to health records successfully!")


# ============================================================
# TAB 3 - HEALTH RECORDS
# ============================================================

with tab3:
    st.header("📊 Health Records & Trends")

    if "patient_id" not in st.session_state:
        st.info("👈 Please register or select a patient first.")
    else:
        patient = get_patient_profile(st.session_state.patient_id)
        report_count = get_report_count(st.session_state.patient_id)

        st.success(f"✅ Viewing records for: {patient.get('name')}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Reports", report_count)
        with col2:
            st.metric("Age", patient.get("age"))
        with col3:
            st.metric("BMI", f"{patient.get('bmi', 'N/A')} ({patient.get('bmi_category', '')})")

        st.divider()

        # Action buttons
        col4, col5, col6 = st.columns(3)

        with col4:
            if st.button("📈 Compare All Reports", use_container_width=True):
                with st.spinner("Analyzing trends across all reports..."):
                    comparison = compare_reports(st.session_state.patient_id)
                    st.session_state.comparison_result = comparison

        with col5:
            if st.button("📋 Full Health Summary", use_container_width=True):
                with st.spinner("Creating complete health summary..."):
                    summary = get_health_summary(st.session_state.patient_id)
                    st.session_state.summary_result = summary

        with col6:
            if st.button("🏃 Lifestyle Recommendations", use_container_width=True):
                with st.spinner("Preparing personalized recommendations..."):
                    lifestyle = get_lifestyle_recommendations(st.session_state.patient_id)
                    st.session_state.lifestyle_result = lifestyle

        # Show results
        if "comparison_result" in st.session_state:
            st.divider()
            st.subheader("📈 Report Comparison & Trends")
            st.markdown(st.session_state.comparison_result)

        if "summary_result" in st.session_state:
            st.divider()
            st.subheader("📋 Complete Health Summary")
            st.markdown(st.session_state.summary_result)

        if "lifestyle_result" in st.session_state:
            st.divider()
            st.subheader("🏃 Personalized Lifestyle Recommendations")
            st.markdown(st.session_state.lifestyle_result)

        st.divider()

        # Show all past reports
        st.subheader("📁 All Past Reports")
        all_reports = get_patient_reports(st.session_state.patient_id)

        if not all_reports:
            st.info("No reports uploaded yet. Go to Analyze Report tab to upload your first report.")
        else:
            for i, report in enumerate(all_reports):
                with st.expander(
                    f"Report {i+1} - {report.get('report_type', 'General')} - {report.get('date', 'Unknown date')}",
                    expanded=False
                ):
                    st.markdown("**Explanation:**")
                    st.markdown(report.get("full_explanation", "No explanation available"))
                    st.divider()
                    st.markdown("**Health Advice:**")
                    st.markdown(report.get("full_advisor_notes", "No advice available"))


# ============================================================
# TAB 4 - ASK QUESTIONS
# ============================================================

with tab4:
    st.header("💬 Ask Questions About Your Health")

    if "patient_id" not in st.session_state:
        st.info("👈 Please register or select a patient first.")
    else:
        patient = get_patient_profile(st.session_state.patient_id)
        st.success(f"✅ Asking about: {patient.get('name')}'s health records")

        st.write("Ask any question about your medical reports and health history. The AI will answer based on your actual reports.")

        # Example questions
        st.caption("Example questions you can ask:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("• Why is my blood sugar high?")
            st.caption("• What does low hemoglobin mean for me?")
        with col2:
            st.caption("• Is my kidney function normal?")
            st.caption("• What should I eat given my reports?")
        with col3:
            st.caption("• Am I at risk for diabetes?")
            st.caption("• What medicines should I take?")

        st.divider()

        # Question input
        user_question = st.text_area(
            "Your Question",
            placeholder="Type your health question here...",
            height=100
        )

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("🔍 Get Answer", type="primary", use_container_width=True):
                if user_question:
                    with st.spinner("Finding answer from your health records..."):
                        answer = answer_health_question(
                            st.session_state.patient_id,
                            user_question
                        )
                        st.session_state.question_answer = answer
                        st.session_state.asked_question = user_question
                else:
                    st.warning("Please type a question first.")

        with col_btn2:
            if st.button("💊 Check My Medications", use_container_width=True):
                with st.spinner("Checking medications against your reports..."):
                    med_check = get_medication_check(st.session_state.patient_id)
                    st.session_state.medication_result = med_check

        # Show answers
        if "question_answer" in st.session_state:
            st.divider()
            st.subheader(f"💡 Answer to: {st.session_state.asked_question}")
            st.markdown(st.session_state.question_answer)

        if "medication_result" in st.session_state:
            st.divider()
            st.subheader("💊 Medication Check")
            st.markdown(st.session_state.medication_result)