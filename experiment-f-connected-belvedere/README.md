# Experiment F — Connected Belvedere

## Question

Can the art-first workflow transfer from the accepted piazza to a second
source-video-inspired playable node without modifying the piazza geometry or
requiring another bespoke asset-repair pipeline?

## Result

**Yes for one deliberately simple second node.** The traveler can follow the
existing lower-court route to the piazza's east terminus, press `E`, explore a
new stone belvedere, and return to the piazza. The new scene is based on the
source video's valley-overlook frame and uses the Experiment E piazza only as a
style reference.

![Belvedere runtime](diagnostics/runtime_belvedere_capture.png)

The belvedere generation succeeded on the first attempt at the exact 1672×941
runtime size. No paint cleanup, cropping, alpha repair, or resizing was needed.
The preserved original and runtime asset are byte-identical. Geometry remains
separate and manually aligned against the final pixels.

## Controls and playtest

- Arrow keys or WASD: move.
- `E`: travel while standing inside a gold portal marker.
- `F2`: show the current cyan walkable boundary, yellow tested route, and gold
  portal.
- `Esc`: quit.

In the piazza, follow the lower route around the fountain to the east endpoint;
the interaction prompt appears near the gold marker. On the belvedere, the
return marker is at the open bottom-center entrance.

```powershell
godot --path "D:\Apennino scene\experiment-f-connected-belvedere" --scene res://scenes/main.tscn
```

## Reproduce the evidence

Requirements: Godot 4.7.2, Python, and Pillow.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_validation.ps1
```

The runner validates locked assets and provenance, proves the Experiment E
piazza geometry is byte-identical, runs eight runtime checks, rejects four
single-cause mutations, captures the belvedere with a hidden real renderer,
and verifies that the no-player capture exactly equals the locked scene art.

## What this teaches—and what it does not

This is the first evidence that the workflow can be repeated across nodes. The
useful reusable unit is:

`video composition frame + established style reference → clean scene art →`
`geometry authored against final pixels → tested route/boundary → explicit`
`round-trip portal mapping`

It is not yet evidence of automatic or cheap world generation. A human/agent
still selected the frame, judged the generated scene, drew a conservative
10-vertex walkable boundary, chose portal anchors, and reviewed the overlay.
The second node is also an unusually easy terrace: one elevation, no NPCs, no
stairs, and no new occlusion layer.

The honest efficiency conclusion is that the content step transferred well,
while the research harness remains expensive relative to the amount of map
added. Future nodes should reuse this harness as a frozen template and add new
tests only for genuinely new capabilities.

The runtime capture also exposes a visual portability gap: the inherited
traveler is clearly readable but too small for the belvedere's masonry and the
source frame's protagonist scale. This is retained as evidence that a fixed
sprite size is not automatically a cross-node scale contract. See
`diagnostics/visual_audit.md`.

See [RESULTS.md](RESULTS.md) for the full evidence and scalability assessment.
