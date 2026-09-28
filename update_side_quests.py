#!/usr/bin/env python3
"""Refresh FieldLevel + Duolingo JSON used by side-quests.html widgets.

  python3 scripts/update_side_quests.py

Then redeploy. Browsers load data/*.json from your site (CORS-safe).
Strava still needs a one-time profile embed from Share your Activities.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

FL_API = (
    "https://www.fieldlevel.com/api/profileapi/profilev2/"
    "syed.umerhannan.2705490?sport=soccermen&profileInteractionContextEnum=4"
)
FL_PROFILE = "https://www.fieldlevel.com/app/profile/syed.umerhannan.2705490/soccermen"
DUO_API = "https://www.duolingo.com/2017-06-30/users?username=SyedUHannan"
DUO_PROFILE = "https://www.duolingo.com/u/SyedUHannan"
DUO_WIDGET = "https://duolingo-stats-card.vercel.app/api?username=SyedUHannan&theme=forest"


def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; side-quests-updater/1.0)"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def update_fieldlevel() -> dict:
    raw = get_json(FL_API)
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
    out = {
        "source": "fieldlevel",
        "profileUrl": FL_PROFILE,
        "apiUrl": FL_API,
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
    path = DATA / "fieldlevel.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"FieldLevel → {path} ({out.get('team')})")
    return out


def update_duolingo() -> dict:
    raw = get_json(DUO_API)
    users = raw.get("users") or []
    u = users[0] if users else {}
    courses = []
    for c in (u.get("courses") or [])[:6]:
        courses.append(
            {
                "title": c.get("title") or c.get("learningLanguage"),
                "xp": c.get("xp"),
                "learningLanguage": c.get("learningLanguage"),
            }
        )
    out = {
        "username": u.get("username") or "SyedUHannan",
        "name": u.get("name"),
        "streak": u.get("streak"),
        "totalXp": u.get("totalXp"),
        "learningLanguage": u.get("learningLanguage"),
        "courses": courses,
        "profileUrl": DUO_PROFILE,
        "widgetSvg": DUO_WIDGET,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    path = DATA / "duolingo.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Duolingo → {path} (streak {out.get('streak')}, xp {out.get('totalXp')})")
    return out


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    update_fieldlevel()
    update_duolingo()
    print("Done. Redeploy so the site serves the new JSON.")


if __name__ == "__main__":
    main()
