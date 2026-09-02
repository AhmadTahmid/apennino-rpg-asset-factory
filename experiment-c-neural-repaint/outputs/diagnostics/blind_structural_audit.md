# Blind structural audit

The reviewer compared the structural source, landmark guide, and anonymous
A–D source-edge overlays. Candidate identities and provenance were hidden
until after the verdict.

All displacement estimates below are approximate and expressed at the locked
1920×1080 evaluation size after measuring the 960×540 diagnostic images.

| Label | Strict gate | Evidence |
| --- | --- | --- |
| A | Fail | New zoomed-out plaza composition. Fountain displaced about 232 px right and 174 px up; original roof silhouettes, path junction, alley, and corridor graph were replaced. |
| B | Fail | Coarse topology retained, but fountain shifted about 112 px left and multiple façades/eaves diverged from source contours. |
| C | Fail | New zoomed-out village. Fountain displaced about 102 px right and 136 px up; source roofs, junction, alley, and corridors were replaced. |
| D | Fail — closest | Broad topology, three major roofs, upper bridge/path, and alley remained recognizable, but the fountain shifted about 72 px left and roof/path boundaries drifted by tens of pixels. |

A and C preserve the semantic request, not the scaffold. B and D preserve
coarse topology, but neither is mask-stable enough to reuse collision,
elevation, navigation, or occlusion data from the source.

## Blind recommendation

Do not decompose or integrate any candidate into Godot under Experiment C's
geometry-first premise. Candidate D is the best qualitative target for a
tighter conditioning experiment. A future production gate should use explicit
tolerances, for example: critical landmark displacement no greater than 12 px
at 1920×1080, roof/eave/path contour error no greater than 16 px median and
32 px maximum, corridor-mask IoU at least 0.95, and no corridor connected-
component change.
