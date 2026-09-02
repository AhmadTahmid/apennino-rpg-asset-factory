# Experiment E — Independent Visual Audit

Date: 2026-09-02
Reviewer role: independent read-only visual audit; not the asset generator or implementer

## Verdict

Experiment E **passes as a narrow local-occlusion proof**, not as
production-ready character integration.

| Claim | Verdict | Evidence and residual risk |
| --- | --- | --- |
| Traveler distinction and directional readability | Pass | Teal/cream clothing, trousers, satchel, and uncovered brown hair separate the traveler from the baked red hero, green/white elderly woman, and brown-hatted man. Four directions and step/idle states are legible. |
| Native style and scale match | Partial | The traveler is about 20–30% lower in visual mass than the central baked figures, with darker/coarser outlines and flatter facial/value treatment. He reads as a game sprite placed into the painting. A production iteration should regenerate at roughly 1.15–1.25× native visual mass, soften the darkest contour, and add a subtle contact shadow rather than merely scaling the current atlas. |
| Correct foreground ordering | Pass | In `runtime_occlusion_capture_crop.png`, planter foliage and railing hide the lower legs/feet while the torso and head remain visible. |
| Causal mutation | Pass | In `runtime_occlusion_capture_player_above_crop.png`, the boots incorrectly render over the foliage. The paired captures demonstrate the effect of draw order. |
| Foreground extraction quality | Pass at locked alignment | No rectangular paving patch is visible. A thin pale/olive fringe and tiny edge pixels could halo if the layer is scaled, filtered, or shifted off integer coordinates. Keep identity placement and nearest filtering; consider a later one-pixel cleanup. |
| Unchanged walkability and scope | Pass | The geometry overlay retains Experiment D's lower U-shaped court and fountain obstacle. The local planter pose lies inside that unchanged micro-scope and opens no new exit. |

## Required nonclaim

The result proves one hand-authored, source-locked foreground overlap at one
court edge. It does not demonstrate general Y-sorting, scene-wide depth
extraction, roof/fountain/facade occlusion, dynamic NPC depth, or broader
walkability.
