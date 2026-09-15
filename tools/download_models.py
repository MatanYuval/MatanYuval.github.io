#!/usr/bin/env python3
"""Download every Kiri .glb listed in index.html.

    python3 download_models.py --check      # just report how much it will be
    python3 download_models.py              # download into models/
    python3 download_models.py --class colpophyllia_natans   # only one class

Safe to re-run: files already on disk are skipped, so an interrupted run resumes.
Filenames carry the class, so the folder is self-describing:

    models/colpophyllia_natans/Project_066__<kiri-id>.glb
"""
import argparse, json, pathlib, re, sys, time

try:
    import requests
except ImportError:
    sys.exit("pip install requests")

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "models"


def load():
    page = HERE / "index.html"
    if not page.exists():
        sys.exit("put this next to index.html")
    txt = page.read_text(encoding="utf-8")

    def grab(decl):
        """Pull one JSON literal out of the page by walking its brackets.
        A regex is not enough here: a trailing // comment sits on some lines."""
        i = txt.index(decl) + len(decl)
        while txt[i] in " =":
            i += 1
        open_ch = txt[i]
        close_ch = {"[": "]", "{": "}"}[open_ch]
        depth, j, instr, esc = 0, i, False, False
        while j < len(txt):
            c = txt[j]
            if instr:
                if esc: esc = False
                elif c == "\\": esc = True
                elif c == '"': instr = False
            elif c == '"': instr = True
            elif c == open_ch: depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0:
                    return json.loads(txt[i:j + 1])
            j += 1
        raise ValueError("could not find the end of " + decl)

    models = grab("const MODELS")
    taxa = grab("const TAXA")
    labels = grab("let BASE")
    # a labels.json next to the page wins, same rule the site uses
    lj = HERE / "labels.json"
    if lj.exists():
        labels = json.loads(lj.read_text()).get("labels", labels)
    names = {s["id"]: s["label"] for g in taxa["groups"] for s in g["species"]}
    names.update({g["id"]: g["label"] for g in taxa["groups"]})
    return models, labels, names


def safe(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report total size, download nothing")
    ap.add_argument("--class", dest="cls", help="only this class id")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--flat", action="store_true", help="no per-class subfolders")
    a = ap.parse_args()

    models, labels, names = load()
    todo = []
    for m in models:
        cls = (labels.get(str(m["id"])) or {}).get("class") or "unlabelled"
        if a.cls and cls != a.cls:
            continue
        folder = OUT if a.flat else OUT / cls
        todo.append((m, cls, folder / f'{safe(m["name"])}__{m["id"]}.glb'))
    if a.limit:
        todo = todo[: a.limit]

    s = requests.Session()
    s.headers["User-Agent"] = "coral-collection/1.0"

    if a.check:
        print(f"checking sizes of {len(todo)} models (HEAD requests, no download)…")
        total = unknown = 0
        for i, (m, cls, dest) in enumerate(todo, 1):
            try:
                r = s.head(m["glb"], timeout=20, allow_redirects=True)
                n = int(r.headers.get("content-length", 0))
                total += n
                if not n:
                    unknown += 1
            except Exception as e:
                unknown += 1
            if i % 50 == 0:
                print(f"  …{i}/{len(todo)}  {total/1e9:.2f} GB so far")
        print(f"\n{len(todo)} models, {total/1e9:.2f} GB"
              + (f" ({unknown} sizes unknown)" if unknown else ""))
        print(f"average {total/max(1,len(todo)-unknown)/1e6:.1f} MB per model")
        return

    done = skipped = failed = 0
    t0 = time.time()
    for i, (m, cls, dest) in enumerate(todo, 1):
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with s.get(m["glb"], timeout=120, stream=True) as r:
                r.raise_for_status()
                tmp = dest.with_suffix(".part")
                with tmp.open("wb") as fh:
                    for chunk in r.iter_content(1 << 20):
                        fh.write(chunk)
                tmp.rename(dest)
            done += 1
        except Exception as e:
            print(f"  ! {m['name']}: {e}")
            failed += 1
        if i % 20 == 0:
            rate = done / max(1e-9, time.time() - t0)
            print(f"  {i}/{len(todo)}  downloaded {done}, skipped {skipped}, failed {failed}"
                  f"  ({rate*60:.0f}/min)")

    size = sum(f.stat().st_size for f in OUT.rglob("*.glb"))
    print(f"\ndownloaded {done}, already had {skipped}, failed {failed}")
    print(f"{OUT} now holds {size/1e9:.2f} GB")
    if failed:
        print("re-run the same command to retry the failures")


if __name__ == "__main__":
    main()
