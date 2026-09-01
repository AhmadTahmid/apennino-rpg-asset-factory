"""
Canonical configuration constants for the Appennino 3D -> 2D Asset Factory.
Centralizes camera, lighting, scale, materials, and output resolutions
to ensure 100% perspective and visual consistency across all renders.
"""

import math
import os
from pathlib import Path

# Paths
BASE_DIR = Path("d:/Apennino scene").resolve()
OUTPUT_DIR = BASE_DIR / "output"
SCENE_OUTPUT_DIR = OUTPUT_DIR / "scene"
ISOLATED_OUTPUT_DIR = OUTPUT_DIR / "isolated_assets"
VARIATIONS_OUTPUT_DIR = OUTPUT_DIR / "variations"
COMPOSITE_OUTPUT_DIR = OUTPUT_DIR / "2d_composite"
DIAGNOSTICS_OUTPUT_DIR = OUTPUT_DIR / "diagnostics"
SOURCE_DIR = BASE_DIR / "source"

# World Scale Constants (1 unit = 1 meter)
WORLD_SCALE = {
    "unit_to_meter": 1.0,
    "human_height": 1.75,
    "floor_height": 2.8,
    "standard_door_height": 2.1,
    "standard_door_width": 1.0,
    "standard_window_height": 1.3,
    "standard_window_width": 0.9,
    "stair_riser": 0.18,
    "stair_tread": 0.32,
    "retaining_wall_height": 2.2,
}

# Canonical RPG Camera Settings (LOCKED - Never alter between isolated assets)
# Elevated 3/4 Dimetric View matching the Appennino reference video
CANONICAL_CAMERA = {
    "type": "ORTHO",
    "pitch_deg": 56.0,          # Downward pitch angle from horizontal
    "yaw_deg": 45.0,            # Z-rotation angle (45 degrees)
    "roll_deg": 0.0,
    "rotation_euler": (
        math.radians(56.0),
        0.0,
        math.radians(45.0)
    ),
    "full_scene_ortho_scale": 23.0,
    "asset_ortho_scale": 7.5,   # Framing scale for individual buildings
    "prop_ortho_scale": 3.2,    # Framing scale for smaller props
    "scene_resolution": (1920, 1080),
    "asset_resolution": (1024, 1024),
    "pixel_resolution": (480, 270),
}

# Canonical Lighting Rig (LOCKED - Warm Mediterranean afternoon daylight)
CANONICAL_LIGHTING = {
    "sun_color": (1.0, 0.95, 0.86, 1.0),       # Warm golden sunlight
    "sun_energy": 3.8,
    "sun_angle_deg": 12.0,                      # Soft shadow edges (non-harsh)
    "sun_rotation_euler": (
        math.radians(48.0),
        math.radians(22.0),
        math.radians(130.0)
    ),
    "sky_color": (0.68, 0.80, 0.94, 1.0),       # Soft cyan-blue sky fill bounce
    "sky_energy": 0.90,
    "ambient_occlusion_distance": 2.5,
    "ambient_occlusion_factor": 0.35,
}

# Stylized Color Palette (sRGB hex references for materials)
PALETTE = {
    "limestone_base": (0.86, 0.82, 0.74, 1.0),      # Warm cream stone
    "limestone_dark": (0.68, 0.63, 0.54, 1.0),      # Weathered stone crevices
    "limestone_quoin": (0.75, 0.70, 0.60, 1.0),     # Corner blocks
    "terracotta_bright": (0.82, 0.35, 0.16, 1.0),   # Sunlit roof tile
    "terracotta_dark": (0.55, 0.20, 0.08, 1.0),     # Shadowed tile ridge
    "aged_wood": (0.32, 0.22, 0.14, 1.0),           # Dark timber/beams
    "aged_wood_light": (0.45, 0.33, 0.22, 1.0),     # Weathered plank highlight
    "shutter_olive": (0.34, 0.44, 0.30, 1.0),       # Vintage green shutter
    "shutter_chestnut": (0.38, 0.24, 0.15, 1.0),    # Brown wood shutter
    "cobble_stone": (0.62, 0.59, 0.53, 1.0),        # Street paving stone
    "cobble_mortar": (0.42, 0.39, 0.34, 1.0),       # Ground mortar
    "fountain_stone": (0.72, 0.69, 0.63, 1.0),      # Carved fountain stone
    "water_turquoise": (0.28, 0.62, 0.65, 0.85),    # Clear mountain fountain water
    "foliage_green": (0.22, 0.48, 0.16, 1.0),       # Ivy / shrub canopy
    "foliage_light": (0.40, 0.65, 0.24, 1.0),       # Leaf highlight
    "flower_geranium_red": (0.88, 0.18, 0.16, 1.0), # Vivid red blooms
    "flower_pink": (0.92, 0.42, 0.56, 1.0),         # Soft pink blooms
    "flower_white": (0.95, 0.94, 0.88, 1.0),        # White/cream blooms
    "wrought_iron": (0.18, 0.18, 0.18, 1.0),        # Balconies, lanterns
    "terracotta_pot": (0.78, 0.40, 0.22, 1.0),      # Flower pots
    "plaster_cream": (0.88, 0.85, 0.78, 1.0),       # Stucco finish
}
