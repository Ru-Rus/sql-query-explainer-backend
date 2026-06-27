from app.utils.sql_validator import is_valid_sql

def test_valid_select():
    assert is_valid_sql("SELECT * FROM users") is True

def test_valid_with_where():
    assert is_valid_sql("SELECT id, name FROM orders WHERE status = 'pending'") is True

def test_valid_with_trailing_semicolon():
    assert is_valid_sql("SELECT * FROM users;") is True

def test_blocks_multi_statement():
    assert is_valid_sql("SELECT * FROM users; DROP TABLE users;") is False

def test_blocks_empty():
    assert is_valid_sql("") is False

def test_blocks_too_short():
    assert is_valid_sql("SELECT") is False

def test_blocks_no_keyword():
    assert is_valid_sql("just some random text here") is False

def test_blocks_too_long():
    assert is_valid_sql("SELECT " + "a" * 2001) is False

def test_valid_insert():
    assert is_valid_sql("INSERT INTO users (name) VALUES ('Alice')") is True

def test_valid_update():
    assert is_valid_sql("UPDATE orders SET status = 'done' WHERE id = 1") is True

def test_valid_delete():
    assert is_valid_sql("DELETE FROM sessions WHERE expired = true") is True

def test_valid_create_table():
    assert is_valid_sql("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50))") is True

def test_valid_multi_create_table():
    assert is_valid_sql("""
        CREATE TABLE departments (id INT PRIMARY KEY, name VARCHAR(50));
        CREATE TABLE employees (id INT REFERENCES departments(id));
    """) is True