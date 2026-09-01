"""
Master Scene Assembly Script for Appennino Town RPG Screen.
Builds the multi-tiered hill-town scene matching the reference composition.
"""

import bpy
import bmesh
import math
import sys
from pathlib import Path
from mathutils import Vector, Euler

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.parent))

from scripts.config import (
    CANONICAL_CAMERA, CANONICAL_LIGHTING, SOURCE_DIR, SCENE_OUTPUT_DIR, DIAGNOSTICS_OUTPUT_DIR
)
from scripts.materials import initialize_all_materials
from scripts.camera import create_canonical_camera, validate_camera_consistency, export_camera_metadata
from scripts.lighting import setup_canonical_lighting
from scripts.architecture import (
    create_stone_house, create_staircase, create_retaining_wall
)
from scripts.props import (
    create_fountain, create_barrel, create_crate, create_flower_pot,
    create_wall_lantern, create_human_scale_ref
)
from scripts.vegetation import create_shrub, create_stylized_tree, create_ivy_patch


def reset_scene():
    """Wipes all objects, meshes, and materials for clean regeneration."""
    bpy.ops.wm.read_homefile(use_empty=True)
    if not bpy.data.collections:
        col = bpy.data.collections.new("SceneCollection")
        bpy.context.scene.collection.children.link(col)


def create_ground_terraces(mats):
    """
    Creates multi-level cobblestone and plaza terraces.
    """
    # 1. Lower Plaza Ground Plane (Z = 0.0)
    mesh_low = bpy.data.meshes.new("Ground_Lower_Plaza")
    bm_l = bmesh.new()
    bmesh.ops.create_cube(bm_l, size=1.0)
    for v in bm_l.verts:
        v.co.x = (v.co.x) * 32.0 + 2.0
        v.co.y = (v.co.y) * 32.0 - 2.0
        v.co.z = (v.co.z - 0.5) * 0.4
    bm_l.to_mesh(mesh_low)
    bm_l.free()

    obj_low = bpy.data.objects.new("Ground_Lower_Plaza", mesh_low)
    obj_low.data.materials.append(mats["cobblestone"])
    bpy.context.scene.collection.objects.link(obj_low)

    # 2. Upper Terrace Ground Plane (Z = 2.4)
    mesh_high = bpy.data.meshes.new("Ground_Upper_Terrace")
    bm_h = bmesh.new()
    bmesh.ops.create_cube(bm_h, size=1.0)
    for v in bm_h.verts:
        v.co.x = (v.co.x) * 22.0 - 5.0
        v.co.y = (v.co.y) * 18.0 + 7.5
        v.co.z = 2.4 + (v.co.z - 0.5) * 0.4
    bm_h.to_mesh(mesh_high)
    bm_h.free()

    obj_high = bpy.data.objects.new("Ground_Upper_Terrace", mesh_high)
    obj_high.data.materials.append(mats["cobblestone"])
    bpy.context.scene.collection.objects.link(obj_high)

    return obj_low, obj_high


def create_mountain_backdrop(mats):
    """
    Creates stylized distant mountain ridges in the upper-right background.
    """
    mesh_mt = bpy.data.meshes.new("Distant_Mountains")
    bm_m = bmesh.new()

    # Mountain Ridge 1 (Far background)
    verts1 = [
        bm_m.verts.new((0.0, 22.0, -2.0)),
        bm_m.verts.new((14.0, 18.0, -2.0)),
        bm_m.verts.new((26.0, 14.0, -2.0)),
        bm_m.verts.new((7.0, 20.0, 12.0)),
        bm_m.verts.new((19.0, 16.0, 14.5)),
    ]
    bm_m.faces.new([verts1[0], verts1[1], verts1[3]])
    bm_m.faces.new([verts1[1], verts1[4], verts1[3]])
    bm_m.faces.new([verts1[1], verts1[2], verts1[4]])

    # Mountain Ridge 2 (Mid background)
    verts2 = [
        bm_m.verts.new((-6.0, 18.0, -2.0)),
        bm_m.verts.new((8.0, 15.0, -2.0)),
        bm_m.verts.new((18.0, 12.0, -2.0)),
        bm_m.verts.new((2.0, 16.5, 9.0)),
        bm_m.verts.new((12.0, 13.5, 10.5)),
    ]
    bm_m.faces.new([verts2[0], verts2[1], verts2[3]])
    bm_m.faces.new([verts2[1], verts2[4], verts2[3]])
    bm_m.faces.new([verts2[1], verts2[2], verts2[4]])

    bm_m.to_mesh(mesh_mt)
    bm_m.free()

    obj_mt = bpy.data.objects.new("Distant_Mountains", mesh_mt)
    obj_mt.data.materials.append(mats["mountain"])
    bpy.context.scene.collection.objects.link(obj_mt)
    return obj_mt


def build_appennino_scene():
    """
    Constructs the entire Appennino scene matching the reference composition.
    """
    print("--> Resetting scene...")
    reset_scene()

    print("--> Initializing materials...")
    mats = initialize_all_materials()

    print("--> Setting up canonical lighting and camera...")
    setup_canonical_lighting()
    
    # Target point at center of the plaza / midground
    cam = create_canonical_camera(
        target_point=Vector((-0.5, 0.8, 2.0)),
        ortho_scale=CANONICAL_CAMERA["full_scene_ortho_scale"]
    )
    validate_camera_consistency(cam)
    export_camera_metadata()

    print("--> Building terrain terraces & retaining structures...")
    create_ground_terraces(mats)
    create_mountain_backdrop(mats)

    # Retaining Wall dividing Lower Plaza (Z=0) and Upper Terrace (Z=2.4)
    create_retaining_wall(
        name="Main_Retaining_Wall",
        location=(-4.2, 1.4, 0.0),
        rotation_z=math.radians(-12.0),
        length=10.0,
        height=2.4,
        thickness=0.65
    )

    # Stone Staircase climbing from plaza to upper terrace
    create_staircase(
        name="Plaza_Staircase",
        location=(-1.2, 0.8, 0.0),
        rotation_z=math.radians(78.0),
        width=1.7,
        steps=13,
        tread=0.32,
        riser=0.185,
        side_wall=True
    )

    print("--> Generating architectural buildings...")
    # 1. Primary Upper House (Left / Top-Center, Z=2.4)
    create_stone_house(
        name="Primary_House_Upper",
        location=(-5.4, 5.0, 2.4),
        rotation_z=math.radians(12.0),
        width=5.8,
        depth=4.6,
        floors=2,
        floor_height=2.8,
        roof_type="gable",
        roof_pitch=1.6,
        shutter_color="green",
        balcony_floor=2,
        flowerboxes=True,
        chimney=True,
        ivy=True
    )

    # 2. Secondary Upper Annex / Tower behind primary house (Z=2.4)
    create_stone_house(
        name="Upper_Annex_Building",
        location=(-1.0, 8.8, 2.4),
        rotation_z=math.radians(-6.0),
        width=4.0,
        depth=4.0,
        floors=3,
        floor_height=2.6,
        roof_type="hip",
        roof_pitch=1.4,
        shutter_color="brown",
        balcony_floor=0,
        flowerboxes=True,
        chimney=False,
        ivy=True
    )

    # 3. Secondary Lower Building (Right Midground, Z=0.0)
    create_stone_house(
        name="Secondary_House_Lower",
        location=(4.8, -0.6, 0.0),
        rotation_z=math.radians(-18.0),
        width=5.0,
        depth=4.4,
        floors=2,
        floor_height=2.7,
        roof_type="gable",
        roof_pitch=1.5,
        shutter_color="green",
        balcony_floor=0,
        flowerboxes=True,
        chimney=True,
        ivy=True
    )

    # 4. Right Background Townhouse (Z=0.0)
    create_stone_house(
        name="Right_Background_House",
        location=(7.8, 4.8, 0.0),
        rotation_z=math.radians(-15.0),
        width=4.2,
        depth=4.0,
        floors=2,
        floor_height=2.6,
        roof_type="hip",
        roof_pitch=1.4,
        shutter_color="brown",
        balcony_floor=0,
        flowerboxes=False,
        chimney=True,
        ivy=True
    )

    # 5. Foreground Framing Roof (Bottom-Left Corner, Z=-1.2)
    create_stone_house(
        name="Foreground_Roof_Slice",
        location=(-5.8, -5.6, -1.2),
        rotation_z=math.radians(16.0),
        width=5.5,
        depth=4.8,
        floors=1,
        floor_height=2.8,
        roof_type="gable",
        roof_pitch=1.6,
        shutter_color="brown",
        balcony_floor=0,
        flowerboxes=False,
        chimney=False,
        ivy=False
    )

    print("--> Placing environmental props & street furniture...")
    # Central Fountain in Lower Plaza (Prominently placed in foreground plaza)
    create_fountain(
        name="Piazza_Fountain",
        location=(0.6, -3.2, 0.0),
        radius=1.35,
        height=1.65
    )

    # Wall Lanterns
    create_wall_lantern("Lantern_Upper_House", location=(-3.2, 2.6, 4.0), rot_z=math.radians(12.0))
    create_wall_lantern("Lantern_Lower_House", location=(2.4, -2.6, 1.8), rot_z=math.radians(-18.0))

    # Barrel & Crate Clusters
    create_barrel("Barrel_1", location=(2.8, 1.0, 0.0), radius=0.38, height=0.88)
    create_barrel("Barrel_2", location=(3.3, 1.4, 0.0), radius=0.34, height=0.82)
    create_crate("Crate_1", location=(2.5, 1.4, 0.0), size=0.62)

    # Flower Pots along walls & plaza corners
    create_flower_pot("Pot_Plaza_1", location=(-1.4, -0.6, 0.0), radius=0.22, height=0.34, flower_color="red")
    create_flower_pot("Pot_Plaza_2", location=(-0.9, -0.3, 0.0), radius=0.20, height=0.30, flower_color="pink")
    create_flower_pot("Pot_Fountain_Side", location=(2.4, -3.4, 0.0), radius=0.24, height=0.36, flower_color="red")
    create_flower_pot("Pot_Stair_Top", location=(-1.8, 3.8, 2.4), radius=0.22, height=0.32, flower_color="pink")

    print("--> Placing vegetation...")
    # Stylized hill-town tree on upper terrace
    create_stylized_tree("Upper_Terrace_Tree", location=(-7.5, 1.8, 2.4), trunk_height=2.4, crown_radius=1.6)
    # Shrub clusters
    create_shrub("Shrub_Corner_1", location=(5.8, 2.5, 0.0), radius=0.65, height=0.85)
    create_shrub("Shrub_Upper_Terrace", location=(-3.2, 9.8, 2.4), radius=0.70, height=0.90)

    # Save .blend file
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    blend_path = SOURCE_DIR / "scene.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(f"--> Saved scene to {blend_path}")

    return cam


def render_scene_variants():
    """
    Renders the scene in full resolution and reduced resolution.
    """
    SCENE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.preview_samples = 32
    scene.cycles.use_denoising = True
    scene.render.film_transparent = False

    # 1. Variant A — Clean Stylized (1920x1080)
    print("--> Rendering Variant A (Clean Stylized)...")
    scene.render.resolution_x = CANONICAL_CAMERA["scene_resolution"][0]
    scene.render.resolution_y = CANONICAL_CAMERA["scene_resolution"][1]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'

    clean_path = SCENE_OUTPUT_DIR / "clean.png"
    scene.render.filepath = str(clean_path)
    bpy.ops.render.render(write_still=True)
    print(f"--> Clean render saved to {clean_path}")

    # 2. Variant B — Pixel-ish / Reduced Resolution (480x270 upscaled)
    print("--> Rendering Variant B (Pixel-ish)...")
    pixel_temp_path = SCENE_OUTPUT_DIR / "pixel_lowres.png"
    scene.render.resolution_x = CANONICAL_CAMERA["pixel_resolution"][0]
    scene.render.resolution_y = CANONICAL_CAMERA["pixel_resolution"][1]
    scene.render.filepath = str(pixel_temp_path)
    bpy.ops.render.render(write_still=True)
    print(f"--> Low-res render saved to {pixel_temp_path}")


if __name__ == "__main__":
    build_appennino_scene()
    render_scene_variants()
    print("--> Scene generation and rendering complete.")
