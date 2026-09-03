import gradio as gr, psycopg2, os

def fetch():
    with psycopg2.connect(os.environ["DATABASE_URL"]) as c, c.cursor() as cur:
        cur.execute("SELECT name,model,state FROM stages WHERE run_id=%s ORDER BY updated_at", (latest_run(),))
        stages = cur.fetchall()
        cur.execute("SELECT model,task,accuracy,latency_p50_ms,latency_p95_ms FROM results WHERE run_id=%s ORDER BY accuracy DESC", (latest_run(),))
        rows = cur.fetchall()
    return pipeline_html(stages), rows, gallery_html()

STEPPER_CSS = """
.step{display:inline-block;margin:0 14px;text-align:center}
.dot{width:26px;height:26px;border-radius:50%;margin:auto;background:#444}
.running .dot{background:#3b82f6;animation:pulse 1s infinite}
.done .dot{background:#22c55e}.failed .dot{background:#ef4444}
@keyframes pulse{50%{transform:scale(1.25);opacity:.6}}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=STEPPER_CSS) as demo:
    gr.Markdown("# Automated Vision Model Benchmark — Live Mission Control")
    with gr.Tab("Live Pipeline"):  pipe = gr.HTML()
    with gr.Tab("Leaderboard"):    board = gr.Dataframe()
    with gr.Tab("Visual Gallery"): gal = gr.HTML()
    timer = gr.Timer(5)                       # refresh every 5 s
    timer.tick(fetch, outputs=[pipe, board, gal])
demo.launch()
