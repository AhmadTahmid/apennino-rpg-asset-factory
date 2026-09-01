"""
Procedural Stylized Shader Material Library for Blender.
Rich Italian/Appennino stone masonry, terracotta roofs, aged wood,
olive shutters, cobblestone, water, wrought iron, and lush foliage.
"""

import bpy
from .config import PALETTE


def get_or_create_material(name, create_fn):
    """Utility to retrieve an existing material or generate it if absent."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    create_fn(mat, mat.node_tree)
    return mat


def setup_limestone_wall_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (700, 0)

        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (400, 0)
        bsdf.inputs['Roughness'].default_value = 0.86

        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-800, 0)

        # Voronoi for stone block courses
        v_blocks = nodes.new(type='ShaderNodeTexVoronoi')
        v_blocks.location = (-550, 150)
        v_blocks.feature = 'DISTANCE_TO_EDGE'
        v_blocks.inputs['Scale'].default_value = 3.6
        v_blocks.inputs['Randomness'].default_value = 0.85

        # Noise for plaster / stone grain
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-550, -150)
        noise.inputs['Scale'].default_value = 12.0
        noise.inputs['Detail'].default_value = 2.0

        # Ramp for Stone Mortar & Surface (Warm sandy ochre to weathered limestone)
        ramp_stone = nodes.new(type='ShaderNodeValToRGB')
        ramp_stone.location = (-250, 150)
        ramp_stone.color_ramp.elements[0].position = 0.05
        ramp_stone.color_ramp.elements[0].color = (0.52, 0.47, 0.40, 1.0)  # Mortar
        ramp_stone.color_ramp.elements[1].position = 0.22
        ramp_stone.color_ramp.elements[1].color = (0.86, 0.80, 0.70, 1.0)  # Warm limestone

        # Subtle noise blend
        mix_plaster = nodes.new(type='ShaderNodeMix')
        mix_plaster.data_type = 'RGBA'
        mix_plaster.blend_type = 'MULTIPLY'
        mix_plaster.inputs['Factor'].default_value = 0.20
        mix_plaster.location = (50, 100)

        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (150, -150)
        bump.inputs['Strength'].default_value = 0.24
        bump.inputs['Distance'].default_value = 0.06

        links.new(tex_coord.outputs['Object'], v_blocks.inputs['Vector'])
        links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

        links.new(v_blocks.outputs['Distance'], ramp_stone.inputs['Fac'])
        links.new(ramp_stone.outputs['Color'], mix_plaster.inputs[6])
        links.new(noise.outputs['Color'], mix_plaster.inputs[7])
        links.new(mix_plaster.outputs[2], bsdf.inputs['Base Color'])

        links.new(v_blocks.outputs['Distance'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Limestone_Wall", build)


def setup_terracotta_roof_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (700, 0)

        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (400, 0)
        bsdf.inputs['Roughness'].default_value = 0.80

        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-750, 0)

        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-550, 0)

        wave = nodes.new(type='ShaderNodeTexWave')
        wave.location = (-300, 150)
        wave.wave_type = 'BANDS'
        wave.bands_direction = 'X'
        wave.inputs['Scale'].default_value = 6.0
        wave.inputs['Distortion'].default_value = 0.5
        wave.inputs['Detail'].default_value = 2.0

        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-300, -150)
        noise.inputs['Scale'].default_value = 14.0

        ramp = nodes.new(type='ShaderNodeValToRGB')
        ramp.location = (-50, 150)
        ramp.color_ramp.elements[0].position = 0.12
        ramp.color_ramp.elements[0].color = (0.58, 0.20, 0.08, 1.0)  # Shadow groove
        ramp.color_ramp.elements[1].position = 0.85
        ramp.color_ramp.elements[1].color = (0.84, 0.38, 0.16, 1.0)  # Sunlit terracotta

        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (180, -150)
        bump.inputs['Strength'].default_value = 0.42
        bump.inputs['Distance'].default_value = 0.10

        links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
        links.new(wave.outputs['Color'], ramp.inputs['Fac'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(wave.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Terracotta_Roof", build)


def setup_aged_wood_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.30, 0.20, 0.12, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.75
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Aged_Wood", build)


def setup_shutter_material(variant="green"):
    name = f"Mat_Painted_Shutter_{variant.capitalize()}"
    base_col = (0.28, 0.42, 0.24, 1.0) if variant == "green" else (0.36, 0.22, 0.14, 1.0)

    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = base_col
        bsdf.inputs['Roughness'].default_value = 0.65
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material(name, build)


def setup_cobblestone_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links

        output = nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (600, 0)

        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (300, 0)
        bsdf.inputs['Roughness'].default_value = 0.88

        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-700, 0)

        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.location = (-450, 100)
        voronoi.feature = 'DISTANCE_TO_EDGE'
        voronoi.inputs['Scale'].default_value = 3.2
        voronoi.inputs['Randomness'].default_value = 0.88

        ramp = nodes.new(type='ShaderNodeValToRGB')
        ramp.location = (-180, 100)
        ramp.color_ramp.elements[0].position = 0.06
        ramp.color_ramp.elements[0].color = (0.42, 0.38, 0.32, 1.0)  # Mortar
        ramp.color_ramp.elements[1].position = 0.28
        ramp.color_ramp.elements[1].color = (0.76, 0.72, 0.64, 1.0)  # Paving stone

        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (50, -100)
        bump.inputs['Strength'].default_value = 0.35
        bump.inputs['Distance'].default_value = 0.10

        links.new(tex_coord.outputs['Object'], voronoi.inputs['Vector'])
        links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
        links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
        links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Cobblestone", build)


def setup_fountain_stone_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.78, 0.74, 0.66, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.78
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Fountain_Stone", build)


def setup_water_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.24, 0.58, 0.64, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['Transmission Weight'].default_value = 0.85
        bsdf.inputs['IOR'].default_value = 1.333
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Water", build)


def setup_foliage_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.24, 0.48, 0.18, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.55
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Foliage_Ivy", build)


def setup_flower_material(color_name="red"):
    name = f"Mat_Flower_{color_name.capitalize()}"
    col = (0.88, 0.15, 0.14, 1.0) if color_name == "red" else (0.92, 0.40, 0.55, 1.0)

    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = col
        bsdf.inputs['Roughness'].default_value = 0.45
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material(name, build)


def setup_wrought_iron_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.16, 0.16, 0.16, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.40
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Wrought_Iron", build)


def setup_terracotta_pot_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.75, 0.38, 0.20, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.82
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Terracotta_Pot", build)


def setup_glass_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.12, 0.18, 0.24, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.10
        bsdf.inputs['Metallic'].default_value = 0.25
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Glass", build)


def setup_lantern_glow_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        emission = nodes.new(type='ShaderNodeEmission')
        emission.inputs['Color'].default_value = (1.0, 0.84, 0.48, 1.0)
        emission.inputs['Strength'].default_value = 5.0
        links.new(emission.outputs['Emission'], output.inputs['Surface'])

    return get_or_create_material("Mat_Lantern_Glow", build)


def setup_mountain_backdrop_material():
    def build(mat, tree):
        nodes = tree.nodes
        links = tree.links
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.42, 0.56, 0.52, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.95
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return get_or_create_material("Mat_Mountain_Backdrop", build)


def initialize_all_materials():
    return {
        "limestone": setup_limestone_wall_material(),
        "roof": setup_terracotta_roof_material(),
        "wood": setup_aged_wood_material(),
        "shutter_green": setup_shutter_material("green"),
        "shutter_brown": setup_shutter_material("brown"),
        "cobblestone": setup_cobblestone_material(),
        "fountain": setup_fountain_stone_material(),
        "water": setup_water_material(),
        "foliage": setup_foliage_material(),
        "flower_red": setup_flower_material("red"),
        "flower_pink": setup_flower_material("pink"),
        "iron": setup_wrought_iron_material(),
        "pot": setup_terracotta_pot_material(),
        "glass": setup_glass_material(),
        "lantern_glow": setup_lantern_glow_material(),
        "mountain": setup_mountain_backdrop_material(),
    }
