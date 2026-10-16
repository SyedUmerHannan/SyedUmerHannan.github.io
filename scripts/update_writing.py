#!/usr/bin/env python3
"""Pull Substack + Medium RSS into data/writing.json."""
from pathlib import Path
import json, re, urllib.request, html as htmlmod
from xml.etree import ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (compatible; SUH-site-bot/1.0; +https://syedumerhannan.github.io)"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()

def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return htmlmod.unescape(re.sub(r"\s+", " ", s).strip())

def parse_rss(url, source):
    root_xml = ET.fromstring(fetch(url))
    items = []
    for item in root_xml.findall(".//item"):
        title = strip_html(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip().split("?")[0]
        desc = strip_html(item.findtext("description") or "")[:320]
        pub = item.findtext("pubDate") or ""
        try:
            dt = parsedate_to_datetime(pub)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            date = dt.strftime("%Y-%m-%d")
            date_human = dt.strftime("%b ") + str(dt.day) + dt.strftime(", %Y")
        except Exception:
            date, date_human = "", pub
        if title and link:
            items.append({
                "source": source,
                "title": title,
                "url": link,
                "date": date,
                "date_human": date_human,
                "summary": desc,
            })
    return items

def main():
    substack = parse_rss("https://syedumerhannan.substack.com/feed", "Substack")
    medium = parse_rss("https://medium.com/feed/@syedumerhannan", "Medium")
    series = [x for x in substack if "syedumerhannan.substack.com" in x["url"]]
    for i, x in enumerate(series):
        x["series"] = "The Regenerative Edge"
        x["series_number"] = len(series) - i
    writing = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "substack": series,
        "medium": medium,
        "all": sorted(series + medium, key=lambda x: x.get("date") or "", reverse=True),
    }
    out = ROOT / "data" / "writing.json"
    out.write_text(json.dumps(writing, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {out} ({len(series)} Substack, {len(medium)} Medium)")

if __name__ == "__main__":
    main()
