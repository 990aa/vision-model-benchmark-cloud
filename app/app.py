import os
import gradio as gr
import psycopg2

STAGES = ["INIT", "DATASET", "EVAL", "METRICS", "ARTIFACTS", "PUBLISH", "NOTIFY"]
CSS = """
.pipe{display:flex;flex-wrap:wrap;gap:8px;align-items:stretch}
.step{background:#1e293b;border-radius:12px;padding:10px 14px;min-width:120px;text-align:center}
.step .dot{width:14px;height:14px;border-radius:50%;background:#475569;margin:0 auto 6px}
.step.running .dot{background:#38bdf8;animation:p 1s infinite}
.step.done .dot{background:#22c55e}
.step.failed .dot{background:#ef4444}
@keyframes p{50%{opacity:.4;transform:scale(1.3)}}
.sub{font-size:.75em;color:#94a3b8}
img{width:210px;border-radius:10px;margin:5px}
"""

def q(sql, args=()):
    with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchall()

def latest():
    r = q("SELECT id FROM runs ORDER BY started_at DESC LIMIT 1")
    return str(r[0][0]) if r else None

def pipeline_html(rid):
    if not rid:
        return "<p>No runs yet. Trigger the workflow in GitHub Actions.</p>"
    rows = q("SELECT name, model, state, note FROM stages WHERE run_id=%s", (rid,))
    by = {}
    for name, model, state, note in rows:
        by.setdefault(name, []).append((model, state, note or ""))
    h = ['<div class="pipe">']
    for s in STAGES:
        items = by.get(s, [])
        if s == "EVAL" and items:
            dots = "".join(f'<span class="sub">{m}: {st}</span><br>' for m, st, _ in items)
            state = ("done" if all(st == "done" for _, st, _ in items)
                     else "failed" if any(st == "failed" for _, st, _ in items)
                     else "running")
            h.append(f'<div class="step {state}"><div class="dot"></div><b>EVAL</b><br>{dots}</div>')
        else:
            st = items[0][1] if items else "pending"
            note = items[0][2] if items else ""
            h.append(f'<div class="step {st}"><div class="dot"></div><b>{s}</b><div class="sub">{note}</div></div>')
    h.append("</div>")
    return "".join(h)

def board(rid):
    if not rid:
        return []
    return [[m, t, f"{s:.1%}", f"{p50:.0f}", f"{p95:.0f}"]
            for m, t, s, p50, p95 in q(
                "SELECT model, task, score, latency_p50_ms, latency_p95_ms "
                "FROM results WHERE run_id=%s ORDER BY score DESC", (rid,))]

def gallery(rid):
    if not rid:
        return ""
    urls = [u for (u,) in q("SELECT url FROM artifacts WHERE run_id=%s LIMIT 24", (rid,))]
    return "".join(f'<img src="{u}">' for u in urls) or "<p>No images yet.</p>"

def refresh():
    rid = latest()
    head = f"**Latest run:** `{rid}`" if rid else "No runs yet."
    return head, pipeline_html(rid), board(rid), gallery(rid)

with gr.Blocks(theme=gr.themes.Soft(), css=CSS, title="Vision Benchmark Mission Control") as demo:
    gr.Markdown("## 🔭 Automated Vision Model Benchmark — Live Mission Control")
    run_md = gr.Markdown()
    with gr.Tabs():
        with gr.TabItem("🛰️ Live Pipeline"):
            pipe = gr.HTML()
        with gr.TabItem("🏆 Leaderboard"):
            tbl = gr.Dataframe(headers=["model", "task", "score", "p50 ms", "p95 ms"])
        with gr.TabItem("🖼️ Visual Gallery"):
            gal = gr.HTML()
    demo.load(refresh, None, [run_md, pipe, tbl, gal], every=5)

demo.queue().launch()
