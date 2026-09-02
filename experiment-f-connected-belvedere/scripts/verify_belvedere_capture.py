"""Verify the real-rendered belvedere background and localized traveler."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    art = Image.open(ROOT / "assets" / "belvedere.png").convert("RGB")
    capture = Image.open(ROOT / "diagnostics" / "runtime_belvedere_capture.png").convert("RGB")
    baseline = Image.open(ROOT / "diagnostics" / "runtime_belvedere_baseline.png").convert("RGB")
    baseline_diff = ImageChops.difference(art, baseline)
    player_diff = ImageChops.difference(capture, baseline)
    baseline_bbox = baseline_diff.getbbox()
    player_bbox = player_diff.getbbox()
    changed_pixels = 0
    if player_bbox:
        for pixel in player_diff.crop(player_bbox).get_flattened_data():
            if pixel != (0, 0, 0):
                changed_pixels += 1
    expected_envelope = (812, 656, 861, 721)
    bbox_inside_envelope = bool(
        player_bbox
        and player_bbox[0] >= expected_envelope[0]
        and player_bbox[1] >= expected_envelope[1]
        and player_bbox[2] <= expected_envelope[2]
        and player_bbox[3] <= expected_envelope[3]
    )
    passed = baseline_bbox is None and bbox_inside_envelope and 300 <= changed_pixels <= 1600
    if player_bbox:
        crop_box = (
            max(0, player_bbox[0] - 120),
            max(0, player_bbox[1] - 80),
            min(capture.width, player_bbox[2] + 120),
            min(capture.height, player_bbox[3] + 120),
        )
        capture.crop(crop_box).save(ROOT / "diagnostics" / "runtime_belvedere_capture_crop.png")
    report = {
        "passed": passed,
        "baseline_equals_locked_art": baseline_bbox is None,
        "baseline_difference_bbox": list(baseline_bbox) if baseline_bbox else None,
        "traveler_difference_bbox": list(player_bbox) if player_bbox else None,
        "expected_traveler_envelope": list(expected_envelope),
        "traveler_bbox_inside_expected_envelope": bbox_inside_envelope,
        "traveler_changed_pixel_count": changed_pixels,
        "changed_pixel_acceptance_range": [300, 1600],
    }
    (ROOT / "diagnostics" / "render_capture_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
