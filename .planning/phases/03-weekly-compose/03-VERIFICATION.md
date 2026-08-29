---
phase: 03-weekly-compose
verified: 2026-08-29T09:00:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 3: Weekly compose Verification Report

**Phase Goal:** A weekly `Surface(REPORT, Draft)` composes from authored voice plus adapter
evidence — new block kinds, the Weekly Spec path, content-addressed assets, BI values via
export — where the composer assembles and traces and never editorializes.
**Verified:** 2026-08-29T09:00:00Z
**Status:** passed
**Re-verification:** No — initial verification (goal-backward, code-review-fix scrutiny requested)

## Goal Achievement

### Observable Truths (ROADMAP Phase 3 Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Four new block kinds join the typed `Block` union; none can be silently dropped | ✓ VERIFIED | `get_args(get_args(Block)[0])` == 15 members live. `render.py` fall-through `return ""` at the old line 620 is gone — `grep -n 'return ""' render.py` shows only 4 unrelated occurrences (lines 505, 515, 778, plus a `join`), none in `_block_html`'s dispatch tail. `tests/test_weekly_blocks.py::test_unrecognized_block_raises_a_teaching_error_naming_its_kind` and the full dispatch-coverage test pass live. |
| 2 | A hand-authored Weekly Spec composes through the Case Spec mechanism: narrative byte-verbatim with real-span Traces, `config:` bound never claimed, absences → `missing[]` | ✓ VERIFIED | `tests/test_weeklyspec.py` (72+ tests) pass live including the span-swap regression, the config-never-claimed guard, and the editorialization guard (`weekly-editorial-bait.yml`, three baited pairs). Ran `tests/test_weeklyspec.py tests/test_weekly_blocks.py tests/test_weekly_values.py tests/test_semantic_gate_frozen.py tests/test_review.py -q` together: 146 passed. |
| 3 | An asset enters a Surface only as a content-addressed file meeting the provenance minimum; a BI-values screenshot without its required deep link routes to `missing[]`, never placed | ✓ VERIFIED | `AssetRecord(folder="", date="", event="")` now raises `ValidationError` live (WR-02 fix confirmed — was constructible pre-fix per review). `AssetBlock(asset=rec, evidence=[])` raises on `min_length=1`. 13 parametrized `asset_routing` cases in `test_weeklyspec.py` cover all provenance rows, the deep-link rule, hash-mismatch/substitution, and root-escape (raise, not `missing[]`) — all pass live. |
| 4 | BI values reach the weekly through the existing ADAPT-03 excel adapter fed an export; no new adapter module; ADAPT-05 unchanged | ✓ VERIFIED | `git diff --stat $(git merge-base HEAD origin/main) -- src/newsletters/adapters/` is empty (exit 0, no output). `grep -c 'openpyxl\|xlsx\|load_workbook' src/newsletters/weeklyspec.py` = 0. `tests/test_weekly_values.py` (resolve("excel") → parse → distill → KpiStripBlock/ClaimsBlock) passes live. |
| 5 | Composing the same inputs twice yields a byte-identical Draft Surface at EPOCH_ZERO that has never advanced the gate, and renders through Phase 2's writer to a deck satisfying the determinism definition | ✓ VERIFIED | Live check: `build_weekly_report(load_weekly_spec(...), author=...)` run twice on `weekly-full.yml` → `sa.model_dump_json() == sb.model_dump_json()` is `True`; `sa.created` = `1970-01-01 00:00:00+00:00` (EPOCH_ZERO); `sa.review.state` = `draft`. `tests/test_pptx_determinism.py` (7 passed) and `weekly_slots` reopened-bytes tests in `test_weeklyspec.py` pass live. |

**Score:** 5/5 truths verified

### Code-Review Fix Verification (03-REVIEW.md, commits 2892a14..5631ad5)

All 9 findings claimed "fixed" were checked against live files, not the SUMMARY narrative:

| Finding | Claimed Fix | Live Verification |
|---------|-------------|--------------------|
| CR-01 (Critical) | Duplicate YAML keys refused at parse boundary | `src/newsletters/_yaml_loader.py` contains `_checked_mapping` raising `"duplicate key {key!r} at line ..."` — confirmed present, wired into `load_config` via `yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG`. |
| WR-01 | Exact-find span minter skips YAML comments | `src/newsletters/specspan.py` contains `_comment_start`, `_comment_spans`, and the skip-loop in `mint` — confirmed present with the WR-01 citation in comments. |
| WR-02 | Blank provenance unrepresentable at type level | Live construction test: `AssetRecord(folder="", date="", event="")` now raises `ValidationError` (previously constructed per the review finding). `evidence: list[Trace] = Field(min_length=1)` confirmed in `semantic.py:620`. |
| **WR-03** | Gate sees every claim carrier (`NarrativeBlock` claims, `AssetBlock.evidence`), not just `ClaimsBlock` | **Independently executed, not trusted.** `tests/test_review.py::test_blocks_stale_narrative_claim_on_a_published_weekly`, `::test_blocks_stale_asset_evidence_on_a_published_weekly`, and `::test_pr_gate_refuses_an_untraced_narrative_claim` all **PASS** when run in isolation (`3 passed, 11 deselected`). The stale-narrative-published scenario test publishes a `Surface` with a `NarrativeBlock` claim, asserts `review_blockers == []` pre-drift, mutates the source transcript, and asserts a `STALE` blocker fires post-drift — this is the exact scenario the finding described as unreachable, and it is now reachable and green. `tests/test_semantic_gate_frozen.py` pin for `Surface._published_claims` was updated in the same commit (`bd956ce`) to the new digest `ea523ffe...`, with a comment citing **"03-REVIEW WR-03"** by name as the sanctioned reason for the widening — confirmed present verbatim in the live file. The full `test_semantic_gate_frozen.py` suite (11 tests, including the non-vacuity mutation-discrimination arm) passes live. |
| WR-04 | `compose_kpi_item` promoted public, single source of KPI policy/wording | `src/newsletters/compose.py` exports `compose_kpi_item`, `NO_KPIS`, `UNCOMPUTABLE_DELTA`, `ONE_ENDPOINT` in `__all__`; `weeklyspec.py` imports and calls `compose_kpi_item` (line 961) — no local `_kpi_item` duplicate remains. |
| WR-05 | Blank authored list items disclosed via `missing[]`, not silently dropped | `weeklyspec.py` contains `absent(f"{key}[{index}]")` at lines 656, 662, 750 — confirmed present. |
| WR-06 | Placed asset without alt/caption still renders provenance | `render.py:682` emits `<figcaption class="sg-mono">{folder} · {date} · {event}</figcaption>` unconditionally for `AssetBlock` — confirmed present, using only pre-existing `_CSS` classes. |
| IN-01 | `build_weekly_report` dedupes `missing[]` | `weeklyspec.py:1056` calls `dedup_in_order(missing)`, importing the promoted `compose.dedup_in_order` — confirmed present. |
| IN-03 | `pptx_writer.py` banner points at the live gate guard | `pptx_writer.py` module docstring now names `tests/test_semantic_gate_frozen.py` instead of the removed byte-freeze — confirmed present. |

**Gates re-run independently (not trusted on the fixer's report):**

| Gate | Result |
|------|--------|
| `.venv/bin/python -m pytest -q` (full suite) | **837 passed, 0 skipped, 1 pre-existing warning** — matches claimed baseline exactly |
| `.venv/bin/python -m pytest tests/test_review.py -k "stale_narrative or stale_asset_evidence or pr_gate_refuses_an_untraced_narrative" -v` | 3 passed (WR-03 scenario tests, run in isolation) |
| `.venv/bin/python -m pytest tests/test_semantic_gate_frozen.py -q` | 11 passed |
| `.venv/bin/lint-imports` | 2 contracts kept, 0 broken |
| `newsletters check --corpus rev1\|work\|module` | all three: "All published surfaces clean — no blockers" |
| Debt-marker scan (`TBD\|FIXME\|XXX`) on all phase-modified `src/` files | 0 matches |
| Double-compose byte-identity + EPOCH_ZERO + Draft state | Confirmed live (see truth #5 above) |
| `git diff --stat <base> -- src/newsletters/adapters/` | empty |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/semantic.py` | 4 new block kinds, 15-member union, pure insertion | ✓ VERIFIED | 15 members confirmed live; `Surface._published_claims` widened for WR-03 as a pure insertion (pin updated same commit) |
| `src/newsletters/render.py` | 4 HTML branches + fail-loud fall-through + `_claim_badge` on NarrativeBlock | ✓ VERIFIED | Confirmed live; WR-06 figcaption present |
| `src/newsletters/specspan.py` | promoted `SpanMinter`/`absent`, comment-aware find | ✓ VERIFIED | WR-01 fix present |
| `src/newsletters/weeklyspec.py` | schema, loader, asset routing, composer, `weekly_slots` | ✓ VERIFIED | 1058+ lines; all cited fixes present |
| `src/newsletters/review.py` | `review_blockers` walks all claim carriers | ✓ VERIFIED | WR-03 fix present and tested |
| `src/newsletters/_yaml_loader.py` | duplicate-key refusal | ✓ VERIFIED | CR-01 fix present |
| `tests/test_semantic_gate_frozen.py` | 8 gate-function pins + zero-deletion diff shape | ✓ VERIFIED | 11 tests pass; WR-03 pin update citation present |
| `.github/workflows/ci.yml` | `weekly` job runs the compose path, `0 skipped` assertion | ✓ VERIFIED (structural; job's first observed CI green is a carried human-verification item, not a gap) | job present, `fetch-depth: 0`, module list includes weekly test files |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `render.py::_block_html` | `semantic.py` block classes | `isinstance` dispatch over 4 new kinds | WIRED | confirmed by passing dispatch-coverage test |
| `weeklyspec.py` | `specspan.py` | `from .specspan import SpanMinter, absent` | WIRED | confirmed by grep + passing tests |
| `casespec.py` | `specspan.py` | same promoted minter | WIRED | `c.SpanMinter is s.SpanMinter` — one implementation |
| `weeklyspec.py` | `compose.py` | `compose_kpi_item`, `addressed`, `dedup_in_order` imports | WIRED | confirmed live import line 67 |
| `review.py::review_blockers` | `semantic.py` (`NarrativeBlock`, `AssetBlock`) | new claim/trace walk (WR-03) | WIRED | confirmed live, test-proven both directions (stale detection + clean-until-drift) |
| `Surface._published_claims` | `NarrativeBlock.items[].claim` | pure-insertion walk (WR-03) | WIRED | confirmed live, `test_pr_gate_refuses_an_untraced_narrative_claim` passes |
| weekly composer | `pptx_writer.render_surface_pptx` | `weekly_slots` → explicit-slots API | WIRED | confirmed via `test_weeklyspec.py` deck tests + live byte-identity check |
| excel adapter | weekly `KpiStripBlock`/`ClaimsBlock` | `resolve("excel")` → `parse`/`distill` → binding | WIRED | confirmed via `test_weekly_values.py` passing live |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| 15-member Block union | `get_args(get_args(Block)[0])` length | 15 | ✓ PASS |
| Provenance-less AssetRecord refused | direct construction with empty folder/date/event | `ValidationError` | ✓ PASS |
| Double-compose byte identity | `build_weekly_report` run twice, `model_dump_json()` compared | `True`, `created`=EPOCH_ZERO, `review.state`=`draft` | ✓ PASS |
| WR-03 stale-narrative scenario | `pytest -k "stale_narrative or stale_asset_evidence or pr_gate_refuses..."` | 3 passed | ✓ PASS |
| Gate-freeze pins (incl. WR-03 update) | `pytest tests/test_semantic_gate_frozen.py -q` | 11 passed | ✓ PASS |
| ADAPT-05 / adapters dir untouched | `git diff --stat <base> -- src/newsletters/adapters/` | empty | ✓ PASS |
| Full regression suite | `pytest -q` | 837 passed, 0 skipped | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| WKLY-02 | 03-01, 03-02, 03-03 | New block kinds + Weekly Spec YAML composition, byte-verbatim, config bound never claimed | ✓ SATISFIED | Truths 1 & 2 above; 837/0 suite green |
| WKLY-03 | 03-01 (type half), 03-03 (routing) | Content-addressed asset, provenance minimum, `missing[]` routing | ✓ SATISFIED | Truth 3 above; WR-02 fix confirmed live |
| WKLY-04 | 03-04 | BI values via existing ADAPT-03 adapter, no new adapter, ADAPT-05 unchanged | ✓ SATISFIED | Truth 4 above; clean adapters diff confirmed |

No orphaned requirements found for this phase in `.planning/REQUIREMENTS.md`.

### Anti-Patterns Found

None. Scanned all phase-touched `src/newsletters/` files (`weeklyspec.py`, `specspan.py`, `semantic.py`, `render.py`, `compose.py`, `casespec.py`, `review.py`, `_yaml_loader.py`) for `TBD`/`FIXME`/`XXX` — zero matches. Carried Info-level findings from 03-REVIEW.md (IN-02, IN-04, IN-05, IN-06, IN-07) are documented, non-blocking cosmetic/deferred items, explicitly recorded as "carried" in the review's Fix Outcomes table — not silent omissions.

### Human Verification Required

None required to pass this phase — the following are pre-recorded, out-of-environment confirmations carried explicitly by the phase itself (per task instructions, these are known items, not gaps):

1. **Text-only deck is a recorded decision, not a gap.** `docs/weekly-spec.md` documents that `AssetBlock` images do not reach the `.pptx` deck this phase (no `add_picture` path in the writer; no success criterion budgets it). This is a stated round-two item.
2. **Real-PowerPoint open of the rendered deck is unproven in this environment** (no `.pptx` consumer available; carried from Phase 2 unchanged). This is a PR-review confirmation, not a phase gap.
3. **First observed CI green for the `weekly` job is unobserved from this environment** (no `gh` CLI access here). The job's exact command was proved locally (`174 passed in 1.15s`, 0 skipped) and the job is structurally present in `.github/workflows/ci.yml` with `fetch-depth: 0`. This is a PR-review confirmation.

### Gaps Summary

None. All 5 ROADMAP Phase 3 success criteria are independently verified against live code and passing tests, not merely SUMMARY claims. The WR-03 fix — the fix most likely to have residual scope (extending gate enforcement to new claim carriers) — was independently executed: the stale-narrative-published scenario test was run in isolation and passed, and the `test_semantic_gate_frozen.py` pin update carries the required WR-03 citation verbatim in a code comment. Full regression suite reproduces the claimed 837 passed / 0 skipped exactly. `lint-imports` and `newsletters check` gates are clean. DEF-15 (black/isort house-width lint, no CI job) is pre-existing baseline debt, unrelated to this phase's scope, and was not reintroduced.

---

_Verified: 2026-08-29T09:00:00Z_
_Verifier: Claude (gsd-verifier)_
