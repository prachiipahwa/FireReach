import json
from typing import Dict, TypedDict, Any
from langgraph.graph import StateGraph, START, END
from app.agent.tools import (
    tool_signal_harvester,
    tool_research_analyst,
    tool_outreach_automated_sender
)

class AgentState(TypedDict):
    """
    State representing the data passed between nodes in the LangGraph workflow.
    """
    icp: str
    company_name: str
    target_email: str
    
    # Track the output at each stage
    signals: str
    account_brief: str
    delivery_status: str
    email_content: str
    
    # Track execution path for debugging
    trace: list[str]


def harvest_signals_node(state: AgentState) -> Dict:
    """Node 1: Harvest signals."""
    print("[Node] Calling Signal Harvester...")
    company = state.get("company_name", "")
    
    # Execute the tool
    # Need to pass dictionary properly depending on LangChain version.
    # We call the function directly for simplicity since it's deterministic.
    result_str = tool_signal_harvester.invoke({"company_name": company})
    
    # Update trace
    new_trace = state.get("trace", []) + ["Tool Executed: tool_signal_harvester"]
    
    return {"signals": result_str, "trace": new_trace}


def research_analyst_node(state: AgentState) -> Dict:
    """Node 2: Generate account brief."""
    print("[Node] Calling Research Analyst...")
    icp = state.get("icp", "")
    signals = state.get("signals", "{}")
    
    # Execute the tool
    result_str = tool_research_analyst.invoke({"icp": icp, "signals": signals})
    
    # Update trace
    new_trace = state.get("trace", []) + ["Tool Executed: tool_research_analyst"]
    
    return {"account_brief": result_str, "trace": new_trace}


def outreach_sender_node(state: AgentState) -> Dict:
    """Node 3: Draft and send the email."""
    print("[Node] Calling Outreach Sender...")
    email = state.get("target_email", "")
    brief = state.get("account_brief", "")
    signals = state.get("signals", "{}")
    
    # Execute the tool
    result_str = tool_outreach_automated_sender.invoke({
        "email": email,
        "account_brief": brief,
        "signals": signals
    })
    
    # Parse the result
    try:
        result_data = json.loads(result_str)
        status = result_data.get("delivery_status", "Unknown")
        content = result_data.get("email_content", "Unknown")
    except json.JSONDecodeError:
        status = "Error parsing result"
        content = result_str
        
    # Update trace
    new_trace = state.get("trace", []) + ["Tool Executed: tool_outreach_automated_sender"]
    
    return {
        "delivery_status": status,
        "email_content": content,
        "trace": new_trace
    }


def create_agent_graph() -> StateGraph:
    """
    Creates and compiles the deterministic LangGraph workflow.
    Workflow: START -> Signal Harvester -> Research Analyst -> Outreach Sender -> END
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes representing the three specific tools
    workflow.add_node("harvester", harvest_signals_node)
    workflow.add_node("researcher", research_analyst_node)
    workflow.add_node("sender", outreach_sender_node)
    
    # Define the deterministic edges
    workflow.add_edge(START, "harvester")
    workflow.add_edge("harvester", "researcher")
    workflow.add_edge("researcher", "sender")
    workflow.add_edge("sender", END)
    
    # Compile the graph
    return workflow.compile()

# Instantiate the globally shared graph
agent_executor = create_agent_graph()
