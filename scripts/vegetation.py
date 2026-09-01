"""
Procedural Vegetation & Foliage Generators for Appennino Town.
Climbing ivy, potted plants, shrubs, and stylized Mediterranean trees.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler
from .materials import initialize_all_materials


def create_ivy_patch(name="Ivy_Patch", location=(0, 0, 0), width=1.5, height=2.5, density=16, rot_z=0.0):
    """
    Creates organic climbing ivy patches clinging to stone building walls.
    """
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.rotation_euler = Euler((0, 0, rot_z), 'XYZ')
    bpy.context.scene.collection.objects.link(group)

    mesh = bpy.data.meshes.new(f"{name}_Leaves")
    bm = bmesh.new()

    random.seed(hash(name) % 10000)

    nodes = [(0.0, 0.0)]
    for i in range(density):
        nx = (random.random() - 0.5) * width
        ny = random.random() * height
        nodes.append((nx, ny))

    for nx, ny in nodes:
        rad = random.uniform(0.18, 0.32)
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rad)
        for v in bm.verts[-12:]:
            v.co.y *= 0.35
            v.co.x += nx
            v.co.z += ny
            v.co.y -= 0.04

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(f"{name}_Obj", mesh)
    obj.data.materials.append(mats["foliage"])
    obj.parent = group
    bpy.context.scene.collection.objects.link(obj)

    return group


def create_shrub(name="Shrub", location=(0, 0, 0), radius=0.6, height=0.8):
    """Creates a stylized garden shrub with soft foliage lobes."""
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    bpy.context.scene.collection.objects.link(group)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius)
    for v in bm.verts:
        v.co.z *= height / (radius * 2)
        v.co.z += height / 2

    offsets = [
        (radius * 0.45, radius * 0.35, height * 0.35),
        (-radius * 0.40, radius * 0.40, height * 0.30),
        (radius * 0.30, -radius * 0.45, height * 0.40),
        (-radius * 0.45, -radius * 0.30, height * 0.35),
    ]
    for ox, oy, oz in offsets:
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=radius * 0.65)
        for v in bm.verts[-12:]:
            v.co.x += ox
            v.co.y += oy
            v.co.z += oz

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(f"{name}_Obj", mesh)
    obj.data.materials.append(mats["foliage"])
    obj.parent = group
    bpy.context.scene.collection.objects.link(obj)

    return group


def create_stylized_tree(name="Mediterranean_Tree", location=(0, 0, 0), trunk_height=2.4, crown_radius=1.6):
    """Creates an authentic Mediterranean hill-town tree with leafy canopy clouds."""
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    bpy.context.scene.collection.objects.link(group)

    mesh_trunk = bpy.data.meshes.new(f"{name}_Trunk")
    bm_t = bmesh.new()
    bmesh.ops.create_cone(
        bm_t, cap_ends=True, segments=8,
        radius1=0.28, radius2=0.18, depth=trunk_height
    )
    for v in bm_t.verts:
        v.co.z += trunk_height / 2
        v.co.x += math.sin(v.co.z * 1.2) * 0.14

    bm_t.to_mesh(mesh_trunk)
    bm_t.free()

    obj_trunk = bpy.data.objects.new(f"{name}_Trunk_Obj", mesh_trunk)
    obj_trunk.data.materials.append(mats["wood"])
    obj_trunk.parent = group
    bpy.context.scene.collection.objects.link(obj_trunk)

    # Cloud-like foliage clusters
    mesh_leaves = bpy.data.meshes.new(f"{name}_Canopy")
    bm_l = bmesh.new()

    clusters = [
        (0.0, 0.0, trunk_height + crown_radius * 0.65, crown_radius * 0.95),
        (crown_radius * 0.55, 0.1, trunk_height + crown_radius * 0.50, crown_radius * 0.75),
        (-crown_radius * 0.50, crown_radius * 0.35, trunk_height + crown_radius * 0.60, crown_radius * 0.70),
        (0.1, -crown_radius * 0.55, trunk_height + crown_radius * 0.55, crown_radius * 0.72),
        (-crown_radius * 0.25, -crown_radius * 0.45, trunk_height + crown_radius * 0.85, crown_radius * 0.65),
    ]
    for cx, cy, cz, rad in clusters:
        bmesh.ops.create_icosphere(bm_l, subdivisions=2, radius=rad)
        for v in bm_l.verts[-42:]:
            v.co.x += cx
            v.co.y += cy
            v.co.z += cz

    bm_l.to_mesh(mesh_leaves)
    bm_l.free()

    obj_leaves = bpy.data.objects.new(f"{name}_Canopy_Obj", mesh_leaves)
    obj_leaves.data.materials.append(mats["foliage"])
    obj_leaves.parent = group
    bpy.context.scene.collection.objects.link(obj_leaves)

    return group
