from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from database import (
    get_patient_profile,
    get_patient_reports,
    get_latest_report,
    get_report_count,
    search_reports
)
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI through LangChain
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)


def compare_reports(patient_id):
    """
    Compares current report with past reports
    Finds trends and changes over time
    Uses LangChain to intelligently analyze
    """

    # Get all reports from database
    all_reports = get_patient_reports(patient_id)

    if len(all_reports) < 2:
        return "Not enough reports to compare yet. Upload more reports over time to see trends."

    # Prepare reports for comparison
    reports_text = ""
    for i, report in enumerate(all_reports):
        reports_text += f"""
        === REPORT {i+1} - Date: {report.get('date', 'Unknown')} ===
        {report.get('full_explanation', report.get('explanation', 'No explanation available'))}
        """

    # LangChain prompt for comparison
    comparison_prompt = PromptTemplate(
        input_variables=["reports"],
        template="""
        You are a medical health tracker. You have multiple medical reports 
        from the same patient over different time periods.
        
        Here are all the reports in order from newest to oldest:
        {reports}
        
        Please analyze these reports and provide:
        
        1. 📈 HEALTH TRENDS
           - Which values are improving over time
           - Which values are getting worse over time
           - Which values are staying stable
        
        2. 🔴 AREAS OF CONCERN
           - Values that have been consistently abnormal
           - Any new problems that appeared recently
        
        3. ✅ IMPROVEMENTS
           - Values that have improved since last report
           - Positive health changes
        
        4. 📊 OVERALL HEALTH PROGRESS
           - Is overall health improving or declining
           - Simple summary of health journey
        
        5. 💡 RECOMMENDATIONS
           - What the patient should focus on
           - What to discuss with doctor at next visit
        
        Use simple language. Be encouraging but honest.
        Always end with: Please consult your doctor for professional medical advice.
        """
    )

    # Create LangChain chain
    comparison_chain = LLMChain(
        llm=llm,
        prompt=comparison_prompt
    )

    # Run the chain
    result = comparison_chain.invoke({"reports": reports_text})
    return result["text"]


def get_health_summary(patient_id):
    """
    Creates a complete health summary for a patient
    Based on all their reports
    """
    patient = get_patient_profile(patient_id)
    all_reports = get_patient_reports(patient_id)

    if not all_reports:
        return "No reports found for this patient."

    # Prepare all report data
    reports_text = ""
    for report in all_reports:
        reports_text += f"""
        Date: {report.get('date', 'Unknown')}
        Report Type: {report.get('report_type', 'General')}
        Explanation: {report.get('full_explanation', '')}
        Advisor Notes: {report.get('full_advisor_notes', '')}
        ---
        """

    # Patient basic info
    patient_info = f"""
    Name: {patient.get('name')}
    Age: {patient.get('age')}
    Gender: {patient.get('gender')}
    Blood Group: {patient.get('blood_group')}
    Chronic Conditions: {patient.get('chronic_conditions')}
    Current Medications: {patient.get('current_medications')}
    BMI: {patient.get('bmi')} ({patient.get('bmi_category')})
    """

    summary_prompt = PromptTemplate(
        input_variables=["patient_info", "reports"],
        template="""
        You are a personal health advisor creating a complete health summary.
        
        PATIENT INFORMATION:
        {patient_info}
        
        ALL MEDICAL REPORTS:
        {reports}
        
        Create a complete and easy to understand health summary that includes:
        
        1. 👤 PATIENT OVERVIEW
           - Brief summary of who the patient is
           - Key health background
        
        2. 🏥 HEALTH HISTORY SUMMARY
           - Summary of all reports
           - Key findings from each report
        
        3. 🔴 CURRENT HEALTH CONCERNS
           - Active issues that need attention
           - Values that are abnormal
        
        4. ✅ POSITIVE HEALTH INDICATORS
           - Things that are looking good
           - Improvements made
        
        5. 📋 COMPLETE HEALTH TIMELINE
           - Month by month health changes
        
        6. 🎯 ACTION PLAN
           - Top 5 things patient should do right now
           - Lifestyle changes recommended
           - Tests that should be done next
        
        Write in simple friendly language.
        Always end with: Please consult your doctor for professional medical advice.
        """
    )

    summary_chain = LLMChain(
        llm=llm,
        prompt=summary_prompt
    )

    result = summary_chain.invoke({
        "patient_info": patient_info,
        "reports": reports_text
    })

    return result["text"]


def answer_health_question(patient_id, question):
    """
    Answers any health question the patient has
    Based on their own reports and health history
    """
    patient = get_patient_profile(patient_id)
    latest_report = get_latest_report(patient_id)
    report_count = get_report_count(patient_id)

    # Search for relevant reports based on question
    relevant_reports = search_reports(patient_id, question)

    # Prepare context
    patient_context = f"""
    Patient: {patient.get('name')}, Age: {patient.get('age')}
    Blood Group: {patient.get('blood_group')}
    Chronic Conditions: {patient.get('chronic_conditions')}
    Current Medications: {patient.get('current_medications')}
    Known Allergies: {patient.get('known_allergies')}
    Total Reports on File: {report_count}
    """

    latest_context = ""
    if latest_report:
        latest_context = f"""
        Latest Report Date: {latest_report.get('date')}
        Latest Report Summary: {latest_report.get('full_explanation', '')[:1000]}
        """

    relevant_context = ""
    if relevant_reports:
        for report in relevant_reports[:3]:
            relevant_context += f"""
            Relevant Report ({report.get('date')}):
            {report.get('full_explanation', '')[:500]}
            ---
            """

    question_prompt = PromptTemplate(
        input_variables=["patient_context", "latest_report", "relevant_reports", "question"],
        template="""
        You are a personal health assistant answering questions based on 
        a patient's medical history and reports.
        
        PATIENT BACKGROUND:
        {patient_context}
        
        LATEST REPORT:
        {latest_report}
        
        RELEVANT PAST REPORTS:
        {relevant_reports}
        
        PATIENT QUESTION:
        {question}
        
        Please answer this question:
        - Based on their actual medical reports and history
        - In simple easy to understand language
        - Be specific to this patient not generic
        - If the answer is not in their reports say so honestly
        - Be reassuring but accurate
        
        Always end with: Please consult your doctor for professional medical advice.
        """
    )

    question_chain = LLMChain(
        llm=llm,
        prompt=question_prompt
    )

    result = question_chain.invoke({
        "patient_context": patient_context,
        "latest_report": latest_context,
        "relevant_reports": relevant_context,
        "question": question
    })

    return result["text"]


def get_medication_check(patient_id):
    """
    Checks current medications against report findings
    Flags any concerns
    """
    patient = get_patient_profile(patient_id)
    latest_report = get_latest_report(patient_id)

    if not latest_report:
        return "No reports found to check medications against."

    medications = patient.get("current_medications", "None reported")

    if medications == "None reported":
        return "No current medications on file."

    medication_prompt = PromptTemplate(
        input_variables=["medications", "report"],
        template="""
        You are a medication safety checker.
        
        CURRENT MEDICATIONS:
        {medications}
        
        LATEST MEDICAL REPORT:
        {report}
        
        Please check:
        1. 💊 Are current medications appropriate given the report findings
        2. ⚠️ Any potential concerns between medications and report values
        3. 🔍 Any values in the report that might be affected by these medications
        4. 📋 Questions to ask doctor about medications at next visit
        
        Use simple language. Be helpful and informative.
        Always end with: Please consult your doctor before making any changes to medications.
        """
    )

    medication_chain = LLMChain(
        llm=llm,
        prompt=medication_prompt
    )

    result = medication_chain.invoke({
        "medications": medications,
        "report": latest_report.get("full_explanation", "")[:1000]
    })

    return result["text"]


def get_lifestyle_recommendations(patient_id):
    """
    Gives personalized lifestyle recommendations
    Based on patient profile and report findings
    """
    patient = get_patient_profile(patient_id)
    latest_report = get_latest_report(patient_id)

    if not latest_report:
        return "No reports found to base recommendations on."

    lifestyle_info = f"""
    Age: {patient.get('age')}
    Gender: {patient.get('gender')}
    BMI: {patient.get('bmi')} ({patient.get('bmi_category')})
    Smoking: {patient.get('smoking_status')}
    Alcohol: {patient.get('alcohol_consumption')}
    Exercise: {patient.get('exercise_frequency')}
    Diet: {patient.get('diet_type')}
    Sleep: {patient.get('sleep_hours')} hours
    Stress: {patient.get('stress_level')}
    Occupation: {patient.get('occupation')}
    Chronic Conditions: {patient.get('chronic_conditions')}
    """

    lifestyle_prompt = PromptTemplate(
        input_variables=["lifestyle", "report"],
        template="""
        You are a personalized lifestyle health coach.
        
        PATIENT LIFESTYLE:
        {lifestyle}
        
        LATEST REPORT FINDINGS:
        {report}
        
        Give specific personalized recommendations for:
        
        1. 🥗 DIET
           - Foods to eat more of based on their report
           - Foods to avoid or reduce
           - Simple meal suggestions
        
        2. 🏃 EXERCISE
           - Type of exercise suitable for them
           - How often and how long
           - Any exercises to avoid
        
        3. 😴 SLEEP
           - Sleep recommendations based on their health
           - Tips for better sleep
        
        4. 🧘 STRESS MANAGEMENT
           - Stress reduction techniques
           - Mental health recommendations
        
        5. 🚫 HABITS TO CHANGE
           - Specific habits affecting their health
           - How to change them gradually
        
        6. 📅 DAILY HEALTH ROUTINE
           - Simple daily routine for better health
        
        Be specific to this patient. Use simple friendly language.
        Always end with: Please consult your doctor before making major lifestyle changes.
        """
    )

    lifestyle_chain = LLMChain(
        llm=llm,
        prompt=lifestyle_prompt
    )

    result = lifestyle_chain.invoke({
        "lifestyle": lifestyle_info,
        "report": latest_report.get("full_explanation", "")[:1000]
    })

    return result["text"]





# compare_reports → Takes all past reports and compares them. Shows what is improving, what is getting worse, what stayed same.
# get_health_summary → Creates a complete health story for the patient based on all their reports combined.
# answer_health_question → Patient can ask any question like "why is my sugar high" and it answers based on their actual reports.
# get_medication_check → Checks if current medications match with report findings and flags any concerns.
# get_lifestyle_recommendations → Gives personalized diet, exercise, sleep and stress recommendations based on their actual health data.