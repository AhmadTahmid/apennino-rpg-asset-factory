# Experiment C — Results

## Outcome

**The aesthetic hypothesis passed; the geometry-preservation hypothesis did
not. Experiment C stops at the locked structural gate, before decomposition or
Godot integration.**

OpenAI image generation produced four untouched, provenance-verified images.
The two style-only controls were the blind aesthetic winners. The two
structure-conditioned images retained the source's coarse topology, but moved
spatially critical geometry far enough to invalidate reuse of the source's
collision, elevation, navigation, and occlusion masks.

This is a valid stopping condition, not a reason to loosen the gate after
seeing the outputs.

## Run integrity

- Structural and style inputs matched their locked SHA-256 hashes.
- All four candidate hashes and original dimensions matched provenance.
- Each candidate came from one independent OpenAI image-generation call.
- No candidate was filtered or otherwise post-processed.
- The image tool exposed no model version, seed, request ID, or settings; these
  values remain `null` rather than being invented.
- Gemini was cancelled by the user before any output was accepted. It
  contributed zero candidates and is excluded from all findings.
- The first OpenAI structured image began as a calibration and was promoted
  unchanged into the matrix after the generator switch. Its original copy and
  provenance were retained for auditability.

Exact prompts, input paths, timestamps, hashes, dimensions, and generated
source paths are recorded in `outputs/provenance.json`.

## Blind reveal

| Blind label | Identity after reveal | Condition | Visual rank | Strict structural gate |
| --- | --- | --- | --- | --- |
| C | `control_01.png` | Style only | 1st | Fail as expected: new composition |
| A | `control_02.png` | Style only | 2nd | Fail as expected: new composition |
| D | `structure_01.png` | Style + scaffold | 3rd | Fail, but closest |
| B | `structure_02.png` | Style + scaffold | 4th | Fail |

The visual reviewer ranked `C > A > D > B` without knowing the conditions. The
structural reviewer independently failed all four without knowing their
identities.

## What the images establish

### Validated

1. **Whole-scene neural synthesis can clear the prior aesthetic failure.** Both
   controls are coherent, attractive, single-camera Appennino scenes rather
   than collages or isolated assets.
2. **The target visual language is reachable.** Warm limestone, terracotta,
   vegetation, lived-in detail, atmospheric mountains, and JRPG readability
   remain consistent across a full frame.
3. **Structural conditioning has a real effect.** The structured pair is not a
   generic village: both recover the source's three foreground roof masses,
   upper path band, fountain/alley area, and broad topology.
4. **There is a current quality/control tradeoff.** The style-only controls
   ranked first and second aesthetically; the conditioned images ranked third
   and fourth and showed weaker circulation logic.

### Not validated

1. **Mask-stable repainting.** The closest candidate, `structure_01.png`, moved
   the fountain about 72 px left at the 1920×1080 evaluation size and shifted
   important eaves and path boundaries by tens of pixels.
2. **Reuse of deterministic gameplay geometry.** Collision, navigation,
   elevation, and occlusion derived from the Blender source would visibly
   disagree with either structured image.
3. **Decomposition, Godot integration, or playability.** These were downstream
   stages and were intentionally not run after the geometry gate failed.
4. **Production consistency across nodes.** One scene matrix cannot establish
   cross-scene continuity, reusable assets, or repeatable camera control.

## Structural findings

`structure_01.png` (blind D) is the closest preservation result. Its fountain
is displaced approximately 72 evaluation pixels to the left; the central/left
eaves, façade widths, and path boundaries also drift. Corridors remain broadly
legible, but the output is a close reinterpretation rather than an edge-locked
repaint.

`structure_02.png` (blind B) preserves the same coarse scene bands, but its
fountain moves approximately 112 evaluation pixels left and several building
envelopes diverge more strongly.

The controls' errors are much larger because they were not given the scaffold:
their strong images prove aesthetic capability, not preservation.

## Relationship to the macro objective

The macro objective is not simply to generate attractive Italian-village art;
it is to synthesize beautiful **playable** 2D/2.5D Appennino RPG worlds with
repeatable spatial truth.

Experiment C makes real progress on the first half. It replaces the old false
whole-scene evidence with genuine neural outputs and demonstrates that the
desired authored look is attainable at scene scale. It does not yet join that
art to deterministic gameplay geometry. Therefore whole-frame neural repaint
is not production-safe as a geometry-replacement stage.

The result narrows the architecture choice:

- neural generation is viable for concept scenes, backdrops, texture/detail
  synthesis, and art-first exploration;
- geometry-critical foreground boundaries should remain deterministic unless
  a tighter controlled edit passes explicit spatial tolerances;
- alternatively, an art-first branch must derive new gameplay masks from the
  generated image instead of pretending the old masks still fit.

## Next smallest experiment

Run a separate, pre-registered geometry-control experiment with two branches:

1. **Tighter geometry-first edit:** add explicit edge/depth/semantic guides and
   use the lowest available edit/denoise strength. Require critical landmark
   displacement ≤12 px at 1920×1080, contour error ≤16 px median / ≤32 px max,
   corridor-mask IoU ≥0.95, and unchanged corridor connectivity.
2. **Art-first extraction:** take the visual winner `control_01.png`, derive a
   new walkable mask and occlusion layers from that image, and test one small
   player route. This tests whether generated art can become playable without
   inheriting incompatible Blender geometry.

The geometry-first branch should remain first because it preserves a reusable
world model. If the available generator cannot expose sufficiently strong
control, the hybrid geometry-native foreground/neural-detail architecture is
the more honest production direction.

## Decision

Do not spend time on Experiment C decomposition or Godot integration. Preserve
`control_01.png` as the current aesthetic reference and `structure_01.png` as
the current topology-preservation reference. Begin the next experiment only
with a new manifest and explicit numeric spatial gates.
