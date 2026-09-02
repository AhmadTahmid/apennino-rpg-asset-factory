"""
Automated Asset Normalizer and Alpha Edge Cleaner.
Extracts isolated sprites from white backgrounds using BFS flood-fill,
normalizes scales based on semantic anchors (e.g. 2.1m doors),
and positions them on canonical canvas coordinates (X=512, Y=900).
"""

import json
from collections import deque
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "metadata"
METADATA_DIR.mkdir(parents=True, exist_ok=True)

PPM = 96.0
CANVAS_SIZE = (1024, 1024)
TARGET_GROUND_Y = 900
TARGET_CENTER_X = 512
CANONICAL_DOOR_HEIGHT_PX = 202  # 2.1m at 96 PPM


def clean_and_extract_alpha(img_rgb, bg_thresh=238):
    """
    Converts a white-background sprite into an RGBA image with BFS flood-fill from border.
    """
    img = img_rgb.convert("RGB")
    w, h = img.size
    arr = np.array(img)
    
    # Near-white detection
    is_near_white = (arr[:, :, 0] >= bg_thresh) & (arr[:, :, 1] >= bg_thresh) & (arr[:, :, 2] >= bg_thresh)
    
    # BFS flood fill from all perimeter border pixels
    visited = np.zeros((h, w), dtype=bool)
    queue = deque()
    
    for x in range(w):
        if is_near_white[0, x]:
            visited[0, x] = True
            queue.append((0, x))
        if is_near_white[h - 1, x]:
            visited[h - 1, x] = True
            queue.append((h - 1, x))
            
    for y in range(h):
        if is_near_white[y, 0]:
            visited[y, 0] = True
            queue.append((y, 0))
        if is_near_white[y, w - 1]:
            visited[y, w - 1] = True
            queue.append((y, w - 1))
            
    while queue:
        y, x = queue.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if is_near_white[ny, nx]:
                    visited[ny, nx] = True
                    queue.append((ny, nx))
                    
    # Foreground alpha
    alpha = np.where(visited, 0, 255).astype(np.uint8)
    
    # Feather edge pixels bordering background
    diff_from_white = 255 - np.min(arr, axis=2)
    feather = np.clip(diff_from_white * 6.0, 0, 255).astype(np.uint8)
    alpha = np.minimum(alpha, feather)
    
    res_arr = np.dstack((arr, alpha))
    result = Image.fromarray(res_arr, "RGBA")
    return result


def find_visual_bounds(img_rgba, alpha_thresh=30):
    """Finds tight non-transparent bounding box [min_x, min_y, max_x, max_y]."""
    alpha = np.array(img_rgba.split()[3])
    rows = np.any(alpha > alpha_thresh, axis=1)
    cols = np.any(alpha > alpha_thresh, axis=0)
    if not np.any(rows) or not np.any(cols):
        return [0, 0, img_rgba.width, img_rgba.height]
    min_y, max_y = np.where(rows)[0][[0, -1]]
    min_x, max_x = np.where(cols)[0][[0, -1]]
    return [int(min_x), int(min_y), int(max_x), int(max_y)]


def normalize_asset(input_path, output_path, semantic_type="building", door_detected_h=None):
    """
    Normalizes a single asset image to the canonical 1024x1024 canvas.
    """
    raw_img = Image.open(input_path)
    rgba = clean_and_extract_alpha(raw_img)
    bounds = find_visual_bounds(rgba)
    
    cropped = rgba.crop(bounds)
    w_crop, h_crop = cropped.size
    
    scale_factor = 1.0
    if door_detected_h and door_detected_h > 0:
        scale_factor = CANONICAL_DOOR_HEIGHT_PX / float(door_detected_h)
    elif semantic_type == "building":
        if h_crop > 850:
            scale_factor = 780.0 / h_crop
        elif h_crop < 450:
            scale_factor = 540.0 / h_crop
            
    if abs(scale_factor - 1.0) > 0.02:
        new_w = max(1, int(w_crop * scale_factor))
        new_h = max(1, int(h_crop * scale_factor))
        cropped = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        w_crop, h_crop = new_w, new_h
        
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    paste_x = TARGET_CENTER_X - (w_crop // 2)
    paste_y = TARGET_GROUND_Y - h_crop
    canvas.paste(cropped, (paste_x, paste_y), cropped)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    
    meta = {
        "id": output_path.stem,
        "semantic_type": semantic_type,
        "pixels_per_meter": PPM,
        "ground_anchor": [TARGET_CENTER_X, TARGET_GROUND_Y],
        "visual_bounds": [paste_x, paste_y, paste_x + w_crop, paste_y + h_crop],
        "world_dimensions_m": {
            "width": round(w_crop / PPM, 2),
            "height": round(h_crop / PPM, 2)
        },
        "scale_normalization_factor": round(scale_factor, 4),
        "source_file": str(input_path.name),
        "style_profile": "appennino_v1"
    }
    meta_path = METADATA_DIR / f"{output_path.stem}.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"--> Normalized {output_path.stem}: Scale x{scale_factor:.3f}, Canvas bounds {meta['visual_bounds']}")
    return meta


def process_all_raw_and_styled():
    raw_dir = BASE_DIR / "output/raw_baseline"
    norm_dir = BASE_DIR / "output/normalized"
    
    assets = [
        ("house_A.png", "building", 210),
        ("house_B.png", "building", 205),
        ("house_C.png", "building", 215),
        ("stairs.png", "infrastructure", None),
        ("retaining_wall.png", "infrastructure", None),
        ("fountain.png", "monument", None),
        ("vegetation.png", "foliage", None),
        ("props.png", "props", None),
    ]
    
    for filename, sem_type, door_h in assets:
        src = raw_dir / filename
        if src.exists():
            dest = norm_dir / filename
            normalize_asset(src, dest, sem_type, door_h)


if __name__ == "__main__":
    process_all_raw_and_styled()
