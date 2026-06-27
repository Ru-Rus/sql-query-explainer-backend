from app.constants import MAX_QUERY_LENGTH

def is_valid_sql(query: str) -> bool:
    query = query.strip()

    if len(query) == 0 or len(query) > MAX_QUERY_LENGTH:
        return False

    upper = query.upper()
    sql_keywords = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE',
        'FROM', 'WHERE', 'JOIN',
        'CREATE', 'ALTER', 'DROP', 'TABLE'
    ]
    has_keyword = any(keyword in upper for keyword in sql_keywords)

    # Block multiple statements unless it's a multi CREATE TABLE script
    # Allow semicolons when CREATE TABLE is present (schema definitions)
    is_schema = 'CREATE' in upper and 'TABLE' in upper
    if not is_schema:
        body = query[:-1] if query.endswith(';') else query
        if ';' in body:
            return False

    return has_keyword and len(query) > 10