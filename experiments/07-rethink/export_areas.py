"""Experiment 07: "best areas this season" as a lab map layer (Real's OK, 27 Nov 2026).

Per forest square on the LAB map (live forest + 15% pine squares, burned forest left out as of today):
  areas score = (0.15 x season x altitude + 0.10 x shade) / 0.25     (the live weights; no daily weather)
for each month Oct-Apr, then turned into a RANK among all forest squares that month (0 = lowest,
100 = top), so the colours mean "compared with other forest this month", not "good conditions".
Out: site/web/public/data/lab_areas.pmtiles (layer "areas", properties r10, r11, r12, r1, r2, r3, r4).
Run: site/pipeline/.venv/bin/python experiments/07-rethink/export_areas.py
"""
import json, sys, tempfile
from datetime import date
from pathlib import Path

import numpy as np
from pyproj import Transformer

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "site/pipeline"))
from shroomy import config                                     # noqa: E402
from shroomy.export.web import write_pmtiles                   # noqa: E402
from shroomy.grid import habitat_grid                          # noqa: E402
from shroomy.score import factors as F                         # noqa: E402
from shroomy.score.species import general_habitat              # noqa: E402
from shroomy.score.today import load_habitat                   # noqa: E402

MONTHS = [10, 11, 12, 1, 2, 3, 4]


def main():
    S = config.load("scoring")["score"]
    w = S["weights"]
    hab = load_habitat(date.today())
    ok = general_habitat(hab["habitat_filter"], hab["likely_tree"], S["general_map_trees"])
    rows, cols = np.nonzero(ok)
    band = hab["altitude_band"][rows, cols].astype(int)
    shade = np.nan_to_num(hab["shade_score"][rows, cols])
    ranks = {}
    for m in MONTHS:
        a = (w["season_altitude"] * F.season_factor(m, band, S["season_altitude"]) + w["shade"] * shade) \
            / (w["season_altitude"] + w["shade"])
        order = a.argsort(kind="stable")
        r = np.empty(len(a)); r[order] = np.arange(len(a))
        # ties share the same rank (many squares have the same value)
        uniq, inv = np.unique(a, return_inverse=True)
        mean_r = np.bincount(inv, r) / np.bincount(inv)
        ranks[m] = np.round(mean_r[inv] / (len(a) - 1) * 100).astype(int)
    g = habitat_grid()
    to_ll = Transformer.from_crs(g.crs, "EPSG:4326", always_xy=True)
    feats = []
    for k, (r, c) in enumerate(zip(rows, cols)):
        x0, y0 = g.west + c * g.res, g.north - r * g.res
        lon, lat = to_ll.transform([x0, x0 + g.res, x0 + g.res, x0, x0], [y0, y0, y0 - g.res, y0 - g.res, y0])
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[round(a, 5), round(b, 5)] for a, b in zip(lon, lat)]]},
                      "properties": {f"r{m}": int(ranks[m][k]) for m in MONTHS}})
    out = LAB / "site/web/public/data/lab_areas.pmtiles"
    with tempfile.TemporaryDirectory() as t:
        gj = Path(t) / "areas.geojson"
        gj.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")))
        write_pmtiles(gj, out, "areas", 6, 13)
    print(f"✓ {len(feats):,} forest squares -> {out.relative_to(LAB)} ({out.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    main()
