"""Job 2, step 4: a newer forest layer to test against the 2018 one.
ESA WorldCover 2021 (10 m, CC BY 4.0, (c) ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021)).
Reads only the Cyprus window of the two public tiles (no account, no cost) and writes, per 250 m
habitat square, the share of 10 m pixels that are "tree cover" (class 10).
Out: experiments/02-backtest/weather/worldcover_tree_250m.npy (same rows x cols as habitat_250m.tif)
Run:  site/pipeline/.venv/bin/python experiments/02-backtest/worldcover.py
"""
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject

LAB = Path(__file__).resolve().parents[2]
OUT = LAB / "experiments/02-backtest/weather/worldcover_tree_250m.npy"
BASE = "/vsicurl/https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{}_Map.tif"


def main():
    with rasterio.open(LAB / "site/data/processed/habitat_250m.tif") as h:
        shape, transform, crs = (h.height, h.width), h.transform, h.crs
    share = np.zeros(shape, "float32")
    for tile in ("N33E030", "N33E033"):
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
            with rasterio.open(BASE.format(tile)) as src:
                win = src.window(32.2, 34.5, 34.65, 35.75).intersection(
                    rasterio.windows.Window(0, 0, src.width, src.height))
                cls = src.read(1, window=win)
                tf = src.window_transform(win)
                print(tile, cls.shape)
                tree = (cls == 10).astype("float32")
                tree[cls == 0] = np.nan                     # no data
                part = np.full(shape, np.nan, "float32")
                reproject(tree, part, src_transform=tf, src_crs=src.crs, dst_transform=transform, dst_crs=crs,
                          resampling=Resampling.average, src_nodata=np.nan, dst_nodata=np.nan)
                share = np.where(np.isfinite(part), np.fmax(share, part), share)
    np.save(OUT, share)
    print(f"✓ {OUT.name}: squares with 25%+ tree cover: {(share >= 0.25).sum():,} ({(share >= 0.25).sum() * 0.0625:.0f} km²)")


if __name__ == "__main__":
    main()
