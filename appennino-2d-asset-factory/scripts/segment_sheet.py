"""
Asset Sheet Segmenter.
Splits multi-asset generation sheets (such as family generation sheets) into individual sprites
using defined grid/scaffold coordinates and non-zero alpha bounding boxes.
"""

import json
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output/family_generation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def segment_family_sheet(sheet_path, layout_grid):
    """
    Slices a 1200x900 family sheet into individual assets based on bounding zones.
    layout_grid: dict of {name: (x0, y0, x1, y1)}
    """
    sheet = Image.open(sheet_path)
    extracted = {}
    
    for name, box in layout_grid.items():
        crop_img = sheet.crop(box)
        out_path = OUTPUT_DIR / f"{name}.png"
        crop_img.save(out_path)
        extracted[name] = out_path
        print(f"--> Extracted {name} from sheet: {box}")
        
    return extracted


if __name__ == "__main__":
    # Standard 6-slot grid
    grid = {
        "family_house_A": (0, 0, 400, 480),
        "family_house_B": (400, 0, 800, 480),
        "family_house_C": (800, 0, 1200, 480),
        "family_stairs": (0, 480, 400, 900),
        "family_fountain": (400, 480, 800, 900),
        "family_wall": (800, 480, 1200, 900),
    }
    sheet_file = BASE_DIR / "scaffolds/scaffold_family_sheet.png"
    if sheet_file.exists():
        segment_family_sheet(sheet_file, grid)
