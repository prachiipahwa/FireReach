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

# Request Models
class StartRequest(BaseModel):
    icp: str

class ResumeRequest(BaseModel):
    thread_id: str
    company_list: List[str] = None
    results: List[Dict[str, Any]] = None

# Response Models
class WorkflowResponse(BaseModel):
    status: str
    thread_id: str
    state: str
    trace: List[str]
    company_list: List[str]
    results: List[Dict[str, Any]]

import uuid

@app.post(f"{settings.API_V1_STR}/outreach/start", response_model=WorkflowResponse)
async def start_workflow(request: StartRequest):
    """
    Initializes the LangGraph workflow and runs up to the first breakpoint.
    """
    try:
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state = {
            "icp": request.icp,
            "company_name": "",
            "target_email": "",
            "company_list": [],
            "leads": [],
            "results": [],
            "trace": ["Workflow Initialized"]
        }
        
        print(f"Starting FireReach Workflow for thread: {thread_id}...")
        
        # Invoke up to the first breakpoint (contact_finder)
        for chunk in agent_executor.stream(initial_state, config):
            pass 
        
        # Get the suspended state
        current_state = agent_executor.get_state(config)
        
        response = WorkflowResponse(
            status="success",
            thread_id=thread_id,
            state="paused_at_companies",
            trace=current_state.values.get("trace", []),
            company_list=current_state.values.get("company_list", []),
            results=current_state.values.get("results", [])
        )
        return response
        
    except Exception as e:
        print(f"Workflow initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/outreach/resume", response_model=WorkflowResponse)
async def resume_workflow(request: ResumeRequest):
    """
    Injects human decisions and resumes the workflow.
    """
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        current_state = agent_executor.get_state(config)
        
        if not current_state:
             raise HTTPException(status_code=404, detail="Thread not found")
             
        # Inject the state changes passed by the user
        state_update = {}
        if request.company_list is not None:
             state_update["company_list"] = request.company_list
        if request.results is not None:
             state_update["results"] = request.results
             
        if state_update:
             agent_executor.update_state(config, state_update)
             
        # Resume the workflow by invoking with None
        print(f"Resuming thread {request.thread_id}...")
        for chunk in agent_executor.stream(None, config):
            pass
            
        new_state = agent_executor.get_state(config)
        
        # Determine current status
        # If there are no next nodes, we are DONE.
        if not new_state.next:
             current_step = "completed"
        elif "sender" in new_state.next:
             current_step = "paused_at_approval"
        else:
             current_step = "processing"
             
        response = WorkflowResponse(
            status="success",
            thread_id=request.thread_id,
            state=current_step,
            trace=new_state.values.get("trace", []),
            company_list=new_state.values.get("company_list", []),
            results=new_state.values.get("results", [])
        )
        return response
        
    except Exception as e:
        print(f"Workflow resume failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint to ensure the API is running."""
    return {"status": "ok", "app": settings.PROJECT_NAME}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
