"""
Procedural Environmental Props for Appennino Town.
Fountain, lanterns, barrels, crates, flower boxes, flower pots, and scale reference.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler
from .materials import initialize_all_materials


def create_fountain(name="Stone_Fountain", location=(0, 0, 0), radius=1.3, height=1.6):
    """
    Creates an authentic Italian stone fountain with tiered basin, center column,
    water pool, and spout accents.
    """
    mats = initialize_all_materials()
    fountain_group = bpy.data.objects.new(name, None)
    fountain_group.location = Vector(location)
    bpy.context.scene.collection.objects.link(fountain_group)

    # 1. Lower Stone Basin (Octagonal / Carved wall with coping rim)
    mesh_basin = bpy.data.meshes.new(f"{name}_Basin")
    bm = bmesh.new()
    segments = 16
    basin_h = 0.65

    # Outer cylinder with flared rim
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=radius * 0.95, radius2=radius * 1.05, depth=basin_h
    )
    for v in bm.verts:
        v.co.z += basin_h / 2

    # Basin coping rim
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=segments,
        radius1=radius * 1.12, radius2=radius * 1.12, depth=0.12
    )
    for v in bm.verts[-segments * 2:]:
        v.co.z += basin_h + 0.04

    bm.to_mesh(mesh_basin)
    bm.free()

    obj_basin = bpy.data.objects.new(f"{name}_Basin_Obj", mesh_basin)
    obj_basin.data.materials.append(mats["limestone"])
    obj_basin.parent = fountain_group
    bpy.context.scene.collection.objects.link(obj_basin)

    # 2. Water Surface Disc
    mesh_water = bpy.data.meshes.new(f"{name}_Water")
    bm_w = bmesh.new()
    bmesh.ops.create_circle(bm_w, cap_ends=True, segments=segments, radius=radius * 0.96)
    bm_w.to_mesh(mesh_water)
    bm_w.free()

    obj_water = bpy.data.objects.new(f"{name}_Water_Obj", mesh_water)
    obj_water.location = Vector((0, 0, basin_h * 0.82))
    obj_water.data.materials.append(mats["water"])
    obj_water.parent = fountain_group
    bpy.context.scene.collection.objects.link(obj_water)

    # 3. Center Pedestal & Upper Tier Basin
    mesh_col = bpy.data.meshes.new(f"{name}_Center")
    bm_c = bmesh.new()

    # Pedestal base
    bmesh.ops.create_cube(bm_c, size=0.6)
    for v in bm_c.verts:
        v.co.z += 0.3
    # Pillar shaft
    bmesh.ops.create_cone(
        bm_c, cap_ends=True, segments=12,
        radius1=0.22, radius2=0.18, depth=height * 0.6
    )
    for v in bm_c.verts[-14:]:
        v.co.z += height * 0.45

    # Upper Tier Basin
    bmesh.ops.create_cone(
        bm_c, cap_ends=True, segments=12,
        radius1=0.14, radius2=0.55, depth=0.24
    )
    for v in bm_c.verts[-14:]:
        v.co.z += height * 0.75

    # Center finial tip
    bmesh.ops.create_icosphere(bm_c, subdivisions=2, radius=0.15)
    for v in bm_c.verts[-42:]:
        v.co.z += height * 0.98

    bm_c.to_mesh(mesh_col)
    bm_c.free()

    obj_col = bpy.data.objects.new(f"{name}_Center_Obj", mesh_col)
    obj_col.data.materials.append(mats["limestone"])
    obj_col.parent = fountain_group
    bpy.context.scene.collection.objects.link(obj_col)

    return fountain_group


def create_wall_lantern(name="Wall_Lantern", location=(0, 0, 0), rot_z=0.0):
    """Creates a classic wrought iron street/wall lantern."""
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.rotation_euler = Euler((0, 0, rot_z), 'XYZ')
    bpy.context.scene.collection.objects.link(group)

    mesh_iron = bpy.data.meshes.new(f"{name}_Bracket")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.12)
    for v in bm.verts:
        v.co.x = v.co.x * 0.2 - 0.25
        v.co.z *= 2.0

    bmesh.ops.create_cube(bm, size=0.04)
    for v in bm.verts[-8:]:
        v.co.x = v.co.x * 6.0
        v.co.z += 0.1

    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=4,
        radius1=0.10, radius2=0.16, depth=0.28
    )
    for v in bm.verts[-6:]:
        v.co.z -= 0.12

    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=4,
        radius1=0.18, radius2=0.02, depth=0.12
    )
    for v in bm.verts[-6:]:
        v.co.z += 0.08

    bm.to_mesh(mesh_iron)
    bm.free()

    obj_iron = bpy.data.objects.new(f"{name}_Iron_Obj", mesh_iron)
    obj_iron.data.materials.append(mats["iron"])
    obj_iron.parent = group
    bpy.context.scene.collection.objects.link(obj_iron)

    mesh_glow = bpy.data.meshes.new(f"{name}_Glow")
    bm_g = bmesh.new()
    bmesh.ops.create_icosphere(bm_g, subdivisions=1, radius=0.06)
    bm_g.to_mesh(mesh_glow)
    bm_g.free()

    obj_glow = bpy.data.objects.new(f"{name}_Glow_Obj", mesh_glow)
    obj_glow.location = Vector((0, 0, -0.12))
    obj_glow.data.materials.append(mats["lantern_glow"])
    obj_glow.parent = group
    bpy.context.scene.collection.objects.link(obj_glow)

    return group


def create_barrel(name="Barrel", location=(0, 0, 0), radius=0.36, height=0.85):
    """Creates a wooden barrel with iron hoops."""
    mats = initialize_all_materials()
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=12,
        radius1=radius * 0.88, radius2=radius * 0.88, depth=height
    )
    for v in bm.verts:
        if abs(v.co.z) < height * 0.3:
            v.co.x *= 1.15
            v.co.y *= 1.15

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location) + Vector((0, 0, height / 2))
    obj.data.materials.append(mats["wood"])
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_crate(name="Crate", location=(0, 0, 0), size=0.60):
    """Creates a rustic wooden crate."""
    mats = initialize_all_materials()
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location) + Vector((0, 0, size / 2))
    obj.data.materials.append(mats["wood"])
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_flower_pot(name="Flower_Pot", location=(0, 0, 0), radius=0.20, height=0.32, flower_color="red"):
    """Creates a terracotta flower pot with blooming plants."""
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    bpy.context.scene.collection.objects.link(group)

    mesh_pot = bpy.data.meshes.new(f"{name}_Pot")
    bm_p = bmesh.new()
    bmesh.ops.create_cone(
        bm_p, cap_ends=True, segments=10,
        radius1=radius * 0.75, radius2=radius, depth=height
    )
    bmesh.ops.create_cone(
        bm_p, cap_ends=True, segments=10,
        radius1=radius * 1.08, radius2=radius * 1.08, depth=height * 0.15
    )
    for v in bm_p.verts[-12:]:
        v.co.z += height * 0.45

    bm_p.to_mesh(mesh_pot)
    bm_p.free()

    obj_pot = bpy.data.objects.new(f"{name}_Pot_Obj", mesh_pot)
    obj_pot.location = Vector((0, 0, height / 2))
    obj_pot.data.materials.append(mats["pot"])
    obj_pot.parent = group
    bpy.context.scene.collection.objects.link(obj_pot)

    mesh_fol = bpy.data.meshes.new(f"{name}_Foliage")
    bm_f = bmesh.new()
    bmesh.ops.create_icosphere(bm_f, subdivisions=1, radius=radius * 1.1)
    for v in bm_f.verts:
        v.co.z *= 0.8
    bm_f.to_mesh(mesh_fol)
    bm_f.free()

    obj_fol = bpy.data.objects.new(f"{name}_Foliage_Obj", mesh_fol)
    obj_fol.location = Vector((0, 0, height * 0.95))
    obj_fol.data.materials.append(mats["foliage"])
    obj_fol.parent = group
    bpy.context.scene.collection.objects.link(obj_fol)

    mesh_flw = bpy.data.meshes.new(f"{name}_Blooms")
    bm_fl = bmesh.new()
    offsets = [
        (0.08, 0.05, 0.08), (-0.07, 0.08, 0.06), (0.02, -0.09, 0.07),
        (-0.06, -0.05, 0.05), (0.09, -0.04, 0.06)
    ]
    for ox, oy, oz in offsets:
        bmesh.ops.create_icosphere(bm_fl, subdivisions=1, radius=0.04)
        for v in bm_fl.verts[-12:]:
            v.co.x += ox
            v.co.y += oy
            v.co.z += oz

    bm_fl.to_mesh(mesh_flw)
    bm_fl.free()

    obj_flw = bpy.data.objects.new(f"{name}_Blooms_Obj", mesh_flw)
    obj_flw.location = Vector((0, 0, height * 1.05))
    flw_mat = mats["flower_pink"] if flower_color == "pink" else mats["flower_red"]
    obj_flw.data.materials.append(flw_mat)
    obj_flw.parent = group
    bpy.context.scene.collection.objects.link(obj_flw)

    return group


def create_flower_box(name="Flower_Box", location=(0, 0, 0), width=1.1, depth=0.26, height=0.22, flower_color="red"):
    """Creates a window planter box overflowing with flowers."""
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    bpy.context.scene.collection.objects.link(group)

    mesh_box = bpy.data.meshes.new(f"{name}_Box")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= width
        v.co.y *= depth
        v.co.z *= height
    bm.to_mesh(mesh_box)
    bm.free()

    obj_box = bpy.data.objects.new(f"{name}_Box_Obj", mesh_box)
    obj_box.data.materials.append(mats["pot"])
    obj_box.parent = group
    bpy.context.scene.collection.objects.link(obj_box)

    mesh_fol = bpy.data.meshes.new(f"{name}_Foliage")
    bm_f = bmesh.new()
    num_mounds = max(2, int(width / 0.35))
    step = width / num_mounds
    start_x = -width / 2 + step / 2
    for i in range(num_mounds):
        bmesh.ops.create_icosphere(bm_f, subdivisions=1, radius=depth * 0.85)
        for v in bm_f.verts[-12:]:
            v.co.x += start_x + i * step
            v.co.z += height * 0.65

    bm_f.to_mesh(mesh_fol)
    bm_f.free()

    obj_fol = bpy.data.objects.new(f"{name}_Foliage_Obj", mesh_fol)
    obj_fol.data.materials.append(mats["foliage"])
    obj_fol.parent = group
    bpy.context.scene.collection.objects.link(obj_fol)

    mesh_flw = bpy.data.meshes.new(f"{name}_Flowers")
    bm_fl = bmesh.new()
    num_flowers = num_mounds * 4
    for i in range(num_flowers):
        fx = -width * 0.45 + (i / max(1, num_flowers - 1)) * (width * 0.9)
        fy = (math.sin(i * 1.7) * 0.5) * depth * 0.7
        fz = height * 0.75 + abs(math.cos(i * 2.3)) * 0.08
        bmesh.ops.create_icosphere(bm_fl, subdivisions=1, radius=0.045)
        for v in bm_fl.verts[-12:]:
            v.co.x += fx
            v.co.y += fy
            v.co.z += fz

    bm_fl.to_mesh(mesh_flw)
    bm_fl.free()

    obj_flw = bpy.data.objects.new(f"{name}_Flowers_Obj", mesh_flw)
    flw_mat = mats["flower_pink"] if flower_color == "pink" else mats["flower_red"]
    obj_flw.data.materials.append(flw_mat)
    obj_flw.parent = group
    bpy.context.scene.collection.objects.link(obj_flw)

    return group


def create_human_scale_ref(name="Human_Scale_Ref", location=(0, 0, 0)):
    """Creates a 1.75m scale reference mannequin."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.22, radius2=0.25, depth=1.4)
    for v in bm.verts:
        v.co.z += 0.7
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.16)
    for v in bm.verts[-42:]:
        v.co.z += 1.58

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location)
    mat = bpy.data.materials.new("Mat_Scale_Ref")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 0.9, 1.0)
    obj.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(obj)
    return obj
