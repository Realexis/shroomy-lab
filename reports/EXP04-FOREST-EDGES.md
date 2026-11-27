# Experiment 04: forest edges (27 Nov 2026)

**Answer: one small change looks worth it: also count squares with 15%+ forest when it is mostly pine. It catches a few more finds for very little extra land. Low confidence: the gain is 2–3 finds.**

**Test.** No weather needed, so finds from **all years** count (exact spot within 500 m). For each way of drawing the map's forest:
- **caught** = share of find events inside it (closed reserves count as not caught, as on the map)
- **land** = share of Cyprus land it marks
- **lift** = caught ÷ land: how much sharper than marking land at random (higher = better)

## Main group (tree-partner mushrooms + target species): 45 events

| Forest drawn as | Caught | Land | Lift | Extra land |
|---|---|---|---|---|
| **Live** (25% forest, pine / oak) | 29 = 64% | 25.8% | 2.5 | — |
| + other broadleaf | 32 = 71% | 29.5% | 2.4 | +340 km² |
| **15% forest if mostly pine** | **32 = 71%** | **27.9%** | **2.5** | **+190 km²** |
| 10% forest if mostly pine | 32 = 71% | 29.0% | 2.4 | +296 km² |
| + 250 m edge around forest | 32 = 71% | 36.4% | 2.0 | +969 km² |
| + 500 m edge around forest | 33 = 73% | 42.5% | 1.7 | +1,535 km² |
| + WorldCover 2021 trees | 36 = 80% | 37.5% | 2.1 | +1,074 km² |

(95% range for "caught" is about ±15 points for every row, so the rows overlap.)

## Checks with other groups
- **Target species alone (16 events):** live 69% → **81% with "15% if mostly pine"** (lift 2.7 → 2.9, the best row). Other broadleaf adds nothing here.
- **All mushrooms (209 events):** live 51% → 54%. WorldCover catches most (69%) but marks 1,074 km² more land.
- **Ground decomposers (86 events):** only 36% inside the live forest; they grow in fields and parks too, as expected.

## What it means
- **"15% forest if mostly pine"** catches 3 more main finds and 2 more target finds for +190 km² (+7% more land) and keeps the lift. *Confidence: low* (2–3 finds; ranges overlap).
- **Edges (250 / 500 m) and WorldCover** catch a few more but mark far more land, so the map gets less sharp. *Not recommended. Confidence: medium.*
- **Other broadleaf:** +3 main finds for +340 km², no gain for target species. *Not recommended for now. Confidence: low.*
- 2 of 45 main events are in **closed reserves**: correct, the map leaves them out on purpose.

**Recommendation for later (Real's call; nothing goes live without your OK):** try "15% forest if mostly pine" on the lab map and look at where the new squares fall before deciding.

Script: `experiments/04-forest-edges/forest_edges.py` (`--group=main / target / all / ground`). Nothing changed on the live site or in its scoring.
