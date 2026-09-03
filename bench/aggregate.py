import json
import os
from pathlib import Path
import psycopg2

run = os.environ["RUN_ID"]
with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
    for f in Path("out").glob("*/results.json"):
        r = json.loads(f.read_text())
        cur.execute(
            """INSERT INTO results(run_id, model, slug, task, score, metric, latency_p50_ms, latency_p95_ms)
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (run_id, model)
               DO UPDATE SET score=EXCLUDED.score, latency_p50_ms=EXCLUDED.latency_p50_ms,
                             latency_p95_ms=EXCLUDED.latency_p95_ms""",
            (run, r["model"], r["slug"], r["task"], r["score"], r["metric"],
             r["latency_p50_ms"], r["latency_p95_ms"]))
        print(f'stored {r["model"]}: {r["score"]:.2%}')
