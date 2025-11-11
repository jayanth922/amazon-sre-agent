from state import GraphState
from tools.gateway_client import GatewayClient
import os

class KnowledgeAgent:
    name = "knowledge"

    def __init__(self):
        self.client = GatewayClient(os.environ["RUNBOOKS_MCP_URL"])

    async def run(self, st: GraphState) -> GraphState:
        res = await self.client.call_tool("runbooks.search", {"q": "high 5xx web-api"})
        st["notes"].append(f"knowledge: suggested runbook '{res.get('top','n/a')}'")
        st["need_runbook"] = False
        return st
