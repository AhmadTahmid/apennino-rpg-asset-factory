"""
Native 2D Composition Builder.
Assembles a full 1920x1080 town scene entirely from the normalized 2D outputs using depth sorting
and canonical anchor coordinates (strictly without arbitrary eyeballed scaling).
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent.parent
NORM_DIR = BASE_DIR / "output/normalized"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCENE_W, SCENE_H = 1920, 1080


def create_plaza_background():
    """Generates a warm cobblestone and sky gradient background for the 2D composite."""
    bg = Image.new("RGBA", (SCENE_W, SCENE_H), (240, 244, 248, 255))
    draw = ImageDraw.Draw(bg)
    
    # Sky gradient at top
    for y in range(400):
        t = y / 400.0
        r = int(217 + (235 - 217) * t)
        g = int(237 + (230 - 237) * t)
        b = int(247 + (220 - 247) * t)
        draw.line([(0, y), (SCENE_W, y)], fill=(r, g, b, 255))
        
    # Cobblestone ground plane (Y=350 to Y=1080)
    for y in range(350, SCENE_H):
        t = (y - 350) / float(SCENE_H - 350)
        # Warm cobblestone gradient
        r = int(216 - 25 * t)
        g = int(209 - 25 * t)
        b = int(196 - 25 * t)
        draw.line([(0, y), (SCENE_W, y)], fill=(r, g, b, 255))
        
    # Terrace elevation dividing line (Upper terrace at Y=480, lower plaza at Y=750)
    draw.polygon([(0, 440), (820, 320), (820, 520), (0, 640)], fill=(190, 182, 168, 255))
    return bg


def build_native_composite():
    print("--> Assembling native 2D composite...")
    composite = create_plaza_background()
    
    # Layer stack ordered from back to front (Y-sorted)
    # Each entry: (filename, anchor_x, anchor_y, z_order)
    # Assets are pasted using their canonical anchor (512, 900) relative to placement position
    placements = [
        # Upper terrace background (far depth)
        ("house_B.png", 320, 480),     # Narrow tower on upper terrace
        ("vegetation.png", 180, 540),  # Olive tree behind wall
        ("retaining_wall.png", 420, 620), # Terrace retaining wall
        ("stairs.png", 680, 660),      # Stairs climbing from plaza to terrace
        
        # Midground townhouses
        ("house_A.png", 1120, 580),    # 2-floor stone house mid-right
        ("house_C.png", 1540, 720),    # Wide townhouse front-right
        
        # Plaza center
        ("fountain.png", 780, 860),    # Central piazza fountain
        
        # Foreground street furniture
        ("props.png", 1080, 940),      # Barrels, market crates, lanterns
    ]
    
    for filename, place_x, place_y in placements:
        asset_path = NORM_DIR / filename
        if not asset_path.exists():
            print(f"Warning: {filename} not found, skipping...")
            continue
            
        sprite = Image.open(asset_path)
        # Align canonical anchor (512, 900) to target (place_x, place_y)
        paste_x = place_x - 512
        paste_y = place_y - 900
        composite.paste(sprite, (paste_x, paste_y), sprite)
        print(f"  Pasted {filename} at ({place_x}, {place_y})")
        
    out_path = OUTPUT_DIR / "native_composite.png"
    composite.save(out_path)
    print(f"--> Native composite saved to {out_path}")
    return out_path


def build_hybrid_scene():
    """
    Combines native 2D structured town assets with the reference distant mountain landscape backdrop.
    """
    print("--> Generating hybrid scene with painterly landscape backdrop...")
    # Load atmospheric depth reference crop
    ref_depth = Image.open(BASE_DIR / "reference/overview.png")
    # Take upper landscape portion and scale to 1920x1080
    w, h = ref_depth.size
    landscape_bg = ref_depth.crop((0, 0, w, int(h * 0.55))).resize((SCENE_W, int(SCENE_H * 0.65)), Image.Resampling.LANCZOS)
    
    hybrid = Image.new("RGBA", (SCENE_W, SCENE_H), (217, 237, 247, 255))
    hybrid.paste(landscape_bg, (0, 0))
    
    # Ground plane overlay
    draw = ImageDraw.Draw(hybrid)
    for y in range(int(SCENE_H * 0.50), SCENE_H):
        t = (y - int(SCENE_H * 0.50)) / float(SCENE_H * 0.50)
        r = int(216 - 25 * t)
        g = int(209 - 25 * t)
        b = int(196 - 25 * t)
        draw.line([(0, y), (SCENE_W, y)], fill=(r, g, b, 255))
        
    # Paste the foreground assets from native composite
    placements = [
        ("house_B.png", 280, 520),
        ("vegetation.png", 140, 560),
        ("retaining_wall.png", 380, 640),
        ("stairs.png", 640, 680),
        ("house_A.png", 1160, 600),
        ("house_C.png", 1580, 740),
        ("fountain.png", 780, 880),
        ("props.png", 1080, 950),
    ]
    
    for filename, place_x, place_y in placements:
        asset_path = NORM_DIR / filename
        if not asset_path.exists():
            continue
        sprite = Image.open(asset_path)
        paste_x = place_x - 512
        paste_y = place_y - 900
        hybrid.paste(sprite, (paste_x, paste_y), sprite)
        
    out_path = OUTPUT_DIR / "hybrid_scene.png"
    hybrid.save(out_path)
    print(f"--> Hybrid scene saved to {out_path}")
    return out_path


if __name__ == "__main__":
    build_native_composite()
    build_hybrid_scene()
