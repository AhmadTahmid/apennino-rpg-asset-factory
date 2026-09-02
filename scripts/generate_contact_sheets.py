"""
Review Bundle and Contact Sheet Generator.
Assembles review_bundle/ with key evidence and creates 3 high-resolution labeled contact sheets.
"""

import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLE_DIR = REPO_ROOT / "review_bundle"
BUNDLE_DIR.mkdir(parents=True, exist_ok=True)


def copy_bundle_files():
    print("--> Copying key review bundle images...")
    copies = [
        (REPO_ROOT / "reference_frames/frame_001.jpg", BUNDLE_DIR / "01_reference.jpg"),
        (REPO_ROOT / "appennino-2d-asset-factory/output/raw_baseline/house_A.png", BUNDLE_DIR / "02_raw_baseline.png"),
        (REPO_ROOT / "appennino-2d-asset-factory/output/style_anchored/house_A.png", BUNDLE_DIR / "03_style_anchored.png"),
        (REPO_ROOT / "appennino-2d-asset-factory/scaffolds/scaffold_house_A.png", BUNDLE_DIR / "04_constrained_scaffold.png"),
        (REPO_ROOT / "appennino-2d-asset-factory/scaffolds/scaffold_family_sheet.png", BUNDLE_DIR / "05_family_sheet.png"),
        (REPO_ROOT / "appennino-2d-asset-factory/output/native_composite.png", BUNDLE_DIR / "06_native_composite.png"),
        (REPO_ROOT / "appennino-2d-asset-factory/output/hybrid_scene.png", BUNDLE_DIR / "07_hybrid_scene.png"),
        (REPO_ROOT / "output/scene/clean.png", BUNDLE_DIR / "08_blender_clean.png"),
        (REPO_ROOT / "output/scene/painterly.png", BUNDLE_DIR / "09_blender_painterly.png"),
        (REPO_ROOT / "output/scene/pixelish.png", BUNDLE_DIR / "10_blender_pixelish.png"),
    ]
    for src, dst in copies:
        if src.exists():
            shutil.copy(src, dst)
            print(f"  Copied {src.name} -> {dst.name}")
        else:
            print(f"  WARNING: {src} not found!")


def create_master_contact_sheet():
    """
    Creates review_bundle/contact_sheet.jpg (2x4 grid of the major pipelines).
    """
    print("--> Building master contact sheet...")
    card_w, card_h = 640, 480
    header_h = 70
    cols, rows = 4, 2
    margin = 24
    
    total_w = cols * card_w + (cols + 1) * margin
    total_h = rows * (card_h + header_h) + (rows + 1) * margin + 100
    
    sheet = Image.new("RGB", (total_w, total_h), color=(18, 20, 24))
    draw = ImageDraw.Draw(sheet)
    
    # Title banner
    draw.text((margin, 25), "APPENNINO RPG ASSET FACTORY — EXPERIMENT COMPARISON CONTACT SHEET", fill=(245, 158, 11))
    draw.text((margin, 55), "Direct Empirical Comparison: Reference Target vs 2D AI Baselines vs 2D Constrained vs 3D Blender Factory", fill=(156, 163, 175))
    
    items = [
        ("01. REFERENCE TARGET", "Original Appennino hill-town video frame", BUNDLE_DIR / "01_reference.jpg"),
        ("02. RAW AI BASELINE", "Prompt-only generation (Gemini 3.1 Flash Image)", BUNDLE_DIR / "02_raw_baseline.png"),
        ("03. STYLE-ANCHORED AI", "Conditioned on Style Anchor Board", BUNDLE_DIR / "03_style_anchored.png"),
        ("04. STRUCTURAL SCAFFOLD", "Deterministic 2:1 dimetric vector blueprint", BUNDLE_DIR / "04_constrained_scaffold.png"),
        ("05. NATIVE 2D COMPOSITE", "Metric anchor composition (Zero eyeballed resize)", BUNDLE_DIR / "06_native_composite.png"),
        ("06. HYBRID SCENE", "2D structured assets + generative painterly backdrop", BUNDLE_DIR / "07_hybrid_scene.png"),
        ("07. BLENDER 3D CLEAN", "Procedural Cycles 3D->2D render (100% locked camera)", BUNDLE_DIR / "08_blender_clean.png"),
        ("08. BLENDER 3D PAINTERLY", "Procedural 3D render with line contour post-pass", BUNDLE_DIR / "09_blender_painterly.png"),
    ]
    
    idx = 0
    start_y = 110
    for r in range(rows):
        for c in range(cols):
            if idx >= len(items):
                break
            title, desc, img_path = items[idx]
            x = margin + c * (card_w + margin)
            y = start_y + r * (card_h + header_h + margin)
            
            # Card background
            draw.rectangle([x, y, x + card_w, y + card_h + header_h], fill=(30, 34, 42), outline=(55, 65, 81), width=2)
            # Label
            draw.text((x + 16, y + 14), title, fill=(255, 255, 255))
            draw.text((x + 16, y + 38), desc, fill=(156, 163, 175))
            
            # Image content
            if img_path.exists():
                im = Image.open(img_path).convert("RGB")
                im_fitted = im.resize((card_w - 16, card_h - 16), Image.Resampling.LANCZOS)
                sheet.paste(im_fitted, (x + 8, y + header_h + 8))
            idx += 1
            
    out_path = BUNDLE_DIR / "contact_sheet.jpg"
    sheet.save(out_path, quality=92)
    print(f"--> Saved master contact sheet to {out_path}")


def create_assets_contact_sheet():
    """
    Creates review_bundle/assets_contact_sheet.png (2x4 grid of modular transparent assets).
    """
    print("--> Building modular assets contact sheet...")
    card_w, card_h = 512, 512
    header_h = 60
    cols, rows = 4, 2
    margin = 20
    
    total_w = cols * card_w + (cols + 1) * margin
    total_h = rows * (card_h + header_h) + (rows + 1) * margin + 90
    
    sheet = Image.new("RGB", (total_w, total_h), color=(24, 24, 27))
    draw = ImageDraw.Draw(sheet)
    
    draw.text((margin, 20), "MODULAR ASSETS CONTACT SHEET — INDIVIDUAL TRANSPARENT SPRITES", fill=(56, 189, 248))
    draw.text((margin, 48), "Extracted with BFS flood-fill alpha, normalized to canonical 96 PPM & Y=900 baseline anchor", fill=(161, 161, 170))
    
    norm_dir = REPO_ROOT / "appennino-2d-asset-factory/output/normalized"
    assets = [
        ("HOUSE A (2-FLOOR)", "Gable roof, olive shutters, balcony, ivy", norm_dir / "house_A.png"),
        ("HOUSE B (3-FLOOR TOWER)", "Narrow tower, brown shutters, chimney", norm_dir / "house_B.png"),
        ("HOUSE C (WIDE SHOP)", "Hip roof, arched shop door, flower boxes", norm_dir / "house_C.png"),
        ("STONE STAIRS", "Steps climbing 2.4m elevation with parapet", norm_dir / "stairs.png"),
        ("RETAINING WALL", "Limestone terrace wall with coping stones", norm_dir / "retaining_wall.png"),
        ("CARVED FOUNTAIN", "Octagonal basin with center column finial", norm_dir / "fountain.png"),
        ("MEDITERRANEAN VEGETATION", "Olive tree, garden shrubs, potted geraniums", norm_dir / "vegetation.png"),
        ("STREET PROPS", "Barrels, stacked fruit crates, wall lantern", norm_dir / "props.png"),
    ]
    
    idx = 0
    start_y = 90
    for r in range(rows):
        for c in range(cols):
            if idx >= len(assets):
                break
            title, desc, img_path = assets[idx]
            x = margin + c * (card_w + margin)
            y = start_y + r * (card_h + header_h + margin)
            
            draw.rectangle([x, y, x + card_w, y + card_h + header_h], fill=(39, 39, 42), outline=(63, 63, 70), width=2)
            draw.text((x + 14, y + 10), title, fill=(255, 255, 255))
            draw.text((x + 14, y + 32), desc, fill=(161, 161, 170))
            
            # Draw subtle checkerboard pattern inside image area to highlight transparency
            img_x0, img_y0 = x + 8, y + header_h + 8
            img_w, img_h = card_w - 16, card_h - 16
            draw.rectangle([img_x0, img_y0, img_x0 + img_w, img_y0 + img_h], fill=(48, 48, 54))
            
            if img_path.exists():
                im = Image.open(img_path).convert("RGBA")
                im_resized = im.resize((img_w, img_h), Image.Resampling.LANCZOS)
                sheet.paste(im_resized, (img_x0, img_y0), im_resized)
            idx += 1
            
    out_path = BUNDLE_DIR / "assets_contact_sheet.png"
    sheet.save(out_path)
    print(f"--> Saved assets contact sheet to {out_path}")


def create_scaffolds_contact_sheet():
    """
    Creates review_bundle/scaffolds_contact_sheet.png (side-by-side scaffold vs final output).
    """
    print("--> Building scaffolds-to-assets contact sheet...")
    pair_w, pair_h = 480, 480
    header_h = 50
    rows = 5
    cols = 2
    margin = 20
    
    total_w = cols * pair_w + (cols + 1) * margin + 60
    total_h = rows * (pair_h + header_h) + (rows + 1) * margin + 90
    
    sheet = Image.new("RGB", (total_w, total_h), color=(20, 20, 22))
    draw = ImageDraw.Draw(sheet)
    
    draw.text((margin, 20), "STRUCTURAL SCAFFOLD -> FINAL GENERATED ASSET COMPARISON", fill=(244, 63, 94))
    draw.text((margin, 48), "Evaluating whether spatial vector conditioning successfully guided the diffusion model", fill=(161, 161, 170))
    
    scaff_dir = REPO_ROOT / "appennino-2d-asset-factory/scaffolds"
    styled_dir = REPO_ROOT / "appennino-2d-asset-factory/output/style_anchored"
    norm_dir = REPO_ROOT / "appennino-2d-asset-factory/output/normalized"
    
    pairs = [
        ("HOUSE A", scaff_dir / "scaffold_house_A.png", styled_dir / "house_A.png"),
        ("HOUSE B (TOWER)", scaff_dir / "scaffold_house_B.png", styled_dir / "house_B.png"),
        ("HOUSE C (SHOP)", scaff_dir / "scaffold_house_C.png", styled_dir / "house_C.png"),
        ("STAIRCASE", scaff_dir / "scaffold_stairs.png", norm_dir / "stairs.png"),
        ("FOUNTAIN", scaff_dir / "scaffold_fountain.png", norm_dir / "fountain.png"),
    ]
    
    start_y = 90
    for r, (label, scaf_p, gen_p) in enumerate(pairs):
        row_y = start_y + r * (pair_h + header_h + margin)
        
        # Row Header
        draw.text((margin + 10, row_y + 12), f"{r+1}. {label}", fill=(255, 255, 255))
        
        # Left: Scaffold
        x_left = margin
        y_box = row_y + header_h
        draw.rectangle([x_left, y_box, x_left + pair_w, y_box + pair_h], fill=(32, 32, 36), outline=(60, 60, 68), width=2)
        draw.text((x_left + 12, row_y + 28), "INPUT SCAFFOLD (Vector Geometry)", fill=(147, 197, 253))
        if scaf_p.exists():
            im_s = Image.open(scaf_p).convert("RGBA").resize((pair_w - 16, pair_h - 16), Image.Resampling.LANCZOS)
            sheet.paste(im_s, (x_left + 8, y_box + 8), im_s)
            
        # Arrow in center
        arrow_x = x_left + pair_w + 12
        draw.text((arrow_x, y_box + pair_h // 2 - 15), "--->", fill=(244, 63, 94))
        
        # Right: Generated Output
        x_right = x_left + pair_w + 50
        draw.rectangle([x_right, y_box, x_right + pair_w, y_box + pair_h], fill=(32, 32, 36), outline=(60, 60, 68), width=2)
        draw.text((x_right + 12, row_y + 28), "OUTPUT SPRITE (Rendered Asset)", fill=(74, 222, 128))
        if gen_p.exists():
            im_g = Image.open(gen_p).convert("RGBA").resize((pair_w - 16, pair_h - 16), Image.Resampling.LANCZOS)
            sheet.paste(im_g, (x_right + 8, y_box + 8), im_g)
            
    out_path = BUNDLE_DIR / "scaffolds_contact_sheet.png"
    sheet.save(out_path)
    print(f"--> Saved scaffolds contact sheet to {out_path}")


if __name__ == "__main__":
    copy_bundle_files()
    create_master_contact_sheet()
    create_assets_contact_sheet()
    create_scaffolds_contact_sheet()
    print("--> Review bundle and contact sheets complete!")
