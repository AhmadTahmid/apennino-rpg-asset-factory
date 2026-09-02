"""Validate Experiment F art provenance, geometry, and inherited contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    ROOT / "assets" / "piazza.png": (
        "FD11B82DEAD94E5BF5CB30F9DD9F718C84C5D9D5AAFD8170483FA222B5CBB54F",
        (1672, 941),
        "RGB",
    ),
    ROOT / "assets" / "belvedere.png": (
        "812AF962D4D567F99B474D9CAC328FCF2E176A973226C3FC3694D08177A992BA",
        (1672, 941),
        "RGB",
    ),
    ROOT / "assets" / "source" / "belvedere_generated_original.png": (
        "812AF962D4D567F99B474D9CAC328FCF2E176A973226C3FC3694D08177A992BA",
        (1672, 941),
        "RGB",
    ),
    ROOT / "assets" / "traveler_walk_sheet.png": (
        "4433340653530325DA27FE497E17226741B926404283383F1006FE7FE0FB6876",
        (144, 256),
        "RGBA",
    ),
    ROOT / "assets" / "southwest_planter_foreground.png": (
        "7A59A290EA28117E6DF18EBDC26AF6B5D801BE120A50B7F7098BBECBE48C7895",
        (1672, 941),
        "RGBA",
    ),
}
PIAZZA_GEOMETRY_HASH = "DF0924A62B4216268C7152070644BBDC9635CF19A4693A2290003C5D6C38CAF4"
BELVEDERE_GEOMETRY_HASH = "02E836B1068E9B398189EA79097B02F3D8EC82AD1022E7E882230C0B0D50BCC4"
PIAZZA_PORTAL = (1095.0, 655.0)
PIAZZA_PORTAL_RADIUS = 28.0


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


def image_style_summary(path: Path) -> dict:
    with Image.open(path) as source:
        rgb = source.convert("RGB")
        hsv = rgb.convert("HSV")
        luminance = rgb.convert("L")
        rgb_stat = ImageStat.Stat(rgb)
        hsv_stat = ImageStat.Stat(hsv)
        luminance_stat = ImageStat.Stat(luminance)
    return {
        "mean_rgb": [round(value, 3) for value in rgb_stat.mean],
        "mean_saturation_0_255": round(hsv_stat.mean[1], 3),
        "mean_luminance_0_255": round(luminance_stat.mean[0], 3),
        "luminance_stddev": round(luminance_stat.stddev[0], 3),
    }


def main() -> int:
    failures: list[str] = []
    checked_assets: list[dict] = []
    for path, (expected_hash, expected_size, expected_mode) in EXPECTED.items():
        if not path.exists():
            failures.append(f"Missing asset: {path}")
            continue
        actual_hash = digest(path)
        with Image.open(path) as image:
            actual_size = image.size
            actual_mode = image.mode
        if actual_hash != expected_hash:
            failures.append(f"Hash mismatch: {path}")
        if actual_size != expected_size:
            failures.append(f"Dimension mismatch: {path}")
        if actual_mode != expected_mode:
            failures.append(f"Mode mismatch: {path}; got {actual_mode}, expected {expected_mode}")
        checked_assets.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": actual_hash,
                "dimensions": list(actual_size),
                "mode": actual_mode,
            }
        )

    piazza_geometry_path = ROOT / "data" / "node_001_geometry.json"
    belvedere_geometry_path = ROOT / "data" / "node_002_geometry.json"
    piazza_hash = digest(piazza_geometry_path)
    belvedere_hash = digest(belvedere_geometry_path)
    if piazza_hash != PIAZZA_GEOMETRY_HASH:
        failures.append("Experiment E piazza geometry changed")
    if belvedere_hash != BELVEDERE_GEOMETRY_HASH:
        failures.append("Belvedere geometry hash changed")

    piazza_geometry = json.loads(piazza_geometry_path.read_text(encoding="utf-8"))
    belvedere_geometry = json.loads(belvedere_geometry_path.read_text(encoding="utf-8"))
    piazza_boundary = piazza_geometry["walkable_boundary"]
    belvedere_boundary = belvedere_geometry["walkable_boundary"]
    if not point_in_polygon(PIAZZA_PORTAL, piazza_boundary):
        failures.append("Piazza portal anchor is outside the inherited walkable boundary")
    for waypoint in belvedere_geometry["tested_route"]["waypoints"]:
        if not point_in_polygon(tuple(waypoint), belvedere_boundary):
            failures.append(f"Belvedere route waypoint lies outside boundary: {waypoint}")
    arrival = tuple(belvedere_geometry["player"]["arrival_spawn"])
    portal = tuple(belvedere_geometry["portal"]["anchor"])
    portal_radius = float(belvedere_geometry["portal"]["interaction_radius_px"])
    if not point_in_polygon(arrival, belvedere_boundary):
        failures.append("Belvedere arrival spawn lies outside boundary")
    if not point_in_polygon(portal, belvedere_boundary):
        failures.append("Belvedere return portal lies outside boundary")
    arrival_distance = ((arrival[0] - portal[0]) ** 2 + (arrival[1] - portal[1]) ** 2) ** 0.5
    if arrival_distance <= portal_radius:
        failures.append("Belvedere arrival spawn would immediately retrigger the return portal")

    provenance_path = ROOT / "data" / "art_generation_provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if provenance["tool_mode"] != "built_in_image_gen":
        failures.append("Unexpected image-generation mode")
    if provenance["output"]["sha256"] != EXPECTED[ROOT / "assets" / "belvedere.png"][0]:
        failures.append("Provenance hash does not match the locked belvedere")
    if provenance["output"]["derivative_operations"] != "none; project asset is byte-identical to preserved original":
        failures.append("Belvedere derivative declaration changed")

    style_summary = {
        "piazza": image_style_summary(ROOT / "assets" / "piazza.png"),
        "belvedere": image_style_summary(ROOT / "assets" / "belvedere.png"),
        "interpretation": "descriptive continuity telemetry only; not treated as proof of stylistic equivalence",
    }
    report = {
        "passed": not failures,
        "failures": failures,
        "checked_assets": checked_assets,
        "piazza_geometry_sha256": piazza_hash,
        "belvedere_geometry_sha256": belvedere_hash,
        "piazza_geometry_unchanged_from_experiment_e": piazza_hash == PIAZZA_GEOMETRY_HASH,
        "belvedere_route_waypoint_count": len(belvedere_geometry["tested_route"]["waypoints"]),
        "belvedere_arrival_to_portal_distance_px": arrival_distance,
        "belvedere_portal_radius_px": portal_radius,
        "style_summary": style_summary,
    }
    output = ROOT / "diagnostics" / "preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
