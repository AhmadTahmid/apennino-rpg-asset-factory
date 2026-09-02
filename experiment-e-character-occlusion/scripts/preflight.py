"""Verify Experiment E inputs, atlas semantics, occluder provenance, and geometry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    ROOT / "assets" / "control_01.png": (
        "FD11B82DEAD94E5BF5CB30F9DD9F718C84C5D9D5AAFD8170483FA222B5CBB54F",
        (1672, 941),
        "RGB",
    ),
    ROOT / "assets" / "source" / "traveler_generated_checkerboard.png": (
        "AEBFDF032F67777B468766425A4D9995E8379B9D28AB7D413C0C3547B0A92C32",
        (996, 1578),
        "RGB",
    ),
    ROOT / "assets" / "traveler_walk_sheet.png": (
        "4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876",
        (144, 256),
        "RGBA",
    ),
    ROOT / "assets" / "southwest_planter_mask.png": (
        "E57567DF8FD4B9C30AEB8D8452E5F28FD62053AB906330B9D2E04486B9AD5C91",
        (1672, 941),
        "L",
    ),
    ROOT / "assets" / "southwest_planter_foreground.png": (
        "7A59A290EA28117E6DF18EBDC26AF6B5D801BE120A50B7F7098BBECBE48C7895",
        (1672, 941),
        "RGBA",
    ),
}

GEOMETRY_HASH = "DF0924A62B4216268C7152070644BBDC9635CF19A4693A2290003C5D6C38CAF4"
GRID = (3, 4)
CELL_SIZE = (48, 64)
OCCLUSION_ANCHOR = (704, 675)
MUST_CLEAR_MASK_POINTS = ((680, 645), (705, 645), (720, 650), (722, 700), (665, 640))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def point_in_polygon(point: tuple[float, float], polygon: list[list[float]]) -> bool:
    x, y = point
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x1, y1 = previous
        x2, y2 = current
        if (y1 > y) != (y2 > y):
            intersection = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < intersection:
                inside = not inside
        previous = current
    return inside


def atlas_checks(atlas: Image.Image) -> tuple[list[str], dict]:
    failures: list[str] = []
    alpha = atlas.getchannel("A")
    border_alpha = []
    for x in range(atlas.width):
        border_alpha.extend((alpha.getpixel((x, 0)), alpha.getpixel((x, atlas.height - 1))))
    for y in range(atlas.height):
        border_alpha.extend((alpha.getpixel((0, y)), alpha.getpixel((atlas.width - 1, y))))
    if any(border_alpha):
        failures.append("Atlas outer border is not transparent")

    frames: list[dict] = []
    for row in range(GRID[1]):
        row_hashes = []
        baselines = []
        for column in range(GRID[0]):
            frame = atlas.crop(
                (
                    column * CELL_SIZE[0],
                    row * CELL_SIZE[1],
                    (column + 1) * CELL_SIZE[0],
                    (row + 1) * CELL_SIZE[1],
                )
            )
            bbox = frame.getchannel("A").getbbox()
            frame_hash = hashlib.sha256(frame.tobytes()).hexdigest().upper()
            if bbox is None:
                failures.append(f"Atlas frame {row},{column} is empty")
                baseline = None
            else:
                baseline = bbox[3] - 1
                baselines.append(baseline)
                if bbox[0] == 0 or bbox[1] == 0 or bbox[2] == CELL_SIZE[0] or bbox[3] == CELL_SIZE[1]:
                    failures.append(f"Atlas frame {row},{column} touches a cell edge")
            row_hashes.append(frame_hash)
            frames.append(
                {
                    "row": row,
                    "column": column,
                    "alpha_bbox": list(bbox) if bbox else None,
                    "foot_baseline_y": baseline,
                    "pixel_sha256": frame_hash,
                }
            )
        if len(set(row_hashes)) != 3:
            failures.append(f"Atlas row {row} does not contain three distinct poses")
        if baselines and max(baselines) - min(baselines) > 1:
            failures.append(f"Atlas row {row} foot baselines drift: {baselines}")
    return failures, {"transparent_outer_border": not any(border_alpha), "frames": frames}


def occluder_checks(scene: Image.Image, atlas: Image.Image, mask: Image.Image, foreground: Image.Image) -> tuple[list[str], dict]:
    failures: list[str] = []
    scene_rgb = scene.convert("RGB")
    foreground_rgb = foreground.convert("RGB")
    foreground_alpha = foreground.getchannel("A")
    mask_bbox = mask.getbbox()
    opaque_count = sum(mask.histogram()[1:])
    mismatch_count = 0
    alpha_mismatch_count = 0
    if mask_bbox is None:
        failures.append("Occluder mask is empty")
    else:
        for y in range(mask_bbox[1], mask_bbox[3]):
            for x in range(mask_bbox[0], mask_bbox[2]):
                mask_alpha = mask.getpixel((x, y))
                if mask_alpha:
                    if foreground_rgb.getpixel((x, y)) != scene_rgb.getpixel((x, y)):
                        mismatch_count += 1
                if foreground_alpha.getpixel((x, y)) != mask_alpha:
                    alpha_mismatch_count += 1
    if mismatch_count:
        failures.append(f"Occluder has {mismatch_count} non-source RGB pixels")
    if alpha_mismatch_count:
        failures.append(f"Occluder alpha differs from mask at {alpha_mismatch_count} pixels")
    occupancy = opaque_count / (scene.width * scene.height)
    if not (0.0 < occupancy < 0.002):
        failures.append(f"Occluder occupancy is implausible: {occupancy}")

    uncleared = [point for point in MUST_CLEAR_MASK_POINTS if mask.getpixel(point)]
    if uncleared:
        failures.append(f"Reviewed must-clear mask controls became opaque: {uncleared}")

    # Atlas row 0, column 1 is the declared south-facing idle pose.  Godot
    # draws its 48x64 frame bottom-centred at the player's footpoint.
    idle = atlas.crop((48, 0, 96, 64))
    idle_alpha = idle.getchannel("A")
    sprite_opaque = 0
    overlap = 0
    top_left = (OCCLUSION_ANCHOR[0] - 24, OCCLUSION_ANCHOR[1] - 64)
    overlap_points: list[list[int]] = []
    for local_y in range(64):
        for local_x in range(48):
            if not idle_alpha.getpixel((local_x, local_y)):
                continue
            sprite_opaque += 1
            world_point = (top_left[0] + local_x, top_left[1] + local_y)
            if mask.getpixel(world_point):
                overlap += 1
                if len(overlap_points) < 20:
                    overlap_points.append(list(world_point))
    overlap_fraction = overlap / sprite_opaque if sprite_opaque else 0.0
    if not (0.01 <= overlap_fraction <= 0.60):
        failures.append(f"Declared pose has implausible occluder overlap fraction: {overlap_fraction}")

    return failures, {
        "alpha_bbox": list(mask_bbox) if mask_bbox else None,
        "opaque_pixel_count": opaque_count,
        "alpha_occupancy_fraction": occupancy,
        "source_rgb_mismatch_count": mismatch_count,
        "mask_alpha_mismatch_count": alpha_mismatch_count,
        "must_clear_points": [list(point) for point in MUST_CLEAR_MASK_POINTS],
        "uncleared_control_points": [list(point) for point in uncleared],
        "occlusion_anchor": list(OCCLUSION_ANCHOR),
        "idle_sprite_opaque_pixels": sprite_opaque,
        "overlap_pixel_count": overlap,
        "overlap_fraction": overlap_fraction,
        "sample_overlap_points": overlap_points,
    }


def main() -> int:
    failures: list[str] = []
    checked: list[dict] = []
    for path, (expected_hash, expected_size, expected_mode) in EXPECTED.items():
        actual_hash = digest(path) if path.exists() else None
        actual_size = None
        actual_mode = None
        if path.exists():
            with Image.open(path) as image:
                actual_size = image.size
                actual_mode = image.mode
        if actual_hash != expected_hash:
            failures.append(f"Hash mismatch: {path}")
        if actual_size != expected_size:
            failures.append(f"Dimension mismatch: {path}")
        if actual_mode != expected_mode:
            failures.append(f"Mode mismatch: {path}; got {actual_mode}, expected {expected_mode}")
        checked.append(
            {
                "path": str(path),
                "sha256": actual_hash,
                "dimensions": actual_size,
                "mode": actual_mode,
            }
        )

    geometry_path = ROOT / "data" / "node_001_geometry.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    geometry_hash = digest(geometry_path)
    if geometry_hash != GEOMETRY_HASH:
        failures.append("Experiment D geometry hash changed")
    boundary = geometry["walkable_boundary"]
    spawn = tuple(geometry["player"]["spawn"])
    if not point_in_polygon(spawn, boundary):
        failures.append("Spawn lies outside walkable boundary")
    if not point_in_polygon(OCCLUSION_ANCHOR, boundary):
        failures.append("Occlusion anchor lies outside accepted walkable boundary")
    for waypoint in geometry["tested_route"]["waypoints"]:
        if not point_in_polygon(tuple(waypoint), boundary):
            failures.append(f"Waypoint lies outside walkable boundary: {waypoint}")

    with Image.open(ROOT / "assets" / "control_01.png") as scene_image:
        scene = scene_image.convert("RGBA")
    with Image.open(ROOT / "assets" / "traveler_walk_sheet.png") as atlas_image:
        atlas = atlas_image.convert("RGBA")
    with Image.open(ROOT / "assets" / "southwest_planter_mask.png") as mask_image:
        mask = mask_image.convert("L")
    with Image.open(ROOT / "assets" / "southwest_planter_foreground.png") as foreground_image:
        foreground = foreground_image.convert("RGBA")

    atlas_failures, atlas_evidence = atlas_checks(atlas)
    failures.extend(atlas_failures)
    occluder_failures, occluder_evidence = occluder_checks(scene, atlas, mask, foreground)
    failures.extend(occluder_failures)

    preparation = json.loads((ROOT / "diagnostics" / "asset_preflight.json").read_text(encoding="utf-8"))
    if not preparation.get("passed"):
        failures.append("Asset preparation report is not passing")
    if preparation["atlas"]["sha256"] != EXPECTED[ROOT / "assets" / "traveler_walk_sheet.png"][0]:
        failures.append("Asset preparation atlas hash disagrees with locked preflight hash")
    if preparation["occluder"]["foreground_sha256"] != EXPECTED[ROOT / "assets" / "southwest_planter_foreground.png"][0]:
        failures.append("Asset preparation foreground hash disagrees with locked preflight hash")

    report = {
        "passed": not failures,
        "failures": failures,
        "checked_assets": checked,
        "geometry_sha256": geometry_hash,
        "expected_geometry_sha256": GEOMETRY_HASH,
        "geometry_unchanged_from_experiment_d": geometry_hash == GEOMETRY_HASH,
        "atlas_contract": atlas_evidence,
        "occluder_contract": occluder_evidence,
    }
    output = ROOT / "diagnostics" / "preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
