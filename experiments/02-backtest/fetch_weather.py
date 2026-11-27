"""Job 2, step 1: past daily weather for the back-test, from the SAME model the live map uses
(Open-Meteo historical forecast API, ECMWF IFS 9 km), seasons 2022-23 to 2026-27.

Points: a 0.1 degree grid (about 10 km) over every part of Cyprus that has land.
Days: 31 Aug -> 30 Apr each season (the score looks back 30+ days from 1 Oct); this season to yesterday.
Budget: the live robot uses the same free allowance from this Mac (~1,200 calls/day). This script
keeps the lab far below the limits: at most 1,500 calls per hour and 4,000 per day, and it
caches every reply, so running it again costs nothing.
Run:  site/pipeline/.venv/bin/python experiments/02-backtest/fetch_weather.py [--dry]
"""
import json, sys, time, urllib.parse, urllib.request
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer

LAB = Path(__file__).resolve().parents[2]
OUT = LAB / "experiments/02-backtest/weather"; OUT.mkdir(parents=True, exist_ok=True)
CACHE = OUT / "cache"; CACHE.mkdir(exist_ok=True)
URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"
UA = {"User-Agent": "shroomy-lab-research/0.1"}
DAILY = ["precipitation_sum", "temperature_2m_mean", "temperature_2m_min"]
HOURLY = ["soil_moisture_0_to_7cm"]
N_VARS = len(DAILY) + len(HOURLY)
PER_REQ = 25
MAX_HOUR, MAX_DAY = 1500, 4000
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
SEASONS = [(f"{y}-08-31", min(f"{y + 1}-04-30", YESTERDAY)) for y in (2022, 2023, 2024, 2025, 2026)]


def points():
    """Centres of 0.1 degree boxes that hold at least one 250 m land square."""
    with rasterio.open(LAB / "site/data/processed/habitat_250m.tif") as s:
        land = s.read(s.descriptions.index("land_fraction") + 1) > 0.5
        rows, cols = np.nonzero(land)
        x, y = rasterio.transform.xy(s.transform, rows, cols)
    lon, lat = Transformer.from_crs("EPSG:32636", "EPSG:4326", always_xy=True).transform(x, y)
    boxes = sorted({(round(np.floor(a * 10) / 10 + 0.05, 2), round(np.floor(b * 10) / 10 + 0.05, 2))
                    for a, b in zip(lon, lat)})
    return np.array(boxes)                                   # (n, 2) lon, lat


def cost(n_loc, n_days):
    return n_loc * (N_VARS / 10) * (n_days / 14)      # Open-Meteo: 1 call per location, 10 variables, 14 days


USAGE = OUT / "usage.json"


def used(seconds):
    log = json.loads(USAGE.read_text()) if USAGE.exists() else []
    return sum(c for t, c in log if time.time() - t < seconds)


def note(c):
    log = json.loads(USAGE.read_text()) if USAGE.exists() else []
    log.append([time.time(), c]); USAGE.write_text(json.dumps(log))


def get(pts, start, end):
    key = CACHE / f"{start}_{end}_{pts[0][0]:.2f}_{pts[0][1]:.2f}_{len(pts)}.json"
    if key.exists(): return json.loads(key.read_text())
    n_days = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
    c = cost(len(pts), n_days)
    while used(3600) + c > MAX_HOUR:
        if used(86400) + c > MAX_DAY: raise SystemExit(f"day budget reached ({used(86400):.0f}); run again tomorrow")
        print(f"  hour budget: waiting ({used(3600):.0f} used)"); time.sleep(120)
    q = dict(latitude=",".join(f"{p[1]:.2f}" for p in pts), longitude=",".join(f"{p[0]:.2f}" for p in pts),
             models="ecmwf_ifs", daily=",".join(DAILY), hourly=",".join(HOURLY), timezone="Asia/Nicosia",
             start_date=start, end_date=end)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL + "?" + urllib.parse.urlencode(q), headers=UA), timeout=180) as r:
                data = json.load(r)
            break
        except Exception as e:
            print("  retry", attempt + 1, e); time.sleep(60 * (attempt + 1))
    else:
        raise SystemExit("weather download failed")
    note(c)
    data = data if isinstance(data, list) else [data]
    key.write_text(json.dumps(data))
    return data


def main(dry=False):
    pts = points()
    total = sum(cost(len(pts), (date.fromisoformat(b) - date.fromisoformat(a)).days + 1) for a, b in SEASONS)
    print(f"{len(pts)} points, {len(SEASONS)} seasons, about {total:.0f} calls")
    if dry: return
    for a, b in SEASONS:
        dates = [(date.fromisoformat(a) + timedelta(days=i)).isoformat()
                 for i in range((date.fromisoformat(b) - date.fromisoformat(a)).days + 1)]
        arr = {k: np.full((len(pts), len(dates)), np.nan, "float32") for k in ("precip", "tmean", "tmin", "soil")}
        elev = np.zeros(len(pts))
        for i in range(0, len(pts), PER_REQ):
            for j, d in enumerate(get(pts[i:i + PER_REQ], a, b)):
                k = i + j
                dl = d["daily"]
                arr["precip"][k] = np.array(dl["precipitation_sum"], "float64")
                arr["tmean"][k] = np.array(dl["temperature_2m_mean"], "float64")
                arr["tmin"][k] = np.array(dl["temperature_2m_min"], "float64")
                sm = np.array(d["hourly"]["soil_moisture_0_to_7cm"], "float64").reshape(len(dates), 24)
                arr["soil"][k] = np.nanmean(sm, axis=1)
                elev[k] = d.get("elevation", 0.0)
            print(f"  {a[:4]}: {min(i + PER_REQ, len(pts))}/{len(pts)} points (used this hour {used(3600):.0f})")
        x, y = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True).transform(pts[:, 0], pts[:, 1])
        np.savez_compressed(OUT / f"season_{a[:4]}.npz", lon=pts[:, 0], lat=pts[:, 1], x=np.array(x), y=np.array(y),
                            elev_om=elev, dates=np.array(dates), **arr)
        print(f"✓ season {a[:4]} saved")


if __name__ == "__main__":
    main("--dry" in sys.argv)
