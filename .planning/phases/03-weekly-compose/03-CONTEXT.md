# Phase 3: Weekly compose - Context

**Gathered:** 2026-08-29
**Status:** Ready for planning
**Mode:** Auto-generated (discuss skipped via workflow.skip_discuss; the ONE milestone
discussion round already happened — decisions below are binding)

<domain>
## Phase Boundary

A weekly `Surface(REPORT, Draft)` composes from authored voice plus adapter evidence — the four
new block kinds join the typed `Block` union, the **Weekly Spec** YAML path lifts authored
material through the Case Spec mechanism (author's narrative byte-verbatim with real-span
traces), assets enter only as content-addressed records meeting the provenance minimum, and BI
values arrive via the existing ADAPT-03 excel adapter fed exports. The composer assembles and
traces; it never editorializes. Requirements: WKLY-02, WKLY-03, WKLY-04. Full success criteria:
`.planning/ROADMAP.md` Phase 3 (5 criteria). **The spec is already written** — `docs/weekly-spec.md`
is the contract (eight-key schema, seven loader rules, block kinds field-by-field, AssetRecord +
four-condition missing[] routing incl. the WR-07 rows); implement it, don't re-design it.

</domain>

<decisions>
## Implementation Decisions

**Binding (recorded, no reopening):**
1. Reuse `Surface(REPORT)` (D-01) — no new kind; blocks join the existing discriminated union.
2. Provenance minimum = folder + date + event label; deep link REQUIRED only for a BI screenshot
   standing in for values (D-02). `AssetBlock.asset` required; `AssetBlock.evidence`
   min_length=1 — provenance-less placement unrepresentable, not policed.
3. Named placeholders / NL_ prefix contract (D-03) — the composer produces the `slots` mapping
   for Phase 2's `render_surface_pptx` explicit-slots API.
4. Faithful-not-suggestive: narrative byte-verbatim (Case Spec block-scalar mechanism);
   `config:` bound never claimed; absences → `missing[]` with the spec's named reasons;
   planted-editorialization guard test (v1.1 planted-cheat precedent).
5. **Close the render fall-through**: every new block kind gets an HTML render branch using
   existing design-system tokens, AND the `return ""` fall-through at the end of `_block_html`
   becomes fail-loud so an unrecognized block can never again be silently droppable (ROADMAP
   SC-1; the fall-through is unreachable today — keep it that way by construction).

**Claude's discretion** (decide per recorded reasoning, log): module layout (e.g.
`weeklyspec.py` beside `casespec.py`; a small `assets.py` if warranted), exact compose entry
point name, how the weekly composer reuses `compose.py`'s KPI-strip/claims machinery.

</decisions>

<code_context>
## Existing Code Insights

- `src/newsletters/casespec.py` — THE mechanism to extend: raw YAML → content-addressed Source →
  real-span `Trace.from_source` → typed blocks; `config:` binding; `missing[]` disclosure.
- `src/newsletters/compose.py` + `swimlane.py` — the module composer (KPI strip + claims) the
  weekly extends; `SectionBinding` seam.
- `src/newsletters/semantic.py` — the `Block` union (~semantic.py:449); Surface; review gate
  (BYTE-UNCHANGED except the sanctioned union addition — check whether the union lives in
  semantic.py; if adding members requires touching semantic.py, that IS sanctioned this phase
  per the ROADMAP, but the GATE code (`Review`, `advance`, publish path) must not change —
  prove with targeted diff/tests, since the blanket byte-unchanged gate no longer applies).
- `src/newsletters/render.py` — `_block_html` dispatch (fall-through at end); design tokens in
  `_CSS`.
- `src/newsletters/adapters/excel_adapter.py` — ADAPT-03, values-via-export feeds this untouched.
- `src/newsletters/pptx_writer.py` — Phase 2's explicit-slots renderer the composed weekly must
  render through (ROADMAP SC-5: byte-identical double-compose, renders to a deck satisfying the
  recorded determinism definition).
- `docs/weekly-spec.md` — the contract. `docs/design-system.md` — token authority.

</code_context>

<specifics>
## Specific Ideas

- Compose twice → byte-identical Surface (`created=EPOCH_ZERO`, sorted inputs, stable ids), never
  advanced past Draft.
- ADAPT-05 (`adapters/powerbi*`) unchanged — clean-diff gate.
- No new adapter module (WKLY-04): values enter through ADAPT-03 outputs.
- UI hint (roadmap): new blocks render into the existing HTML surface under design-system
  tokens; NO web/ work.

</specifics>

<deferred>
## Deferred Ideas

Sample corpus + operator recipe are Phase 4's. Carried Phase-2 items (template regeneration,
fixture delegation, layout-walk contract) stay Phase 4/PR items.

</deferred>
