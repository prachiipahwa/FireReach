from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Dict

class State(TypedDict):
    input: str

def node_a(state: State) -> Dict:
    return {"input": "b"}

try:
    workflow = StateGraph(State)
    workflow.add_node("a", node_a)
    workflow.set_entry_point("a") # using set_entry_point
    workflow.add_edge("a", END)
    app = workflow.compile()
    print("Test 1 (set_entry_point) Result:", app.invoke({"input": "a"}))
except Exception as e:
    print("Test 1 Failed:", repr(e))

try:
    workflow2 = StateGraph(State)
    workflow2.add_node("a", node_a)
    workflow2.add_edge(START, "a") # using START
    workflow2.add_edge("a", END)
    app2 = workflow2.compile()
    print("Test 2 (START) Result:", app2.invoke({"input": "a"}))
except Exception as e:
    print("Test 2 Failed:", repr(e))
