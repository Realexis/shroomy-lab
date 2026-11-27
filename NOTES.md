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

**Open question for Job 1:** finds on the phone copy (public link) or local only? Ask Real before publishing any find locations.
