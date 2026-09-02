"""Verify the real-rendered town is the locked raster plus the scaled traveler."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    art = Image.open(ROOT / "assets" / "moonroot_hollow.png").convert("RGB")
    capture = Image.open(ROOT / "diagnostics" / "runtime_town_capture.png").convert("RGB")
    baseline = Image.open(ROOT / "diagnostics" / "runtime_town_baseline.png").convert("RGB")
    baseline_bbox = ImageChops.difference(art, baseline).getbbox()
    player_diff = ImageChops.difference(capture, baseline)
    player_bbox = player_diff.getbbox()
    changed_pixels = 0
    if player_bbox:
        changed_pixels = sum(pixel != (0, 0, 0) for pixel in player_diff.crop(player_bbox).get_flattened_data())
    envelope = (788, 672, 885, 801)
    inside = bool(
        player_bbox
        and player_bbox[0] >= envelope[0]
        and player_bbox[1] >= envelope[1]
        and player_bbox[2] <= envelope[2]
        and player_bbox[3] <= envelope[3]
    )
    passed = baseline_bbox is None and inside and 2000 <= changed_pixels <= 5000
    report = {
        "passed": passed,
        "baseline_equals_locked_town_art": baseline_bbox is None,
        "baseline_difference_bbox": list(baseline_bbox) if baseline_bbox else None,
        "traveler_difference_bbox": list(player_bbox) if player_bbox else None,
        "expected_traveler_envelope": list(envelope),
        "traveler_bbox_inside_expected_envelope": inside,
        "traveler_changed_pixel_count": changed_pixels,
        "changed_pixel_acceptance_range": [2000, 5000],
    }
    (ROOT / "diagnostics" / "render_capture_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
