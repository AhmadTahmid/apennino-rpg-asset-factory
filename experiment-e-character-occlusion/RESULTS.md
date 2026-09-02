# Experiment E — Results

## Verdict

**Pass as a local causal depth-ordering proof, with character-integration
residuals.** On the unchanged lower-court geometry, a four-direction animated
traveler can pass behind one exact-source southwest planter. Reversing draw
order visibly and numerically breaks the effect.

This is not a production-readiness pass. Independent visual review finds the
traveler distinct and readable, but slightly underscaled, flatter, and more
strongly outlined than the inhabitants baked into the scene.

## Normal validation

Twelve runtime checks passed:

| Test | Result | What it establishes |
| --- | --- | --- |
| Asset integrity | Pass | Scene, atlas, mask, foreground, geometry hashes and dimensions match. |
| Atlas integrity | Pass | RGBA 3×4 atlas, twelve nonempty frames, transparent borders, three distinct poses per row, and y=59 foot baselines. |
| Direction mapping | Pass | Actual down/left/right/up movement selects rows 0/1/2/3. |
| Temporal animation | Pass | Moving trace contains repeated `0,1,2,1` cycles; stop returns to idle column 1. |
| Foreground asset contract | Pass | 2,072 alpha pixels match the mask; every retained RGB pixel equals the locked source. |
| Foreground transform | Pass | Full-canvas layer is integer-aligned at identity scale/rotation/offset. |
| Occlusion state | Pass | Fixed pose has 130 hidden and 859 visible traveler pixels; foreground z=20 exceeds player z=10. |
| Collision probes | Pass | Known-open probes are clear and fountain center names `FountainBasin`. |
| Fountain blocking | Pass | Direct movement is blocked by the visible basin. |
| Lower-court outbound | Pass | Five route legs reach the east side without collision. |
| Lower-court return | Pass | Four route legs return to spawn without collision. |
| Outer boundary | Pass | Southwest escape is blocked by `PlazaBoundary`. |

The complete expected/actual values are in `diagnostics/test_results.json`.

## Real-render evidence

A hidden Windows GL Compatibility run captured the correct order, a reversed
order, and a no-player baseline at native 1672×941 resolution. Independent
pixel comparison passed:

| Probe | Expected | Actual |
| --- | ---: | ---: |
| Declared player/planter overlap | 130 | 130 |
| Correct-order overlap pixels equal baseline | 130 | 130 |
| Reversed-order overlap pixels reveal player | 130 | 130 |
| Player pixels visible outside mask | 859 | 859 |
| Outside-mask pixels unchanged by z-order reversal | 859 | 859 |
| Runtime baseline pixels equal source under full mask | 2,072 | 2,072 |

This closes a gap that a z-index assertion alone would leave. The paired crops
also passed independent visual audit as a credible local foreground effect.

## Mutation validation

Seven known-bad states exited nonzero and failed only their declared checks:

| Mutation | Required failures |
| --- | --- |
| `freeze_animation` | `temporal_animation` |
| `swap_left_right_rows` | `direction_mapping` |
| `occluder_below_player` | `occlusion_state_contract` |
| `occluder_shift_x20` | `foreground_transform_contract`, `occlusion_state_contract` |
| `full_rectangle_mask` | `foreground_asset_contract`, `occlusion_state_contract` |
| `shift_fountain` | `collision_probe_contract`, `fountain_blocking`, outbound, return |
| `corridor_blocker` | `collision_probe_contract`, outbound, return |

The runner rejects a mutation that exits zero, lacks a fresh result, reports a
different mutation ID, fails an unrelated test, omits a required failure, or
records source hashes that no longer match the files.

## Stumbles retained as findings

### “Transparent PNG” was a flattened checkerboard twice

The initial generation produced the right character concept and twelve useful
poses, but the PNG was `RGB`, not `RGBA`; the visible checkerboard was part of
the pixels. A targeted edit explicitly requesting alpha again returned `RGB`
and changed the height from 1578 to 1579. The final alpha therefore comes from
a disclosed deterministic extraction step, not from pretending the model
obeyed the request.

### Equal grid slicing clipped the north-facing row

The generator honored three columns but left asymmetric vertical margins.
Equal-height four-row slicing cut the top of the north-facing hair and initially
made another row appear implausibly thin due to disconnected background
remnants. Whitespace midlines and largest-component cleanup fixed the mechanical
slicing; both the faulty assumption and correction are visible in the script
and asset report.

### The first semantic mask copied paving

An outer polygon alone produced a clean-looking but invalid patch containing
cobblestones. Hue-aware selection, rail corridors, and largest-component
cleanup reduced it to the planter/foliage/rail object. Reviewed must-clear
points and a low full-canvas occupancy gate prevent a broad rectangle from
passing.

### The visually proposed occlusion anchor had zero overlap

The first anchor `(704,660)` looked plausible but shared **zero** pixels between
the fixed traveler pose and extracted mask. The preflight failed. Searching the
actual alpha intersection selected `(704,675)`, still within the unchanged
walkable polygon, with 130/989 overlap pixels. Coordinate plausibility was not
accepted as proof.

### Headless physics could not produce render evidence

Godot's headless dummy renderer returned no viewport texture. The final runner
keeps physics/movement headless and uses a short hidden real-renderer process
only for native-resolution captures. The failure and successful renderer logs
are both retained.

### The delegated harness stalled and initially had parse errors

The first delegated validation attempt did not yield a fresh result, and its
import log exposed strict GDScript type errors even though editor launch
returned zero—the same exit-code trap seen in Experiment D. The main task
stopped the stale run, corrected the typed comparisons, scanned the import log
for script errors, and required fresh JSON before accepting the suite.

## Macro-objective impact

The defensible chain is now:

`reference video → extracted visual language → coherent generated scene →`
`geometry authored against final pixels → tested movement/collision →`
`animated player embodiment → one mutation-sensitive foreground interaction`

This makes the small playable recreation feel more like a game while exposing
two reusable AI-native workflow boundaries:

1. attractive generated sprite sheets may still need deterministic structural
   normalization and alpha repair;
2. flattened scene depth becomes trustworthy only when a sparse source-locked
   layer, actual render comparison, and reversed-order control all agree.

## What remains open

- production-matched traveler scale, values, outline weight, and contact shadow;
- more than one foreground object or general Y-sorting;
- automatic occlusion/collision extraction;
- a real exit and second playable zone;
- interaction with inhabitants and props;
- stairs, elevation, roofs, and cross-node continuity.
