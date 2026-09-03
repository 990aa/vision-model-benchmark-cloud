import json
import os
from pathlib import Path

run = os.environ["RUN_ID"]
pages = os.environ.get("PAGES_URL", "").rstrip("/")
cards = []
for m in sorted(Path("out").iterdir()) if Path("out").exists() else []:
    rj = m / "results.json"
    if not rj.exists():
        continue
    r = json.loads(rj.read_text())
    imgs = "".join(
        f'<a href="{pages}/runs/{run}/{r["slug"]}/{f.name}" target="_blank">'
        f'<img src="{pages}/runs/{run}/{r["slug"]}/{f.name}"></a>'
        for f in sorted((m / "vis").glob("*.jpg"))[:8])
    cards.append(f"""<section><h2>{r['model']}</h2>
      <p><b>Task:</b> {r['task']} · <b>{r['metric']}:</b> {r['score']:.1%} ·
      <b>Latency p50:</b> {r['latency_p50_ms']:.0f} ms · <b>p95:</b> {r['latency_p95_ms']:.0f} ms</p>
      <div>{imgs}</div></section>""")

html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Vision Benchmark Report — run {run}</title>
<style>body{{background:#0b1020;color:#e5e7eb;font-family:Segoe UI,Arial;margin:40px}}
img{{width:220px;border-radius:10px;margin:6px}}a{{display:inline-block}}
section{{background:#111833;border-radius:14px;padding:20px;margin:18px 0}}
h1{{color:#93c5fd}}h2{{color:#a5b4fc}}</style></head><body>
<h1>🔭 Automated Vision Model Benchmark — Run {run}</h1>
{''.join(cards) or '<p>No results.</p>'}
</body></html>"""

Path("site").mkdir(exist_ok=True)
(Path("site") / "index.html").write_text(html, encoding="utf-8")
print("site built")
