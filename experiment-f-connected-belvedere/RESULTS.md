# Experiment F — Results

## Verdict

**Pass as a first cross-node transfer, not as proof of automated scaling.** A
second video-inspired micro-node was generated, made playable, connected in
both directions, mutation-tested, and real-render verified while preserving
the prior piazza geometry byte-for-byte.

## Normal validation

Eight runtime checks passed:

| Test | What it establishes |
| --- | --- |
| Asset integrity | Both 1672×941 scenes, traveler, foreground, and geometry files match locked hashes. |
| Node 001 regression | Piazza visibility, spawn, boundary, foreground, and fountain collision remain intact. |
| Portal gating | Travel is rejected away from the portal and enabled at the declared source-space anchor. |
| Piazza route to portal | The accepted five-leg lower-court route reaches the travel point. |
| Transition to belvedere | Scene art, collision set, occluder visibility, and arrival spawn switch together. |
| Belvedere route | A nine-leg terrace loop reaches the return portal without collision. |
| Belvedere boundary | Attempting to cross the front parapet is blocked by `BelvedereBoundary`. |
| Round-trip return | Return restores the piazza art, foreground, collision, and declared east-side spawn. |

## Mutation validation

Four known-bad states failed only their declared check:

| Mutation | Exact rejected contract |
| --- | --- |
| `wrong_belvedere_spawn` | `transition_to_belvedere` |
| `broken_return` | `round_trip_return` |
| `shift_piazza_portal_x100` | `portal_gating` |
| `belvedere_corridor_blocker` | `belvedere_route` |

## Real-render evidence

The hidden GL renderer captured the new node at native resolution with and
without the traveler. Independent pixel comparison found:

- the no-player capture equals the locked belvedere image at every pixel;
- the player capture differs only inside the expected 49×65 sprite envelope;
- 895 pixels change inside that envelope.

This proves that the runtime is actually showing the locked generated scene and
traveler, rather than merely passing state assertions.

Independent visual audit passes the environment and floor readability, but
marks traveler integration partial: the inherited sprite is visibly too small
against the terrace masonry and the source overlook protagonist. The portal is
functionally proven but remains an authored travel link, not evidence that the
two paintings are geometrically adjacent. See `diagnostics/visual_audit.md`.

## Generation outcome

Unlike Experiment E's sprite sheet, the belvedere generation needed no repair:

- one built-in generation call;
- exact required dimensions on first output;
- no unwanted HUD, text, character, or blocked entrance;
- project asset byte-identical to the preserved original;
- geometry authored only after the pixels were locked.

The exact prompt, input roles, source path, dimensions, and hash are in
`data/art_generation_provenance.json`.

## Stumble retained

The first Godot test launch exposed strict type-inference errors in dynamically
called test variables. Without a fresh-result requirement, an engine process
could remain alive after the script failed to load. The final runner deletes
prior result payloads, scans the import log for parse failures, and requires a
fresh JSON result for every normal and mutated run.

## Scalability assessment

### Evidence that transfers

1. A source-video frame can serve as a composition target while a previously
   accepted node supplies visual language; the model did not need the old
   geometry or a handcrafted layout scaffold.
2. The existing traveler/controller moved into the new scene unchanged.
3. The data model for final-art geometry, route testing, boundary testing,
   portal mapping, mutations, and real-render evidence transferred directly.
4. Cross-node state errors are cheap to express and catch once portal and spawn
   mappings are explicit data/contracts.

### Still bespoke and not scalable

1. Frame selection, visual acceptance, walkable polygon authorship, and portal
   placement remain manual judgment.
2. The belvedere is structurally easy. It does not test stairs, multiple
   elevations, NPCs, moving occluders, doors, or general depth sorting.
3. One successful transfer is evidence of repeatability, not a measured
   production rate. We do not yet have several nodes' cost/repair statistics.
4. The validation and documentation effort is currently larger than the actual
   content-integration effort. Rebuilding equally elaborate evidence for every
   simple node would be wasteful.
5. A fixed player atlas did not guarantee consistent perceived scale in a new
   environment. Character-to-world scale needs its own guide or per-node
   contract.

## Efficiency decision

Freeze Experiment F as the reusable two-node template. For subsequent ordinary
nodes, reuse the same checks and record only incremental evidence: generation
attempt count, cleanup operations, geometry vertices, route/portal results,
and a runtime capture. Add new mutation families only when a new capability is
introduced. After two or three more nodes, compare repair rate and manual
geometry effort before claiming scalability.

## Nonclaims

- automatic video-to-world compilation;
- inferred physical continuity between the painted piazza and belvedere;
- production-ready transition effects or streaming;
- automatic frame selection, collision extraction, or portal placement;
- multi-elevation traversal, NPC interaction, or general scene depth;
- proof that every source-video frame will generate cleanly on the first try.
