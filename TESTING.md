# FireReach Local Testing Guide

This guide provides a precise, step-by-step walkthrough for testing the FireReach Autonomous Outreach Engine locally from scratch, tailored exactly to the generated code.

---

## 1. Prerequisites

Before starting, ensure your system has the following installed:

* **Python version**: Python 3.10 or higher (3.11+ recommended).
* **Node.js version**: Node.js 18.x or higher.
* **Package Managers**: `npm` (comes with Node.js) and `pip` (Python).

**Required Python Packages** (from `backend/requirements.txt`):
* `fastapi`
* `uvicorn`
* `pydantic`, `pydantic-settings`
* `langchain-core`, `langchain-groq`, `langgraph`
* `tavily-python`
* `sendgrid`
* `python-dotenv`

**Required Environment Variables**:
* `GROQ_API_KEY`: Required for Llama 3 LLM reasoning.
* `TAVILY_API_KEY`: Required for the signal harvester web search.
* `SENDGRID_API_KEY`: Required for dispatching the drafted emails.
* `SENDER_EMAIL`: The verified "from" email address configured in SendGrid.

*(Note: The system supports falling back to mocked signals/emails if the keys are set to exactly `"mock"` or left empty, allowing functional UI testing without live credentials).*

---

## 2. Environment Setup

The backend relies on `pydantic-settings` to load configurations. You must define an environment file `.env` inside the `firereach/backend/` directory.

Create a file named `.env` in `firereach/backend/` and use the following template:

```env
# /firereach/backend/.env

# API Keys
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Optional API Keys for extended harvesting
SERPAPI_API_KEY=
NEWSAPI_KEY=

# Email Sender Profile
SENDER_EMAIL=noreply@firereach.ai
```

---

## 3. Backend Setup

Open a terminal to configure and launch the FastAPI orchestrator.

**1. Navigate to the backend directory**:
```bash
# Windows
cd "d:\NALR\rabbit\Fire Reach\firereach\backend"

# macOS/Linux
cd path/to/firereach/backend
```

**2. Create and activate a virtual environment**:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**:
```bash
pip install -r requirements.txt
```

**4. Run the FastAPI server**:
```bash
python -m uvicorn app.main:app --reload --port 8000
```
*(If `uvicorn` is not found, running it via `python -m uvicorn` ensures the virtual environment's module is used).*

**Expected Console Output**:
```text
INFO:     Will watch for changes in these directories: ['path/to/firereach/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1234] using WatchFiles
INFO:     Started server process [5678]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 4. Frontend Setup

Open a **new** terminal to configure and start the Vite React dashboard.

**1. Navigate to the frontend directory**:
```bash
# Windows
cd "d:\NALR\rabbit\Fire Reach\firereach\frontend"

# macOS/Linux
cd path/to/firereach/frontend
```

**2. Install dependencies**:
```bash
npm install
```

**3. Run the Vite development server**:
```bash
npm run dev
```

**Expected Console Output**:
```text
  VITE v5.4.0  ready in 400 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 5. Backend API Test

You can test the LangGraph workflow directly via the interactive Swagger UI.

1. Open your browser and navigate to: **http://localhost:8000/docs**
2. Expand the `POST /api/v1/outreach` endpoint.
3. Click the **"Try it out"** button.
4. Input the following sample JSON request body:

```json
{
  "icp": "Mid-market B2B SaaS companies focused on developer tooling.",
  "company_name": "Vercel",
  "target_email": "hello@vercel.example.com"
}
```

5. Click **"Execute"**.
6. **Expected Response Structure**:
The server will return a `200 OK` status with the complete deterministic output:
```json
{
  "status": "success",
  "trace": [
    "Workflow Initialized",
    "Tool Executed: tool_signal_harvester",
    "Tool Executed: tool_research_analyst",
    "Tool Executed: tool_outreach_automated_sender"
  ],
  "signals": "{\n  \"company\": \"Vercel\",\n  \"signals\": [\n    ...array of extracted news...\n  ]\n}",
  "account_brief": "Paragraph 1: Vercel has recently expanded... \n\nParagraph 2: Given the ICP...",
  "email_content": "Subject: Scaling Your Developer Tools at Vercel \n\nHi there,\n...",
  "delivery_status": "Sent successfully via SendGrid (Status: 202)"
}
```

---

## 6. End-to-End UI Test

To test the entire workflow visually from the React frontend:

1. Open your browser to: **http://localhost:5173**
2. In the "Campaign Target" panel on the left, input the following values:
   - **Target Company**: `Acme Corp` (or any real company to see live Tavily signals)
   - **Target Email**: `founder@acmecorp.example.com`
   - **Ideal Customer Profile (ICP)**: `B2B SaaS companies focused on AI-driven sales enablement tools needing scalable infrastructure.`
3. Click **"Initialize Workflow"**.

**What will appear in the UI:**
The UI will enter a loading state with a spinner. Once the FastAPI backend returns the LangGraph execution payload, the right-hand panel will populate with four sections:
* **Agent Reasoning Loop**: A list verifying the execution trace (`START -> tool_signal_harvester -> tool_research_analyst -> tool_outreach_automated_sender -> END`).
* **Harvested Signals**: A bulleted list of 5 recent growth indicators fetched by Tavily (funding, hiring, etc.).
* **Strategic Account Brief**: Two dense paragraphs explaining the company's growth factors and their alignment with the inputted ICP layout.
* **Autonomous Outreach Draft**: The finalized, hyper-personalized email explicitly referencing the harvested signals dynamically drafted by Llama 3.
* **Delivery Status Badge**: Located below the email draft, confirming if the email bypassed Sandbox or was fired through SendGrid successfully.

---

## 7. Troubleshooting

If you encounter issues while testing, consult the common errors below:

**1. Missing or Invalid API Keys**
* **Error**: The output signals or account brief mentions "Error analyzing signals: Authentication failed..." or you receive a Groq validation error in the FastAPI console.
* **Fix**: Ensure your `.env` is located strictly inside `firereach/backend/.env`. Stop the Uvicorn terminal (CTRL+C) and restart the server to ensure environment variables are newly loaded. 

**2. SendGrid Not Configured**
* **Error**: The UI Delivery Status Badge says "Failed to send email: The from address does not match a verified Sender Identity."
* **Fix**: SendGrid requires Domain Authentication. Ensure the `SENDER_EMAIL` in your `.env` exactly matches the email authorized in your SendGrid dashboard settings.

**3. CORS Errors in Browser Console**
* **Error**: The UI freezes on the loading spinner, and opening the Browser Console (F12) shows a "CORS policy" block.
* **Fix**: The React dashboard uses a Vite proxy in `vite.config.js` to route `/api` explicitly to `http://localhost:8000`. Ensure you are running the frontend via `npm run dev` and accessing `http://localhost:5173`. Do *not* open `index.html` directly in the browser via file path.

**4. Tavily API Returning Empty Signals**
* **Error**: The "Harvested Signals" list in the UI says "Error fetching real signals".
* **Fix**: Ensure your `TAVILY_API_KEY` is fully provisioned and not out of credits. As a fallback, you can remove the key or set `TAVILY_API_KEY=mock` in your `.env` to engage the fallback mock-payload logic defined in `tools.py` for testing.

**5. Uvicorn "Cannot import name 'app'"**
* **Error**: Running the uvicorn command results in an ImportError.
* **Fix**: Ensure you are executing the command `python -m uvicorn app.main:app --reload` from the literal `firereach/backend/` directory, so python can see the root `app/` folder.
