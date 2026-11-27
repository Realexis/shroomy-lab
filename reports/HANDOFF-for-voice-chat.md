# Shroomy LAB — hand-over for a voice chat (27 Nov 2026)

## Who and what
- I'm Real. I'm dyslexic: please keep answers short, main point first, plain words.
- **ShroomyMap** (shroomymap.cy) is my live website: a phone map of mushroom **growing conditions** in Cyprus forests. It does **not** show where mushrooms are.
- Every screen has a safety banner: "Conditions only. Never eat a wild mushroom based on this map, an app or an AI." Emergency 112, Poison Centre 1401.
- How the score works today: each 250 m forest square gets a daily score from 0 to 100. Six layers are added up: rain over 30 days, a recent rain burst, temperature, soil moisture, season × altitude, and shade. Then it is multiplied by a "forest yes/no" filter and a "water gate" (no soaking rain of 20 mm or more = low score).

## The lab (built today)
- A separate copy of the site for experiments. **Nothing goes live without my OK.**
- Phone address: https://realexis.github.io/shroomy-lab/ (public to anyone with the link, hidden from search engines).
- On my Mac: folder `shroomy-rnd`. Start it with `bash ~/Desktop/WORK/Claude_Code/shroomy-rnd/start.sh`.
- Extra buttons on the lab map:
  - **Past finds**: 2,356 public fungi records from iNaturalist and GBIF, with photos, credits, year/month filters and a Play button.
  - **Pine 15%**: shows the new pine squares added in the lab.
- Cost so far: EUR 0.

## What we tested, and what we found
1. **Past finds.** 2,356 records. Mostly lichens; 600 mushrooms. Mushroom finds peak **November to January**. Only morels are a real spring mushroom.
2. **Back-test**: would the map have scored real finds higher than random spots? I tested it on 36 find events from 2022 to 2026, using the live map's own code and weather model.
   - **The forest part works.** Finds land in the map's forest far more often than chance (69%, and 84% for finds inside the forest; 50% = a coin toss).
   - **The weather part does not work yet.** It can't pick the right day, or the right spot inside the forest (41–45%, about a coin toss or worse).
   - Temperature is "perfect" nearly all winter, so it tells nothing. The water gate may even hurt.
   - The newer ESA WorldCover 2021 forest map is no better than the 2018 one. Multiplying habitat × weather gives no gain.
3. **Re-timing the rain** (up to 60 days back, smaller soaking rain): **no gain.** Don't change the rain part on this evidence.
4. **Forest edges:** adding squares with **15%+ forest that is mostly pine** catches a few more finds for only +190 km² of land. **This is now in the lab score** (3,040 squares). Low confidence: the gain is 2–3 finds.
5. **"Found" vs "out but found nothing" days.** Nobody publishes empty days, so I used iNaturalist: days when mushroom recorders were in the forest recording other things but logged no mushroom. That gave 185 outings: 25 found, 160 nothing.
   - The live score can't tell them apart (48%).
   - Found days were **cooler** (11.7 vs 13.6 °C), at **shadier and higher** spots, and came after **smaller** rain.
   - A tweak lifts the result to **51–61%**: a cooler best temperature band (6–13 °C instead of 8–18), **no water gate**, and **2× shade**. It stops the weather part pointing the wrong way, but it doesn't prove the weather part works. Confidence: low–medium.

## Honest limits
- Very few good records: 36 find events, 25 "found" outings.
- The weather model works in 9 km squares, so it misses the rain at the exact spot.
- People record finds when they go out (weekends), not when mushrooms first appear.
- I looked for more data and found nothing useful. Mushroom Observer has 15 old records, Observation.org 3, and a bolete research paper has no dated records.

## Decisions waiting for me
1. Put the tweak (cooler band, no water gate, 2× shade) into the **lab** score? It's only a test.
2. Later: should any lab change (15% pine squares, the tweak) go to the **live** site? Only with my OK.
3. Should the site start collecting **my own and visitors' finds AND empty search days** (a private finds log)? That's the data needed to really tune the weather part.

## Ideas for next steps
- Add the tweak to the lab map and watch it through this season. Compare it with the live map and with new finds as they come in.
- Re-run the tests each month as new iNaturalist records arrive. The scripts are ready, and the cost is EUR 0.
- Design a simple "I searched here: found / found nothing" button for the site. Privacy: keep exact spots private.
- Ask local mushroom groups or the Cyprus Mycological Association for dated records, with their permission.

## Rules to keep
- Never change the live site, its repos or its daily robot from the lab.
- Ask before anything that costs money.
- Never say a mushroom is safe to eat, and never call it a "mushroom map".
- The free weather service is shared with the live robot: keep the lab's use small.
- All notes and reports are in `shroomy-rnd/NOTES.md` and `shroomy-rnd/reports/`.
