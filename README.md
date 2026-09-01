# Appennino 3D → 2D Procedural Asset Factory

An automated, procedural Blender (`bpy`) pipeline for generating coherent 2D/2.5D RPG assets inspired by Italian/Appennino hill-town architecture.

---

## Repository Structure

```text
d:\Apennino scene\
│
├── README.md                      # Pipeline overview and usage guide
├── experiment_report.md           # In-depth technical evaluation & answers to core questions
│
├── scripts/
│   ├── config.py                  # Canonical locked camera, lighting, scale, and palette constants
│   ├── materials.py               # Procedural stylized shader library (stone, roof, wood, foliage)
│   ├── architecture.py            # Procedural building, roof, door, window, stair, and wall generators
│   ├── props.py                   # Environmental props (fountain, lanterns, barrels, crates, pots)
│   ├── vegetation.py              # Foliage generators (climbing ivy, shrubs, Mediterranean trees)
│   ├── camera.py                  # Camera alignment, framing, and consistency validation
│   ├── lighting.py                # Canonical Mediterranean daylight lighting rig
│   ├── build_scene.py             # Master full-scene assembly & rendering script
│   ├── postprocess.py             # Pixel-art downscale/upscale & painterly contour filter
│   ├── render.py                  # Isolated asset batch renderer & variations showcase
│   └── composite_test.py          # 2D sprite layering and assembly validation script
│
├── output/
│   ├── scene/
│   │   ├── clean.png              # Variant A: Clean stylized Cycles render (1920x1080)
│   │   ├── pixelish.png           # Variant B: Integer upscaled (4x) pixel aesthetic (1920x1080)
│   │   └── painterly.png          # Variant C: Illustrated storybook stylization (1920x1080)
│   │
│   ├── isolated_assets/
│   │   ├── house_A.png            # 2-floor stone house sprite (RGBA)
│   │   ├── house_B.png            # 3-floor narrow townhouse sprite (RGBA)
│   │   ├── house_C.png            # 2-floor wide townhouse sprite (RGBA)
│   │   ├── stairs.png             # Stone staircase sprite (RGBA)
│   │   ├── retaining_wall.png     # Stone retaining wall sprite (RGBA)
│   │   ├── fountain.png           # Tiered stone fountain sprite (RGBA)
│   │   ├── vegetation.png         # Mediterranean tree & shrubs sprite (RGBA)
│   │   └── props.png              # Barrels, crates, lanterns, pots sprite (RGBA)
│   │
│   ├── variations/
│   │   └── houses_together.png    # Side-by-side render of Houses A, B, and C
│   │
│   ├── 2d_composite/
│   │   └── assembled_2d_scene.png # 2D layered composite of independently rendered sprites
│   │
│   └── diagnostics/
│       ├── camera_settings.json   # Canonical camera configuration metadata
│       ├── asset_metadata.json    # Polygon counts, dimensions, and render records
│       └── scale_reference.png    # 1.75m humanoid mannequin scale test
│
└── source/
    └── scene.blend                # Generated Blender scene file
```

---

## Quick Start / Headless Execution

### 1. Build and Render Full Scene (Variants A, B, C)
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python scripts/build_scene.py
& "C:\Users\Acer\AppData\Local\Programs\Python\Python312\python.exe" scripts/postprocess.py
```

### 2. Render Isolated Modular Assets, Variations & Diagnostics
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background --python scripts/render.py
```

### 3. Run 2D Composite Sprite Assembly Test
```powershell
& "C:\Users\Acer\AppData\Local\Programs\Python\Python312\python.exe" scripts/composite_test.py
```

---

## Key Principles

1. **Locked Canonical Camera**: Elevated 3/4 Dimetric View (`Pitch: 56.0°`, `Yaw: 45.0°`, `Type: ORTHO`). Guarantees zero perspective drift across all rendered sprites.
2. **Locked Canonical Lighting**: Warm golden sunlight (`Azimuth: 130°`, `Elevation: 48°`, `Energy: 3.8`) with soft shadow edges and cool cyan sky fill.
3. **World Scale Truth**: `1 Blender Unit = 1.0 meter`. Standard door = 2.1m, floor = 2.8m, stair riser = 0.18m, calibrated with a 1.75m reference mannequin.
4. **Parametric Richness**: Buildings are assembled from semantic architectural components (corner quoins, rafter tails, voussoir arches, shutters at ajar angles, wrought iron balconies, flower boxes).
