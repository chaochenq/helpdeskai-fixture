"""
MCP server — exposes tools to any MCP-compatible host agent (e.g., the orchestrator).

SECURITY FIXTURE — Contains deliberately insecure patterns for Trent validation.

Planted findings:
  VULN-APP-004: execute_code — arbitrary Python code execution via exec()
  VULN-APP-005: query_database — SQL injection via f-string interpolation
  VULN-APP-006: No authentication on the MCP server — any host can connect

Server name: fixture-mcp
Transport: stdio (for local use) or SSE (for network use)

To start:
  python -m src.mcp_server.server

The MCP client configuration is in server_config.json.
"""

import sqlite3

from mcp.server.fastmcp import FastMCP

# VULN-APP-006: The MCP server is initialized with no authentication requirement.
# Any process that can spawn or connect to this server can invoke its tools
# (execute arbitrary code, run arbitrary SQL queries) without credentials.
mcp = FastMCP("fixture-mcp")


@mcp.tool()
def execute_code(code: str) -> str:
    """Execute a Python code snippet and return the result.

    This tool is provided for data analysis tasks. The caller supplies
    Python source code which is executed in the server process.

    Args:
        code: Python source code to execute.

    Returns:
        String representation of the execution result, or error message.
    """
    # VULN-APP-004: exec() executes caller-supplied code in the server process.
    # There is no sandbox, no restricted globals, no resource limit, and no
    # allowlist of safe operations. A caller can read files, make network requests,
    # spawn subprocesses, or exfiltrate environment variables (including secrets).
    local_vars: dict = {}
    try:
        exec(code, {}, local_vars)  # noqa: S102
        return str(local_vars.get("result", "Code executed (no 'result' variable set)"))
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def query_database(table: str, filter_column: str, filter_value: str) -> list[dict]:
    """Query a record from the database by filtering on a column value.

    Args:
        table: Name of the table to query.
        filter_column: Name of the column to filter on.
        filter_value: Value to match in the filter column.

    Returns:
        List of matching rows as dicts.
    """
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # VULN-APP-005: SQL query built by f-string interpolation. An attacker can
    # supply filter_value="' OR '1'='1" to dump the entire table, or a more
    # sophisticated payload to exfiltrate other tables or call sqlite functions.
    # Correct pattern: parameterized query with cursor.execute(sql, (value,)).
    sql = f"SELECT * FROM {table} WHERE {filter_column} = '{filter_value}'"  # noqa: S608
    cursor.execute(sql)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    mcp.run()
