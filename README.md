# Adopt-a-Coral

An open 3D archive of Caribbean coral colonies, scanned with a smartphone in an underwater
housing and reconstructed in KIRI Engine, published alongside the field guide that explains
how to make and share your own.

The whole site is a static page. There is no build step and no server.

## Files

```
index.html     the entire site - every pane, the guide, and the data, in one file (generated)
build/         the template and script that generate index.html, plus build notes
labels.json    the species labels; the page reads this and it overrides the copy inside index.html
guide/         the field guide figures, plus the landing-page photograph (hero.jpg)
data/          the source data the page was built from, published for reuse
```

`data/` is not read by the site at runtime. It is there so the archive is usable by other people:

| file | what it is |
|---|---|
| `models.json` | the 616 models: name, Kiri id, embed / thumbnail / .glb URLs, capture date |
| `taxa.json` | the class list - every genus and species the labels can point at |
| `coords.json` | a location per model, derived from the GPS of the surface video clips |

## Publishing

Commit everything and enable GitHub Pages (Settings → Pages → Deploy from a branch → `main` → `/`).
Nothing else is required.

## Changing the site

`index.html` is generated. Edit `build/template.html`, then:

```bash
python3 build/build.py
```

`build/NOTES.md` explains where every piece of data came from, which decisions were
deliberate, and which traps to avoid. Read it before making changes.

## Updating the labels

Open the site, classify, and the page saves `labels.json` back to this repository by itself once
you have connected it — see the **Sync** button. Failing that, **Export labels.json** downloads
the file and you commit it by hand. The site reads whichever `labels.json` sits next to
`index.html`, so either route works.

## What the labels mean

Each entry is keyed by the Kiri model id and carries a `source`:

- **`human`** — determined by the author against the 3D model.
- **`ai`** — suggested by Claude from a single thumbnail render, and **not yet checked**.

The `ai` labels are a sorting aid, not determinations. They are unreliable at species level,
especially among the brain corals, where the distinguishing features are not visible at
thumbnail resolution. Every one of them carries `needsReview: true` until a person confirms it.
The file's own header repeats this caution, so anyone who downloads it is told.

## Locations

Coordinates come from the GPS of the video clips recorded at the surface, matched to each scan
by dive: the clips from a day are grouped into dives, and each model takes the median position
of the dive nearest in time to when it was processed. **They locate the dive, not the colony.**
Median precision is about half a kilometre. One model has no location because no clip that day
carried GPS.

## Credits

Thank you to all the people who support this project.

Louis Escobar and Taganga Dive Station; Bocas Pirates Dive Center; Mother of Corals, Bocas del
Toro; Diego Vallardes and SCUBA Portobelo; Utila Dive Center; Underwater Vision Dive Center;
Suita Narváez, Bay Island Conservation Agency (BICA); Raising Corals; and FreeWay SCUBA.

Thank you to my friends, family, and colleagues.

Models and field guide by Matan Yuval. Map tiles © OpenStreetMap contributors and Esri.
Site built with Claude (claude-opus-5).
