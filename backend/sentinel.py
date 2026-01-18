import os
import json
from openai import OpenAI

# Initialize client only if key exists, otherwise we'll mock it or error
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except:
    client = None

def analyze_call_transcript(transcript: str):
    """
    Analyzes a call transcript to determine if it's safe or a scam.
    Returns a dict with status and reasoning.
    """
    if not client:
        # Mock response for demo purposes if no API key
        print("Warning: No OpenAI API Key found. Using mock response.")
        if "gift card" in transcript.lower() or "irs" in transcript.lower():
            return {
                "classification": "Confirmed Scam",
                "reasoning": "The caller demands payment via gift cards/IRS, which is a common scam pattern."
            }
        return {
            "classification": "Safe",
            "reasoning": "No suspicious keywords detected in the conversation."
        }
        
    system_prompt = """
    You are 'Sentinel', an AI protector for seniors. Analyze the phone call transcript.
    Classify it as one of: 'Safe', 'Suspicious', 'Confirmed Scam'.
    Provide a concise reasoning.
    Return JSON format: {"classification": "...", "reasoning": "..."}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ],
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    return json.loads(content)

def analyze_document_mock(filename: str):
    """
    Mock analysis for uploaded documents.
    """
    lower_name = filename.lower()
    
    if "scam" in lower_name or "prize" in lower_name or "winner" in lower_name:
        return {
            "classification": "Confirmed Scam",
            "reasoning": "Document contains high-risk keywords ('Prize', 'Winner'). Typical mail fraud pattern."
        }
    elif "bill" in lower_name or "invoice" in lower_name:
        # Simulate a high bill check
        return {
            "classification": "Safe",
            "reasoning": "Standard utility bill structure detected. Amount is within normal range."
        }
    else:
        return {
            "classification": "Safe",
            "reasoning": "Document appears to be a standard letter. No threats detected."
        }
