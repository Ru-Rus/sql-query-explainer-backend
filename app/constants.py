import os

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/day")
MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "2000"))

