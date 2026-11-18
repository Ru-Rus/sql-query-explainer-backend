import os
import time
from google import genai
from dotenv import load_dotenv
from app.constants import GEMINI_MODEL
import logging

load_dotenv()

logger = logging.getLogger(__name__)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Models to try in order if the primary model experiences high demand (503)
CANDIDATE_MODELS = [GEMINI_MODEL]
for fallback in ["gemini-3.8-flash", "gemini-2.5-flash-lite"]:
    if fallback not in CANDIDATE_MODELS:
        CANDIDATE_MODELS.append(fallback)

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

    last_exception = None
    response = None

    for model_name in CANDIDATE_MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                break
            except Exception as e:
                err_str = str(e)
                last_exception = e
                # Check for transient errors: 503 UNAVAILABLE, high demand, or rate spikes
                if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str.lower():
                    logger.warning(f"Model {model_name} busy (attempt {attempt + 1}): {e}. Retrying/falling back...")
                    time.sleep(1)
                    continue
                else:
                    logger.warning(f"Error calling {model_name}: {e}")
                    break

        if response is not None:
            break

    if response is None:
        logger.error(f"All Gemini models exhausted. Last error: {last_exception}")
        raise last_exception

    text = response.text.strip()

    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return text