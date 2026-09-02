# Reusable Manifest-Driven Runtime

Experiment H separates content from mechanics at the smallest useful boundary:

```text
generated opaque raster plate
            +
declarative location semantics (JSON)
            ↓
one Godot runtime → collision, interaction, traversal, quest, save/load
            ↓
headless route tests + known-bad mutations + real-render comparison
```

## Manifest contract

Each location declares:

- a stable ID, display name, and raster art resource;
- one spawn point;
- one conservative walkable boundary;
- zero or more invisible obstacles;
- interaction anchors and radii;
- explicit route waypoints used by the automated playthrough.

Coordinates are native image pixels with origin at the top left. This keeps
visual review, runtime setup, and test evidence in one coordinate system.

## Runtime responsibilities

`world_runtime.gd` owns mechanics that should not be repeated per map:

- load the selected plate into the single background sprite;
- destroy and reconstruct invisible collision from manifest data;
- place and animate the shared traveler;
- resolve proximity interaction;
- run the quest/inventory state machine;
- serialize and validate persistence;
- update text UI and the ending state.

The quest state machine remains code because Experiment H contains only one
short authored quest. A larger project should move dialogue and state
preconditions/effects into a second validated data schema rather than grow one
large match statement.

## Validation boundary

The system deliberately uses three different forms of evidence:

1. static checks lock assets, provenance, coordinates, and raster-only policy;
2. Godot headless tests use real character movement and collision, not
   teleport-only assertions, for the full quest route;
3. non-headless OpenGL captures prove that the runtime background is exactly the
   source raster and that enabling the traveler changes only its local envelope.

Mutations test causal sensitivity: bypassing a gate, losing the star-seed,
removing completion, corrupting a spawn, blocking the forest, and drifting a
loaded position each produce a known set of failed contracts.

## Scaling implication

This design removes per-location scene assembly, but not semantic authorship.
The next compiler should produce a draft manifest from a gameplay-aware image
brief and vision analysis, then require review of:

- boundary conservatism;
- obstacle footprints;
- landmark anchors;
- portal/spawn pairings;
- route reachability.

Keeping that draft reviewable is safer than letting image pixels silently
become collision truth. The manifest is also engine-agnostic enough to target a
browser runtime later without changing the generated art or semantic contract.
