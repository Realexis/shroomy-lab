# Shroomy LAB: what we learned, what we keep, what to change (27 Nov 2026)

**Main point: the map knows WHERE, not WHEN. A simpler "best areas this season" score did as well as or better than today's daily score in almost every test. Nothing is changed on the live site.**

## What we learned
- **Where works.** Real finds land in the map's forest far more often than chance (69% vs random land; 84% for finds inside the forest; 50% = coin toss).
- **When doesn't.** The daily weather part could not pick the right day or spot (41–48%). Re-timing the rain didn't help.
- **Cool, shady, higher spots** had more finds. So did **Nov–Jan** (morels in spring). Most finds were pine partners (*Suillus*, *Lactarius*).

## Keep / drop / unsure (one line each)
**Map layers**
- **Forest 2018 (Copernicus):** KEEP. It is the part that works.
- **Pine / oak partner-tree rule:** KEEP. Adding "other broadleaf": +3 finds for +340 km², no gain for target species.
- **Closed nature reserves:** KEEP. The law; 2 finds there, correctly left out.
- **Burned forest (EFFIS):** KEEP. The logic is sound; too few burned finds to test.
- **Shade:** KEEP. It helped in every test.
- **Season × altitude:** KEEP. It matches the Nov–Jan peak; the core of "best areas".
- **15% pine squares (lab only):** UNSURE. +3 of 45 finds caught for +190 km²; other tests barely move.
- **Temperature (8–18 °C best):** UNSURE. Useless as set (perfect nearly all winter); a cooler band helps a little.
- **Rain 30 days / rain burst:** UNSURE. No effect in any test; dropping them didn't hurt.
- **Soil moisture:** UNSURE. Tiny help in one test, none in another.
- **Water gate:** DROP candidate. No help or harm in every test (removing it: +2 to +8 points).
- **WorldCover 2021 forest:** DROP. No better than 2018, marks more non-forest land. (Archived.)

**Data sources**
- **iNaturalist finds, exact spot + date:** KEEP. The main test data.
- **GBIF herbarium records:** KEEP for the Past finds layer and season, not for day tests (mostly old, rough spots).
- **GBIF DNA samples from soil and sea:** DROP. Not mushrooms anyone saw.
- **Lichens, wood fungi, moulds, field decomposers:** DROP from the tests. They grow differently.
- **"Out but found nothing" outings (iNaturalist):** KEEP. Our only "nothing" days.
- **Past weather, live model 2022–26:** KEEP. Needed to re-run tests, no new calls.
- **Mushroom Observer, Observation.org, bolete paper:** DROP. Nothing usable.

## Top 3 changes, tested (live forest map; win rate, 50% = coin toss)
| Score | Finds vs random forest, same day | vs random land | vs same spot, other days | Found vs nothing outings | Outings, held-back 2025–26 |
|---|---|---|---|---|---|
| Live today | 40% | 84% | 43% | 46% | 49% |
| **1. Best areas this season** (season × altitude + shade; no daily weather) | **54%** | **88%** | 49% | **61%** | **67%** |
| 2. Cooler band + no gate + 2× shade | 50% | 87% | **51%** | 59% | 52% |
(First three columns: 24 finds inside the forest. Outings: 172 outings, 24 found; held-back: 6 found.)

1. **Show "best areas this season" as the main map**, with recent weather as a simple note only (e.g. "soaking rain in the last weeks: yes / no"), not in the colours. It's simpler and more honest. *Confidence: low–medium.* Best or equal-best on most tests, but on the held-back finds (6–7) it is mixed: better at picking days, worse at picking spots.
2. **If you keep a daily score:** cooler best band (6–13 °C), no water gate, 2× shade. Better than today in every test. *Confidence: low–medium.*
3. **Keep the 15% pine squares in the lab** and watch them this season. *Confidence: low* (a gain of 3 finds).

**No change:** rain timing, WorldCover, other broadleaf, habitat × weather. The evidence didn't show they make the map better.

## Limits
36 find events and 24–25 "found" outings. 9 km weather. Finds cluster where people walk (Troodos trails are high and shady, so part of the "higher, shadier" result may be where people go). Every change stays in the lab until you say so.

Details: `experiments/07-rethink/` (runs and logs), `NOTES.md`, `archive/README.md`.
