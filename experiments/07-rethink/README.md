# Experiment 07: rethink (27 Nov 2026)

One contest of the candidate changes on every test we have, existing data only (no new downloads).

Runs (logs in `logs/`, re-made with these commands from `experiments/02-backtest` and `experiments/06-effort`):
- Back-test, main group, live forest:   `backtest.py --group=main --habitat=live` (and `--late` = held-back 2025–26 only)
- Back-test, main group, lab forest (15% pine): `backtest.py --group=main` (and `--late`)
- Outings found vs nothing: `outings.py --habitat=live` / `outings.py` (lab forest)

New variant: **"areas only (season + shade)"** = the live formula with rain total, rain burst, temperature and soil moisture set to 0 and no water gate. Only season × altitude and shade are left.

Summary and ranking: `reports/RETHINK-SUMMARY.md`.
