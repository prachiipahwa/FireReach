import json
from typing import Dict, TypedDict, Any, List
from langgraph.graph import StateGraph, START, END
from app.agent.tools import (
    tool_lead_generator,
    tool_contact_finder,
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
    
    company_list: List[str]
    leads: List[Dict[str, str]]
    
    # Track the output at each stage
    signals: str
    account_brief: str
    delivery_status: str
    email_content: str
    
    # Aggregated batch results
    results: List[Dict[str, Any]]
    
    # Track execution path for debugging
    trace: list[str]

def lead_generator_node(state: AgentState) -> Dict:
    """Node: Generate list of companies based on ICP using Tavily and Groq."""
    print("[Node] Calling Lead Generator...")
    icp = state.get("icp", "")
    new_trace = state.get("trace", []) + ["Lead Generation Started"]
    
    # Error handling: if ICP is empty
    if not icp or not icp.strip():
        new_trace.append("Error: ICP is empty. Generated 0 companies.")
        return {"company_list": [], "trace": new_trace}
        
    try:
        companies_json = tool_lead_generator.invoke({"icp": icp})
        companies = json.loads(companies_json)
        new_trace.append(f"Generated {len(companies)} companies via LLM Search")
    except Exception as e:
        new_trace.append(f"Error during lead generation: {str(e)}")
        companies = []
        
    return {"company_list": companies, "trace": new_trace}

def contact_finder_node(state: AgentState) -> Dict:
    """Node: Find contacts for the list of companies via Hunter.io."""
    print("[Node] Calling Contact Finder...")
    company_list = state.get("company_list", [])
    new_trace = state.get("trace", []) + ["Contact Finder Started"]
    
    leads = []
    
    # Handle edge cases: Empty company_list
    if not company_list:
        new_trace.append("Warning: empty company_list provided. Generated 0 leads.")
        return {"leads": leads, "trace": new_trace}
        
    for comp in company_list:
        if not comp or not isinstance(comp, str) or not comp.strip():
            continue
            
        company_clean = comp.strip()
        
        try:
           email = tool_contact_finder.invoke({"company_name": company_clean})
        except Exception as e:
           new_trace.append(f"Warning: Contact fetch failed for {company_clean}")
           continue
           
        # Ensure email format is valid string
        if isinstance(email, str) and email and "@" in email:
            leads.append({
                "company_name": company_clean,
                "email": email
            })
            
    new_trace.append(f"Discovered {len(leads)} verified leads via Hunter.io")
    return {"leads": leads, "trace": new_trace}

def harvest_signals_node(state: AgentState) -> Dict:
    """Node 1: Harvest signals."""
    print("[Node] Calling Signal Harvester...")
    
    leads = state.get("leads", [])
    single_company = state.get("company_name", "")
    new_trace = state.get("trace", []) + ["Node Executed: harvest_signals_node"]
    
    # Handle single logic
    result_str = ""
    if single_company:
        result_str = tool_signal_harvester.invoke({"company_name": single_company})
        new_trace.append(f"Tool Executed: tool_signal_harvester (single)")
        
    # Handle batch logic using "results" array
    results = state.get("results", [])
    # If results is empty but we have leads, initialize it
    if not results and leads:
        for lead in leads:
            results.append({
                "company_name": lead.get("company_name", ""),
                "email": lead.get("email", "")
            })
            
    for item in results:
        company = item.get("company_name", "")
        if company:
            new_trace.append(f"Processing company: {company}")
            try:
                res = tool_signal_harvester.invoke({"company_name": company})
                item["signals"] = res
                new_trace.append(f"Tool Executed: tool_signal_harvester for {company}")
            except Exception as e:
                new_trace.append(f"Error harvesting signals for {company}: {str(e)}")
                item["signals"] = f"Error: {str(e)}"
    
    return {"signals": result_str, "results": results, "trace": new_trace}


def research_analyst_node(state: AgentState) -> Dict:
    """Node 2: Generate account brief."""
    print("[Node] Calling Research Analyst...")
    icp = state.get("icp", "")
    
    # Handle single logic
    signals = state.get("signals", "{}")
    result_str = ""
    new_trace = state.get("trace", []) + ["Node Executed: research_analyst_node"]
    
    if signals and signals != "{}":
        try:
            result_str = tool_research_analyst.invoke({"icp": icp, "signals": signals})
        except Exception as e:
            result_str = f"Error: {str(e)}"
        new_trace.append("Tool Executed: tool_research_analyst (single)")
        
    # Handle batch logic
    results = state.get("results", [])
    
    for item in results:
        company = item.get("company_name", "")
        if company:
            new_trace.append(f"Processing company: {company}")
            try:
                company_signals = item.get("signals", "{}")
                res = tool_research_analyst.invoke({"icp": icp, "signals": company_signals})
                item["account_brief"] = res
                new_trace.append(f"Tool Executed: tool_research_analyst for {company}")
            except Exception as e:
                new_trace.append(f"Error researching {company}: {str(e)}")
                item["account_brief"] = f"Error: {str(e)}"
                
    return {"account_brief": result_str, "results": results, "trace": new_trace}


from app.core.config import settings
import random

def outreach_generator_node(state: AgentState) -> Dict:
    """Node 3: Draft the email."""
    print("[Node] Calling Outreach Generator...")
    
    # Temporarily disable actual sending in the tool to generate drafts only
    original_sg_key = getattr(settings, "SENDGRID_API_KEY", "mock")
    settings.SENDGRID_API_KEY = "mock"
    
    new_trace = state.get("trace", []) + ["Node Executed: outreach_generator_node"]
    results = state.get("results", [])
    
    for item in results:
        lead_email = item.get("email", "")
        company = item.get("company_name", "")
        
        if lead_email and company:
            new_trace.append(f"Drafting email for company: {company}")
            try:
                company_brief = item.get("account_brief", "")
                company_signals = item.get("signals", "{}")
                
                res_str = tool_outreach_automated_sender.invoke({
                    "email": lead_email,
                    "account_brief": company_brief,
                    "signals": company_signals
                })
                
                res_data = json.loads(res_str)
                item["email_content"] = res_data.get("email_content", "Unknown")
                item["delivery_status"] = "Drafted"
                new_trace.append(f"Email drafted for {lead_email}")
            except Exception as e:
                new_trace.append(f"Error drafting outreach for {company}: {str(e)}")
                item["email_content"] = ""
                item["delivery_status"] = "Error"
                
    # Restore actual key
    settings.SENDGRID_API_KEY = original_sg_key
                
    return {"results": results, "trace": new_trace}


from langgraph.checkpoint.memory import MemorySaver

def sender_node(state: AgentState) -> Dict:
    """Node 4: Send approved emails."""
    print("[Node] Calling Sender Node...")
    new_trace = state.get("trace", []) + ["Node Executed: sender_node"]
    results = state.get("results", [])
    
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    
    for item in results:
        lead_email = item.get("email", "")
        company = item.get("company_name", "")
        
        if not lead_email or not company:
            continue
            
        if item.get("approved"):
            new_trace.append(f"Sending email for {company} ({lead_email})")
            
            # Actually send if we have a real key, otherwise mock
            if getattr(settings, "SENDGRID_API_KEY", "mock") != "mock" and settings.SENDGRID_API_KEY:
                try:
                    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                    email_content = item.get("email_content", "")
                    
                    lines = email_content.split('\n')
                    subject = "Connecting"
                    if lines[0].startswith("Subject: "):
                        subject = lines[0].replace("Subject: ", "").strip()
                        body = "\n".join(lines[1:]).strip()
                    else:
                        body = email_content
                        
                    from_email = Email(getattr(settings, "SENDER_EMAIL", "noreply@firereach.example"))
                    to_email = To(lead_email)
                    content = Content("text/plain", body)
                    mail = Mail(from_email, to_email, subject, content)
                    
                    response = sg.client.mail.send.post(request_body=mail.get())
                    item["delivery_status"] = f"Sent via SendGrid (Status: {response.status_code})"
                except Exception as e:
                    item["delivery_status"] = f"Failed to send: {str(e)}"
                    new_trace.append(f"Error sending email to {lead_email}: {str(e)}")
            else:
                item["delivery_status"] = "Simulated delivery (approved)"
        else:
            new_trace.append(f"Skipping email for {company} (Not approved)")
            if item.get("delivery_status") != "Error":
                item["delivery_status"] = "Skipped (Not approved)"
                
    return {"results": results, "trace": new_trace}


def create_agent_graph() -> StateGraph:
    """
    Creates and compiles the deterministic LangGraph workflow.
    Workflow: START -> Lead Generator -> (PAUSE) -> Contact Finder -> Harvester -> Researcher -> Outreach Generator -> (PAUSE) -> Sender -> END
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes representing the tools
    workflow.add_node("lead_generator", lead_generator_node)
    workflow.add_node("contact_finder", contact_finder_node)
    workflow.add_node("harvester", harvest_signals_node)
    workflow.add_node("researcher", research_analyst_node)
    workflow.add_node("outreach_generator", outreach_generator_node)
    workflow.add_node("sender", sender_node)
    
    # Define the deterministic edges
    workflow.add_edge(START, "lead_generator")
    workflow.add_edge("lead_generator", "contact_finder")
    workflow.add_edge("contact_finder", "harvester")
    workflow.add_edge("harvester", "researcher")
    workflow.add_edge("researcher", "outreach_generator")
    workflow.add_edge("outreach_generator", "sender")
    workflow.add_edge("sender", END)
    
    # Add memory checkpointer
    memory = MemorySaver()
    
    # Compile the graph with interrupts
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["contact_finder", "sender"]
    )

# Instantiate the globally shared graph
agent_executor = create_agent_graph()
