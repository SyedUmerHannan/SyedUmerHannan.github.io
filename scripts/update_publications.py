#!/usr/bin/env python3
"""Refresh publications metrics from Google Scholar, Crossref, Zenodo.

ResearchGate blocks automated access to read counts. Optional field
researchgate_reads in data/publications.json is preserved if you set it by hand.
"""
from pathlib import Path
import json, re, urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (compatible; SUH-site-bot/1.0; +https://syedumerhannan.github.io)"}
SCHOLAR = "https://scholar.google.com/citations?user=HoDp67cAAAAJ&hl=en"

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()

def load_previous():
    path = ROOT / "data" / "publications.json"
    if not path.exists():
        return {}
    try:
        prev = json.loads(path.read_text())
        return {p["title"]: p for p in prev.get("papers", [])}
    except Exception:
        return {}

def main():
    prev = load_previous()
    html = fetch(SCHOLAR).decode("utf-8", "replace")
    titles = re.findall(r'class="gsc_a_at"[^>]*>([^<]+)', html)
    cite_cells = re.findall(r'class="gsc_a_ac[^"]*"[^>]*>([^<]*)', html)
    year_vals = re.findall(r'gsc_a_h[^>]*>(\d{4})<', html)

    enrich = {
        "Virelion Biotech Computational Cardiovascular Research Platform": {
            "doi": "10.5281/zenodo.22680867",
            "url": "https://doi.org/10.5281/zenodo.22680867",
            "venue": "Zenodo",
        },
        "Cutting Through the Debate: Surgical Resection Versus Surveillance-Based Approach for Kikuchi SM2/3 Colorectal Polyps": {
            "doi": "10.7759/cureus.97774",
            "url": "https://doi.org/10.7759/cureus.97774",
            "venue": "Cureus",
        },
    }

    pubs = []
    for i, title in enumerate(titles):
        cites = 0
        if i < len(cite_cells) and cite_cells[i].strip().isdigit():
            cites = int(cite_cells[i].strip())
        year = year_vals[i] if i < len(year_vals) else ""
        p = {
            "title": title,
            "year": year,
            "citations": cites,
            "citations_source": "Google Scholar",
            "scholar_url": SCHOLAR,
            "url": None,
            "doi": None,
            "venue": None,
            "researchgate_reads": (prev.get(title) or {}).get("researchgate_reads"),
            "reads": None,
            "reads_source": None,
        }
        for key, meta in enrich.items():
            if key.lower() in title.lower() or title.lower() in key.lower():
                p.update(meta)
        pubs.append(p)

    try:
        z = json.loads(fetch("https://zenodo.org/api/records/22680867"))
        stats = z.get("stats") or {}
        for p in pubs:
            if p.get("doi") == "10.5281/zenodo.22680867":
                p["reads"] = stats.get("views") or stats.get("version_views")
                p["reads_source"] = "Zenodo views"
                p["downloads"] = stats.get("downloads") or stats.get("version_downloads")
    except Exception as e:
        print("zenodo:", e)

    try:
        cr = json.loads(fetch("https://api.crossref.org/works/10.7759/cureus.97774"))
        msg = cr.get("message") or {}
        for p in pubs:
            if p.get("doi") == "10.7759/cureus.97774":
                p["citations"] = msg.get("is-referenced-by-count", p["citations"])
                p["citations_source"] = "Crossref"
    except Exception as e:
        print("crossref:", e)

    out = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scholar_profile": SCHOLAR,
        "orcid": "https://orcid.org/0009-0004-0282-8765",
        "researchgate_note": "ResearchGate blocks automated reads; set researchgate_reads manually per paper if needed.",
        "papers": pubs,
    }
    path = ROOT / "data" / "publications.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {path} ({len(pubs)} papers)")

if __name__ == "__main__":
    main()
