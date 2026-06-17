---
phase: 03-content-addressed-provenance-faithfulness
verified: 2026-06-17T13:58:44Z
status: human_needed
score: 3/3 success criteria verified
overrides_applied: 0
human_verification:
  - test: "Confirm the Option-A scope boundary is the intended product semantics: the strict span-containment gate has teeth ONLY on content-addressed traces, and the live capture path (capture.py) still emits un-addressed empty-span traces that receive the structural (is-traced) pass."
    expected: "Reviewer accepts that for THIS phase, criterion 2's strict entailment is satisfied for content-addressed evidence (the migrated sample corpus + any future Trace.from_source path), and that content-addressing the live capture path is intentionally deferred to a later phase (it is not a Phase-3 success criterion)."
    why_human: "This is a product/scope judgment about how much of the pipeline must be under the strict gate. The code correctly implements the resolved Option A; whether Option A's coverage is sufficient for the milestone is a human decision, not a programmatic one."
---

# Phase 3: Content-Addressed Provenance & Faithfulness Gate — Verification Report

**Phase Goal:** Make traces resistant to source drift and make unfaithful claims structurally unable to pass as audited — content-address every trace; enforce entailment at the socket boundary for all backends.
**Verified:** 2026-06-17T13:58:44Z
**Status:** human_needed (all three success criteria VERIFIED in code; one scope-adequacy judgment surfaced for the reviewer)
**Re-verification:** No — initial verification
**Requirements:** PROV-01, PROV-02

## Goal Achievement

### Success Criteria (the ROADMAP contract)

| # | Criterion | Status | Evidence |
| - | --------- | ------ | -------- |
| 1 | Every claim's Trace is content-addressed (hash + offset + verbatim span), not positional; editing a source flips dependent claims to STALE | VERIFIED | `semantic.py:58` `Source.content_hash` (SHA-256 of full transcript); `:86-95` optional `content_hash/start/end`; `:109-153` `Trace.from_source` pins hash+offsets+`span=transcript[start:end]` with offset validation; `:160-167` `is_stale_against` = `is_addressed and live_hash != recorded`; `:182-194` `Claim.is_stale`; `:293-302` `Distillation.stale_claims`. Behavioral check (a): a content-addressed trace went `stale=False`→`True` after the source transcript changed; an un-addressed trace stayed `False`. |
| 2 | A faithfulness gate verifies each emitted claim is entailed by its traced evidence span, deterministic span-containment in no-AI mode | VERIFIED (scoped per Option A) | `distill/faithfulness.py:42-50` `_normalize` (casefold + whitespace-collapse on transient copies); `:53-74` `SpanContainmentFaithfulness.entails` — content-addressed trace ⇒ strict normalized containment; `ports.py:95-131` `_enforce` defaults to span-containment (lazy import) and raises on the first unfaithful claim; `conformance.py:38-94` `assert_conforms` routes faithfulness through the single `_enforce` seam so **every** backend inherits it. Behavioral check (b): content-addressed claim "omega" against span "beta" → `entails=False`, `_enforce` raised. |
| 3 | A claim whose text cannot be located in or entailed by its own trace is routed to `missing[]`, never surfaced as a fact | VERIFIED | `distill/faithfulness.py:77-107` `route_unfaithful_to_missing` keeps only entailed claims, appends each failing claim's `text` VERBATIM to `missing[]`, rebuilds via `model_copy` (no in-place mutation). Behavioral check (b): unfaithful "omega" moved to `missing[]`, faithful "beta" kept; original distillation + stored `claim.text`/`trace.span` unmutated. Untraced claim ⇒ never entailed (`:63-64`). |

**Score:** 3/3 success criteria verified in code.

### The Option-A Adequacy Judgment (the key call)

**What the code does (verified, matches the resolved decision exactly):**
`SpanContainmentFaithfulness.entails` (`faithfulness.py:62-74`) returns True iff the claim has ≥1 trace AND either (a) some trace is **un-addressed** (`trace.is_addressed is False` → structural pass, span-containment N/A) OR (b) some **content-addressed** trace's normalized span contains the normalized claim text. A claim with no traces is never entailed. This mirrors the 03-01 STALE rule ("un-addressed ⇒ never a false positive"). `capture.py` was deliberately NOT modified — confirmed: `capture_session` (`capture.py:65-78`) still builds `Trace(source_id=..., locator=...)` with empty span and no content_hash, i.e. un-addressed traces.

**Is criterion 2 under-enforced because the live capture path produces un-addressed traces that get the structural pass?**
- **For content-addressed evidence: NO — fully enforced.** The strict containment gate is live and has teeth at the single socket seam (`_enforce`/`assert_conforms`), so every backend is covered. Behavioral check (b) and the 21 faithfulness-gate tests confirm a content-addressed non-containing span is rejected and routed to `missing[]`.
- **For the live capture path: PARTIALLY, by design.** `capture.py` emits un-addressed empty-span traces, which take the Option-A (a) structural pass — span-containment is a no-op there. So a claim minted via `capture_session` is checked only for being traced, not for entailment by its span. This is the correct faithful behavior (avoids false positives on evidence that was never content-addressed) but it does mean criterion 2's strict "entailed by its span" guarantee does **not yet** reach claims produced by the live capture pipeline.

**Where the gate is a no-op vs. where it should not be:**
- The gate is a no-op exactly where there is no content-addressed evidence to check (un-addressed traces). Given Option A, that is intended, not a defect.
- It is **not** a no-op anywhere it should have teeth: every content-addressed trace is strictly checked. The shipped sample corpus is the relevant real surface, and it IS under the strict gate (next paragraph).

**Is the published/sample corpus (which 03-02 content-addressed) fully under the strict gate?**
**YES.** Behavioral check (c) over `build_surfaces()`: report-kickoff (4), report-datamodel (6), report-rev1 (4), and article-semantic-spine (6, shares session-datamodel via promotion) carry **20 content-addressed traces**, all passing strict span-containment (0 gate failures), all `stale_claims()==[]` at build. The only un-addressed corpus claims are report-plan's 4 (structural roadmap locators, empty span) — correctly left un-addressed and passing via the structural fallback. So the part of the sample corpus that has verbatim evidence is fully under the strict gate; the part without verbatim spans is honestly outside it.

**Verdict on adequacy:** Option A adequately satisfies criteria 2 and 3 *as scoped for this phase*. Criteria 2/3 are about the gate existing, being deterministic, enforced at the boundary for all backends, and routing unfaithful claims to `missing[]` — all verified. There is a **real but bounded residual risk**: claims born on the live `capture.py` path are not yet under strict entailment because they are un-addressed. Closing that fully requires a later phase to content-address the live capture path (mint capture traces via `Trace.from_source` with real spans). That is **not** a Phase-3 success criterion (PROV-01/02 do not require migrating the live capture path), so it is a forward note, not a Phase-3 gap. Surfaced as the single human-verification item for an explicit scope decision.

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `src/newsletters/semantic.py` | content_hash, from_source, is_addressed, is_stale_against, Claim.is_stale, stale_claims | VERIFIED | All present and substantive (`:58, 109, 155, 160, 182, 293`); imported/used across distill + dogfood + tests. |
| `src/newsletters/distill/faithfulness.py` | SpanContainmentFaithfulness, route_unfaithful_to_missing, _normalize | VERIFIED | Present (`:42, 53, 77`); imports only `..semantic` + stdlib; wired as default at `_enforce`. |
| `src/newsletters/distill/ports.py` | _enforce default swapped to span-containment | VERIFIED | `:95-131` lazy default to `SpanContainmentFaithfulness`; injectable `check` preserved; `FaithfulnessCheck` `@runtime_checkable`. |
| `src/newsletters/distill/conformance.py` | assert_conforms routes faithfulness through _enforce | VERIFIED | `:86-87` calls `_enforce(result, check)`; default inherits span-containment for every backend. |
| `src/newsletters/distill/__init__.py` | barrel exports for the gate | VERIFIED | `:22, 38-40` exports `SpanContainmentFaithfulness`, `route_unfaithful_to_missing`. |
| `src/newsletters/dogfood.py` | _address_trace, address_corpus_traces, MigrationReport, _record_transcript, _address_report; corpus addressed at build | VERIFIED | `:67, 84, 115, 179, 190`; wired into `_sources_and_reports` (`:410-412`); 20 traces addressed, 0 stale at build. |
| `tests/test_provenance.py` | content-addressing/STALE tests | VERIFIED | 17 tests pass. |
| `tests/test_provenance_migration.py` | faithful migration tests | VERIFIED | 11 tests pass. |
| `tests/test_faithfulness_gate.py` | span-containment + routing tests | VERIFIED | 21 tests pass. |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `Trace.from_source` | `Source.content_hash` | pins hash at mint | WIRED | `semantic.py:150`. |
| `_enforce` | `SpanContainmentFaithfulness` | lazy default check | WIRED | `ports.py:119-122`; default applies when `check=None`. |
| `assert_conforms` | `_enforce` | single faithfulness seam | WIRED | `conformance.py:87`; every backend inherits. |
| `dogfood._address_report` | `Trace.from_source` (via `_address_trace`) | str.find + re-mint | WIRED | `dogfood.py:104-112`; corpus pinned at build. |
| `route_unfaithful_to_missing` | `Distillation.missing[]` | verbatim relocation | WIRED | `faithfulness.py:103`; behavioral check confirms. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Editing source flips content-addressed claim to STALE | python script over `Trace.from_source` + edited Source | `is_stale_against` False→True; un-addressed stays False | PASS |
| Content-addressed non-containing claim not entailed → missing[] | `route_unfaithful_to_missing` on "omega" vs span "beta" | "omega"→missing[], "beta" kept; `_enforce` raised; stored text/span unmutated | PASS |
| Migrated sample corpus: 0 stale, all addressed claims pass gate | `build_surfaces()` traversal | 20 addressed traces, 0 stale, 0 gate failures; report-plan 4 un-addressed (structural) | PASS |
| Un-addressed traced claim passes via structural fallback (Option A) | `entails` on empty-span trace claim | True; untraced claim False | PASS |
| No AI module loads importing distill/semantic | `import newsletters.distill; check sys.modules` | AI modules: NONE | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| PROV-01 | 03-01, 03-02 | Every claim's Trace is content-addressed (hash + offset), not positional | SATISFIED | content_hash/from_source/STALE in semantic.py; corpus migrated (20 traces); criterion 1 + checks (a),(c). |
| PROV-02 | 03-03 | Faithfulness gate verifies each emitted claim is entailed by its span; no-AI deterministic span-containment | SATISFIED (scoped per Option A) | SpanContainmentFaithfulness at the single seam; criterion 2/3 + checks (b),(c). Residual: live capture path un-addressed (forward note, not a PROV-02 requirement). |

### Gate Results (re-run independently via .venv/bin/python — ACTUAL output)

| Gate | Command | Result |
| ---- | ------- | ------ |
| Full test suite | `.venv/bin/python -m pytest -q` | **85 passed, 1 xfailed** |
| Type check (phase scope) | `mypy src/newsletters/semantic.py src/newsletters/distill` | **Success: no issues found in 8 source files** |
| AI-optional contract | `.venv/bin/lint-imports` | **Contracts: 1 kept, 0 broken** |
| Build | `.venv/bin/newsletters build` | **rendered 9 surfaces + index, exit 0**; `git status content/` clean (byte-identical, faithful) |
| Runtime AI-free | `import newsletters.distill; sys.modules` | **No AI module loaded** |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| (none) | — | No `TBD`/`FIXME`/`XXX` debt markers in phase-modified files | — | The deferred-items.md note is genuine scope documentation, not an in-code debt marker. |

The Option-A structural fallback (`return True` for un-addressed traces in `entails`) is intentional, documented, and load-bearing — NOT a stub. `route_unfaithful_to_missing`'s mutable default `check=SpanContainmentFaithfulness()` is a stateless checker (no `__init__` state), so the shared-default-instance pattern is safe here.

### Hard-Rule Status

| Hard rule | Status | Evidence |
| --------- | ------ | -------- |
| No auto-publish | INTACT | `semantic.py:262-270` `_published_requires_satisfied_policy` last modified in Rev1 commit `5aca6f2` (2026-06-13), untouched by phase 3. |
| Every published claim traces to evidence; unsubstantiated → missing[] | INTACT / STRENGTHENED | `open_pull_request` untraced guard unchanged; `route_unfaithful_to_missing` adds verbatim relocation to `missing[]`. |
| AI-optional core (stdlib + Pydantic) | INTACT | lint-imports 1 kept/0 broken; faithfulness/provenance use `hashlib`/`str.casefold`/`str.split`/`str.find` only; no AI module loads at runtime; bare-install unaffected (no new deps). |
| Faithful, not suggestive | INTACT | Gate normalizes on transient copies only; stored `claim.text`/`trace.span` never mutated (behavioral check b); migration adds only hash+offsets (rendered HTML byte-identical). |

### Deferred-Items Note Honesty Check

`deferred-items.md` claims 8 pre-existing mypy errors in `dogfood.py` in functions NOT touched by phase 3. **Verified honest:** `mypy src/newsletters/dogfood.py` reports exactly 8 errors at lines 454 (`_newsletter_for`), 490 (`_show`), 564/568/572/576 (`_plan_report`). `git blame` traces these lines to commits `5aca6f2` (2026-06-13) and `93a4527` (2026-06-14) — both predate all phase-3 commits (2026-06-17). The phase-3-added functions (`MigrationReport` L67, `_address_trace` L84, `address_corpus_traces` L115, `_record_transcript` L179, `_address_report` L190) are mypy-clean. The note is accurate and the errors are genuinely pre-existing, not introduced by this phase.

### Human Verification Required

#### 1. Option-A scope adequacy (the key product judgment)

**Test:** Confirm the Option-A scope boundary is the intended product semantics — the strict span-containment gate has teeth ONLY on content-addressed traces; the live capture path (`capture.py`) still emits un-addressed empty-span traces that receive the structural (is-traced) pass.
**Expected:** Reviewer accepts that, for this phase, criterion 2's strict entailment is satisfied for content-addressed evidence (the migrated sample corpus + any future `Trace.from_source` path), and that content-addressing the live capture path is intentionally deferred to a later phase (it is not a Phase-3 success criterion).
**Why human:** This is a product/scope judgment about how much of the pipeline must be under the strict gate. The code correctly implements the resolved Option A; whether Option A's coverage is sufficient for the milestone is a human decision.

### Gaps Summary

**No Phase-3 gaps.** All three success criteria are verified in live code, all gates re-run green independently, all hard rules intact, the deferred mypy note is honest, and the three behavioral checks pass. The phase goal is achieved for content-addressed evidence: traces are drift-resistant (STALE on source edit) and unfaithful content-addressed claims are structurally routed to `missing[]` at the single socket seam for every backend.

**One forward note (not a gap):** Under the resolved Option A, claims minted on the live `capture.py` path are un-addressed (empty span) and so receive the structural pass rather than strict entailment. Closing that — content-addressing the live capture path so criterion 2's strict guarantee reaches capture-produced claims — is appropriate future work (a later phase / AI-mode entailment AI-01/02), explicitly out of Phase-3 scope per 03-CONTEXT.md decision 4. Surfaced as a human scope decision, not a blocker.

---

_Verified: 2026-06-17T13:58:44Z_
_Verifier: Claude (gsd-verifier)_
