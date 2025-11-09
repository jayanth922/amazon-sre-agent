from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from .client_postgres import SREMemoryClient

# ---------- Pydantic arg models ----------

class RetrieveArgs(BaseModel):
    memory_type: Literal["preference", "infrastructure", "investigation"] = Field(
        ..., description="Which memory bucket to search"
    )
    actor_id: Optional[str] = Field(
        None, description="User id for preferences/investigations; agent id for infrastructure"
    )
    query: str = Field("*", description="Free-text query for semantic/keyword search")
    max_results: int = Field(20, ge=1, le=100)
    session_id: Optional[str] = Field(None, description="Current session for scoping")
    namespace_prefix: Optional[str] = Field(
        None, description="Optional namespace prefix filter like /sre/users/{user}/preferences"
    )

class SavePreferenceArgs(BaseModel):
    user_id: str
    content: dict = Field(..., description="JSON blob of user preferences")

class SaveInfrastructureArgs(BaseModel):
    agent_name: str = Field(..., description="e.g., kubernetes-agent")
    user_id: str
    session_id: str
    content: dict = Field(..., description="JSON blob of infrastructure knowledge")

class SaveInvestigationArgs(BaseModel):
    user_id: str
    session_id: str
    summary: dict = Field(..., description="Investigation summary: findings/timeline/actions")

# ---------- Tool builders ----------

def create_memory_tools(client: SREMemoryClient):
    """
    Returns a list of StructuredTool objects the Supervisor can pass to its planning agent.
    Names match the original sample's intent.
    """

    def _retrieve(
        memory_type: str,
        actor_id: str | None = None,
        query: str = "*",
        max_results: int = 20,
        session_id: str | None = None,
        namespace_prefix: str | None = None,
    ):
        return client.retrieve_memories(
            memory_type=memory_type,
            actor_id=actor_id,
            query=query,
            max_results=max_results,
            session_id=session_id,
            namespace_prefix=namespace_prefix,
        )

    def _save_preference(user_id: str, content: dict):
        return client.create_event(
            strategy="preference",
            namespace=f"/sre/users/{user_id}/preferences",
            actor_id=user_id,
            content=content,
        )

    def _save_infrastructure(agent_name: str, user_id: str, session_id: str, content: dict):
        return client.create_event(
            strategy="infrastructure",
            namespace=f"/sre/infrastructure/{agent_name}/{user_id}",
            actor_id=agent_name,
            session_id=session_id,
            content=content,
        )

    def _save_investigation(user_id: str, session_id: str, summary: dict):
        return client.save_investigation_summary(user_id=user_id, session_id=session_id, summary=summary)

    retrieve_tool = StructuredTool.from_function(
        name="retrieve_memory",
        description=(
            "Retrieve long-term memory for planning. "
            "Use memory_type='preference' for user prefs, 'infrastructure' for infra knowledge, "
            "or 'investigation' for past summaries. Returns a list of items with content."
        ),
        func=_retrieve,
        args_schema=RetrieveArgs,
    )

    save_pref_tool = StructuredTool.from_function(
        name="save_preference",
        description="Persist user preferences (report style, escalation destinations, etc.)",
        func=_save_preference,
        args_schema=SavePreferenceArgs,
    )

    save_infra_tool = StructuredTool.from_function(
        name="save_infrastructure",
        description="Persist infrastructure knowledge extracted from agent runs (patterns, baselines).",
        func=_save_infrastructure,
        args_schema=SaveInfrastructureArgs,
    )

    save_inv_tool = StructuredTool.from_function(
        name="save_investigation",
        description="Persist an investigation summary (timeline/findings/actions).",
        func=_save_investigation,
        args_schema=SaveInvestigationArgs,
    )

    # return as a list; Supervisor typically passes these to its planning agent
    return [retrieve_tool, save_pref_tool, save_infra_tool, save_inv_tool]


def update_memory_tools_user_id(tools, user_id: str):
    """
    Backwards-compatible no-op: the OSS tools accept user_id as an argument,
    so we don't need to rebind anything here. We keep this symbol so older
    supervisor code that expects it continues to run.
    """
    return tools
