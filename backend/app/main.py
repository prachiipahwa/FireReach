import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

from app.core.config import settings
from app.agent.graph import agent_executor

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the FireReach Autonomous Outreach Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class OutreachRequest(BaseModel):
    icp: str
    company_name: str
    target_email: str

# Response Model
class OutreachResponse(BaseModel):
    status: str
    trace: List[str]
    signals: str
    account_brief: str
    email_content: str
    delivery_status: str

@app.post(f"{settings.API_V1_STR}/outreach", response_model=OutreachResponse)
async def generate_outreach(request: OutreachRequest):
    """
    Endpoint to trigger the autonomous outreach agentic workflow.
    Takes an ICP, target company, and target email.
    Executes the deterministic LangGraph workflow:
    START -> Signal Harvester -> Research Analyst -> Outreach Sender -> END
    """
    try:
        # Initialize the workflow state (LangGraph AgentState)
        initial_state = {
            "icp": request.icp,
            "company_name": request.company_name,
            "target_email": request.target_email,
            "signals": "",
            "account_brief": "",
            "delivery_status": "",
            "email_content": "",
            "trace": ["Workflow Initialized"]
        }
        
        # Execute the workflow
        print(f"Starting FireReach Workflow for {request.company_name}...")
        final_state = agent_executor.invoke(initial_state)
        
        # Construct the response
        response = OutreachResponse(
            status="success",
            trace=final_state.get("trace", []),
            signals=final_state.get("signals", ""),
            account_brief=final_state.get("account_brief", ""),
            email_content=final_state.get("email_content", ""),
            delivery_status=final_state.get("delivery_status", "")
        )
        return response
        
    except Exception as e:
        print(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint to ensure the API is running."""
    return {"status": "ok", "app": settings.PROJECT_NAME}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
