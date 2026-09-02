"""Verify real-renderer captures for the single preregistered occlusion pose."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
NORMAL = ROOT / "diagnostics" / "runtime_occlusion_capture.png"
PLAYER_ABOVE = ROOT / "diagnostics" / "runtime_occlusion_capture_player_above.png"
BASELINE = ROOT / "diagnostics" / "runtime_occlusion_baseline.png"
REPORT = ROOT / "diagnostics" / "render_capture_verification.json"
NORMAL_CROP = ROOT / "diagnostics" / "runtime_occlusion_capture_crop.png"
PLAYER_ABOVE_CROP = ROOT / "diagnostics" / "runtime_occlusion_capture_player_above_crop.png"
EXPECTED_SIZE = (1672, 941)
ANCHOR = (704, 675)
SPRITE_TOP_LEFT = (ANCHOR[0] - 24, ANCHOR[1] - 64)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    failures: list[str] = []
    captures = {}
    for path in (NORMAL, PLAYER_ABOVE, BASELINE):
        if not path.exists():
            failures.append(f"Missing fresh capture: {path}")
            continue
        with Image.open(path) as image:
            captures[path.name] = image.convert("RGB")
            if image.size != EXPECTED_SIZE:
                failures.append(f"Capture has wrong size: {path}; got {image.size}")
    if failures:
        payload = {"passed": False, "failures": failures}
        REPORT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    normal = captures[NORMAL.name]
    player_above = captures[PLAYER_ABOVE.name]
    baseline = captures[BASELINE.name]

    review_crop = (630, 575, 790, 715)
    normal.crop(review_crop).resize((800, 700), Image.Resampling.NEAREST).save(NORMAL_CROP)
    player_above.crop(review_crop).resize((800, 700), Image.Resampling.NEAREST).save(PLAYER_ABOVE_CROP)
    atlas = Image.open(ROOT / "assets" / "traveler_walk_sheet.png").convert("RGBA")
    idle_alpha = atlas.crop((48, 0, 96, 64)).getchannel("A")
    mask = Image.open(ROOT / "assets" / "southwest_planter_mask.png").convert("L")
    source = Image.open(ROOT / "assets" / "control_01.png").convert("RGB")

    overlap_points: list[tuple[int, int]] = []
    clear_player_points: list[tuple[int, int]] = []
    for local_y in range(64):
        for local_x in range(48):
            if not idle_alpha.getpixel((local_x, local_y)):
                continue
            point = (SPRITE_TOP_LEFT[0] + local_x, SPRITE_TOP_LEFT[1] + local_y)
            if mask.getpixel(point):
                overlap_points.append(point)
            else:
                clear_player_points.append(point)

    normal_occluded_equal_baseline = sum(
        normal.getpixel(point) == baseline.getpixel(point) for point in overlap_points
    )
    mutation_reveals_player = sum(
        player_above.getpixel(point) != baseline.getpixel(point) for point in overlap_points
    )
    normal_shows_player_outside_mask = sum(
        normal.getpixel(point) != baseline.getpixel(point) for point in clear_player_points
    )
    mutation_matches_normal_outside_mask = sum(
        player_above.getpixel(point) == normal.getpixel(point) for point in clear_player_points
    )
    baseline_source_matches = sum(
        baseline.getpixel((x, y)) == source.getpixel((x, y))
        for y in range(mask.height)
        for x in range(mask.width)
        if mask.getpixel((x, y))
    )
    mask_opaque_count = sum(mask.histogram()[1:])

    if len(overlap_points) != 130:
        failures.append(f"Declared overlap changed: {len(overlap_points)} pixels, expected 130")
    if normal_occluded_equal_baseline != len(overlap_points):
        failures.append("Correct z-order did not restore every overlap pixel to foreground/baseline")
    if mutation_reveals_player != len(overlap_points):
        failures.append("Player-above mutation did not reveal every declared overlap pixel")
    if normal_shows_player_outside_mask != len(clear_player_points):
        failures.append("Correct capture hides unexpected player pixels outside the mask")
    if mutation_matches_normal_outside_mask != len(clear_player_points):
        failures.append("Z-order mutation changed player pixels outside the mask")
    if baseline_source_matches != mask_opaque_count:
        failures.append("No-player runtime baseline differs from locked source under occluder mask")

    payload = {
        "passed": not failures,
        "failures": failures,
        "renderer": "Godot GL Compatibility real Windows display driver (not headless dummy)",
        "capture_hashes": {
            "correct_order": digest(NORMAL),
            "player_above_mutation": digest(PLAYER_ABOVE),
            "no_player_baseline": digest(BASELINE),
            "correct_order_review_crop": digest(NORMAL_CROP),
            "player_above_review_crop": digest(PLAYER_ABOVE_CROP),
        },
        "capture_dimensions": list(EXPECTED_SIZE),
        "anchor": list(ANCHOR),
        "declared_overlap_pixels": len(overlap_points),
        "correct_order_overlap_pixels_equal_baseline": normal_occluded_equal_baseline,
        "player_above_overlap_pixels_different_from_baseline": mutation_reveals_player,
        "visible_player_pixels_outside_mask": len(clear_player_points),
        "correct_order_visible_player_pixels": normal_shows_player_outside_mask,
        "mutation_pixels_equal_correct_outside_mask": mutation_matches_normal_outside_mask,
        "runtime_baseline_source_matches_under_full_mask": baseline_source_matches,
        "full_mask_opaque_pixels": mask_opaque_count,
        "headless_limit": "Godot's dummy headless renderer returned no viewport texture; diagnostics/capture_render.log preserves that expected failed route.",
    }
    REPORT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
