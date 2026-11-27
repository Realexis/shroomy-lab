"""Experiment 06, step 1: "out in the field" days from iNaturalist.

Real has no "searched, found nothing" records, and no public source has them. The usual trick:
people who record mushrooms also record plants, birds, insects... A day when such a person was out
(any observation) is an OUTING. If no mushroom was recorded on that outing, it is a stand-in for
"searched, nothing found". Not perfect (they may not have looked for mushrooms), but it fixes the
biggest problem of the back-test: finds only show days when people went out.

Downloads every Cyprus observation (any living thing) made 1 Sep 2022 - 26 Nov 2026 by the 261 people
who have recorded fungi in Cyprus. Public data, no account. 1 request per second (iNaturalist's ask).
Keeps only: user id, date, lat/lon, location accuracy, obscured flag, taxon name, its rank and
class/iconic group. Out: data/finds/raw/effort.json (local only; not published).
Run: python3 -I experiments/06-effort/fetch_effort.py
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path

LAB = Path(__file__).resolve().parents[2]
RAW = LAB / "data/finds/raw"
OUT = RAW / "effort.json"
UA = {"User-Agent": "shroomy-lab-research/0.1"}


def get(url):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", attempt + 1, e); time.sleep(10 * (attempt + 1))
    raise SystemExit("download failed")


def main():
    users = sorted({o["user"]["id"] for o in json.load(open(RAW / "inat.json"))})
    out = []
    for i in range(0, len(users), 60):
        above = 0
        while True:
            q = dict(place_id=10289, user_id=",".join(map(str, users[i:i + 60])), d1="2022-09-01", d2="2026-11-26",
                     per_page=200, order_by="id", order="asc", id_above=above)
            r = get("https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(q))
            if not r["results"]: break
            for o in r["results"]:
                if not o.get("location") or not o.get("observed_on"): continue
                lat, lon = map(float, o["location"].split(","))
                t = o.get("taxon") or {}
                out.append(dict(u=o["user"]["id"], d=o["observed_on"], lat=round(lat, 5), lon=round(lon, 5),
                                acc=o.get("public_positional_accuracy"), obs=bool(o.get("obscured")),
                                name=t.get("name"), rank=t.get("rank"), iconic=t.get("iconic_taxon_name")))
            above = r["results"][-1]["id"]
            print(f"  users {i + 1}-{min(i + 60, len(users))}: {len(out):,} kept", flush=True)
            time.sleep(1.1)
    OUT.write_text(json.dumps(out))
    print(f"✓ {len(out):,} observations -> {OUT.relative_to(LAB)}")


if __name__ == "__main__":
    main()
