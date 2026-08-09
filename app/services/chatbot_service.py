from google import genai
from flask import current_app
import json

def generate_chat_response(query, document_context, chat_history=None, api_key=None):

    if not api_key:
        api_key = current_app.config.get('GEMINI_API_KEY')

    if not api_key:
        raise ValueError("Gemini API Key is missing.")

    client = genai.Client(api_key=api_key)

    context_str = json.dumps(document_context, indent=2) if isinstance(document_context, dict) else str(document_context)

    history_str = ""
    if chat_history:
        for msg in chat_history:
            sender = "Student" if msg['sender_type'] == 'User' else "Tutor"
            history_str += f"{sender}: {msg['content']}\n"

    system_prompt = f"""
You are an AI exam preparation tutor.

Below is the analysis of previous semester question papers:

--- Context ---
{context_str}
---------------
"""

    if history_str:
        system_prompt += f"""
--- Previous Conversation ---
{history_str}
-----------------------------
"""

    user_prompt = f"""
Student Question: {query}

Provide structured exam preparation guidance.

Format:

Important Topics:
- ...

Predicted Questions:
- ...

Exam Pattern:
...

Study Strategy:
...
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",   # ✅ correct model usage
            contents=system_prompt + "\n" + user_prompt
        )

        return response.text

    except Exception as e:
        print("Gemini API error:", e)
        return "AI analysis failed. Please try again."