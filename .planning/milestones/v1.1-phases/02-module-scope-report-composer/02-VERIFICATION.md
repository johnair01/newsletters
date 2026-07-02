---
phase: 02-module-scope-report-composer
verified: 2026-07-02T21:30:00Z
status: passed
score: 4/4 must-haves verified
---

# Phase 2: Module-scope Report composer Verification Report

Retroactive verification (2026-07-02). Evidence: PR #5 body (squash merge `22396ce` — "compose.py:
kind-agnostic composer over SectionBinding[] … 605 tests; all enforced gates green; CI green") +
02-0X-SUMMARY §Gate-Results sections (02-01 592, 02-02 592, 02-03 592, 02-04 605) + fresh gate re-run
on current HEAD `1e3f1bc654cf898a07e7ce344e6254ca52665cec` (branch `loop/2026-07-02-deep-review`).

**Phase Goal:** Given traced bindings, the composer assembles one `Surface(REPORT, Draft)` per module
— per-lane KPI strip (Δ at compose time) + traced claims, honest `missing[]` routing, stable `R-NNN`
— selecting/ordering/linking traced material only, never authoring facts.
**Verified:** 2026-07-02
**Status:** passed

> **Scope note (verification target = CURRENT merged HEAD, not the plan-time snapshot).** The live
> composer verified here is the state AFTER two mid-phase orchestrator fixes that reshaped the Δ
> disclosure contract (`4031af1` on `compose.py`, `efb635a` on `swimlane.py`). Those two commits are
> the ontological story of this phase; they are told in `02-LEARNINGS.md` and summarized under
> "The Δ-contract drift" below. Everything asserted here is what runs on HEAD today.

## The Δ-contract drift (the phase's story, verified on HEAD)

The disclosure rule for a KPI's movement passed through three forms; HEAD is the third:

1. **Silent** (02-02 `3a51bf0`): "a single (or zero) endpoint → point-in-time value, NO note."
   Combined with 02-01's binding (where a `value:` KPI carried **one** endpoint reference), a
   genuinely-declared-but-single `values:` movement could go deltaless with **no disclosure**.
2. **Over-disclosing** (`4031af1`): added "exactly 1 endpoint → declared movement, only one endpoint
   usable → `missing[]` note" (COMP-02 letter). But because a point-in-time `value:` KPI *still*
   carried one endpoint, **every** point-in-time KPI now fired a FALSE "declares period movement"
   note. Over-firing honesty is itself unfaithful.
3. **Movement-form-only** (`efb635a`, the semantic resolution): moved the fix into the loader — a
   `value:` KPI contributes **zero** endpoints; only a `values:` list pairs endpoints. Now
   `0 endpoints` = point-in-time (no note), `1 endpoint` = a real declared-but-single movement (note
   fires correctly). Disclosure tracks *declared-but-unmet promises*, not the absence of a promise.

Verified live on HEAD (direct composer drive): a KPI item with `kpi_endpoints=[[]]` (loader's
point-in-time shape) emits **no** movement note and `delta=None`; a KPI item with a single-element
endpoint list emits `"KPI 'M' declares period movement but only one endpoint is usable …"`. Both
arms behave as the movement-form-only contract requires.

## Goal Achievement

### Observable Truths

The four ROADMAP Phase-2 success criteria, each mapped goal-backward to the test/evidence proving it
on current HEAD.

| # | Truth (ROADMAP success criterion) | Status | Evidence (test on HEAD) |
|---|-------|--------|----------|
| 1 | One `Surface(REPORT)` from an arbitrary lane set via a kind-agnostic `SectionBinding` seam (per section: `KpiStripBlock` + `ClaimsBlock`); a second/other kind slots in with zero composer change | ✓ VERIFIED | `test_kind_agnostic_seam_second_kind` composes a NON-lane "risk register" `SectionBinding` into a valid Draft REPORT with zero composer change; its traced finding survives onto a `ClaimsBlock`, no `KpiStripBlock`, omission disclosed. `compose_module_report` iterates `load.bindings` as generic sections in file order (compose.py:340-366). |
| 2 | Δ from one pure `compute_delta(start, close)` over two independently content-addressed endpoints into `KpiItem.delta`; reproducibility recomputes every rendered delta byte-equal; either endpoint absent → `delta=None`/`dir=None` + `missing[]` note, never a fabricated `0`; no `Kpi` start/baseline field | ✓ VERIFIED | `test_every_rendered_delta_recomputes_byte_equal` recomputes each rendered delta AND dir from the two paired endpoints; exercises all three arms (real movement, point-in-time no-delta, Δ==0 → dir=None + computed zero). `compute_delta` is pure (compose.py:108-146). `models.py` byte-unchanged this phase (Δ lives only in `KpiItem.delta`/`.dir`). |
| 3 | A test fails if the composer emits any zero-trace or un-content-addressed claim (Hole B), and a numeral-free-prose guard fails on any un-sourced digit run in non-`ClaimsBlock` text (Hole A); `faithfulness.py`/`coverage.py` untouched | ✓ VERIFIED | Hole B: `test_every_claimsblock_claim_is_traced_and_addressed` (positive) + `test_untraced_and_unaddressed_claims_are_routed_to_missing` (planted zero-trace AND planted un-addressed both routed to `missing[]`, non-vacuous). Hole A: `test_authored_prose_is_numeral_free` (non-vacuous via a poisoned `ProseBlock("we shipped 42 features")`) + `test_kpi_numbers_are_sourced_to_endpoints` (the only out-of-claim numerals are KPI value/delta traceable to a content-addressed close endpoint). Gate-untouched: `test_faithfulness_coverage_semantic_templates_site_are_untouched` (`git diff --exit-code`). |
| 4 | Stable `R-NNN` from `Ledger.ref_for` against its own `content/module/ids.json`; lands `Draft` with an owner/manager quote slot + a `fanout` stub; a no-auto-publish test proves it cannot reach `Published` without the gate | ✓ VERIFIED | R-NNN via reused `site.Ledger.ref_for` keyed by the surface slug (compose.py:322-325); no inline ref format. `test_unowned_and_sourced_quote_honesty` proves sourced-or-omit (omit+disclose / verbatim-from-traced-claim / "unassigned" for unowned). `_fanout_stub` always present, every `href=None`. `test_no_auto_publish_on_the_composed_surface`: gate is Draft; `publish()` raises and leaves Draft; a direct `Review(state=PUBLISHED, …)` raises via the model validator. |

**Score:** 4/4 truths verified

### Research-Hole Closure (verified by the exact tests TODAY)

The two research holes this phase owned are closed at the composer by named, non-vacuous tests on HEAD:

| Hole | Description | Closing test(s) on HEAD | Non-vacuity proof |
|------|-------------|-------------------------|-------------------|
| **A** (non-`ClaimsBlock` content ungated) | Authored/derived numerals outside a traced claim | `test_authored_prose_is_numeral_free` + `test_kpi_numbers_are_sourced_to_endpoints` | A poisoned `ProseBlock("we shipped 42 features")` is caught (`"42"` appears in the authored digit runs); the only allow-listed out-of-claim numerals are `KpiItem.value`/`.delta`, each checked traceable to a content-addressed close endpoint |
| **B** (un-addressed trace free pass) | A claim with zero traces, or a trace with `is_addressed == False`, surviving onto a block | `test_every_claimsblock_claim_is_traced_and_addressed` + `test_untraced_and_unaddressed_claims_are_routed_to_missing` | A planted zero-evidence `Claim` AND a planted `Trace(source_id=…)` with no `content_hash` (`is_addressed False`) are both proven routed to `missing[]`, not left on a `ClaimsBlock` |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/compose.py` | New composer: pure `compute_delta` + `compose_module_report` | ✓ EXISTS + SUBSTANTIVE | 396 lines. `compute_delta` (Decimal + single regex, undefined-as-first-class), `compose_module_report` (kind-agnostic seam, traced-or-missing routing, `created=EPOCH_ZERO`, sourced-or-omit quote, fanout stub, ledger ref). AI-free / yaml-free; imports only `semantic`/`swimlane`/`templates`/`site`/`adapters._timestamps` + stdlib. |
| `src/newsletters/swimlane.py` (additive) | `SectionBinding.kpi_endpoints` reference-only pairing | ✓ EXISTS + SUBSTANTIVE | `kpi_endpoints: list[list[Claim]]` (default_factory) 1:1 with `kpi_items`; populated by reference in `_bind_kpis` (movement `values:` form only after `efb635a`). `models.py`/`semantic.py` untouched. |
| `tests/test_compose.py` | Trust-guard proof suite over the live composer | ✓ EXISTS + SUBSTANTIVE | 13 tests, in-memory hand-built bindings via a forward-only `_Cursor` minter; Holes A+B, Δ reproducibility, determinism, no-auto-publish, seam, edge cases, gate-untouched. |
| `tests/test_swimlane_endpoints.py` | Endpoint-pairing invariant proof (02-01) | ✓ EXISTS + SUBSTANTIVE | 5 tests over both committed fixtures: alignment, reference-not-re-mint (object identity), coverage-identity-unaffected, ordering, no-fabricated-endpoint (trap mapping-shaped `values:`). |
| `content/module/ids.json` | (Deferred to Phase 3) module ledger | ⛔ NOT CREATED (by design) | Compose is disk-write-free; the caller (Phase 3) owns `Ledger.load → save()`. Consistent with 02-03 plan. |

**Artifacts:** 4/4 in-scope artifacts verified (the ledger file is intentionally deferred).

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `compose_module_report` | `KpiItem.delta` / `.dir` | `compute_delta` over paired `kpi_endpoints` | ✓ WIRED | compose.py:212-226 — Δ only when both endpoints content-addressed AND numeric |
| `compose_module_report` | `Surface.created` | explicit `EPOCH_ZERO` (never `now()`) | ✓ WIRED | compose.py:394 — the confirmed determinism trap avoided |
| `compose_module_report` | `site.Ledger.ref_for` | reuse, append-only, keyed by surface slug | ✓ WIRED | compose.py:322-325 — sole ref source, no inline format, no `save()` |
| `_bind_kpis` | `SectionBinding.kpi_endpoints` | by-reference, movement (`values:`) form only | ✓ WIRED | swimlane.py:373-405 — `value:` contributes 0 refs (efb635a); lockstep with `kpi_items` |

**Wiring:** 4/4 connections verified

## Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| COMP-01: kind-agnostic `SectionBinding` seam → per-section `KpiStripBlock` + `ClaimsBlock` | ✓ SATISFIED | - |
| COMP-02: pure `compute_delta` from two content-addressed endpoints; reproducible; never a fabricated 0 | ✓ SATISFIED | - |
| COMP-03: Hole B + Hole A closed by new guards; `faithfulness.py`/`coverage.py` untouched | ✓ SATISFIED | - |
| COMP-04: stable `R-NNN` via reused ledger; Draft; quote slot; fanout stub; no-auto-publish | ✓ SATISFIED | - |

**Coverage:** 4/4 requirements satisfied

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/newsletters/swimlane.py` | 131-141 (`SectionBinding` docstring), ~330 (`_bind_kpis` docstring) | Stale docstring: "one entry for a single `value:` KPI" contradicts the `efb635a` movement-form-only behavior (`value:` → 0 endpoints) | ℹ️ Info | Already recorded in Round 1's `01-VERIFICATION.md` Anti-Patterns; not re-litigated here. Documentation-only; runtime is correct. |
| `tests/test_compose.py` | 127-128, `_build_load` | Test-fixture semantic drift (NEW this round): the "Team size" and "Throughput" KPIs model a *point-in-time* KPI as a **one-element** endpoint list (`[[c_6]]`, `[[v_alpha]]`), but the LIVE loader emits a point-in-time `value:` KPI as **zero** endpoints. Under HEAD semantics a one-element list fires the "declares period movement but only one endpoint is usable" note — so the fixture comment "one endpoint → point-in-time, no delta" describes pre-`efb635a` behavior. Tests still pass (none asserts the note's absence). | ⚠️ Warning (test only) | The compose-level **zero-endpoint arm** (the exact faithful path `efb635a` established: `value:` → 0 endpoints → no false note) is not directly exercised by `test_compose.py`. It is verified structurally + by live drive in this report and proven at the loader level by `test_swimlane_endpoints`, but a compose-level guard would pin it. Recommend one "prove-it" guard test (a `kpi_endpoints=[[]]` item asserts no movement note). Loop reviews, does not refactor. |

**Anti-patterns:** 2 found (0 blockers, 1 warning, 1 info)

## Human Verification Required

None — all four success criteria are verifiable programmatically and were re-run fresh on HEAD.

## Gaps Summary

**No goal gaps.** All four COMP requirements achieved on current merged HEAD. One test-side warning
(the zero-endpoint compose arm lacks a direct guard; the fixture's "point-in-time" shape drifted from
the loader's actual emission) is logged for a future guard test. See `02-VALIDATION.md` for the full
validation-coverage edge list.

## Fresh Gate Re-Run (verbatim tails, HEAD 1e3f1bc)

```
$ .venv/bin/pytest tests/test_compose.py tests/test_swimlane_endpoints.py -q
..................                                                       [100%]
18 passed in 0.08s
```

```
$ .venv/bin/pytest -q
........................................................................ [ 69%]
........................................................................ [ 80%]
........................................................................ [ 92%]
...............................................                          [100%]
623 passed in 12.15s
```

```
$ .venv/bin/lint-imports
------------------------------------

Core (newsletters) must not import any AI/LLM package KEPT
problem.py must not import any network/external-system package KEPT

Contracts: 2 kept, 0 broken.
```

Full-suite count is 623 on HEAD (Phases 2–4 all merged); the 13 compose + 5 endpoint guards verified
above are inside the green 623. At PR #5 merge the count was 605 (per `22396ce`).

## Verification Metadata

**Verification approach:** Goal-backward (4 ROADMAP success criteria) + research-hole closure audit +
artifact/wiring/requirement audit + git-history reconstruction of the Δ-contract drift.
**Must-haves source:** `.planning/ROADMAP.md` Phase 2 success criteria.
**Automated checks:** targeted pytest (18), full suite (623), lint-imports (2 kept 0 broken) — all
green; plus a live composer drive confirming the zero- vs one-endpoint disclosure arms.
**Human checks required:** 0.
**Total verification time:** ~40 min (paper trail + live code + git history + fresh gates).

---
*Verified: 2026-07-02*
*Verifier: Claude (Bureau Chief, deep-review loop Round 2 — retroactive)*
