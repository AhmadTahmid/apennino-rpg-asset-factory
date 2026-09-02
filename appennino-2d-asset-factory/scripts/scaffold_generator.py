"""
Deterministic Structural Scaffold Generator for 2D/2.5D Appennino RPG Assets.
Draws precise 2:1 dimetric isometric architectural scaffolds with semantic metadata.
"""

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent.parent
SCAFFOLDS_DIR = BASE_DIR / "scaffolds"
SCAFFOLDS_DIR.mkdir(parents=True, exist_ok=True)

CANVAS_SIZE = (1024, 1024)
PPM = 96.0  # Pixels per meter
GROUND_Y = 900
CENTER_X = 512

# 2:1 Dimetric vector slopes (26.565 degrees)
# 1m right-down: dx = cos(26.565)*PPM, dy = sin(26.565)*PPM
# In 2:1 projection: dx = 2, dy = 1 per unit step
ISO_DX = math.cos(math.radians(26.565)) * PPM
ISO_DY = math.sin(math.radians(26.565)) * PPM

# Colors for structural semantic zones
COLOR_OUTLINE = (30, 41, 59, 255)       # Slate dark outline
COLOR_WALL_FRONT = (226, 232, 240, 255)  # Light grey front wall
COLOR_WALL_SIDE = (203, 213, 225, 255)   # Slightly darker side wall
COLOR_ROOF = (254, 215, 170, 255)        # Warm peach roof
COLOR_DOOR = (180, 83, 9, 255)           # Terracotta/wood door
COLOR_WINDOW = (147, 197, 253, 255)      # Light blue glass opening
COLOR_SHUTTER = (101, 163, 13, 255)      # Olive green shutters
COLOR_GROUND_LINE = (239, 68, 68, 255)   # Red ground baseline guide


def create_canvas():
    img = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    # Subtle ground guide
    draw.line([(64, GROUND_Y), (960, GROUND_Y)], fill=(200, 200, 200, 180), width=2)
    draw.ellipse([CENTER_X - 6, GROUND_Y - 6, CENTER_X + 6, GROUND_Y + 6], fill=COLOR_GROUND_LINE)
    return img, draw


def generate_house_a():
    """
    House A: 2 floors (5.8m height), gable roof, front door with arch, 3 windows, shutters, balcony.
    """
    img, draw = create_canvas()
    
    # Dimensions in pixels
    w_px = int(4.5 * PPM)   # ~432 px wide
    h_wall = int(5.6 * PPM) # ~538 px wall height (2 floors)
    h_roof = int(1.8 * PPM) # ~173 px roof pitch
    
    # Ground base corner
    x0, y0 = CENTER_X - int(w_px * 0.45), GROUND_Y
    x_right = x0 + w_px
    
    # Front façade polygon
    front_poly = [
        (x0, y0),
        (x_right, y0),
        (x_right, y0 - h_wall),
        (x0, y0 - h_wall)
    ]
    draw.polygon(front_poly, fill=COLOR_WALL_FRONT, outline=COLOR_OUTLINE, width=3)
    
    # Gable roof triangle
    x_ridge = x0 + w_px // 2
    y_ridge = y0 - h_wall - h_roof
    roof_poly = [
        (x0 - 20, y0 - h_wall + 10),
        (x_ridge, y_ridge),
        (x_right + 20, y0 - h_wall + 10)
    ]
    draw.polygon(roof_poly, fill=COLOR_ROOF, outline=COLOR_OUTLINE, width=4)
    # Eaves overhang rafter line
    draw.line([(x0 - 20, y0 - h_wall + 10), (x_right + 20, y0 - h_wall + 10)], fill=COLOR_OUTLINE, width=3)
    
    # Arched doorway (Ground floor center)
    door_w = int(1.05 * PPM) # ~101 px
    door_h = int(2.10 * PPM) # ~202 px
    door_x0 = x0 + int(w_px * 0.15)
    door_y0 = y0
    draw.rectangle([door_x0, door_y0 - door_h + 30, door_x0 + door_w, door_y0], fill=COLOR_DOOR, outline=COLOR_OUTLINE, width=3)
    draw.pieslice([door_x0, door_y0 - door_h, door_x0 + door_w, door_y0 - door_h + 60], 180, 360, fill=COLOR_DOOR, outline=COLOR_OUTLINE, width=3)
    
    # Ground floor window right
    win_w = int(0.75 * PPM)
    win_h = int(1.10 * PPM)
    win_x = x0 + int(w_px * 0.65)
    win_y = y0 - int(0.8 * PPM)
    draw.rectangle([win_x, win_y - win_h, win_x + win_w, win_y], fill=COLOR_WINDOW, outline=COLOR_OUTLINE, width=3)
    # Shutters
    draw.rectangle([win_x - 22, win_y - win_h, win_x, win_y], fill=COLOR_SHUTTER, outline=COLOR_OUTLINE, width=2)
    draw.rectangle([win_x + win_w, win_y - win_h, win_x + win_w + 22, win_y], fill=COLOR_SHUTTER, outline=COLOR_OUTLINE, width=2)
    
    # Floor 2: Balcony & Door (Left)
    balc_w = int(1.4 * PPM)
    balc_h = 35
    balc_x0 = x0 + int(w_px * 0.12)
    balc_y0 = y0 - int(2.8 * PPM)
    # Balcony door
    draw.rectangle([balc_x0 + 15, balc_y0 - door_h + 10, balc_x0 + 15 + door_w, balc_y0], fill=COLOR_WINDOW, outline=COLOR_OUTLINE, width=3)
    # Balcony railing
    draw.rectangle([balc_x0, balc_y0 - balc_h, balc_x0 + balc_w, balc_y0], fill=(71, 85, 105, 255), outline=COLOR_OUTLINE, width=3)
    
    # Floor 2: Window right
    win2_x = x0 + int(w_px * 0.65)
    win2_y = y0 - int(3.5 * PPM)
    draw.rectangle([win2_x, win2_y - win_h, win2_x + win_w, win2_y], fill=COLOR_WINDOW, outline=COLOR_OUTLINE, width=3)
    draw.rectangle([win2_x - 22, win2_y - win_h, win2_x, win2_y], fill=COLOR_SHUTTER, outline=COLOR_OUTLINE, width=2)
    draw.rectangle([win2_x + win_w, win2_y - win_h, win2_x + win_w + 22, win2_y], fill=COLOR_SHUTTER, outline=COLOR_OUTLINE, width=2)
    
    # Save image
    out_path = SCAFFOLDS_DIR / "scaffold_house_A.png"
    img.save(out_path)
    
    # Metadata
    meta = {
        "id": "house_A",
        "semantic_type": "building",
        "canvas_size": CANVAS_SIZE,
        "pixels_per_meter": PPM,
        "ground_anchor": [CENTER_X, GROUND_Y],
        "door_anchor": [door_x0 + door_w // 2, door_y0],
        "door_height_px": door_h,
        "door_height_m": 2.10,
        "world_dimensions_m": {"width": 4.5, "depth": 3.8, "height": 7.4},
        "visual_bounds": [x0 - 25, y_ridge - 10, x_right + 25, y0]
    }
    with open(SCAFFOLDS_DIR / "scaffold_house_A.json", "w") as f:
        json.dump(meta, f, indent=2)
    return out_path, meta


def generate_house_b():
    """
    House B: 3 floors narrow tower, arched door, chimney, brown shutters.
    """
    img, draw = create_canvas()
    w_px = int(3.6 * PPM)   # ~345 px
    h_wall = int(7.8 * PPM) # ~748 px wall height (3 floors)
    h_roof = int(1.4 * PPM) # ~134 px
    
    x0, y0 = CENTER_X - int(w_px * 0.5), GROUND_Y
    x_right = x0 + w_px
    
    # Front façade
    front_poly = [(x0, y0), (x_right, y0), (x_right, y0 - h_wall), (x0, y0 - h_wall)]
    draw.polygon(front_poly, fill=COLOR_WALL_FRONT, outline=COLOR_OUTLINE, width=3)
    
    # Roof
    x_ridge = x0 + w_px // 2
    y_ridge = y0 - h_wall - h_roof
    roof_poly = [(x0 - 18, y0 - h_wall + 8), (x_ridge, y_ridge), (x_right + 18, y0 - h_wall + 8)]
    draw.polygon(roof_poly, fill=COLOR_ROOF, outline=COLOR_OUTLINE, width=4)
    draw.line([(x0 - 18, y0 - h_wall + 8), (x_right + 18, y0 - h_wall + 8)], fill=COLOR_OUTLINE, width=3)
    
    # Chimney on left
    draw.rectangle([x0 + 20, y_ridge - 40, x0 + 65, y0 - h_wall], fill=(168, 162, 158, 255), outline=COLOR_OUTLINE, width=3)
    
    # Arched door (Center)
    door_w = int(1.05 * PPM)
    door_h = int(2.10 * PPM)
    door_x0 = x0 + (w_px - door_w) // 2
    door_y0 = y0
    draw.rectangle([door_x0, door_y0 - door_h + 30, door_x0 + door_w, door_y0], fill=COLOR_DOOR, outline=COLOR_OUTLINE, width=3)
    draw.pieslice([door_x0, door_y0 - door_h, door_x0 + door_w, door_y0 - door_h + 60], 180, 360, fill=COLOR_DOOR, outline=COLOR_OUTLINE, width=3)
    
    # Windows on floors 2 & 3
    win_w = int(0.72 * PPM)
    win_h = int(1.05 * PPM)
    for fl_y in [y0 - int(3.2 * PPM), y0 - int(5.6 * PPM)]:
        wx = x0 + (w_px - win_w) // 2
        draw.rectangle([wx, fl_y - win_h, wx + win_w, fl_y], fill=COLOR_WINDOW, outline=COLOR_OUTLINE, width=3)
        draw.rectangle([wx - 20, fl_y - win_h, wx, fl_y], fill=(120, 80, 50, 255), outline=COLOR_OUTLINE, width=2)
        draw.rectangle([wx + win_w, fl_y - win_h, wx + win_w + 20, fl_y], fill=(120, 80, 50, 255), outline=COLOR_OUTLINE, width=2)
        
    out_path = SCAFFOLDS_DIR / "scaffold_house_B.png"
    img.save(out_path)
    
    meta = {
        "id": "house_B",
        "semantic_type": "building",
        "canvas_size": CANVAS_SIZE,
        "pixels_per_meter": PPM,
        "ground_anchor": [CENTER_X, GROUND_Y],
        "door_anchor": [door_x0 + door_w // 2, door_y0],
        "door_height_px": door_h,
        "door_height_m": 2.10,
        "world_dimensions_m": {"width": 3.6, "depth": 3.6, "height": 9.2},
        "visual_bounds": [x0 - 20, y_ridge - 45, x_right + 20, y0]
    }
    with open(SCAFFOLDS_DIR / "scaffold_house_B.json", "w") as f:
        json.dump(meta, f, indent=2)
    return out_path, meta


def generate_house_c():
    """
    House C: 2 floors wide townhouse, arched ground shop opening, hip roof.
    """
    img, draw = create_canvas()
    w_px = int(5.4 * PPM)   # ~518 px
    h_wall = int(5.4 * PPM) # ~518 px
    h_roof = int(1.5 * PPM)
    
    x0, y0 = CENTER_X - int(w_px * 0.5), GROUND_Y
    x_right = x0 + w_px
    
    # Front façade
    front_poly = [(x0, y0), (x_right, y0), (x_right, y0 - h_wall), (x0, y0 - h_wall)]
    draw.polygon(front_poly, fill=COLOR_WALL_FRONT, outline=COLOR_OUTLINE, width=3)
    
    # Hip roof trapezoid
    roof_poly = [
        (x0 - 18, y0 - h_wall + 8),
        (x0 + 80, y0 - h_wall - h_roof),
        (x_right - 80, y0 - h_wall - h_roof),
        (x_right + 18, y0 - h_wall + 8)
    ]
    draw.polygon(roof_poly, fill=COLOR_ROOF, outline=COLOR_OUTLINE, width=4)
    draw.line([(x0 - 18, y0 - h_wall + 8), (x_right + 18, y0 - h_wall + 8)], fill=COLOR_OUTLINE, width=3)
    
    # Wide arched ground shop door (Right side)
    door_w = int(1.30 * PPM)
    door_h = int(2.10 * PPM)
    door_x0 = x0 + int(w_px * 0.55)
    door_y0 = y0
    draw.rectangle([door_x0, door_y0 - door_h + 35, door_x0 + door_w, door_y0], fill=COLOR_DOOR, outline=COLOR_OUTLINE, width=3)
    draw.pieslice([door_x0, door_y0 - door_h, door_x0 + door_w, door_y0 - door_h + 70], 180, 360, fill=COLOR_DOOR, outline=COLOR_OUTLINE, width=3)
    
    # Left ground window
    win_w = int(0.85 * PPM)
    win_h = int(1.15 * PPM)
    draw.rectangle([x0 + 40, y0 - win_h - 40, x0 + 40 + win_w, y0 - 40], fill=COLOR_WINDOW, outline=COLOR_OUTLINE, width=3)
    
    # Floor 2: Two symmetrical shuttered windows with flower boxes
    for wx in [x0 + 50, x_right - 50 - win_w]:
        wy = y0 - int(3.3 * PPM)
        draw.rectangle([wx, wy - win_h, wx + win_w, wy], fill=COLOR_WINDOW, outline=COLOR_OUTLINE, width=3)
        draw.rectangle([wx - 22, wy - win_h, wx, wy], fill=COLOR_SHUTTER, outline=COLOR_OUTLINE, width=2)
        draw.rectangle([wx + win_w, wy - win_h, wx + win_w + 22, wy], fill=COLOR_SHUTTER, outline=COLOR_OUTLINE, width=2)
        # Flower box
        draw.rectangle([wx - 10, wy, wx + win_w + 10, wy + 20], fill=(220, 38, 38, 255), outline=COLOR_OUTLINE, width=2)
        
    out_path = SCAFFOLDS_DIR / "scaffold_house_C.png"
    img.save(out_path)
    
    meta = {
        "id": "house_C",
        "semantic_type": "building",
        "canvas_size": CANVAS_SIZE,
        "pixels_per_meter": PPM,
        "ground_anchor": [CENTER_X, GROUND_Y],
        "door_anchor": [door_x0 + door_w // 2, door_y0],
        "door_height_px": door_h,
        "door_height_m": 2.10,
        "world_dimensions_m": {"width": 5.4, "depth": 4.2, "height": 6.9},
        "visual_bounds": [x0 - 20, y0 - h_wall - h_roof - 5, x_right + 20, y0]
    }
    with open(SCAFFOLDS_DIR / "scaffold_house_C.json", "w") as f:
        json.dump(meta, f, indent=2)
    return out_path, meta


def generate_stairs_and_wall():
    """
    Stairs & Retaining Wall scaffold: stone steps climbing to a 2.4m elevation.
    """
    img, draw = create_canvas()
    
    # Retaining wall block
    wall_w = int(3.5 * PPM)
    wall_h = int(2.4 * PPM) # 230 px
    x_wall = CENTER_X - int(2.5 * PPM)
    y_wall = GROUND_Y
    
    draw.polygon([
        (x_wall, y_wall),
        (x_wall + wall_w, y_wall),
        (x_wall + wall_w, y_wall - wall_h),
        (x_wall, y_wall - wall_h)
    ], fill=(148, 163, 184, 255), outline=COLOR_OUTLINE, width=3)
    # Coping stones
    draw.rectangle([x_wall - 10, y_wall - wall_h - 18, x_wall + wall_w + 10, y_wall - wall_h], fill=(203, 213, 225, 255), outline=COLOR_OUTLINE, width=3)
    
    # Stair steps climbing up to the right
    x_stair = x_wall + wall_w
    steps = 12
    step_riser = int(0.185 * PPM) # 18 px
    step_tread = int(0.28 * PPM)  # 27 px
    
    curr_x = x_stair - (steps * step_tread) // 2
    curr_y = GROUND_Y
    for i in range(steps):
        draw.rectangle([curr_x, curr_y - step_riser, curr_x + step_tread, curr_y], fill=(226, 232, 240, 255), outline=COLOR_OUTLINE, width=2)
        curr_x += step_tread
        curr_y -= step_riser
        
    out_path = SCAFFOLDS_DIR / "scaffold_stairs.png"
    img.save(out_path)
    
    meta = {
        "id": "stairs_and_wall",
        "semantic_type": "infrastructure",
        "canvas_size": CANVAS_SIZE,
        "pixels_per_meter": PPM,
        "ground_anchor": [CENTER_X, GROUND_Y],
        "height_m": 2.40,
        "world_dimensions_m": {"width": 5.8, "depth": 2.5, "height": 2.55},
        "visual_bounds": [x_wall - 15, y_wall - wall_h - 25, curr_x + 15, GROUND_Y]
    }
    with open(SCAFFOLDS_DIR / "scaffold_stairs.json", "w") as f:
        json.dump(meta, f, indent=2)
    return out_path, meta


def generate_fountain():
    """
    Fountain scaffold: carved octagonal stone basin with central spraying water finial.
    """
    img, draw = create_canvas()
    
    r_basin_x = int(1.4 * PPM) # ~134 px radius
    r_basin_y = int(0.65 * PPM) # ~62 px (dimetric squashed ellipse)
    h_basin = 55
    cx, cy = CENTER_X, GROUND_Y - 40
    
    # Outer basin rim
    draw.polygon([
        (cx - r_basin_x, cy),
        (cx - int(r_basin_x * 0.7), cy + r_basin_y),
        (cx + int(r_basin_x * 0.7), cy + r_basin_y),
        (cx + r_basin_x, cy),
        (cx + r_basin_x, cy + h_basin),
        (cx + int(r_basin_x * 0.7), cy + r_basin_y + h_basin),
        (cx - int(r_basin_x * 0.7), cy + r_basin_y + h_basin),
        (cx - r_basin_x, cy + h_basin)
    ], fill=(203, 213, 225, 255), outline=COLOR_OUTLINE, width=3)
    
    # Water surface ellipse
    draw.ellipse([cx - r_basin_x + 10, cy - r_basin_y + 10, cx + r_basin_x - 10, cy + r_basin_y - 10], fill=(56, 189, 248, 255), outline=COLOR_OUTLINE, width=2)
    
    # Central tiered pedestal and plume
    ped_w = 40
    ped_h = 110
    draw.rectangle([cx - ped_w // 2, cy - ped_h, cx + ped_w // 2, cy], fill=(148, 163, 184, 255), outline=COLOR_OUTLINE, width=3)
    # Water plume
    draw.pieslice([cx - 30, cy - ped_h - 60, cx + 30, cy - ped_h], 180, 360, fill=(224, 242, 254, 255), outline=(56, 189, 248, 255), width=2)
    
    out_path = SCAFFOLDS_DIR / "scaffold_fountain.png"
    img.save(out_path)
    
    meta = {
        "id": "fountain",
        "semantic_type": "prop_monument",
        "canvas_size": CANVAS_SIZE,
        "pixels_per_meter": PPM,
        "ground_anchor": [CENTER_X, GROUND_Y],
        "height_m": 2.2,
        "world_dimensions_m": {"width": 2.8, "depth": 2.8, "height": 2.2},
        "visual_bounds": [cx - r_basin_x - 10, cy - ped_h - 65, cx + r_basin_x + 10, cy + h_basin + 5]
    }
    with open(SCAFFOLDS_DIR / "scaffold_fountain.json", "w") as f:
        json.dump(meta, f, indent=2)
    return out_path, meta


def generate_family_sheet():
    """
    Combined family sheet scaffold: 6 zones on one 1200x900 canvas.
    [House A | House B | House C]
    [Stairs  | Fountain| Retaining Wall]
    """
    w_sheet, h_sheet = 1200, 900
    img = Image.new("RGBA", (w_sheet, h_sheet), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Grid boundaries
    draw.line([(400, 0), (400, 900)], fill=(148, 163, 184, 180), width=2)
    draw.line([(800, 0), (800, 900)], fill=(148, 163, 184, 180), width=2)
    draw.line([(0, 480), (1200, 480)], fill=(148, 163, 184, 180), width=2)
    
    # Paste downscaled scaffolds into each slot
    ha = Image.open(SCAFFOLDS_DIR / "scaffold_house_A.png").resize((380, 380))
    hb = Image.open(SCAFFOLDS_DIR / "scaffold_house_B.png").resize((380, 380))
    hc = Image.open(SCAFFOLDS_DIR / "scaffold_house_C.png").resize((380, 380))
    st = Image.open(SCAFFOLDS_DIR / "scaffold_stairs.png").resize((380, 340))
    ft = Image.open(SCAFFOLDS_DIR / "scaffold_fountain.png").resize((380, 340))
    
    img.paste(ha, (10, 80), ha)
    img.paste(hb, (410, 80), hb)
    img.paste(hc, (810, 80), hc)
    img.paste(st, (10, 500), st)
    img.paste(ft, (410, 500), ft)
    
    # Label each slot
    draw.text((30, 20), "SLOT 1: HOUSE A", fill=COLOR_OUTLINE)
    draw.text((430, 20), "SLOT 2: HOUSE B", fill=COLOR_OUTLINE)
    draw.text((830, 20), "SLOT 3: HOUSE C", fill=COLOR_OUTLINE)
    draw.text((30, 490), "SLOT 4: STAIRS & WALL", fill=COLOR_OUTLINE)
    draw.text((430, 490), "SLOT 5: FOUNTAIN", fill=COLOR_OUTLINE)
    draw.text((830, 490), "SLOT 6: RETAINING WALL", fill=COLOR_OUTLINE)
    
    out_path = SCAFFOLDS_DIR / "scaffold_family_sheet.png"
    img.save(out_path)
    print("--> Scaffolds generated successfully!")


if __name__ == "__main__":
    generate_house_a()
    generate_house_b()
    generate_house_c()
    generate_stairs_and_wall()
    generate_fountain()
    generate_family_sheet()
