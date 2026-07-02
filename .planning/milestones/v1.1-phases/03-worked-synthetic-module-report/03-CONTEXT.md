# Phase 3: Worked synthetic Module Report - Context

**Gathered:** 2026-07-02
**Status:** Ready for planning
**Source:** Stage-A milestone seed §5/§6.3 + research + Phases 1–2 as-built
(discuss skipped — decisions LOCKED)

<domain>
## Phase Boundary

A committed synthetic `module-a` config composes and renders **end-to-end** (loader → composer →
ledger → render → Library): a third `module` corpus with its own ledger, gate-visible
(claim-beside-verbatim-trace + populated honesty panel), byte-stable, `newsletters check
--corpus module` wired. Requirements: MODA-01, MODA-02.

**Method-docs sub-task is SKIPPED** — the companion files (`_incoming/`) are absent from the
workspace; the PR body must note this per seed §6.3. Do not fabricate them.

</domain>

<decisions>
## Implementation Decisions (LOCKED)

### The worked example config (MODA-01)
- One committed YAML config for `module-a` in the fabricated naming scheme, per seed §5:
  module `module-a`, area `area-bem`, the §4 worked-example lane set — **Safety & Culture,
  MA (incl. MA cost), Quality, VF Transfer, MOR/IQ tools & defect projects** — with owners
  `owner-safety|owner-ma|owner-quality|owner-vf|owner-mor`, engineers `eng-01…`, tools
  `toolset-1…`, **fabricated metrics only**. Nothing resembling real fab/tool/metric/site/
  program nomenclature. No colleague names.
- These specifics live ONLY in the config + rendered content — the abstraction guard keeps them
  out of `src/` (its denylist already covers this scheme; src additions must stay generic).
- Config location: under `content/module/` (e.g. `content/module/module-a.yml`) — the corpus is
  self-contained like `content/work/`. Exact filename Claude's discretion.
- Include per-KPI period movement (`values: [start, close]` — at least one up, one down, one
  Δ==0, one declared-but-single endpoint so the honesty panel is POPULATED honestly), at least
  one lane with no KPIs, and a traced module-owner quote (so the sourced path renders) — the
  point is a gate-visible example exercising the real contract, not a happy-path brochure.

### Site build (MODA-01/02)
- Mirror `worksurface.build_work_site` (the Phase-11 precedent): a `build_module_site()` that
  loads the config, composes via `compose_module_report`, persists the ledger
  (`content/module/ids.json`, first ref R-001 — the caller-owns-save decision from 02-03), and
  renders into `content/module/site/` REUSING `render.py` (no new renderer, no fork). Where the
  builder lives is Claude's discretion (suggest compose.py or a thin `modulesite` seam inside
  the existing module set — but render.py/site.py/worksurface.py stay UNEDITED unless the edit
  is provably additive and gate-safe; prefer zero edits to existing modules).
- Claim-beside-verbatim-trace + honesty panel come free from `render_surface` (PROV-03) —
  verify they are actually populated in the module output (test), don't just assume.
- Self-hosted fonts / zero external calls: reuse the Phase-11/12 shared assets exactly as
  build_work_site does; a no-external-call check over the new output.
- Committed rendered output == fresh build (the committed==fresh-build norm from Phase 11/12);
  byte-stable double-render over `content/module/site` (SITE-06 extended to the new corpus).
- The quote wiring (02-03 hand-off): the builder selects the module-owner quote claim from the
  loaded config (a generic structural key, e.g. `quote:`/`owner:` at module level — keys are
  Claude's discretion, generic only) and passes it to `compose_module_report(quote=, owner=)`.

### CLI + gate (MODA-02)
- `newsletters check --corpus module` and `newsletters build --corpus module` (or the live
  equivalent — READ cli.py's actual --corpus shape first) route to the module corpus and run
  the SAME unforked `review_blockers` gate. cli.py edit is allowed but ADDITIVE-ONLY (extend the
  corpus choices; never fork the gate; review.py untouched).
- Gate proof both ways: exit 0 on the clean corpus; nonzero on a PLANTED blocker (a gate that
  only sees clean input proves nothing — Phase-10/11 norm).
- The composed report ships in `Draft` (review state) — like the work corpus, `check` passes
  vacuously on published-only scope; note this honestly in the PR (same caveat as Phase 11).

### Testing
- End-to-end: config → load → compose → render; every claim traced+addressed; honesty panel
  lists the planted single-endpoint disclosure + any quote/lane gaps; R-001 stable across
  rebuilds (ledger append-only proven by rebuild).
- Synthetic-name confidentiality check over committed `content/module/` (the fixture scheme +
  no real-looking nomenclature — a denylist/allowlist test per PITFALLS #confidentiality).
- Byte-stable double-render; no-external-call; committed==fresh-build.
- Determinism: the whole build must be reproducible (EPOCH_ZERO everywhere; no now()).

### Claude's Discretion
- module-a KPI/metric names & values (fabricated, plausible-generic like "throughput-index");
  lane descriptions; quote text (attributed to `owner-…`, no real-sounding names).
- Builder placement + config key for the quote; test file layout.

</decisions>

<canonical_refs>
## Canonical References

### Live code (read before planning/implementing)
- `src/newsletters/worksurface.py` — build_work_site: THE structural template for this phase
- `src/newsletters/compose.py` — as-built composer API (quote=/owner=/ledger= kwargs)
- `src/newsletters/swimlane.py` — as-built loader (config schema keys it actually recognizes)
- `src/newsletters/cli.py` — the LIVE --corpus routing to extend additively
- `src/newsletters/render.py` + `site.py` — reuse-only (render_surface devices, Ledger)
- `tests/test_worksurface.py` — the corpus-level test patterns (gate fires both ways,
  no-external-call, byte-stable, committed==fresh)
- `content/work/` — the corpus layout to mirror (ids.json + site/ + fonts)

### Research & rules
- `.planning/research/SUMMARY.md` + `PITFALLS.md` (Phase-3 set: ledger path, confidentiality,
  byte-stability on committed content); ROADMAP Phase 3 success criteria; CLAUDE.md hard rules.

</canonical_refs>

<specifics>
## Specific Ideas

- Gate policy as before (enforced set green; advisory no-new-failures; isort --profile black).
- One task = one atomic commit; push every task.
- FORBIDDEN: conftest, existing tests, .importlinter, ci.yml, faithfulness/coverage/semantic/
  templates/models; render.py/site.py/review.py/worksurface.py reuse-only (zero edits
  preferred; any edit must be additive + justified in the SUMMARY).

</specifics>

<deferred>
## Deferred Ideas

- Method docs into docs/method/ (files absent — noted in PR, not fabricated).
- Main-Library integration of the module corpus (the corpus has its own site, like work);
  cross-corpus Library merge is future work.
- Owner-audit review routing (DEF-04); publishing the module report (stays Draft).

</deferred>

---

*Phase: 03-worked-synthetic-module-report*
*Context gathered: 2026-07-02*
