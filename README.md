# Syed Umer Hannan — personal site

Static site for [SyedUmerHannan.github.io](https://syedumerhannan.github.io).

## Local
Open `index.html` or serve the folder:

```bash
python3 -m http.server 8080
```

## Refresh FieldLevel + Duolingo widgets
```bash
python3 scripts/update_side_quests.py
```

## GitHub Pages
Repo Settings → Pages → Deploy from branch `main` / root.

Scheduled refresh is in `.github/workflows/update-widgets.yml`.
