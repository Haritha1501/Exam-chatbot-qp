from google import genai
from google.genai import types
from flask import current_app
import json

def analyze_question_paper(text, api_key=None):
    """
    Analyze extracted PDF text using the Gemini API to infer paper structure.
    Returns a structured dictionary with frequent_topics, repeated_questions, and exam_pattern.
    """
    # Prefer explicitly passed API key (useful for background jobs), fallback to app config
    if not api_key:
        # Requires an active Flask application context
        api_key = current_app.config.get('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError("Gemini API Key is missing. Ensure GEMINI_API_KEY is set in environment or config.")

    # Initialize the new google.genai client
    client = genai.Client(api_key=api_key)
    
    # We will use gemini-1.5-flash and configure JSON output natively in the call
    
    prompt = f"""
    You are an expert academic AI assistant. Analyze the following text extracted from university exam question paper(s).
    
    Your task is to analyze the text and output a structured JSON response containing exactly these keys:
    1. "frequent_topics": A list of strings representing the most frequent topics covered in this exam based on the questions.
    2. "repeated_questions": A list of strings representing questions that seem to represent core recurring concepts (summarize the core concept if the exact phrasing varies).
    3. "exam_pattern": A description of the exam's structural pattern (e.g., number of sections, types of questions like short/long answers, marks distribution if visible).
    
    Extracted Text:
    ---
    {text}
    ---
    
    Provide ONLY the JSON response matching the structure described.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # Assuming the model returns valid JSON
        structured_data = json.loads(text)
        return structured_data
    except json.JSONDecodeError:
        print("Failed to decode JSON response from Gemini API.")
        # Fallback to a dictionary indicating failure if valid JSON was not produced
        return {
            "error": "Failed to generate structured analysis.",
            "raw_response": response.text if response else ""
        }
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {"error": str(e)}
