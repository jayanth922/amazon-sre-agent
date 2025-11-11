import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

TOKEN = os.getenv("GATEWAY_TOKEN","")
RUNBOOKS = [
  {"title":"High 5xx in web-api", "steps":["check pods","check error rate","roll restart web-api"]},
  {"title":"Pod CrashLoopBackOff", "steps":["describe pod","inspect logs","rollback"]}
]

app = FastAPI()

class RPC(BaseModel):
    jsonrpc: str
    id: str | int
    method: str
    params: dict | None = None

def _auth(auth: str | None):
    if TOKEN and (not auth or auth != f"Bearer {TOKEN}"):
        raise HTTPException(401, "unauthorized")

@app.post("/mcp")
def mcp(rpc: RPC, authorization: str | None = Header(None)):
    _auth(authorization)
    if rpc.method == "tools/list":
        return {"jsonrpc":"2.0","id":rpc.id,"result":{"tools":[
          {"name":"runbooks.search","input_schema":{"type":"object","properties":{"q":{"type":"string"}}}}
        ]}}
    if rpc.method == "tools/call":
        if rpc.params["name"] == "runbooks.search":
            q = rpc.params.get("arguments",{}).get("q","").lower()
            hits = [rb for rb in RUNBOOKS if q in rb["title"].lower()]
            top = hits[0]["title"] if hits else None
            return {"jsonrpc":"2.0","id":rpc.id,"result":{"top": top, "hits": hits}}
    return {"jsonrpc":"2.0","id":rpc.id,"error":{"code":-32601,"message":"unknown method"}}
