#!/usr/bin/env python3
"""Download the Kiri thumbnails and tile them into numbered contact sheets.

Put this next to index.html and run:

    pip install pillow requests
    python3 make_sheets.py

It reads the model list straight out of index.html, so there is nothing else to
configure. You get:

    sheets/sheet_001.jpg …   20 models per sheet, each stamped with a row number
    sheets/index.csv          row -> model id + name

Upload the sheets to Claude and you get back a row,class CSV; apply_labels.py
turns that into labels.json.

Options:
    --per-sheet 20   models per sheet
    --cols 5         tiles per row
    --limit 100      only the first N models (good for a trial run)
"""
import argparse, csv, json, pathlib, re, sys

try:
    import requests
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Install the two dependencies first:  pip install pillow requests")

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "sheets"
THUMBS = OUT / "thumbs"


def load_models():
    page = HERE / "index.html"
    if not page.exists():
        sys.exit("index.html not found - put this script in the same folder as index.html")
    m = re.search(r"const MODELS = (\[.*?\]);\n", page.read_text(encoding="utf-8"), re.S)
    if not m:
        sys.exit("Could not find the model list inside index.html")
    models = json.loads(m.group(1))
    for i, mod in enumerate(models, 1):
        mod["row"] = i
    return models


def fetch(models):
    THUMBS.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    missing = [m for m in models if not (THUMBS / f"{m['id']}.jpg").exists()]
    print(f"Downloading {len(missing)} thumbnails ({len(models) - len(missing)} already here)…")
    for i, m in enumerate(missing, 1):
        try:
            r = s.get(m["thumb"], timeout=30)
            r.raise_for_status()
            (THUMBS / f"{m['id']}.jpg").write_bytes(r.content)
        except Exception as e:
            print(f"  ! row {m['row']} {m['name']}: {e}")
        if i % 25 == 0:
            print(f"  …{i}/{len(missing)}")


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/Library/Fonts/Arial Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf"):
        if pathlib.Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def build(models, per_sheet, cols, cell):
    big, small = font(int(cell * .12)), font(int(cell * .075))
    pad, cap = 8, int(cell * .16)
    for start in range(0, len(models), per_sheet):
        chunk = models[start:start + per_sheet]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (cell + pad) + pad, rows * (cell + cap + pad) + pad), (245, 245, 243))
        d = ImageDraw.Draw(sheet)
        for i, m in enumerate(chunk):
            x = pad + (i % cols) * (cell + pad)
            y = pad + (i // cols) * (cell + cap + pad)
            try:
                im = Image.open(THUMBS / f"{m['id']}.jpg").convert("RGB")
                im.thumbnail((cell, cell))
                sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
            except Exception:
                d.rectangle([x, y, x + cell, y + cell], fill=(212, 212, 210))
            d.rectangle([x, y, x + cell, y + cell], outline=(178, 178, 176))
            d.rectangle([x, y, x + int(cell * .30), y + int(cell * .19)], fill=(15, 109, 99))
            d.text((x + 7, y + 4), str(m["row"]), fill=(255, 255, 255), font=big)
            d.text((x, y + cell + 3), m["name"][:28], fill=(40, 50, 48), font=small)
        n = start // per_sheet + 1
        sheet.save(OUT / f"sheet_{n:03d}.jpg", quality=87)
        print(f"  sheet_{n:03d}.jpg  rows {chunk[0]['row']}–{chunk[-1]['row']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-sheet", type=int, default=20)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--cell", type=int, default=340)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()

    models = load_models()
    todo = models[:a.limit] if a.limit else models
    OUT.mkdir(exist_ok=True)
    fetch(todo)
    print("Building sheets…")
    build(todo, a.per_sheet, a.cols, a.cell)
    with (OUT / "index.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["row", "id", "name"])
        for m in models:
            w.writerow([m["row"], m["id"], m["name"]])
    print(f"\nDone → {OUT}")


if __name__ == "__main__":
    main()
