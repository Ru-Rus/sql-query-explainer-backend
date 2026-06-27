from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.utils.sql_validator import is_valid_sql
from app.services.gemini_service import explain_query
from app.limiter import limiter
from app.constants import RATE_LIMIT
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    explanation: str
    performance_issues: list
    erd_description: str
    optimizations: list

@router.post("/explain", response_model=QueryResponse)
@limiter.limit(RATE_LIMIT)
async def explain_sql(request: Request, payload: QueryRequest):
    if not is_valid_sql(payload.query):
        raise HTTPException(status_code=400, detail="Please paste a valid SQL query only.")

    try:
        result = explain_query(payload.query)
    except Exception as e:
        logger.error(f"Gemini call failed: {e}")
        raise HTTPException(status_code=502, detail="Couldn't reach the AI service. Please try again.")

    try:
        return json.loads(result)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}\nRaw response: {result}")
        raise HTTPException(status_code=502, detail="The AI returned an unexpected response. Please try again.")