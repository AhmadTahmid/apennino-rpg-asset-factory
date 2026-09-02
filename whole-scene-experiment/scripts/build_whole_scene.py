"""
Whole-Scene 3D Procedural Builder for Experiment B.
Reconstructs the exact scene_001.json layout in Blender 5.2 (bpy) with high-fidelity materials,
canonical lighting, and locked dimetric projection.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler
import json
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
EXP_DIR = SCRIPT_DIR.parent
SCENE_JSON = EXP_DIR / "scene/scene_001.json"
GEN_DIR = EXP_DIR / "generation"
GEN_DIR.mkdir(parents=True, exist_ok=True)


def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)


def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def setup_materials():
    mats = {}
    # Warm aged limestone
    mats["stone"] = create_material("Stone", (0.85, 0.82, 0.77, 1.0), roughness=0.85)
    # Terracotta roof tiles
    mats["roof"] = create_material("Terracotta", (0.78, 0.35, 0.16, 1.0), roughness=0.75)
    # Olive green shutters
    mats["shutters"] = create_material("Shutters", (0.31, 0.42, 0.29, 1.0), roughness=0.6)
    # Walnut wood doors & beams
    mats["wood"] = create_material("Wood", (0.35, 0.22, 0.15, 1.0), roughness=0.7)
    # Cobblestone pavement
    mats["piazza"] = create_material("PiazzaGround", (0.82, 0.79, 0.74, 1.0), roughness=0.9)
    # Upper terrace stone
    mats["terrace"] = create_material("TerraceGround", (0.80, 0.77, 0.72, 1.0), roughness=0.9)
    # Foliage green
    mats["foliage"] = create_material("Foliage", (0.35, 0.48, 0.30, 1.0), roughness=0.6)
    # Water
    mats["water"] = create_material("Water", (0.25, 0.65, 0.70, 1.0), roughness=0.1)
    # Distant mountain haze
    mats["mountains"] = create_material("Mountains", (0.65, 0.72, 0.82, 1.0), roughness=0.95)
    return mats


def create_box(name, x_min, x_max, y_min, y_max, z_min, z_max, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # In Blender: X is East-West, Y is North-South, Z is vertical
    # In scene_001.json: X is [0, 36], Y is [0, 24] (North=0, South=24).
    # Center the scene around (18, 12)
    x0 = x_min - 18.0
    x1 = x_max - 18.0
    y0 = -(y_max - 12.0)  # Invert Y so North is +Y in 3D
    y1 = -(y_min - 12.0)
    z0 = z_min
    z1 = z_max
    
    bm = bmesh.new()
    verts = [
        bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
    ]
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]])
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]])
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]])
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]])
    bm.faces.new([verts[2], verts[6], verts[7], verts[3]])
    bm.faces.new([verts[3], verts[7], verts[4], verts[0]])
    
    bm.to_mesh(mesh)
    bm.free()
    
    if mat:
        obj.data.materials.append(mat)
    return obj


def create_gable_roof(name, x_min, x_max, y_min, y_max, z_base, roof_h, ridge_axis, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    x0 = x_min - 18.0 - 0.2
    x1 = x_max - 18.0 + 0.2
    y0 = -(y_max - 12.0) - 0.2
    y1 = -(y_min - 12.0) + 0.2
    zb = z_base
    zr = z_base + roof_h
    
    bm = bmesh.new()
    if ridge_axis == "E-W":
        ymid = (y0 + y1) / 2.0
        v_bl = bm.verts.new((x0, y0, zb))
        v_br = bm.verts.new((x1, y0, zb))
        v_tr = bm.verts.new((x1, y1, zb))
        v_tl = bm.verts.new((x0, y1, zb))
        v_rmid_l = bm.verts.new((x0, ymid, zr))
        v_rmid_r = bm.verts.new((x1, ymid, zr))
        bm.faces.new([v_bl, v_br, v_rmid_r, v_rmid_l]) # South slope
        bm.faces.new([v_rmid_l, v_rmid_r, v_tr, v_tl]) # North slope
        bm.faces.new([v_bl, v_rmid_l, v_tl])           # West gable
        bm.faces.new([v_br, v_tr, v_rmid_r])           # East gable
    else: # N-S
        xmid = (x0 + x1) / 2.0
        v_bl = bm.verts.new((x0, y0, zb))
        v_br = bm.verts.new((x1, y0, zb))
        v_tr = bm.verts.new((x1, y1, zb))
        v_tl = bm.verts.new((x0, y1, zb))
        v_rmid_s = bm.verts.new((xmid, y0, zr))
        v_rmid_n = bm.verts.new((xmid, y1, zr))
        bm.faces.new([v_bl, v_rmid_s, v_rmid_n, v_tl]) # West slope
        bm.faces.new([v_br, v_tr, v_rmid_n, v_rmid_s]) # East slope
        bm.faces.new([v_bl, v_br, v_rmid_s])           # South gable
        bm.faces.new([v_tl, v_rmid_n, v_tr])           # North gable
        
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        obj.data.materials.append(mat)
    return obj


def build_scene(scene_data):
    clean_scene()
    mats = setup_materials()
    
    # 1. Ground Planes
    # Lower Piazza: Z=0.0
    create_box("LowerPiazza", 1.0, 35.0, 7.0, 23.0, -0.5, 0.0, mats["piazza"])
    # Upper Terrace: Z=2.8
    create_box("UpperTerrace", 7.0, 29.0, 1.0, 7.0, 0.0, 2.8, mats["terrace"])
    
    # 2. Retaining Walls (Z=0.0 to 2.8)
    create_box("RetainingWallWest", 7.5, 15.8, 6.8, 7.2, 0.0, 2.9, mats["stone"])
    create_box("RetainingWallEast", 18.6, 28.5, 6.8, 7.2, 0.0, 2.9, mats["stone"])
    
    # 3. Overlook Balustrade
    create_box("OverlookBalustrade", 22.0, 34.5, 21.8, 22.4, 0.0, 1.1, mats["stone"])
    
    # 4. Central Stairs (14 steps)
    for i in range(14):
        t0 = i / 14.0
        t1 = (i + 1) / 14.0
        y_w0 = 10.4 - t0 * (10.4 - 6.8)
        y_w1 = 10.4 - t1 * (10.4 - 6.8)
        z_step = (i + 1) * 0.2
        create_box(f"StairStep_{i}", 15.8, 18.6, y_w1, y_w0, 0.0, z_step, mats["stone"])
        
    # 5. Buildings
    for b in scene_data["buildings"]:
        fp = b["footprint_m"]
        zb = b["elevation_z_m"]
        wh = b["wall_height_m"]
        rh = b["roof_height_m"]
        
        # Walls
        create_box(f"{b['id']}_walls", fp["x_min"], fp["x_max"], fp["y_min"], fp["y_max"], zb, zb + wh, mats["stone"])
        # Roof
        create_gable_roof(f"{b['id']}_roof", fp["x_min"], fp["x_max"], fp["y_min"], fp["y_max"], zb + wh, rh, b.get("roof_ridge_axis", "E-W"), mats["roof"])
        
        # Door
        d = b.get("door")
        if d:
            dx = d["x_m"]
            dy = d["y_m"]
            create_box(f"{b['id']}_door", dx - 0.6, dx + 0.6, dy - 0.1, dy + 0.1, zb, zb + d["height_m"], mats["wood"])
            
    # Chimney on House B
    create_box("HouseB_Chimney", 10.0, 10.8, 4.0, 4.8, 2.8 + 7.6, 2.8 + 7.6 + 2.0, mats["stone"])
    
    # 6. Fountain (Octagonal basin + center spout)
    fc_x, fc_y = scene_data["fountain"]["center_m"]
    r = scene_data["fountain"]["radius_m"]
    # Basin
    create_box("FountainBasin", fc_x - r, fc_x + r, fc_y - r, fc_y + r, 0.0, 0.8, mats["stone"])
    create_box("FountainWater", fc_x - r + 0.2, fc_x + r - 0.2, fc_y - r + 0.2, fc_y + r - 0.2, 0.0, 0.7, mats["water"])
    create_box("FountainSpout", fc_x - 0.25, fc_x + 0.25, fc_y - 0.25, fc_y + 0.25, 0.0, 2.2, mats["stone"])
    
    # 7. Olive Tree
    tc_x, tc_y = scene_data["vegetation_regions"][0]["center_m"]
    create_box("TreeTrunk", tc_x - 0.35, tc_x + 0.35, tc_y - 0.35, tc_y + 0.35, 0.0, 2.6, mats["wood"])
    create_box("TreeCanopy", tc_x - 2.8, tc_x + 2.8, tc_y - 2.8, tc_y + 2.8, 2.6, 6.4, mats["foliage"])
    
    # 8. Distant Mountains Backdrop
    create_box("FarMountains", -25.0, 25.0, -18.0, -17.0, -2.0, 12.0, mats["mountains"])
    
    # 9. Camera Setup (Orthographic, 56 deg pitch, 45 deg yaw)
    cam_data = bpy.data.cameras.new(name="CanonicalCamera")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 32.0
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    
    # Position camera back-right looking forward-left at 56° pitch, 45° yaw
    pitch_rad = math.radians(56.0)
    yaw_rad = math.radians(-45.0)
    dist = 40.0
    cam_obj.location = (
        dist * math.cos(pitch_rad) * math.sin(yaw_rad),
        -dist * math.cos(pitch_rad) * math.cos(yaw_rad),
        dist * math.sin(pitch_rad)
    )
    cam_obj.rotation_euler = (pitch_rad, 0.0, -yaw_rad)
    
    # 10. Lighting Rig (Warm Mediterranean Morning Sunlight)
    sun_data = bpy.data.lights.new(name="SunLight", type="SUN")
    sun_data.energy = 4.2
    sun_data.color = (1.0, 0.94, 0.85)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(48.0), math.radians(20.0), math.radians(-135.0))
    
    # World Ambient
    world = bpy.data.worlds.new(name="AppenninoSky")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.78, 0.86, 0.96, 1.0)
        bg.inputs["Strength"].default_value = 0.8
    bpy.context.scene.world = world
    
    # Render Settings
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080


def render_candidate(filepath):
    bpy.context.scene.render.filepath = str(filepath)
    bpy.ops.render.render(write_still=True)
    print(f"--> Successfully rendered: {filepath}")


if __name__ == "__main__":
    with open(SCENE_JSON, "r", encoding="utf-8") as f:
        sdata = json.load(f)
    build_scene(sdata)
    
    # Render Candidate 01 (Clean Cycles procedural pass)
    c1_path = GEN_DIR / "candidate_01.png"
    render_candidate(c1_path)
