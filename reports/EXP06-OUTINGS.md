# Experiment 06: "found" vs "out but found nothing" (27 Nov 2026)

**Answer: one tweak (cooler temperature band + no water gate + more shade) stops the weather part pointing the wrong way. It does not yet make it clearly good. Confidence: low–medium.**

## The idea
No one publishes "searched, found nothing". So: the 261 people who record fungi in Cyprus on iNaturalist also record plants, birds, insects. A day one of them was **in the map's forest** = an **outing**.
- **Found** = they recorded a tree-partner mushroom that day.
- **Nothing** = they recorded other things in the forest, but no mushroom.
Main test: only the **31 people who do record mushrooms** (so "nothing" likely means none seen). 67,913 public records downloaded (2022–26), Oct–Apr only.
Result: **185 outings: 25 found, 160 nothing.**

## What separates "found" from "nothing" days (win: 50% = coin toss)
| | Found | Nothing | Win |
|---|---|---|---|
| **Live score** | 37 | 39 | **48%** (37–58) → no help |
| Shade of the spot | 0.4 | 0.3 | **59%** (51–69) |
| Altitude | 735 m | 430 m | 59% (49–68) |
| Temperature, last 7 days | 11.7 °C | 13.6 °C | **39%** (29–48) → finds on **cooler** days |
| Biggest 3-day rain, last 30 days | 12.5 mm | 16.3 mm | **39%** (28–47) → finds after **smaller** rain |
| Water gate | 0.6 | 0.8 | 43% (30–49) |

**Same pattern as the back-test**, now with "nothing" days to compare. Finds come on cooler days, at shadier, higher spots, and not right after big rain.
By month: chance of a find per outing is highest **Nov–Jan (25–33%)**, lowest Oct, Mar, Apr (4–7%).

## Tweaks tested (lab only)
| Score | Outings | Back-test: vs forest same day | Back-test: vs same spot, other days |
|---|---|---|---|
| Live | 48% | 41% | 44% |
| No water gate | 56% | 44% | 48% |
| Cooler band (best 6–13 °C instead of 8–18) | 51% | — | — |
| **Cooler + no gate + 2× shade** | **61%** | **51%** | **52%** |
(Back-test columns = main group, finds inside the lab forest. The tweak's gains there are beyond the noise.)

- On the **seasons held back** (2025–26, only 7 finds): 58% vs 55% live. Too few to confirm.
- On **all mushrooms** in the back-test: smaller gain (+1 to +5 points).

## Honest limits
- 25 "found" outings. People may not look for mushrooms on every outing.
- The tweak was chosen on the same data it is tested on (except 2025–26). It **removes harm**; it does not prove the weather part works.
- Why big rain goes with *fewer* finds is not known. Perhaps the 9 km weather model, or people stay home in wet weeks.

Scripts: `experiments/06-effort/` (fetch_effort, outings). The downloaded records stay on this Mac (not published). Nothing changed on the live site.
