---
phase: 1
slug: swim-lane-binding-traced-yaml-loader
status: retroactive
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-02
---

# Phase 1 — Validation Strategy (retroactive)

> Retroactive validation audit (2026-07-02), written after the fact for the deep-review loop. Maps
> each Phase-1 requirement to how it is validated on current HEAD
> `6c7dfc318f8dec6ca0301606914710a962e0f933`: **test-validated** (an executable assertion drives the
> live loader), **structurally validated** (guaranteed by construction/type, no test forces the
> edge), or **unvalidated** (an honest edge no test or type currently covers). Judgment derived
> honestly — gaps stated plainly.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (`.venv`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `.venv/bin/pytest tests/test_swimlane.py tests/test_swimlane_endpoints.py tests/test_abstraction_guard.py -q` |
| **Full suite command** | `.venv/bin/pytest -q` |
| **Estimated runtime** | ~0.3 s targeted; ~11.5 s full (623 tests) |

---

## Sampling Rate (as executed)

- **After every task commit:** each 01-0X task carried an inline `python -c` acceptance probe (loader
  tasks) or a pytest run (test tasks). Recorded verbatim in each SUMMARY §Verify.
- **After every plan wave:** full `.venv/bin/pytest -q` (baseline held 574 → 587 across the phase).
- **Circuit breaker:** Phase 1 gated the whole milestone — the enforced gate set had to be cleanly
  green or the overnight run STOPPED. It was green (587 at merge).
- **Max feedback latency:** < 15 s (full suite).

---

## Per-Requirement Validation Map

| Requirement | Behavior | Validation kind | Evidence / Command | Status |
|-------------|----------|-----------------|--------------------|--------|
| LANE-01 | N lanes → N `SectionBinding`, file order | **test** | `test_lanes_bind_at_dict_level` | ✅ green |
| LANE-01 | Bound at parsed-dict level, never `models.FunctionalGroup`/`Kpi` | **test** | negative `isinstance` + `__module__` check in `test_lanes_bind_at_dict_level` | ✅ green |
| LANE-01 | `models.py` unchanged | **structural** | `git diff` empty for `models.py` this phase (01-02-SUMMARY) | ✅ by construction |
| LANE-02 | Every value minted only via `Trace.from_source` | **structural + test** | `_Minter.mint` sole path (swimlane.py:227); `test_faithful_spans` proves faithful spans | ✅ green |
| LANE-02 | Every trace `is_addressed` (Hole B closed upstream) | **test (adversarial)** | `test_every_emitted_trace_is_addressed` — positive on both fixtures + an un-addressed trace REJECTED (proven non-vacuous) | ✅ green |
| LANE-02 | Read-anchored identity `claims+unextracted==walked` | **test (cross-checked)** | `test_no_yaml_scalar_is_read_but_undisclosed` vs INDEPENDENT `_count_scalar_leaves` | ✅ green |
| LANE-02 | Honest routing with exact reason codes | **test** | pinned `[_R_ANCHOR_ALIAS,_R_BLOCK_SCALAR,_R_TYPE_COERCED]` via loader's own constants | ✅ green |
| LANE-02 | Forward-only cursor → duplicates get distinct offsets | **test (generic)** | duplicate-offset assertion over any text appearing >1× | ✅ green |
| LANE-02 | Determinism (same file → byte-identical Source+bindings+load) | **test** | `test_load_is_byte_stable` (`model_dump_json` ×2) | ✅ green |
| LANE-03 | Guard fails on any config-specific name in `src/` | **test** | `test_no_config_specific_name_in_src` | ✅ green |
| LANE-03 | Guard demonstrably FIRES (non-vacuous) | **test (self-test)** | `test_guard_detects_planted_leak` + live red→revert demo (01-04-SUMMARY) | ✅ green |
| LANE-04 | `[config]` extra declares PyYAML only, non-AI | **test** | `test_config_extra_declared` | ✅ green |
| LANE-04 | No top-level yaml import in `_yaml_loader.py` OR `swimlane.py` | **test** | `test_yaml_loader_has_no_toplevel_yaml_import` | ✅ green |
| LANE-04 | Bare install imports succeed, yaml out of `sys.modules` | **test (subprocess)** | `test_swimlane_package_imports_without_yaml` | ✅ green |
| LANE-04 | Teaching `ImportError` on missing PyYAML | **test** | `test_yaml_loader_raises_teaching_error_without_yaml` vs `MISSING_YAML_MESSAGE` | ✅ green |
| LANE-04 | `safe_load` only, never `yaml.load` | **structural** | `load_config` calls `_load_yaml().safe_load` only (_yaml_loader.py:85); no test drives a malicious `!!python/object` payload to prove `yaml.load` is unreachable | ⚠️ structural-only |
| LANE-04 | `swimlane` import loads no AI module | **test (subprocess)** | `test_swimlane_import_loads_no_ai_module` + `lint-imports` contract | ✅ green |
| COMP-01/02 (post-phase `02-01`) | `kpi_endpoints` aligned, reference-not-re-mint, identity unaffected | **test** | `tests/test_swimlane_endpoints.py` (5 tests) | ✅ green |

---

## Structurally-Validated (guaranteed, not test-driven)

These behaviors are correct by construction or type, but **no test forces the edge** — they would
survive a refactor only as long as the construction holds:

1. **Read-anchored identity `RuntimeError` raise path is itself untested.** The identity is asserted
   to HOLD (`test_no_yaml_scalar_is_read_but_undisclosed`), but the `raise RuntimeError` on a drift
   (swimlane.py:548) is never exercised — unlike the Hole-B guard, which IS proven to fire. A future
   change that silently drops a scalar *and* miscounts `walked` in the same direction could pass. The
   independent `_count_scalar_leaves` cross-check mitigates this substantially. **Recommend:** a
   "prove-it-fires" test that monkeypatches the walk to drop a scalar and asserts the `RuntimeError`.
2. **Edge policy (`ValueError` on path-traversal, `FileNotFoundError`, `UnicodeDecodeError`)** is
   inherited from the `worksurface` edge policy and lives in code (swimlane.py:498-507), but **no
   swimlane test exercises any of the three**. They are structurally validated by `Path.relative_to`
   / `read_text(encoding="utf-8")` semantics.
3. **`safe_load`-only safety** — structurally guaranteed (see table), no adversarial YAML payload
   test.
4. **Non-string / coerced heading path** (swimlane.py:436-438) — code walks it generically; no
   fixture drives a non-string `heading:`.

---

## Unvalidated Edges (honest gaps)

No test or type currently covers these; they are out of the Phase-1 contract but named for honesty:

- **Non-UTF-8 config file** — asserted to raise in the docstring, never test-driven for swimlane.
- **Deeply nested / recursive lane structures** — `_walk_generic` recurses without a depth bound;
  a pathological YAML could hit Python's recursion limit. No test.
- **Very large config files** — no size bound; `str.find` per scalar is O(n·m) worst case. No
  performance test (fixtures are tiny by design — the "tiny committed fixture as executable
  contract" pattern).
- **Malformed YAML (`yaml.YAMLError`)** — surfaced to the caller (never swallowed), but no swimlane
  test drives a syntactically-broken config.
- **Empty / non-mapping top-level document** — handled (swimlane.py:533-535) but not fixture-driven.
- **A `value:` KPI's endpoint count** — the movement-form-only behavior (`value:` → 0 endpoints) is
  only validated *indirectly* (alignment test tolerates an empty list; ordering test skips
  `value:`-only KPIs). No test pins "a `value:` KPI yields exactly 0 endpoints" — which is why the
  stale docstring (see VERIFICATION Anti-Patterns) went unnoticed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Abstraction guard fires on a real source leak (not just in-memory) | LANE-03 | The in-memory self-test proves the matcher; a true source-write demo confirms the file walk | 01-04-SUMMARY records: plant `owner-1` into `swimlane.py` → suite RED → revert → green. |

---

## Nyquist Judgment

**`nyquist_compliant: true`** — honestly derived. Every requirement (LANE-01..04) has at least one
executable, non-vacuous test driving the live loader; the two most safety-critical invariants (Hole
B, abstraction guard) additionally carry adversarial "prove-it-fires" halves, and the coverage
identity is cross-checked against an independent yardstick. Sampling continuity held (no 3
consecutive tasks without automated verify). The residual gaps are **error-path and
out-of-contract edges** (edge-policy raises, the identity `RuntimeError`, malformed/huge/non-UTF-8
inputs), not core-behavior gaps — sampling is above the Nyquist rate for the phase's load-bearing
behaviors. The one gap worth closing next is the untested identity-`RuntimeError` (its sibling guard,
Hole B, sets the precedent for proving-it-fires).

---

## Validation Sign-Off

- [x] Every requirement has an automated verify
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covered (existing pytest infra; fixtures + suites added in 01-03/01-04)
- [x] No watch-mode flags
- [x] Feedback latency < 15 s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** retroactive, 2026-07-02 (deep-review loop Round 1)
