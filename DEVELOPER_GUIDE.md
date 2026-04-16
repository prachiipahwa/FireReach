# FireReach Autonomous Outreach Engine - Developer Guide

This document provides a comprehensive technical overview, testing strategy, and debugging guide for the upgraded FireReach Lead Generation and Outreach system.

---

## 1. SYSTEM OVERVIEW (CODE-BASED)

### Full Architecture
The system consists of a **FastAPI backend** managing an asynchronous REST API, which triggers a **LangGraph-powered state machine** (`agent_executor`). LangGraph enforces a strict deterministic workflow without random LLM loops, ensuring predictability.

### Updated LangGraph Pipeline
The sequential graph runs as follows:
`START` → `Lead Generator` → `Contact Finder` → `Signal Harvester` → `Research Analyst` → `Outreach Generator` → `Approval Node` → `Sender` → `END`

- **Lead Generator**: Mocks ICP keyword matching to output a list of relevant company names.
- **Contact Finder**: Formats names and generates realistic contact emails for the generated companies.
- **Signal Harvester**: Iterates over leads to fetch company-specific signals (or mocked events).
- **Research Analyst**: Mocks or calls an LLM to build a two-paragraph ICP-based account brief.
- **Outreach Generator**: Calls `tool_outreach_automated_sender` (with `SENDGRID_API_KEY` mocked out) to strictly *draft* the emails.
- **Approval Node**: Applies a semi-autonomous filter (e.g., random 80% passing) assigning `{ "approved": True }` or `False`.
- **Sender**: Conditionally uses the real SendGrid API to dispatch emails *only* if `approved == True`.

### Data Flow
1. **API Call**: Client sends `POST /api/v1/outreach` containing `icp`, `company_name` (optional fallback), and `target_email` (optional fallback). 
2. **State Ingestion**: Values initialize the `AgentState` TypedDict.
3. **Graph Execution**: State passes through nodes, accumulating outputs in the `results: List[Dict]` matrix.
4. **API Response**: Workflow finishes; FastAPI returns the `results`, individual backward-compatible tracking fields, and the aggregated `trace` log array.

### Structure of AgentState
```python
class AgentState(TypedDict):
    icp: str
    company_name: str
    target_email: str
    company_list: List[str]
    leads: List[Dict[str, str]]
    signals: str
    account_brief: str
    delivery_status: str
    email_content: str
    results: List[Dict[str, Any]] # Core Batch Matrix
    trace: list[str]              # Execution Logs
```

---

## 2. STEP-BY-STEP LOCAL SETUP GUIDE

**Requirements:** Python 3.10+

1. **Create Virtual Environment:**
   Run in the `backend/` directory:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run FastAPI Server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Run Frontend (React/Vite):**
   In a separate terminal, navigate to `frontend/`:
   ```bash
   npm install
   npm run dev
   ```

---

## 3. API TESTING GUIDE

### a) Sample Request Payload

To test the multi-lead ICP flow, use the `/outreach` endpoint:

```json
{
  "icp": "B2B SaaS companies focused on AI and machine learning looking to scale",
  "company_name": "",
  "target_email": ""
}
```

### b) curl Command execution
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/outreach' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "icp": "healthcare and medical software",
  "company_name": "",
  "target_email": ""
}'
```

### c) Expected Output Format
The response includes the global execution status, the trace array, and the batch arrays tracked inside `results` (assuming FastAPI model accommodates `results` mapping):

```json
{
  "status": "success",
  "trace": [
    "Workflow Initialized",
    "Lead Generation Started",
    "Generated 6 companies",
    "Contact Finder Started",
    "Generated 6 leads",
    "Processing company: MedTech Innovations",
    "... [Truncated Tool Executions] ...",
    "Approval decision for MedTech Innovations: APPROVED",
    "Skipping email for CareWave Health (Not approved)"
  ],
  "signals": "",
  "account_brief": "",
  "email_content": "",
  "delivery_status": ""
}
```

---

## 4. NODE-WISE TESTING STRATEGY

### Lead Generator
- **Input**: `icp` string.
- **Output**: `company_list: List[str]`.
- **Testing**: Pass an empty ICP or whitespace; verify failure safely bypasses list population.

### Contact Finder
- **Input**: `company_list: List[str]`.
- **Output**: `leads: List[dict]`.
- **Testing**: Pass a list containing empty strings or malformed objects; verify it correctly ignores invalid entities.

### Signal Harvester (Iterative)
- **Input**: `leads` list.
- **Output**: Replaces state `results` assigning `signals`.
- **Testing**: Mock the Tavily key incorrectly. Trace must show "Error fetching real signals:" inside the result string, bypassing application crashes.

### Research Analyst (Iterative)
- **Input**: `results` list containing signals.
- **Output**: Replaces state `results` assigning `account_brief`.
- **Testing**: Test with an offline Groq API key or empty `signals`. The code falls back to `mock` text payloads to guarantee execution continuation. 

### Outreach Generator (Mock Sender)
- **Input**: `results` containing `account_brief`.
- **Output**: Replaces state `results` assigning `email_content`.
- **Testing**: It forces `settings.SENDGRID_API_KEY = "mock"` safely in memory before calling the tool. Verify no live emails are sent out. 

### Approval Node
- **Input**: `results` containing drafted `email_content`.
- **Output**: Replaces state `results`, appending `approved: True/False`.
- **Testing**: Force `random.random() < 0.0` or `1.0` locally to test total rejection or acceptance behavior.

### Sender Node
- **Input**: `results` with boolean `approved` variables.
- **Output**: Modifies `delivery_status` in results natively.
- **Testing**: Execute with active SendGrid API key and valid email address to verify real email triggering *only* occurs if `approved == True`. 

---

## 5. DEBUGGING GUIDE

### Tracing Execution
The `trace` field in `AgentState` automatically traps all step-by-step logic.
- Look for `Error: ` explicitly prefixed in the trace array to find execution breakpoints without console logs.
- Trace automatically binds company names to actions: e.g., `"Error sending outreach for Acme Corp: Invalid email"`.

### Debugging JSON parsing issues
In `tool_research_analyst` and `tool_outreach_automated_sender`, Llama 3 may ignore formatting constraints and return raw markdown strings.
- We utilize `json.loads(result_str)` with a `except Exception as e:` try-catch wrapper.
- If it fails, `delivery_status` becomes `"Error parsing result"`. To debug, check the trace or extract the raw `str(e)` output from the failure content block.

### Handling Partial Failures
LangGraph state operates synchronously across items in the batch loop (`for obj in results:`). We wrapped execution blocks inside `try/except Exception as e:` during the `invoke` calls. If one company fails an API call (e.g., Timeout), it logs the internal object status as `"Error: timeout"` and the `for` loop smoothly continues to the next Lead.

---

## 6. API KEY INTEGRATION GUIDE

### a) Where API keys should be stored
Define overrides inside the `/backend/.env` file. These map to Pydantic BaseSettings in `app.core.config`:

```env
GROQ_API_KEY=gsk_abc...
TAVILY_API_KEY=tvly-...
SENDGRID_API_KEY=SG....
SENDER_EMAIL=youremail@example.com
```
*Never commit this file to version control.*

### b) Example Integrations

**Integrating Clearbit for Lead Generation**:
Inside `_simulate_company_generation()` in `graph.py`, introduce HTTP requests:
```python
import requests
def fetch_real_companies(icp: str):
    response = requests.post(
        "https://api.clearbit.com/v1/companies/search",
         headers={"Authorization": f"Bearer {settings.CLEARBIT_KEY}"},
         json={"query": icp} # Example representation
    )
    return [item['name'] for item in response.json().get('results', [])]
```

### c) Handling external failures safely
Pattern to adopt across all new nodes:
```python
try:
    # 1. External Call
    response = requests.get(...)
    response.raise_for_status() 
    item["custom_data"] = response.json()
except requests.exceptions.RequestException as e:
    # 2. Add to Trace
    new_trace.append(f"Network error on {company}: {e}")
    # 3. Graceful fallback payload
    item["custom_data"] = "Service Unavailable"
```

---

## 7. EXTENSIBILITY GUIDE

### Adding a new node
1. Define the function accepting `state: AgentState` and returning a `Dict` of fields to overwrite/append.
2. In `create_agent_graph()`, attach the node: `workflow.add_node("new_feature", new_feature_node)`
3. Rewire exactly one `add_edge()` input and output sequentially (e.g. from `harvester` -> `new_feature`, then `new_feature` -> `researcher`).

### Modifying state safely
State variables defined in `TypedDict` are entirely overwritten by node returns if they hit root keys (e.g. returning `{"trace": new_trace}` overwrites the old trace array). To safely append to arrays, you must extract first: `state.get("trace", []) + ["New"]`.

### Plugging in real APIs
Because graph logic wraps tool executions natively, you can swap `tool_signal_harvester` in `tools.py` with entirely new internal logic (e.g. replacing Tavily with Exa or SerpAPI) without modifying `graph.py` at all!
