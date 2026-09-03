import json
from pathlib import Path
from PIL import Image
from datasets import load_dataset

N = 100
OUT = Path("data/sample")
OUT.mkdir(parents=True, exist_ok=True)

ds = load_dataset("microsoft/cats_vs_dogs", split="train", streaming=True)
try:
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
    labels[fname] = names[ex["label"]]

(OUT / "labels.json").write_text(json.dumps(labels))
print(f"prepared {len(labels)} images")
