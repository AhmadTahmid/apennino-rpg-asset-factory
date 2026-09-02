# Moonroot Hollow — Transfer and Engine Assessment

## Verdict

**The previous findings transfer, and a from-scratch town is substantially
easier. Godot was not the main bottleneck.**

The difficult part of the Appennino work was chiefly constrained
reconstruction: interpreting a moving reference, preserving its identity,
deciding which painted surfaces were physically traversable, and proving that
geometry matched flattened art. The real Italian setting added visual density,
terraces, stairs, and occlusion, but an equally detailed invented reference
would have caused similar problems.

With creative freedom, the art prompt could request gameplay topology before
pixels existed: one elevation, a broad clearing, one central obstacle, two
edge NPCs, and a clear spawn. The first output obeyed well enough to support a
complete quest without repair.

## Efficiency evidence

| Measure | Moonroot Hollow |
| --- | ---: |
| New town-generation calls | 1 |
| Post-generation pixel operations | 0 |
| External composition/style references | 0 |
| Visible raster assets | 2 town/player PNGs |
| Walkable-boundary vertices | 10 |
| Blocking landmarks | 1 moonwell |
| Quest landmarks | 3 |
| Tested quest-route waypoints | 9 |
| Normal runtime checks | 7 passed |
| Deliberate mutations | 4 detected |

This is not a universal benchmark. It is one favorable sample with a simple
single-level layout, but it demonstrates why design freedom matters more than
whether the setting is Italian or fantastical.

## Runtime evidence

Seven checks pass:

- locked town, traveler, and geometry hashes;
- raster-only visible-art policy;
- spawn, 2× player scale, atlas, boundary, well, and initial quest state;
- moonwater cannot be collected before speaking to Mora;
- the complete talk → collect → deliver route and state sequence;
- visible moonwell collision;
- outer-town boundary collision.

Four mutations fail only their intended contract:

| Mutation | Detected failure |
| --- | --- |
| `allow_early_well` | quest ordering |
| `shift_apothecary_x180` | complete quest loop |
| `missing_completion` | complete quest loop |
| `corridor_blocker` | complete quest loop |

The real renderer's no-player capture is pixel-identical to the locked town
art. The scaled traveler changes 3,956 pixels only inside its expected runtime
envelope.

## Was Appennino unusually hard?

Partly, but not because limestone towns are inherently hostile to AI.

The costly factors were:

1. **Reference fidelity.** We could not simplify or rearrange freely without
   ceasing to recreate the video.
2. **Flattened semantics.** People, roofs, stairs, stalls, foliage, and paving
   shared one image even though gameplay needed separate meanings.
3. **Multiple elevations and camera ambiguity.** Apparent paths were sometimes
   roofs, lower levels, or scenery.
4. **Reverse-order design.** Art existed before gameplay topology, so collision
   had to be inferred afterward.
5. **Research proof burden.** We were testing the workflow itself, not merely
   shipping a small game.

Moonroot Hollow reverses item 4: gameplay needs shaped the art prompt. That was
the largest efficiency improvement.

## Is Godot still the path of least resistance?

**For a local, complete 2D RPG slice in this workspace: yes.** Godot already
provides deterministic input, collision, scene loading, UI text, stateful
scripts, native rendering, and headless tests. Replacing it would not solve the
hard visual-semantic problems; it would reintroduce runtime plumbing.

Other options have narrower advantages:

| Runtime | Advantage | Cost here |
| --- | --- | --- |
| Phaser/HTML Canvas | Fastest browser sharing and code iteration | Rebuild physics/test/export conventions; custom canvas can tempt procedural placeholder art |
| RPG Maker | Fast stock RPG loops and menus | Tile/grid assumptions fight whole-scene generated paintings and custom semantics |
| LÖVE/Pygame | Very small programmable surface | More input, UI, packaging, and test infrastructure to own |
| Unity | Broad tooling and deployment | More project/editor overhead than this small 2D scope needs |

## What “AI-native” should mean beyond Godot

Godot should be the runtime target, not the intelligence layer. The missing
AI-native workflow belongs above it:

`design brief → generated raster scene → declarative town/quest manifest →`
`vision-assisted anchors and conservative geometry → generated Godot scene →`
`automated playthrough/mutations → real-render review`

Godot does not natively provide semantic image decomposition, prompt
provenance, visual scale calibration, gameplay-aware generation, or
vision-based geometry review. Those should remain engine-agnostic orchestration
so the same manifest could later target Godot and a browser runtime.

## Honest limitations

- The two NPCs are baked into the town painting; they cannot animate or change
  visually during dialogue.
- The player atlas was reused rather than generating another character under a
  time-optimization experiment.
- One screen, one obstacle, and one linear quest do not establish production
  scalability.
- Collision and interaction anchors remain manually authored after visual
  inspection.
- There is no inventory screen, combat, save system, audio, interior, or
  export package.

## Next optimization

The next useful engineering step is not another engine comparison. It is a
small scene compiler that consumes a raster background plus a town manifest
like `data/town_geometry.json` and emits the repetitive Godot scene, collision,
interaction, and baseline tests. That would attack the remaining integration
cost while preserving Godot's runtime advantages.
