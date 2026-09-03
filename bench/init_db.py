import os
import psycopg2

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
  id TEXT PRIMARY KEY, status TEXT, started_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS stages(
  run_id TEXT, name TEXT, model TEXT DEFAULT '', state TEXT, note TEXT,
  updated_at TIMESTAMPTZ DEFAULT now(), PRIMARY KEY (run_id, name, model));
CREATE TABLE IF NOT EXISTS results(
  run_id TEXT, model TEXT, slug TEXT, task TEXT, score REAL, metric TEXT,
  latency_p50_ms REAL, latency_p95_ms REAL, PRIMARY KEY (run_id, model));
CREATE TABLE IF NOT EXISTS artifacts(
  run_id TEXT, slug TEXT, kind TEXT, url TEXT);
"""

if __name__ == "__main__":
    with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute(SCHEMA)
    print("DB schema ready")
