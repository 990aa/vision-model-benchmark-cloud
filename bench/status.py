import os, sys, psycopg2

STAGES = ["INIT","DATASET","EVAL","METRICS","ARTIFACTS","PUBLISH","NOTIFY"]

def upsert(run_id, name, model, state, note=""):
    with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute("""
          INSERT INTO stages(run_id,name,model,state,note,updated_at)
          VALUES(%s,%s,%s,%s,%s,now())
          ON CONFLICT (run_id,name,model)
          DO UPDATE SET state=EXCLUDED.state, note=EXCLUDED.note, updated_at=now()
        """, (run_id, name, model, state, note))

if __name__ == "__main__":
    upsert(os.environ["RUN_ID"], sys.argv[1], sys.argv[2] or "", sys.argv[3],
           " ".join(sys.argv[4:]))
