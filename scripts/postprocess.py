"""
Post-processing script using system Python (Pillow) to generate
Variant B (Pixel-ish) and Variant C (Painterly / Illustrated).
"""

from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

BASE_DIR = Path("d:/Apennino scene").resolve()
SCENE_DIR = BASE_DIR / "output" / "scene"


def process_pixelish():
    lowres_path = SCENE_DIR / "pixel_lowres.png"
    out_path = SCENE_DIR / "pixelish.png"
    if not lowres_path.exists():
        print(f"Warning: {lowres_path} does not exist.")
        return

    with Image.open(lowres_path) as img:
        # 1. Upscale 4x using NEAREST neighbor for crisp pixel art edges
        upscaled = img.resize((1920, 1080), resample=Image.Resampling.NEAREST)
        
        # 2. Boost color vibrance and slight contrast for JRPG palette
        enh_color = ImageEnhance.Color(upscaled)
        vibrant = enh_color.enhance(1.22)
        enh_cont = ImageEnhance.Contrast(vibrant)
        final_pixel = enh_cont.enhance(1.08)

        final_pixel.save(out_path)
        print(f"--> Pixel-ish variant successfully generated: {out_path}")


def process_painterly():
    clean_path = SCENE_DIR / "clean.png"
    out_path = SCENE_DIR / "painterly.png"
    if not clean_path.exists():
        print(f"Warning: {clean_path} does not exist.")
        return

    with Image.open(clean_path) as img:
        # 1. Warm color grading
        enh_cont = ImageEnhance.Contrast(img)
        img_c = enh_cont.enhance(1.14)
        enh_col = ImageEnhance.Color(img_c)
        img_warm = enh_col.enhance(1.25)

        # 2. Soft architectural edge emphasis
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageOps.invert(edges)
        enh_edge = ImageEnhance.Contrast(edges)
        edge_mask = enh_edge.enhance(2.2).convert('RGB')

        # 3. Painterly composite & soft sharp pass
        blended = Image.blend(img_warm, img, 0.18)
        # Multiply subtle edge ink lines
        inked = ImageOps.colorize(edge_mask.convert('L'), black="#2A2421", white="#FFFFFF")
        final_painterly = Image.blend(blended, inked, 0.08)
        final_painterly = final_painterly.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))

        final_painterly.save(out_path)
        print(f"--> Painterly variant successfully generated: {out_path}")


if __name__ == "__main__":
    process_pixelish()
    process_painterly()
