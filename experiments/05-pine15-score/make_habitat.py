"""Experiment 05 (Real's OK, 27 Nov 2026): put the "15% forest if mostly pine" squares into the LAB score.

Writes the lab's site/data/processed/habitat_250m.tif from the live copy (backup/habitat_250m_live.tif):
squares with 15-25% forest, mostly conifer, open (no closed reserve), on land, become forest habitat:
  habitat_filter = 1, forest_type = 1 (conifer),
  likely_tree = 2 (Troodos black pine) at 1,200 m and above, else 1 (Calabrian pine)
  (the live map's own tree rule: config/scoring.yaml habitat.trees.black_pine_min_m).
Everything else is unchanged. The lab only; never the live site.
Run: site/pipeline/.venv/bin/python experiments/05-pine15-score/make_habitat.py
"""
from pathlib import Path

import numpy as np
import rasterio
import yaml

LAB = Path(__file__).resolve().parents[2]
SRC = LAB / "experiments/05-pine15-score/backup/habitat_250m_live.tif"
DST = LAB / "site/data/processed/habitat_250m.tif"


def main():
    black_min = yaml.safe_load(open(LAB / "site/config/scoring.yaml"))["habitat"]["trees"]["black_pine_min_m"]
    with rasterio.open(SRC) as s:
        prof, names = s.profile, list(s.descriptions)
        d = {n: s.read(i + 1) for i, n in enumerate(names)}
    forest = d["conifer_fraction"] + d["broadleaf_fraction"]
    new = ((d["habitat_filter"] == 0) & (d["forest_type"] == 0) & (d["reserve_id"] == 0) & (d["land_fraction"] > 0.5)
           & (forest >= 0.15) & (d["conifer_fraction"] >= d["broadleaf_fraction"]))
    d["habitat_filter"][new] = 1
    d["forest_type"][new] = 1
    d["likely_tree"][new] = np.where(d["elevation_m"][new] >= black_min, 2, 1)
    with rasterio.open(DST, "w", **prof) as o:
        for i, n in enumerate(names):
            o.write(d[n], i + 1)
            o.set_band_description(i + 1, n)
    print(f"✓ {int(new.sum()):,} squares added ({new.sum() * 0.0625:.0f} km²): "
          f"Calabrian pine {int((d['likely_tree'][new] == 1).sum()):,}, black pine {int((d['likely_tree'][new] == 2).sum()):,}")


if __name__ == "__main__":
    main()
