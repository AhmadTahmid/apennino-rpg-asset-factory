# Experiment C — Controlled Neural Whole-Scene Repaint

## Decision under test

Can a real neural image model repaint one spatially coherent RPG scene into the
desired Appennino visual language while preserving the geometry needed for
gameplay?

This experiment intentionally does **not** test Godot integration,
decomposition, cross-node continuity, or a general scene compiler. Those stages
remain gated on a successful image result.

## Why this experiment exists

The earlier whole-scene experiment did not test this question. Its first
candidate was an almost blank Blender render, its other candidates were Pillow
filters of that render, and its scores were hard-coded. The old experiment is
preserved unchanged as evidence.

The structural source for Experiment C is `../output/scene/clean.png`. It is not
beautiful enough to ship, but it contains one coherent camera, connected ground
planes, buildings, roofs, paths, a fountain, and occlusion relationships. The
flat `scene_001_structure.png` diagram is excluded because it is not a true
dimetric scene and is incompatible with the Blender camera.

## Roles

- **Codex:** owns the complete experimental loop: locks the inputs and prompts,
  invokes OpenAI image generation, preserves untouched outputs and provenance,
  runs the preflight and diagnostics, anonymizes candidates, coordinates
  independent audits, and records the final structural/methodological verdict.
- **OpenAI built-in image generation:** produces images only. It does not
  change the experiment, select a winner, or assign scores.
- **User:** may add blind aesthetic judgment or playtest feedback, but neither
  is required for Codex to finish the experiment to its honest stop condition.

## Candidate matrix

| Candidate | Inputs | Purpose |
| --- | --- | --- |
| `control_01.png` | style board + two reference frames | Style-only control |
| `control_02.png` | style board + two reference frames | Style-only control |
| `structure_01.png` | Blender structural scene + style board + two reference frames | Structural treatment |
| `structure_02.png` | Blender structural scene + style board + two reference frames | Structural treatment |

All four candidates must be untouched original model outputs. Post-processing
may be explored later, but a filtered derivative never counts as a candidate.

The first structured image was initially recorded as an OpenAI calibration.
After the user cancelled Gemini before it produced an output, that untouched
image was promoted to `outputs/originals/structure_01.png`. Its original copy
and original provenance remain under `outputs/openai_calibration/` so the
decision history is auditable. Gemini produced no candidate and none will be
counted.

## Sequence and stop rules

1. Run `python scripts/preflight.py`.
2. Stop if the structural source is blank, malformed, the wrong aspect ratio,
   or fails the edge/content checks.
3. Generate exactly the four candidates with OpenAI built-in image generation,
   using one independent generation call per candidate.
4. Save the untouched images in `outputs/originals/` and complete
   `outputs/provenance.json`.
5. Run `python scripts/prepare_review.py`.
6. Reject any candidate with missing provenance, missing required scene
   elements, a broken walkable corridor, a moved staircase/fountain, or a major
   building silhouette that no longer corresponds to the structural source.
7. Only candidates that pass the structural gate enter blind aesthetic review.
8. Continue to decomposition/Godot only if at least one structurally passing
   candidate is also judged aesthetically worth exploring for hours.

There are no numeric beauty scores authored by the generator. If no candidate
passes, the result is a useful failure, not a reason to redefine the test.

`GEMINI_ANTIGRAVITY_RUNBOOK.md` is retained only as a cancelled historical
artifact and must not be executed.
