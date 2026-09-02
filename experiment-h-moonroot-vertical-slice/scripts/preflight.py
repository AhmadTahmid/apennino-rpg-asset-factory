"""Static, provenance, geometry, and raster-policy checks for Experiment H."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    "assets/moonroot_hollow.png": ("7B4DF1C2EB62D1E1C12893E5F9D4B3E3DF28249C5323F8C6D9C9294194D09674", (1672, 941)),
    "assets/lumenwood_crossing.png": ("1B79BBC4ABE4011860D867EA54A5F2183A1E028F57AD650AEA35DDB7D1D34FF8", (1672, 941)),
    "assets/heartroot_sanctuary.png": ("0234F095E91097B296051DBF73A702C5470F9138148597127B74C649E4A621C0", (1672, 941)),
    "assets/traveler_walk_sheet.png": ("4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876", (144, 256)),
}
MANIFEST_HASH = "2EFC7DD695D9896FFDACF421C1F69C1378E70821BE370FDCDB1C4161558D7008"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def point_in_polygon(point: tuple[float, float], polygon: list[list[float]]) -> bool:
    x, y = point
    inside = False
    previous = len(polygon) - 1
    for current, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[previous]
        if (yi > y) != (yj > y):
            crossing = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < crossing:
                inside = not inside
        previous = current
    return inside


def main() -> int:
    failures: list[str] = []
    assets = {}
    for relative, (expected_hash, expected_size) in EXPECTED.items():
        path = ROOT / relative
        actual_hash = sha256(path)
        with Image.open(path) as image:
            size = image.size
            mode = image.mode
        assets[relative] = {"sha256": actual_hash, "dimensions": size, "mode": mode}
        if actual_hash != expected_hash:
            failures.append(f"Hash mismatch: {relative}")
        if size != expected_size:
            failures.append(f"Dimension mismatch: {relative}")

    manifest_path = ROOT / "data" / "world_manifest.json"
    manifest_hash = sha256(manifest_path)
    if manifest_hash != MANIFEST_HASH:
        failures.append("World manifest hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if set(manifest["locations"]) != {"town", "forest", "sanctuary"}:
        failures.append("Manifest must define town, forest, and sanctuary")
    checked_points = 0
    outside_points = []
    for location_id, spec in manifest["locations"].items():
        points = [("spawn", spec["spawn"])]
        points.extend((f"interaction:{name}", item["anchor"]) for name, item in spec["interactions"].items())
        for route_name, route in spec["tested_routes"].items():
            points.extend((f"route:{route_name}:{index}", point) for index, point in enumerate(route))
        for name, point in points:
            checked_points += 1
            if not point_in_polygon(tuple(point), spec["walkable_boundary"]):
                outside_points.append(f"{location_id}:{name}")
    if outside_points:
        failures.append(f"Gameplay points outside boundaries: {outside_points}")

    provenance = json.loads((ROOT / "data" / "art_generation_provenance.json").read_text(encoding="utf-8"))
    if provenance["tool_mode"] != "built_in_image_gen":
        failures.append("Unexpected environment generation mode")
    for output in provenance["outputs"]:
        project = ROOT / output["project_asset"]
        original = ROOT / output["preserved_original"]
        if sha256(project) != output["sha256"] or sha256(original) != output["sha256"]:
            failures.append(f"Provenance or original mismatch: {output['location_id']}")
        if output["derivative_operations"] not in {"none", "none; project asset is byte-identical to preserved original"}:
            failures.append(f"Unexpected pixel operation: {output['location_id']}")

    svg_files = [str(path.relative_to(ROOT)) for path in ROOT.rglob("*.svg")]
    asset_files = [path for path in (ROOT / "assets").rglob("*") if path.is_file()]
    non_raster_assets = [str(path.relative_to(ROOT)) for path in asset_files if path.suffix.lower() not in {".png", ".import"}]
    scene_text = (ROOT / "scenes" / "main.tscn").read_text(encoding="utf-8")
    runtime_text = (ROOT / "scripts" / "world_runtime.gd").read_text(encoding="utf-8")
    banned_visible_nodes = [token for token in ("type=\"ColorRect\"", "type=\"Polygon2D\"", "type=\"Line2D\"", "type=\"NinePatchRect\"") if token in scene_text]
    procedural_draw_calls = [token for token in ("func _draw", "draw_polygon", "draw_circle", "draw_line", "Image.create") if token in runtime_text]
    if svg_files:
        failures.append(f"SVG files are forbidden: {svg_files}")
    if non_raster_assets:
        failures.append(f"Non-raster visible assets: {non_raster_assets}")
    if banned_visible_nodes:
        failures.append(f"Banned visible node types: {banned_visible_nodes}")
    if procedural_draw_calls:
        failures.append(f"Procedural visible drawing calls: {procedural_draw_calls}")

    report = {
        "passed": not failures,
        "failures": failures,
        "assets": assets,
        "manifest_sha256": manifest_hash,
        "expected_manifest_sha256": MANIFEST_HASH,
        "checked_gameplay_points": checked_points,
        "outside_gameplay_points": outside_points,
        "visible_art_policy": {
            "svg_file_count": len(svg_files),
            "non_raster_asset_count": len(non_raster_assets),
            "banned_visible_node_types": banned_visible_nodes,
            "procedural_draw_calls": procedural_draw_calls,
            "passed": not (svg_files or non_raster_assets or banned_visible_nodes or procedural_draw_calls),
        },
    }
    output = ROOT / "diagnostics" / "preflight.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
