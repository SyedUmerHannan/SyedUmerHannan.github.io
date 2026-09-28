#!/usr/bin/env python3
"""Pull public FieldLevel profile JSON and write site_new/data/fieldlevel.json

Run from repo root or site_new:
  python3 scripts/update_fieldlevel.py

Then redeploy. Browser cannot call FieldLevel directly (no CORS).
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = (
    "https://www.fieldlevel.com/api/profileapi/profilev2/"
    "syed.umerhannan.2705490?sport=soccermen&profileInteractionContextEnum=4"
)
PROFILE = "https://www.fieldlevel.com/app/profile/syed.umerhannan.2705490/soccermen"

ROOT = Path(__file__).resolve().parents[1]  # site_new/
OUT = ROOT / "data" / "fieldlevel.json"


def fetch() -> dict:
    req = urllib.request.Request(
        API,
        headers={"User-Agent": "Mozilla/5.0 (compatible; personal-site-updater/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def normalize(raw: dict) -> dict:
    a = raw.get("Athlete") or {}
    d = raw.get("Details") or {}
    teams = d.get("Teams") or []
    team_name = team_type = team_start = None
    if teams:
        t0 = teams[0]
        team = t0.get("Team") or {}
        team_name = (
            team.get("OrganizationName")
            or team.get("TeamName")
            or team.get("TeamDisplayName")
        )
        team_type = (team.get("AthleticAssociationEnum") or {}).get("Label")
        team_start = (t0.get("StartDateUtc") or "")[:10]
    return {
        "source": "fieldlevel",
        "profileUrl": PROFILE,
        "apiUrl": API,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "displayName": a.get("DisplayName"),
        "positions": a.get("Positions"),
        "sport": (a.get("SportEnum") or {}).get("Label"),
        "height": a.get("Height"),
        "weightLbs": a.get("Weight"),
        "city": a.get("City"),
        "state": a.get("State"),
        "gradYear": a.get("HighSchoolGraduationYear"),
        "dominantFoot": (d.get("DominantSideValue") or {}).get("Value"),
        "hobbies": d.get("HobbiesAndInterests"),
        "team": team_name,
        "teamType": team_type,
        "teamStart": team_start,
        "commitment": (a.get("CommitmentLevelEnum") or {}).get("Label"),
    }


def main() -> None:
    raw = fetch()
    widget = normalize(raw)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(widget, indent=2) + "\n")
    print(f"Wrote {OUT}")
    print(f"  {widget['displayName']} · {widget['positions']} · {widget['team']}")


if __name__ == "__main__":
    main()
