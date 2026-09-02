# Experiment D — Results

## Verdict

**Pass within the deliberately narrow scope.** A visually strong, generated
Appennino scene now supports one real playable lower-court route in Godot.

The player can travel west–south–east below the fountain and return, collide
with the visible basin, and be blocked by the scoped plaza boundary. The
northern arc is closed because it contains people, an animal, and market props
baked into the flattened painting. The experiment makes no claim about the rest
of the town.

The revised route passed independent visual audit because every tested
footpoint remains on unobstructed lower-court paving. This does not validate the
rest of the image as playable geometry.

## Normal validation

Godot 4.7.2 ran six fail-capable runtime checks. All six passed:

| Test | Result | Evidence |
| --- | --- | --- |
| Asset integrity | Pass | Exact scene/player hashes and 1672×941 art dimensions matched. |
| Collision probes | Pass | Four known-open points were clear; the fountain center resolved to `FountainBasin`. |
| Fountain blocking | Pass | Direct approach returned `BLOCKED`, named `FountainBasin`, and recorded a real slide collision. |
| Lower-court outbound | Pass | Five legs reached the east side through visible lower paving with no unexpected collision. |
| Lower-court return | Pass | Four legs returned to spawn through the same conservative court with no unexpected collision. |
| Outer boundary | Pass | Escape attempt returned `BLOCKED` by `PlazaBoundary`. |

The full expected/actual values are stored in
`diagnostics/test_results.json`.

The runtime result also records SHA-256 hashes for the geometry JSON, world
script, player controller, test script, and main scene. Visual alignment between
the hand-authored geometry and the painted pixels remains a manually reviewed
claim supported by the overlay; it is not independently inferred by the tests.

## Mutation validation

Two deliberately broken variants prove that the suite can fail:

1. `shift_fountain` moved the collider 180 px right. The suite rejected it:
   the art-center probe became empty, a known-open point became solid, direct
   fountain approach incorrectly reached the target, and movement disagreed
   with the painting.
2. `corridor_blocker` inserted an invisible solid across the lower route. The
   suite rejected it when outbound movement was blocked specifically by
   `MutationCorridorBlocker`.

Both mutations exited nonzero and wrote `passed: false` evidence files. The
PowerShell validator treats a mutation that exits `0` as a validation failure.

## Stumbles retained as findings

### Engine exit code was not proof of test execution

The first GDScript contained parse errors, yet launching it through the GUI
`godot.exe` returned process code `0`. An exit-code-only wrapper would have
reported a false success—the same class of error found in the old Experiment
B harness.

The final runner uses blocking `godot_console.exe` and requires a fresh JSON
result file whose `passed` field is true. Missing results fail regardless of
the engine process code.

### The first south waypoint touched the real boundary

In the superseded full-orbit suite, `(888, 741)` was visually plausible but
left less than the player's foot radius before the south boundary. Physics
blocked it, so it moved to `(888, 730)`. That entire orbit suite was later
invalidated by visual audit. The accepted lower-court route uses `(888, 720)`
and makes no winding or full-orbit claim.

### Physics passed a visually invalid northern route

The first normal suite completed a full fountain orbit, but independent visual
audit showed that its north arc crossed the baked red protagonist, elderly
woman, cat, and market frontage. That passing JSON and overlay are preserved as
`diagnostics/invalidated_full_orbit_*` evidence. The accepted geometry closes
the northern court and tests only a clear lower U-shaped route. This is a
reminder that collision success alone cannot certify flattened scene art.

## What this validates

- Beautiful whole-scene neural art can serve as the background for a small,
  genuinely playable 2D node.
- Authoring collision against final art avoids the mask-drift failure exposed
  by Experiment C.
- A tiny honest scope produces stronger evidence than a large self-certified
  demo.
- Machine-readable expected/actual results plus mutation testing substantially
  improve confidence over screenshots or videos alone.

## What this does not validate

- automatic collision or mask extraction;
- playability of the visible stairs, alleys, terraces, or lower level;
- foreground occlusion or Y-sorting against the flattened art;
- interaction with the people and market painted into the background;
- collision for the baked people, cat, stalls, planters, and other small props;
- seamless boundary visuals—some conservative invisible walls cut across
  apparently open cobbles;
- exhaustive manual-input or full-perimeter coverage (the automated route and
  one southwest escape vector are tested);
- final player art, animation, cross-node continuity, or world synthesis.

## Macro-objective impact

This is the first defensible end-to-end slice in the repository:

`reference video → extracted visual language → generated coherent scene →`
`geometry authored against final art → controllable and tested playable node`

It proves the project can reach the user's minimum success condition—a small
playable recreation inspired by the video—without pretending the entire frame
has solved gameplay semantics.

## Recommended next module

Keep this node playable and add one capability at a time:

1. replace the marker player with a style-matched animated character;
2. add one authored foreground occluder near the east doorway and test actual
   draw order with pixel probes or rendered-frame comparison;
3. open exactly one exit into a second tiny zone;
4. only then test assisted extraction of collision/occlusion masks.
