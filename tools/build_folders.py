#!/usr/bin/env python3
"""Turn labels.json into a real folder per class inside the repo.

    python3 tools/build_folders.py            # writes classes/<class>/...
    python3 tools/build_folders.py --clean    # remove classes/ first

Each class folder gets:
    index.json   - the models in that class (name, ids, embed/thumb/glb urls)
    index.html   - a plain gallery page for that class, so the folder is a real
                   URL on the site: https://yourdomain/classes/acropora_palmata/
"""
import argparse, html, json, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "classes"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><link rel="stylesheet" href="../../assets/style.css"></head>
<body>
<header class="top"><h1>{title}</h1><span class="pill">{n} models</span>
<nav><a class="btn" href="../../index.html">Classify</a>
<a class="btn" href="../../browse.html">All classes</a></nav></header>
<div class="wrap"><div class="tiles">{tiles}</div></div>
</body></html>
"""

TILE = """<a class="tile" href="{embed}" target="_blank" rel="noopener">
<img loading="lazy" src="{thumb}" alt="{name}"><div class="cap">{name}</div></a>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()

    models = json.loads((ROOT / "data/models.json").read_text())["models"]
    labels = json.loads((ROOT / "data/labels.json").read_text())["labels"]
    taxa = json.loads((ROOT / "data/taxa.json").read_text())
    names = {}
    for g in taxa["groups"]:
        names[g["id"]] = g["label"]
        for s in g["species"]:
            names[s["id"]] = s["label"]

    if args.clean and OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(exist_ok=True)

    buckets: dict[str, list] = {}
    for m in models:
        cls = (labels.get(str(m["id"])) or {}).get("class") or "unlabelled"
        buckets.setdefault(cls, []).append(m)

    index = []
    for cls, items in sorted(buckets.items()):
        d = OUT / cls
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.json").write_text(json.dumps(
            {"class": cls, "label": names.get(cls, cls), "count": len(items), "models": items},
            indent=1))
        tiles = "\n".join(
            TILE.format(embed=html.escape(m["embed"]), thumb=html.escape(m["thumb"]),
                        name=html.escape(m["name"]))
            for m in items)
        (d / "index.html").write_text(PAGE.format(
            title=html.escape(names.get(cls, cls)), n=len(items), tiles=tiles))
        index.append({"class": cls, "label": names.get(cls, cls), "count": len(items)})
        print(f"{len(items):4d}  classes/{cls}/")

    (OUT / "index.json").write_text(json.dumps(
        {"classes": sorted(index, key=lambda c: -c["count"])}, indent=1))
    print(f"\n{len(index)} folders under {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
