# Transferable Findings — AI-Native Video-to-Playable Workflow

This is the living cross-experiment record. It separates observations that are
supported by artifacts from hypotheses that remain open.

## What currently works

### 1. Video references can define a usable world language

A small number of representative frames were enough to recover recurring
visual features: warm limestone, terracotta roofs, olive shutters, geraniums,
stacked levels, stairs, retaining walls, central civic space, and blue-green
mountain atmosphere. Whole-scene generation reproduced this language much more
coherently than independently generated modular sprites.

### 2. Whole-scene generation solves the collage problem

Experiment C's style-only controls share one camera, light direction, material
language, and spatial composition. They are substantially stronger as complete
places than the earlier cutout assembly.

### 3. Coarse conditioning is not mask stability

The structure-conditioned images visibly resembled the Blender scaffold, but
their critical features still moved by tens to hundreds of pixels. The closest
fountain moved approximately 72 px at the locked 1920×1080 evaluation size.
This is enough to make inherited collision, navigation, elevation, and
occlusion wrong.

The reusable lesson: evaluate landmark and contour agreement, not whether both
images contain “a fountain and three roofs.”

### 4. Art-first playability is viable at small scope

Experiment D discards the incompatible Blender masks and authors a conservative
walkable polygon and fountain collider against the final generated image. A
real player controller completes a collision-free lower-court route and return,
is blocked by the visible fountain, and is blocked on the tested southwest
escape vector.

An initially passing full-orbit physics test was rejected during visual audit:
its northern arc crossed people, an animal, and the market baked into the
flattened painting. The accepted scope closes that arc. This demonstrates why
behavioral correctness and pixel-level scene plausibility require separate
review.

This validates a minimum end-to-end chain, not full automatic world synthesis.

### 5. Mutation testing is essential for agent-authored validation

The playable suite is deliberately run against two corruptions: a shifted
fountain and an invisible corridor blocker. Both must fail. This proves the
checks depend on the behavior they claim to test.

## Failure patterns worth reusing elsewhere

### Generator self-certification

The earlier system generated artifacts, authored its own scores, and announced
success. Independent inspection showed that the visual and gameplay claims did
not follow from the evidence. Separate generation, blind review, structural
audit, and runtime verification.

### Hard-coded evaluation

Scores in the historical whole-scene experiment were literal constants. A
metric without a computation path is a label, not evidence.

### Tautological reconstruction metrics

Keeping the complete master image in a “background” layer guarantees perfect
reconstruction when the same foreground is recomposited. PSNR 100 dB therefore
proved nothing about semantic decomposition.

### Timeout or collision treated as completion

The historical controller emitted its success callback after collision or a
timeout. The replacement uses mutually exclusive `REACHED`, `BLOCKED`, and
`TIMEOUT` outcomes. Tests assert the expected outcome and collider identity.

### Process exit code treated as test execution

During Experiment D, the first Godot test script had parse errors while the GUI
launcher still returned process code `0`. The validator now uses the blocking
console executable and requires a fresh machine-readable result payload. No
result file means failure.

### Visually plausible coordinates accepted without physics

The initial south waypoint looked safe but placed the player's foot collider
too close to the boundary. Real movement blocked. The waypoint was corrected
on visible paving, and the stumble remains recorded in Experiment D's report.

## Architecture decision table

| Need | Current best approach | Confidence |
| --- | --- | --- |
| Deterministic buildings, stairs, and boundaries | Procedural/semantic geometry | High |
| Rich atmosphere and coherent full-frame concept art | Whole-scene neural generation | High |
| Repaint while retaining exact masks | Not yet solved with available whole-frame generation | High confidence in current failure |
| Small playable vignette from final art | Manual geometry authored against final pixels | Validated for one node |
| Automatic collision/occlusion extraction | Open question | Unvalidated |
| Cross-node continuity | Open question | Unvalidated |

## Recommended experimental order

1. Lock the input hashes, prompt, coordinate system, success gates, and
   nonclaims before generation.
2. Generate untouched candidates with a control condition.
3. Blind-review beauty separately from structural fidelity.
4. If old geometry must be reused, require numeric landmark, contour, and
   connectivity tolerances.
5. If the art is the source of truth, author or extract new geometry against
   the final pixels.
6. Build the smallest playable route first.
7. Require expected/actual assertions and known-bad mutation runs.
8. Add one capability at a time: player art, occlusion, interaction, elevation,
   then multiple nodes.

## Current macro status

The project has reached a defensible minimum playable result. It has not yet
reached automatic video-to-map compilation. The most promising immediate path
is to expand the validated art-first node incrementally while continuing a
separate geometry-control research branch.
