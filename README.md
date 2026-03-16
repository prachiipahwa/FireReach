# FireReach 🚀 – Autonomous Outreach Engine

FireReach is a production-ready agentic AI system that performs hyper-personalized B2B outreach by autonomously chaining real-time web search signals, LLM account research, and automated email delivery.

## 🧠 Project Overview
Designed to replace manual SDR research, FireReach takes a specific Ideal Customer Profile (ICP), a Target Company, and an Email. It then executes a deterministic **LangGraph Workflow** to harvest live growth signals (funding, hiring, market expansion), synthesizes a strategic account brief, and drafts an email explicitly referencing those real-time signals before dispatching it.

## 🏗️ Architecture & Tech Stack
- **Frontend Dashboard**: React + Vite (Aesthetic dark-mode glassmorphic UI)
- **Backend API Orchestrator**: Python + FastAPI
- **Agent Framework**: LangGraph (Deterministic Workflow)
- **LLM Reasoning**: Groq (Llama-3 70B)
- **Live Search API**: Tavily Search API
- **Email Dispatch**: SendGrid API

## ⚙️ Local Setup Instructions
To run this project locally, ensure you have Python 3.11+ and Node 18+ installed.

### 1. Environment Setup
Create a `.env` file in `firereach/backend/.env`:
```env
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
SENDGRID_API_KEY=your_key_here
SENDER_EMAIL=your_verified_sendgrid_email@example.com
```

### 2. Backend Server
```bash
cd backend
python -m venv venv
# Activate venv: `source venv/bin/activate` or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173` to test the UI!

## 📸 Dashboard Screenshots
*(Upload a screenshot of the FireReach UI here showcasing the "Campaign Target" input form and the generated LangGraph trace output panels).*

## 🌍 Free Deployment Links
* **Frontend (Vercel)**: `https://fire-reach-iota.vercel.app/`
* **Backend API (Render)**: `https://firereach-api-flbo.onrender.com/docs`

*For detailed system architecture, tool schemas, and free deployment guides, please see [DOCS.md](DOCS.md).*
