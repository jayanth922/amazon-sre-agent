from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any, Iterable, Optional

from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from sqlalchemy.dialects.postgresql import JSONB

# Lazy import for sentence-transformers to keep import time low
_EMBED_MODEL = None

def _get_embed_model():
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer  # type: ignore
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        _EMBED_MODEL = SentenceTransformer(model_name)
    return _EMBED_MODEL

def _now() -> datetime:
    return datetime.utcnow()

_TTL_DAYS = {
    "preference": 90,
    "infrastructure": 30,
    "investigation": 60,
    "conversation": 14,  # short-term
}

_EMBED_STRATS = {"preference", "infrastructure"}

class SREMemoryClient:
    """
    Drop-in replacement for the sample's memory client.
    Stores events in Postgres with optional pgvector embeddings.
    """

    def __init__(self, dsn: Optional[str] = None):
        self.dsn = dsn or os.getenv("SRE_MEMORY_DSN", "postgresql+psycopg://sre:sre@localhost:5432/sre_memory")
        self.engine: Engine = create_engine(self.dsn, future=True)

        # Quick connectivity check (non-fatal if DB is starting)
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except OperationalError as e:
            # Let caller handle startup order; they can retry later
            print(f"[SREMemoryClient] DB not ready yet: {e}")

    # -------------------------
    # Helpers
    # -------------------------
    def _maybe_embed(self, text_to_embed: Optional[str], strategy: str) -> Optional[list[float]]:
        if strategy not in _EMBED_STRATS or not text_to_embed or not text_to_embed.strip():
            return None
        model = _get_embed_model()
        # returns a numpy array; convert to python list for psycopg
        vec = model.encode(text_to_embed, normalize_embeddings=True)
        return vec.tolist()  # type: ignore

    def _ttl_for(self, strategy: str) -> Optional[datetime]:
        days = _TTL_DAYS.get(strategy)
        return _now() + timedelta(days=days) if days else None

    # -------------------------
    # Public API
    # -------------------------
    def create_event(
        self,
        *,
        strategy: str,
        namespace: str,
        actor_id: str,
        session_id: Optional[str] = None,
        role: Optional[str] = None,
        content: Any = None,
        embed_text: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Insert an event. If strategy is semantic, compute embedding.
        Returns {"ok": True, "id": "..."} on success.
        """
        if content is None:
            content = {}

        # Choose text for embedding
        text_to_embed = embed_text
        if text_to_embed is None:
            if isinstance(content, str):
                text_to_embed = content
            elif isinstance(content, dict):
                # Prefer common keys if present
                for k in ("summary", "text", "value", "details"):
                    if k in content and isinstance(content[k], str):
                        text_to_embed = content[k]
                        break
                if text_to_embed is None:
                    text_to_embed = json.dumps(content, ensure_ascii=False)
            else:
                text_to_embed = str(content)

        embedding = self._maybe_embed(text_to_embed, strategy)
        ttl = self._ttl_for(strategy)

        with self.engine.begin() as conn:
            stmt = text(
                """
                INSERT INTO events
                    (strategy, namespace, actor_id, session_id, role, content, embedding, ttl_expires_at, metadata)
                VALUES
                    (:strategy, :namespace, :actor_id, :session_id, :role, :content, :embedding, :ttl, :metadata)
                RETURNING id::text
                """
            ).bindparams(
                bindparam("content", type_=JSONB),
                bindparam("metadata", type_=JSONB),
            )

            result = conn.execute(
                stmt,
                {
                    "strategy": strategy,
                    "namespace": namespace,
                    "actor_id": actor_id,
                    "session_id": session_id,
                    "role": role,
                    # pass native Python objects, not json.dumps(...)
                    "content": content,
                    "embedding": embedding,
                    "ttl": ttl,
                    "metadata": metadata or {},
                },
            )
            new_id = result.scalar_one()
        return {"ok": True, "id": new_id}

    def retrieve_memories(
        self,
        *,
        memory_type: str,         # "preference" | "infrastructure" | "investigation"
        actor_id: Optional[str] = None,
        query: str = "*",
        max_results: int = 20,
        session_id: Optional[str] = None,
        namespace_prefix: Optional[str] = None,
    ) -> dict:
        """
        Search events for planning-time retrieval.
        - For 'preference' and 'infrastructure': semantic search (cosine distance ASC).
        - For 'investigation': keyword search (ILIKE) or recent if query == "*".
        """
        memory_type = memory_type.lower()
        if memory_type in _EMBED_STRATS:
            # Semantic search
            query_vec = self._maybe_embed(query, memory_type) or self._maybe_embed(" ", memory_type)
            where = ["strategy = :strategy"]
            params: dict[str, Any] = {"strategy": memory_type, "limit": max_results, "query_vec": query_vec}

            if actor_id:
                where.append("actor_id = :actor_id")
                params["actor_id"] = actor_id
            if session_id:
                where.append("(session_id = :session_id OR session_id IS NULL)")
                params["session_id"] = session_id
            if namespace_prefix:
                where.append("namespace LIKE :ns")
                params["ns"] = f"{namespace_prefix}%"

            sql = f"""
                SELECT id::text, namespace, actor_id, session_id, created_at,
                       1 - (embedding <=> CAST(:query_vec AS vector)) AS score, content
                FROM events
                WHERE {' AND '.join(where)} AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:query_vec AS vector) ASC
                LIMIT :limit
            """
            with self.engine.begin() as conn:
                rows = conn.execute(text(sql), params).mappings().all()
            return {"ok": True, "items": [dict(r) for r in rows]}

        else:
            # Investigation: keyword or recent
            where = ["strategy = :strategy"]
            params = {"strategy": "investigation", "limit": max_results}

            if actor_id:
                where.append("actor_id = :actor_id")
                params["actor_id"] = actor_id
            if session_id:
                where.append("(session_id = :session_id OR session_id IS NULL)")
                params["session_id"] = session_id
            if namespace_prefix:
                where.append("namespace LIKE :ns")
                params["ns"] = f"{namespace_prefix}%"

            if query and query != "*":
                where.append("content::text ILIKE :q")
                params["q"] = f"%{query}%"
                order = "ORDER BY created_at DESC"
            else:
                order = "ORDER BY created_at DESC"

            sql = f"""
                SELECT id::text, namespace, actor_id, session_id, created_at, NULL::float AS score, content
                FROM events
                WHERE {' AND '.join(where)}
                {order}
                LIMIT :limit
            """
            with self.engine.begin() as conn:
                rows = conn.execute(text(sql), params).mappings().all()
            return {"ok": True, "items": [dict(r) for r in rows]}

    # Placeholder signatures for later steps
    def save_investigation_summary(self, *, user_id: str, session_id: str, summary: dict) -> dict:
        return self.create_event(
            strategy="investigation",
            namespace=f"/sre/investigations/{user_id}/{session_id}",
            actor_id=user_id,
            session_id=session_id,
            role=None,
            content=summary,
        )

    def get_last_k_turns(self, *, user_id: str, session_id: str, k: int = 10) -> dict:
        with self.engine.begin() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT role, content, created_at
                    FROM events
                    WHERE strategy = 'conversation'
                      AND actor_id = :user_id
                      AND session_id = :session_id
                    ORDER BY created_at DESC
                    LIMIT :k
                    """
                ),
                {"user_id": user_id, "session_id": session_id, "k": k},
            ).mappings().all()
        # Return newest-first; callers can reverse if needed
        return {"ok": True, "items": [dict(r) for r in rows]}
