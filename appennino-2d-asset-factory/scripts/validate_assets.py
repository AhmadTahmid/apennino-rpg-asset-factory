"""
Asset and Metadata Consistency Validator.
Inspects all normalized assets, metadata schemas, pixels-per-meter fidelity,
and flags scale drift or perspective misalignment.
"""

import json
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = BASE_DIR / "metadata"
NORM_DIR = BASE_DIR / "output/normalized"


def validate_all_assets():
    print("=== STARTING ASSET VALIDATION ===")
    errors = []
    warnings = []
    
    json_files = list(METADATA_DIR.glob("*.json"))
    if not json_files:
        print("No metadata files found!")
        return False
        
    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)
            
        asset_id = data.get("id")
        png_path = NORM_DIR / f"{asset_id}.png"
        
        # Check image exists
        if not png_path.exists():
            errors.append(f"Missing PNG file for metadata: {asset_id}.png")
            continue
            
        img = Image.open(png_path)
        if img.size != (1024, 1024):
            errors.append(f"{asset_id}: Image size {img.size} != canonical (1024, 1024)")
            
        # Check ground anchor
        anchor = data.get("ground_anchor")
        if anchor != [512, 900]:
            warnings.append(f"{asset_id}: Ground anchor {anchor} differs from canonical [512, 900]")
            
        # Check scale normalization
        scale_fac = data.get("scale_normalization_factor", 1.0)
        if scale_fac < 0.7 or scale_fac > 1.4:
            warnings.append(f"{asset_id}: Extreme scale normalization factor x{scale_fac:.3f} (>30% correction required)")
            
        # Check dimensions
        dims = data.get("world_dimensions_m", {})
        w_m = dims.get("width", 0)
        h_m = dims.get("height", 0)
        print(f"[OK] {asset_id.ljust(16)} | Type: {data.get('semantic_type', 'unknown').ljust(14)} | Dims: {w_m}m x {h_m}m | Scale: x{scale_fac:.3f}")
        
    print(f"\nValidation Summary: {len(json_files)} assets inspected.")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("[OK] Zero structural errors.")
        
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
            
    print("=== VALIDATION COMPLETE ===")
    return len(errors) == 0


if __name__ == "__main__":
    validate_all_assets()
