from sre_agent.memory_oss.client_postgres import SREMemoryClient
from sre_agent.memory_oss.tools import create_memory_tools

c = SREMemoryClient()
tools = create_memory_tools(c)

# 1) save_preference
print("save_preference...")
resp1 = [t for t in tools if t.name == "save_preference"][0].invoke({"user_id":"alice@acme","content":{"timezone":"PST","style":"concise"}})
print(resp1)

# 2) retrieve_memory (preferences)
print("retrieve_memory...")
resp2 = [t for t in tools if t.name == "retrieve_memory"][0].invoke({
    "memory_type":"preference",
    "actor_id":"alice@acme",
    "query":"concise style",
    "max_results":5
})
print(resp2)

# 3) save_infrastructure and fetch
print("save_infrastructure...")
[t for t in tools if t.name == "save_infrastructure"][0].invoke({
    "agent_name":"kubernetes-agent",
    "user_id":"alice@acme",
    "session_id":"sess-002",
    "content":{"service":"checkout","pattern":"CrashLoop when mem < 256Mi"}
})
print("retrieve infra...")
resp3 = [t for t in tools if t.name == "retrieve_memory"][0].invoke({
    "memory_type":"infrastructure",
    "actor_id":"kubernetes-agent",
    "query":"CrashLoop",
    "max_results":5
})
print(resp3)
