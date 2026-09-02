"""Validate and fingerprint Experiment C inputs before any paid generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageStat


EXP_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = EXP_DIR / "experiment_manifest.json"
DIAG_DIR = EXP_DIR / "outputs" / "diagnostics"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def resolved(relative_to_experiment: str) -> Path:
    return (EXP_DIR / relative_to_experiment).resolve()


def image_record(path: Path) -> dict:
    with Image.open(path) as source:
        rgb = source.convert("RGB")
        stats = ImageStat.Stat(rgb)
        gray = rgb.convert("L")
        edge = gray.filter(ImageFilter.FIND_EDGES)
        edge_hist = edge.histogram()
        edge_pixels = sum(edge_hist[32:])
        total = rgb.width * rgb.height
        return {
            "path": str(path),
            "sha256": sha256(path),
            "dimensions_px": [rgb.width, rgb.height],
            "channel_mean": [round(v, 3) for v in stats.mean],
            "channel_stddev": [round(v, 3) for v in stats.stddev],
            "edge_coverage_over_32": round(edge_pixels / total, 5),
        }


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    DIAG_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    failures = []
    for item in manifest["inputs"]:
        path = resolved(item["path"])
        if not path.exists():
            failures.append(f"Missing input: {path}")
            continue
        record = image_record(path)
        record["role"] = item["role"]
        record["expected_sha256"] = item["sha256"]
        record["hash_matches_manifest"] = record["sha256"] == item["sha256"]
        if not record["hash_matches_manifest"]:
            failures.append(f"Hash mismatch: {path}")
        records.append(record)

    structural = next((r for r in records if r["role"] == "structural_source"), None)
    if structural:
        if structural["dimensions_px"] != manifest["canvas"]["evaluation_size_px"]:
            failures.append("Structural source is not 1920x1080.")
        if min(structural["channel_stddev"]) < 18.0:
            failures.append("Structural source has insufficient visual variance and may be blank.")
        coverage = structural["edge_coverage_over_32"]
        if not 0.03 <= coverage <= 0.65:
            failures.append(f"Structural edge coverage is implausible: {coverage}")

        source_path = Path(structural["path"])
        with Image.open(source_path) as source:
            rgb = source.convert("RGB")
            edge = rgb.convert("L").filter(ImageFilter.FIND_EDGES)
            edge = edge.point(lambda value: 255 if value >= 32 else 0)
            edge.save(DIAG_DIR / "structural_source_edges.png")

            guide = rgb.copy()
            draw = ImageDraw.Draw(guide)
            for name, point in manifest["structural_landmarks_px"].items():
                x, y = point
                radius = 14
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(255, 0, 180), width=5)
                draw.text((x + 18, y - 10), name, fill=(255, 0, 180), stroke_width=2, stroke_fill=(255, 255, 255))
            guide.save(DIAG_DIR / "structural_landmark_guide.png")

    report = {
        "experiment_id": manifest["experiment_id"],
        "passed": not failures,
        "failures": failures,
        "inputs": records,
    }
    (DIAG_DIR / "preflight_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
