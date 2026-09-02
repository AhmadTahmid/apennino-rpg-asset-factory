# Appennino RPG Asset Factory: 3D Procedural vs. 2D AI-Native Experiments

A comparative research repository investigating two contrasting asset-production pipelines for a 2.5D Italian/Appennino hill-town RPG:
1. **Procedural Blender 3D → 2D Asset Factory**: Procedural geometry, locked dimetric camera, locked lighting, and modular sprite generation.
2. **AI-Native 2D-First Asset Factory**: Style anchor conditioning, structural 2D scaffolds, automated alpha defringing, and metric scale normalization.

---

## 🔍 Independent AI & Peer Review Hub

If you are an AI assistant (e.g., ChatGPT) or technical artist reviewing this experiment:
- **Comprehensive Review Page**: [`REVIEW.md`](REVIEW.md) (Embedded visual outputs, exact models, conditioning methods, and composition rules).
- **Machine-Readable Asset Manifest**: [`review_manifest.json`](review_manifest.json) (Direct `raw.githubusercontent.com` URLs for all critical images).
- **Review Visuals Bundle**: [`review_bundle/`](review_bundle/) (Pre-packaged copies of raw baselines, style-anchored assets, scaffolds, composites, and contact sheets).

---

## Master Comparison Contact Sheet

![Master Contact Sheet](review_bundle/contact_sheet.jpg)

---

## Repository Structure

```text
├── REVIEW.md                      # Primary peer-review guide with inline image evidence
├── review_manifest.json           # Machine-readable index with raw GitHub URLs
├── review_bundle/                 # Self-contained review copies & 3 high-res contact sheets
│   ├── contact_sheet.jpg          # Master comparative 8-panel sheet
│   ├── assets_contact_sheet.png   # 8 transparent modular sprites
│   └── scaffolds_contact_sheet.png# Scaffold-to-asset pairs
│
├── appennino-2d-asset-factory/    # AI-Native 2D Pipeline Experiment
│   ├── style/
│   │   ├── style_bible.yaml       # Codified palette, perspective, and architectural rules
│   │   └── anchor_board.png       # Multimodal visual style conditioning anchor
│   ├── scaffolds/                 # Deterministic 2:1 dimetric vector scaffolds & JSON metadata
│   ├── scripts/                   # Normalization, segmentation, and composite builders
│   ├── output/
│   │   ├── raw_baseline/          # Control Group A (prompt-only generation)
│   │   ├── style_anchored/        # Control Group B (style-anchor conditioned)
│   │   ├── normalized/            # BFS alpha-cleaned, scale-normalized transparent sprites
│   │   ├── native_composite.png   # 1920x1080 native 2D assembled scene
│   │   └── hybrid_scene.png       # 2D structured sprites + painterly generative backdrop
│   ├── metadata/                  # Asset dimensions, PPM, and anchor telemetry
│   └── experiment_report.md       # Comprehensive 2D experiment report
│
├── scripts/                       # Procedural Blender 3D Pipeline
│   ├── architecture.py            # Procedural buildings, roofs, quoins, stairs, walls
│   ├── materials.py               # Procedural Cycles shaders (stone, terracotta, wood, foliage)
│   ├── camera.py                  # Canonical locked dimetric camera rig & validator
│   ├── lighting.py                # Canonical Mediterranean sun rig
│   ├── build_scene.py             # Master full-scene assembly & render script
│   ├── render.py                  # Batch isolated transparent sprite renderer
│   ├── postprocess.py             # Pixel-art downscale/upscale & painterly contour filter
│   └── generate_contact_sheets.py # Builds review_bundle contact sheets
│
├── output/                        # Procedural Blender 3D Deliverables
│   ├── scene/                     # Clean, Painterly, and Pixel-ish 1920x1080 renders
│   ├── isolated_assets/           # 8 transparent 3D-rendered modular sprites
│   ├── variations/                # Side-by-side house variations showcase
│   ├── 2d_composite/              # 2D layered sprite composite test
│   └── diagnostics/               # Scale reference mannequin and camera metadata
│
├── workflows/
│   └── prompt_catalog.md          # Exact prompts, models, seeds, and conditioning inputs
└── source/
    └── scene.blend                # Complete reproducible Blender 5.2 scene file
```

---

## Comparative Findings & Verdict

| Metric | Raw 2D AI | Style-Anchored 2D | Constrained 2D Factory | Procedural Blender 3D |
| :--- | :---: | :---: | :---: | :---: |
| **Artistic Attractiveness** | **9.2** | **9.5** | **9.4** | 7.8 (Clean) / 8.5 (Painterly) |
| **Perspective Discipline** | 5.2 | 6.8 | 8.2 | **10.0 (Perfect Dimetric)** |
| **Scale Consistency** | 3.5 (Macro drift) | 5.0 (Macro drift) | 8.5 (Normalized) | **9.8 (Exact Metric PPM)** |
| **Modular Snapping** | 2.5 | 4.0 | 7.0 | **9.5 (Exact Grid Fit)** |
| **Recomposability in 2D** | 4.0 | 6.0 | 7.8 | **9.2** |
| **OVERALL PIPELINE SCORE** | **5.7 / 10** | **7.0 / 10** | **8.4 / 10** | **8.9 / 10** |

### Recommended Production Synthesis
- **Geometry & Scale (Blender)**: Procedural 3D scripts guarantee 100% locked dimetric camera perspective, metric scale truth, and exact collision hulls.
- **Surface Texturing & Detailing (2D AI)**: Style-anchored diffusion models apply rich Italian stone, terracotta, and ivy textures over 3D passes.
- **Backdrops (2D AI)**: 100% pure 2D AI generation for distant mountain ranges and skies.
