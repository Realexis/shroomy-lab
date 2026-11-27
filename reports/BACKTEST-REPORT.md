# Back-test: does Shroomy predict real finds? (27 Nov 2026)

**Does it work? Partly. The forest part works well; the weather part does not yet pick the right days or the right spots inside the forest.**

**What was tested.** 45 tree-partner mushroom finds + target species (= **36 find events**, seasons 2022–26), rebuilt with the live scoring code and the live weather model. Groups agreed in `reports/backtest-groups.md`.
**Win rate** = how often a find scores higher than a random comparison. **50% = a coin toss**, 100% = always higher.

| Test (main group) | All 36 events | 24 events inside the map's forest |
|---|---|---|
| Find vs **random land**, same day | **69%** (61–76) | **84%** (82–87) |
| Find vs **random forest**, same day | 27% (19–36) | 40% (31–50) |
| Find vs **same spot, other days** | 45% (38–52) | 43% (33–53) |

(Brackets = 95% range. 12 of 36 events score 0 because they sit outside the map's forest.)

## What helps · what to remove · what to replace
- **Helps a lot: the forest/habitat filter.** Switch it off and the win vs random land drops from 69% to 47%. *Confidence: high.*
- **Helps a little: shade** and **soil moisture** (removing either lowers the win by up to 2 points; just above the noise). *Confidence: low.*
- **Does nothing (yet): rain total, rain pulse, temperature, season × altitude.** Removing any one changes the win by 0–2 points, inside the noise; removing temperature even helps a little. Temperature scores 1.0 (perfect) on almost every winter day, so it cannot tell days apart. *Confidence: medium.*
- **May make it worse: the water gate.** Finds came on days with *less* recent big rain than usual (biggest 3-day rain 12 mm vs 17 mm on other days). Removing the gate raises the win by 2–4 points, inside the noise. *Confidence: low.*
- **Replace the 2018 forest with WorldCover 2021? No.** It also holds only 24 of 36 finds and marks more non-forest land as forest (win vs land inside forest: 76% instead of 84%). Keep 2018 + the fire layer. *Confidence: medium.*
- **"Habitat × weather" (multiply)? No gain.** Same results (within 1.5 points), because the score already multiplies by the forest filter and the water gate. *Confidence: medium.*

## Top 3 recommended changes (lab experiments first, nothing live yet)
1. **Re-time the rain.** Test the rain 30–60 days before (not only 0–30), and a smaller "soaking" rain than 20 mm. Finds come later or after smaller rain than the gate expects. *Confidence: low–medium.*
2. **Make temperature tell days apart.** The 8–18 °C "best" band is met nearly all winter. Finds were cooler than random forest the same day (11.6 vs 12.7 °C; win 35%). Test a narrower band or cooler peak. *Confidence: low.*
3. **Fix the forest edges.** Of the 12 finds outside the map's forest: 7 sit in squares with under 25% forest (most are pine partners: Suillus, Pisolithus, Lactarius), 3 in "other broadleaf" squares, 2 in closed reserves (correct). Test a lower forest threshold near pine, and which "other broadleaf" squares hold pine. *Confidence: low–medium.*

## Side results (LOW confidence, small numbers)
- **Target species alone** (Suillus, *Lactarius deliciosus*, Morchella; 12 events): vs land 67%, vs forest 20%, vs other days 41%. Same pattern, too few to judge.
- **Ground decomposers** (Agaricus, puffballs…; 64 events, 26 inside forest): vs forest 54%, vs other days 59%. Weather fits them slightly better.
- **Spot within 2 km instead of 500 m:** only 1 more event; no change.
- **Season:** one peak, Oct–Jan. Only **Morchella** is a real spring mushroom (6 of 7 records Feb–May).

## Honest limits
36 events can catch a clearly wrong part, not prove a model. Weather is a 9 km model, not the rain at the spot. Finds show where people walk, not where mushrooms are most common. No find data before 2022 for the live weather model.

*Footnote — every mushroom record (156 events): vs land 64%, vs forest 28%, vs other days 51%; inside the map's forest: 87%, 50%, 53%.*
