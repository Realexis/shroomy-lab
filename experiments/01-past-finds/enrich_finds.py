"""Job 1, step 2: add to each record in data/finds/finds.json
  - group: mushroom / lichen / other   (from the name's class, via the free GBIF name checker)
  - district: the Cyprus district it falls in (geoBoundaries ADM1, from OpenStreetMap, ODbL licence)
and write the small file the lab map reads: site/web/public/data/finds.json.
Run after fetch_finds.py:  python3 -I experiments/01-past-finds/enrich_finds.py
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path

LAB = Path(__file__).resolve().parents[2]
UA = {"User-Agent": "shroomy-lab-research/0.1"}
DISTRICTS_URL = ("https://www.geoboundaries.org/data/snapshots/1c423398df24ddf6e730b116567d2181c9782778d0459c3f3b76ca2f9f12b6bc"
                 "/gbOpen/CYP/ADM1/geoBoundaries-CYP-ADM1_simplified.geojson")
# Classes that are (nearly all) lichens, and classes that make mushrooms, brackets, puffballs, cups, jelly fungi.
LICHEN = {"Lecanoromycetes", "Arthoniomycetes", "Lichinomycetes", "Candelariomycetes", "Coniocybomycetes"}
MUSHROOM = {"Agaricomycetes", "Pezizomycetes", "Tremellomycetes", "Dacrymycetes"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def inside(lon, lat, ring):
    hit, j = False, len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi: hit = not hit
        j = i
    return hit


def main():
    path = LAB / "data/finds/finds.json"
    d = json.load(open(path)); recs = d["records"]

    cache_f = LAB / "data/finds/raw/name_class.json"
    cache = json.load(open(cache_f)) if cache_f.exists() else {}
    for n in sorted({r["name"] for r in recs if r["name"]} - set(cache)):
        m = get("https://api.gbif.org/v1/species/match?" + urllib.parse.urlencode(dict(name=n, kingdom="Fungi")))
        cache[n] = m.get("class"); time.sleep(0.1)
    json.dump(cache, open(cache_f, "w"), indent=0)

    dist_f = LAB / "data/finds/raw/cy_districts.geojson"
    if not dist_f.exists(): dist_f.write_text(json.dumps(get(DISTRICTS_URL)))
    polys = []
    for f in json.load(open(dist_f))["features"]:
        g = f["geometry"]; parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        polys += [(f["properties"]["shapeName"], p[0]) for p in parts]

    for r in recs:
        c = cache.get(r["name"])
        r["class"] = c
        r["group"] = "lichen" if c in LICHEN else "mushroom" if c in MUSHROOM else "other" if c else "unknown"
        r["district"] = next((n for n, ring in polys if inside(r["lon"], r["lat"], ring)), "at sea / coast")
    json.dump(d, open(path, "w"), ensure_ascii=False, indent=0)

    # Small file for the map: short keys, only what the map shows.
    keep = ["id", "name", "common", "date", "year", "month", "lat", "lon", "acc_m", "loc", "group", "kind",
            "source", "link", "observer", "licence", "photo", "has_photo", "district"]
    web = LAB / "site/web/public/data/finds.json"
    json.dump(dict(fetched=d["fetched"], records=[{k: r[k] for k in keep} for r in recs]),
              open(web, "w"), ensure_ascii=False, separators=(",", ":"))
    print(f"✓ {len(recs)} records with group + district -> {web.relative_to(LAB)} ({web.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    main()
