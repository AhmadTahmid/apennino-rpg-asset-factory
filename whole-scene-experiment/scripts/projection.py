"""
Deterministic 2.5D World-to-Screen Projection System.
Centralizes the mathematical transform between continuous world coordinates (meters)
and 1920x1080 canvas pixel space.
"""

# Canonical Canvas Resolution
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080

# World Dimensions (meters)
WORLD_WIDTH_M = 36.0   # West (0.0m) to East (36.0m)
WORLD_DEPTH_M = 24.0   # North/Back (0.0m) to South/Front (24.0m)

# Projection Calibration
ORIGIN_SCREEN_X = 960.0
ORIGIN_SCREEN_Y = 660.0

PPM_X = 48.0          # Horizontal scale: 48 pixels per meter (36m * 48 = 1728px, centered)
PPM_Y = 24.0          # Depth foreshortening: 24 pixels per meter
PPM_Z = 36.0          # Vertical elevation lift: 36 pixels per meter height

# Dimetric Ground Axis Angle: 2:1 ratio slope
DIMETRIC_SLOPE = 0.5   # dy/dx for receding 2:1 ground lines


def world_to_screen(x_m: float, y_m: float, z_m: float = 0.0) -> tuple[float, float]:
    """
    Transforms continuous 3D world coordinates (x, y, z in meters)
    into 2D screen coordinates (sx, sy in pixels).
    """
    dx = x_m - 18.0
    dy = y_m - 12.0
    
    # Primary elevated projection with dimetric tilt
    sx = ORIGIN_SCREEN_X + dx * PPM_X
    sy = ORIGIN_SCREEN_Y + dy * PPM_Y - z_m * PPM_Z
    return (sx, sy)


def screen_to_world_ground(sx: float, sy: float, z_m: float = 0.0) -> tuple[float, float]:
    """
    Inverse projection from screen coordinates onto a specific elevation ground plane (Z).
    """
    dx = (sx - ORIGIN_SCREEN_X) / PPM_X
    dy = (sy + z_m * PPM_Z - ORIGIN_SCREEN_Y) / PPM_Y
    x_m = dx + 18.0
    y_m = dy + 12.0
    return (x_m, y_m)
