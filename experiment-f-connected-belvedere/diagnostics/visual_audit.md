# Experiment F — Visual Audit

## Verdict

**Environment pass; cross-node character integration partial; physical
continuity deliberately unproven.**

## Findings

- **Source-video relationship: pass.** The new node preserves the overlook
  composition's defining semantics: paved belvedere, low parapet, layered green
  valley, distant church/fields, terracotta roofs, and a right-side bell tower.
  It removes the source HUD, prompt, birds, and protagonist as requested.
- **Playable-floor readability: pass.** The terrace is unusually easy to read.
  The cyan geometry stays on visible ground, the tested loop stays mainly on
  stone paving, and the parapet provides an unambiguous front boundary.
- **Piazza style continuity: partial/pass.** Warm limestone, terracotta, pixel
  treatment, and atmospheric mountain depth belong to the same broad visual
  language. The belvedere is brighter and greener (mean luminance 126.5 versus
  107.5) because far more of the frame is sky/valley; that telemetry is
  descriptive, not proof of identity.
- **Traveler scale: partial.** The inherited 48×64 atlas renders only a roughly
  25×52 opaque traveler in the capture. It reads clearly but visibly small
  against the terrace blocks and much smaller than the overlook protagonist in
  the source frame. Experiment E's scale residual becomes more obvious here.
- **Portal semantics: functional pass, spatial nonclaim.** The transition is a
  tested authored travel link between two source compositions. The current
  piazza painting does not visually prove that its east endpoint is physically
  adjacent to this belvedere.
- **Depth/occlusion: no new claim.** The belvedere intentionally has no new
  foreground extraction. The parapet blocks player feet through collision; the
  player does not pass behind it.

## Consequence

A reusable node contract needs an explicit character-to-environment scale
check, not only fixed sprite pixels. The next content-scaling run should either
generate scenes against a locked player-height guide or declare a per-node
sprite scale and validate it visually. This is a new cross-node issue; it does
not invalidate the round-trip traversal result.
