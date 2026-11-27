"""Experiment 03: WHEN does rain matter for finds? (Back-test recommendation 1.)

Step 1 — timing curve: rain in 10-day steps (0-10, 10-20 ... 50-60 days before) at each find's square,
vs (A) random open forest the same day and (C) the same square on other days (1 Nov - 30 Apr).
Win rate 50% = rain in that step tells nothing; above 50% = finds follow more rain in that step.

Step 2 — a few re-timed scores (rain total and water gate moved / softened), everything else live.
To avoid fooling ourselves, each variant is also checked on seasons it was NOT chosen on:
pick on 2022-24, check on 2025-26.

Finds: same events as the back-test (experiments/02-backtest/backtest.py), only 1 Nov - 30 Apr
(weather starts 31 Aug, so October finds lack 60 days of rain), only finds inside the map's forest.
Run: site/pipeline/.venv/bin/python experiments/03-rain-timing/rain_timing.py --group=main
"""
import json, sys
from datetime import date
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "experiments/02-backtest"))
import backtest as B                                           # noqa: E402
from shroomy.score.downscale import Interpolator              # noqa: E402
from shroomy.score.today import day_factors                   # noqa: E402

F, S = B.F, B.S
STEPS = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60)]
MIN_T = 62                                                       # 31 Aug + 62 days = 1 Nov


def gate_from(cell_p, t, full_at, days=30, full_until=20, skip=0):
    """The live water gate, with its soak amount, look-back and start (skip = ignore the last N days) changeable."""
    p = cell_p[:, : t + 1 - skip] if skip else cell_p
    faded, _, _ = F.recent_soak(p, p.shape[1] - 1, days, S["rain_pulse"]["window_days"],
                                S["mushroom_clock"]["wet_day_mm"], full_until)
    return np.clip(faded / full_at, 0, 1) if full_at else np.ones(len(cell_p))


def rain_window(cell_p, t, a, b):
    return cell_p[:, t - b + 1: t - a + 1].sum(axis=1)


VARIANTS = {
    "live (rain 0-30 d, gate 20 mm)":            dict(rt=(0, 30), gate=20),
    "gate 10 mm":                                 dict(rt=(0, 30), gate=10),
    "no gate":                                    dict(rt=(0, 30), gate=0),
    "rain 15-45 d, gate 20 mm":                   dict(rt=(15, 45), gate=20),
    "rain 30-60 d, gate 20 mm":                   dict(rt=(30, 60), gate=20),
    "rain 0-60 d (2x mm), gate 20 mm":            dict(rt=(0, 60), gate=20, rt_scale=2),
    "rain 30-60 d, gate 10 mm over 60 d":         dict(rt=(30, 60), gate=10, gate_days=60, gate_full=45),
}


def scores(f, cell_p, t, ok, v):
    f = dict(f)
    a, b = v["rt"]
    k = v.get("rt_scale", 1)
    f["rain_total"] = F.ramp(rain_window(cell_p, t, a, b), 20 * k, 80 * k)
    g = gate_from(cell_p, t, v["gate"], v.get("gate_days", 30), v.get("gate_full", 20))
    return F.combine(f, B.WEIGHTS, ok) * g


def main():
    hab = B.habitat()
    clim = dict(np.load(B.config.PROCESSED / "weather" / "soil_climatology.npz"))
    _, events, _ = B.find_events()
    fr, fc = np.nonzero((hab["habitat_filter"] > 0) & np.isin(hab["likely_tree"], S["general_map_trees"]))
    pick = np.random.default_rng(11).choice(len(fr), 3000, replace=False)
    pool = (fr[pick], fc[pick])
    curve = {s: {"A": [], "C": []} for s in STEPS}
    res = {v: {"A": [], "C": [], "season": []} for v in VARIANTS}
    used = []
    for e in events:
        e["row"], e["col"], _, _ = B.cell_of(hab, e["lon"], e["lat"])
    for season in sorted({e["season"] for e in events}):
        w = dict(np.load(B.W / f"season_{season}.npz")); dates = [str(d) for d in w["dates"]]
        ev = [e for e in events if e["season"] == season and e["date"] in dates and dates.index(e["date"]) >= MIN_T
              and B.tree_ok(hab, np.array([e["row"]]), np.array([e["col"]]), date.fromisoformat(e["date"]))[0]]
        if not ev: continue
        er = np.array([e["row"] for e in ev]); ec = np.array([e["col"] for e in ev])
        cxy = lambda r, c: np.c_[hab["transform"].c + (c + 0.5) * 250, hab["transform"].f - (r + 0.5) * 250]
        pts = np.c_[w["x"], w["y"]]
        i_ev, i_pool = Interpolator(pts, cxy(er, ec)), Interpolator(pts, cxy(*pool))
        p_ev, p_pool = i_ev(w["precip"]), i_pool(w["precip"])       # daily rain per square, whole season
        days = [i for i, d in enumerate(dates) if i >= MIN_T and d[5:7] in ("11", "12", "01", "02", "03", "04")]

        def all_scores(interp, rows, cols, pc, t):
            on = date.fromisoformat(dates[t])
            f, _ = day_factors(S, w, t, interp, np.nan_to_num(hab["elevation_m"][rows, cols]),
                               hab["altitude_band"][rows, cols].astype(int), hab["shade_score"][rows, cols], on.month, clim)
            ok = B.tree_ok(hab, rows, cols, on)
            return {v: scores(f, pc[:, : t + 1], t, ok, VARIANTS[v]) for v in VARIANTS}

        own = {t: all_scores(i_ev, er, ec, p_ev, t) for t in days}
        for k, e in enumerate(ev):
            t = dates.index(e["date"])
            used.append(dict(date=e["date"], names=sorted(e["names"])))
            for s in STEPS:
                x = rain_window(p_ev[k:k + 1], t, *s)[0]
                curve[s]["A"].append(B.win(x, rain_window(p_pool, t, *s)))
                curve[s]["C"].append(B.win(x, [rain_window(p_ev[k:k + 1], u, *s)[0] for u in days if u != t]))
            sp = all_scores(i_pool, *pool, p_pool, t)
            for v in VARIANTS:
                res[v]["A"].append(B.win(own[t][v][k], sp[v]))
                res[v]["C"].append(B.win(own[t][v][k], [own[u][v][k] for u in days if u != t]))
                res[v]["season"].append(season)

    n = len(used)
    print(f"[{B.GROUP}] {n} find events inside the map's forest, 1 Nov - 30 Apr\n")
    print("Step 1: rain in each 10-day step before the find (win %, 95% range)")
    print(f"{'days before':14s}{'A vs forest, same day':>26s}{'C vs same spot, other days':>30s}")
    out = {"events": n, "curve": {}, "variants": {}}
    for s in STEPS:
        a, c = B.boot(curve[s]["A"]), B.boot(curve[s]["C"])
        out["curve"][f"{s[0]}-{s[1]}"] = dict(A=a, C=c)
        print(f"{s[0]:>3d}-{s[1]:<3d} days    {a[0]*100:6.0f} ({a[1]*100:3.0f}-{a[2]*100:3.0f}){'':10s}{c[0]*100:6.0f} ({c[1]*100:3.0f}-{c[2]*100:3.0f})")
    print("\nStep 2: re-timed scores (win %) — all seasons | chosen on 2022-24 | checked on 2025-26")
    for v in VARIANTS:
        r = res[v]; seas = np.array(r["season"])
        row = {}
        for test in ("A", "C"):
            vals = np.array(r[test])
            row[test] = dict(all=B.boot(vals), early=float(vals[seas <= 2024].mean()) if (seas <= 2024).any() else None,
                             late=float(vals[seas >= 2025].mean()) if (seas >= 2025).any() else None,
                             diff=B.boot_diff(vals, res["live (rain 0-30 d, gate 20 mm)"][test]))
        out["variants"][v] = row
        fmt = lambda x: f"{x*100:4.0f}" if x is not None else "   -"
        print(f"{v:38s} A {row['A']['all'][0]*100:4.0f} ({row['A']['diff'][0]*100:+3.0f}) |{fmt(row['A']['early'])} |{fmt(row['A']['late'])}"
              f"    C {row['C']['all'][0]*100:4.0f} ({row['C']['diff'][0]*100:+3.0f}) |{fmt(row['C']['early'])} |{fmt(row['C']['late'])}")
    print(f"\nevents per season group: 2022-24 = {int((seas <= 2024).sum())}, 2025-26 = {int((seas >= 2025).sum())}")
    out["events_list"] = used
    json.dump(out, open(LAB / f"experiments/03-rain-timing/results_{B.GROUP}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
