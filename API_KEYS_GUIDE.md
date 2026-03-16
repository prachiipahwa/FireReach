# FireReach API Key Configuration Guide

This guide explains how to obtain, configure, and verify the real API keys required to run the FireReach Autonomous Outreach Engine in production mode.

---

## 1. Purpose of Each API Key in This Project

The FireReach backend relies on exactly three external services to operate the LangGraph workflow. If these keys are missing or set to `mock`, the system will fall back to simulated data.

* **`GROQ_API_KEY`**: 
  * **Used in**: `tool_research_analyst` and `tool_outreach_automated_sender`.
  * **Purpose**: Powers the fast Llama-3 (`llama3-70b-8192`) LLM reasoning. It synthesizes the raw signals into the strategic account brief and dynamically drafts the highly personalized outreach emails.
* **`TAVILY_API_KEY`**: 
  * **Used in**: `tool_signal_harvester`.
  * **Purpose**: Performs real-time intent-focused web searches (funding, hiring, expansion, etc.) to fetch live company growth signals.
* **`SENDGRID_API_KEY`**: 
  * **Used in**: `tool_outreach_automated_sender`.
  * **Purpose**: Authenticates with SendGrid's email API to dispatch the drafted personalized outreach emails to the target recipients.
* **`SENDER_EMAIL`**: 
  * **Used in**: `tool_outreach_automated_sender`.
  * **Purpose**: The verified "From" email address used by SendGrid to send the emails. It must exactly match a Sender Identity verified in your SendGrid account.

---

## 2. How to Create Each API Key

### A. Groq API Key
Groq provides blazing-fast inference for LangChain's LLM components.
1. **Sign Up**: Go to the [Groq Console](https://console.groq.com/).
2. **Generate Key**: Click on **API Keys** in the left sidebar, then click **Create API Key**. Name it "FireReach".
3. **Usage Limits**: The free tier includes generous rate limits (e.g., thousands of tokens per minute for Llama-3 models). Keep the key secure.

### B. Tavily API Key
Tavily acts as an AI-focused search engine for the signal harvester.
1. **Sign Up**: Go to [Tavily](https://tavily.com/) and create an account.
2. **Generate Key**: After logging in, you will land on the API dashboard where your API key is displayed. Copy it.
3. **Usage Limits**: The free "Research" tier provides 1,000 free API calls per month.

### C. SendGrid API Key & Sender Email
SendGrid is the SMTP/API service that delivers your outreach.
1. **Sign Up**: Go to [SendGrid](https://sendgrid.com/) and create an account.
2. **Generate API Key**: 
   * Navigate to **Settings** > **API Keys** in the left sidebar.
   * Click **Create API Key**. 
   * Give it **Restricted Access** (specifically Mail Send privileges) or **Full Access**, and copy the generated `SG...` key.
3. **Verify Sender Email (`SENDER_EMAIL`)**: 
   * Go to **Settings** > **Sender Authentication**.
   * Under **Single Sender Verification**, click **Verify a Single Sender**.
   * Fill out your organizational details and the specific email address you want to send from.
   * Check your inbox and click the verification link. The email you verified is your `SENDER_EMAIL`.

---

## 3. How to Configure the Keys in the FireReach Project

Create a file named `.env` strictly inside the `firereach/backend/` directory. Copy the real keys into it exactly as structured below. Do not use quotes around the values.

```env
# /firereach/backend/.env

# API Keys
GROQ_API_KEY=your_real_groq_api_key_here
TAVILY_API_KEY=your_real_tavily_api_key_here
SENDGRID_API_KEY=your_real_sendgrid_api_key_here

# Email Sender Profile (Must be verified in SendGrid)
SENDER_EMAIL=your_verified_email@example.com
```

---

## 4. How to Verify Each API is Working

Restart your FastAPI server (`python -m uvicorn app.main:app --reload --port 8000`) after updating the `.env` file, then initialize the workflow from the React dashboard.

* **Verify Tavily**: In the dashboard, the "Harvested Signals" section should display very recent, real-world news or data specific to the Target Company you inputted, rather than hardcoded mock funding lines.
* **Verify Groq**: The "Strategic Account Brief" and "Autonomous Outreach Draft" will be dynamically generated and highly varied depending on the target company and ICP. It will not use the fallback mock template.
* **Verify SendGrid**: The "Delivery Status" badge at the bottom of the dashboard will display a 200/202 status code instead of "Simulated delivery". For example: `Sent successfully via SendGrid (Status: 202)`. You should also actually receive the email in the target inbox!

---

## 5. Common Mistakes & Troubleshooting

If things aren't working as expected, check these common pitfalls:

* **Unverified Sender Email**: If SendGrid returns a `403 Forbidden` or `Failed to send email` error, ensure the `SENDER_EMAIL` in your `.env` exactly matches the email address you verified in SendGrid's *Single Sender Verification*.
* **Environment Variables Not Loading**: If the UI still shows generic mock data, the FastAPI server hasn't read the `.env` file. Stop the Uvicorn terminal instance (CTRL+C) and run it again to load the new variables from `backend/.env`.
* **Expired or Invalid API Keys**: Ensure you haven't accidentally pasted whitespace or quotes at the end of the keys in the `.env` file. Groq will throw an `AuthenticationError` if the key is invalid.
* **Rate Limits**: If you are looping the agent heavily within a minute, you may hit the Groq or Tavily free-tier rate limitations, resulting in a `429 Too Many Requests` error logged in the FastAPI terminal.
* **Tavily Returning Empty Data**: If Tavily cannot find any recent news on a highly obscure target company, the harvester array might be empty. Ensure the target company has a digital footprint.
