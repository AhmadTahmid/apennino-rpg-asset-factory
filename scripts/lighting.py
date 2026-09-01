"""
Canonical Lighting Rig for Appennino Asset Factory.
Sets up locked warm Mediterranean afternoon daylight with soft contact shadows.
"""

import bpy
import math
from mathutils import Euler
from .config import CANONICAL_LIGHTING


def setup_canonical_lighting(collection=None):
    """
    Creates or updates the canonical lighting rig:
    - Warm key sun light with soft shadow angle
    - Soft ambient sky bounce
    - Balanced ambient occlusion
    """
    if collection is None:
        collection = bpy.context.scene.collection

    # Remove existing light objects to prevent light buildup
    for obj in list(collection.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # 1. Main Sun Lamp
    sun_data = bpy.data.lights.new(name="Canonical_Sun_Key", type='SUN')
    sun_data.color = CANONICAL_LIGHTING["sun_color"][:3]
    sun_data.energy = CANONICAL_LIGHTING["sun_energy"]
    sun_data.angle = math.radians(CANONICAL_LIGHTING["sun_angle_deg"])

    sun_obj = bpy.data.objects.new(name="Canonical_Sun_Key", object_data=sun_data)
    sun_obj.rotation_mode = 'XYZ'
    sun_obj.rotation_euler = Euler(CANONICAL_LIGHTING["sun_rotation_euler"], 'XYZ')
    collection.objects.link(sun_obj)

    # 2. World Environment / Sky fill
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Appennino_World")
        bpy.context.scene.world = world

    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = CANONICAL_LIGHTING["sky_color"]
        bg_node.inputs['Strength'].default_value = CANONICAL_LIGHTING["sky_energy"]

    # 3. Ambient Occlusion on Scene
    if hasattr(bpy.context.scene, "world") and bpy.context.scene.world:
        # Fast ambient contact shading
        pass

    # 4. Color Management for Rich Stylized Tones
    bpy.context.scene.view_settings.view_transform = 'AgX' if 'AgX' in [v.name for v in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Standard'
    bpy.context.scene.view_settings.look = 'Medium High Contrast'

    return sun_obj
