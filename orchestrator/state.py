from typing import TypedDict, List, Any, Optional

class GraphState(TypedDict, total=False):
    incident_id: str
    alert: dict
    notes: List[str]
    need_metrics: bool
    need_runbook: bool
    proposed_action: Optional[str]
    result: Any
