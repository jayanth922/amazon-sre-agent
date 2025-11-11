from state import GraphState
from tools.gateway_client import GatewayClient
import os

class ObservabilityAgent:
    name = "observability"

    def __init__(self):
        self.client = GatewayClient(os.environ["METRICS_MCP_URL"])

    async def run(self, st: GraphState) -> GraphState:
        q = 'rate(http_requests_total{job="web"}[5m])'
        res = await self.client.call_tool("metrics.query_range", {
            "query": q, "start": "-10m", "end": "now", "step": "30s"
        })
        st["notes"].append(f"observability: got {len(res.get('values', []))} samples")
        st["proposed_action"] = "restart web-api"  # just to demonstrate flow
        st["need_metrics"] = False
        return st
