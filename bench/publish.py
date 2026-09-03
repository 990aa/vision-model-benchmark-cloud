import os
import shutil
from pathlib import Path
import psycopg2

run = os.environ["RUN_ID"]
pages = os.environ.get("PAGES_URL", "").rstrip("/")
count = 0
with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
    cur.execute("DELETE FROM artifacts WHERE run_id=%s", (run,))
    for vis in sorted(Path("out").glob("*/vis/*.jpg")):
        slug = vis.parent.parent.name
        dst = Path("site") / "runs" / run / slug
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy(vis, dst / vis.name)
        url = f"{pages}/runs/{run}/{slug}/{vis.name}"
        cur.execute("INSERT INTO artifacts(run_id, slug, kind, url) VALUES(%s,%s,'vis',%s)",
                    (run, slug, url))
        count += 1
print(f"published {count} images")
