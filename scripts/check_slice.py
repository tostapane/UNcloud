"""Slice checks: radar order, optical zero pattern, s2cloudless, read speed.

Usage: uv run python scripts/check_slice.py data/slice
"""

import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from s2cloudless import S2PixelCloudDetector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402


def read(path):
    with rasterio.open(path) as f:
        return f.read()


def describe_file(path):
    with rasterio.open(path) as f:
        print(f"  {path.name}: bands={f.count} size={f.width}x{f.height} "
              f"dtype={f.dtypes[0]} nodata={f.nodata} compress={f.compression}")


def check_radar(files):
    print(f"\n== Radar ({len(files)} patches)")
    describe_file(files[0])
    imgs = np.stack([read(p) for p in files]).astype(np.float32)  # N, 2, H, W
    for c, name in enumerate(config.S1_BANDS):
        x = imgs[:, c]
        bad = ~np.isfinite(x)
        lo, hi = config.S1_CLIP[c]
        v = x[~bad]
        p1, p50, p99 = np.percentile(v, [1, 50, 99])
        print(f"  ch{c} ({name}): mean={v.mean():.2f} dB  p1={p1:.2f}  median={p50:.2f}  p99={p99:.2f}  "
              f"NaN/inf={bad.mean():.4%}  <=min({lo})={(v <= lo).mean():.2%}  >max({hi})={(v > hi).mean():.2%}")
    m0, m1 = np.nanmean(imgs[:, 0]), np.nanmean(imgs[:, 1])
    print(f"  -> second channel darker: {m1 < m0} (expected True if order is VV, VH)")


def check_optical(files, label):
    print(f"\n== Optical {label} ({len(files)} patches)")
    describe_file(files[0])
    n_px = all_zero = any_zero = over_max = blank = 0
    band_zero = np.zeros(len(config.S2_BANDS), dtype=np.int64)
    for p in files:
        x = read(p)  # 13, H, W
        z = x == 0
        n_px += z[0].size
        all_zero += z.all(0).sum()
        any_zero += z.any(0).sum()
        band_zero += z.reshape(len(z), -1).sum(1)
        over_max += (x > config.S2_CLIP[1]).sum()
        blank += z.all()
    print(f"  pixels with all bands 0: {all_zero / n_px:.4%}")
    print(f"  pixels with any band 0:  {any_zero / n_px:.4%}")
    print(f"  fully blank patches:     {blank}")
    print(f"  values > {config.S2_CLIP[1]}:          {over_max / (n_px * 13):.4%}")
    nz = [f"{b}={c}" for b, c in zip(config.S2_BANDS, band_zero) if c]
    print(f"  zero count per band:     {', '.join(nz) or 'none'}")


def check_s2cloudless(files, batch=16):
    print(f"\n== s2cloudless on cloudy ({len(files)} patches)")
    det = S2PixelCloudDetector(**config.S2CLOUDLESS)
    cov, quant_err = [], 0.0
    t0 = time.perf_counter()
    for i in range(0, len(files), batch):
        x = np.stack([read(p) for p in files[i:i + batch]]).astype(np.float32)
        x = np.clip(x, *config.S2_CLIP) / config.S2_CLIP[1]
        prob = det.get_cloud_probability_maps(np.moveaxis(x, 1, -1))  # N, H, W
        mask = det.get_mask_from_prob(prob)
        cov += list(mask.reshape(len(mask), -1).mean(1))
        quant_err = max(quant_err, np.abs(np.round(prob * 255) / 255 - prob).max())
    dt = (time.perf_counter() - t0) / len(files)
    cov = np.array(cov)
    hist, _ = np.histogram(cov, bins=5, range=(0, 1))
    print(f"  time per patch: {dt * 1000:.0f} ms (incl. read)  -> full dataset ~{dt * 122218 / 3600:.1f} h")
    print(f"  coverage mean={cov.mean():.2f}  bins 0-20/20-40/40-60/60-80/80-100%: {hist.tolist()}")
    print(f"  8-bit storage max error: {quant_err:.4f}")


def check_speed(files, label, n=50):
    t0 = time.perf_counter()
    for p in files[:n]:
        read(p)
    dt = (time.perf_counter() - t0) / min(n, len(files))
    print(f"  {label}: {dt * 1000:.1f} ms per file")


def main(root):
    root = Path(root).expanduser()
    s1 = sorted(root.glob("*_s1/*/*.tif"))
    s2 = sorted(root.glob("*_s2/*/*.tif"))
    s2c = sorted(root.glob("*_s2_cloudy/*/*.tif"))
    print(f"found: radar={len(s1)} clear={len(s2)} cloudy={len(s2c)}")

    check_radar(s1)
    check_optical(s2, "clear")
    check_optical(s2c, "cloudy")
    check_s2cloudless(s2c)

    print("\n== Read speed (local disk, warm cache possible)")
    check_speed(s1, "radar")
    check_speed(s2, "clear")
    check_speed(s2c, "cloudy")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/slice")
