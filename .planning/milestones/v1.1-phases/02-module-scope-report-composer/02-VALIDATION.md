---
phase: 2
slug: module-scope-report-composer
status: retroactive
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-02
---

# Phase 2 — Validation Strategy (retroactive)

> Retroactive validation audit (2026-07-02), written for the deep-review loop (Round 2). Maps each
> Phase-2 requirement to how it is validated on current HEAD
> `1e3f1bc654cf898a07e7ce344e6254ca52665cec`: **test-validated** (an executable assertion drives the
> live composer/loader), **structurally validated** (guaranteed by construction/type, no test forces
> the edge), or **unvalidated** (an honest edge no test or type currently covers). Judgment derived
> honestly — gaps stated plainly, not papered over.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (`.venv`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `.venv/bin/pytest tests/test_compose.py tests/test_swimlane_endpoints.py -q` |
| **Full suite command** | `.venv/bin/pytest -q` |
| **Estimated runtime** | ~0.08 s targeted (18 tests); ~12 s full (623 tests) |

---

## Sampling Rate (as executed)

- **Per task:** each 02-0X task carried an inline `python -c` acceptance probe (02-01/02/03 loader +
  composer tasks) or a scoped `pytest -k` run (02-04 test tasks). Recorded verbatim in each SUMMARY
  §Gate-Results.
- **Per wave:** full `.venv/bin/pytest -q` (587 → 592 after 02-01; 592 held through 02-02/03;
  605 after 02-04's 13 guards).
- **Two mid-phase fixes** (`4031af1`, `efb635a`) re-ran the full suite green without touching any test
  file — the semantic change was absorbed by the existing guards (see the drift note in VERIFICATION).
- **Max feedback latency:** < 15 s (full suite).

---

## Per-Requirement Validation Map

| Requirement | Behavior | Validation kind | Evidence / Command | Status |
|-------------|----------|-----------------|--------------------|--------|
| COMP-01 | Kind-agnostic seam: a NON-lane `SectionBinding` composes with zero change | **test** | `test_kind_agnostic_seam_second_kind` (a "risk register" kind) | ✅ green |
| COMP-01 | N bindings → N `KpiStripBlock` + N `ClaimsBlock`, file order | **test** | `test_kpi_numbers_are_sourced_to_endpoints` (zip block↔binding), `test_determinism_with_repeated_value_across_lanes` (headings `["Alpha","Beta"]`) | ✅ green |
| COMP-01 | Zero-KPI section omits strip, keeps claims, discloses | **test** | `test_zero_kpi_lane_omits_strip_but_keeps_claims` | ✅ green |
| COMP-01 | Empty binding set → valid Draft, populated `missing[]`, never None | **test** | `test_empty_lane_set_is_a_valid_draft_with_populated_missing` | ✅ green |
| COMP-02 | `compute_delta` pure, signed magnitude + dir; Δ==0 → dir=None; non-numeric/absent → (None,None) | **test** | `test_every_rendered_delta_recomputes_byte_equal` recomputes each rendered delta AND dir; three arms exercised | ✅ green |
| COMP-02 | Reproducibility: every rendered delta recomputes byte-equal from its two endpoints | **test** | same test — `item.delta == compute_delta(ep[0].text, ep[-1].text)[0]` | ✅ green |
| COMP-02 | Never a fabricated 0 when <2 computable endpoints | **test** | same test — `saw_no_delta` arm asserts `len(computable) < 2 or recomputed is None` | ✅ green |
| COMP-02 | No `Kpi` start/baseline field added | **structural** | `git diff` empty for `models.py`/`semantic.py` this phase | ✅ by construction |
| COMP-02 | Δ only from two content-addressed numeric endpoints | **test** | `test_kpi_numbers_are_sourced_to_endpoints` (close endpoint `is_addressed`) | ✅ green |
| COMP-02 (02-01) | `kpi_endpoints` aligned, reference-not-re-mint, coverage identity unaffected, ordered, no fabricated endpoint | **test** | `tests/test_swimlane_endpoints.py` (5 tests) over both fixtures | ✅ green |
| COMP-03 | Hole B: zero-trace/un-addressed claim never on a `ClaimsBlock`, routed to `missing[]` | **test (adversarial)** | `test_every_claimsblock_claim_is_traced_and_addressed` + `test_untraced_and_unaddressed_claims_are_routed_to_missing` (planted both, non-vacuous) | ✅ green |
| COMP-03 | Hole A: no un-sourced digit run in non-`ClaimsBlock` authored text | **test (adversarial)** | `test_authored_prose_is_numeral_free` (poisoned `ProseBlock` caught) | ✅ green |
| COMP-03 | `faithfulness.py`/`coverage.py`/`semantic.py`/`templates.py`/`site.py` untouched | **test (runtime git diff)** | `test_faithfulness_coverage_semantic_templates_site_are_untouched` (`git diff --exit-code`) | ✅ green |
| COMP-04 | Stable `R-NNN` via reused `Ledger.ref_for`, keyed by surface slug | **structural + probe** | compose.py:322-325; 02-03 plan smoke check (R-001 first, immutable on re-sight) | ⚠️ probe-only (no pytest asserts R-001 on the composed surface) |
| COMP-04 | Sourced-or-omit quote (omit+disclose / verbatim / "unassigned") | **test** | `test_unowned_and_sourced_quote_honesty` (all three cases) | ✅ green |
| COMP-04 | Fanout stub always present, every `href=None` | **structural** | `_fanout_stub` (compose.py:257-262); asserted indirectly in seam/edge composes | ⚠️ no dedicated fanout `href is None` assert in `test_compose.py` |
| COMP-04 | No-auto-publish: Draft; `publish()` raises; direct PUBLISHED raises | **test (adversarial)** | `test_no_auto_publish_on_the_composed_surface` | ✅ green |
| COMP-01/02 | Determinism: two composes byte-identical `model_dump_json`; `created==EPOCH_ZERO` | **test** | `test_two_composes_are_byte_identical`, `test_determinism_with_repeated_value_across_lanes` | ✅ green |

---

## Structurally-Validated (guaranteed, not test-driven)

Correct by construction/type, but **no test forces the edge** — they survive a refactor only as long
as the construction holds:

1. **The zero-endpoint compose arm (the `efb635a` resolution) is untested at compose level.** The
   whole point of the movement-form-only fix — a point-in-time `value:` KPI (`kpi_endpoints=[[]]`)
   yields `delta=None` with **no** movement note — is exercised by *no* `test_compose.py` test. All
   hand-built fixtures model "point-in-time" as a **one-element** endpoint list, which under HEAD
   semantics fires the "only one endpoint usable" note. The behavior is proven at the loader level
   (`test_swimlane_endpoints`) and by the live drive recorded in `02-VERIFICATION.md`, and the
   composer's `_compose_kpi_item` has an explicit zero-endpoint branch. **Recommend:** one guard test
   with `kpi_endpoints=[[]]` asserting no movement note. (This is the single-line drift-risk this
   phase carries; it is the compose-level twin of Round 1's swimlane docstring drift.)

2. **`compute_delta` unit handling on mixed units is silent.** Verified live: `compute_delta("10
   days", "7 items") → ("-3", "down")` — the differing units are **dropped** and a unitless delta is
   produced with no disclosure. No test drives mixed-unit endpoints. In practice config is authored
   with consistent units per KPI, so this is out-of-scope faithfulness slack, not a live defect — but
   it is unvalidated.

3. **Fanout `href is None` invariant** is guaranteed by `_fanout_stub` construction (every
   `FanoutLink(kind, title)` uses the model default `href=None`) but has no dedicated compose-level
   assertion (only the 02-03 smoke check). A regression that set an `href` would not turn any
   `test_compose.py` test red.

4. **`R-NNN` value on the composed surface** is proven by the 02-03 plan's `python -c` smoke check
   (fresh ledger → R-001, immutable on re-sight, never saved), not by a committed pytest. The
   `test_compose.py` suite uses a fresh empty in-memory ledger per compose and does not assert the
   assigned ref string.

---

## Unvalidated Edges (honest gaps — no test AND no structural guarantee)

1. **Locale / thousands-separator numerals mis-parse silently.** Verified live: `compute_delta("1,000",
   "2,000") → ("+1,000", "up")` — but by accident: the regex `^\s*([+-]?\d+(?:\.\d+)?)\s*(\S*)\s*$`
   reads the magnitude as `1` and `2` and treats `,000` as a *unit* string; the "+1" happens to render
   with a `,000` suffix that looks right. `compute_delta("1,500", "2,000")` would produce `"+1"` (units
   `,500`≠`,000` → dropped) for a real change of 500. Config is expected to use plain numbers, so this
   is latent, not live — but wholly unvalidated.

2. **Very large numbers / high precision:** `compute_delta` uses `Decimal`, so arbitrary precision is
   handled correctly (`compute_delta("1e20-ish", "1")` verified sane), but no test pins it.

3. **A quote claim carrying multiple traces:** `_addressed` checks `all(t.is_addressed for t in
   claim.evidence)`, so a multi-trace quote is handled correctly; `_quote_block` renders `quote.text`
   regardless of trace count. No test drives a multi-trace quote claim.

4. **A hand-built `SectionBinding` with `len(kpi_items) != len(kpi_endpoints)`:** compose degrades
   gracefully — `endpoints = endpoints_by_kpi[index] if index < len(endpoints_by_kpi) else []` (so
   surplus items get zero endpoints; surplus endpoint lists are ignored). The loader guarantees
   lockstep alignment (`test_kpi_endpoints_align_with_kpi_items`), so this mismatch cannot arise from
   config — but a hand-built caller could trigger it and no compose test covers the ragged case.

5. **`compute_delta` mixed int/float pair formatting:** verified live (`("1.5","3") → ("+1.5","up")`,
   `("-5","5") → ("+10","up")`), correct, but the int/float `is_float` promotion is not pinned by a
   committed test (the fixture uses only integer endpoints and a "days"/"bugs" unit).

---

## Nyquist Compliance (honestly derived)

**nyquist_compliant: true** — every one of the four COMP requirements has at least one executable,
non-vacuous test driving the live composer, and the two research holes (A, B) are each closed by a
guard proven to fire on a planted violation. The trust-critical behaviors — delta reproducibility,
byte-determinism, no-auto-publish, traced-or-missing routing, the numeral-free-prose gate — are
sampled at commit granularity and cannot silently regress.

The gaps above are **edges around a well-sampled core**, not core blind spots: the one behavioral
branch lacking a direct compose-level test (the zero-endpoint point-in-time arm) is covered
structurally, at the loader level, and by live drive — the same disposition Round 1 gave the
loader's `RuntimeError` raise path. The unvalidated `compute_delta` edges (mixed units, locale
separators) are faithfulness slack on inputs the controlled config never produces. None rises to a
Nyquist violation; each is logged as a recommended future guard rather than a false "validated."

---
*Validation audit: 2026-07-02 (retroactive, deep-review loop Round 2)*
*Auditor: Claude (Bureau Chief)*
