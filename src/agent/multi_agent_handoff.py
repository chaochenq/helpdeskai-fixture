"""
Multi-agent handoff — two-agent pattern where orchestrator delegates to sub-agent
via a shared state channel.

SECURITY FIXTURE — Contains deliberately insecure patterns for Trent validation.

Planted findings:
  VULN-APP-007: Missing inter-agent authentication. The handoff is a plain dict
                with no HMAC, no signed token, and no channel integrity check.
                An attacker who can write to the shared state dict (e.g., via a
                compromised tool return value or a malicious external service)
                can inject instructions into the sub-agent's task.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentChannel:
    """Shared communication channel between orchestrator and sub-agent.

    VULN-APP-007: This channel is an in-process dict. In a distributed deployment
    (multiple workers, external message queue), the equivalent would be an
    unencrypted, unauthenticated message on a queue. No integrity protection,
    no authentication of the sender, no replay protection.
    """

    task: str = ""
    result: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    # Intentionally no: hmac_signature, sender_id, timestamp, nonce


async def run_handoff(
    orchestrator_task: str,
    orchestrator_run,
    sub_agent_run,
) -> str:
    """Run a two-agent handoff: orchestrator produces a task, sub-agent executes it.

    Args:
        orchestrator_task: The initial task for the orchestrator.
        orchestrator_run: Callable that runs the orchestrator and returns a channel.
        sub_agent_run: Callable that runs the sub-agent given a channel.

    Returns:
        The sub-agent's result string.
    """
    # Phase 1: Orchestrator plans and writes to the channel.
    channel = AgentChannel(task=orchestrator_task)
    channel = await orchestrator_run(channel)

    # Phase 2: Sub-agent reads from the channel and executes.
    # VULN-APP-007: No verification that the channel was populated by the
    # legitimate orchestrator. Any code path that can write to 'channel.task'
    # before this point can hijack the sub-agent's behavior.
    channel = await sub_agent_run(channel)

    return channel.result


# Example usage (not for production):
if __name__ == "__main__":
    async def mock_orchestrator(channel: AgentChannel) -> AgentChannel:
        channel.task = "Read the file at /tmp/config.json and summarize it."
        return channel

    async def mock_sub_agent(channel: AgentChannel) -> AgentChannel:
        channel.result = f"Sub-agent executed task: {channel.task}"
        return channel

    result = asyncio.run(
        run_handoff("Analyze the system config", mock_orchestrator, mock_sub_agent)
    )
    print(result)
