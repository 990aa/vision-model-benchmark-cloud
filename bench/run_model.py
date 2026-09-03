import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import status

RUN_ID = os.environ["RUN_ID"]
CAT_IDX = set(range(281, 286))          # ImageNet cat classes
DOG_IDX = set(range(151, 269))          # ImageNet dog classes

def samples():
    d = Path("data/sample")
    labels = json.loads((d / "labels.json").read_text())
    return [(d / f, labels[f]) for f in sorted(labels)]

def pct(x, p):
    return float(np.percentile(x, p)) if x else 0.0

def heatmap(model, proc, img, outpath):
    """Grad-CAM heatmap; falls back to plain image if anything fails."""
    try:
        from pytorch_grad_cam import XGradCAM
        from pytorch_grad_cam.utils.image import show_cam_on_image
        if hasattr(model, "resnet"):
            layer, rt = model.resnet.encoder.stages[-1], None
        elif hasattr(model, "vit"):
            def rt(t):
                b, n, d = t.shape
                h = w = int((n - 1) ** 0.5)
                return t[:, 1:, :].reshape(b, h, w, d).permute(0, 3, 1, 2)
            layer = model.vit.encoder.layer[-1]
        else:
            raise RuntimeError("unknown architecture for Grad-CAM")
        cam = XGradCAM(model=model, target_layers=[layer], reshape_transform=rt)
        tensor = proc(images=img, return_tensors="pt")["pixel_values"]
        g = cam(input_tensor=tensor)[0]
        rgb = np.array(img.resize((g.shape[1], g.shape[0]))) / 255
        Image.fromarray(show_cam_on_image(rgb, g, use_rgb=True)).save(outpath)
        return True
    except Exception as e:
        print("heatmap skipped:", e)
        img.save(outpath)
        return False

def draw_boxes(img, preds, outpath):
    d = ImageDraw.Draw(img)
    for p in preds:
        b = p["box"]
        d.rectangle([b["xmin"], b["ymin"], b["xmax"], b["ymax"]], outline=(0, 255, 0), width=3)
        d.text((b["xmin"], max(0, b["ymin"] - 14)), f'{p["label"]} {p["score"]:.2f}', fill=(0, 255, 0))
    img.save(outpath, quality=88)

def run_classification(model_id, slug):
    import torch
    from transformers import AutoImageProcessor, AutoModelForImageClassification
    proc = AutoImageProcessor.from_pretrained(model_id)
    model = AutoModelForImageClassification.from_pretrained(model_id)
    model.eval()
    correct, lats = 0, []
    vis = Path("out") / slug / "vis"
    vis.mkdir(parents=True, exist_ok=True)
    for i, (p, gt) in enumerate(samples()):
        img = Image.open(p).convert("RGB")
        inputs = proc(images=img, return_tensors="pt")
        t0 = time.perf_counter()
        with torch.no_grad():
            top = torch.topk(model(**inputs).logits, 5).indices[0].tolist()
        lats.append((time.perf_counter() - t0) * 1000)
        pred = next(("cat" if t in CAT_IDX else "dog"
                     for t in top if t in (CAT_IDX | DOG_IDX)), "unknown")
        correct += pred == gt
        if i < 6:
            heatmap(model, proc, img, vis / f"{p.stem}_cam.jpg")
    return {"score": correct / len(lats), "metric": "top-1 accuracy", "lats": lats, "vis": vis}

def run_detection(model_id, slug):
    from transformers import pipeline as tf_pipeline
    det = tf_pipeline("object-detection", model=model_id, threshold=0.4, device=-1)
    hits, boxes, lats = 0, 0, []
    vis = Path("out") / slug / "vis"
    vis.mkdir(parents=True, exist_ok=True)
    for i, (p, gt) in enumerate(samples()):
        img = Image.open(p).convert("RGB")
        t0 = time.perf_counter()
        preds = det(img)
        lats.append((time.perf_counter() - t0) * 1000)
        hits += any(x["label"] in ("cat", "dog") for x in preds)
        boxes += len(preds)
        if i < 8:
            draw_boxes(img, preds, vis / f"{p.stem}_det.jpg")
    return {"score": hits / len(lats), "metric": "subject hit rate", "lats": lats, "vis": vis,
            "extra": {"boxes_per_image": boxes / len(lats)}}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--task", required=True)     # image-classification | object-detection
    ap.add_argument("--slug", required=True)
    a = ap.parse_args()

    status.stage(RUN_ID, "EVAL", a.slug, "running", a.model)
    out = run_classification(a.model, a.slug) if a.task == "image-classification" \
          else run_detection(a.model, a.slug)

    res = {"model": a.model, "slug": a.slug, "task": a.task,
           "score": out["score"], "metric": out["metric"],
           "latency_p50_ms": pct(out["lats"], 50), "latency_p95_ms": pct(out["lats"], 95)}
    res.update(out.get("extra", {}))
    (Path("out") / a.slug / "results.json").write_text(json.dumps(res, indent=2))
    status.stage(RUN_ID, "EVAL", a.slug, "done", f'{a.model} score={res["score"]:.1%}')
    print(json.dumps(res, indent=2))
