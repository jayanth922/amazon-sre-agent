-- extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS vector;

-- events table
CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  strategy TEXT NOT NULL CHECK (strategy IN ('preference','infrastructure','investigation','conversation')),
  namespace TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  session_id TEXT,
  role TEXT,
  content JSONB NOT NULL,
  embedding VECTOR(768),
  ttl_expires_at TIMESTAMPTZ,
  metadata JSONB
);

-- indexes
CREATE INDEX IF NOT EXISTS idx_events_strategy_actor ON events(strategy, actor_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_namespace ON events(namespace);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id, created_at);

-- ANN index for cosine
CREATE INDEX IF NOT EXISTS idx_events_embedding_ivfflat
  ON events USING ivfflat (embedding vector_cosine_ops);
