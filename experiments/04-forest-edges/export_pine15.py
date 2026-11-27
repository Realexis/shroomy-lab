"""Experiment 04: the squares that "15% forest if mostly pine" would ADD to the map's forest,
as a GeoJSON for the lab map (site/web/public/data/lab_pine15.geojson). Each square: its forest %
and conifer % (2018 forest map). Open squares only (no closed reserves), not already in the live forest.
Run: site/pipeline/.venv/bin/python experiments/04-forest-edges/export_pine15.py
"""
import json, sys
from pathlib import Path

import numpy as np
from pyproj import Transformer

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "experiments/02-backtest"))
import backtest as B                                           # noqa: E402


def main():
    hab = B.habitat()
    forest = hab["conifer_fraction"] + hab["broadleaf_fraction"]
    tree = hab["likely_tree"].astype(int)
    live = (hab["habitat_filter"] > 0) & np.isin(tree, [1, 2, 3])
    new = (~live & (hab["reserve_id"] == 0) & (hab["land_fraction"] > 0.5) & (forest >= 0.15)
           & (hab["conifer_fraction"] >= hab["broadleaf_fraction"]))
    rows, cols = np.nonzero(new)
    tf = hab["transform"]
    to_ll = Transformer.from_crs("EPSG:32636", "EPSG:4326", always_xy=True)
    feats = []
    for r, c in zip(rows, cols):
        x0, y0 = tf.c + c * 250, tf.f - r * 250
        xs, ys = [x0, x0 + 250, x0 + 250, x0, x0], [y0, y0, y0 - 250, y0 - 250, y0]
        lon, lat = to_ll.transform(xs, ys)
        feats.append({"type": "Feature", "geometry": {"type": "Polygon",
                      "coordinates": [[[round(a, 5), round(b, 5)] for a, b in zip(lon, lat)]]},
                      "properties": {"f": int(round(forest[r, c] * 100)), "p": int(round(hab["conifer_fraction"][r, c] * 100))}})
    out = LAB / "site/web/public/data/lab_pine15.geojson"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, separators=(",", ":")))
    print(f"✓ {len(feats):,} new squares ({len(feats) * 0.0625:.0f} km²) -> {out.relative_to(LAB)} ({out.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    main()
