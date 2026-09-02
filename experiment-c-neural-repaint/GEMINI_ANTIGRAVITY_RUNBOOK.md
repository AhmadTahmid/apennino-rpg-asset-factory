# CANCELLED — Gemini/Antigravity generation runbook

**Do not execute this runbook.** The user cancelled Gemini participation before
any candidate was accepted. It is retained only to document the abandoned plan
and prevent accidental claims that Gemini contributed to Experiment C.

Gemini is a bounded image-generation worker for this run. Do not ask it to
write code, repair the old experiment, create reports, choose a winner, or
grade the images.

## Shared scene brief

Create a complete 16:9 illustrated RPG environment: a dense, inhabited Italian
Appennino hill-town node viewed from one coherent elevated three-quarter game
camera. Use warm aged limestone, terracotta barrel roofs, olive shutters,
geraniums and ivy, connected cobbled lanes, stairs and retaining walls, a
central stone fountain, readable player-scale circulation, and distant
blue-green valley and mountain atmosphere. The result must read as one authored
place rather than a collection of isolated assets. Use consistent morning light
from upper left, consistent contact shadows, and one unified pixel-painterly
JRPG rendering language. No text, labels, UI, borders, white background, or
asset-sheet layout.

## Control generation prompt

Attach only these images:

1. `../appennino-2d-asset-factory/style/anchor_board.png`
2. `../reference_frames/frame_001.jpg`
3. `../reference_frames/frame_003.jpg`

Use this prompt twice, producing two independent original outputs:

> Generate one complete 16:9 game scene using the attached images only as
> aesthetic and world-language references. Follow the shared scene brief
> exactly. Compose a single coherent playable hill-town node with connected
> paths and stairs. Do not make an asset sheet or isolated object collage.
> Return the untouched original image without annotations or evaluation.

Save the outputs as:

- `outputs/originals/control_01.png`
- `outputs/originals/control_02.png`

## Structure-conditioned generation prompt

Attach these images in this explicit role order:

1. **STRUCTURE TO PRESERVE:** `../output/scene/clean.png`
2. **STYLE BOARD:** `../appennino-2d-asset-factory/style/anchor_board.png`
3. **AESTHETIC REFERENCE 1:** `../reference_frames/frame_001.jpg`
4. **AESTHETIC REFERENCE 2:** `../reference_frames/frame_003.jpg`

Use this prompt twice, producing two independent original outputs:

> Neural repaint/edit task. The first attached image is the spatial source of
> truth. Repaint the entire frame into the Appennino pixel-painterly JRPG style
> shown by the other references. Preserve the first image's exact 16:9 camera,
> major building footprints and silhouettes, three large foreground roof
> masses, fountain center, stairs, retaining walls, path junctions, arched
> alley, and open walkable corridors. Do not crop, rotate, mirror, zoom, move,
> delete, or add major architecture. You may enrich surfaces with coherent
> limestone, terracotta tiles, shutters, flowers, ivy, small props, people, and
> atmospheric mountains only where they do not change gameplay geometry.
> Replace the crude procedural look with one unified authored scene; do not
> return an asset collage. Return only the untouched original generated image,
> with no annotations, scores, claims, or post-processing.

Save the outputs as:

- `outputs/originals/structure_01.png`
- `outputs/originals/structure_02.png`

## Required provenance

Copy `outputs/provenance.template.json` to `outputs/provenance.json` and record
only values actually exposed by Antigravity:

- exact model/model version shown;
- generation timestamp with timezone;
- candidate filename;
- all attached input paths;
- the exact prompt used;
- seed, job/request ID, and settings if exposed;
- original output dimensions.

Use `null` for settings Antigravity does not expose. Never invent them.
