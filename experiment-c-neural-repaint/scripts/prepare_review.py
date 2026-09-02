"""Verify candidate provenance and create anonymous review diagnostics."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


EXP_DIR = Path(__file__).resolve().parent.parent
ORIGINALS = EXP_DIR / "outputs" / "originals"
DIAGNOSTICS = EXP_DIR / "outputs" / "diagnostics"
PROVENANCE = EXP_DIR / "outputs" / "provenance.json"
MANIFEST = EXP_DIR / "experiment_manifest.json"
SOURCE = EXP_DIR.parent / "output" / "scene" / "clean.png"
EXPECTED = ["control_01.png", "control_02.png", "structure_01.png", "structure_02.png"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest.upper()


def fit_16x9(path: Path) -> Image.Image:
    with Image.open(path) as source:
        rgb = source.convert("RGB")
        return ImageOps.fit(rgb, (960, 540), method=Image.Resampling.LANCZOS)


def main() -> int:
    DIAGNOSTICS.mkdir(parents=True, exist_ok=True)
    failures = []
    if not PROVENANCE.exists():
        failures.append("Missing outputs/provenance.json")
        provenance_runs = []
    else:
        provenance_runs = json.loads(PROVENANCE.read_text(encoding="utf-8")).get("runs", [])

    provenance_by_name = {run.get("candidate"): run for run in provenance_runs}
    verified = []
    for name in EXPECTED:
        path = ORIGINALS / name
        if not path.exists():
            failures.append(f"Missing candidate: {name}")
            continue
        with Image.open(path) as image:
            dimensions = [image.width, image.height]
        digest = sha256(path)
        run = provenance_by_name.get(name)
        if not run:
            failures.append(f"Missing provenance entry: {name}")
        else:
            required = ["timestamp", "input_paths", "exact_prompt", "original_dimensions_px"]
            for field in required:
                if run.get(field) in (None, "", []):
                    failures.append(f"Missing provenance field {field}: {name}")
            if run.get("sha256") and run["sha256"].upper() != digest:
                failures.append(f"Provenance hash mismatch: {name}")
        verified.append({"candidate": name, "sha256": digest, "dimensions_px": dimensions})

    if failures:
        print(json.dumps({"passed": False, "failures": failures, "verified": verified}, indent=2))
        return 1

    labels = ["A", "B", "C", "D"]
    shuffled = EXPECTED[:]
    random.Random("appennino-experiment-c-locked").shuffle(shuffled)
    mapping = dict(zip(labels, shuffled))
    (DIAGNOSTICS / "blind_mapping.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    sheet = Image.new("RGB", (1920, 1160), (24, 27, 33))
    draw = ImageDraw.Draw(sheet)
    for index, label in enumerate(labels):
        candidate = fit_16x9(ORIGINALS / mapping[label])
        x = (index % 2) * 960
        y = (index // 2) * 580
        sheet.paste(candidate, (x, y + 40))
        draw.text((x + 20, y + 10), f"Candidate {label}", fill=(255, 255, 255))
    sheet.save(DIAGNOSTICS / "blind_review_sheet.png")
    sheet.save(DIAGNOSTICS / "blind_review_sheet.jpg", quality=90)

    source_edges = fit_16x9(SOURCE).convert("L").filter(ImageFilter.FIND_EDGES)
    source_edges = source_edges.point(lambda value: 255 if value >= 32 else 0)
    magenta = Image.new("RGBA", source_edges.size, (255, 0, 180, 0))
    magenta.putalpha(source_edges.point(lambda value: 150 if value else 0))
    for label, name in mapping.items():
        candidate = fit_16x9(ORIGINALS / name).convert("RGBA")
        overlay = Image.alpha_composite(candidate, magenta)
        overlay.save(DIAGNOSTICS / f"candidate_{label}_source_edge_overlay.png")
        overlay.convert("RGB").save(
            DIAGNOSTICS / f"candidate_{label}_source_edge_overlay.jpg", quality=90
        )

    result = {"passed": True, "verified": verified, "anonymous_labels": labels}
    (DIAGNOSTICS / "review_preparation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
