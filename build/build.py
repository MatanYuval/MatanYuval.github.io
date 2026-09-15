#!/usr/bin/env python3
"""Rebuild index.html from the template and the data files.

    python3 build/build.py

index.html is generated, not hand-written. Edit build/template.html instead, then
run this. The template is ordinary HTML with eight placeholders that get replaced
with JSON at build time:

    __MODELS__   data/models.json   -> the 616 models
    __TAXA__     data/taxa.json     -> the class list
    __LABELS__   labels.json        -> the labels themselves
    __META__     labels.json        -> everything in that file except the labels
    __COORDS__   data/coords.json   -> a location per model
    __GUIDE__    build/guide_data.json -> the field guide, both languages, plus the TOC
    __HERO__     build/hero_bits.json  -> the author's own hero paragraph and figure caption
    __BUILD__    generated          -> the stamp shown in the header

Editing index.html directly works too - it is one self-contained file - but the
next run of this script overwrites it, so put lasting changes in the template.
"""
import json, pathlib, datetime, sys

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Berlin")          # the stamp should match the author's clock
except Exception:
    TZ = None

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "build"


def main():
    tpl = (B / "template.html").read_text(encoding="utf-8")
    labels_doc = json.loads((ROOT / "labels.json").read_text())
    labels = labels_doc["labels"]
    meta = {k: v for k, v in labels_doc.items() if k not in ("labels", "counts", "updatedAt")}

    now = datetime.datetime.now(TZ) if TZ else datetime.datetime.now()
    stamp = now.strftime("%Y-%m-%d %H:%M %Z").strip()
    build = {"at": stamp,
             "human": sum(1 for v in labels.values() if v.get("source") == "human")}

    def compact(o):
        return json.dumps(o, separators=(",", ":"), ensure_ascii=False)

    out = (tpl
        .replace("__BUILD__", json.dumps(build))
        .replace("__META__", json.dumps(meta))
        .replace("__HERO__", json.dumps(json.load(open(B / "hero_bits.json"))))
        .replace("__GUIDE__", json.dumps(json.load(open(B / "guide_data.json"))))
        .replace("__MODELS__", compact(json.loads((ROOT / "data/models.json").read_text())["models"]))
        .replace("__COORDS__", compact(json.loads((ROOT / "data/coords.json").read_text())["coords"]))
        .replace("__TAXA__", compact(json.loads((ROOT / "data/taxa.json").read_text())))
        .replace("__LABELS__", compact(labels)))

    left = [t for t in ("__BUILD__", "__META__", "__HERO__", "__GUIDE__",
                        "__MODELS__", "__COORDS__", "__TAXA__", "__LABELS__") if t in out]
    if left:
        sys.exit("placeholders not filled: " + ", ".join(left))

    (ROOT / "index.html").write_text(out, encoding="utf-8")
    kb = len(out) // 1024
    print(f"index.html written - {kb} KB, build {stamp}")
    print(f"  {len(labels)} labels, {build['human']} confirmed by the author")


if __name__ == "__main__":
    main()
