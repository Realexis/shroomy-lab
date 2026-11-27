"""Job 2: WHY does the score do what it does at the finds? Per layer (0..1) and raw weather:
finds vs random open forest on the same day, and vs the same spot on other days of the season.
Uses the same events and code as backtest.py.  Run: ... diagnose.py --group=main
"""
import json
from datetime import date

import numpy as np

import backtest as B
from shroomy.score.downscale import Interpolator
from shroomy.score.today import day_factors, water_gate


def cell_layers(w, interp, hab, rows, cols, t, on, clim):
    elev = np.nan_to_num(hab["elevation_m"][rows, cols])
    f, inp = day_factors(B.S, w, t, interp, elev, hab["altitude_band"][rows, cols].astype(int),
                         hab["shade_score"][rows, cols], on.month, clim)
    gate, rain3, _ = water_gate(B.S, interp(w["precip"][:, : t + 1]), t)
    out = {**{f"layer {k}": np.nan_to_num(v) for k, v in f.items()}, "water gate": gate,
           "rain 30 d (mm)": inp["rain_30d_mm"], "rain 7 d (mm)": inp["rain_7d_mm"], "biggest 3-day rain (mm)": rain3,
           "temp 7 d (C)": inp["t7_mean_c"], "soil percentile": np.nan_to_num(inp["soil_percentile"], nan=50),
           "altitude (m)": elev}
    out["live score"] = B.F.combine(f, B.WEIGHTS, B.tree_ok(hab, rows, cols, on)) * gate
    return out


def main():
    hab = B.habitat()
    clim = dict(np.load(B.config.PROCESSED / "weather" / "soil_climatology.npz"))
    _, events, _ = B.find_events()
    fr, fc = np.nonzero((hab["habitat_filter"] > 0) & np.isin(hab["likely_tree"], B.S["general_map_trees"]))
    pick = np.random.default_rng(7).choice(len(fr), 3000, replace=False)
    pool = (fr[pick], fc[pick])
    vs_forest, vs_days = {}, {}
    for e in events:
        e["row"], e["col"], _, _ = B.cell_of(hab, e["lon"], e["lat"])
    for season in sorted({e["season"] for e in events}):
        w = dict(np.load(B.W / f"season_{season}.npz")); dates = [str(d) for d in w["dates"]]
        ev = [e for e in events if e["season"] == season
              and B.tree_ok(hab, np.array([e["row"]]), np.array([e["col"]]), date.fromisoformat(e["date"]))[0]]
        if not ev: continue
        er = np.array([e["row"] for e in ev]); ec = np.array([e["col"] for e in ev])
        cxy = lambda r, c: np.c_[hab["transform"].c + (c + 0.5) * 250, hab["transform"].f - (r + 0.5) * 250]
        pts = np.c_[w["x"], w["y"]]
        i_ev, i_pool = Interpolator(pts, cxy(er, ec)), Interpolator(pts, cxy(*pool))
        days = [i for i, d in enumerate(dates) if d[5:7] in ("10", "11", "12", "01", "02", "03", "04") and i >= 31]
        own = {t: cell_layers(w, i_ev, hab, er, ec, t, date.fromisoformat(dates[t]), clim) for t in days}
        for k, e in enumerate(ev):
            t = dates.index(e["date"]); on = date.fromisoformat(e["date"])
            p = cell_layers(w, i_pool, hab, *pool, t, on, clim)
            for name, v in own[t].items():
                vs_forest.setdefault(name, []).append((v[k], float(np.median(p[name])), B.win(v[k], p[name])))
                vs_days.setdefault(name, []).append((v[k], float(np.median([own[u][name][k] for u in days])),
                                                     B.win(v[k], [own[u][name][k] for u in days if u != t])))
    out = {}
    print(f"{len(next(iter(vs_forest.values())))} find events inside the map's forest ({B.GROUP})")
    print(f"{'':26s}{'find':>8s}{'forest':>8s}{'win':>6s}   {'find':>8s}{'season':>8s}{'win':>6s}")
    for name in vs_forest:
        a, b = np.array(vs_forest[name]), np.array(vs_days[name])
        out[name] = dict(find=float(np.median(a[:, 0])), forest_same_day=float(np.median(a[:, 1])), win_forest=float(a[:, 2].mean()),
                         same_spot_season=float(np.median(b[:, 1])), win_days=float(b[:, 2].mean()))
        o = out[name]
        print(f"{name:26s}{o['find']:8.2f}{o['forest_same_day']:8.2f}{o['win_forest']*100:6.0f}   "
              f"{o['find']:8.2f}{o['same_spot_season']:8.2f}{o['win_days']*100:6.0f}")
    json.dump(out, open(B.LAB / f"experiments/02-backtest/diagnose_{B.GROUP}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
