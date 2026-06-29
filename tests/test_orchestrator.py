"""
Basic unit tests for the orchestrator.

These tests use mocked LLM and tool calls — they do not make real API calls.
They exist to give the CI environment something to run and to verify the import
structure of the agent package.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def test_tool_read_file_exists():
    """Verify read_file tool is importable and callable."""
    from src.agent.tools import read_file
    assert callable(read_file)


def test_tool_run_shell_exists():
    """Verify run_shell tool is importable and callable."""
    from src.agent.tools import run_shell
    assert callable(run_shell)


def test_tool_fetch_url_exists():
    """Verify fetch_url tool is importable and callable."""
    from src.agent.tools import fetch_url
    assert callable(fetch_url)


def test_all_tools_in_registry():
    """Verify all three tools are in the ALL_TOOLS registry."""
    from src.agent.tools import ALL_TOOLS
    tool_names = [t.name for t in ALL_TOOLS]
    assert "read_file" in tool_names
    assert "run_shell" in tool_names
    assert "fetch_url" in tool_names


def test_sub_agent_tools_subset_of_all():
    """Verify sub-agent tool registry is a strict subset of ALL_TOOLS."""
    from src.agent.tools import ALL_TOOLS, SUB_AGENT_TOOLS
    all_names = {t.name for t in ALL_TOOLS}
    sub_names = {t.name for t in SUB_AGENT_TOOLS}
    assert sub_names.issubset(all_names)
    # run_shell should NOT be in the sub-agent registry
    assert "run_shell" not in sub_names


def test_agent_channel_has_no_auth_fields():
    """
    Fixture verification: AgentChannel intentionally lacks auth fields.
    This test documents the missing-auth finding (VULN-APP-007) by asserting
    the absence of security fields — so if auth is later added, this test
    must be updated to reflect the improvement.
    """
    from src.agent.multi_agent_handoff import AgentChannel
    channel = AgentChannel(task="test", result="", metadata={})
    # Verify auth fields are absent (the fixture's deliberate vulnerability).
    assert not hasattr(channel, "hmac_signature")
    assert not hasattr(channel, "sender_id")
    assert not hasattr(channel, "nonce")
