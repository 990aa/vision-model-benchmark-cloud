import os
import sys
import psycopg2

def _conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def start_run(run_id):
    with _conn() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO runs(id, status) VALUES(%s,'running') "
            "ON CONFLICT (id) DO UPDATE SET status='running'", (run_id,))

def stage(run_id, name, model, state, note=""):
    with _conn() as c, c.cursor() as cur:
        cur.execute(
            """INSERT INTO stages(run_id, name, model, state, note, updated_at)
               VALUES(%s,%s,%s,%s,%s,now())
               ON CONFLICT (run_id, name, model)
               DO UPDATE SET state=EXCLUDED.state, note=EXCLUDED.note, updated_at=now()""",
            (run_id, name, model or "", state, note))

if __name__ == "__main__":
    run_id = os.environ["RUN_ID"]
    cmd = sys.argv[1]
    if cmd == "start":
        start_run(run_id)
    elif cmd == "stage":
        stage(run_id, sys.argv[2], sys.argv[3], sys.argv[4], " ".join(sys.argv[5:]))
    print("status ok:", " ".join(sys.argv[1:]))
