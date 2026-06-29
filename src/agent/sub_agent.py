"""
Sub-agent (task executor) — ReAct-style agent delegated to by the orchestrator.

SECURITY FIXTURE — Contains deliberately insecure patterns for Trent validation.

Planted findings (via parent design):
  VULN-APP-003, VULN-APP-002: inherits risky tools (read_file, fetch_url)
  VULN-APP-008: external system prompt (same mutable-path issue as orchestrator)
"""

import os
from typing import Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


class SubAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    result: str


def _load_sub_agent_prompt() -> str:
    """Load the sub-agent system prompt.

    Shares the same mutable-path vulnerability as orchestrator._load_system_prompt().
    """
    prompt_path = os.environ.get(
        "SUB_AGENT_SYSTEM_PROMPT_PATH", "prompts/sub_agent_system.md"
    )
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a task execution agent. Complete the task using your tools."


def create_sub_agent_node(tools: list[BaseTool]):
    """Build a sub-agent node function suitable for embedding in the orchestrator graph."""

    system_prompt = _load_sub_agent_prompt()
    llm = ChatAnthropic(model="claude-3-5-haiku-20241022")
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: SubAgentState) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: SubAgentState) -> str:
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        # Capture the final response as the result.
        return END

    tool_node = ToolNode(tools)

    graph = StateGraph(SubAgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, ["tools", END])
    graph.add_edge("tools", "agent")

    compiled = graph.compile()

    def run_sub_agent(state: dict) -> dict:
        """Node function: runs the sub-agent and returns the result to the parent."""
        task = state.get("context", {}).get("sub_agent_task", "")
        from langchain_core.messages import HumanMessage
        result = compiled.invoke({"messages": [HumanMessage(content=task)], "result": ""})
        last_message = result["messages"][-1]
        return {
            "context": {**state.get("context", {}), "sub_agent_result": last_message.content}
        }

    return run_sub_agent
