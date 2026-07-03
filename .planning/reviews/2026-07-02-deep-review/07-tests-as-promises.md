# Round 7 — Tests as promises: the guard ledger for the v1.1 surface + trust spine

> Deep-review loop, Round 7. Subject: the whole test suite (623) read as a **promise ledger** —
> for each promise, which test guards it, whether that guard has *teeth*, and which promises are
> guarded only vacuously, structurally, or not at all. Standing lenses: delta-to-reality · drift ·
> total-history honesty.
>
> **Method (per CLAUDE.md).** Every teeth-class below was assigned by READING THE TEST BODY at this
> SHA, not the test name. A test earns **adversarial-fires** only if it plants a violation and
> proves the guard rejects it (the RETRO "prove-it-FIRES" discipline). **This document reviews; it
> does not refactor** — no code was written this round; remediations are specified, not applied.

**For the record (run once, this branch `loop-r7/tests-as-promises`):**

- `.venv/bin/pytest -q` tail:

```
........................................................................ [ 92%]
...............................................                          [100%]
623 passed in 11.58s
```

- `.venv/bin/pytest --collect-only -q | tail -3`:

```
tests/test_worksurface.py::test_build_corpus_work_smoke

623 tests collected in 0.30s
```

Teeth vocabulary: **adversarial-fires** = plants a violation, proves rejection · **positive-only** =
asserts the happy path / an invariant holds, never forces the failing edge · **structural** =
guaranteed by a git-diff / import / type / absence scan (a config or edge, not a planted cheat) ·
**VACUOUS** = passes without asserting anything on the current inputs.

---

## Part 1 — Promise → guard ledger

### 1A. The v1.1 surface (Phases 1–4: loader, composer, module corpus, voice)

| # | Promise (one line) | Guarding test(s) | Teeth | Notes (verified by reading the body) |
|---|--------------------|------------------|-------|--------------------------------------|
| 1 | N lanes → N dict-level `SectionBinding`, file order, never `models.*` | `test_lanes_bind_at_dict_level` | positive-only + structural | Counts read from same parsed fixture; negative `isinstance`/`__module__` checks add structural teeth. No planted violation. |
| 2 | Every loader scalar is claimed or disclosed (`claims+unextracted==walked`) | `test_no_yaml_scalar_is_read_but_undisclosed` | positive-only (independent cross-check) | Cross-checks against independent `_count_scalar_leaves` — strong, but the `RuntimeError` raise path (swimlane.py:548) is never forced. (R1 structural #1.) |
| 3 | Exact ordered `_R_*` routing reasons on the trap | same test, part (c) | positive-only | Pinned via loader's own constants (no inline dup → no drift). |
| 4 | Forward-only cursor → duplicate values get distinct offsets | same test, part (e) | positive-only (generic) | Generic over any text appearing >1×; asserts distinctness, not a re-point rejection. |
| 5 | Mapping-shaped `values:` → empty display + `missing[]` note | same test, part (d) | positive-only | Reads the trap fixture; asserts the disclosure exists. |
| 6 | Every emitted claim faithful (text==span, re-sliceable, non-stale) | `test_faithful_spans` | positive-only | Both fixtures; no planted non-faithful claim (faithfulness's adversarial half lives in `test_faithfulness_gate.py`). |
| 7 | **Hole B (loader): every trace is_addressed** | `test_every_emitted_trace_is_addressed` | **adversarial-fires** | Hand-built `Trace(content_hash=None)` REJECTED by the same predicate that passes for a real claim; real claim proven True (non-vacuous). |
| 8 | Loader determinism (byte-identical double load) | `test_load_is_byte_stable` | positive-only | `model_dump_json` ×2 on Source + bindings + whole load. |
| 9 | **No config-specific name in `src/` (abstraction)** | `test_no_config_specific_name_in_src` + `test_guard_detects_planted_leak` | **adversarial-fires** | Self-test plants `owner-1`/`Jean-Luc Picard`/`eng-07` through the SAME `_scan_text`; clean structural keys stay clean. |
| 10 | `kpi_endpoints` aligned 1:1 with `kpi_items` | `test_kpi_endpoints_align_with_kpi_items` | positive-only | Both fixtures. |
| 11 | Endpoints are references, not re-mints (object identity) | `test_endpoints_are_references_not_re_mints` | positive-only | `is`-identity, not `==`. |
| 12 | Endpoints add zero mints (coverage identity intact) | `test_coverage_identity_unaffected_by_endpoints` | positive-only | The `+field` didn't drift the identity. |
| 13 | `values:`-list endpoints ordered + addressed | `test_values_list_endpoints_ordered_and_addressed` | positive-only | Strictly-forward offsets, file order. |
| 14 | Mapping-shaped `values:` → <2 references (no fabricated endpoint) | `test_disclosed_endpoints_yield_no_fabricated_reference` | structural (trap fixture) | Drives the trap's mapping slot; asserts `len<2`. Not a planted cheat but a real disclosed edge. |
| 15 | **Hole B (composer): un-addressed/untraced claim → `missing[]`** | `test_every_claimsblock_claim_is_traced_and_addressed` (+) `test_untraced_and_unaddressed_claims_are_routed_to_missing` | **adversarial-fires** | Second test PLANTS a zero-evidence claim AND an un-addressed-trace claim; proves both are absent from ClaimsBlocks and present in `missing[]`. |
| 16 | **Hole A: authored prose carries no un-sourced digit run** | `test_authored_prose_is_numeral_free` | **adversarial-fires** | Poisoned `ProseBlock("we shipped 42 features")` caught by the same scan that passes clean output. Composer-only (semantic layer has no numeral guard — #5 ceiling). |
| 17 | Only out-of-claim numerals are KPI value/delta traced to endpoints | `test_kpi_numbers_are_sourced_to_endpoints` | positive-only | value == close-endpoint text; delta requires ≥2. |
| 18 | **No auto-publish on the composed surface** | `test_no_auto_publish_on_the_composed_surface` | **adversarial-fires** | `publish()` w/o reviewer RAISES and leaves gate Draft; direct `Review(PUBLISHED,…)` RAISES. |
| 19 | Every rendered Δ recomputes byte-equal; no fabricated 0; Δ==0 honest | `test_every_rendered_delta_recomputes_byte_equal` | positive-only (3 arms) | Movement / point-in-time(1-elem) / Δ==0 arms. **True zero-endpoint `[[]]` arm NOT exercised** (R2 #1 — see Part 2). |
| 20 | Composer determinism (byte-identical; created==EPOCH_ZERO; repeated value stable) | `test_two_composes_are_byte_identical`, `test_determinism_with_repeated_value_across_lanes` | positive-only | Asserts EPOCH_ZERO sentinel + total file-order. |
| 21 | Kind-agnostic seam: a non-lane binding composes unchanged | `test_kind_agnostic_seam_second_kind` | positive-only | "risk register" kind; disclosure of no-KPIs asserted. |
| 22 | Zero-KPI section omits strip, keeps claims, discloses | `test_zero_kpi_lane_omits_strip_but_keeps_claims` | positive-only | |
| 23 | Empty binding set → valid Draft + populated `missing[]` | `test_empty_lane_set_is_a_valid_draft_with_populated_missing` | positive-only | Composer level only — NOT through the builder/CLI (R3 #3). |
| 24 | Sourced-or-omit quote (omit+disclose / owner / unassigned) | `test_unowned_and_sourced_quote_honesty` | positive-only | 3 arms. **Adversarial arm missing:** an untraced/unaddressed quote (compose.py:274 `not _addressed`) is never planted (see Part 2, new find). |
| 25 | This suite weakens NO gate (protected files byte-untouched) | `test_faithfulness_coverage_semantic_templates_site_are_untouched` | adversarial-by-design | Runtime `git diff --exit-code` over 5 gate files. |
| 26 | Module surface: every ClaimsBlock claim traced+addressed; honesty panel populated | `test_every_claim_traced_and_addressed` | positive-only | Also asserts body non-empty AND `missing` non-empty (anti-Pitfall-11). |
| 27 | Single-endpoint disclosure VISIBLE (escaped) in rendered HTML | `test_single_endpoint_disclosure_visible_in_html` | positive-only (content) | Asserts `class="honesty"` + `class="claim-span"` + the full escaped entry text — real content teeth, not just the class. |
| 28 | Owner quote rendered from the sourced path, present in HTML | `test_owner_quote_rendered_from_sourced_path` | positive-only (content) | Escaped quote text present. |
| 29 | Module output auto-loads zero external resources | `test_no_external_calls` | structural | Forbidden-host / `url(http` / `<link href="http">` scans + woff2 present. Absence scan, no planted external. |
| 30 | Module build byte-stable double-render | `test_byte_stable_double_render` | positive-only | Identical file set + byte-identical every file. |
| 31 | R-001 stable across rebuild (append-only) | `test_r001_stable_across_rebuild` | positive-only (proof-by-rebuild) | Fresh tmp ledger; stability proven by rebuild, not a literal twice. |
| 32 | Committed `content/module/` == fresh build | `test_committed_equals_fresh_build` | positive-only | Byte-for-byte; committed ledger unchanged. |
| 33 | No `datetime.now()` reachable (EPOCH_ZERO) | `test_no_datetime_now_reachable` | structural | Asserts sentinel on surface.created + every source.timestamp. |
| 34 | **Committed content is synthetic (no real-looking names/emails)** | `test_committed_content_is_synthetic` | **adversarial-fires** | Planted `Jean-Luc Picard`/`ops@starfleet.int` caught by same scanner; positive fabricated-marker assert. |
| 35 | `check --corpus module` clean → exit 0 | `test_check_module_clean_exits_zero` | **VACUOUS-by-design** | The only surface ships Draft → exempt from `review_blockers`; clean direction validates nothing (documented in the test). Teeth are in #36. |
| 36 | **Same UNFORKED gate fires on a planted blocker → nonzero** | `test_check_module_blocks_on_planted_blocker` | **adversarial-fires** | Monkeypatched in-memory PUBLISHED unentailed surface → nonzero + `BLOCK`/`merge blocked`/surface id. |
| 37 | `build --corpus module` routes to `build_module_site` | `test_build_module_smoke` | positive-only | Emits report + library pages. |
| 38 | Voice: 6 dispatch sections in prescribed order | `test_ship_pr_body_is_a_signals_dispatch` | positive-only (contract-text) | Order asserted INSIDE ship.md — not on a generated body (R4 #3). |
| 39 | Voice: verbatim gates, never-paraphrase, no-AI-framing, evidence rule | `test_ship_mandates_verbatim_gate_output_and_forbids_hype` | positive-only (contract-text) | Presence of mandate strings. |
| 40 | Voice: fallbacks may not assert facts; offender not returned as guidance | `test_ship_forbids_fact_asserting_fallbacks` | positive-only + structural absence | Asserts the offender string absent from post-`forbidden` text. |
| 41 | Voice: client "Start here" section's 3 parts + link-rendered rule | `test_ship_requires_the_client_section` | positive-only (contract-text) | Keyword check (`rendered`/`link`), not a real linked artifact (R4 #5). |
| 42 | Voice: summary template feeds the dispatch | `test_summary_template_feeds_the_dispatch` | positive-only | |
| 43 | Voice: `config.json` `pr_body_sections` has no fact-asserting fallback | `test_config_carries_no_boilerplate_pr_sections` | **VACUOUS** | `pr_body_sections == []` → loop body never runs; asserts nothing today (R4 #1). |
| 44 | Voice reversion → RED suite (installer-clobber protection) | whole `test_signals_voice.py` (`_pr_body_step` hard-fails if step deleted) | structural (teeth un-fired) | RED guaranteed by assertion structure; the "revert-a-line → RED" ritual was NOT run this milestone for ship.md (R4 structural #1). |
| 45 | `[config]` extra = PyYAML only, non-AI | `test_config_extra_declared` | positive-only/structural | |
| 46 | No top-level yaml import in `_yaml_loader.py`/`swimlane.py` | `test_yaml_loader_has_no_toplevel_yaml_import` | structural | Source-text edge scan. |
| 47 | **Bare install imports succeed with yaml blocked** | `test_swimlane_package_imports_without_yaml` | **adversarial-fires** | `sys.meta_path` finder BLOCKS yaml; import still works, yaml stays out of `sys.modules`. |
| 48 | **Teaching `ImportError` when PyYAML absent** | `test_yaml_loader_raises_teaching_error_without_yaml` | **adversarial-fires** | Blocks yaml; asserts `MISSING_YAML_MESSAGE` + `[config]`/`PyYAML` substrings. |
| 49 | Happy path returns module when PyYAML present | `test_yaml_loader_returns_module_when_present` | positive-only | Skips cleanly on bare env. |
| 50 | `safe_load` only, never `yaml.load` | *(none)* | **structural-only** | No adversarial `!!python/object` payload drives the unreachability (R1 table + structural #3). |

### 1B. The 12 trust invariants (baseline: `05-trust-invariants.md`; teeth re-confirmed by body-read)

| Inv | Promise | Guarding test(s) | Teeth | Notes / ceiling that becomes an unguarded arm |
|-----|---------|------------------|-------|-----------------------------------------------|
| 1 | No auto-publish (policy-satisfied gate is the only path) | `test_published_without_approval_is_rejected`, `test_article_requires_a_peer_not_the_author`, `test_no_auto_publish_on_the_composed_surface`, `test_socket_never_auto_publishes` | **adversarial-fires** | Enforces policy satisfaction, not reviewer-identity authenticity; `require_peer` is string-inequality only (colluding names pass) — external trust, unguardable here. |
| 2 | Every published claim traces to evidence | `test_untraced_claim_blocks_review`, `test_traced_claim_passes_review`, `test_untraced_and_unaddressed_claims_are_routed_to_missing`, `test_faithfulness_seam_rejects_untraced` | **adversarial-fires** | Gate inspects only `ClaimsBlock` claims — a numeral in a `ProseBlock`/`KpiStrip` is invisible (covered only by #5 Hole A, composer-only). |
| 3 | Content-addressed STALE (computed, never a stored flag) | `test_blocks_stale_published_claim`, `test_every_emitted_trace_is_addressed` | adversarial-fires (loader half) / structural (review half) | Un-addressed trace is never stale (Option-A); missing source ⇒ silently "not stale," not an error. |
| 4 | Faithfulness: span-containment + Option-A fallback | `test_entails_false_when_addressed_span_does_not_contain_claim`, `test_unaddressed_trace_is_structural_fallback_entailed`, `test_entails_false_for_untraced_claim`, `test_enforce_default_now_rejects_addressed_unentailed_claim` | **adversarial-fires** | **The chain's weakest link (05 verdict):** an un-addressed trace passes with NO content check. Teeth are opt-in by the producer. |
| 5 | Hole A — numeral-free non-claims content | `test_authored_prose_is_numeral_free`, `test_kpi_numbers_are_sourced_to_endpoints` | **adversarial-fires** | Composer-only, test-side regex — NOT an in-model invariant; any other Surface producer bypasses it. |
| 6 | Hole B — all traces addressed (loader + composer) | `test_every_emitted_trace_is_addressed`, `test_untraced_and_unaddressed_claims_are_routed_to_missing` | **adversarial-fires** | Closed at two producers, not in the type; Rev1 `Claim` still permits un-addressed traces. |
| 7 | Byte-stable determinism | `test_load_is_byte_stable`, `test_two_composes_are_byte_identical`, `test_determinism_with_repeated_value_across_lanes`, `test_committed_equals_fresh_build` | positive-only | Enforced per-caller, not in the type: `capture.build_report` / `worksurface.build_work_report` inherit `now()` and are NOT byte-stable (latent trap; semantic.py frozen). |
| 8 | AI-optional core | `.venv/bin/lint-imports` + `test_*_imports_no_ai` (×4) + bare-install CI + `test_no_ai_pydantic_plugin_active` | adversarial-fires (runtime) / structural (linter) | Two-layer by necessity: the static contract cannot see pydantic-plugin auto-activation; runtime guard closes it. |
| 9 | No-write-back problem boundary | `test_problem_loads_no_external_module`, `test_problem_api_has_no_write_back_method`, `test_transition_human_gated_empty_actor_raises`, `test_spine_unchanged_by_problem` + `lint-imports` | **adversarial-fires** | API allow-list is a substring scan — a write-back method named outside `WRITE_BACK_SUBSTRINGS` would evade it. Real bypass found+closed this milestone (`89e0947`). |
| 10 | Three state axes never collide | `test_problemstate_distinct_from_reviewstate`, `test_lifecycle_verb_collides_with_no_axis_verb` | structural | Proves disjoint enums/verbs, NOT free-text copy — the compass still says "one promotion chain" (drift → R8). |
| 11 | Private corpus never serialized | `test_private_corpus_not_serialized_into_surface`, `test_corpus_emphasis_orders_without_leaking`, `test_render_does_not_leak_private_corpus` | positive-only (value-scan) | Field-name absence scan, not a schema proof (holds structurally: Surface has no Corpus field). |
| 12 | Read-anchored coverage identity (loader feeder) | `test_no_yaml_scalar_is_read_but_undisclosed`, `test_coverage_lying_completeness_rejected` | positive-only (cross-checked) / adversarial (coverage half) | The identity-`RuntimeError` raise path itself is never forced (R1 structural #1). |

**Ledger row count: 62** (50 v1.1-surface rows + 12 invariant rows).

---

## Part 2 — Unguarded promises (no test, or only vacuous/structural cover)

Each entry: promise → why it is unguarded → concrete one-test remediation.

**Already-found (rounds 1–4), re-confirmed at this SHA by body-read:**

1. **Δ==0 / point-in-time no-FALSE-disclosure arm (module).** The corpus carries `throughput-index [15,15]` (Δ==0) and a `value:`-only KPI; live drive shows `surface.missing` stays silent for them — but no test *asserts the absence* of a disclosure. (R3 structural #3.) **Remedy:** `assert not any("throughput-index" in m or <point-in-time phrasing> in m for m in build_module_surfaces()[0].missing)`.
2. **Empty `pr_body_sections` makes the fallback guard VACUOUS.** `test_config_carries_no_boilerplate_pr_sections` iterates `[]`, asserting nothing (row 43). (R4 #1.) **Remedy:** add a fixture section with a `no known …` fallback and assert the guard's rule rejects it (test the predicate, not just live config).
3. **Single-config `sorted(glob("*.yml"))[0]` discovery.** `modulesite._discover_config` (modulesite.py:77) silently builds only the alphabetically-first config if a second `*.yml` appears; never tested. (R3 #2.) **Remedy:** write two `*.yml` into a tmp corpus, assert `_discover_config` either raises or is documented to pick one deterministically (pin the actual behavior).
4. **Zero-lane config through the builder/CLI.** Empty binding set is tested at the composer (row 23) but never end-to-end through `build_module_surfaces`/`build_module_site` (discovery→render→gate). (R3 #3.) **Remedy:** a tmp lane-less config driven through `build_module_site(tmp)` asserting a valid Draft page + populated honesty panel.

**New finds this round:**

5. **Quote-slot faithfulness teeth are unproven (the quote-path twin of Hole B).** `_quote_block` returns `None` for an untraced/unaddressed quote (compose.py:274 `if quote is None or not _addressed(quote)`), routing to the `_QUOTE_ABSENT_NOTE` disclosure — a real trust gate. But `test_unowned_and_sourced_quote_honesty` only plants *no quote* and *addressed quotes*; an **un-addressed/untraced quote is never planted**, so the `not _addressed(quote)` branch is un-fired (positive-only, row 24). This is exactly the arm the Hole-B guard proves for ClaimsBlock claims but the quote slot does not. **Remedy:** one arm in the existing test — pass `quote=Claim(text="x", evidence=[Trace(source_id=...)])` (un-addressed) and assert NO `QuoteBlock` is emitted AND `_QUOTE_ABSENT_NOTE` is in `surface.missing`.
6. **Multi-trace quote claim.** `_addressed` checks `all(t.is_addressed …)`, so a quote with several traces is handled — but no test drives it (R2 unvalidated #3, re-confirmed). **Remedy:** fold a 2-trace quote into the quote test; assert verbatim render + all-addressed acceptance.
7. **Ledger collision / R-NNN namespace across corpora.** Each corpus uses its own `ids.json` (module: `content/module/ids.json`; work: its own), so R-NNN cannot collide **by construction** — but nothing asserts the two ledgers are independent or that a second slug in one ledger namespaces correctly. Combined with the shared-fixed-path caveat (R3 #4), this is untested cross-corpus. **Remedy:** build both corpora into tmp, assert each surface's `ref` is drawn from its own corpus ledger (no cross-write).
8. **`compute_delta` locale / thousands-separator + mixed-unit silent mis-parse.** Verified live (R2 unvalidated #1): `compute_delta("1,500","2,000") → "+1"` (real change 500) because `,500`≠`,000` are read as *units* and dropped; mixed units drop silently with no disclosure. Latent (config uses plain numbers) but wholly unguarded and faithfulness-adjacent. **Remedy:** either a guard asserting a thousands-separator/mixed-unit pair raises-or-discloses, or a documented input-precondition test pinning the current (surprising) behavior.

**Structural-only, teeth un-fired (guarded shape, but the failing edge is never exercised):**

9. **Read-anchored identity `RuntimeError` raise path** (swimlane.py:548) — asserted to HOLD, never forced to fire (R1 structural #1). **Remedy:** monkeypatch the walk to drop a scalar; assert `RuntimeError`.
10. **`safe_load`-only unreachability of `yaml.load`** — structural-only (row 50). **Remedy:** feed a `!!python/object/apply:os.system` payload through `load_config`; assert it does NOT execute (safe_load rejects the tag).
11. **Voice contract "revert-a-line → RED" ritual** — never run for ship.md this milestone (row 44; R4 structural #1). **Remedy:** the manual honesty ritual, or a meta-test that mutates a copy of ship.md and asserts the guard goes red.

**Verified guarded WITH teeth (checked because the brief flagged them as suspects — they are NOT gaps):**

- **Render honesty-panel CONTENT assertions** — `test_render.py::test_honesty_panel_lists_missing_and_unextracted` asserts the actual `missing[]` text, the drop locator, AND the reason string appear in the HTML (not just `class="honesty"`); `test_honesty_panel_clean_surface_shows_positive_confirmation` pins "Fully traced"; `test_modulesite.py::test_single_endpoint_disclosure_visible_in_html` asserts the full escaped entry. Content is genuinely guarded.
- **Compose quote-path multiplicity of the *rendered* text** — the omit/owner/unassigned arms ARE covered (row 24); only the *un-addressed-quote* and *multi-trace* arms are missing (items 5–6 above).

---

## Part 3 — Consolidated backlog (recorded-not-fixed, rounds 1–6 + new)

Class legend: **code-doc drift** · **unguarded arm** · **spec drift** · **process**.
Owner legend: **fix-batch** (one gated PR of guard tests) · **R8 compass** (Round-8 ontology/compass sweep) · **maintainer** (decision, not a code change).

| # | Item | Round | Class | Remediation (one line / one test) | Owner |
|---|------|-------|-------|-----------------------------------|-------|
| B1 | Two stale `swimlane.py` docstrings (post-`efb635a`: `value:` KPI endpoint count) | R1 | code-doc drift | Edit the two docstrings to state `value:` → 0 endpoints (movement-form-only). | R8 compass |
| B2 | Read-anchored identity `RuntimeError` raise path never fired | R1 | unguarded arm | `test`: monkeypatch walk to drop a scalar → assert `RuntimeError` (swimlane.py:548). | fix-batch |
| B3 | `safe_load`-only unreachability of `yaml.load` untested | R1 | unguarded arm | `test`: feed `!!python/object/apply` payload through `load_config` → assert no exec. | fix-batch |
| B4 | Zero-endpoint compose arm (`kpi_endpoints=[[]]`) untested | R2 | unguarded arm | `test`: compose a binding with `kpi_endpoints=[[]]` → assert `delta is None` and NO movement note. | fix-batch |
| B5 | `compute_delta` mixed-unit / thousands-separator silent mis-parse | R2 | unguarded arm | `test`: pin/guard `compute_delta("1,500","2,000")` behavior (raise-or-disclose). | fix-batch |
| B6 | Multi-config `sorted(glob)[0]` discovery silently picks one | R3 | unguarded arm | `test`: two `*.yml` in tmp corpus → assert `_discover_config` raises or pins the pick. | fix-batch |
| B7 | Zero-lane config unexercised through builder/CLI | R3 | unguarded arm | `test`: lane-less tmp config through `build_module_site` → valid Draft + populated `missing`. | fix-batch |
| B8 | Δ==0 / point-in-time no-FALSE-disclosure arm not asserted (module) | R3 | unguarded arm | `test`: assert those phrasings ABSENT from `build_module_surfaces()[0].missing`. | fix-batch |
| B9 | Shared-ledger fixed-path hermeticity (build writes committed `ids.json` regardless of out_dir) | R3 | process | Thread ledger path through `out_dir` for true hermeticity (design change, not a test). | maintainer |
| B10 | Draft-vacuity of `check --corpus module` clean pass | R3 | unguarded arm | Accept as documented (no committed Published surface by design); teeth already in the blocker test. | maintainer |
| B11 | ROADMAP "five-vs-six sections" text vs the shipped 6-section dispatch | R4 | spec drift | Edit ROADMAP/spec to say six sections (Start here + five). | R8 compass |
| B12 | `config.json` empty `pr_body_sections` makes fallback guard VACUOUS | R4 | unguarded arm | `test`: add a fixture section with a fact-asserting fallback → assert the rule rejects it. | fix-batch |
| B13 | Voice guard "revert-a-line → RED" ritual never run for ship.md | R4 | process | Run the manual honesty ritual, or a meta-test mutating a ship.md copy. | fix-batch |
| B14 | Voice guards validate contract TEXT, never a generated body | R4 | process | Named future hardening: a body-linter over `generate_pr_body` output (out of milestone scope). | maintainer |
| B15 | Compass "one promotion chain" phrasing vs the 3-axis / "fan-out" ontology | R5 | spec drift | Rewrite the WHERE-WE-ARE decisions-log line to "fan-out chain"; distinct from Problem ladder. | R8 compass |
| B16 | PR #9 footer nuance — harness-appended (not phase output) | R4/R5 | process | Note in retro that PR #9's footer is harness-appended; no code/spec change. | maintainer |
| B17 | 5 config-toggle recommendations (verifier/nyquist/code_review/security/ui promised vs ran) | R6 | process | Present toggle-change recommendations to the maintainer (no unilateral flips). | maintainer |
| B18 | **NEW: quote-slot faithfulness teeth unproven (un-addressed quote → omit+disclose)** | R7 | unguarded arm | `test`: pass an un-addressed quote `Claim` → assert NO `QuoteBlock` + `_QUOTE_ABSENT_NOTE` in `missing`. | fix-batch |
| B19 | **NEW: multi-trace quote claim unexercised** | R7 | unguarded arm | `test`: a 2-trace addressed quote → assert verbatim render + acceptance. | fix-batch |
| B20 | **NEW: ledger R-NNN independence across corpora untested** | R7 | unguarded arm | `test`: build module + work into tmp → assert each `ref` drawn from its own ledger (no cross-write). | fix-batch |

**Backlog item count: 20** (B1–B20; B18–B20 new this round).

---

## Deepest-learning summary (3 sentences)

The v1.1 test net has genuine teeth exactly where the milestone chose to prove things — Hole A, Hole
B, no-auto-publish, the abstraction guard, the AI-optional bare-install, the synthetic-content
scanner, and the module merge-gate blocker are all **adversarial-fires** guards that plant a
violation and prove rejection — but a consistent, honest pattern runs through every gap: the guards
prove the *happy path holds* far more often than they prove the *failing edge fires*, so the
"prove-it-FIRES" discipline is applied to the headline invariants and left off the quieter arms
(the zero-endpoint delta, the un-addressed quote, the identity `RuntimeError`, the vacuous config
fallback). The single most important new finding is that the **quote slot is the one producer path
with a real trust check (`_quote_block` rejects an un-addressed quote) that has no adversarial guard
at all** — it is Hole B for quotes, un-proven — which fits the Round-5 verdict precisely: the
chain's automated teeth are conditional on being *exercised*, and the unexercised arms are where an
untrusted producer (or a careless refactor) would slip through. The backlog is dominated by
**unguarded arms with one-test remedies** (12 of 20), which means the honest close here is not "the
suite is weak" but "the suite is a well-sampled core with a named, cheap-to-close fringe" — and the
fringe should be closed as one fix-batch PR of guard tests, not smoothed over as already-green.
