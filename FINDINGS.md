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

### 6. Generated sprite sheets need structural verification, not visual trust

Experiment E's first character generation looked like a transparent 3×4 atlas,
but both it and a targeted alpha-repair edit were ordinary RGB images with a
baked checkerboard. Equal-height slicing also clipped the north-facing row
because the generator left asymmetric vertical margins.

The usable workflow was: preserve both failed originals, inspect image mode and
dimensions, remove only border-connected checkerboard pixels, keep the largest
character component in each cell, slice at measured whitespace midlines, and
normalize frames to a common baseline. The final atlas passes alpha, cell,
distinct-frame, clipping, baseline, directional-runtime, and temporal-runtime
checks. “Looks like a sprite sheet” is not an asset contract.

### 7. One local foreground layer can be proven causally

Experiment E extracts a sparse full-canvas planter layer from the exact final
scene. Every one of its 2,072 visible RGB pixels equals the source, placement is
identity-aligned, and the selected pose overlaps 130 of 989 traveler pixels.
A real renderer shows all 130 restored to foreground pixels in correct order
and all 130 replaced by player pixels when the z-order is reversed.

This validates one source-locked overlap, not generalized Y-sorting. The useful
pattern is: sparse reviewed mask + exact source-pixel equality + preregistered
overlap + real-render baseline + reversed-order mutation.

### 8. The art-first contract transferred to a second node once

Experiment F used a source-video overlook frame for composition and the
accepted piazza only for visual language. One generation call returned a clean
1672×941 belvedere with no post-generation pixel operations. The existing
traveler/controller, final-art geometry schema, route checks, boundary checks,
mutation pattern, and real-render proof transferred directly. Explicit portal
anchors and spawn mappings made piazza → belvedere → piazza testable.

This is useful evidence of repeatability, but not automatic scaling. The node
was structurally easy, and frame selection, visual acceptance, a 10-vertex
walkable boundary, and both portal anchors still required manual judgment.
The inherited traveler also appears too small in the belvedere, showing that a
fixed sprite size is not a sufficient cross-node character/world scale
contract.

### 9. Evidence cost can exceed content cost

In Experiment F, generating and integrating the actual second node was simpler
than constructing and rerunning research-grade validation around it. Continuing
to create new bespoke harnesses for ordinary nodes would burn time and tokens
without proportional learning. The efficiency rule is now to freeze the
two-node harness, reuse it for ordinary content, and add new mutation families
only when introducing a genuinely new capability. Measure generation attempts,
cleanup operations, geometry effort, and test failures across several nodes
before making a production-scale claim.

### 10. The setting was not the main bottleneck

Moonroot Hollow removes reference fidelity and gives the generator explicit
gameplay topology: one elevation, a broad clearing, one central obstacle, two
edge NPCs, and an open spawn. The first generated output required zero pixel
repair and supported a complete talk → collect → deliver quest. This indicates
that the Appennino cost came primarily from constrained reconstruction,
flattened semantics, multi-level ambiguity, and research proof—not from Italian
stone architecture itself.

The transferable prompt lesson is to specify gameplay topology before scene
generation whenever creative freedom permits.

### 11. Godot is the runtime layer, not the AI-native layer

Godot remained cheap once art and semantics were clear: movement, collision,
interaction state, UI text, real rendering, and headless tests reused directly.
Switching engines would not solve semantic image decomposition or geometry
alignment. AI-native value belongs above the engine in raster generation,
declarative manifests, provenance, vision-assisted anchors, scale calibration,
playthrough generation, mutations, and render review.

The next efficiency target is a small manifest-to-Godot scene compiler, with a
browser runtime considered later as a second target rather than a replacement
for the orchestration layer.

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

### Visually plausible occlusion pose accepted without alpha overlap

The first proposed planter pose `(704,660)` lay inside the court and looked
reasonable, but the traveler and mask shared zero opaque pixels. Preflight
rejected it. `(704,675)` remains inside the same walkable polygon and yields a
measured 130/989 overlap. Layering tests need alpha intersection, not coordinate
intuition.

### Semantic cutout that secretly copies background

The first planter mask retained pale paving inside its outer polygon. It would
have hidden the player with a copied cobblestone patch while appearing locally
seamless. Hue-aware selection, connected-component cleanup, reviewed clear
points, source-pixel equality, and a strict occupancy ceiling removed that
failure mode.

### Headless rendering assumed to prove pixels

Godot's headless dummy renderer ran logic but returned no viewport image. The
final workflow separates headless physics/animation tests from a short hidden
real-renderer capture, then independently compares correct order, wrong order,
and no-player baseline pixels.

## Architecture decision table

| Need | Current best approach | Confidence |
| --- | --- | --- |
| Deterministic buildings, stairs, and boundaries | Procedural/semantic geometry | High |
| Rich atmosphere and coherent full-frame concept art | Whole-scene neural generation | High |
| Repaint while retaining exact masks | Not yet solved with available whole-frame generation | High confidence in current failure |
| Small playable vignette from final art | Manual geometry authored against final pixels | Validated for one node |
| One foreground overlap in flattened art | Sparse exact-source layer + real-render mutation | Validated locally |
| Automatic collision/occlusion extraction | Open question | Unvalidated |
| Explicit round-trip cross-node continuity | Authored portal/spawn mapping + route/boundary tests | Validated once on a simple second node |
| Automatic portal placement or inferred physical continuity | Open question | Unvalidated |
| Lean new RPG town with complete linear quest | Gameplay-first raster generation + reused Godot runtime | Validated once |
| Raster-only visible art policy | PNG asset scan + scene/script primitive scan + real render | Validated in Moonroot Hollow |

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
8. Validate generated game assets structurally: mode, alpha, grid, baselines,
   direction mapping, and temporal progression.
9. For foreground claims, compare real rendered pixels against a baseline and a
   deliberately reversed z-order.
10. Reuse the frozen two-node harness for ordinary nodes; record attempt count,
    cleanup work, geometry effort, and failures instead of rebuilding the proof.
11. Add new capability tests only for interaction, elevation, dynamic depth, or
    other genuinely new semantics.

## Current macro status

The project has reached a defensible two-node playable result with animated
embodiment, one local depth interaction, and explicit round-trip continuity. It
has not reached automatic video-to-map compilation, production-matched
character integration, automatic geometry/portal extraction, multi-elevation
play, or general scene depth. The next useful question is no longer whether a
second simple node is possible; it is whether two or three more nodes can be
added with a falling repair rate and bounded manual geometry effort while the
same validation template remains unchanged.
