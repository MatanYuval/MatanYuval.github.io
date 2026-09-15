#!/usr/bin/env python3
"""Turn a row,class CSV (the one Claude sends back) into labels.json.

Put this next to index.html with the CSV, then:

    python3 apply_labels.py suggestions.csv

Writes labels.json beside index.html. Commit both and the live site shows the
classifications; every label written this way is flagged needsReview, so the
"Needs review" filter in the page walks you through confirming them in 3D.
"""
import csv, datetime, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 apply_labels.py suggestions.csv")
    page = (HERE / "index.html").read_text(encoding="utf-8")
    models = json.loads(re.search(r"const MODELS = (\[.*?\]);\n", page, re.S).group(1))
    taxa = json.loads(re.search(r"const TAXA = (\{.*?\});\n", page, re.S).group(1))
    valid = {g["id"] for g in taxa["groups"]} | {s["id"] for g in taxa["groups"] for s in g["species"]}
    by_row = {i: m for i, m in enumerate(models, 1)}

    out = HERE / "labels.json"
    doc = json.loads(out.read_text()) if out.exists() else {"version": 1, "labels": {}}
    labels = doc["labels"]

    applied = skipped = 0
    for r in csv.DictReader(pathlib.Path(sys.argv[1]).open(encoding="utf-8-sig")):
        row, cls = int(r["row"]), (r.get("class") or "").strip()
        if not cls or row not in by_row:
            skipped += 1
            continue
        if cls not in valid:
            print(f"  ! row {row}: '{cls}' is not in the class list - skipped")
            skipped += 1
            continue
        labels[str(by_row[row]["id"])] = {
            "class": cls,
            "confidence": float(r.get("confidence") or 0.6),
            "source": "ai",
            "note": (r.get("note") or "").strip(),
            "needsReview": True,
            "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        applied += 1

    doc["updatedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    out.write_text(json.dumps(doc, indent=1))
    print(f"applied {applied}, skipped {skipped} → {out}")


if __name__ == "__main__":
    main()
