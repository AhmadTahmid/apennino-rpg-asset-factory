# Experiment H — Results and Macro Assessment

## Verdict

**The raster-first workflow scaled from one room to a small complete adventure
without proportional engine work.** Two new first-pass environment generations,
one reusable scene, and one manifest produced three traversable locations, a
persistent quest, inventory, save/load, restart, and an ending.

This is stronger evidence than Experiment G's single screen, but it is still a
linear vertical slice—not evidence that a whole RPG can be generated without
semantic design work.

## Measured result

| Measure | Experiment H |
| --- | ---: |
| Playable locations | 3 |
| New environment-generation calls | 2 |
| Usable first outputs | 2 |
| Regeneration calls | 0 |
| Post-generation pixel operations | 0 |
| Reused raster plates / character atlases | 1 / 1 |
| Quest states / inventory item types | 8 / 2 |
| Normal runtime contracts | 12 passed, 0 failed |
| Deliberate mutations | 6 detected |
| Real-render captures | 6 |
| Exact background baselines | 3 of 3 |

The effort ledger deliberately does not invent wall-clock, token-cost, or
human-equivalent labor measurements. See
[data/effort_ledger.json](data/effort_ledger.json).

## Runtime evidence

The normal suite proves:

- all four visible assets have locked hashes and expected dimensions;
- the project contains only raster illustrated assets and engine text;
- three manifest locations and all 29 gameplay points are inside their declared
  boundaries;
- the initial state is correct and the sanctuary portal is gated;
- the complete physical route reaches every landmark and the ending;
- moonwater is added then consumed, and the star-seed is added then consumed;
- save/load restores location, state, inventory, and exact player position;
- an incompatible save is rejected without changing live state;
- new game resets location, quest, inventory, position, and ending UI;
- the town well, forest basin, and sanctuary altar collide with the correct
  named bodies;
- every location boundary blocks the player.

Six known-bad mutations fail the expected contracts:

| Mutation | Detected failures |
| --- | --- |
| Portal works without star-seed | Locked-portal contract |
| Star-seed is not awarded | Full slice; inventory contract |
| Altar never completes | Full slice |
| Forest spawn is outside the level | Full slice; save/load; forest collision and boundary checks |
| Forest corridor is blocked | Full slice; forest landmark collision identity |
| Loaded position drifts 120 px | Save/load round trip |

Godot's non-headless OpenGL renderer produced a no-player and player capture for
every location. All three no-player images are pixel-identical to their locked
generated plates. The traveler changes exactly 3,956 pixels inside its expected
local envelope in each node.

## What this teaches about speed

The dominant acceleration did not come from switching engines or writing more
agent orchestration. It came from ordering the work correctly:

1. ask for gameplay topology while generating the art;
2. keep each plate to one elevation and a broad readable route;
3. use one coordinate system from image through tests;
4. put repeated runtime behavior behind a manifest;
5. test the whole quest route, persistence, and failure modes automatically.

The two new plates needed no repair because their prompts specified entry,
exit, walk lane, landmark placement, elevation count, exclusions, and runtime
intent. This is a favorable two-sample result, not a guaranteed generation
rate. Still, it supports the hypothesis that topology-aware prompting reduces
integration work more than additional post-processing does.

## Relation to the Appennino objective

The original Appennino problem remains harder for structural reasons:

- source fidelity forbids rearranging the image around gameplay;
- a moving video must be interpreted before a stable plate exists;
- terraces, stairs, roofs, people, and scenery occupy ambiguous depths;
- geometry has to be inferred after the pixels were authored for a different
  purpose.

Experiment H therefore does not solve video-to-playable reconstruction. It
does prove that the downstream game-building method is viable once a usable
plate and semantics exist. The reusable contribution is the plate + manifest +
runtime + falsification boundary; the unsolved Appennino contribution is
reliable automated extraction of that plate and manifest from video.

## Godot decision

Godot remains the path of least resistance for this target. The generic runtime
now supplies collision, input, animation, UI, state, persistence, scene
transition, headless physics, and renderer capture in a small code surface.
Replacing it would not automate semantic geometry; it would recreate these
mechanics.

The AI-native layer belongs above Godot. It should generate or analyze raster
plates, propose manifest semantics, record provenance, compile runtime data,
and run evaluations. Because the manifest is engine-neutral JSON, a browser
target could be added later for distribution without making it the current
authoring backbone.

## Scope choices and honest limits

Combat was intentionally not added. A credible combat loop needs additional
animated character art, feedback, balance, and failure/restart states. Under a
time-to-complete objective, persistence and a real ending tested more reusable
RPG infrastructure per new asset.

Remaining limits:

- NPCs and quest objects are baked into backgrounds, so their visuals do not
  react or animate;
- boundaries and anchors are still authored after visual inspection;
- the quest is linear and the state machine is code, not data;
- there is no audio, combat, settings menu, accessibility pass, packaging, or
  platform export;
- three simple one-elevation nodes do not validate multi-level maps or a large
  world;
- style continuity is strong but not mathematically guaranteed by generation.

## Next highest-value experiment

Stop adding bespoke gameplay features for one iteration. Build a draft-manifest
compiler that accepts a gameplay-aware art brief plus a raster plate, proposes
anchors/boundaries/routes, emits this schema, and measures correction distance.
That attacks the remaining manual bottleneck and directly reconnects the
fantastical result to the video-to-playable macro objective.
