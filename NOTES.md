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

## 2026-11-27 — Job 1: "Past finds" layer (local + phone copy)
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
- **Real, 27 Nov: yes, finds on the phone copy.** Published with `PUBLISH_FINDS=1 bash publish.sh` (the built `gh-pages` branch carries `data/finds.json`). Checked online: all 2,356 records load. The source branch `main` still keeps `data/finds/` out of git (rebuild with the two scripts). Always publish with `PUBLISH_FINDS=1` from now on, or the finds drop off the phone copy.
- Records before 1980 (27) sit in the "before 1980" end of the year slider.

**Limits**
- Most records are lichens; only 294 mushroom records are good enough to test the map with.
- Records likely cluster where people walk (trails, picnic sites), not where mushrooms are most common (not measured yet; Job 2 will need to allow for it).
- District borders are simplified, so 128 coastal points fall "outside" any district.

---

## 2026-11-27 — Job 2 PREVIEW (low confidence, 1 season only)
- Asked by Real mid-download. Weather ready for season 2022-23 only → **12 find events** (7 inside the map's forest).
- Finds beat random land squares 63% of the time (inside the map's forest: 82%) → the forest/habitat filter does the work.
- Finds did **not** beat random forest squares on the same day (20%; inside forest 33%) or their own spot on other days (35% / 25%).
- 9 of 12 events are April 2023 (spring); 5 of 12 sit outside the map's forest (incl. a *Suillus*, a pine partner, scored 0).
- "Mushroom" group includes brackets on wood (*Laetiporus*, *Phellinus*), which may not follow rain the same way.
- Nothing changed in the scoring or layers. Full test follows when the download ends.

---

## 2026-11-27 — Job 2: back-test done → `reports/BACKTEST-REPORT.md`
**What we did**
- Past weather from the **live model** (ECMWF IFS 9 km, Open-Meteo historical forecast), 128 points (0.1°), seasons 2022–26. 3,880 calls, paced ≤1,500/hour so the live robot's allowance stayed safe.
- Groups agreed with Real (`reports/backtest-groups.md`): **main** = tree-partner mushrooms + target species (45 finds → 36 events). Side: target species (12 events), ground decomposers (64), spot within 2 km (37), all mushrooms (156, footnote).
- Each find vs random land (same day), random open forest (same day), same spot on other days. Variants: each layer off, no gate, no habitat filter, other broadleaf counted, WorldCover 2021 forest, habitat × weather.
- Fires count only if they burned **before** the find (the live code marks all fires since 2018; fine for today's map, wrong for the past).
- Scripts: `experiments/02-backtest/` (fetch_weather, worldcover, backtest, diagnose).

**Result (main group)**
- Forest part works: finds beat random land 69% (inside the map's forest 84%).
- Weather part does not (yet): vs random forest 27% / 40%, vs other days 45% / 43% (50% = coin toss).
- Temperature is 1.0 on almost every winter day → tells nothing. Water gate is lower on find days (0.59 vs 0.77).
- WorldCover 2021: no better (same 24/36 finds inside, more non-forest land marked forest). Habitat × weather: no change.
- 12 of 36 events outside the map's forest: 7 in squares <25% forest, 3 "other broadleaf", 2 closed reserves.

**Decisions**: none yet. Nothing changed in the live site or its scoring. Next ideas (Real decides): re-time rain (30–60 days, smaller soak), narrower temperature band, forest edges.

---

## 2026-11-27 — Experiment 03: re-time the rain → `reports/EXP03-RAIN-TIMING.md`
- Real: "whatever you like" → started with back-test recommendation 1.
- 23 events (main group, Nov–Apr, inside the map's forest) + 78 (all mushrooms) as a check.
- Rain in 10-day steps 0–60 days before: **no step beats 50%** (all ranges include 50%).
- 6 re-timed scores: best (rain 30–60 d + gate 10 mm over 60 d) +5–7 points on the main group, but not on held-back seasons 2025–26 and not on all mushrooms → noise.
- **Decision: don't change the rain part.** Weather signal too weak to see with this data. Next: forest edges (recommendation 3).
- Idea for later (Real's call): collect dated finds + "searched, nothing" days to tune weather properly.

---

## 2026-11-27 — Experiment 04: forest edges → `reports/EXP04-FOREST-EDGES.md`
- Finds from all years (exact spot), no weather. Main group 45 events, target 16, all mushrooms 209, ground 86.
- Live forest catches 64% of main finds on 25.8% of the land (lift 2.5).
- **"15% forest if mostly pine"**: 71% caught for +190 km² (lift stays 2.5); target species 69% → 81%. Best trade-off. Low confidence (2–3 finds).
- Edges (250 / 500 m) and WorldCover catch a few more but mark ~1,000–1,500 km² more land → map less sharp. Not recommended.
- Other broadleaf: +3 main finds for +340 km², no target gain. Not now.
- **Decision: none yet.** Possible next step (Real's call): show "15% if mostly pine" on the lab map to look at the new squares.
- **Pine 15% button** on the lab map (local + phone copy, 27 Nov): shows the 3,040 squares (190 km²) the rule would add, in bright blue, with a note. Lab only; not in the score. Real to look and decide.
