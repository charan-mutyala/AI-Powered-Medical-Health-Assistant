from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import os
import base64
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI model for all agents
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)


# ============================================================
# DEFINE ALL 3 AGENTS
# ============================================================

def create_agents():
    """
    Creates all 3 agents with their roles and goals
    """

    # AGENT 1 - EXTRACTOR AGENT
    # Reads raw text and organizes it into structured data
    extractor_agent = Agent(
        role="Medical Report Data Extractor",
        goal="""
        Read the raw medical report text carefully and extract 
        ALL information in a structured and organized way.
        Do not miss any value, test, measurement or observation.
        Organize everything clearly so the next agent can explain it.
        """,
        backstory="""
        You are an expert medical data analyst with 20 years of experience
        reading all types of medical reports including blood tests, urine tests,
        ECG reports, MRI reports, CT scans, X-rays, discharge summaries,
        prescriptions and any other medical document.
        You have seen thousands of reports and can identify and organize
        every single piece of information no matter how complex the report is.
        You never miss any data and always present it in a clean structured format.
        """,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # AGENT 2 - EXPLAINER AGENT
    # Takes structured data and explains everything in simple language
    explainer_agent = Agent(
        role="Medical Report Explainer",
        goal="""
        Take the structured medical data and explain every single value
        and finding in very simple plain language that anyone can understand.
        Tell the patient exactly what each test means, what their result is,
        whether it is normal or abnormal, and what it means for their health.
        Be thorough, clear and compassionate.
        """,
        backstory="""
        You are a brilliant doctor who is known for explaining complex medical
        information to patients in the simplest possible way.
        You have a gift for making complicated medical jargon easy to understand
        for people with no medical background.
        You always explain things calmly and reassuringly while being honest
        about any concerns. You cover every single test and value without skipping anything.
        Patients always leave your office feeling informed and confident.
        """,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    # AGENT 3 - ADVISOR AGENT
    # Takes explanation and gives health recommendations
    advisor_agent = Agent(
        role="Personal Health Advisor",
        goal="""
        Based on the explained medical report provide personalized health advice,
        flag any urgent concerns, suggest lifestyle changes, and prepare
        specific questions the patient should ask their doctor.
        Be practical, specific and helpful.
        """,
        backstory="""
        You are a highly experienced personal health advisor who has helped
        thousands of patients understand their health and take action.
        You specialize in translating medical findings into practical
        day to day advice that patients can actually follow.
        You know exactly what questions patients should ask their doctors
        and what lifestyle changes make the biggest difference.
        You are warm, encouraging and always focused on empowering patients
        to take control of their health.
        """,
        llm=llm,
        verbose=True,
        allow_delegation=False
    )

    return extractor_agent, explainer_agent, advisor_agent


# ============================================================
# DEFINE ALL 3 TASKS
# ============================================================

def create_tasks(extractor_agent, explainer_agent, advisor_agent, report_content):
    """
    Creates tasks for each agent
    Each task passes its output to the next agent
    """

    # TASK 1 - Extract and organize all data from report
    extraction_task = Task(
        description=f"""
        Read this complete medical report carefully and extract ALL information:

        {report_content}

        Your job is to:
        1. Extract patient information if present (name, age, date, doctor name etc)
        2. Extract EVERY test and its values - do not skip any
        3. Extract reference ranges for each test if available
        4. Extract doctor observations and notes if present
        5. Extract diagnosis if mentioned
        6. Extract prescribed medications if any
        7. Extract any recommendations made by doctor
        8. Organize everything into clear sections

        Format your output as:

        PATIENT INFO:
        (all patient details found)

        TEST RESULTS:
        Test Name | Result | Unit | Reference Range | Status (Normal/Low/High)
        (list every single test)

        DOCTOR OBSERVATIONS:
        (any notes or observations from doctor)

        DIAGNOSIS:
        (any diagnosis mentioned)

        MEDICATIONS PRESCRIBED:
        (any medications mentioned)

        DOCTOR RECOMMENDATIONS:
        (any recommendations in the report)

        Do not miss anything. Extract everything present in the report.
        """,
        expected_output="""
        A completely organized and structured version of all data 
        found in the medical report with nothing missed.
        """,
        agent=extractor_agent
    )

    # TASK 2 - Explain everything in simple language
    explanation_task = Task(
        description="""
        Take the structured medical data from the previous task and 
        explain everything in simple plain English.

        For EVERY test and value explain:
        - What this test measures in simple words
        - What the patient result is
        - Whether it is NORMAL, LOW or HIGH
        - What this means for the patient health
        - Why this test is important

        Also explain:
        - Any diagnosis mentioned in simple terms
        - What prescribed medications do
        - What doctor observations mean

        Format your output clearly with:
        - Use emojis to make it friendly (✅ for normal, 🔴 for high, 🔵 for low)
        - Use simple headings for each section
        - Write as if explaining to someone with no medical knowledge
        - Be thorough but clear

        Start with a brief overview then go test by test.
        End with a simple overall health summary.
        Always add: Please consult your doctor for professional medical advice.
        """,
        expected_output="""
        A complete, clear and simple explanation of every test and finding
        in the medical report written for a non medical person.
        """,
        agent=explainer_agent,
        context=[extraction_task]  # receives output from task 1
    )

    # TASK 3 - Give health advice and recommendations
    advisor_task = Task(
        description="""
        Based on the explained medical report from the previous task,
        provide comprehensive personalized health advice.

        Your response must include:

        1. 🚨 URGENT CONCERNS (if any)
           - Any values that need immediate attention
           - Any results that are seriously abnormal

        2. ⚠️ AREAS TO WATCH
           - Values that are borderline or mildly abnormal
           - Things to monitor over time

        3. ✅ GOOD NEWS
           - Values that are normal and healthy
           - Positive findings to be happy about

        4. 🥗 DIET RECOMMENDATIONS
           - Specific foods to eat more based on these results
           - Specific foods to avoid or reduce

        5. 🏃 LIFESTYLE RECOMMENDATIONS
           - Exercise suggestions
           - Sleep recommendations
           - Stress management tips

        6. 💊 MEDICATION NOTES (if any were prescribed)
           - Simple explanation of what each medication does
           - Important things to remember when taking them

        7. ❓ QUESTIONS TO ASK YOUR DOCTOR
           - List 5 specific important questions based on these results
           - Make them specific to the actual findings

        8. 📅 NEXT STEPS
           - What tests should be repeated and when
           - When to follow up with doctor
           - Any specialist consultations recommended

        Be warm, encouraging and practical.
        Always end with: Please consult your doctor for professional medical advice.
        """,
        expected_output="""
        Comprehensive personalized health advice with urgent concerns,
        diet and lifestyle recommendations, doctor questions and next steps.
        """,
        agent=advisor_agent,
        context=[explanation_task]  # receives output from task 2
    )

    return extraction_task, explanation_task, advisor_task


# ============================================================
# MAIN FUNCTION - RUN THE CREW
# ============================================================

def run_medical_crew(extracted_content):
    """
    Main function that runs all 3 agents
    Takes extracted content from extractor.py
    Returns complete explanation and advice
    """

    # Prepare report content for agents
    if extracted_content["type"] == "text":
        report_content = extracted_content["content"]

    elif extracted_content["type"] == "image":
        # Convert image to base64 for AI to read
        image_data = base64.standard_b64encode(
            extracted_content["content"]
        ).decode("utf-8")

        format_map = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "JPG": "image/jpeg"
        }
        media_type = format_map.get(
            extracted_content["format"].upper(), "image/png"
        )

        report_content = f"[IMAGE REPORT - Base64 encoded {media_type} image provided]"

    else:
        return {
            "success": False,
            "error": "Could not process the file",
            "extraction": "",
            "explanation": "",
            "advice": ""
        }

    try:
        # Create agents
        extractor_agent, explainer_agent, advisor_agent = create_agents()

        # Create tasks
        extraction_task, explanation_task, advisor_task = create_tasks(
            extractor_agent,
            explainer_agent,
            advisor_agent,
            report_content
        )

        # Create crew with all agents and tasks
        medical_crew = Crew(
            agents=[extractor_agent, explainer_agent, advisor_agent],
            tasks=[extraction_task, explanation_task, advisor_task],
            process=Process.sequential,  # agents work one after another
            verbose=True
        )

        # Run the crew
        result = medical_crew.kickoff()

        # Get individual task outputs
        extraction_output = extraction_task.output.raw if extraction_task.output else ""
        explanation_output = explanation_task.output.raw if explanation_task.output else ""
        advisor_output = advisor_task.output.raw if advisor_task.output else ""

        return {
            "success": True,
            "extraction": extraction_output,    # organized raw data
            "explanation": explanation_output,  # simple explanation
            "advice": advisor_output,           # health advice
            "final_output": str(result)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "extraction": "",
            "explanation": "",
            "advice": ""
        }
