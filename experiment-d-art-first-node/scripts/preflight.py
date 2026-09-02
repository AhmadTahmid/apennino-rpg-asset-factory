"""Verify Experiment D inputs and geometry before running Godot."""

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
    ),
    ROOT / "assets" / "player.png": (
        "21B0086C676A466196D97E72889D13940BE62922A5439624C2605ECE68157102",
        (48, 64),
    ),
}


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
    checked: list[dict] = []
    for path, (expected_hash, expected_size) in EXPECTED.items():
        actual_hash = digest(path) if path.exists() else None
        actual_size = None
        if path.exists():
            with Image.open(path) as image:
                actual_size = image.size
        if actual_hash != expected_hash:
            failures.append(f"Hash mismatch: {path}")
        if actual_size != expected_size:
            failures.append(f"Dimension mismatch: {path}")
        checked.append({"path": str(path), "sha256": actual_hash, "dimensions": actual_size})

    geometry_path = ROOT / "data" / "node_001_geometry.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "experiment_manifest.json").read_text(encoding="utf-8"))
    geometry_hash = digest(geometry_path)
    expected_geometry_hash = manifest["geometry"]["sha256"]
    if geometry_hash != expected_geometry_hash:
        failures.append("Geometry hash does not match experiment manifest")
    boundary = geometry["walkable_boundary"]
    spawn = tuple(geometry["player"]["spawn"])
    if not point_in_polygon(spawn, boundary):
        failures.append("Spawn lies outside walkable boundary")
    for waypoint in geometry["tested_route"]["waypoints"]:
        if not point_in_polygon(tuple(waypoint), boundary):
            failures.append(f"Waypoint lies outside walkable boundary: {waypoint}")

    fountain = geometry["obstacles"][0]
    cx, cy = fountain["center"]
    rx, ry = fountain["radii"]
    for waypoint in geometry["tested_route"]["waypoints"]:
        normalized = ((waypoint[0] - cx) / rx) ** 2 + ((waypoint[1] - cy) / ry) ** 2
        if normalized <= 1.0:
            failures.append(f"Waypoint lies inside fountain obstacle: {waypoint}")

    report = {
        "passed": not failures,
        "failures": failures,
        "checked_assets": checked,
        "geometry_sha256": geometry_hash,
        "expected_geometry_sha256": expected_geometry_hash,
        "geometry_schema_version": geometry["schema_version"],
    }
    output = ROOT / "diagnostics" / "preflight.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
