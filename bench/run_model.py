import time, json, numpy as np
from transformers import pipeline
from PIL import Image, ImageDraw

def draw_boxes(img, boxes, labels, out):
    d = ImageDraw.Draw(img)
    for b, l in zip(boxes, labels):
        d.rectangle(b, outline=(0,255,0), width=3)
        d.text((b[0], max(0, b[1]-14)), l, fill=(0,255,0))
    img.save(out, quality=85)

def benchmark(model_id, task, images, gt):
    pipe = pipeline(task, model=model_id)   # downloaded ONCE, in the cloud runner
    lats = []
    for img, path in images:
        t0 = time.perf_counter()
        out = pipe(img)
        lats.append((time.perf_counter()-t0)*1000)
        if task == "object_detection":
            draw_boxes(img, [o["box"] for o in out],
                       [o["label"] for o in out], f"vis/{model_id.split('/')[-1]}_{path.stem}.jpg")
    # accuracy: mAP@50 for detection (IoU match), top-1 for classification
    return {"latency_p50_ms": float(np.percentile(lats,50)),
            "latency_p95_ms": float(np.percentile(lats,95)), ...}
