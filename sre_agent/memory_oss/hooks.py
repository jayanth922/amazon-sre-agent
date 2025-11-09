from __future__ import annotations
from typing import Any, Dict, List
from .client_postgres import SREMemoryClient

class MemoryHookProvider:
    """
    Called by agent nodes after an agent finishes a step.
    We keep writes conservative: only write when the response_obj
    includes explicit keys.
    """
    def __init__(self, client: SREMemoryClient):
        self.client = client

    def on_agent_response(
        self,
        *,
        agent_name: str,         # e.g., "kubernetes-agent"
        response_obj: Dict[str, Any],
        user_id: str,
        session_id: str,
    ):
        writes = 0

        # 1) User preferences (explicit structure only)
        prefs = None
        for key in ("preferences", "user_preferences"):
            val = response_obj.get(key)
            if isinstance(val, dict) and val:
                prefs = val
                break
        if prefs:
            self.client.create_event(
                strategy="preference",
                namespace=f"/sre/users/{user_id}/preferences",
                actor_id=user_id,
                session_id=None,
                role=None,
                content=prefs,
            )
            writes += 1

        # 2) Infrastructure knowledge (list or dict under common keys)
        infra_items: List[Dict[str, Any]] = []
        if isinstance(response_obj.get("infrastructure_knowledge"), list):
            infra_items = [x for x in response_obj["infrastructure_knowledge"] if isinstance(x, dict)]
        elif isinstance(response_obj.get("infrastructure_knowledge"), dict):
            infra_items = [response_obj["infrastructure_knowledge"]]
        elif isinstance(response_obj.get("knowledge"), list):
            infra_items = [x for x in response_obj["knowledge"] if isinstance(x, dict)]

        for item in infra_items:
            self.client.create_event(
                strategy="infrastructure",
                namespace=f"/sre/infrastructure/{agent_name}/{user_id}",
                actor_id=agent_name,       # agent-scoped knowledge
                session_id=session_id,
                role=None,
                content=item,
            )
            writes += 1

        return {"ok": True, "written": writes}
