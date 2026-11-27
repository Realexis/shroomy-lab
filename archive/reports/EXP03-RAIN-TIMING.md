# Experiment 03: re-time the rain (27 Nov 2026)

**Answer: no rain timing we tried makes the score pick finds better. Don't change the rain part on this evidence.**

**Test.** Same finds as the back-test, only 1 Nov–30 Apr and inside the map's forest: **23 events** (main group) and **78** (every mushroom, as a bigger check). Weather from the live model.
Win rate: 50% = a coin toss.

## 1. When does rain matter? (rain in each 10-day step before the find)

| Days before | Main: vs forest same day | Main: vs same spot other days | All mushrooms: vs forest | All: vs other days |
|---|---|---|---|---|
| 0–10 | 45% | 44% | 48% | 49% |
| 10–20 | 49% | 47% | 50% | 48% |
| 20–30 | 42% | 46% | 49% | 47% |
| 30–40 | 49% | 56% | 52% | 51% |
| 40–50 | 52% | 50% | 55% | 45% |
| 50–60 | 48% | 44% | 51% | 48% |

Every 95% range includes 50%. **No 10-day step stands out.** Finds did not follow more rain than random forest or other days, at any delay up to 60 days.

## 2. Re-timed scores (everything else as live)

| Variant | Main: vs forest | Main: vs other days | All: vs forest | All: vs other days |
|---|---|---|---|---|
| Live (rain 0–30 days, gate 20 mm) | 39% | 40% | 50% | 48% |
| Gate 10 mm | 41% | 43% | 49% | 49% |
| No gate | 42% | 43% | 46% | 48% |
| Rain 15–45 days | 39% | 41% | 49% | 47% |
| Rain 30–60 days | 40% | 43% | 50% | 47% |
| Rain 0–60 days | 39% | 41% | 49% | 47% |
| Rain 30–60 days + gate 10 mm over 60 days | **46%** | **44%** | 51% | 49% |

- The best one (last row) gains 5–7 points on the main group, but **not** on the check seasons it was not chosen on (2025–26: 53% vs live 58% against forest), and **not** on all mushrooms (+1). That is noise, not a fix.
- *Confidence that rain re-timing will not help with this data: medium.*

## What it means
- With these finds and a 9 km weather model, **the weather signal is too weak to see**. Possible reasons, not tested: the model misses local rain; people record finds when they go out (weekends, holidays), not when mushrooms first appear; finds are spread over the whole wet season.
- The part that clearly works is **where** (the forest filter). Better gains are likely there: **recommendation 3, forest edges**, next.
- Better weather tuning needs **better find data**: dated finds with exact spots *and* "searched, found nothing" days. The site's private finds log could collect that later (Real's call).

Script: `experiments/03-rain-timing/rain_timing.py` (`--group=main` / `--group=all`). Nothing changed on the live site or in its scoring.
