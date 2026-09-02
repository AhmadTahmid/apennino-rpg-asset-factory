"""Preflight Moonroot Hollow's raster-only art and gameplay geometry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
TOWN_HASH = "7B4DF1C2EB62D1E1C12893E5F9D4B3E3DF28249C5323F8C6D9C9294194D09674"
TRAVELER_HASH = "4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876"
GEOMETRY_HASH = "E0A63D3F32BA02AD0E7FA8B1910913BD343260828DA0D5A634E69F74E9C11A98"


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


def main() -> int:
    failures: list[str] = []
    town_path = ROOT / "assets" / "moonroot_hollow.png"
    original_path = ROOT / "assets" / "source" / "moonroot_hollow_generated_original.png"
    traveler_path = ROOT / "assets" / "traveler_walk_sheet.png"
    expected = {
        town_path: (TOWN_HASH, (1672, 941), "RGB"),
        original_path: (TOWN_HASH, (1672, 941), "RGB"),
        traveler_path: (TRAVELER_HASH, (144, 256), "RGBA"),
    }
    assets: list[dict] = []
    for path, (expected_hash, expected_size, expected_mode) in expected.items():
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
        assets.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": actual_hash,
                "dimensions": list(actual_size) if actual_size else None,
                "mode": actual_mode,
            }
        )

    geometry_path = ROOT / "data" / "town_geometry.json"
    geometry_hash = digest(geometry_path)
    if geometry_hash != GEOMETRY_HASH:
        failures.append("Town geometry hash changed")
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    boundary = geometry["walkable_boundary"]
    points_to_check: list[tuple[str, tuple[float, float]]] = [
        ("player spawn", tuple(geometry["player"]["spawn"])),
    ]
    for landmark, spec in geometry["quest_landmarks"].items():
        points_to_check.append((f"{landmark} interaction anchor", tuple(spec["interaction_anchor"])))
    for route_name, waypoints in geometry["tested_quest_route"].items():
        for index, waypoint in enumerate(waypoints):
            points_to_check.append((f"{route_name} waypoint {index}", tuple(waypoint)))
    outside_points = [name for name, point in points_to_check if not point_in_polygon(point, boundary)]
    if outside_points:
        failures.append(f"Gameplay points outside boundary: {outside_points}")

    well = geometry["obstacles"][0]
    well_center = tuple(well["center"])
    well_radii = tuple(well["radii"])
    well_interaction = tuple(geometry["quest_landmarks"]["moonwell"]["interaction_anchor"])
    normalized_well_distance = (
        ((well_interaction[0] - well_center[0]) / well_radii[0]) ** 2
        + ((well_interaction[1] - well_center[1]) / well_radii[1]) ** 2
    ) ** 0.5
    if normalized_well_distance <= 1.15:
        failures.append("Moonwell interaction anchor is too close to the blocking ellipse")

    provenance = json.loads((ROOT / "data" / "art_generation_provenance.json").read_text(encoding="utf-8"))
    if provenance["tool_mode"] != "built_in_image_gen":
        failures.append("Unexpected town art generation mode")
    if provenance["output"]["sha256"] != TOWN_HASH:
        failures.append("Town provenance hash disagrees with locked output")

    svg_files = [str(path.relative_to(ROOT)) for path in ROOT.rglob("*.svg")]
    visible_assets = [path for path in (ROOT / "assets").rglob("*") if path.is_file()]
    non_raster_visible_assets = [
        str(path.relative_to(ROOT))
        for path in visible_assets
        if path.suffix.lower() not in {".png", ".import"}
    ]
    scene_text = (ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
    world_text = (ROOT / "scripts" / "town_world.gd").read_text(encoding="utf-8")
    banned_visible_nodes = [token for token in ("ColorRect", "Polygon2D", "Line2D", "NinePatchRect") if token in scene_text]
    procedural_draw_calls = [token for token in ("func _draw", "draw_polygon", "draw_circle", "draw_line", "Image.create") if token in world_text]
    if svg_files:
        failures.append(f"SVG files are forbidden: {svg_files}")
    if non_raster_visible_assets:
        failures.append(f"Non-raster visible assets found: {non_raster_visible_assets}")
    if banned_visible_nodes:
        failures.append(f"Procedural visible node types found: {banned_visible_nodes}")
    if procedural_draw_calls:
        failures.append(f"Procedural visible drawing calls found: {procedural_draw_calls}")

    report = {
        "passed": not failures,
        "failures": failures,
        "assets": assets,
        "geometry_sha256": geometry_hash,
        "expected_geometry_sha256": GEOMETRY_HASH,
        "checked_gameplay_points": len(points_to_check),
        "outside_gameplay_points": outside_points,
        "moonwell_interaction_normalized_distance": normalized_well_distance,
        "visible_art_policy": {
            "svg_file_count": len(svg_files),
            "non_raster_visible_asset_count": len(non_raster_visible_assets),
            "banned_visible_node_types": banned_visible_nodes,
            "procedural_draw_calls": procedural_draw_calls,
            "passed": not (svg_files or non_raster_visible_assets or banned_visible_nodes or procedural_draw_calls),
        },
    }
    output = ROOT / "diagnostics" / "preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
