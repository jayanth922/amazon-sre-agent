import os, time
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

TOKEN = os.getenv("GATEWAY_TOKEN", "")

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
          {"name":"metrics.query_range","input_schema":{"type":"object"}}
        ]}}
    if rpc.method == "tools/call":
        name = rpc.params["name"]
        args = rpc.params.get("arguments", {})
        if name == "metrics.query_range":
            # return fake time-series
            now = int(time.time())
            values = [[now-300+i*30, 0.1*i] for i in range(10)]
            return {"jsonrpc":"2.0","id":rpc.id,"result":{"values":values}}
        return {"jsonrpc":"2.0","id":rpc.id,"error":{"code":-32601,"message":"unknown tool"}}
    return {"jsonrpc":"2.0","id":rpc.id,"error":{"code":-32601,"message":"unknown method"}}
