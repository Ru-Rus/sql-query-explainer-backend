import os
from google import genai
from dotenv import load_dotenv
from app.constants import GEMINI_MODEL
import logging

load_dotenv()

logger = logging.getLogger(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def explain_query(sql_query: str) -> str:
    prompt = f"""
    You are an expert SQL Query Explainer.
    Analyze this SQL query and respond in valid JSON format only.

    Query: {sql_query}

    Return this exact structure:
    {{
      "explanation": "Explain the query in very simple plain English",
      "performance_issues": ["issue 1", "issue 2"],
      "erd_description": "Describe the tables and how they are related",
      "optimizations": ["suggestion 1", "suggestion 2"]
    }}
    If no issues, make performance_issues and optimizations empty lists [].
    Keep answers short and clear.
    Respond with ONLY the raw JSON object. No markdown formatting, no code fences, no extra commentary.
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
    except Exception as e:
        logger.error(f"API call error: {e}")
        raise

    text = response.text.strip()

    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return text