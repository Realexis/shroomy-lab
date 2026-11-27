"""Experiment 04: forest edges (back-test recommendation 3).

Question: can the map's forest ("habitat") catch more real finds without marking much more land?
No weather needed, so finds from ALL years count (exact spot within 500 m).
For each way of drawing the forest:
  caught  = share of find events inside it (closed reserves count as "not caught", as on the map)
  land    = share of Cyprus land squares it marks
  lift    = caught / land  (how much better than marking land at random; higher = sharper)
  95% ranges from re-sampling the events.
Below 25% forest the 2018 map gives no tree type, so in the lowered-threshold variants a square
counts when its forest is mostly conifer (pine).
Run: site/pipeline/.venv/bin/python experiments/04-forest-edges/forest_edges.py [--group=main|all|ground]
"""
import json, sys
from datetime import date
from pathlib import Path

import numpy as np
from scipy.ndimage import binary_dilation

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "experiments/02-backtest"))
import backtest as B                                           # noqa: E402


def events():
    recs = json.load(open(LAB / "data/finds/finds.json"))["records"]
    keep = [r for r in recs if r["group"] == "mushroom" and B.GROUPS[B.GROUP](r) and r["loc"] == "good"]
    ev = []
    for r in sorted(keep, key=lambda r: r["date"] or ""):
        for e in ev:
            if e["date"] == r["date"] and np.hypot((e["lat"] - r["lat"]) * 111, (e["lon"] - r["lon"]) * 91) < 1.0:
                break
        else:
            ev.append(dict(date=r["date"], lat=r["lat"], lon=r["lon"], name=r["name"]))
    return keep, ev


def main():
    hab = B.habitat()
    land = hab["land_fraction"] > 0.5
    forest = hab["conifer_fraction"] + hab["broadleaf_fraction"]
    tree = hab["likely_tree"].astype(int)
    open_ = hab["reserve_id"] == 0
    pine = hab["conifer_fraction"] >= hab["broadleaf_fraction"]
    live = (hab["habitat_filter"] > 0) & np.isin(tree, [1, 2, 3])
    wc = np.nan_to_num(hab["wc_tree"]) >= 0.25
    ring1 = np.ones((3, 3), bool)
    V = {
        "live (25% forest, pine / oak)": live,
        "+ other broadleaf": (hab["habitat_filter"] > 0) & np.isin(tree, [1, 2, 3, 4]),
        "15% forest if mostly pine": live | (open_ & (forest >= 0.15) & pine),
        "10% forest if mostly pine": live | (open_ & (forest >= 0.10) & pine),
        "+ 250 m edge around forest": live | (binary_dilation(live, ring1) & open_ & land),
        "+ 500 m edge around forest": live | (binary_dilation(live, ring1, iterations=2) & open_ & land),
        "+ WorldCover 2021 trees (25%)": live | (wc & open_ & land),
        "10% if pine + 250 m edge": live | (open_ & (forest >= 0.10) & pine) | (binary_dilation(live, ring1) & open_ & land),
    }
    keep, ev = events()
    rc = [B.cell_of(hab, e["lon"], e["lat"])[:2] for e in ev]
    rows = np.array([r for r, _ in rc]); cols = np.array([c for _, c in rc])
    # a square burned before the find does not count (as in the back-test)
    burned = np.array([hab["burn_share"][r, c] > 0.5 and 0 < hab["burn_date"][r, c] < date.fromisoformat(e["date"]).toordinal()
                       if e["date"] and len(e["date"]) == 10 else False for e, r, c in zip(ev, rows, cols)])
    in_reserve = ~open_[rows, cols]
    print(f"[{B.GROUP}] {len(keep)} finds (exact spot, all years) -> {len(ev)} find events; "
          f"{int(in_reserve.sum())} in closed reserves, {int(burned.sum())} burned before the find\n")
    print(f"{'forest drawn as':34s}{'caught':>16s}{'land':>8s}{'lift':>7s}{'  extra km²':>11s}")
    out, base_area = {}, live[land].sum()
    for name, m in V.items():
        hit = m[rows, cols] & ~burned
        c, lo, hi = B.boot(hit.astype(float))
        share = m[land].mean()
        out[name] = dict(caught=c, lo=lo, hi=hi, n_caught=int(hit.sum()), land_share=float(share), lift=c / share,
                         extra_km2=float((m[land].sum() - base_area) * 0.0625))
        print(f"{name:34s}{int(hit.sum()):4d} = {c*100:3.0f}% ({lo*100:2.0f}-{hi*100:2.0f}){share*100:7.1f}%{c/share:7.1f}{out[name]['extra_km2']:+10.0f}")
    json.dump(dict(group=B.GROUP, events=len(ev), in_reserve=int(in_reserve.sum()), variants=out),
              open(LAB / f"experiments/04-forest-edges/results_{B.GROUP}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
