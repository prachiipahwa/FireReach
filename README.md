# FireReach - Autonomous Lead Gen & Outreach Engine

FireReach is a highly modular, semi-autonomous sequential state machine designed to scale B2B Outbound. Using FastAPI and LangGraph, the system intelligently provisions ICPs into realistic leads, harvests business intent signals, structures contextual outreach messaging, routes them through a human-approval gatekeeper, and deploys high-volume automated campaigns via SendGrid.

## Features (Production Live Data)
- **Live Search Lead Generation:** Pass in an Ideal Customer Profile (ICP), and the engine uses **Tavily Search** and **Groq (Llama-3)** to instantly scrape the web for real-world companies that match your exact criteria.
- **Dynamic Email Enrichment:** Seamlessly integrated with **Hunter.io API** to perform lightning-fast domain searches and extract the highest-confidence decision-maker emails for the discovered companies.
- **Human-in-the-Loop React Wizard:** Review discovered companies, insert custom additions dynamically, manually approve AI-drafted messaging, and inject personalized sender signatures prior to transmission!
- **Interactive KPI Dashboard:** View live trace logs of the agent's internal reasoning and review visual execution badges upon campaign completion.
- **Direct Mail Deployment:** SendGrid architecture instantly blasts localized context if explicitly approved by the gatekeeper.

## Textual Architecture Flow
`React Wizard Payload` ➔ **FastAPI** 
➔ `INITIAL_STATE`
➔ **LangGraph** (Tavily/Groq Lead Search)
➔ **LangGraph** (Hunter.io Enrichment)
➔ `INTERRUPT: Human Company Selection`
➔ **LangGraph** (Signal Harvester `[loops per lead]`)
➔ **LangGraph** (Research Analyst `[loops per lead]`)
➔ **LangGraph** (Outreach Generator `[loops per lead]`)
➔ `INTERRUPT: Human Draft Approval`
➔ **LangGraph** (SendGrid Deployment)
➔ `REACT COMPLETED DASHBOARD`

## Setup Steps

1. **Configure Backend:**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   *Vital Keys Required:* `GROQ_API_KEY`, `TAVILY_API_KEY`, `HUNTER_API_KEY`, and `SENDGRID_API_KEY`. (Note: Keeping `SENDGRID_API_KEY="mock"` safely mocks delivery for testing).
   
3. **Boot the APIs:**
   Terminal 1 (Backend):
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Terminal 2 (Frontend React UI):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Initialize Campaign:**
   Navigate your browser to `http://localhost:5173/`, define your niche ICP in the dashboard, and watch the agents work!

*See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) and [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md) for full architectural breakdowns and credential provisioning.*
