# Syed Umer Hannan — personal site

Static site for [syedumerhannan.github.io](https://syedumerhannan.github.io).

## Local

```bash
python3 -m http.server 8080
```

## Refresh FieldLevel + Duolingo widgets

```bash
python3 scripts/update_side_quests.py
```

## GitHub Pages

Settings → Pages → Deploy from branch `main` / root.

Scheduled refresh: `.github/workflows/update-widgets.yml`.
