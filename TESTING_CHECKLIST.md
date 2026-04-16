# FireReach System Testing Checklist

## Pre-Flight Setup
- [ ] Python virtual environment created (`venv`)
- [ ] Dependencies installed via `pip install -r requirements.txt`
- [ ] `.env` file created from `.env.example`
- [ ] Mock variables validated to prevent live accidental emails. Set `SENDGRID_API_KEY=mock`.
- [ ] FastAPI boots without errors (`uvicorn app.main:app --reload`).

## Internal Node Logic Tests
- [ ] **Lead Generator**: Passing an empty `icp` immediately returns zero companies and gracefully cascades through the pipeline without halting the process.
- [ ] **Agent Trace Verification**: `trace` accurately appends "Approval decision for...", "Sending email for...", and tool invocation markers.
- [ ] **Partial Failure Safety**: Changing one lead's email format string logic manually to throw an exception does not kill the batch process iteration. Output matrix continues to populate remaining leads.
- [ ] **Outreach Generator Gate**: Ensuring `settings.SENDGRID_API_KEY` overwrite reliably blocks the tool from actually invoking an external request even if keys are accidentally left live in `.env`.

## End-to-End API Scenario
- [ ] Invoke `POST /api/v1/outreach` targeting "AI SaaS startups" via Postman or HTTPie.
- [ ] Validate response HTTP 200.
- [ ] Ensure `trace` length corresponds to the number of leads generated (approx ~30 events).
- [ ] Confirm "SKIPPED" appears next to leads that random approval evaluated as `False`.
- [ ] Verify "Drafted" appears on leads pre-approval.

## Production Integration Tests
- [ ] Insert valid Groq LLM API Key; Verify customized text outputs vs standard mock strings.
- [ ] Set strict approval to 100%, insert valid SendGrid Key + Verified Sender Domain; Verify receipt of test payload on live endpoint email securely.
