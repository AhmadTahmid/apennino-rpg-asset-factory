"""
Canonical Camera Manager & Validator for Appennino Asset Factory.
Ensures zero perspective drift across all rendered assets.
"""

import bpy
import math
import json
from mathutils import Vector, Euler
from .config import CANONICAL_CAMERA, DIAGNOSTICS_OUTPUT_DIR


def create_canonical_camera(name="Canonical_RPG_Camera", ortho_scale=None, target_point=Vector((0.0, 0.0, 0.0))):
    """
    Creates or configures the canonical locked RPG orthographic camera.
    """
    if ortho_scale is None:
        ortho_scale = CANONICAL_CAMERA["full_scene_ortho_scale"]

    # Retrieve or create camera data
    if name in bpy.data.cameras:
        cam_data = bpy.data.cameras[name]
    else:
        cam_data = bpy.data.cameras.new(name=name)

    cam_data.type = CANONICAL_CAMERA["type"]
    cam_data.ortho_scale = ortho_scale
    cam_data.clip_start = 0.1
    cam_data.clip_end = 500.0

    # Retrieve or create object
    if name in bpy.data.objects:
        cam_obj = bpy.data.objects[name]
    else:
        cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)

    # Set canonical rotation (Pitch 56 deg, Yaw 45 deg, Roll 0 deg)
    cam_obj.rotation_mode = 'XYZ'
    cam_obj.rotation_euler = Euler(CANONICAL_CAMERA["rotation_euler"], 'XYZ')

    # Update view layer to compute world matrix
    bpy.context.view_layer.update()
    look_dir = (cam_obj.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()

    dist = 45.0
    cam_obj.location = Vector(target_point) - dist * look_dir

    bpy.context.scene.camera = cam_obj
    return cam_obj


def frame_asset_camera(cam_obj, target_center=Vector((0.0, 0.0, 0.0)), ortho_scale=6.0):
    """
    Adjusts camera position and ortho scale to frame an isolated asset
    while maintaining 100% strict angle/rotation lock.
    """
    cam_obj.data.ortho_scale = ortho_scale
    
    # Re-enforce locked rotation
    cam_obj.rotation_mode = 'XYZ'
    cam_obj.rotation_euler = Euler(CANONICAL_CAMERA["rotation_euler"], 'XYZ')

    bpy.context.view_layer.update()
    look_dir = (cam_obj.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()

    dist = 45.0
    cam_obj.location = Vector(target_center) - dist * look_dir


def validate_camera_consistency(cam_obj):
    """
    Validates that the active camera strictly complies with canonical settings.
    Raises ValueError if rotation or projection type has drifted.
    """
    if cam_obj.data.type != 'ORTHO':
        raise ValueError(f"Camera type is {cam_obj.data.type}, must be ORTHO.")

    cur_rot = cam_obj.rotation_euler
    target_rot = CANONICAL_CAMERA["rotation_euler"]
    eps = 1e-4

    for i, axis in enumerate(['X', 'Y', 'Z']):
        if abs(cur_rot[i] - target_rot[i]) > eps:
            raise ValueError(
                f"Camera rotation on axis {axis} has drifted: {math.degrees(cur_rot[i]):.2f} deg "
                f"vs canonical {math.degrees(target_rot[i]):.2f} deg."
            )
    return True


def export_camera_metadata(filepath=None):
    """Exports camera settings to JSON for automated verification."""
    if filepath is None:
        DIAGNOSTICS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        filepath = DIAGNOSTICS_OUTPUT_DIR / "camera_settings.json"

    data = {
        "camera_type": CANONICAL_CAMERA["type"],
        "pitch_degrees": CANONICAL_CAMERA["pitch_deg"],
        "yaw_degrees": CANONICAL_CAMERA["yaw_deg"],
        "rotation_euler_radians": CANONICAL_CAMERA["rotation_euler"],
        "full_scene_ortho_scale": CANONICAL_CAMERA["full_scene_ortho_scale"],
        "asset_ortho_scale": CANONICAL_CAMERA["asset_ortho_scale"],
        "scene_resolution": CANONICAL_CAMERA["scene_resolution"],
        "asset_resolution": CANONICAL_CAMERA["asset_resolution"],
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filepath
