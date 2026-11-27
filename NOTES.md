# Shroomy LAB — running notes

The R&D copy of ShroomyMap (a map of mushroom growing **conditions**, not of where mushrooms are).
**Nothing here goes to the live site without Real's OK.**

## Addresses
- **Local:** `bash ~/Desktop/WORK/Claude_Code/shroomy-rnd/start.sh` → http://localhost:5190/
- **Phone:** https://realexis.github.io/shroomy-lab/ (repo `Realexis/shroomy-lab`, branch `gh-pages`)
- Publish to the phone address **by hand only**: `bash publish.sh`. No robot, no auto update.

## Rules for this lab
- Never push to `Realexis/cyprus-mushroom-finder` or `Realexis/shroomy`; never touch the live robots.
- Cost stays EUR 0. Ask before anything paid.
- Safety banner + 112 · Poison Centre 1401 stay on every screen.
- The phone address is **public to anyone with the link** (free GitHub Pages). noindex only keeps it out of search engines.

---

## 2026-11-27 — Step 0: lab set up
**What we did**
- Folder `shroomy-rnd/` (not `Shroomy-Lab/`: macOS ignores capitals, so it would clash with the live folder `shroomy-lab`).
- `site/` = live source from branch `lab`, commit `65c4062` (no git history).
- Map data (scores, tiles) copied from the live robot's copy, weather run **2026-11-27**. It does **not** update by itself.
- Left out on purpose: the private `data/` folder, the live robot scripts (they push to the live repos), the GitHub Actions files, and the `CNAME` file (it would try to take shroomymap.cy).
- Build flags for the lab: `VITE_NOINDEX=1` (search engines skip it), `VITE_COUNTER=off` (no visits mixed into live numbers), `VITE_PREVIEW_LABEL=Lab` (badge in the header).
- Big map files are **not** in the source branch (`main`); only the built `gh-pages` branch carries them.
- Empty folders ready: `data/finds/`, `experiments/`, `reports/`.

- Checked both addresses: map with today's colours, safety banner, 112 · 1401 button and "Lab" badge all show. Phone copy has noindex.

**Open question for Job 1:** finds on the phone copy (public link) or local only? Ask Real before publishing any find locations.

---

## 2026-11-27 — Job 1: "Past finds" layer (local only so far)
**What we did**
- `experiments/01-past-finds/fetch_finds.py`: every Cyprus fungi record (lichens included) from **iNaturalist** (place 10289 = whole island, taxon 47170 = Fungi) and **GBIF** (country CY, kingdom Fungi, with coordinates). Free APIs, no keys.
- `experiments/01-past-finds/enrich_finds.py`: adds a **group** (mushroom / lichen / other / not named, from the name's class via the GBIF name checker) and the **district** (geoBoundaries, from OpenStreetMap, ODbL). Writes `site/web/public/data/finds.json` for the map.
- Map: **Past finds** button → dots + filter panel (years range, months, groups, ▶ Play through the years). Tap a dot → card with photo, name, date, location accuracy, district, credit line, link to the original record.
- Dots: **solid** = location within 500 m · **faded** = rough or unknown location · **hollow ring** = location blurred on purpose by the source (kept blurred).

**Removed (and why)**
- 3,269 GBIF **DNA samples** from soil/sea: nobody saw a mushroom.
- 314 GBIF copies of iNaturalist records (same record twice).
- 546 near duplicates: same name, same day, within 200 m (likely several sheets or photos of one find; not checked one by one).
- 10 iNaturalist "casual" records (no date, captive or no photo).

**Result: 2,356 records, 753 names**
- Sources: iNaturalist 1,467 · GBIF 889 (herbaria such as Berlin, Madrid, Kew, Meise).
- Groups: **lichens 1,451 · mushrooms 600 · other fungi 139 · not named 166**.
- Location: good 670 · rough/unknown 1,539 · blurred 147.
- Years: 1912–2026. **82% are from 2016 on** (2020–26: 1,479). 1980–99: 282 (mostly herbarium). Before 1980: 27.
- Months (all): Jan 222 · Feb 201 · Mar 390 · Apr 326 · May 230 · Jun 97 · Jul 50 · Aug 29 · Sep 90 · Oct 85 · Nov 358 · Dec 248.
- Districts (all): Nicosia 732 · Paphos 670 · Limassol 551 · Larnaca 142 · Famagusta 103 · Kyrenia 30 · on the coast edge 128.
- **Mushrooms only (600)**: Dec 143 · Jan 114 · Nov 94 · Feb 62 · Apr 52 · Oct 45; almost none May–Aug. Districts: Nicosia 205 (incl. north Troodos) · Paphos 178 · Limassol 163.
- **Usable for Job 2** (mushroom, good location, exact day): **294**, nearly all iNaturalist 2020–26.

**Licences / photos**
- Photos are shown from their original address (not copied) **only** when the photo licence is Creative Commons or public domain: 1,144 shown. 506 more have photos at the source with "all rights reserved" or an http-only address: the card says "Photo only at the source" and links there.
- Every card shows the credit line and a link to the original record.

**Decisions**
- Finds are **not** on the phone copy and **not** in the public GitHub repo yet. `publish.sh` leaves them out unless run with `PUBLISH_FINDS=1`. Waiting for Real's answer.
- Records before 1980 (27) sit in the "before 1980" end of the year slider.

**Limits**
- Most records are lichens; only 294 mushroom records are good enough to test the map with.
- Records likely cluster where people walk (trails, picnic sites), not where mushrooms are most common (not measured yet; Job 2 will need to allow for it).
- District borders are simplified, so 128 coastal points fall "outside" any district.
