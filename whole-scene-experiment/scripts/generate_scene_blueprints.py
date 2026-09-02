"""
Whole-Scene Structural Blueprint & Gameplay Mask Generator.
Reads scene_001.json and produces all 8 deterministic raster blueprint passes at 1920x1080:
1. scene_001_structure.png (Structural wireframe blueprint for image conditioning)
2. walkable_mask.png (White = walkable, Black = non-walkable)
3. collision_mask.png (White = solid obstacles, Black = open space)
4. elevation_map.png (Grayscale elevation levels with stair gradient)
5. stairs_mask.png (White = stair corridor)
6. portal_mask.png (Color-coded scene transition zones)
7. semantic_id_map.png (Color-coded object segmentation map)
8. occlusion_guide.png (White = foreground occluding elements)
"""

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).resolve().parent
EXP_DIR = SCRIPT_DIR.parent
SCENE_JSON = EXP_DIR / "scene/scene_001.json"
BLUEPRINT_DIR = EXP_DIR / "scene/blueprints"
BLUEPRINT_DIR.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(SCRIPT_DIR))
from projection import world_to_screen, CANVAS_WIDTH, CANVAS_HEIGHT


def load_scene():
    with open(SCENE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def create_structure_blueprint(scene):
    """
    Renders scene_001_structure.png: clean architectural line art / layout blocking.
    Establishes building silhouettes, roof pitches, terrace lines, stairs, fountain, tree, and overlook.
    """
    print("--> Generating scene_001_structure.png...")
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=(240, 243, 246))
    draw = ImageDraw.Draw(img)
    
    # 1. Distant Mountain Silhouettes & Sky
    # Far mountain ridge
    m_pts1 = [(0, 160), (320, 120), (680, 150), (1050, 110), (1450, 140), (1920, 115), (1920, 260), (0, 260)]
    draw.polygon(m_pts1, fill=(210, 220, 230), outline=(170, 185, 200), width=2)
    # Mid valley ridge
    m_pts2 = [(0, 240), (450, 190), (920, 220), (1350, 185), (1920, 210), (1920, 340), (0, 340)]
    draw.polygon(m_pts2, fill=(195, 208, 220), outline=(150, 168, 185), width=2)
    
    # Label for Distant Vista
    draw.text((820, 135), "DISTANT APENNINE MOUNTAINS & VALLEY VISTA", fill=(100, 120, 145))
    
    # 2. Upper Terrace Ground Baseline & Retaining Wall
    # Upper terrace floor outline
    p_t_w_top = world_to_screen(7.5, 7.0, 2.8)
    p_t_e_top = world_to_screen(28.5, 7.0, 2.8)
    p_t_w_bot = world_to_screen(7.5, 7.0, 0.0)
    p_t_e_bot = world_to_screen(28.5, 7.0, 0.0)
    
    # Retaining wall face (Z=0.0 to Z=2.8)
    # West wall section
    w_w_top = world_to_screen(7.5, 7.0, 2.8)
    w_e_top = world_to_screen(15.8, 7.0, 2.8)
    w_e_bot = world_to_screen(15.8, 7.0, 0.0)
    w_w_bot = world_to_screen(7.5, 7.0, 0.0)
    draw.polygon([w_w_top, w_e_top, w_e_bot, w_w_bot], fill=(222, 225, 230), outline=(50, 60, 75), width=2)
    draw.text((w_w_top[0] + 40, w_w_top[1] + 35), "STONE RETAINING WALL (Z=2.8m)", fill=(70, 80, 95))
    
    # East wall section
    e_w_top = world_to_screen(18.6, 7.0, 2.8)
    e_e_top = world_to_screen(28.5, 7.0, 2.8)
    e_e_bot = world_to_screen(28.5, 7.0, 0.0)
    e_w_bot = world_to_screen(18.6, 7.0, 0.0)
    draw.polygon([e_w_top, e_e_top, e_e_bot, e_w_bot], fill=(222, 225, 230), outline=(50, 60, 75), width=2)
    
    # 3. Central Staircase
    s_nw = world_to_screen(15.8, 6.8, 2.8)
    s_ne = world_to_screen(18.6, 6.8, 2.8)
    s_se = world_to_screen(18.6, 10.4, 0.0)
    s_sw = world_to_screen(15.8, 10.4, 0.0)
    draw.polygon([s_nw, s_ne, s_se, s_sw], fill=(235, 238, 242), outline=(30, 40, 60), width=3)
    # Draw step treads
    for i in range(1, 14):
        t = i / 14.0
        y_w = 10.4 - t * (10.4 - 6.8)
        z_w = t * 2.8
        p1 = world_to_screen(15.8, y_w, z_w)
        p2 = world_to_screen(18.6, y_w, z_w)
        draw.line([p1, p2], fill=(80, 95, 115), width=2)
    draw.text((s_sw[0] + 15, s_sw[1] - 45), "CENTRAL STAIRCASE (14 STEPS)", fill=(30, 45, 70))
    
    # 4. Lower Piazza Pavement Grid Lines
    for y_m in range(10, 22, 2):
        p_left = world_to_screen(7.5, float(y_m), 0.0)
        p_right = world_to_screen(28.5, float(y_m), 0.0)
        draw.line([p_left, p_right], fill=(225, 228, 232), width=1)
    for x_m in range(8, 29, 2):
        p_top = world_to_screen(float(x_m), 10.0, 0.0)
        p_bot = world_to_screen(float(x_m), 21.0, 0.0)
        draw.line([p_top, p_bot], fill=(225, 228, 232), width=1)
        
    # 5. Buildings
    def draw_building_box(b):
        fp = b["footprint_m"]
        z_base = b["elevation_z_m"]
        wall_h = b["wall_height_m"]
        roof_h = b["roof_height_m"]
        
        # Base ground footprint points
        g_sw = world_to_screen(fp["x_min"], fp["y_max"], z_base)
        g_se = world_to_screen(fp["x_max"], fp["y_max"], z_base)
        g_ne = world_to_screen(fp["x_max"], fp["y_min"], z_base)
        g_nw = world_to_screen(fp["x_min"], fp["y_min"], z_base)
        
        # Wall eave top points
        w_sw = world_to_screen(fp["x_min"], fp["y_max"], z_base + wall_h)
        w_se = world_to_screen(fp["x_max"], fp["y_max"], z_base + wall_h)
        w_ne = world_to_screen(fp["x_max"], fp["y_min"], z_base + wall_h)
        w_nw = world_to_screen(fp["x_min"], fp["y_min"], z_base + wall_h)
        
        # Front wall face
        draw.polygon([g_sw, g_se, w_se, w_sw], fill=(215, 218, 225), outline=(30, 40, 55), width=3)
        # Side wall face (if visible)
        draw.polygon([g_se, g_ne, w_ne, w_se], fill=(195, 200, 210), outline=(30, 40, 55), width=2)
        
        # Roof geometry
        if b.get("roof_type") == "gable":
            ridge_axis = b.get("roof_ridge_axis", "E-W")
            if ridge_axis == "E-W":
                r_mid_w = world_to_screen(fp["x_min"], (fp["y_min"] + fp["y_max"]) / 2, z_base + wall_h + roof_h)
                r_mid_e = world_to_screen(fp["x_max"], (fp["y_min"] + fp["y_max"]) / 2, z_base + wall_h + roof_h)
                # Front slope
                draw.polygon([w_sw, w_se, r_mid_e, r_mid_w], fill=(225, 140, 95), outline=(160, 60, 30), width=3)
                # Gable triangle on west
                draw.polygon([w_nw, w_sw, r_mid_w], fill=(200, 120, 80), outline=(160, 60, 30), width=2)
            else: # N-S
                r_mid_s = world_to_screen((fp["x_min"] + fp["x_max"]) / 2, fp["y_max"], z_base + wall_h + roof_h)
                r_mid_n = world_to_screen((fp["x_min"] + fp["x_max"]) / 2, fp["y_min"], z_base + wall_h + roof_h)
                # East slope
                draw.polygon([w_se, w_ne, r_mid_n, r_mid_s], fill=(225, 140, 95), outline=(160, 60, 30), width=3)
                # South gable triangle
                draw.polygon([w_sw, w_se, r_mid_s], fill=(235, 150, 105), outline=(160, 60, 30), width=2)
        else: # Hip roof
            r_top = world_to_screen((fp["x_min"] + fp["x_max"]) / 2, (fp["y_min"] + fp["y_max"]) / 2, z_base + wall_h + roof_h)
            draw.polygon([w_sw, w_se, r_top], fill=(225, 140, 95), outline=(160, 60, 30), width=3)
            
        # Draw Entrance Door & Windows
        d = b.get("door")
        if d:
            d_p1 = world_to_screen(d["x_m"], d["y_m"], z_base)
            d_p2 = world_to_screen(d["x_m"], d["y_m"], z_base + d["height_m"])
            draw.rectangle([d_p1[0] - 18, d_p2[1], d_p1[0] + 18, d_p1[1]], fill=(120, 75, 45), outline=(40, 25, 15), width=2)
            
        # Label
        draw.text((w_sw[0] + 15, w_sw[1] + 25), f"{b['id'].upper()} ({b['name']})", fill=(20, 25, 35))
        
    for b in scene["buildings"]:
        draw_building_box(b)
        
    # 6. Fountain (Octagonal Basin in Lower Piazza)
    f_info = scene["fountain"]
    fc_x, fc_y = f_info["center_m"]
    r = f_info["radius_m"]
    # Draw 8-sided polygon in screen space
    basin_pts_bottom = []
    basin_pts_top = []
    for i in range(8):
        ang = i * (2 * math.pi / 8)
        bx = fc_x + r * math.cos(ang)
        by = fc_y + r * math.sin(ang) * 0.7  # foreshortened
        basin_pts_bottom.append(world_to_screen(bx, by, 0.0))
        basin_pts_top.append(world_to_screen(bx, by, f_info["basin_height_m"]))
        
    draw.polygon(basin_pts_bottom, fill=(180, 185, 195), outline=(40, 50, 65), width=2)
    draw.polygon(basin_pts_top, fill=(90, 175, 195), outline=(40, 50, 65), width=3)
    # Center Spout
    fc_screen = world_to_screen(fc_x, fc_y, 0.0)
    fc_spout = world_to_screen(fc_x, fc_y, f_info["spout_height_m"])
    draw.line([fc_screen, fc_spout], fill=(60, 75, 95), width=6)
    draw.ellipse([fc_spout[0] - 12, fc_spout[1] - 12, fc_spout[0] + 12, fc_spout[1] + 12], fill=(120, 190, 210), outline=(40, 60, 80), width=2)
    draw.text((fc_screen[0] - 65, fc_screen[1] + 35), "CARVED STONE FOUNTAIN", fill=(30, 45, 65))
    
    # 7. Olive Tree (Southeast overlook terrace)
    t_info = scene["vegetation_regions"][0]
    tc_x, tc_y = t_info["center_m"]
    t_base = world_to_screen(tc_x, tc_y, 0.0)
    t_top = world_to_screen(tc_x, tc_y, t_info["tree_height_m"])
    # Trunk
    draw.line([t_base, (t_top[0], t_top[1] + 80)], fill=(95, 80, 65), width=16)
    # Foliage Canopy
    c_r = t_info["canopy_radius_m"] * 24.0
    c_center = (t_top[0], t_top[1] + 50)
    draw.ellipse([c_center[0] - c_r, c_center[1] - c_r * 0.7, c_center[0] + c_r, c_center[1] + c_r * 0.7], fill=(115, 145, 105), outline=(45, 70, 40), width=3)
    draw.text((t_base[0] - 50, t_base[1] + 20), "MEDITERRANEAN OLIVE TREE", fill=(45, 70, 40))
    
    # 8. Scenic Overlook Balustrade
    ob_pts = []
    for x_m in [22.0, 26.0, 30.0, 34.5]:
        ob_pts.append(world_to_screen(x_m, 22.0, 0.0))
    for i in range(len(ob_pts) - 1):
        p1 = ob_pts[i]
        p2 = ob_pts[i + 1]
        draw.line([p1, p2], fill=(40, 50, 65), width=5)
        # Vertical posts
        draw.line([p1, (p1[0], p1[1] - 38)], fill=(50, 65, 80), width=4)
    p_last = ob_pts[-1]
    draw.line([p_last, (p_last[0], p_last[1] - 38)], fill=(50, 65, 80), width=4)
    draw.text((ob_pts[1][0] - 20, ob_pts[1][1] + 20), "SCENIC VALLEY OVERLOOK", fill=(40, 55, 75))
    
    # Title / Legend Header
    draw.rectangle([30, 30, 680, 110], fill=(255, 255, 255, 230), outline=(50, 60, 75), width=2)
    draw.text((45, 42), "STRUCTURAL BLUEPRINT: SCENE_001 (APPENNINO HILL-TOWN)", fill=(20, 25, 35))
    draw.text((45, 66), "Deterministic 2:1 Dimetric Geometry Pass (36m x 24m World Area)", fill=(100, 110, 125))
    draw.text((45, 86), "Spatial Source of Truth: Buildings, Stairs, Retaining Wall, Fountain, Overlook", fill=(70, 80, 95))
    
    out_path = BLUEPRINT_DIR / "scene_001_structure.png"
    img.save(out_path)
    print(f"--> Saved {out_path.name}")


def create_walkable_and_collision_masks(scene):
    """
    Renders walkable_mask.png and collision_mask.png.
    """
    print("--> Generating walkable_mask.png & collision_mask.png...")
    # Walkable: Black = non-walkable, White = walkable
    walk_img = Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), color=0)
    w_draw = ImageDraw.Draw(walk_img)
    
    # 1. Lower Piazza walkable polygon
    piazza = scene["walkable_regions"][0]["polygon_m"]
    p_screen = [world_to_screen(pt[0], pt[1], 0.0) for pt in piazza]
    w_draw.polygon(p_screen, fill=255)
    
    # 2. Upper Terrace walkable polygon
    terrace = scene["walkable_regions"][1]["polygon_m"]
    t_screen = [world_to_screen(pt[0], pt[1], 2.8) for pt in terrace]
    w_draw.polygon(t_screen, fill=255)
    
    # 3. Stairs corridor
    stairs = scene["walkable_regions"][2]["polygon_m"]
    # stairs slope from Z=0 to Z=2.8
    s_screen = []
    for pt in stairs:
        t = (10.4 - pt[1]) / (10.4 - 6.8)
        z = max(0.0, min(2.8, t * 2.8))
        s_screen.append(world_to_screen(pt[0], pt[1], z))
    w_draw.polygon(s_screen, fill=255)
    
    # Subtract Obstacles from walkable:
    # Fountain basin (radius 1.7m)
    fc_x, fc_y = scene["fountain"]["center_m"]
    r = scene["fountain"]["radius_m"]
    f_pts = [world_to_screen(fc_x + r * math.cos(i * math.pi / 4), fc_y + r * math.sin(i * math.pi / 4) * 0.7, 0.0) for i in range(8)]
    w_draw.polygon(f_pts, fill=0)
    
    # Retaining wall line
    w_draw.polygon([world_to_screen(7.5, 6.7, 0.0), world_to_screen(15.8, 6.7, 0.0), world_to_screen(15.8, 7.3, 0.0), world_to_screen(7.5, 7.3, 0.0)], fill=0)
    w_draw.polygon([world_to_screen(18.6, 6.7, 0.0), world_to_screen(28.5, 6.7, 0.0), world_to_screen(28.5, 7.3, 0.0), world_to_screen(18.6, 7.3, 0.0)], fill=0)
    
    # Overlook balustrade
    w_draw.polygon([world_to_screen(22.0, 21.8, 0.0), world_to_screen(34.5, 21.8, 0.0), world_to_screen(34.5, 22.8, 0.0), world_to_screen(22.0, 22.8, 0.0)], fill=0)
    
    # Olive tree trunk
    tc_x, tc_y = scene["vegetation_regions"][0]["center_m"]
    t_pt = world_to_screen(tc_x, tc_y, 0.0)
    w_draw.ellipse([t_pt[0] - 16, t_pt[1] - 12, t_pt[0] + 16, t_pt[1] + 12], fill=0)
    
    # Market crates props
    cp = scene["props"][0]["footprint_m"]
    c_poly = [world_to_screen(cp["x_min"], cp["y_min"], 0.0), world_to_screen(cp["x_max"], cp["y_min"], 0.0),
              world_to_screen(cp["x_max"], cp["y_max"], 0.0), world_to_screen(cp["x_min"], cp["y_max"], 0.0)]
    w_draw.polygon(c_poly, fill=0)
    
    walk_img.save(BLUEPRINT_DIR / "walkable_mask.png")
    print("--> Saved walkable_mask.png")
    
    # Collision Mask: White = Solid Obstacle, Black = Empty/Traversable
    coll_img = Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), color=0)
    c_draw = ImageDraw.Draw(coll_img)
    
    # Outer bounds
    c_draw.rectangle([0, 0, CANVAS_WIDTH, 260], fill=255) # Top non-walkable backdrop
    
    # Buildings collision polygons
    for b in scene["buildings"]:
        fp = b["footprint_m"]
        z = b["elevation_z_m"]
        b_poly = [world_to_screen(fp["x_min"], fp["y_min"], z), world_to_screen(fp["x_max"], fp["y_min"], z),
                  world_to_screen(fp["x_max"], fp["y_max"], z), world_to_screen(fp["x_min"], fp["y_max"], z)]
        c_draw.polygon(b_poly, fill=255)
        
    # Retaining walls
    c_draw.polygon([world_to_screen(2.0, 6.7, 0.0), world_to_screen(15.8, 6.7, 0.0), world_to_screen(15.8, 7.3, 0.0), world_to_screen(2.0, 7.3, 0.0)], fill=255)
    c_draw.polygon([world_to_screen(18.6, 6.7, 0.0), world_to_screen(35.0, 6.7, 0.0), world_to_screen(35.0, 7.3, 0.0), world_to_screen(18.6, 7.3, 0.0)], fill=255)
    
    # Fountain basin
    c_draw.polygon(f_pts, fill=255)
    # Overlook balustrade
    c_draw.polygon([world_to_screen(22.0, 21.8, 0.0), world_to_screen(34.5, 21.8, 0.0), world_to_screen(34.5, 23.5, 0.0), world_to_screen(22.0, 23.5, 0.0)], fill=255)
    # Tree trunk
    c_draw.ellipse([t_pt[0] - 16, t_pt[1] - 12, t_pt[0] + 16, t_pt[1] + 12], fill=255)
    # Crates
    c_draw.polygon(c_poly, fill=255)
    
    coll_img.save(BLUEPRINT_DIR / "collision_mask.png")
    print("--> Saved collision_mask.png")


def create_elevation_map(scene):
    """
    Renders elevation_map.png:
    0 = Level 0 (Z=0.0m)
    128 = Level 1 (Z=2.8m)
    Gradient 0..128 along stairs.
    """
    print("--> Generating elevation_map.png...")
    elev_img = Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), color=0)
    e_draw = ImageDraw.Draw(elev_img)
    
    # Upper terrace polygon: level 128 (Z=2.8m)
    t_poly = [world_to_screen(pt[0], pt[1], 2.8) for pt in scene["walkable_regions"][1]["polygon_m"]]
    # Also include the ground footprint behind it up to horizon
    t_back = [world_to_screen(7.5, 1.0, 2.8), world_to_screen(28.5, 1.0, 2.8)]
    full_upper = [world_to_screen(7.5, 7.0, 2.8), world_to_screen(28.5, 7.0, 2.8), world_to_screen(28.5, 1.0, 2.8), world_to_screen(7.5, 1.0, 2.8)]
    e_draw.polygon(full_upper, fill=128)
    e_draw.polygon(t_poly, fill=128)
    
    # Stairs continuous vertical gradient 0 -> 128
    for i in range(14):
        t0 = i / 14.0
        t1 = (i + 1) / 14.0
        val = int(t0 * 128)
        y0 = 10.4 - t0 * (10.4 - 6.8)
        y1 = 10.4 - t1 * (10.4 - 6.8)
        z0 = t0 * 2.8
        z1 = t1 * 2.8
        step_pts = [
            world_to_screen(15.8, y0, z0),
            world_to_screen(18.6, y0, z0),
            world_to_screen(18.6, y1, z1),
            world_to_screen(15.8, y1, z1),
        ]
        e_draw.polygon(step_pts, fill=val)
        
    elev_img.save(BLUEPRINT_DIR / "elevation_map.png")
    print("--> Saved elevation_map.png")


def create_stairs_portal_and_semantic_masks(scene):
    """
    Renders stairs_mask.png, portal_mask.png, semantic_id_map.png, and occlusion_guide.png.
    """
    print("--> Generating stairs_mask, portal_mask, semantic_id_map, and occlusion_guide...")
    # 1. Stairs Mask
    stairs_img = Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), color=0)
    s_draw = ImageDraw.Draw(stairs_img)
    s_poly = []
    for pt in scene["walkable_regions"][2]["polygon_m"]:
        t = (10.4 - pt[1]) / (10.4 - 6.8)
        z = max(0.0, min(2.8, t * 2.8))
        s_poly.append(world_to_screen(pt[0], pt[1], z))
    s_draw.polygon(s_poly, fill=255)
    stairs_img.save(BLUEPRINT_DIR / "stairs_mask.png")
    print("--> Saved stairs_mask.png")
    
    # 2. Portal Mask (RGB color coded)
    portal_img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=(0, 0, 0))
    p_draw = ImageDraw.Draw(portal_img)
    # South Lane Exit: Blue (0, 120, 255)
    p_south = [world_to_screen(pt[0], pt[1], 0.0) for pt in scene["portals"][0]["trigger_polygon_m"]]
    p_draw.polygon(p_south, fill=(0, 120, 255))
    # East Street Exit: Green (0, 220, 100)
    p_east = [world_to_screen(pt[0], pt[1], 0.0) for pt in scene["portals"][1]["trigger_polygon_m"]]
    p_draw.polygon(p_east, fill=(0, 220, 100))
    portal_img.save(BLUEPRINT_DIR / "portal_mask.png")
    print("--> Saved portal_mask.png")
    
    # 3. Semantic ID Map
    # Unique RGB per object type
    sem_img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), color=(30, 40, 60)) # Sky/Vista
    sem_draw = ImageDraw.Draw(sem_img)
    
    # Ground: (140, 130, 120)
    sem_draw.polygon([world_to_screen(pt[0], pt[1], 0.0) for pt in scene["walkable_regions"][0]["polygon_m"]], fill=(140, 130, 120))
    sem_draw.polygon([world_to_screen(pt[0], pt[1], 2.8) for pt in scene["walkable_regions"][1]["polygon_m"]], fill=(160, 150, 140))
    # Stairs: (180, 170, 160)
    sem_draw.polygon(s_poly, fill=(180, 170, 160))
    
    # Buildings:
    # House A: (220, 50, 50)
    bA = scene["buildings"][0]
    fpA = bA["footprint_m"]
    polyA = [world_to_screen(fpA["x_min"], fpA["y_max"], 0.0), world_to_screen(fpA["x_max"], fpA["y_max"], 0.0),
             world_to_screen(fpA["x_max"], fpA["y_min"], bA["wall_height_m"] + bA["roof_height_m"]),
             world_to_screen(fpA["x_min"], fpA["y_min"], bA["wall_height_m"] + bA["roof_height_m"])]
    sem_draw.polygon(polyA, fill=(220, 50, 50))
    
    # House B: (50, 120, 220)
    bB = scene["buildings"][1]
    fpB = bB["footprint_m"]
    polyB = [world_to_screen(fpB["x_min"], fpB["y_max"], 2.8), world_to_screen(fpB["x_max"], fpB["y_max"], 2.8),
             world_to_screen(fpB["x_max"], fpB["y_min"], 2.8 + bB["wall_height_m"] + bB["roof_height_m"]),
             world_to_screen(fpB["x_min"], fpB["y_min"], 2.8 + bB["wall_height_m"] + bB["roof_height_m"])]
    sem_draw.polygon(polyB, fill=(50, 120, 220))
    
    # House C: (50, 200, 100)
    bC = scene["buildings"][2]
    fpC = bC["footprint_m"]
    polyC = [world_to_screen(fpC["x_min"], fpC["y_max"], 2.8), world_to_screen(fpC["x_max"], fpC["y_max"], 2.8),
             world_to_screen(fpC["x_max"], fpC["y_min"], 2.8 + bC["wall_height_m"] + bC["roof_height_m"]),
             world_to_screen(fpC["x_min"], fpC["y_min"], 2.8 + bC["wall_height_m"] + bC["roof_height_m"])]
    sem_draw.polygon(polyC, fill=(50, 200, 100))
    
    # Shop: (220, 160, 40)
    bS = scene["buildings"][3]
    fpS = bS["footprint_m"]
    polyS = [world_to_screen(fpS["x_min"], fpS["y_max"], 0.0), world_to_screen(fpS["x_max"], fpS["y_max"], 0.0),
             world_to_screen(fpS["x_max"], fpS["y_min"], bS["wall_height_m"] + bS["roof_height_m"]),
             world_to_screen(fpS["x_min"], fpS["y_min"], bS["wall_height_m"] + bS["roof_height_m"])]
    sem_draw.polygon(polyS, fill=(220, 160, 40))
    
    # Fountain: (0, 220, 240)
    fc_x, fc_y = scene["fountain"]["center_m"]
    r = scene["fountain"]["radius_m"]
    f_pts = [world_to_screen(fc_x + r * math.cos(i * math.pi / 4), fc_y + r * math.sin(i * math.pi / 4) * 0.7, 0.0) for i in range(8)]
    sem_draw.polygon(f_pts, fill=(0, 220, 240))
    
    # Olive Tree: (80, 140, 50)
    tc_x, tc_y = scene["vegetation_regions"][0]["center_m"]
    t_top = world_to_screen(tc_x, tc_y, 6.8)
    c_r = scene["vegetation_regions"][0]["canopy_radius_m"] * 24.0
    c_center = (t_top[0], t_top[1] + 50)
    sem_draw.ellipse([c_center[0] - c_r, c_center[1] - c_r * 0.7, c_center[0] + c_r, c_center[1] + c_r * 0.7], fill=(80, 140, 50))
    
    sem_img.save(BLUEPRINT_DIR / "semantic_id_map.png")
    print("--> Saved semantic_id_map.png")
    
    # 4. Occlusion Guide (White = Foreground Occluders that cover the player)
    occ_img = Image.new("L", (CANVAS_WIDTH, CANVAS_HEIGHT), color=0)
    o_draw = ImageDraw.Draw(occ_img)
    
    # Roofs:
    # House A roof
    w_sw = world_to_screen(fpA["x_min"], fpA["y_max"], bA["wall_height_m"])
    w_se = world_to_screen(fpA["x_max"], fpA["y_max"], bA["wall_height_m"])
    r_mid = world_to_screen((fpA["x_min"] + fpA["x_max"]) / 2, fpA["y_max"], bA["wall_height_m"] + bA["roof_height_m"])
    r_top = world_to_screen((fpA["x_min"] + fpA["x_max"]) / 2, fpA["y_min"], bA["wall_height_m"] + bA["roof_height_m"])
    o_draw.polygon([w_sw, w_se, r_mid, r_top, (w_sw[0], r_top[1])], fill=255)
    
    # House B roof
    w_sw_B = world_to_screen(fpB["x_min"], fpB["y_max"], 2.8 + bB["wall_height_m"])
    w_se_B = world_to_screen(fpB["x_max"], fpB["y_max"], 2.8 + bB["wall_height_m"])
    r_top_B = world_to_screen(fpB["x_max"], fpB["y_min"], 2.8 + bB["wall_height_m"] + bB["roof_height_m"])
    o_draw.polygon([w_sw_B, w_se_B, r_top_B, (w_sw_B[0], r_top_B[1])], fill=255)
    
    # House C roof
    w_sw_C = world_to_screen(fpC["x_min"], fpC["y_max"], 2.8 + bC["wall_height_m"])
    w_se_C = world_to_screen(fpC["x_max"], fpC["y_max"], 2.8 + bC["wall_height_m"])
    r_top_C = world_to_screen(fpC["x_max"], fpC["y_min"], 2.8 + bC["wall_height_m"] + bC["roof_height_m"])
    o_draw.polygon([w_sw_C, w_se_C, r_top_C, (w_sw_C[0], r_top_C[1])], fill=255)
    
    # Shop roof & awning
    w_sw_S = world_to_screen(fpS["x_min"], fpS["y_max"], bS["wall_height_m"])
    w_se_S = world_to_screen(fpS["x_max"], fpS["y_max"], bS["wall_height_m"])
    r_top_S = world_to_screen((fpS["x_min"] + fpS["x_max"]) / 2, fpS["y_min"], bS["wall_height_m"] + bS["roof_height_m"])
    o_draw.polygon([w_sw_S, w_se_S, r_top_S, (w_sw_S[0], r_top_S[1])], fill=255)
    
    # Olive Tree Canopy (overhead canopy occludes player walking under it)
    o_draw.ellipse([c_center[0] - c_r, c_center[1] - c_r * 0.7, c_center[0] + c_r, c_center[1] + c_r * 0.7], fill=255)
    
    occ_img.save(BLUEPRINT_DIR / "occlusion_guide.png")
    print("--> Saved occlusion_guide.png")


if __name__ == "__main__":
    scene_data = load_scene()
    create_structure_blueprint(scene_data)
    create_walkable_and_collision_masks(scene_data)
    create_elevation_map(scene_data)
    create_stairs_portal_and_semantic_masks(scene_data)
    print("--> All 8 deterministic blueprint passes generated successfully!")
