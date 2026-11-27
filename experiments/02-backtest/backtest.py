"""Job 2: does the Shroomy score predict real finds?

For each mushroom find (iNaturalist/GBIF, exact spot within 500 m, exact date, 1 Oct - 30 Apr,
seasons 2022-23 to 2026-27) we rebuild what Shroomy WOULD have scored that 250 m square that day,
with the live scoring code (site/pipeline/shroomy/score, unchanged) and the live weather model.

One "find event" = finds on the same day within 1 km (one patch photographed by several people
counts once). Each event is compared with:
  A. random open-forest squares (the map's own habitat) on the same day  -> does the weather part pick the right forest?
  B. random land squares on the same day                                   -> does the whole map pick the right places?
  C. the same square on every other day of its season (1 Oct - 30 Apr)   -> does it pick the right days?
Score of a test = "win rate" (AUC): the chance a find beats a random comparison. 50% = no better
than chance, 100% = always higher. 95% ranges come from re-sampling the events 1,000 times.

Variants: the live score; each layer switched off one at a time; no habitat filter; no water gate;
"other broadleaf" counted as habitat; the WorldCover 2021 forest instead of the 2018 one; and
"habitat x weather" (multiply habitat, weather and season instead of adding them).

Run (after fetch_weather.py and worldcover.py):  site/pipeline/.venv/bin/python experiments/02-backtest/backtest.py
Out: experiments/02-backtest/results.json and a printed table.
"""
import json, sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "site/pipeline"))
from shroomy import config                                   # noqa: E402
from shroomy.habitat import burns                            # noqa: E402
from shroomy.score import factors as F                       # noqa: E402
from shroomy.score.downscale import Interpolator             # noqa: E402
from shroomy.score.today import day_factors, water_gate      # noqa: E402

W = LAB / "experiments/02-backtest/weather"
RNG = np.random.default_rng(2026)
N_POOL = 3000
FACTORS = F.FACTORS
S = config.load("scoring")["score"]
WEIGHTS = S["weights"]


# ------------------------------------------------------------------ habitat
def habitat():
    with rasterio.open(config.PROCESSED / "habitat_250m.tif") as s:
        hab = {s.descriptions[i]: s.read(i + 1) for i in range(s.count)}
        hab["transform"] = s.transform
    share, latest = burns.burned_layer()
    hab["burn_share"], hab["burn_date"] = share, latest
    hab["wc_tree"] = np.load(W / "worldcover_tree_250m.npy")
    return hab


def cell_of(hab, lon, lat):
    x, y = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True).transform(lon, lat)
    r, c = rasterio.transform.rowcol(hab["transform"], x, y)
    return int(r), int(c), x, y


# ------------------------------------------------------------------ samples
def find_events():
    recs = json.load(open(LAB / "data/finds/finds.json"))["records"]
    keep, dropped = [], defaultdict(int)
    for r in recs:
        if r["group"] != "mushroom": continue
        if r["loc"] != "good" or not r["date"] or len(r["date"]) != 10: dropped["rough spot or no exact day"] += 1; continue
        d = date.fromisoformat(r["date"])
        season = d.year if d.month >= 8 else d.year - 1
        if season < 2022: dropped["before the 2022-23 season (no weather from the live model)"] += 1; continue
        if not (d.month >= 10 or d.month <= 4): dropped["May-September (outside the scored season)"] += 1; continue
        if d >= date.today(): dropped["today"] += 1; continue
        keep.append({**r, "season": season})
    # events: same day, within 1 km
    events = []
    for r in sorted(keep, key=lambda r: r["date"]):
        for e in events:
            if e["date"] == r["date"] and np.hypot((e["lat"] - r["lat"]) * 111, (e["lon"] - r["lon"]) * 91) < 1.0:
                e["n"] += 1; e["names"].add(r["name"]); break
        else:
            events.append(dict(date=r["date"], season=r["season"], lat=r["lat"], lon=r["lon"], n=1, names={r["name"]}))
    return keep, events, dict(dropped)


# ------------------------------------------------------------------ scoring
def tree_ok(hab, rows, cols, on, worldcover=False, other_broadleaf=False):
    """The map's habitat at date `on`: open forest (not a closed reserve), a partner tree, not burned before `on`."""
    tree = hab["likely_tree"][rows, cols].astype(int)
    burned = (hab["burn_share"][rows, cols] > 0.5) & (hab["burn_date"][rows, cols] > 0) \
        & (hab["burn_date"][rows, cols] < on.toordinal())
    trees = [1, 2, 3, 4] if other_broadleaf else S["general_map_trees"]
    if not worldcover:
        ok = (hab["habitat_filter"][rows, cols] > 0) & np.isin(tree, trees)
    else:
        # WorldCover 2021 decides WHERE the forest is; the tree type stays the 2018 guess, and new
        # forest (no 2018 tree) is taken as pine (the island's main forest tree).
        wc = np.nan_to_num(hab["wc_tree"][rows, cols]) >= 0.25
        open_ = hab["reserve_id"][rows, cols] == 0
        ok = wc & open_ & (np.isin(tree, trees) | (tree == 0))
    return ok & ~burned


def habitat_quality(hab, rows, cols, ok):
    """0..1 habitat for "habitat x weather": forest share x partner tree x shade."""
    forest = hab["conifer_fraction"][rows, cols] + hab["broadleaf_fraction"][rows, cols]
    shade = np.nan_to_num(hab["shade_score"][rows, cols])
    return ok * F.ramp(forest, 0.25, 0.75) * (0.5 + 0.5 * shade)


def variants(f, gate, hab, rows, cols, on):
    """Every score variant for the given squares on day `on` (f = the six factors, gate = water gate)."""
    ok = tree_ok(hab, rows, cols, on)
    out = {"live score": F.combine(f, WEIGHTS, ok) * gate}
    for k in FACTORS:
        w = {**WEIGHTS, k: 0.0}
        out[f"without {k.replace('_', ' ')}"] = F.combine(f, w, ok) * gate
    out["without water gate"] = F.combine(f, WEIGHTS, ok)
    out["without habitat filter"] = F.combine(f, WEIGHTS, np.ones_like(ok)) * gate
    out["other broadleaf counts"] = F.combine(f, WEIGHTS, tree_ok(hab, rows, cols, on, other_broadleaf=True)) * gate
    out["WorldCover 2021 forest"] = F.combine(f, WEIGHTS, tree_ok(hab, rows, cols, on, worldcover=True)) * gate
    wx = {k: WEIGHTS[k] for k in ("rain_total", "rain_pulse", "temperature", "soil_moisture")}
    weather = sum(wx[k] * np.nan_to_num(f[k]) for k in wx) / sum(wx.values()) * gate
    hq = habitat_quality(hab, rows, cols, ok)
    out["habitat x weather x season"] = 100 * hq * weather * f["season_altitude"]
    out["habitat x weather"] = 100 * hq * weather
    return out


def score_cells(w, interp, hab, rows, cols, t, on, clim):
    elev = np.nan_to_num(hab["elevation_m"][rows, cols])
    band = hab["altitude_band"][rows, cols].astype(int)
    shade = hab["shade_score"][rows, cols]
    f, _ = day_factors(S, w, t, interp, elev, band, shade, on.month, clim)
    gate, _, _ = water_gate(S, interp(w["precip"][:, : t + 1]), t)
    return variants(f, gate, hab, rows, cols, on)


# ------------------------------------------------------------------ win rate
def win(x, pool):
    """Share of `pool` below x (ties count half)."""
    pool = np.asarray(pool)
    return ((pool < x).sum() + 0.5 * (pool == x).sum()) / len(pool)


def boot(vals, n=1000):
    vals = np.asarray(vals)
    idx = RNG.integers(0, len(vals), (n, len(vals)))
    m = vals[idx].mean(axis=1)
    return float(vals.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_diff(a, b, n=1000):
    d = np.asarray(a) - np.asarray(b)
    idx = RNG.integers(0, len(d), (n, len(d)))
    m = d[idx].mean(axis=1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def main():
    hab = habitat()
    clim = dict(np.load(config.PROCESSED / "weather" / "soil_climatology.npz"))
    keep, events, dropped = find_events()
    have = {int(p.stem.split("_")[1]) for p in W.glob("season_*.npz")}
    if "--partial" in sys.argv: events = [e for e in events if e["season"] in have]
    print(f"{len(keep)} finds -> {len(events)} find events; left out: {dropped}")

    land_r, land_c = np.nonzero(hab["land_fraction"] > 0.5)
    pick = RNG.choice(len(land_r), N_POOL, replace=False)
    pool_land = (land_r[pick], land_c[pick])
    forest_r, forest_c = np.nonzero((hab["habitat_filter"] > 0) & np.isin(hab["likely_tree"], S["general_map_trees"]))
    pick = RNG.choice(len(forest_r), N_POOL, replace=False)
    pool_forest = (forest_r[pick], forest_c[pick])

    for e in events:
        e["row"], e["col"], e["x"], e["y"] = cell_of(hab, e["lon"], e["lat"])

    res = defaultdict(lambda: defaultdict(list))          # variant -> test -> per-event win rate
    facts = []
    for season in sorted({e["season"] for e in events}):
        w = dict(np.load(W / f"season_{season}.npz"))
        dates = [str(d) for d in w["dates"]]
        ev = [e for e in events if e["season"] == season]
        er = np.array([e["row"] for e in ev]); ec = np.array([e["col"] for e in ev])
        cxy = lambda r, c: np.c_[hab["transform"].c + (c + 0.5) * 250, hab["transform"].f - (r + 0.5) * 250]
        pts = np.c_[w["x"], w["y"]]
        i_ev, i_land, i_for = Interpolator(pts, cxy(er, ec)), Interpolator(pts, cxy(*pool_land)), Interpolator(pts, cxy(*pool_forest))
        # every scored day of the season for the find squares (test C)
        days = [i for i, d in enumerate(dates) if d[5:7] in ("10", "11", "12", "01", "02", "03", "04") and i >= 31]
        own = {}
        for t in days:
            own[t] = score_cells(w, i_ev, hab, er, ec, t, date.fromisoformat(dates[t]), clim)
        for t in sorted({dates.index(e["date"]) for e in ev}):
            on = date.fromisoformat(dates[t])
            sl = score_cells(w, i_land, hab, *pool_land, t, on, clim)
            sf = score_cells(w, i_for, hab, *pool_forest, t, on, clim)
            for k, e in enumerate(ev):
                if e["date"] != dates[t]: continue
                for v in own[t]:
                    x = own[t][v][k]
                    res[v]["A. vs random forest, same day"].append(win(x, sf[v]))
                    res[v]["B. vs random land, same day"].append(win(x, sl[v]))
                    res[v]["C. vs same spot, other days"].append(win(x, [own[u][v][k] for u in days if u != t]))
                facts.append(dict(date=e["date"], n=e["n"], live=float(own[t]["live score"][k]),
                                  in_habitat=bool(tree_ok(hab, er[k:k + 1], ec[k:k + 1], on)[0]),
                                  in_worldcover=bool(tree_ok(hab, er[k:k + 1], ec[k:k + 1], on, worldcover=True)[0]),
                                  forest_median_live=float(np.median(sf["live score"]))))
        print(f"  season {season}: {len(ev)} events done")

    inside = np.array([f["in_habitat"] for f in facts])
    table = {}
    for subset, mask in (("all finds", np.ones(len(facts), bool)), ("finds inside the map's forest", inside)):
        base = res["live score"]
        table[subset] = {}
        for v, tests in res.items():
            table[subset][v] = {}
            for test, vals in tests.items():
                vals = np.asarray(vals)[mask]; ref = np.asarray(base[test])[mask]
                m, lo, hi = boot(vals)
                d = boot_diff(vals, ref) if v != "live score" else (0.0, 0.0, 0.0)
                table[subset][v][test] = dict(win=m, lo=lo, hi=hi, diff=d[0], diff_lo=d[1], diff_hi=d[2], n=int(mask.sum()))
    n = len(facts)
    summary = dict(
        finds=len(keep), events=n, dropped=dropped,
        in_habitat=sum(f["in_habitat"] for f in facts), in_worldcover=sum(f["in_worldcover"] for f in facts),
        live_median_at_finds=float(np.median([f["live"] for f in facts])),
        live_median_random_forest=float(np.median([f["forest_median_live"] for f in facts])),
        fair_or_better_at_finds=sum(f["live"] >= 45 for f in facts),
        seasons=dict(sorted(defaultdict(int, {}).items())),
    )
    for f in facts: summary["seasons"][str(f["date"][:7])] = summary["seasons"].get(str(f["date"][:7]), 0) + 1
    json.dump(dict(summary=summary, table=table, events=facts), open(LAB / "experiments/02-backtest/results.json", "w"), indent=1)

    print(json.dumps(summary, indent=1))
    for subset, t_ in table.items():
        tests = list(t_["live score"])
        print(f"\n== {subset} (n={t_['live score'][tests[0]]['n']})")
        print(f"{'variant':30s}" + "".join(f"{t[:2]:>24s}" for t in tests))
        for v in t_:
            row = "".join(f"{t_[v][t]['win']*100:6.1f} ({t_[v][t]['lo']*100:4.1f}-{t_[v][t]['hi']*100:4.1f})"
                          + (f"{t_[v][t]['diff']*100:+5.1f}{'*' if t_[v][t]['diff_lo'] > 0 or t_[v][t]['diff_hi'] < 0 else ' '}" if v != "live score" else "       ") for t in tests)
            print(f"{v:30s}{row}")
    print("\n* = the change is bigger than the noise (95% range of the difference does not include 0)")


if __name__ == "__main__":
    main()
