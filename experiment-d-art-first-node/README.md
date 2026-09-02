# Experiment D — Art-First Playable Piazza

## Question

Can one attractive whole-scene image derived from the Appennino reference video
become a mechanically honest playable micro-node when collision geometry is
authored against the **final art**, rather than inherited from a different
Blender layout?

## Result scope

This experiment targets one conservative, single-elevation U-shaped route
through the lower half of the central fountain court in Experiment C's blind
visual winner. Success means a player can travel west–south–east and back,
collide with the basin, and be blocked by the scoped plaza boundary.

It does **not** claim automatic collision extraction, semantic decomposition,
stairs, elevation, roof occlusion, NPC interaction, portals, or whole-town
playability. Painted people, the cat, market stalls, and small props are static
non-reactive background decoration and are deliberately kept outside the tested
route. Some invisible-wall behavior exists where the conservative boundary cuts
across apparently open paving, and there is no true foreground depth sorting.

Accepted geometry covers only a hand-authored lower-court U-route on the single
visible fountain-plaza elevation. It is not a complete fountain loop or a
freely navigable village. The northern market and inhabitants, northwest
stairs, east street, right-side gaps, lower arches, and roof-occluded foreground
remain static scenery. Collision is an approximate 2D foot-space mask with
intentionally inset invisible boundaries.

## Lineage

- Video input: `../A_random_Appennino_Italian_tow.mp4` (10.005 s, 1280×720,
  24 fps; not copied into this experiment).
- Reference frames: `../reference_frames/frame_001.jpg` and `frame_003.jpg`.
- Generated scene: byte-identical copy of Experiment C's `control_01.png`, the
  blind aesthetic winner.
- Gameplay geometry: manually authored in native image coordinates and stored
  in `data/node_001_geometry.json`.

## Controls

- Arrow keys or WASD: move.
- `F2`: toggle the authored geometry overlay.
- `Esc`: quit.

## Reproduce

```powershell
godot_console --headless --editor --path "D:\Apennino scene\experiment-d-art-first-node" --quit
godot_console --headless --path "D:\Apennino scene\experiment-d-art-first-node" --scene res://tests/test_node.tscn
godot --path "D:\Apennino scene\experiment-d-art-first-node" --scene res://scenes/main.tscn
```

Run the complete validation, including mutation checks that are expected to
fail:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_validation.ps1
```

The runner accepts two deliberate mutations:

- `--mutation=shift_fountain` moves the collision basin away from the art.
- `--mutation=corridor_blocker` inserts an invisible blocker across the route.

The normal suite must exit `0`; each mutation run must exit nonzero. A timeout
or collision never counts as reaching a waypoint.

## Coordinate convention

All geometry uses native 1672×941 image pixels with origin at the upper-left.
The background is neither cropped nor silently stretched. The scoped boundary,
fountain ellipse, spawn, route, and closed exits are documented in the JSON and
in `diagnostics/geometry_overlay.png`.
