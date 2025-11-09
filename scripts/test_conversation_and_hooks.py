from sqlalchemy import text
from sre_agent.memory_oss.client_postgres import SREMemoryClient
from sre_agent.memory_oss.conversation import create_conversation_memory_manager
from sre_agent.memory_oss.hooks import MemoryHookProvider

USER = "alice@acme"
SESSION = "sess-001"

c = SREMemoryClient()

# 1) Save a small conversation batch
save_batch = create_conversation_memory_manager(c)
print("saving conversation batch...")
print(save_batch(
    user_id=USER,
    session_id=SESSION,
    messages=[
        {"role": "user", "content": "checkout pods are crashlooping"},
        {"role": "assistant", "content": "checking k8s status"},
        {"role": "tool", "content": {"tool": "k8s.get_pod_status", "result": "CrashLoopBackOff on checkout-v2"}},
    ],
))

# 2) Simulate an agent response with infra knowledge + preferences
hook = MemoryHookProvider(c)
print("hook writing infra/prefs...")
print(hook.on_agent_response(
    agent_name="kubernetes-agent",
    response_obj={
        "infrastructure_knowledge": [
            {"service": "checkout", "pattern": "CrashLoopBackOff when memory < 256Mi"},
        ],
        "preferences": {"report_style": "concise", "escalate_channel": "#oncall-sre"},
    },
    user_id=USER,
    session_id=SESSION,
))

# 3) Read back counts to verify
with c.engine.begin() as conn:
    n_conv = conn.execute(text(
        "select count(*) from events where strategy='conversation' and actor_id=:u and session_id=:s"
    ), {"u": USER, "s": SESSION}).scalar_one()
    n_prefs = conn.execute(text(
        "select count(*) from events where strategy='preference' and actor_id=:u"
    ), {"u": USER}).scalar_one()
    n_infra = conn.execute(text(
        "select count(*) from events where strategy='infrastructure' and session_id=:s"
    ), {"s": SESSION}).scalar_one()
print({"conversation": n_conv, "preferences": n_prefs, "infrastructure": n_infra})
