# FireReach - Autonomous Lead Gen & Outreach Engine

FireReach is a highly modular, semi-autonomous sequential state machine designed to scale B2B Outbound. Using FastAPI and LangGraph, the system intelligently provisions ICPs into realistic leads, harvests business intent signals, structures contextual outreach messaging, routes them through a human-approval gatekeeper, and deploys high-volume automated campaigns via SendGrid.

## Features (Upgraded System)
- **ICP-driven Lead Generation:** Seed an Idea Customer Profile (ICP); let the engine mock the market segment and synthesize responsive leads.
- **Batch Processing:** Sequentially process arrays of potential prospects seamlessly resolving errors internally per target to prevent total system collapse.
- **Autonomous Signal Harvesting & Research Agent:** Pull relevant news events or technical stacks per domain and construct compelling reasons to connect.
- **Human-in-the-Loop Approval:** The core graph forces drafted messaging through a discrete Approval routing sequence preventing out-of-bounds dispatch.
- **Direct Mail Deployment:** Pluggable SendGrid architecture instantly blasts localized context if explicitly approved.

## Textual Architecture Flow
`User API payload` ➔ **FastAPI** 
➔ `INITIAL_STATE (AgentState)`
➔ **LangGraph** (Lead Generator)
➔ **LangGraph** (Contact Finder)
➔ **LangGraph** (Signal Harvester `[loops per lead]`)
➔ **LangGraph** (Research Analyst `[loops per lead]`)
➔ **LangGraph** (Outreach Generator `[loops per lead]`)
➔ **LangGraph** (Human Approval Filter)
➔ **LangGraph** (Delivery Sender)
➔ `FASTAPI RESPONSE`

## Setup Steps

1. Configure virtual env:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Configure environment:
   ```bash
   cp .env.example .env
   # Update variables
   ```
3. Boot the API:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Usage

Endpoint: `POST /api/v1/outreach`

Payload:
```json
{
  "icp": "Healthcare AI SaaS seeking Series A funding",
  "company_name": "",
  "target_email": ""
}
```

Wait roughly 5-15 seconds for deterministic graph compilation and mocked LLM outputs. The API will respond with full pipeline trace logs, extracted signals, and aggregated dispatch states mapping which targets succeeded dynamically!

*See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for full architectural breakdowns and testing strategies!*
