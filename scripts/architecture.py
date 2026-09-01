"""
Procedural Architectural Generator for Appennino Hill Town.
Generates parametric stone houses, roofs with rafter tails, arched doors,
shuttered windows with mullions, balconies, chimneys, stone staircases, and retaining walls.
"""

import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler
from .materials import initialize_all_materials
from .props import create_flower_box, create_flower_pot, create_wall_lantern
from .vegetation import create_ivy_patch


def add_corner_quoins(bm, width, depth, height, quoin_size=0.32, quoin_thick=0.02):
    """
    Adds alternating stone corner blocks (quoins) to building edges.
    """
    hw = width / 2
    hd = depth / 2
    corners = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
    num_quoins = max(2, int(height / (quoin_size * 1.5)))
    step_z = height / num_quoins

    for cx, cy in corners:
        sign_x = 1.0 if cx > 0 else -1.0
        sign_y = 1.0 if cy > 0 else -1.0
        for i in range(num_quoins):
            z_pos = (i + 0.5) * step_z
            is_long_x = (i % 2 == 0)
            lx = quoin_size * 1.2 if is_long_x else quoin_size * 0.7
            ly = quoin_size * 0.7 if is_long_x else quoin_size * 1.2

            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts[-8:]:
                v.co.x = cx + sign_x * (v.co.x * lx - (quoin_thick if sign_x < 0 else -quoin_thick) / 2)
                v.co.y = cy + sign_y * (v.co.y * ly - (quoin_thick if sign_y < 0 else -quoin_thick) / 2)
                v.co.z = z_pos + v.co.z * (step_z * 0.85)


def create_roof(name, parent_group, width, depth, height_offset, pitch_height=1.5, style="gable", overhang=0.45):
    """
    Creates a detailed terracotta roof with overhang eaves, timber rafter tails,
    tile rows, and ridge cap tiles.
    """
    mats = initialize_all_materials()
    rw = width + overhang * 2
    rd = depth + overhang * 2

    # 1. Main Roof Geometry
    mesh_roof = bpy.data.meshes.new(f"{name}_Roof_Mesh")
    bm_r = bmesh.new()

    if style == "gable":
        verts = [
            bm_r.verts.new((-rw / 2, -rd / 2, 0.0)),
            bm_r.verts.new((rw / 2, -rd / 2, 0.0)),
            bm_r.verts.new((rw / 2, rd / 2, 0.0)),
            bm_r.verts.new((-rw / 2, rd / 2, 0.0)),
            bm_r.verts.new((-rw / 2, 0.0, pitch_height)),
            bm_r.verts.new((rw / 2, 0.0, pitch_height)),
        ]
        bm_r.faces.new([verts[0], verts[1], verts[5], verts[4]])
        bm_r.faces.new([verts[2], verts[3], verts[4], verts[5]])
        bm_r.faces.new([verts[3], verts[0], verts[4]])
        bm_r.faces.new([verts[1], verts[2], verts[5]])
        bm_r.faces.new([verts[0], verts[3], verts[2], verts[1]])
    else:  # Hip roof
        verts = [
            bm_r.verts.new((-rw / 2, -rd / 2, 0.0)),
            bm_r.verts.new((rw / 2, -rd / 2, 0.0)),
            bm_r.verts.new((rw / 2, rd / 2, 0.0)),
            bm_r.verts.new((-rw / 2, rd / 2, 0.0)),
            bm_r.verts.new((-rw * 0.25, 0.0, pitch_height)),
            bm_r.verts.new((rw * 0.25, 0.0, pitch_height)),
        ]
        bm_r.faces.new([verts[0], verts[1], verts[5], verts[4]])
        bm_r.faces.new([verts[2], verts[3], verts[4], verts[5]])
        bm_r.faces.new([verts[3], verts[0], verts[4]])
        bm_r.faces.new([verts[1], verts[2], verts[5]])
        bm_r.faces.new([verts[0], verts[3], verts[2], verts[1]])

    # Ridge Cap tiles (cylinder along top peak)
    ridge_len = rw if style == "gable" else rw * 0.55
    bmesh.ops.create_cone(
        bm_r, cap_ends=True, segments=8,
        radius1=0.12, radius2=0.12, depth=ridge_len * 1.02
    )
    for v in bm_r.verts[-10:]:
        vx, vy, vz = v.co.x, v.co.y, v.co.z
        v.co.x = vz
        v.co.y = vy
        v.co.z = vx + pitch_height + 0.04

    bm_r.to_mesh(mesh_roof)
    bm_r.free()

    obj_roof = bpy.data.objects.new(f"{name}_Roof_Obj", mesh_roof)
    obj_roof.location = Vector((0, 0, height_offset))
    obj_roof.data.materials.append(mats["roof"])
    obj_roof.parent = parent_group
    bpy.context.scene.collection.objects.link(obj_roof)

    # 2. Timber Rafter Tails underneath the roof overhang
    mesh_rafters = bpy.data.meshes.new(f"{name}_Rafters")
    bm_raf = bmesh.new()
    num_rafters = max(4, int(rw / 0.55))
    step_raf = rw / (num_rafters + 1)
    for side in [-1, 1]:
        y_pos = side * (depth / 2 + overhang * 0.5)
        for i in range(1, num_rafters + 1):
            x_pos = -rw / 2 + i * step_raf
            bmesh.ops.create_cube(bm_raf, size=1.0)
            for v in bm_raf.verts[-8:]:
                v.co.x = x_pos + v.co.x * 0.12
                v.co.y = y_pos + v.co.y * (overhang * 0.9)
                v.co.z = v.co.z * 0.14 - 0.08

    bm_raf.to_mesh(mesh_rafters)
    bm_raf.free()

    obj_rafters = bpy.data.objects.new(f"{name}_Rafters_Obj", mesh_rafters)
    obj_rafters.location = Vector((0, 0, height_offset))
    obj_rafters.data.materials.append(mats["wood"])
    obj_rafters.parent = parent_group
    bpy.context.scene.collection.objects.link(obj_rafters)


def create_door(name, parent_group, location, width=1.05, height=2.1, style="arched"):
    """
    Creates an aged wooden door with stone arch / surround and iron handle.
    """
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.parent = parent_group
    bpy.context.scene.collection.objects.link(group)

    # 1. Wooden Door Panel
    mesh_door = bpy.data.meshes.new(f"{name}_Panel")
    bm_d = bmesh.new()

    if style == "arched":
        bmesh.ops.create_cube(bm_d, size=1.0)
        for v in bm_d.verts:
            v.co.x *= width * 0.95
            v.co.y *= 0.08
            v.co.z = (v.co.z + 0.5) * (height - width / 2)
        bmesh.ops.create_cone(
            bm_d, cap_ends=True, segments=12,
            radius1=width * 0.475, radius2=width * 0.475, depth=0.08
        )
        for v in bm_d.verts[-14:]:
            vx, vy, vz = v.co.x, v.co.y, v.co.z
            v.co.y = vz
            v.co.z = vy + (height - width / 2)
    else:
        bmesh.ops.create_cube(bm_d, size=1.0)
        for v in bm_d.verts:
            v.co.x *= width * 0.95
            v.co.y *= 0.08
            v.co.z = (v.co.z + 0.5) * height

    bm_d.to_mesh(mesh_door)
    bm_d.free()

    obj_door = bpy.data.objects.new(f"{name}_Panel_Obj", mesh_door)
    obj_door.data.materials.append(mats["wood"])
    obj_door.parent = group
    bpy.context.scene.collection.objects.link(obj_door)

    # 2. Stone Arch Surround (Voussoirs / Frame)
    mesh_frame = bpy.data.meshes.new(f"{name}_Surround")
    bm_f = bmesh.new()
    frame_thick = 0.15
    frame_depth = 0.12

    for side in [-1, 1]:
        bmesh.ops.create_cube(bm_f, size=1.0)
        for v in bm_f.verts[-8:]:
            v.co.x = side * (width / 2 + frame_thick / 2) + v.co.x * frame_thick
            v.co.y = v.co.y * frame_depth
            v.co.z = (v.co.z + 0.5) * (height - (width / 2 if style == "arched" else 0))

    if style == "arched":
        num_voussoirs = 7
        arch_r = width / 2 + frame_thick / 2
        for i in range(num_voussoirs):
            angle = math.pi * (i + 0.5) / num_voussoirs
            ax = -arch_r * math.cos(angle)
            az = (height - width / 2) + arch_r * math.sin(angle)
            bmesh.ops.create_cube(bm_f, size=1.0)
            for v in bm_f.verts[-8:]:
                v.co.x = ax + v.co.x * frame_thick * 1.05
                v.co.y = v.co.y * frame_depth
                v.co.z = az + v.co.z * frame_thick * 0.95
    else:
        bmesh.ops.create_cube(bm_f, size=1.0)
        for v in bm_f.verts[-8:]:
            v.co.x = v.co.x * (width + frame_thick * 2)
            v.co.y = v.co.y * frame_depth
            v.co.z = height + frame_thick / 2 + v.co.z * frame_thick

    bm_f.to_mesh(mesh_frame)
    bm_f.free()

    obj_frame = bpy.data.objects.new(f"{name}_Surround_Obj", mesh_frame)
    obj_frame.data.materials.append(mats["limestone"])
    obj_frame.parent = group
    bpy.context.scene.collection.objects.link(obj_frame)

    return group


def create_window(name, parent_group, location, width=0.9, height=1.3, arched=True, shutters=True, shutter_color="green", flower_box=False):
    """
    Creates an authentic window with stone sill, mullions, wooden shutters, and optional flower box.
    """
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.parent = parent_group
    bpy.context.scene.collection.objects.link(group)

    # 1. Glass Pane (Dark recessed opening)
    mesh_glass = bpy.data.meshes.new(f"{name}_Glass")
    bm_g = bmesh.new()
    bmesh.ops.create_cube(bm_g, size=1.0)
    for v in bm_g.verts:
        v.co.x *= width * 0.92
        v.co.y *= 0.05
        v.co.z = (v.co.z + 0.5) * height
    bm_g.to_mesh(mesh_glass)
    bm_g.free()

    obj_glass = bpy.data.objects.new(f"{name}_Glass_Obj", mesh_glass)
    obj_glass.data.materials.append(mats["glass"])
    obj_glass.parent = group
    bpy.context.scene.collection.objects.link(obj_glass)

    # 2. Window Mullions / Wooden Grille
    mesh_mull = bpy.data.meshes.new(f"{name}_Mullions")
    bm_m = bmesh.new()
    # Vertical divider
    bmesh.ops.create_cube(bm_m, size=0.035)
    for v in bm_m.verts:
        v.co.z = (v.co.z + 0.5) * height
    # Horizontal divider
    bmesh.ops.create_cube(bm_m, size=0.035)
    for v in bm_m.verts[-8:]:
        v.co.x *= (width * 0.9) / 0.035
        v.co.z = height * 0.55
    bm_m.to_mesh(mesh_mull)
    bm_m.free()

    obj_mull = bpy.data.objects.new(f"{name}_Mullions_Obj", mesh_mull)
    obj_mull.data.materials.append(mats["wood"])
    obj_mull.parent = group
    bpy.context.scene.collection.objects.link(obj_mull)

    # 3. Stone Sill
    mesh_sill = bpy.data.meshes.new(f"{name}_Sill")
    bm_s = bmesh.new()
    bmesh.ops.create_cube(bm_s, size=1.0)
    for v in bm_s.verts:
        v.co.x *= width * 1.25
        v.co.y *= 0.20
        v.co.z *= 0.09
    bm_s.to_mesh(mesh_sill)
    bm_s.free()

    obj_sill = bpy.data.objects.new(f"{name}_Sill_Obj", mesh_sill)
    obj_sill.location = Vector((0, -0.05, -0.045))
    obj_sill.data.materials.append(mats["limestone"])
    obj_sill.parent = group
    bpy.context.scene.collection.objects.link(obj_sill)

    # 4. Wooden Shutters (Open/Ajar)
    if shutters:
        shutter_mat = mats["shutter_green"] if shutter_color == "green" else mats["shutter_brown"]
        shutter_w = width * 0.50
        shutter_h = height * 0.95

        for side, angle_deg in [(-1, 22.0), (1, -22.0)]:
            mesh_sh = bpy.data.meshes.new(f"{name}_Shutter_{'L' if side < 0 else 'R'}")
            bm_sh = bmesh.new()
            bmesh.ops.create_cube(bm_sh, size=1.0)
            for v in bm_sh.verts:
                v.co.x = (v.co.x + 0.5) * shutter_w * side
                v.co.y *= 0.04
                v.co.z = (v.co.z + 0.5) * shutter_h
            bm_sh.to_mesh(mesh_sh)
            bm_sh.free()

            obj_sh = bpy.data.objects.new(f"{name}_Shutter_{'L' if side < 0 else 'R'}_Obj", mesh_sh)
            obj_sh.location = Vector((side * (width / 2 + 0.02), -0.05, 0.0))
            obj_sh.rotation_euler = Euler((0, 0, math.radians(angle_deg * side)), 'XYZ')
            obj_sh.data.materials.append(shutter_mat)
            obj_sh.parent = group
            bpy.context.scene.collection.objects.link(obj_sh)

    # 5. Flower Box
    if flower_box:
        fb = create_flower_box(
            f"{name}_FB", location=(0, -0.15, -0.10),
            width=width * 1.15, depth=0.22, height=0.18, flower_color="red"
        )
        fb.parent = group

    return group


def create_balcony(name, parent_group, location, width=2.0, depth=0.85):
    """
    Creates a traditional Italian stone balcony with wrought iron railing and flower boxes.
    """
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.parent = parent_group
    bpy.context.scene.collection.objects.link(group)

    # 1. Cantilevered Stone Slab Base
    mesh_slab = bpy.data.meshes.new(f"{name}_Slab")
    bm_s = bmesh.new()
    bmesh.ops.create_cube(bm_s, size=1.0)
    for v in bm_s.verts:
        v.co.x *= width
        v.co.y = (v.co.y - 0.5) * depth
        v.co.z *= 0.16

    for bx in [-width * 0.35, width * 0.35]:
        bmesh.ops.create_cone(bm_s, cap_ends=True, segments=4, radius1=0.14, radius2=0.04, depth=0.45)
        for v in bm_s.verts[-6:]:
            v.co.x += bx
            v.co.y -= depth * 0.3
            v.co.z -= 0.28

    bm_s.to_mesh(mesh_slab)
    bm_s.free()

    obj_slab = bpy.data.objects.new(f"{name}_Slab_Obj", mesh_slab)
    obj_slab.data.materials.append(mats["limestone"])
    obj_slab.parent = group
    bpy.context.scene.collection.objects.link(obj_slab)

    # 2. Wrought Iron Railing
    mesh_rail = bpy.data.meshes.new(f"{name}_Rail")
    bm_r = bmesh.new()
    rail_h = 0.85

    bmesh.ops.create_cube(bm_r, size=1.0)
    for v in bm_r.verts[-8:]:
        v.co.x *= width
        v.co.y = -depth + v.co.y * 0.05
        v.co.z = rail_h + v.co.z * 0.04

    for side in [-1, 1]:
        bmesh.ops.create_cube(bm_r, size=1.0)
        for v in bm_r.verts[-8:]:
            v.co.x = side * (width / 2) + v.co.x * 0.04
            v.co.y = -depth / 2 + v.co.y * depth
            v.co.z = rail_h + v.co.z * 0.04

    num_bars = max(4, int(width / 0.22))
    step_bar = width / (num_bars + 1)
    for i in range(1, num_bars + 1):
        bx = -width / 2 + i * step_bar
        bmesh.ops.create_cube(bm_r, size=0.03)
        for v in bm_r.verts[-8:]:
            v.co.x += bx
            v.co.y -= depth
            v.co.z = (v.co.z + 0.5) * rail_h

    bm_r.to_mesh(mesh_rail)
    bm_r.free()

    obj_rail = bpy.data.objects.new(f"{name}_Rail_Obj", mesh_rail)
    obj_rail.data.materials.append(mats["iron"])
    obj_rail.parent = group
    bpy.context.scene.collection.objects.link(obj_rail)

    # 3. Flower Box on Railing
    fb = create_flower_box(
        f"{name}_FB", location=(0, -depth - 0.10, rail_h * 0.65),
        width=width * 0.85, depth=0.22, height=0.18, flower_color="red"
    )
    fb.parent = group

    return group


def create_chimney(name, parent_group, location, width=0.65, depth=0.65, height=1.6):
    """
    Creates a stone chimney with terracotta slab cap.
    """
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.parent = parent_group
    bpy.context.scene.collection.objects.link(group)

    mesh_st = bpy.data.meshes.new(f"{name}_Stack")
    bm_s = bmesh.new()
    bmesh.ops.create_cube(bm_s, size=1.0)
    for v in bm_s.verts:
        v.co.x *= width
        v.co.y *= depth
        v.co.z = (v.co.z + 0.5) * height

    bmesh.ops.create_cube(bm_s, size=1.0)
    for v in bm_s.verts[-8:]:
        v.co.x *= width * 1.25
        v.co.y *= depth * 1.25
        v.co.z = height + 0.05 + v.co.z * 0.08

    for ox, oy in [(-width * 0.2, 0), (width * 0.2, 0)]:
        bmesh.ops.create_cone(bm_s, cap_ends=True, segments=8, radius1=0.10, radius2=0.08, depth=0.25)
        for v in bm_s.verts[-10:]:
            v.co.x += ox
            v.co.y += oy
            v.co.z += height + 0.22

    bm_s.to_mesh(mesh_st)
    bm_s.free()

    obj_st = bpy.data.objects.new(f"{name}_Stack_Obj", mesh_st)
    obj_st.data.materials.append(mats["limestone"])
    obj_st.parent = group
    bpy.context.scene.collection.objects.link(obj_st)

    return group


def create_stone_house(
    name="Stone_House",
    location=(0, 0, 0),
    rotation_z=0.0,
    width=6.0,
    depth=5.0,
    floors=2,
    floor_height=2.8,
    roof_type="gable",
    roof_pitch=1.6,
    roof_overhang=0.45,
    door_style="arched",
    shutter_color="green",
    balcony_floor=2,
    flowerboxes=True,
    chimney=True,
    ivy=True,
):
    """
    Assembles a complete Appennino stone house with parametric variations.
    """
    mats = initialize_all_materials()
    house_group = bpy.data.objects.new(name, None)
    house_group.location = Vector(location)
    house_group.rotation_euler = Euler((0, 0, rotation_z), 'XYZ')
    bpy.context.scene.collection.objects.link(house_group)

    total_height = floors * floor_height

    # 1. Main Stone Body Mesh
    mesh_body = bpy.data.meshes.new(f"{name}_Body")
    bm_b = bmesh.new()

    bmesh.ops.create_cube(bm_b, size=1.0)
    for v in bm_b.verts:
        v.co.x *= width
        v.co.y *= depth
        v.co.z = (v.co.z + 0.5) * total_height

    if roof_type == "gable":
        verts_gable = [
            bm_b.verts.new((-width / 2, -depth / 2, total_height)),
            bm_b.verts.new((-width / 2, depth / 2, total_height)),
            bm_b.verts.new((-width / 2, 0.0, total_height + roof_pitch)),
            bm_b.verts.new((width / 2, -depth / 2, total_height)),
            bm_b.verts.new((width / 2, depth / 2, total_height)),
            bm_b.verts.new((width / 2, 0.0, total_height + roof_pitch)),
        ]
        bm_b.faces.new([verts_gable[0], verts_gable[1], verts_gable[2]])
        bm_b.faces.new([verts_gable[4], verts_gable[3], verts_gable[5]])

    add_corner_quoins(bm_b, width, depth, total_height)

    bm_b.to_mesh(mesh_body)
    bm_b.free()

    obj_body = bpy.data.objects.new(f"{name}_Body_Obj", mesh_body)
    obj_body.data.materials.append(mats["limestone"])
    obj_body.parent = house_group
    bpy.context.scene.collection.objects.link(obj_body)

    # 2. Roof
    create_roof(
        f"{name}_Roof", house_group, width, depth,
        height_offset=total_height, pitch_height=roof_pitch,
        style=roof_type, overhang=roof_overhang
    )

    # 3. Ground Floor Door (Front Façade, Y = -depth/2)
    door_x = -width * 0.22
    create_door(
        f"{name}_Door", house_group,
        location=(door_x, -depth / 2 - 0.02, 0.0),
        width=1.05, height=2.1, style=door_style
    )

    # Ground Floor Window (Front Façade)
    win_x = width * 0.25
    create_window(
        f"{name}_G_Win", house_group,
        location=(win_x, -depth / 2 - 0.02, 0.9),
        width=0.9, height=1.3, arched=False,
        shutters=True, shutter_color=shutter_color, flower_box=flowerboxes
    )

    # 4. Upper Floors Windows & Balcony
    for fl in range(2, floors + 1):
        fl_z = (fl - 1) * floor_height
        if fl == balcony_floor:
            create_balcony(
                f"{name}_F{fl}_Balcony", house_group,
                location=(-width * 0.15, -depth / 2 - 0.02, fl_z + 0.35),
                width=2.1, depth=0.8
            )
            create_door(
                f"{name}_F{fl}_BalconyDoor", house_group,
                location=(-width * 0.15, -depth / 2 - 0.02, fl_z + 0.35),
                width=1.1, height=2.1, style="rectangular"
            )
            create_window(
                f"{name}_F{fl}_Win_R", house_group,
                location=(width * 0.28, -depth / 2 - 0.02, fl_z + 0.8),
                width=0.85, height=1.25, arched=True,
                shutters=True, shutter_color=shutter_color, flower_box=flowerboxes
            )
        else:
            for wx, arched in [(-width * 0.25, True), (width * 0.25, True)]:
                create_window(
                    f"{name}_F{fl}_Win_{'L' if wx < 0 else 'R'}", house_group,
                    location=(wx, -depth / 2 - 0.02, fl_z + 0.8),
                    width=0.85, height=1.25, arched=arched,
                    shutters=True, shutter_color=shutter_color, flower_box=flowerboxes
                )

    # 5. Side Façade Windows (X = width/2)
    if depth >= 3.8:
        for fl in range(1, floors + 1):
            fl_z = (fl - 1) * floor_height + 0.8
            create_window(
                f"{name}_Side_Win_F{fl}", house_group,
                location=(width / 2 + 0.02, 0.0, fl_z),
                width=0.8, height=1.1, arched=True,
                shutters=True, shutter_color=shutter_color, flower_box=False
            )

    # 6. Chimney
    if chimney:
        chim_x = width * 0.28
        chim_y = -depth * 0.15
        chim_z = total_height + (roof_pitch * 0.5)
        create_chimney(
            f"{name}_Chimney", house_group,
            location=(chim_x, chim_y, chim_z),
            width=0.6, depth=0.6, height=1.7
        )

    # 7. Climbing Ivy on corner
    if ivy:
        create_ivy_patch(
            f"{name}_Ivy", location=(-width / 2 + 0.5, -depth / 2 - 0.02, 0.2),
            width=1.6, height=total_height * 0.7, density=14
        )

    return house_group


def create_staircase(
    name="Stone_Staircase",
    location=(0, 0, 0),
    rotation_z=0.0,
    width=1.8,
    steps=10,
    tread=0.34,
    riser=0.18,
    side_wall=True,
):
    """
    Creates an authentic stone staircase ascending an elevation change.
    """
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.rotation_euler = Euler((0, 0, rotation_z), 'XYZ')
    bpy.context.scene.collection.objects.link(group)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    for i in range(steps):
        y_start = i * tread
        z_start = i * riser
        step_depth = tread * 1.05
        step_height = riser

        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts[-8:]:
            v.co.x *= width
            v.co.y = y_start + (v.co.y + 0.5) * step_depth
            v.co.z = z_start + (v.co.z + 0.5) * step_height

    if side_wall:
        total_len = steps * tread
        total_h = steps * riser
        for side in [-1, 1]:
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts[-8:]:
                v.co.x = side * (width / 2 + 0.14) + v.co.x * 0.25
                v.co.y = (v.co.y + 0.5) * (total_len + tread)
                v.co.z = (v.co.y / total_len) * total_h + (v.co.z + 0.5) * 0.65

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(f"{name}_Obj", mesh)
    obj.data.materials.append(mats["limestone"])
    obj.parent = group
    bpy.context.scene.collection.objects.link(obj)

    create_flower_pot(
        f"{name}_Pot", location=(width / 2 + 0.15, tread * 0.5, 0.65),
        radius=0.18, height=0.28, flower_color="pink"
    ).parent = group

    return group


def create_retaining_wall(
    name="Retaining_Wall",
    location=(0, 0, 0),
    rotation_z=0.0,
    length=8.0,
    height=2.2,
    thickness=0.6,
    coping_stones=True,
):
    """
    Creates a heavy stone retaining wall with coping stones along top.
    """
    mats = initialize_all_materials()
    group = bpy.data.objects.new(name, None)
    group.location = Vector(location)
    group.rotation_euler = Euler((0, 0, rotation_z), 'XYZ')
    bpy.context.scene.collection.objects.link(group)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm = bmesh.new()

    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= length
        v.co.y *= thickness
        v.co.z = (v.co.z + 0.5) * height
        if v.co.z > height * 0.5:
            v.co.y *= 0.88

    if coping_stones:
        num_copings = max(4, int(length / 0.65))
        step_c = length / num_copings
        for i in range(num_copings):
            cx = -length / 2 + (i + 0.5) * step_c
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts[-8:]:
                v.co.x = cx + v.co.x * (step_c * 0.96)
                v.co.y *= thickness * 1.2
                v.co.z = height + 0.06 + v.co.z * 0.12

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(f"{name}_Obj", mesh)
    obj.data.materials.append(mats["limestone"])
    obj.parent = group
    bpy.context.scene.collection.objects.link(obj)

    create_ivy_patch(
        f"{name}_Ivy", location=(-length * 0.2, -thickness / 2 - 0.02, 0.1),
        width=2.0, height=height * 0.85, density=12
    ).parent = group

    return group
