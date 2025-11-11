import os, json, psycopg
from typing import Any

DSN = os.getenv("POSTGRES_DSN")

def save_state(incident_id: str, state: dict):
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute("""
          CREATE TABLE IF NOT EXISTS agent_sessions(
            incident_id text primary key,
            state jsonb not null,
            updated_at timestamptz default now()
          )""")
        cur.execute("""
          INSERT INTO agent_sessions(incident_id, state)
          VALUES (%s, %s)
          ON CONFLICT (incident_id) DO UPDATE SET state=EXCLUDED.state, updated_at=now()
        """, (incident_id, json.dumps(state)))
        conn.commit()

def load_state(incident_id: str) -> dict | None:
    with psycopg.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute("SELECT state FROM agent_sessions WHERE incident_id=%s", (incident_id,))
        row = cur.fetchone()
        return row[0] if row else None
