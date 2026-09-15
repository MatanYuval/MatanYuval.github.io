#!/usr/bin/env python3
"""Apply a row -> class list (e.g. one produced from the contact sheets) to labels.json.

Input is a small CSV or JSON keyed by the row numbers stamped on the sheets:

    row,class,confidence,note
    37,orbicella_faveolata,0.8,
    38,acropora_palmata,1,broken branch

    python3 tools/apply_rows.py suggestions.csv                 # merge in
    python3 tools/apply_rows.py suggestions.csv --source ai     # mark provenance
    python3 tools/apply_rows.py suggestions.csv --overwrite      # replace human labels too

Anything written this way is flagged needsReview:true, so the classifier's
"Needs review" filter walks you through confirming it in the 3D viewer.
"""
import argparse, csv, datetime, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("infile")
    ap.add_argument("--source", default="ai")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    models = json.loads((ROOT / "data/models.json").read_text())["models"]
    by_row = {i: m for i, m in enumerate(models, 1)}
    taxa = json.loads((ROOT / "data/taxa.json").read_text())
    valid = {g["id"] for g in taxa["groups"]} | {s["id"] for g in taxa["groups"] for s in g["species"]}

    doc_path = ROOT / "data/labels.json"
    doc = json.loads(doc_path.read_text()) if doc_path.exists() else {"version": 1, "labels": {}}
    labels = doc["labels"]

    p = pathlib.Path(args.infile)
    rows = (json.loads(p.read_text()) if p.suffix == ".json"
            else list(csv.DictReader(p.open())))

    applied = skipped = 0
    for r in rows:
        row = int(r["row"])
        cls = (r.get("class") or "").strip()
        m = by_row.get(row)
        if not m or not cls:
            skipped += 1
            continue
        if cls not in valid:
            print(f"  ! row {row}: unknown class '{cls}' - add it to data/taxa.json first")
            skipped += 1
            continue
        key = str(m["id"])
        if not args.overwrite and labels.get(key, {}).get("source") == "human":
            skipped += 1
            continue
        labels[key] = {
            "class": cls,
            "confidence": float(r.get("confidence") or 0.6),
            "source": args.source,
            "note": (r.get("note") or "").strip(),
            "needsReview": True,
            "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        applied += 1

    doc["updatedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    doc_path.write_text(json.dumps(doc, indent=1))
    print(f"applied {applied}, skipped {skipped} -> {doc_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
