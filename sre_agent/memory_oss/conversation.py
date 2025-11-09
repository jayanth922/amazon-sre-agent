from __future__ import annotations
from typing import List, Dict, Any
from .client_postgres import SREMemoryClient

NAMESPACE_TPL = "/sre/conversations/{user_id}/{session_id}"

def create_conversation_memory_manager(client: SREMemoryClient):
    """
    Returns save_batch(user_id, session_id, messages)
    messages: list of dicts, each with at least {"role": "...", "content": ...}
    We'll store one row per message under strategy='conversation'.
    """
    def save_batch(*, user_id: str, session_id: str, messages: List[Dict[str, Any]]):
        ns = NAMESPACE_TPL.format(user_id=user_id, session_id=session_id)
        written = 0
        for m in messages or []:
            role = m.get("role") or m.get("type") or "unknown"
            raw_content = m.get("content")
            # normalize content to JSON-serializable structure
            if isinstance(raw_content, (str, dict, list)):
                content = raw_content
            else:
                content = {"text": str(raw_content)}
            client.create_event(
                strategy="conversation",
                namespace=ns,
                actor_id=user_id,           # conversation is scoped to user
                session_id=session_id,
                role=role,
                content=content,
                embed_text=None,            # no need to embed convo rows
            )
            written += 1
        return {"ok": True, "written": written}
    return save_batch
