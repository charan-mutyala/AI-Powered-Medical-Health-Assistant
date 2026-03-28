import openai
import os
import base64
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def explain_medical_report(extracted_content):
    
    system_prompt = """
    You are a helpful medical report explainer. Your job is to:
    
    1. Read the medical report carefully
    2. Explain every test and value in very simple plain English
    3. For each value tell the user:
       - What the test measures
       - What the patient result is
       - Whether it is NORMAL LOW or HIGH
       - What it means for their health in simple words
    4. At the end give a simple summary of overall health based on the report
    5. Suggest 2-3 questions the patient should ask their doctor
    
    Important rules:
    - Never use complex medical jargon
    - Always be calm and reassuring in tone
    - Always end with: Please consult your doctor for professional medical advice
    - Format your response clearly with sections and emojis to make it easy to read
    """
    
    if extracted_content["type"] == "text":
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please explain this medical report to me in simple language:\n\n{extracted_content['content']}"}
        ]
    
    elif extracted_content["type"] == "image":
        image_data = base64.standard_b64encode(extracted_content["content"]).decode("utf-8")
        
        format_map = {
            "PNG": "image/png",
            "JPEG": "image/jpeg",
            "JPG": "image/jpeg"
        }
        media_type = format_map.get(extracted_content["format"].upper(), "image/png")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Please explain this medical report to me in simple language"
                    }
                ]
            }
        ]
    
    else:
        return "Error: Could not process the file"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        messages=messages
    )
    
    return response.choices[0].message.content


def ask_followup_question(report_content, conversation_history, user_question):
    
    system_prompt = """
    You are a helpful medical report explainer. The user has already received 
    an explanation of their medical report and now has followup questions.
    Answer their questions in simple clear language.
    Always end with: Please consult your doctor for professional medical advice
    """
    
    messages = [{"role": "system", "content": system_prompt}] + conversation_history + [
        {"role": "user", "content": user_question}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1000,
        messages=messages
    )
    
    return response.choices[0].message.content