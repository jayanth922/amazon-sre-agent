import httpx, os, uuid

class GatewayClient:
    def __init__(self, base_url: str):
        self.url = base_url
        self.token = os.getenv("GATEWAY_TOKEN", "")

    async def _rpc(self, method: str, params=None):
        payload = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}
        if params is not None:
            payload["params"] = params
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(self.url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data["result"]

    async def list_tools(self):
        return await self._rpc("tools/list")

    async def call_tool(self, name: str, arguments: dict):
        return await self._rpc("tools/call", {"name": name, "arguments": arguments})
