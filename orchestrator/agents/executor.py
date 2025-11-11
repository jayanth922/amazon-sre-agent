from state import GraphState

class ExecutorAgent:
    name = "executor"

    async def run(self, st: GraphState) -> GraphState:
        st["notes"].append(f"executor: propose to {st.get('proposed_action')}")
        st["result"] = {"proposal": st.get("proposed_action"), "status": "needs-approval"}
        st["proposed_action"] = None
        return st
