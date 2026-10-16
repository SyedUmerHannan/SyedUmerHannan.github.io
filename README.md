# Syed Umer Hannan — personal site

Static site for [syedumerhannan.github.io](https://syedumerhannan.github.io).

## Local

```bash
python3 -m http.server 8080
```

## Data refresh (writing, publications, widgets)

```bash
python3 scripts/update_writing.py        # Substack + Medium RSS → data/writing.json
python3 scripts/update_publications.py   # Scholar / Crossref / Zenodo → data/publications.json
python3 scripts/update_side_quests.py    # FieldLevel + Duolingo
```

Scheduled via `.github/workflows/update-widgets.yml`.

**Note:** ResearchGate blocks automated read counts. Set `researchgate_reads` on a paper in `data/publications.json` by hand if you want those numbers shown.

## GitHub Pages

Settings → Pages → Deploy from branch `main` / root.
