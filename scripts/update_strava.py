#!/usr/bin/env python3
"""Strava public pages hide YTD totals from logged-out clients.

Edit data/strava.json stats by hand, or set STRAVA_ACCESS_TOKEN and extend this
script to call https://www.strava.com/api/v3/athletes/{id}/stats

Current athlete id: 201168411
"""
from pathlib import Path
import json, os, urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "strava.json"
data = json.loads(path.read_text()) if path.exists() else {}
data.setdefault("athleteId", "201168411")
data.setdefault("profileUrl", "https://www.strava.com/athletes/201168411")
data.setdefault("stats", {})
token = os.environ.get("STRAVA_ACCESS_TOKEN")
if token:
    req = urllib.request.Request(
        f"https://www.strava.com/api/v3/athletes/{data['athleteId']}/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        stats = json.loads(r.read())
    ytd = stats.get("ytd_run_totals") or stats.get("ytd_ride_totals") or {}
    data["stats"] = {
        "activities": ytd.get("count"),
        "distance_km": round((ytd.get("distance") or 0) / 1000, 1) if ytd.get("distance") is not None else None,
        "moving_time_hours": round((ytd.get("moving_time") or 0) / 3600, 1) if ytd.get("moving_time") is not None else None,
        "elevation_m": int(ytd.get("elevation_gain") or 0) if ytd.get("elevation_gain") is not None else None,
    }
    data["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("Updated from Strava API", data["stats"])
else:
    data["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("No STRAVA_ACCESS_TOKEN — kept manual stats:", data.get("stats"))
