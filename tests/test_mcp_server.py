"""
Basic unit tests for the MCP server tools.

These tests verify the tool function behavior without an MCP runtime.
They also document the security contract (or lack thereof) for each tool.
"""

import pytest
import sqlite3
import os
import tempfile


def test_execute_code_basic():
    """Verify execute_code runs Python and captures the result variable."""
    from src.mcp_server.server import execute_code
    output = execute_code.fn(code="result = 1 + 1")
    assert output == "2"


def test_execute_code_error_returns_message():
    """Verify execute_code returns error messages rather than raising."""
    from src.mcp_server.server import execute_code
    output = execute_code.fn(code="raise ValueError('test error')")
    assert "Error" in output
    assert "test error" in output


def test_execute_code_no_sandbox():
    """
    Fixture verification: execute_code does NOT sandbox the provided code.
    This test documents VULN-APP-004 by demonstrating that os.environ is
    accessible from within execute_code — i.e., there is no restricted globals.
    """
    from src.mcp_server.server import execute_code
    # Set a dummy env var and verify execute_code can read it.
    os.environ["FIXTURE_TEST_SECRET"] = "plaintext-value"
    output = execute_code.fn(code="import os; result = os.environ.get('FIXTURE_TEST_SECRET')")
    assert output == "plaintext-value"
    del os.environ["FIXTURE_TEST_SECRET"]


def test_query_database_basic():
    """Verify query_database returns rows from the database."""
    from src.mcp_server.server import query_database

    # Create a temporary database for the test.
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice')")
    conn.commit()
    conn.close()

    # Patch the server's database path.
    original_connect = sqlite3.connect
    import unittest.mock as mock
    with mock.patch("sqlite3.connect", return_value=sqlite3.connect(db_path)):
        rows = query_database.fn(table="users", filter_column="name", filter_value="Alice")
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"

    os.unlink(db_path)


def test_auth_example_validates_key():
    """Verify the auth middleware correctly validates API keys."""
    import hashlib
    from src.mcp_server.auth_example import ApiKeyAuthMiddleware

    test_key = "test-api-key-12345"
    key_hash = hashlib.sha256(test_key.encode()).hexdigest()
    os.environ["MCP_API_KEY_HASH"] = key_hash

    middleware = ApiKeyAuthMiddleware()
    assert middleware.validate(test_key) is True
    assert middleware.validate("wrong-key") is False

    del os.environ["MCP_API_KEY_HASH"]
