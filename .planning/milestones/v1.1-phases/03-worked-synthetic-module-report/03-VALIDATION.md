---
phase: 3
slug: worked-synthetic-module-report
status: retroactive
nyquist_compliant: true
wave_0_complete: true
created: 2026-07-02
---

# Phase 3 — Validation Strategy (retroactive)

> Retroactive validation audit (2026-07-02), written for the deep-review loop (Round 3). Maps each
> Phase-3 requirement to how it is validated on current HEAD
> `e68bad281866a4434b03943ad2156e493320b58e`: **test-validated** (an executable assertion drives the
> live builder/gate over the committed corpus), **structurally validated** (guaranteed by
> construction/reuse, no test forces the edge), or **unvalidated** (an honest edge no test or
> structure currently covers). Judgment derived honestly — gaps stated plainly, not papered over.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (`.venv`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `.venv/bin/pytest tests/test_modulesite.py tests/test_module_cli.py -q` |
| **Full suite command** | `.venv/bin/pytest -q` |
| **Live gate command** | `.venv/bin/newsletters check --corpus module ; echo exit=$?` |
| **Estimated runtime** | ~0.20 s targeted (12 tests); ~11.5 s full (623 tests) |

---

## Sampling Rate (as executed)

- **Per task:** each 03-0X task carried an inline `python -c` acceptance probe (03-01 loader/builder
  probes; 03-02's CliRunner `check --corpus module` exit-0 probe) or a scoped `pytest -k` run
  (03-03's test tasks). Recorded verbatim in each SUMMARY.
- **Per plan:** full `.venv/bin/pytest -q` (605 after 03-01; 608 after 03-02's 3 CLI tests; 617 after
  03-03's 9 modulesite tests).
- **In-phase fixes** (`851ccf5`, `e566bfb`) each re-ran the full suite green — the abstraction guard
  drove both (see VERIFICATION §"The abstraction-guard drift").
- **Max feedback latency:** < 12 s (full suite).

---

## Per-Requirement Validation Map

| Requirement | Behavior | Validation kind | Evidence / Command | Status |
|-------------|----------|-----------------|--------------------|--------|
| MODA-01 | Config → load → compose → render end-to-end; every ClaimsBlock claim traced + content-addressed (Hole B) | **test** | `test_every_claim_traced_and_addressed` (positive: every kept claim `is_traced` + every trace `is_addressed`; body non-empty, `missing` non-empty — Pitfall 11) | ✅ green |
| MODA-01 | Populated honesty panel VISIBLE in rendered HTML (single-endpoint disclosure) | **test** | `test_single_endpoint_disclosure_visible_in_html` (locates the disclosure by composer phrasing, asserts the full escaped entry + `class="honesty"` + `class="claim-span"` in the HTML) | ✅ green |
| MODA-01 | Owner quote rendered from the SOURCED path (not fabricated, not omitted) | **test** | `test_owner_quote_rendered_from_sourced_path` (reads the composed `QuoteBlock` text, asserts escaped-present in HTML) | ✅ green |
| MODA-01 | Zero external calls / self-hosted fonts | **test** | `test_no_external_calls` (no google-fonts host, no `src="http"`, no CSS `url(http`, no `<link href="http">`; `fonts/*.woff2` present) | ✅ green |
| MODA-01 | Committed content is synthetic (fabricated naming only) | **test (adversarial)** | `test_committed_content_is_synthetic` (denylist of real-name shapes + `_EMAIL_RE` over `.yml`+`site/*.html`+`ids.json`; positive fabricated-marker assert; non-vacuous planted `Jean-Luc Picard`/`ops@starfleet.int` self-check) | ✅ green |
| MODA-01 | KPI movement mix populates the honesty panel honestly (up/down/Δ==0/single-endpoint/point-in-time/zero-KPI) | **structural + test** | Config `content/module/module-a.yml` carries the mix; live drive: `surface.missing` = exactly the single-endpoint + zero-KPI disclosures (a Δ==0 and a point-in-time KPI correctly produce NO disclosure) | ⚠️ partial — the *absence* of a false disclosure on the Δ==0 / point-in-time arms is not directly pinned (see Structurally-Validated #3) |
| MODA-02 | `check --corpus module` clean → exit 0 | **test** | `test_check_module_clean_exits_zero` (+ live `newsletters check --corpus module` exit 0) | ✅ green (Draft-vacuous — see Unvalidated Edges #1) |
| MODA-02 | Same UNFORKED gate fires on a planted blocker → nonzero | **test (adversarial)** | `test_check_module_blocks_on_planted_blocker` (in-memory PUBLISHED unentailed surface via monkeypatch → nonzero + `BLOCK`/`merge blocked`/surface id) | ✅ green |
| MODA-02 | `build --corpus module` routes to `build_module_site` | **test** | `test_build_module_smoke` (writes `report-module-a.html` + `library.html` under `--out`) | ✅ green |
| MODA-02 | Own dedicated `content/module/ids.json` ledger, first ref R-001 | **test** | `test_r001_stable_across_rebuild` (fresh tmp ledger → `R-001`; reload+rebuild → same ref, append-only proven by rebuild) | ✅ green |
| MODA-02 | SITE-06 byte-stable double-render over the module corpus | **test** | `test_byte_stable_double_render` (identical file set + byte-identical every file across two builds) | ✅ green |
| MODA-02 | Committed `content/module/` == a fresh build | **test** | `test_committed_equals_fresh_build` (fresh build reproduces every committed file byte-for-byte; committed ledger unchanged) | ✅ green |
| MODA-01/02 | Determinism: no `datetime.now()` reachable | **test** | `test_no_datetime_now_reachable` (`Surface.created` + every `Source.timestamp` == `EPOCH_ZERO`) | ✅ green |
| MODA-01 | rev1/work code paths unchanged; `review.py` untouched | **structural** | cli.py additive `elif` branches; `git diff` clean on `review.py` (Round-2/Phase-2 gate-untouched norm) | ✅ by construction |

---

## Structurally-Validated (guaranteed, not test-driven)

Correct by construction/reuse, but **no test forces the edge** — they survive a refactor only as long
as the construction holds:

1. **Claim-beside-verbatim-trace / honesty-panel rendering is REUSED, not re-implemented.** The
   PROV-03 devices come from `render.py` (Phase 9/10). `test_single_endpoint_disclosure_visible_in_html`
   proves they fire over module content, but the rendering *devices themselves* are guarded in
   `test_render.py`, not here — Phase 3 validates the reuse, not the renderer.

2. **XSS escaping of config content into HTML (T-03-02)** is guaranteed by `render.py`'s existing `_e`
   escaping (the threat register's mitigation is "reuse verified, not re-implemented"). No Phase-3 test
   plants a `<script>` in the config and asserts it is escaped in the output; the escaping is inherited
   from the renderer's own guards. Honest structural reliance, not a Phase-3 assertion.

3. **The Δ==0 and point-in-time KPI arms correctly produce NO false disclosure.** The config includes
   `throughput-index [15,15]` (Δ==0) and `transfer-readiness value: 88` (point-in-time). Live drive
   confirms `surface.missing` contains ONLY the single-endpoint + zero-KPI entries — i.e. these two
   arms correctly stay silent. But no Phase-3 test *asserts the absence* of a disclosure for them; the
   silence is verified structurally + by live drive (and the loader-level movement-form-only contract
   is guarded in Phase 2's `test_swimlane_endpoints`). This is the Phase-3 echo of Round 2's
   "zero-endpoint compose arm" gap. **Recommend:** one guard asserting no `throughput-index`/point-in-time
   phrasing appears in `surface.missing`.

4. **`_select_owner_quote` fallbacks (quote absent / no matching traced claim / non-dict config)** are
   coded explicitly (modulesite.py:98-109 return `None`, letting the composer disclose the omission)
   but no Phase-3 test drives the omit path over the module builder — the committed config always has a
   matching quote, so only the happy path is exercised. The sourced-or-omit *composer* logic is guarded
   in Phase 2's `test_unowned_and_sourced_quote_honesty`.

---

## Unvalidated Edges (honest gaps — no test AND no structural guarantee)

1. **Draft-scope vacuity of `check --corpus module` clean pass.** The clean corpus exits 0 only
   because its single surface is `Draft` (exempt). No committed *Published* module surface exercises
   the gate positively; the gate's teeth are proven solely by the monkeypatched blocker. Latent, by
   design (the report stays Draft) — but the clean direction validates nothing.

2. **Multi-config corpus / ledger collision.** `_discover_config` returns `sorted(glob("*.yml"))[0]`
   — if a SECOND `*.yml` were added under `content/module/`, only the alphabetically-first would build,
   silently. And both configs would share the single `content/module/ids.json`; a second surface slug
   would get its own `R-NNN` in the same ledger, but nothing tests two-config coexistence, slug
   collision, or the discovery-picks-one behavior. Corpus is one-config-by-design, so latent — wholly
   unvalidated.

3. **Config with zero lanes at the CLI/builder level.** Phase 2 tests an empty lane set at the
   *composer* level (`test_empty_lane_set_is_a_valid_draft_with_populated_missing`), but no Phase-3
   test drives `build_module_surfaces`/`build_module_site` over a lane-less module config end-to-end
   (through discovery → render → gate). The path would degrade gracefully by construction, but is
   unexercised over the real builder.

4. **Shared-ledger-path hermeticity under concurrency / non-idempotent state.** `build_module_site`
   writes its ledger to the fixed `content/module/ids.json` regardless of `out_dir`. Every test that
   calls it re-saves that tracked file; safety rests entirely on save-idempotence (re-verified clean
   this round). If two builds ran concurrently, or if the committed ledger were ever out of sync with
   the config's slug, a test build could dirty the tree. No test covers the non-idempotent case; a
   future hardening would thread the ledger path through `out_dir` for true hermeticity (noted in
   03-03-SUMMARY §Concerns as out-of-scope for the test-only plan).

5. **raw.githack / GitHub-Pages link rot: N/A this phase.** The module Library is fully self-hosted
   (zero external call, verified) — there is no external-link surface to rot. The cross-corpus Library
   merge that *would* introduce public links is explicitly DEFERRED (03-CONTEXT §Deferred); the module
   corpus ships its own self-contained site, like `content/work/`. No gap, recorded for completeness.

---

## Nyquist Compliance (honestly derived)

**nyquist_compliant: true** — both MODA requirements have at least one executable, non-vacuous test
driving the live builder/gate over the committed corpus, and the two trust-critical directions (the
gate FIRES on a planted blocker; committed content is provably synthetic) are each closed by a guard
proven to fire on a planted violation. The determinism/integrity core — byte-stable double-render,
committed==fresh, R-001 append-only stability, EPOCH_ZERO — is sampled at commit granularity and
cannot silently regress.

The gaps above are **edges around a well-sampled core**, not core blind spots. The two behavioral
silences lacking a direct Phase-3 assertion (the Δ==0 / point-in-time no-false-disclosure arm; the
quote-omit fallback) are each covered structurally, at the loader/composer level (Phase 2 guards), and
by live drive — the same disposition Rounds 1–2 gave the loader's `RuntimeError` arm and the composer's
zero-endpoint arm. The Draft-vacuity and shared-ledger-path edges are honest, disposed caveats (design
choices, idempotence re-verified), not silent risks. The multi-config discovery ambiguity is latent on
a one-config-by-design corpus. None rises to a Nyquist violation; each is logged as a recommended
future guard rather than a false "validated."

---
*Validation audit: 2026-07-02 (retroactive, deep-review loop Round 3)*
*Auditor: Claude (Bureau Chief)*
