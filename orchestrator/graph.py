from langgraph.graph import StateGraph, END
from state import GraphState
from agents.triage import TriageAgent
from agents.observability import ObservabilityAgent
from agents.knowledge import KnowledgeAgent
from agents.executor import ExecutorAgent

def _route(st: GraphState):
    if st.get("need_metrics"):   return "observability"
    if st.get("need_runbook"):   return "knowledge"
    if st.get("proposed_action"):return "executor"
    return END

def build_graph():
    g = StateGraph(GraphState)
    g.add_node("triage", TriageAgent().run)
    g.add_node("observability", ObservabilityAgent().run)
    g.add_node("knowledge", KnowledgeAgent().run)
    g.add_node("executor", ExecutorAgent().run)
    g.set_entry_point("triage")
    for n in ["triage","observability","knowledge","executor"]:
        g.add_conditional_edges(n, _route)
    return g.compile()
