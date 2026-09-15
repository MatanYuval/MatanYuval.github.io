#!/usr/bin/env python3
"""Download the Kiri thumbnails and tile them into numbered contact sheets.

Why: a contact sheet lets a human (or Claude) pre-sort hundreds of models in a
few passes instead of opening them one at a time. Each tile is stamped with the
model's row number, and sheets/index.csv maps row number -> model id + name, so
any list of "row 37 = Orbicella faveolata" can be turned back into labels.json.

    pip install pillow requests
    python3 tools/make_contact_sheets.py                 # 20 per sheet
    python3 tools/make_contact_sheets.py --per-sheet 12 --cols 4

Output:
    sheets/thumbs/<id>.jpg
    sheets/sheet_001.jpg …
    sheets/index.csv          row,id,name,class_so_far
"""
import argparse, csv, json, pathlib, sys

try:
    import requests
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Install dependencies first:  pip install pillow requests")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "sheets"
THUMBS = OUT / "thumbs"


def fetch(models):
    THUMBS.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    for i, m in enumerate(models, 1):
        p = THUMBS / f"{m['id']}.jpg"
        if p.exists() and p.stat().st_size > 0:
            continue
        try:
            r = s.get(m["thumb"], timeout=30)
            r.raise_for_status()
            p.write_bytes(r.content)
        except Exception as e:  # keep going; a missing thumb becomes a grey tile
            print(f"  ! {m['name']}: {e}")
        if i % 25 == 0:
            print(f"  …{i}/{len(models)}")


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "C:/Windows/Fonts/arialbd.ttf"):
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def build(models, per_sheet, cols, cell):
    f_big, f_small = font(int(cell * 0.11)), font(int(cell * 0.075))
    pad, cap = 8, int(cell * 0.16)
    for start in range(0, len(models), per_sheet):
        chunk = models[start:start + per_sheet]
        rows = (len(chunk) + cols - 1) // cols
        W = cols * (cell + pad) + pad
        H = rows * (cell + cap + pad) + pad
        sheet = Image.new("RGB", (W, H), (245, 245, 243))
        d = ImageDraw.Draw(sheet)
        for i, m in enumerate(chunk):
            x = pad + (i % cols) * (cell + pad)
            y = pad + (i // cols) * (cell + cap + pad)
            p = THUMBS / f"{m['id']}.jpg"
            try:
                im = Image.open(p).convert("RGB")
                im.thumbnail((cell, cell))
                sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
            except Exception:
                d.rectangle([x, y, x + cell, y + cell], fill=(210, 210, 208))
            d.rectangle([x, y, x + cell, y + cell], outline=(180, 180, 178))
            n = str(m["row"])
            d.rectangle([x, y, x + int(cell * 0.28), y + int(cell * 0.18)], fill=(15, 109, 99))
            d.text((x + 6, y + 4), n, fill=(255, 255, 255), font=f_big)
            d.text((x, y + cell + 3), m["name"][:28], fill=(40, 50, 48), font=f_small)
        n = start // per_sheet + 1
        out = OUT / f"sheet_{n:03d}.jpg"
        sheet.save(out, quality=88)
        print(f"  {out.name}  rows {chunk[0]['row']}–{chunk[-1]['row']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-sheet", type=int, default=20)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--cell", type=int, default=340)
    ap.add_argument("--only-unlabelled", action="store_true")
    args = ap.parse_args()

    models = json.loads((ROOT / "data/models.json").read_text())["models"]
    labels = json.loads((ROOT / "data/labels.json").read_text())["labels"]
    for i, m in enumerate(models, 1):
        m["row"] = i
        m["cls"] = (labels.get(str(m["id"])) or {}).get("class", "")
    todo = [m for m in models if not m["cls"]] if args.only_unlabelled else models

    OUT.mkdir(exist_ok=True)
    print(f"Fetching {len(todo)} thumbnails…")
    fetch(todo)
    print("Building sheets…")
    build(todo, args.per_sheet, args.cols, args.cell)

    with (OUT / "index.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["row", "id", "name", "class_so_far"])
        for m in models:
            w.writerow([m["row"], m["id"], m["name"], m["cls"]])
    print(f"\nDone: {OUT}")


if __name__ == "__main__":
    main()
