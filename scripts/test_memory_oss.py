from sre_agent.memory_oss.client_postgres import SREMemoryClient

c = SREMemoryClient()

# 1) Write a preference
print("create preference...")
print(
    c.create_event(
        strategy="preference",
        namespace="/sre/users/alice@acme/preferences",
        actor_id="alice@acme",
        content={"summary": "Escalate to #oncall-sre. Prefer concise answers."},
    )
)

# 2) Search it semantically
print("retrieve...")
print(
    c.retrieve_memories(
        memory_type="preference",
        actor_id="alice@acme",
        query="how to escalate and style of answers",
        max_results=5,
    )
)
