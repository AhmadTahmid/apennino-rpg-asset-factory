"""
2D Sprite Composite Test Script.
Assembles independently rendered transparent 2D assets into a cohesive 2D RPG screen
to test whether modular sprites without 3D coupling visually co-exist naturally.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

BASE_DIR = Path("d:/Apennino scene").resolve()
ISOLATED_DIR = BASE_DIR / "output" / "isolated_assets"
COMPOSITE_DIR = BASE_DIR / "output" / "2d_composite"


def run_composite_assembly():
    COMPOSITE_DIR.mkdir(parents=True, exist_ok=True)
    canvas_w, canvas_h = 1920, 1080

    # 1. Base Canvas (Warm Mediterranean Sky Gradient)
    base = Image.new("RGBA", (canvas_w, canvas_h), (215, 230, 245, 255))
    draw = ImageDraw.Draw(base)
    # Sky to ground gradient
    for y in range(canvas_h):
        fac = y / canvas_h
        r = int(210 + fac * 15)
        g = int(225 - fac * 15)
        b = int(245 - fac * 45)
        draw.line([(0, y), (canvas_w, y)], fill=(r, g, b, 255))

    # Base Cobblestone Ground Tint (Lower 60% of screen)
    ground_poly = [(0, 420), (canvas_w, 420), (canvas_w, canvas_h), (0, canvas_h)]
    draw.polygon(ground_poly, fill=(185, 175, 160, 255))

    # 2. Load Assets
    def load_sprite(filename):
        p = ISOLATED_DIR / filename
        if p.exists():
            return Image.open(p).convert("RGBA")
        print(f"Warning: {p} missing")
        return None

    img_house_a = load_sprite("house_A.png")
    img_house_b = load_sprite("house_B.png")
    img_house_c = load_sprite("house_C.png")
    img_stairs = load_sprite("stairs.png")
    img_wall = load_sprite("retaining_wall.png")
    img_fountain = load_sprite("fountain.png")
    img_veg = load_sprite("vegetation.png")
    img_props = load_sprite("props.png")

    # 3. Layering Back to Front (Y-sorting)
    # Layer 1: Distant Upper House B (Top Left Background)
    if img_house_b:
        s_hb = img_house_b.resize((620, 620), resample=Image.Resampling.LANCZOS)
        base.paste(s_hb, (380, 20), s_hb)

    # Layer 2: Retaining Wall & Stairs
    if img_wall:
        s_w = img_wall.resize((680, 680), resample=Image.Resampling.LANCZOS)
        base.paste(s_w, (80, 310), s_w)

    if img_stairs:
        s_st = img_stairs.resize((500, 500), resample=Image.Resampling.LANCZOS)
        base.paste(s_st, (360, 310), s_st)

    # Layer 3: Upper Main House A (Top Left Midground)
    if img_house_a:
        s_ha = img_house_a.resize((780, 780), resample=Image.Resampling.LANCZOS)
        base.paste(s_ha, (50, 100), s_ha)

    # Layer 4: Lower Townhouse C (Right Midground)
    if img_house_c:
        s_hc = img_house_c.resize((820, 820), resample=Image.Resampling.LANCZOS)
        base.paste(s_hc, (1020, 240), s_hc)

    # Layer 5: Tree & Vegetation (Far Left & Corners)
    if img_veg:
        s_vg = img_veg.resize((650, 650), resample=Image.Resampling.LANCZOS)
        base.paste(s_vg, (-60, 260), s_vg)

    # Layer 6: Central Piazza Fountain (Mid-Front Center)
    if img_fountain:
        s_f = img_fountain.resize((480, 480), resample=Image.Resampling.LANCZOS)
        base.paste(s_f, (740, 520), s_f)

    # Layer 7: Props (Barrels, Crates, Flower Pots in Foreground)
    if img_props:
        s_pr = img_props.resize((460, 460), resample=Image.Resampling.LANCZOS)
        base.paste(s_pr, (540, 680), s_pr)

    out_file = COMPOSITE_DIR / "assembled_2d_scene.png"
    base.save(out_file)
    print(f"--> 2D Composite successfully created: {out_file}")


if __name__ == "__main__":
    run_composite_assembly()
