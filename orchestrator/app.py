#orchestrator/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from graph import build_graph
from memory.pg_store import save_state, load_state

api = FastAPI(title="SRE Orchestrator (OSS)")
app = build_graph()

class Alert(BaseModel):
    service: str
    message: str
    labels: dict = {}

@api.post("/incidents/ingest")
async def ingest(alert: Alert):
    st = {"alert": alert.model_dump()}
    out = await app.ainvoke(st)
    save_state(out["incident_id"], out)
    return out

@api.get("/incidents/{incident_id}")
async def fetch(incident_id: str):
    return load_state(incident_id) or {"error": "not found"}
