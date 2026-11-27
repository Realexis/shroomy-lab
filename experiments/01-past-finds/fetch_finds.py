"""Job 1: pull every Cyprus fungi record (lichens included) from iNaturalist and GBIF.

Writes raw downloads to data/finds/raw/ and one clean, de-duplicated list to data/finds/finds.json.
Free public APIs, no keys. Run:  python3 experiments/01-past-finds/fetch_finds.py
Rules: photos are linked from their original address (never copied), and a photo is only shown when
its licence allows reuse (Creative Commons / public domain). Obscured locations stay obscured.
"""
import json, math, time, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path

LAB = Path(__file__).resolve().parents[2]
RAW = LAB / "data/finds/raw"; RAW.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "shroomy-lab-research/0.1"}
INAT_PLACE, INAT_FUNGI = 10289, 47170           # iNaturalist: Cyprus (whole island), kingdom Fungi (lichens are inside it)
GBIF_FUNGI = 5                                   # GBIF kingdom Fungi
GBIF_INAT_DATASET = "50c9509d-22c7-4a22-a47d-8c48425ef4a7"   # iNaturalist research-grade copy inside GBIF
GOOD_ACC_M = 500                                 # "good" location: known to within 500 m


def get(url):
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except Exception as e:                   # network hiccup or rate limit: wait and retry
            print("  retry", attempt + 1, e); time.sleep(5 * (attempt + 1))
    raise SystemExit("could not download " + url)


def fetch_inat():
    out, above = [], 0
    while True:
        q = dict(place_id=INAT_PLACE, taxon_id=INAT_FUNGI, per_page=200, order_by="id", order="asc", id_above=above)
        r = get("https://api.inaturalist.org/v1/observations?" + urllib.parse.urlencode(q))
        if not r["results"]: break
        out += r["results"]; above = r["results"][-1]["id"]
        print(f"  iNaturalist {len(out)}/{r['total_results']}"); time.sleep(1.1)   # iNat asks for ~1 request/s
    return out


def fetch_gbif():
    out, off = [], 0
    while True:
        q = dict(country="CY", kingdomKey=GBIF_FUNGI, hasCoordinate="true", limit=300, offset=off)
        r = get("https://api.gbif.org/v1/occurrence/search?" + urllib.parse.urlencode(q))
        out += r["results"]; off += 300
        print(f"  GBIF {len(out)}/{r['count']}")
        if r["endOfRecords"]: break
        time.sleep(0.3)
    return out


LIC = {"cc0": "CC0", "cc-by": "CC BY", "cc-by-nc": "CC BY-NC", "cc-by-sa": "CC BY-SA", "cc-by-nd": "CC BY-ND",
       "cc-by-nc-sa": "CC BY-NC-SA", "cc-by-nc-nd": "CC BY-NC-ND"}


def gbif_lic(url):
    u = (url or "").lower()
    if "publicdomain/zero" in u or "cc0" in u: return "CC0"
    for code in ("by-nc-sa", "by-nc-nd", "by-nc", "by-sa", "by-nd", "by"):
        if f"licenses/{code}/" in u or u.endswith(f"cc_{code.replace('-', '_')}_4_0") or f"cc-{code}" in u: return "CC " + code.upper()
    return None


def from_inat(o):
    t = o.get("taxon") or {}
    lat, lon = map(float, o["location"].split(",")) if o.get("location") else (None, None)
    obscured = bool(o.get("obscured")) or o.get("geoprivacy") in ("obscured", "private") \
        or o.get("taxon_geoprivacy") in ("obscured", "private")
    photo = None
    for p in o.get("photos") or []:
        lic = LIC.get(p.get("license_code") or "")
        if lic:                                   # reusable licence only; "all rights reserved" is linked, not shown
            photo = dict(url=p["url"].replace("/square.", "/medium."), licence=lic, credit=p.get("attribution"))
            break
    d = o.get("observed_on_details") or {}
    return dict(
        id=f"inat:{o['id']}", source="iNaturalist", link=o.get("uri") or f"https://www.inaturalist.org/observations/{o['id']}",
        name=t.get("name"), common=t.get("preferred_common_name"), rank=t.get("rank"),
        date=o.get("observed_on"), year=d.get("year"), month=d.get("month"),
        lat=lat, lon=lon, acc_m=o.get("public_positional_accuracy"), obscured=obscured,
        kind="photo observation", quality=o.get("quality_grade"),
        observer=(o.get("user") or {}).get("name") or (o.get("user") or {}).get("login"),
        licence=LIC.get(o.get("license_code") or "", "all rights reserved"),
        photo=photo, has_photo=bool(o.get("photos")))


KIND = {"HUMAN_OBSERVATION": "observation", "OBSERVATION": "observation", "MACHINE_OBSERVATION": "observation",
        "PRESERVED_SPECIMEN": "herbarium specimen", "LIVING_SPECIMEN": "living culture",
        "MATERIAL_CITATION": "literature record", "OCCURRENCE": "record"}


def from_gbif(o):
    photo = None
    for m in o.get("media") or []:
        lic = gbif_lic(m.get("license"))
        if m.get("type") == "StillImage" and m.get("identifier") and lic:
            who = m.get("rightsHolder") or m.get("creator") or o.get("recordedBy") or "unknown"
            photo = dict(url=m["identifier"], licence=lic, credit=f"© {who} ({lic})")
            break
    unc = o.get("coordinateUncertaintyInMeters")
    date = (o.get("eventDate") or "")[:10] or None
    if date and o.get("day") is None: date = None if o.get("month") is None else f"{o['year']}-{o['month']:02d}"
    return dict(
        id=f"gbif:{o['key']}", source="GBIF · " + (o.get("datasetName") or o.get("institutionCode") or "dataset"),
        link=f"https://www.gbif.org/occurrence/{o['key']}",
        name=o.get("species") or o.get("scientificName"), common=None, rank=(o.get("taxonRank") or "").lower() or None,
        date=date, year=o.get("year"), month=o.get("month"),
        lat=o.get("decimalLatitude"), lon=o.get("decimalLongitude"), acc_m=unc,
        obscured="COORDINATE_ROUNDED" in (o.get("issues") or []) or bool(o.get("informationWithheld")),
        kind=KIND.get(o.get("basisOfRecord"), "record"), quality=None,
        observer=o.get("recordedBy"), licence=gbif_lic(o.get("license")) or "see record",
        photo=photo, has_photo=bool(o.get("media")),
        _refs=" ".join(str(o.get(k) or "") for k in ("references", "occurrenceID", "catalogNumber")),
        _basis=o.get("basisOfRecord"), _dataset=o.get("datasetKey"))


def km(a, b):
    return 6371 * math.hypot(math.radians(b["lat"] - a["lat"]),
                             math.radians(b["lon"] - a["lon"]) * math.cos(math.radians(a["lat"])))


def main():
    print("iNaturalist…"); inat_raw = fetch_inat(); json.dump(inat_raw, open(RAW / "inat.json", "w"))
    print("GBIF…"); gbif_raw = fetch_gbif(); json.dump(gbif_raw, open(RAW / "gbif.json", "w"))
    log = defaultdict(int)

    recs = []
    for o in inat_raw:
        r = from_inat(o)
        if r["lat"] is None: log["iNat: no location"] += 1; continue
        if o.get("quality_grade") == "casual": log["iNat: casual (no date, captive or no photo)"] += 1; continue
        recs.append(r)
    inat_ids = {r["id"].split(":")[1] for r in recs} | {str(o["id"]) for o in inat_raw}

    for o in gbif_raw:
        r = from_gbif(o)
        if r["_basis"] == "MATERIAL_SAMPLE": log["GBIF: DNA sample from soil/water (not a mushroom someone saw)"] += 1; continue
        if r["_dataset"] == GBIF_INAT_DATASET: log["GBIF: copy of an iNaturalist record"] += 1; continue
        if "inaturalist.org/observations/" in r["_refs"] and r["_refs"].rsplit("/", 1)[-1].split()[0] in inat_ids:
            log["GBIF: copy of an iNaturalist record"] += 1; continue
        recs.append(r)

    # Fuzzy duplicates: same species, same day, within 200 m -> keep one (prefer the one with a photo, then iNat).
    recs.sort(key=lambda r: (not r["photo"], r["source"] != "iNaturalist"))
    kept, seen = [], defaultdict(list)
    for r in recs:
        k = (r["name"], r["date"]) if r["date"] and r["name"] else None
        if k and any(km(r, s) < 0.2 for s in seen[k]): log["same species, same day, within 200 m"] += 1; continue
        if k: seen[k].append(r)
        kept.append(r)

    for r in kept:
        r["loc"] = "obscured" if r["obscured"] else ("good" if r["acc_m"] is not None and r["acc_m"] <= GOOD_ACC_M else "rough")
        for k in [k for k in r if k.startswith("_")]: del r[k]
        r["lat"], r["lon"] = round(r["lat"], 5), round(r["lon"], 5)
    kept.sort(key=lambda r: (r["date"] or "", r["id"]))
    out = LAB / "data/finds/finds.json"
    json.dump(dict(fetched=time.strftime("%Y-%m-%d"), good_accuracy_m=GOOD_ACC_M, removed=dict(log), records=kept),
              open(out, "w"), ensure_ascii=False, indent=0)
    print(f"✓ {len(kept)} records -> {out.relative_to(LAB)}"); print(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()
