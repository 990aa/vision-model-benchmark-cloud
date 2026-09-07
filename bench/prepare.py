import json
import os
from pathlib import Path
from PIL import Image
from datasets import load_dataset

N = 100
OUT = Path("data/sample")
OUT.mkdir(parents=True, exist_ok=True)

ds = load_dataset("microsoft/cats_vs_dogs", split="train", streaming=True)

names = ["cat", "dog"]
try:
    if hasattr(ds, "features"):
        if "labels" in ds.features and hasattr(ds.features["labels"], "names"):
            names = ds.features["labels"].names
        elif "label" in ds.features and hasattr(ds.features["label"], "names"):
            names = ds.features["label"].names
except Exception:
    names = ["cat", "dog"]

labels = {}
for i, ex in enumerate(ds):
    if i >= N:
        break
    img = ex["image"].convert("RGB")
    img.thumbnail((448, 448))
    fname = f"img_{i:03d}.jpg"
    img.save(OUT / fname, quality=88)

    raw_label = ex.get("labels", ex.get("label", 0))
    if isinstance(raw_label, int) and raw_label < len(names):
        labels[fname] = names[raw_label]
    else:
        labels[fname] = str(raw_label)

(OUT / "labels.json").write_text(json.dumps(labels))
print(f"prepared {len(labels)} images")

# Immediately terminate process and release background streaming threads
os._exit(0)
