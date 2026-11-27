"""Experiment 06, step 2: does the score tell "found" outings from "out but found nothing" outings?

OUTING = one person, one day, at least one observation (exact spot within 500 m, not blurred) inside
the map's forest, 1 Oct - 30 Apr, seasons 2022-26 (the years we have the live model's weather for).
FOUND = that person recorded a main-group mushroom (reports/backtest-groups.md) that day.
NOTHING = they recorded other living things in the forest that day, but no main-group mushroom.

Main test: only people who HAVE recorded a main-group mushroom at least once (so they do record them).
Side test: every fungi recorder.
For every outing: the live score (and each layer) of its forest square on its day, rebuilt exactly as
in the back-test. Win rate = chance a FOUND outing scores higher than a NOTHING outing (50% = coin toss),
overall and within the same calendar month (takes the season out). 95% ranges from re-sampling people.
Run: site/pipeline/.venv/bin/python experiments/06-effort/outings.py
"""
import json, sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "experiments/02-backtest"))
import backtest as B                                           # noqa: E402
from shroomy.score.downscale import Interpolator              # noqa: E402
from shroomy.score.today import day_factors, water_gate       # noqa: E402

RNG = np.random.default_rng(6)
MONTHS = {10, 11, 12, 1, 2, 3, 4}


def is_main(name):
    return (name or "").split(" ")[0] in B.KEEP


def build_outings(hab):
    eff = json.load(open(LAB / "data/finds/raw/effort.json"))
    recorders = {e["u"] for e in eff if is_main(e["name"])}
    # earlier main-group recorders too (records before Sep 2022)
    for o in json.load(open(LAB / "data/finds/raw/inat.json")):
        if is_main((o.get("taxon") or {}).get("name")): recorders.add(o["user"]["id"])
    by = defaultdict(list)
    for e in eff:
        d = date.fromisoformat(e["d"])
        if d.month not in MONTHS or e["obs"] or e["acc"] is None or e["acc"] > 500: continue
        by[(e["u"], e["d"])].append(e)
    outs = []
    for (u, d), obs in by.items():
        on = date.fromisoformat(d)
        season = on.year if on.month >= 8 else on.year - 1
        if season < 2022: continue
        cells = []
        for e in obs:
            r, c, _, _ = B.cell_of(hab, e["lon"], e["lat"])
            if 0 <= r < hab["land_fraction"].shape[0] and 0 <= c < hab["land_fraction"].shape[1] \
                    and B.tree_ok(hab, np.array([r]), np.array([c]), on)[0]:
                cells.append((r, c, is_main(e["name"])))
        if not cells: continue
        found = [x for x in cells if x[2]]
        r, c, _ = found[0] if found else cells[0]      # the find's square, else the first forest square
        outs.append(dict(u=u, date=d, season=season, row=r, col=c, found=bool(found), recorder=u in recorders,
                         n_obs=len(obs)))
    return outs


def main():
    hab = B.habitat()
    clim = dict(np.load(B.config.PROCESSED / "weather" / "soil_climatology.npz"))
    outs = build_outings(hab)
    for season in sorted({o["season"] for o in outs}):
        w = dict(np.load(B.W / f"season_{season}.npz")); dates = [str(d) for d in w["dates"]]
        so = [o for o in outs if o["season"] == season and o["date"] in dates and dates.index(o["date"]) >= 31]
        if not so: continue
        rr = np.array([o["row"] for o in so]); cc = np.array([o["col"] for o in so])
        cxy = np.c_[hab["transform"].c + (cc + 0.5) * 250, hab["transform"].f - (rr + 0.5) * 250]
        interp_all = Interpolator(np.c_[w["x"], w["y"]], cxy)
        for t in sorted({dates.index(o["date"]) for o in so}):
            idx = [k for k, o in enumerate(so) if dates.index(o["date"]) == t]
            on = date.fromisoformat(dates[t])
            sub = Interpolator(np.c_[w["x"], w["y"]], cxy[idx])
            f, inp = day_factors(B.S, w, t, sub, np.nan_to_num(hab["elevation_m"][rr[idx], cc[idx]]),
                                 hab["altitude_band"][rr[idx], cc[idx]].astype(int), hab["shade_score"][rr[idx], cc[idx]], on.month, clim)
            gate, rain3, _ = water_gate(B.S, sub(w["precip"][:, : t + 1]), t)
            ok = B.tree_ok(hab, rr[idx], cc[idx], on)
            live = B.F.combine(f, B.WEIGHTS, ok) * gate
            for j, k in enumerate(idx):
                so[k]["v"] = {"live score": float(live[j]), **{f"layer {n}": float(np.nan_to_num(f[n][j])) for n in f},
                              "water gate": float(gate[j]), "rain 30 d (mm)": float(inp["rain_30d_mm"][j]),
                              "biggest 3-day rain (mm)": float(rain3[j]), "temp 7 d (C)": float(inp["t7_mean_c"][j]), "frost days": float(inp["frost_days"][j]), "in forest": float(ok[j]),
                              "altitude (m)": float(hab["elevation_m"][rr[idx][j], cc[idx][j]])}
    outs = [o for o in outs if "v" in o]
    res = {}
    for label, sel in (("main: people who record mushrooms", lambda o: o["recorder"]), ("side: all fungi recorders", lambda o: True)):
        S = [o for o in outs if sel(o)]
        yes = [o for o in S if o["found"]]; no = [o for o in S if not o["found"]]
        print(f"\n== {label}: {len(S):,} forest outings by {len({o['u'] for o in S})} people · "
              f"FOUND {len(yes)} · NOTHING {len(no):,}")
        print(f"{'':28s}{'found':>8s}{'nothing':>9s}{'win':>6s}{'95% range':>12s}{'same month':>12s}")
        res[label] = dict(outings=len(S), found=len(yes), nothing=len(no), people=len({o['u'] for o in S}), vars={})
        users = sorted({o["u"] for o in S})
        for var in yes[0]["v"]:
            def wins(Y, N, same_month=False):
                vals = []
                for y in Y:
                    pool = [n["v"][var] for n in N if (not same_month or n["date"][5:7] == y["date"][5:7])]
                    if pool: vals.append(B.win(y["v"][var], pool))
                return float(np.mean(vals)) if vals else float("nan")
            m = wins(yes, no); mm = wins(yes, no, True)
            boots = []
            for _ in range(300):                        # re-sample people, not outings
                pick = set(RNG.choice(users, len(users)))
                Y = [o for o in yes if o["u"] in pick]; N = [o for o in no if o["u"] in pick]
                if Y and N: boots.append(wins(Y, N))
            lo, hi = np.percentile(boots, [2.5, 97.5])
            med_y = np.median([o["v"][var] for o in yes]); med_n = np.median([o["v"][var] for o in no])
            res[label]["vars"][var] = dict(found=float(med_y), nothing=float(med_n), win=m, lo=float(lo), hi=float(hi), win_same_month=mm)
            print(f"{var:28s}{med_y:8.1f}{med_n:9.1f}{m*100:6.0f}{f'({lo*100:.0f}-{hi*100:.0f})':>12s}{mm*100:12.0f}")
    # ---- a few score tweaks that follow the pattern (lab only). Picked BEFORE looking at 2025-26.
    W = B.WEIGHTS
    def score(v, cool=False, gate=True, shade_x=1.0, areas=False):
        f = {k: v[f"layer {k}"] for k in B.FACTORS}
        if areas:
            w = {**W, "rain_total": 0.0, "rain_pulse": 0.0, "temperature": 0.0, "soil_moisture": 0.0}
            return float(B.F.combine({k: np.array([x]) for k, x in f.items()}, w, np.array([v["in forest"]]))[0])
        if cool:
            tc = {**B.S["temperature"], "zero_at_c": 2, "best_from_c": 6, "best_to_c": 13, "zero_again_c": 20}
            f["temperature"] = float(B.F.temperature_factor(v["temp 7 d (C)"], v["frost days"], tc))
        w = {**W, "shade": W["shade"] * shade_x}
        return float(B.F.combine({k: np.array([x]) for k, x in f.items()}, w, np.array([v["in forest"]]))[0]) * (v["water gate"] if gate else 1.0)
    TWEAKS = {"live score": {}, "no water gate": dict(gate=False), "cooler best band 6-13 C": dict(cool=True),
              "cooler + no gate": dict(cool=True, gate=False), "cooler + no gate + 2x shade": dict(cool=True, gate=False, shade_x=2.0),
              "areas only (season + shade)": dict(areas=True)}
    S = [o for o in outs if o["recorder"]]
    print("\nScore tweaks (people who record mushrooms): win all | same month | 2022-24 | 2025-26")
    res["tweaks"] = {}
    for name, kw in TWEAKS.items():
        for o in S: o["t"] = score(o["v"], **kw)
        def w_(Y, N, same=False):
            vals = [B.win(y["t"], [n["t"] for n in N if not same or n["date"][5:7] == y["date"][5:7]]) for y in Y
                    if [n for n in N if not same or n["date"][5:7] == y["date"][5:7]]]
            return float(np.mean(vals)) if vals else float("nan")
        yes = [o for o in S if o["found"]]; no = [o for o in S if not o["found"]]
        e = lambda L: [o for o in L if o["season"] <= 2024]; l = lambda L: [o for o in L if o["season"] >= 2025]
        r = dict(all=w_(yes, no), month=w_(yes, no, True), early=w_(e(yes), e(no)), late=w_(l(yes), l(no)),
                 n_early=len(e(yes)), n_late=len(l(yes)))
        res["tweaks"][name] = r
        print(f"  {name:30s}{r['all']*100:5.0f} |{r['month']*100:5.0f} |{r['early']*100:5.0f} ({r['n_early']}) |{r['late']*100:5.0f} ({r['n_late']})")
    by_month = defaultdict(lambda: [0, 0])
    for o in outs:
        if o["recorder"]: by_month[int(o["date"][5:7])][o["found"]] += 1
    res["by_month (nothing, found)"] = {m: by_month[m] for m in (10, 11, 12, 1, 2, 3, 4)}
    print("\nby month (recorders): " + " · ".join(f"{m}: {by_month[m][1]} found / {sum(by_month[m])} outings" for m in (10, 11, 12, 1, 2, 3, 4)))
    json.dump(res, open(LAB / f"experiments/06-effort/results{'_livehab' if '--habitat=live' in sys.argv else ''}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
