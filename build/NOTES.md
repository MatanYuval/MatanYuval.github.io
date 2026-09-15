# Notes for whoever updates this next

Written at the end of the session that built the site, so the next one doesn't start cold.

## How the site is put together

`index.html` is **generated**. `build/template.html` is the real source; `build/build.py`
injects the data and writes `index.html`. Editing `index.html` by hand works — it is one
self-contained file — but the next build overwrites it. Lasting changes go in the template.

Seven panes, all in that one file: Home, Classify, Sorting room, 3D models, Map, Easy steps,
Guide. Everything is inline; the only external requests at runtime are the Kiri embeds and
thumbnails, the Leaflet library from cdnjs, and map tiles.

```
build/template.html     the source
build/build.py          run this after changing the template or the data
build/guide_data.json   the guide, both languages, converted from LaTeX by pandoc
build/hero_bits.json    the author's hero paragraph and the highlight caption, verbatim
```

## Where the data came from

| file | origin |
|---|---|
| `data/models.json` | the author's Kiri Engine export (`kiri-models.json`), sorted oldest first |
| `data/taxa.json` | written for this project; grown as the author named missing genera |
| `data/coords.json` | derived from `iphone_video_locations.csv`, exported from Photos on macOS |
| `labels.json` | 23 determinations by the author, 593 suggestions from thumbnails |
| `guide/*.jpg` | `FigsFInalManual/*.png` from the Overleaf project, resized to 1500px |
| `guide/hero.jpg` | the left panel of Fig1New with its baked-in caption band cropped off |

The guide came from `mainFinal19Jan26.tex` and `mainspanish.tex`, converted with
`pandoc --from=latex --to=html5 --citeproc`. To refresh it after editing Overleaf, re-run
pandoc, fix the image paths to `guide/<name>.jpg`, shift the heading levels down one, and
rebuild `guide_data.json` with `html`, `toc`, `quick` and `quickTitle` per language. The
`quick` block is Appendix C, extracted for the Easy steps pane.

## Decisions worth not relitigating

**The labels are not trustworthy at species level.** 593 of them came from a single
thumbnail render. The author checked about two dozen and nearly all of them were wrong —
the whole Orbicella folder turned out to be Montastraea. `Pseudodiploria strigosa` holds 171
models on that basis and is the most suspect group in the file. Every AI label carries
`needsReview: true`, and `labels.json` says so in its own header. Do not present them as
determinations, and do not quietly "improve" them without the author looking at the models.

**Coordinates locate the dive, not the colony.** The Kiri export has no link to the source
video, so there is no exact join. Clips from a day are clustered into dives and each model
takes the median position of the dive nearest in time to when Kiri processed it. Median
precision about 0.5 km. If Kiri ever exposes the original filename per project, that becomes
an exact join and the coordinates get much better.

**Site names were wrong twice.** 243 models were labelled Roatán when 16.086/−86.912 is
Utila, and 22 were labelled Panamá when 9.638/−82.677 is Costa Rica. Check coordinates
against known places rather than trusting a nearest-anchor guess.

**Browser storage is shared across a whole domain, not per file or folder.** Labels made in
one downloaded copy appear in the next, and anything else hosted on the same domain can read
the same storage — including the sync token. This surprised the author more than once.

**The sync token cannot be scoped below a repository.** Fine-grained, one repo,
Contents: read and write, with an expiry. The site should live in its own repo for that reason.

## Traps hit while building, so they aren't hit again

- Sharing one Leaflet tile-layer instance between two base layers blanks the map when you
  switch, because Leaflet removes the old layer after adding the new one. Give each its own.
- A long URL inside a CSS grid item sizes the whole column. `minmax(0,1fr)` plus
  `overflow-wrap:anywhere`.
- Flex children shrink below their content by default; the class list needed `flex:0 0 auto`
  or the genus boxes collapse into slivers.
- Everything interpolated into markup must be escaped. The page can hold a write-capable
  token, so an unescaped project name would be a real hole, not a cosmetic one.
- Text-replacement build steps need assertions. A silent no-op shipped a broken pane once.
- The sandbox cannot reach `kiriengine.com`, `arcgisonline` or the tile servers. Test with
  Playwright and stubbed routes, and use regex route patterns — a glob like
  `**/tile.openstreetmap.org/**` never matches the `{s}` subdomains.

## Loose ends

- 7 models sit in "Scolymia / Isophyllia (unsplit)" waiting to be split. Delete that class
  once it is empty.
- 163 models are "Stony coral, genus unclear" and 6 are unreadable.
- Project 590 has no coordinates; no clip that day carried GPS.
- The author had 76 classifications in browser storage that were never merged into this file.
  Check whether they made it into the repo before trusting the counts here.
- The guide's own Acknowledgements section still has the older, shorter credits list; the
  site's Credits dialog is the current one.
- Raising Corals and FreeWay SCUBA have no country listed; the author never said.
