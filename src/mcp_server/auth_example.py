"""
Authentication middleware example — POSITIVE CONTROL reference.

This module shows what a correctly authenticated MCP server looks like.
It is NOT wired into server.py (the deliberately insecure fixture server).
Its presence in the codebase allows Trent to surface the contrast:
"A secure auth pattern exists in the codebase but is not deployed."

POSITIVE CONTROL: CTRL-APP-001

In a production MCP server, this middleware would be composed into the
server startup to require a valid API key on every tool call.
"""

import hashlib
import hmac
import os
from functools import wraps
from typing import Callable


class ApiKeyAuthMiddleware:
    """Validates a per-client API key on every MCP tool invocation.

    Configuration:
      MCP_API_KEY_HASH (env var): SHA-256 hex digest of the valid API key.
        Set this instead of the raw key so the key is never in the environment.

    Usage (hypothetical FastMCP extension — not yet part of the FastMCP API):
        mcp = FastMCP("fixture-mcp", middleware=[ApiKeyAuthMiddleware()])

    Alternative for stdio transport: wrap each tool function with
    require_api_key() and pass the key via a shared secret in the startup
    environment rather than on-the-wire.
    """

    def __init__(self) -> None:
        self._key_hash = os.environ.get("MCP_API_KEY_HASH", "")
        if not self._key_hash:
            raise RuntimeError(
                "MCP_API_KEY_HASH environment variable is required. "
                "Set it to the SHA-256 hex digest of the MCP API key."
            )

    def validate(self, provided_key: str) -> bool:
        """Constant-time comparison against the stored key hash."""
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return hmac.compare_digest(provided_hash, self._key_hash)


def require_api_key(tool_func: Callable) -> Callable:
    """Decorator: reject tool calls that do not carry a valid API key.

    The key is expected in the tool call's metadata under 'x-api-key'.
    This is a reference implementation; the exact integration point depends
    on the MCP server framework version.
    """
    _middleware = ApiKeyAuthMiddleware()

    @wraps(tool_func)
    def wrapper(*args, api_key: str = "", **kwargs):
        if not _middleware.validate(api_key):
            raise PermissionError("Invalid or missing API key for MCP tool call.")
        return tool_func(*args, **kwargs)

    return wrapper


# Example of a correctly authenticated tool (for contrast with server.py):
#
# @mcp.tool()
# @require_api_key
# def execute_code_authenticated(code: str, api_key: str = "") -> str:
#     ...
#     exec(code, {}, local_vars)
#     ...
#
# Note: exec() is still fundamentally dangerous even with auth; the correct
# fix for VULN-APP-004 is to replace exec() with a restricted interpreter
# (e.g., RestrictedPython) or to redesign the tool to not accept raw code.
# Auth is a necessary but insufficient control for an exec()-based tool.
