"""Create non-scoring visual diagnostics for the OpenAI calibration image."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


EXP_DIR = Path(__file__).resolve().parent.parent
SOURCE = EXP_DIR.parent / "output" / "scene" / "clean.png"
CANDIDATE = EXP_DIR / "outputs" / "openai_calibration" / "openai_structure_01.png"
DIAGNOSTICS = EXP_DIR / "outputs" / "diagnostics"


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        return ImageOps.fit(source.convert("RGB"), size, method=Image.Resampling.LANCZOS)


def main() -> int:
    if not SOURCE.exists() or not CANDIDATE.exists():
        print("Calibration source or candidate is missing.")
        return 1

    DIAGNOSTICS.mkdir(parents=True, exist_ok=True)
    source_full = fit(SOURCE, (1920, 1080))
    candidate_full = fit(CANDIDATE, (1920, 1080))

    source_small = source_full.resize((960, 540), Image.Resampling.LANCZOS)
    candidate_small = candidate_full.resize((960, 540), Image.Resampling.LANCZOS)
    comparison = Image.new("RGB", (1920, 580), (24, 27, 33))
    comparison.paste(source_small, (0, 40))
    comparison.paste(candidate_small, (960, 40))
    draw = ImageDraw.Draw(comparison)
    draw.text((20, 12), "STRUCTURAL SOURCE", fill=(255, 255, 255))
    draw.text((980, 12), "OPENAI CALIBRATION — UNSCORED", fill=(255, 255, 255))
    comparison.save(DIAGNOSTICS / "openai_calibration_side_by_side.png")

    source_edges = source_full.convert("L").filter(ImageFilter.FIND_EDGES)
    source_edges = source_edges.point(lambda value: 150 if value >= 32 else 0)
    magenta = Image.new("RGBA", source_full.size, (255, 0, 180, 0))
    magenta.putalpha(source_edges)
    overlay = Image.alpha_composite(candidate_full.convert("RGBA"), magenta)
    overlay.convert("RGB").save(DIAGNOSTICS / "openai_calibration_source_edge_overlay.png")
    print("Created OpenAI calibration side-by-side and source-edge overlay diagnostics.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
