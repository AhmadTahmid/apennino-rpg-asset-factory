# Prompt and Workflow Catalog: Appennino RPG Asset Factory

This catalog documents the exact generative AI prompts, model identifiers, conditioning images, and programmatic post-processing steps used across the experiment.

---

## 1. Generative AI Model & Infrastructure

- **Image Generation Model**: `gemini-3.1-flash-image` (Google Antigravity Tooling)
- **Base Resolution**: 1024 × 1024 native square canvas
- **Sampling / Guidance**: Deterministic high-adherence multimodal conditioning
- **Conditioning Mechanism**: Multimodal reference conditioning (`ImagePaths: [anchor_board.png, reference_frame.jpg]`)
- **3D Procedural Engine**: Blender 5.2.1 LTS (`bpy` Cycles render engine, 64 samples, OIDN denoising)

---

## 2. Exact Prompts Registry

### Raw Baseline (Control Group A)
*No structural scaffolds; prompt-only + video reference frame conditioning.*

| Asset | Exact Text Prompt |
| :--- | :--- |
| **House A** | `Isolated 2.5D RPG game asset sprite of a traditional Italian Appennino hill-town stone house. Two storeys tall, gable roof with aged terracotta barrel tiles, rough limestone masonry walls with mortar joints, wooden front door with a round stone arch, rectangular windows with olive-green wooden shutters, windowsill flower boxes with blooming red geraniums. Plain neutral white background, cast shadow to the bottom-right, warm morning sunlight from top-left, clean painterly RPG asset illustration.` |
| **House B** | `Isolated 2.5D RPG game asset sprite of an Italian Appennino narrow stone townhouse tower. Three storeys tall, narrow vertical proportion, stone chimney on roof, dark brown wooden shutters, arched wooden entrance door on ground floor, rough weathered limestone texture, small terracotta roof overhang. Plain neutral white background, cast shadow to bottom-right, warm morning sun from top-left, clean painterly RPG sprite.` |
| **House C** | `Isolated 2.5D RPG game asset sprite of an Italian Appennino wide stone shop building. Two storeys, wide frontage, hip roof with terracotta tiles, wide arched wooden double door on ground floor, upper windows with green shutters and red flower boxes, textured rustic stone masonry. Plain neutral white background, cast shadow to bottom-right, warm morning sunlight from top-left, clean painterly RPG asset illustration.` |
| **Stairs** | `Isolated 2.5D RPG game asset sprite of old Italian Appennino stone stairs and retaining wall. Weathered stone steps climbing up from bottom-left to top-right along a rough limestone retaining wall with coping stones, climbing ivy on the stone wall, potted terracotta flower pot with red geraniums at the base. Plain neutral white background, cast shadow to bottom-right, warm morning sunlight, clean painterly RPG asset illustration.` |
| **Retaining Wall** | `Isolated 2.5D RPG game sprite of an ancient Italian Appennino stone retaining terrace wall, weathered grey and warm beige limestone masonry, flat stone coping caps on top edge, wild green ivy growing across the stones, isolated on white background, sharp clean edges, warm directional lighting.` |
| **Fountain** | `Isolated 2.5D RPG game asset sprite of an Italian village piazza carved stone fountain. Octagonal stone basin filled with clear blue sparkling water, center carved stone pedestal column with splashing water fountain spout, isolated on plain white background, warm sunlight, cozy painterly JRPG aesthetic.` |
| **Vegetation** | `Isolated 2.5D RPG game asset sprite of Mediterranean vegetation. A stylized olive tree with gnarled trunk and soft green canopy, cluster of terracotta pots with flowering red geraniums, garden shrub, isolated on plain white background, warm sunlight, clean painterly RPG sprite.` |
| **Props** | `Isolated 2.5D RPG game asset sprite of old Italian village street props. Two rustic oak barrels with iron hoops, stacked wooden vegetable market crates with apples and greens, wrought-iron wall lantern, isolated on plain white background, warm sunlight, cozy painterly RPG sprite.` |

---

### Style-Anchored Generation (Control Group B)
*Conditioned explicitly on `style/anchor_board.png`.*

| Asset | Exact Text Prompt |
| :--- | :--- |
| **House A** | `Isolated 2.5D RPG game asset sprite of an Italian Appennino stone house, strictly matching the style anchor board's color palette, limestone masonry texture, and terracotta tile color. Two storeys, gable roof, arched wooden entrance door on ground floor, upper window with olive-green shutters, flower box with blooming red geraniums, isolated on white background, consistent warm lighting from top-left.` |
| **House B** | `Isolated 2.5D RPG game asset sprite of an Italian Appennino narrow stone tower townhouse, strictly matching the style anchor board. Three storeys tall, narrow vertical structure, stone chimney, walnut brown wooden shutters, arched wooden door on ground floor, isolated on white background, consistent warm lighting from top-left, cozy JRPG illustrated game sprite.` |
| **House C** | `Isolated 2.5D RPG game asset sprite of an Italian Appennino wide stone shop townhouse, strictly matching the style anchor board. Two storeys, wide frontage, hip roof with terracotta tiles, wide arched wooden double door on ground floor, upper windows with olive shutters and flower boxes with red geraniums, isolated on white background, consistent warm lighting from top-left, cozy JRPG illustrated game sprite.` |

---

## 3. Deterministic Post-Processing & Normalization Logic

1. **Background Removal**:
   - Algorithm: Perimeter Breadth-First Search (BFS) flood-fill starting from all perimeter border pixels where color values `R, G, B >= 238`.
   - Alpha Feathering: `diff = 255 - min(R, G, B); alpha = min(alpha, diff * 6.0)`.
   - Soft Contact Shadow Preservation: Preserves ground contact shadow without bleeding solid white backing into the sprite boundary.
2. **Semantic Anchor Normalization**:
   - Canonical Door Target: Standard 2.10m height corresponds to exactly **202 pixels** at 96 PPM.
   - Rescaling Rule: If an asset has a detected door of height $H_{detected}$, uniform resize factor is $S = 202 / H_{detected}$.
   - Canvas Alignment: The scaled asset is placed onto a 1024 × 1024 transparent canvas such that its ground contact point aligns precisely with canonical ground anchor **(X = 512, Y = 900)**.
3. **Zero Manual Repainting**:
   - 100% of background extraction, scaling, and canvas anchoring was performed automatically by `scripts/normalize_assets.py`. Zero human brush strokes or Photoshop retouches were applied.
