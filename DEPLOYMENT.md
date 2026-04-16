# FireReach Public Deployment Guide (Zero-Cost)

This guide provides exactly tailored, step-by-step instructions for deploying the **FireReach Autonomous Outreach Engine** to the public internet using only 100% free services. 

---

## 1. Verify Repository Structure

Before deploying, ensure your GitHub repository explicitly mirrors the layout generated during local development.

**Expected GitHub Structure:**
```text
firereach/
├── backend/                  <-- FASTAPI BACKEND ROOT
│   ├── app/
│   │   ├── main.py
│   │   ├── agent/
│   │   └── core/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 <-- REACT FRONTEND ROOT
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   ├── index.html
│   ├── package.json
│   ├── vercel.json           <-- SPA Routing Config
│   └── vite.config.js
├── README.md
└── DOCS.md
```
*(Notice that the `.env` file is excluded, as it contains private keys).*

---

## 2. Deploy the Backend on Render (Free Tier)

Render will host the FastAPI orchestrator and the LangGraph workflow utilizing the `Dockerfile` we generated.

1. **Create Account**: Go to [Render](https://render.com/) and sign up for a free account using your GitHub login.
2. **Launch Web Service**: Click **New +** in the top right, then select **Web Service**.
3. **Connect Repository**: Authorize your GitHub account and select your `firereach` repository.
4. **Configuration Settings**:
   * **Name**: `firereach-api`
   * **Language/Environment**: Choose **Docker**. Render will parse your `Dockerfile` to handle the installation and Uvicorn startup automatically.
   * **Root Directory**: `backend` *(CRITICAL: Tell Render to look inside the backend folder for the Dockerfile).*
   * **Instance Type**: Select **Free**.
5. **Set Environment Variables**: Scroll down, click **Advanced**, then **Add Environment Variable**. Add the following exactly (with your real keys):
   * `GROQ_API_KEY`: <your-groq-key>
   * `TAVILY_API_KEY`: <your-tavily-key>
   * `SENDGRID_API_KEY`: <your-sendgrid-key>
   * `SENDER_EMAIL`: <your-verified-sendgrid-email>
6. **Deploy**: Click **Create Web Service**. 
   * **Expected Build Command**: Processed by Docker automatically (`COPY requirements.txt .`, `RUN pip install -r requirements.txt`).
   * **Expected Start Command**: Processed by Docker automatically (`CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", ...`).
7. **Verify API is Working**: Once the deployment logger completes, Render will provide a URL like `https://firereach-api-xxxy.onrender.com`. Click it and append `/docs`. You should see the interactive Swagger UI!

---

## 3. Deploy the Frontend on Vercel (Free Tier)

Vercel will host the Vite + React aesthetic dashboard.

1. **Create Account**: Go to [Vercel](https://vercel.com/) and sign up for a free "Hobby" account using your GitHub login.
2. **Add New Project**: From your dashboard, click **Add New...** -> **Project**.
3. **Import Repository**: Find the `firereach` repository from the linked GitHub list and click **Import**.
4. **Configuration Settings**:
   * **Framework Preset**: Vercel should auto-detect **Vite**.
   * **Root Directory**: Click "Edit" and type `frontend`. *(CRITICAL: This tells Vercel where the React code lives).*
   * **Build Command**: Leave default (`npm run build`).
   * **Output Directory**: Leave default (`dist`).
5. **Set Environment Variables**: Expand the environment variables tab and configure the React app to hit your newly deployed Render API.
   * **Name**: `VITE_API_URL`
   * **Value**: `https://firereach-api-xxxy.onrender.com/api/v1` *(REPLACE THIS with your exact Render backend URL + `/api/v1`).*
6. **Deploy**: Click **Deploy**. Vercel will install dependencies, build the Vite app, and parse our custom `vercel.json` to handle React Router traffic seamlessly.
7. **Verify Frontend**: Vercel will generate a URL like `https://firereach-ui.vercel.app`. Click it to see your live dashboard.

---

## 4. Connect Frontend to Backend

Because we dynamically used Vite Environment Variables in the code I generated:
```javascript
// firereach/frontend/src/api.js
baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
```
The React app strictly relies on the `VITE_API_URL` you deployed in Vercel Step 5. By passing your remote Render URL there, the preconfigured FastAPI `CORSMiddleware` (which we wildcarded to `allow_origins=["*"]` during debugging) will automatically accept traffic from Vercel without blocking it!

---

## 5. Final Live Test Step-by-Step

To verify your system is fully autonomous in the cloud:

1. Open your Vercel frontend URL (e.g., `https://firereach-ui.vercel.app`).
2. **Input Test Campaign**:
   * **Target Company**: Apple
   * **Target Email**: hello@apple.example.com
   * **ICP**: Consumer tech companies looking to scale AI-driven supply chain logistics.
3. Click **"Initialize Workflow"**.
4. Monitor the right-hand panel. It should incrementally reveal:
   * **Agent Reasoning Loop**: Confirming LangGraph walked through the Harvester -> Analyst -> Sender chain.
   * **Harvested Signals**: Live, true recent news about Apple pulled from Tavily.
   * **Strategic Account Brief**: Two paragraphs written by Groq validating your ICP against the news.
   * **Autonomous Outreach Draft**: The drafted email linking the supply chain logistics directly to the fetched news.
   * **Delivery Status Badge**: Displaying `Sent successfully via SendGrid (Status: 202)` (or a Sandbox mocked delivery).

---

## 6. Common Deployment Issues & Fixes

**1. Render Build Failures**
* **Issue**: The build fails saying "No package.json found" or similar.
* **Fix**: You didn't set the **Root Directory** to `backend`. Render is trying to deploy the whole repo at once instead of specifically deploying the Python API folder.

**2. Frontend Calling Localhost (`Failed to fetch`)**
* **Issue**: Clicking "Initialize Workflow" instantly fails with a Network Error, and the F12 Network tab shows it tried to ping `http://localhost:8000`.
* **Fix**: The React dashboard didn't receive your `VITE_API_URL`. Go to your Vercel Project Settings -> Environment Variables, ensure it is added, and **Redeploy** the frontend.

**3. Render "Spin Down" Rate Limiting**
* **Issue**: The first API request of the day takes 60 seconds.
* **Fix**: Render's free tier automatically spins down idle servers after 15 minutes of inactivity. When you hit "Initialize Workflow", it has to cold-start. Simply wait 45-60 seconds, and it will process normally.

**4. SendGrid Sender Verification Blocks**
* **Issue**: The dashboard returns "Failed to send email: The from address does not match a verified Sender Identity."
* **Fix**: The `SENDER_EMAIL` you placed in your Render environment variables is not authorized by your SendGrid account. Log into SendGrid and complete "Single Sender Verification". 

**5. 500 Internal Server Error (Missing Keys)**
* **Issue**: The LangGraph trace fails immediately with a 500 error.
* **Fix**: You forgot to add `GROQ_API_KEY` or `TAVILY_API_KEY` to the Render Environment Variables tab. Add them and manual click "Manual Deploy" -> "Deploy latest commit" in Render.
