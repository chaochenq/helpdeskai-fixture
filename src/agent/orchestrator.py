"""
Orchestrator agent — LangGraph StateGraph with tool registry and sub-agent delegation.

SECURITY FIXTURE — Contains deliberately insecure patterns for Trent validation.

Planted findings:
  VULN-APP-008: System prompt loaded from mutable filesystem path at runtime.
  VULN-APP-010: No max-steps / iteration budget on the agent loop.
"""

import os
from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .tools import ALL_TOOLS, SUB_AGENT_TOOLS
from .sub_agent import create_sub_agent_node


class OrchestratorState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    # Shared context dict used to pass information to/from the sub-agent.
    # VULN-APP-007 (partially): no authentication or integrity check on this dict.
    context: dict


def _load_system_prompt() -> str:
    """Load the orchestrator system prompt from the filesystem.

    VULN-APP-008: This loads the system prompt from a path configurable via an
    environment variable. An attacker with write access to the prompt file (or
    control over AGENT_SYSTEM_PROMPT_PATH) can inject arbitrary instructions
    into the orchestrator's system prompt.
    """
    prompt_path = os.environ.get(
        "AGENT_SYSTEM_PROMPT_PATH", "prompts/orchestrator_system.md"
    )
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful AI assistant with access to tools."


def create_orchestrator(model_name: str = "claude-3-5-sonnet-20241022") -> StateGraph:
    """Build and return the orchestrator LangGraph."""
    llm = ChatAnthropic(model=model_name)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    system_prompt = _load_system_prompt()

    def call_model(state: OrchestratorState) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: OrchestratorState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            # Check if we should delegate to the sub-agent.
            for call in last.tool_calls:
                if call["name"] == "delegate_to_sub_agent":
                    return "sub_agent"
            return "tools"
        return END

    tool_node = ToolNode(ALL_TOOLS)

    # VULN-APP-010: No max_steps / recursion_limit specified — the graph will
    # run until END is reached or until LangGraph's default recursion limit
    # (25) is hit. For production agents, an explicit step budget prevents
    # runaway loops triggered by malicious or malformed inputs.
    graph = StateGraph(OrchestratorState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)
    graph.add_node("sub_agent", create_sub_agent_node(SUB_AGENT_TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, ["tools", "sub_agent", END])
    graph.add_edge("tools", "agent")
    graph.add_edge("sub_agent", "agent")

    return graph.compile()
