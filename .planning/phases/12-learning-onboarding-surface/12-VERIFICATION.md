---
phase: 12-learning-onboarding-surface
verified: 2026-06-19T06:05:30Z
status: passed
score: 3/3 success criteria verified
overrides_applied: 0
re_verification:
  previous_status: none
notes:
  - "Phase has `mode: mvp` in ROADMAP.md but the goal is a capability statement, NOT a User
     Story (`As a …, I want to …, so that …`). Per references/verify-mvp-mode.md this is a
     framing discrepancy (run /gsd mvp-phase 12 to reformat). It does NOT affect goal
     achievement: the 3 LEARN Success Criteria are the contract and are all verified below.
     Recorded as informational, not a gap."
---

# Phase 12: Learning & Onboarding Surface — Verification Report

**Phase Goal:** Add a first-class learning/onboarding surface that re-cuts reviewed records for
newcomers and training-program participants — progressive disclosure, traceable concepts, and
ordered onboarding paths — making org/codebase knowledge digestible to people new to it.
**Verified:** 2026-06-19T06:05:30Z
**Status:** passed
**Re-verification:** No — initial verification
**Branch:** claude/youthful-fermi-dly6mi (read-only verification; no source modified)

## The Central Judgment — FAITHFULNESS (the crux)

**Finding: NO invented prose. The learning re-cut SELECTS / ORDERS / LINKS existing traced
reviewed claims and never authors new factual content. PROVEN at three independent layers.**

1. **Type-level guard (construction time).** `GlossaryTerm.definition` is a `Claim`, never a
   `str` (`semantic.py:432-433`). Live probe: `GlossaryTerm(term='Flux', definition='…str…')`
   raises `ValidationError`; only a traced `Claim` is accepted. A glossary definition therefore
   *cannot* be fabricated prose — it is structurally forced to be a reviewed claim carrying
   `evidence: list[Trace]`.

2. **Preset-level selection (live build).** Built `dogfood.build_surfaces()` and asserted every
   string on `learning-datamodel` against the source record's traced claim set:
   - `learning_surface()` emits ONLY `ClaimsBlock` + one `GlossaryBlock` — no `ProseBlock` body
     (`learning.py:143-167`). Claims come straight from `distillation.claims_for(audience)`
     (`learning.py:130`); the layer routing (`_layer_for`, `learning.py:60-76`) only *reorders*
     by `confidence` + `topics`, it authors nothing.
   - **Probe result: `VIOLATIONS: NONE` — every rendered claim is a member of the source record's
     6 traced claims, and every one `is_traced`.**
   - The HTML carries 9 verbatim addressed spans (`claim-span`) and 9 provenance `ev-chip`s
     (e.g. `session-datamodel:layers`), each lifted verbatim from the source claim.

3. **Honesty routing (un-glossable → missing[], never fabricated).** The dogfood requests 6
   glossary terms (`dogfood.py:655`). 3 resolve to DEFINING traced claims (`Report`, `Article`,
   `capture`); 3 have no traceable defining claim (`Distillation`, `Surface`, `the review gate`)
   and are routed to `surface.missing[]` (`learning.py:152-174`) — surfaced in the honesty panel,
   **never invented**. Confirmed in built HTML:
   `Glossary term 'Distillation' has no traceable defining claim` (+ Surface, + the review gate).
   `_defines()` (`learning.py:79-96`) refuses to gloss a term that is merely mentioned — it
   requires a copula ("is/are/means/refers to"), so a term lands in `missing[]` rather than being
   mis-glossed from an incidental mention.

**No rendered string on the learning surface was found that is not a traced reviewed claim.**

## Goal Achievement — Observable Truths (Success Criteria)

| # | Truth (ROADMAP SC) | Status | Evidence |
| - | ------------------ | ------ | -------- |
| 1 | LEARN-01: a Learning preset re-cuts a reviewed record for a newcomer — progressive disclosure, prerequisite context, in-context glossary | ✓ VERIFIED | `learning_surface()` (`learning.py:99-189`) emits ordered sections **Start here / Prerequisites / Going deeper** (built HTML headings confirmed), an in-context typed `GlossaryBlock`, and carries prerequisite slug refs (`prerequisites=["show-ep01","report-datamodel"]`, `dogfood.py:703`) as links via `Lineage.derived_from`. Live state = `draft`, template = `learning`, distance = 4. L-001 ref assigned in `content/rev1/ids.json:11`; shown in the Library Draft column (`library.html`). |
| 2 | LEARN-02: every concept links back to its source record/claim (explanation → evidence) | ✓ VERIFIED | Pure reuse of the Phase 9-11 devices (`link_for_source`, `_claim_spans`, `_claim_badge`, `_honesty_panel`) on the learning surface (`render.py:508-545`). Built HTML: all 9 claims (6 section + 3 glossary defs) render a verbatim addressed span + a provenance `ev-chip` tracing to a real `Source` (`session-datamodel:*`). See provenance note below re: link form. |
| 3 | LEARN-03: an onboarding path sequences multiple records into an ordered learning track | ✓ VERIFIED | `OnboardingPath`/`OnboardingStep` (`learning.py:197-221`) + `render_path()` (`render.py:985-1054`). Built `onboarding-newcomer.html` renders the ordered track **show-ep01 → report-datamodel → learning-datamodel** with numbered steps and in-track prev/next (first-no-prev, last-no-next). No dead/empty hrefs; unresolved steps degrade to plain text (`render.py:1016-1018`). |

**Score:** 3/3 success criteria verified.

## LEARN-02 Provenance — Detail

Every concept/glossary term/step renders `link_for_source` provenance. In the dogfood corpus the
chosen record (`report-datamodel`) carries **session-locator** traces (`source_id=session-datamodel`,
locator `layers`/`templates`/…), not file-path locators. Per `link_for_source`'s SITE-05 rule
(`render.py:73-100`): file-path → repo blob URL; session/transcript → in-site anchor via
`site.by_slug(source_id)`, else **plain text (no dead link)**. Since `session-datamodel` maps to no
page slug, the provenance correctly renders as plain-text `ev-chip` spans (`session-datamodel:layers`)
— **identical behavior to the parent `report-datamodel` surface, which also renders 0 linked chips.**
This is faithful (every concept shows its traced source; no fabricated/dead link), and is a property
of the source data, not a learning-surface defect. The *mechanism* for a clickable `link_for_source →
repo file` is present and exercised across the site; a future record with file-path locators would
render clickable repo links with no code change.

## LEARN-03 Ordered Path — Confirmation

Built `onboarding-newcomer.html` step hrefs in document order: `show-ep01.html` → `report-datamodel.html`
→ `learning-datamodel.html` (matches authored order, `dogfood.py:720-722`). prev/next present within the
track; no `href=""` / `href="#"`; the only `<script>` is the site-wide theme toggle (363 bytes, no
disclosure JS) — progressive disclosure is ordered DOM, not interactive JS. The path is navigation
over already-gated surfaces (no own claims, no review gate, A5); it is surfaced as a callout ABOVE the
Library board, not as a gate-state column.

## Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `src/newsletters/learning.py` | learning_surface() + OnboardingPath/Step | ✓ VERIFIED | 222 lines; faithful select/order/link; AI-free imports |
| `src/newsletters/templates.py` | LEARNING template, distance 4, registered | ✓ VERIFIED | `LEARNING` (`templates.py:160-171`); in `_REGISTRY` (`:178-179`) |
| `src/newsletters/semantic.py` | typed `GlossaryBlock`/`GlossaryTerm`, in Block union | ✓ VERIFIED | `GlossaryTerm.definition: Claim` (`:421-433`); `GlossaryBlock` (`:436-446`); union (`:461`) |
| `src/newsletters/render.py` | GlossaryBlock branch + render_path() | ✓ VERIFIED | glossary branch (`:541-545`); `render_path` (`:985-1054`) |
| `src/newsletters/dogfood.py` | real re-cut + onboarding path + build | ✓ VERIFIED | `_learning_recut` (`:680-705`), `_onboarding_path` (`:708-724`), wired into `build_site` |
| `content/rev1/site/learning-datamodel.html` | built faithful learning surface | ✓ VERIFIED | 9 traced claims, honesty panel, byte-stable |
| `content/rev1/site/onboarding-newcomer.html` | built ordered track | ✓ VERIFIED | ordered + prev/next, no dead href |
| `content/rev1/site/library.html` | L-001 in Draft column + track callout | ✓ VERIFIED | L-001 present, learning in Draft, onboarding callout |
| `tests/test_learning.py` | faithfulness + LEARN-02/03 tests | ✓ VERIFIED | 22 tests pass |
| `docs/surfaces.md` | Learning + OnboardingPath spec section | ✓ VERIFIED | §"Learning" (`:119`), §OnboardingPath (`:163`), `L-NNN` row (`:235`) |

## Behavioral Spot-Checks (live probes)

| Behavior | Command / Probe | Result | Status |
| -------- | --------------- | ------ | ------ |
| str glossary definition rejected | `GlossaryTerm(definition='str')` | `ValidationError` | ✓ PASS |
| Claim glossary definition accepted, traced | `GlossaryTerm(definition=Claim)` | `is_traced=True` | ✓ PASS |
| every rendered claim ∈ source traced set | build_surfaces + set membership | `VIOLATIONS: NONE` | ✓ PASS |
| un-glossable term → missing[] | live | 3 terms in missing[], not glossed | ✓ PASS |
| no-auto-publish: Draft exempt | `review_blockers(draft)` | `[]` | ✓ PASS |
| no-auto-publish: published → blocked | `publish()` then `review_blockers` | 3× `OPEN_MISSING` | ✓ PASS |
| onboarding path ordered | href order in built HTML | show-ep01 → report-datamodel → learning-datamodel | ✓ PASS |
| no dead hrefs in track | grep `href=""`/`href="#"` | none | ✓ PASS |

## Gate Results (actual output)

| Gate | Command | Result |
| ---- | ------- | ------ |
| Tests (full) | `.venv/bin/python -m pytest -q` | **559 passed, 1 xfailed** |
| Tests (learning) | `pytest tests/test_learning.py -q` | **22 passed** |
| Types | `.venv/bin/mypy src/newsletters` | **9 errors** — all in `capture.py` + `dogfood.py` (pre-existing baseline); **0 in learning.py/render.py/templates.py/semantic.py** (Phase 12 source). No NEW errors. |
| Imports | `.venv/bin/lint-imports` | **1 kept, 0 broken** — "Core must not import any AI/LLM package KEPT" |
| Build | `.venv/bin/newsletters build` | rendered 12 surfaces + library; **byte-stable** (`git diff content/rev1/` empty after rebuild) |
| Check | `.venv/bin/newsletters check` | **exit 0** — "All published surfaces clean — no blockers" (Draft learning surface gate-exempt) |
| External calls | grep `https?://` in built learning/onboarding HTML | **none** (self-hosted fonts) |

## Hard-Rule Status

| Hard Rule | Status | Evidence |
| --------- | ------ | -------- |
| Faithful, not suggestive (THE crux) | ✓ HOLDS | No invented prose — proven 3 ways (type guard, set-membership probe, honesty routing). |
| Every published claim traces to evidence (LEARN-02) | ✓ HOLDS | All 9 concepts render a verbatim span + traced source ref; un-traceable → missing[]. |
| No auto-publish / gate intact | ✓ HOLDS | Surface left Draft; `publish()` would raise 3× OPEN_MISSING via `review_blockers`; `newsletters check` exit 0. |
| AI-optional core | ✓ HOLDS | `learning.py` imports only stdlib + pydantic + `.semantic`/`.templates`; lint-imports contract kept. |
| No external calls | ✓ HOLDS | No `http(s)://` in built HTML; self-hosted fonts. |
| Determinism / byte-stable (SITE-06) | ✓ HOLDS | Rebuild produces zero git diff. |
| Specs are source of truth | ✓ HOLDS | docs/surfaces.md Learning + OnboardingPath spec sections added (spec gap filled). |

## Anti-Patterns Found

| File | Pattern | Severity | Impact |
| ---- | ------- | -------- | ------ |
| (none) | TBD/FIXME/XXX scan of learning.py/templates.py/render.py/test_learning.py | — | No debt markers found |

## Skeptical Scope Findings

- **Does any section/glossary render a definition or sentence that isn't a traced claim?** No.
  Set-membership probe returned `VIOLATIONS: NONE`; glossary defs are `Claim`s by type; no
  `ProseBlock` body is emitted.
- **Is the onboarding path truly ordered + traced (each step a real surface)?** Yes. Three steps
  resolve to real `{slug}.html` pages in authored order with prev/next; the third (`learning-datamodel`)
  is itself the Phase-12 surface, closing the loop.
- **Going deeper layer absent on the dogfood surface** — all 6 claims routed to Start here /
  Prerequisites (none matched the deep-topic set or fell below the confidence floor). This is
  correct behavior (only non-empty layers are emitted, `learning.py:144-147`), not a defect; the
  three-layer mechanism is present and exercised by tests.

## Human Verification

None required for goal achievement — all 3 Success Criteria are programmatically verified against
live code and built output. (Optional, informational: visual fidelity of the learning/track pages
against the design system is a standard human eyeball check, but is not load-bearing for the goal.)

## Gaps Summary

No gaps. All 3 Success Criteria (LEARN-01/02/03) are achieved in live code and built output. The
faithfulness crux — the load-bearing risk of this phase — is decisively satisfied: the teaching
surface never invents prose, every concept traces to a reviewed claim, and un-glossable terms are
shown honestly rather than fabricated. The no-auto-publish invariant is preserved and proven (the
surface ships as a Draft precisely because it has open missing[]). One informational note: the phase
is tagged `mode: mvp` but its ROADMAP goal is not in User-Story format — a framing discrepancy, not
a goal failure.

---

_Verified: 2026-06-19T06:05:30Z_
_Verifier: Claude (gsd-verifier)_
