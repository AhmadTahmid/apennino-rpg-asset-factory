"""Verify each real-render baseline equals its locked raster and player changes stay local."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parent.parent
LOCATIONS = {
    "town": "moonroot_hollow.png",
    "forest": "lumenwood_crossing.png",
    "sanctuary": "heartroot_sanctuary.png",
}


def main() -> int:
    results = {}
    passed = True
    envelope = (780, 705, 892, 870)
    for location, art_name in LOCATIONS.items():
        art = Image.open(ROOT / "assets" / art_name).convert("RGB")
        baseline = Image.open(ROOT / "diagnostics" / f"runtime_{location}_baseline.png").convert("RGB")
        player = Image.open(ROOT / "diagnostics" / f"runtime_{location}_player.png").convert("RGB")
        baseline_bbox = ImageChops.difference(art, baseline).getbbox()
        difference = ImageChops.difference(player, baseline)
        player_bbox = difference.getbbox()
        changed = 0
        if player_bbox:
            changed = sum(pixel != (0, 0, 0) for pixel in difference.crop(player_bbox).get_flattened_data())
        inside = bool(
            player_bbox
            and player_bbox[0] >= envelope[0]
            and player_bbox[1] >= envelope[1]
            and player_bbox[2] <= envelope[2]
            and player_bbox[3] <= envelope[3]
        )
        location_passed = baseline_bbox is None and inside and 2000 <= changed <= 5000
        passed = passed and location_passed
        results[location] = {
            "passed": location_passed,
            "baseline_equals_locked_art": baseline_bbox is None,
            "baseline_difference_bbox": list(baseline_bbox) if baseline_bbox else None,
            "traveler_difference_bbox": list(player_bbox) if player_bbox else None,
            "traveler_bbox_inside_expected_envelope": inside,
            "traveler_changed_pixel_count": changed,
        }
    report = {
        "passed": passed,
        "renderer": "Godot GL Compatibility, non-headless capture",
        "expected_traveler_envelope": list(envelope),
        "changed_pixel_acceptance_range": [2000, 5000],
        "locations": results,
    }
    output = ROOT / "diagnostics" / "render_capture_verification.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
