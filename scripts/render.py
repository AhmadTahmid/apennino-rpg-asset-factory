"""
Modular Asset & Variation Renderer for Appennino Asset Factory.
Renders transparent isolated sprites, procedural variations, and diagnostic metadata
under 100% locked canonical camera and lighting rigs.
"""

import bpy
import bmesh
import math
import json
import sys
from pathlib import Path
from mathutils import Vector, Euler

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.parent))

from scripts.config import (
    CANONICAL_CAMERA, CANONICAL_LIGHTING, WORLD_SCALE,
    ISOLATED_OUTPUT_DIR, VARIATIONS_OUTPUT_DIR, DIAGNOSTICS_OUTPUT_DIR
)
from scripts.materials import initialize_all_materials
from scripts.camera import (
    create_canonical_camera, frame_asset_camera, validate_camera_consistency, export_camera_metadata
)
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


def setup_render_settings():
    """Sets up transparent background and Cycles settings for crisp sprite renders."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    scene.cycles.preview_samples = 32
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True  # Alpha channel for 2D sprites
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.resolution_x = CANONICAL_CAMERA["asset_resolution"][0]
    scene.render.resolution_y = CANONICAL_CAMERA["asset_resolution"][1]
    scene.render.resolution_percentage = 100


def render_single_asset(output_filename, build_fn, ortho_scale=6.5, target_center=(0, 0, 1.5)):
    """
    Builds and renders an isolated asset on transparent background.
    """
    reset_scene()
    mats = initialize_all_materials()
    setup_canonical_lighting()
    cam = create_canonical_camera(target_point=Vector(target_center), ortho_scale=ortho_scale)
    validate_camera_consistency(cam)
    setup_render_settings()

    # Build the asset
    asset_obj = build_fn(mats)

    out_path = ISOLATED_OUTPUT_DIR / output_filename
    bpy.context.scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f"--> Rendered isolated asset: {out_path}")

    # Gather mesh statistics
    poly_count = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH')
    vert_count = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')

    return {
        "filename": output_filename,
        "ortho_scale": ortho_scale,
        "polygons": poly_count,
        "vertices": vert_count,
        "camera_rotation": list(CANONICAL_CAMERA["rotation_euler"]),
        "lighting_energy": CANONICAL_LIGHTING["sun_energy"]
    }


def render_all_isolated_assets():
    """
    Renders all required isolated modular assets for 2D RPG sprite usage.
    """
    ISOLATED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata_records = []

    # 1. House A: 2 floors, gable roof, arched windows, green shutters, balcony, chimney, ivy
    def build_house_a(mats):
        return create_stone_house(
            name="House_A", location=(0, 0, 0), rotation_z=0.0,
            width=5.8, depth=4.6, floors=2, floor_height=2.8,
            roof_type="gable", roof_pitch=1.6, shutter_color="green",
            balcony_floor=2, flowerboxes=True, chimney=True, ivy=True
        )
    metadata_records.append(render_single_asset("house_A.png", build_house_a, ortho_scale=8.5, target_center=(0, 0, 3.2)))

    # 2. House B: 3 floors, narrow footprint, arched doorway, brown shutters, balcony, chimney
    def build_house_b(mats):
        return create_stone_house(
            name="House_B", location=(0, 0, 0), rotation_z=0.0,
            width=4.4, depth=4.0, floors=3, floor_height=2.6,
            roof_type="gable", roof_pitch=1.5, shutter_color="brown",
            balcony_floor=3, flowerboxes=True, chimney=True, ivy=False
        )
    metadata_records.append(render_single_asset("house_B.png", build_house_b, ortho_scale=9.5, target_center=(0, 0, 4.4)))

    # 3. House C: 2 floors, wider footprint, arched shop door, hip roof, green shutters, flower boxes
    def build_house_c(mats):
        return create_stone_house(
            name="House_C", location=(0, 0, 0), rotation_z=0.0,
            width=6.6, depth=4.4, floors=2, floor_height=2.7,
            roof_type="hip", roof_pitch=1.4, shutter_color="green",
            balcony_floor=0, flowerboxes=True, chimney=False, ivy=True
        )
    metadata_records.append(render_single_asset("house_C.png", build_house_c, ortho_scale=8.5, target_center=(0, 0, 3.0)))

    # 4. Staircase
    def build_stairs(mats):
        return create_staircase(
            name="Staircase_Modular", location=(0, 0, 0), rotation_z=math.radians(90.0),
            width=1.8, steps=10, tread=0.34, riser=0.18, side_wall=True
        )
    metadata_records.append(render_single_asset("stairs.png", build_stairs, ortho_scale=5.0, target_center=(0, 1.6, 0.9)))

    # 5. Retaining Wall
    def build_wall(mats):
        return create_retaining_wall(
            name="Retaining_Wall_Modular", location=(0, 0, 0), rotation_z=0.0,
            length=7.5, height=2.2, thickness=0.6, coping_stones=True
        )
    metadata_records.append(render_single_asset("retaining_wall.png", build_wall, ortho_scale=6.5, target_center=(0, 0, 1.1)))

    # 6. Stone Fountain
    def build_fountain(mats):
        return create_fountain(
            name="Fountain_Modular", location=(0, 0, 0), radius=1.35, height=1.65
        )
    metadata_records.append(render_single_asset("fountain.png", build_fountain, ortho_scale=4.2, target_center=(0, 0, 0.85)))

    # 7. Vegetation (Tree + Shrubs + Flower Pots)
    def build_vegetation(mats):
        t = create_stylized_tree("Tree", location=(0, 0, 0), trunk_height=2.2, crown_radius=1.5)
        s1 = create_shrub("Shrub1", location=(1.8, -0.6, 0), radius=0.6, height=0.8)
        s2 = create_shrub("Shrub2", location=(-1.6, 0.5, 0), radius=0.5, height=0.7)
        return t
    metadata_records.append(render_single_asset("vegetation.png", build_vegetation, ortho_scale=6.5, target_center=(0, 0, 2.0)))

    # 8. Environmental Props (Barrels, Crates, Lantern, Pots)
    def build_props(mats):
        b1 = create_barrel("Barrel1", location=(-0.7, 0, 0), radius=0.38, height=0.88)
        b2 = create_barrel("Barrel2", location=(-0.2, 0.5, 0), radius=0.34, height=0.82)
        c1 = create_crate("Crate1", location=(0.6, -0.2, 0), size=0.65)
        l1 = create_wall_lantern("Lantern", location=(0.6, 0.7, 0.9), rot_z=0.0)
        p1 = create_flower_pot("Pot1", location=(-0.8, -0.7, 0), radius=0.22, height=0.32, flower_color="red")
        p2 = create_flower_pot("Pot2", location=(1.2, 0.4, 0), radius=0.20, height=0.30, flower_color="pink")
        return b1
    metadata_records.append(render_single_asset("props.png", build_props, ortho_scale=4.2, target_center=(0, 0, 0.6)))

    # Save asset metadata JSON
    DIAGNOSTICS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = DIAGNOSTICS_OUTPUT_DIR / "asset_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_records, f, indent=2)
    print(f"--> Exported asset metadata: {meta_path}")


def render_procedural_variations():
    """
    Renders House A, House B, and House C side-by-side in one composite scene
    to demonstrate procedural variation and visual coherence.
    """
    VARIATIONS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()
    mats = initialize_all_materials()
    setup_canonical_lighting()
    cam = create_canonical_camera(target_point=Vector((0.0, 0.0, 3.2)), ortho_scale=18.0)
    validate_camera_consistency(cam)
    setup_render_settings()
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # House A (Left)
    create_stone_house(
        name="Var_House_A", location=(-6.5, 2.0, 0.0), rotation_z=0.0,
        width=5.6, depth=4.6, floors=2, floor_height=2.8,
        roof_type="gable", roof_pitch=1.6, shutter_color="green",
        balcony_floor=2, flowerboxes=True, chimney=True, ivy=True
    )

    # House B (Center)
    create_stone_house(
        name="Var_House_B", location=(0.0, 0.0, 0.0), rotation_z=0.0,
        width=4.4, depth=4.2, floors=3, floor_height=2.6,
        roof_type="gable", roof_pitch=1.5, shutter_color="brown",
        balcony_floor=3, flowerboxes=True, chimney=True, ivy=False
    )

    # House C (Right)
    create_stone_house(
        name="Var_House_C", location=(6.5, -2.0, 0.0), rotation_z=0.0,
        width=6.4, depth=4.4, floors=2, floor_height=2.7,
        roof_type="hip", roof_pitch=1.4, shutter_color="green",
        balcony_floor=0, flowerboxes=True, chimney=False, ivy=True
    )

    # Ground Cobble Strip
    mesh_g = bpy.data.meshes.new("Ground_Strip")
    bm_g = bmesh.new()
    bmesh.ops.create_cube(bm_g, size=1.0)
    for v in bm_g.verts:
        v.co.x *= 24.0
        v.co.y *= 12.0
        v.co.z = (v.co.z - 0.5) * 0.3
    bm_g.to_mesh(mesh_g)
    bm_g.free()
    obj_g = bpy.data.objects.new("Ground_Strip", mesh_g)
    obj_g.data.materials.append(mats["cobblestone"])
    bpy.context.scene.collection.objects.link(obj_g)

    out_path = VARIATIONS_OUTPUT_DIR / "houses_together.png"
    bpy.context.scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f"--> Rendered procedural variations showcase: {out_path}")


def render_scale_reference():
    """
    Renders the 1.75m humanoid reference mannequin next to architectural elements.
    """
    DIAGNOSTICS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()
    mats = initialize_all_materials()
    setup_canonical_lighting()
    cam = create_canonical_camera(target_point=Vector((0.0, 0.0, 1.4)), ortho_scale=6.5)
    validate_camera_consistency(cam)
    setup_render_settings()
    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024

    # Doorway & Wall
    create_stone_house(
        name="Ref_House", location=(0, 2.0, 0), rotation_z=0.0,
        width=4.5, depth=3.5, floors=1, floor_height=2.8,
        roof_type="gable", roof_pitch=1.2, shutter_color="green",
        balcony_floor=0, flowerboxes=True, chimney=False, ivy=False
    )
    # Stairs
    create_staircase(
        name="Ref_Stairs", location=(2.4, -0.5, 0), rotation_z=math.radians(90.0),
        width=1.4, steps=6, tread=0.32, riser=0.18, side_wall=True
    )
    # Human Scale Mannequin (1.75m tall)
    create_human_scale_ref("Human_1_75m", location=(-0.5, 0.1, 0.0))

    out_path = DIAGNOSTICS_OUTPUT_DIR / "scale_reference.png"
    bpy.context.scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f"--> Rendered scale reference: {out_path}")


if __name__ == "__main__":
    print("=== STARTING ASSET BATCH RENDERING ===")
    render_all_isolated_assets()
    render_procedural_variations()
    render_scale_reference()
    print("=== ASSET BATCH RENDERING COMPLETE ===")
