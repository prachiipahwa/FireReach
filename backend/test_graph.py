import sys
import traceback

try:
    from app.agent.graph import agent_executor
    initial_state = {
        "icp": "test",
        "company_name": "test",
        "target_email": "test@test.example.com",
        "signals": "",
        "account_brief": "",
        "delivery_status": "",
        "email_content": "",
        "trace": ["Workflow Initialized"]
    }
    result = agent_executor.invoke(initial_state)
    print("SUCCESS")
    print(result)
except Exception as e:
    print("FAILED")
    print(repr(e))
    traceback.print_exc()
