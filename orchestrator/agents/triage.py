import uuid
from typing import Any, Dict
from state import GraphState

class TriageAgent:
    name = "triage"

    async def run(self, st: GraphState) -> GraphState:
        if "incident_id" not in st:
            st["incident_id"] = str(uuid.uuid4())
            st["notes"] = []
        st["notes"].append("triage: parsed alert and set flags")
        # naive rules for demo
        st["need_metrics"] = True
        st["need_runbook"] = True
        return st
