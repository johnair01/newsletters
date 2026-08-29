# Project Milestones: Newsletters

## v1.2 The Published Record (Live: 2026-07-03 · Formally closed: 2026-08-29)

**Delivered:** The published site became a product output — the rendered record IS the site,
republished by ONE automated channel from `main` only, with the linkability/drift/gating
invariants enforced as PR-blocking tests instead of discipline. Merged as PRs #20+#21; deploy
run #5 was the first successful automated Pages publish in the repo's history; post-merge UAT
live-verified (all URLs 200, styled 404, marker, single gh-pages publish commit @ `528d092`).
EiC pages review re-verified live and approved 2026-08-29 (recorded decision at v1.3 kickoff).

**Phases completed:** 2 phases, 2 plans (Phase 1 verified 5/5, Phase 2 verified 4/4)

**Key accomplishments:**

- **Site IA & linkability (PUB-03):** cross-corpus **Records strip** on chrome pages only
  (design-system tokens, per the `signals-navigation` handoff: *no surface a dead-end*), a
  design-system **404** renderer with base-path-absolute hrefs/fonts, and the live dead-nav bug
  (`home_href`) caught by the new assembled-tree test on its first run and fixed at the renderer.
- **One publish channel (PUB-01/02):** stdlib `publish.assemble_site` / `newsletters assemble`
  composes the committed corpora byte-verbatim (rev1→root, `/work/`, `/module/`, `.nojekyll`,
  404) — what was reviewed is what publishes; fails loudly on a missing corpus.
- **Invariants as CI (PUB-04/05):** `tests/test_publish.py` codifies four guarantees (assembled
  links resolve · committed==fresh for ALL corpora + append-only ledgers · fonts shipped with
  OFL · marker everywhere) as the PR-blocking `site-integrity` job; merge-block gates all three
  corpora; bare-install untouched.
- **`deploy-pages.yml` rewritten:** gate-then-force-push `gh-pages` from `main` only (re-runs
  `newsletters check` ×3 + test_publish before any push); no `web/` build, no third-party
  action, warn-only Pages-source preflight.
- **`web/` design preview fixed & deployed under `/web/`** (round 2): real Instrument Sans
  500/600 (the design bundle's were byte-copies of 400), bundler-managed font URLs, env-driven
  basePath, dark tokens restored, `web-ci.yml` gate — DEF-13 amended (labeled preview under the
  record's URL), not broken.

**Interstitial (post-v1.2 window, pre-v1.3):** the **Case Spec authoring path** (PR #24,
2026-07-09) — hand-authored YAML lifted through the zero-AI spine; author's text byte-verbatim
with real-span traces; `config:` bound, never claimed. Recorded here so no work is orphaned
between milestone entries; it is a load-bearing precedent for v1.3's Weekly Spec.

**Known deferred items at close:** DEF-01..12 (carried), DEF-13 (wire `web/` to real data),
DEF-14 (environment deploy channel iff maintainer aligns repo settings), B1–B20 fix-batch
(maintainer-gated), `v1.1` tag still local-only (git proxy drops tag pushes).

---

[Entries in reverse chronological order — newest first]

## v1.1 Swim-Lane Module Report (Shipped: 2026-07-02)

**Delivered:** The missing config-driven Report composer — a traced YAML loader, a pure module-scope
composer, a worked synthetic `module-a` corpus rendered into the Library, and a Signals-voice `ship`
contract — bolted onto the existing trust spine, all deterministic and AI-optional.

**Phases completed:** 1–4 (12 plans total)

**Key accomplishments:**

- **Traced YAML loader (`swimlane.py`):** a module-config file becomes a verbatim-transcript `Source`
  + one `SectionBinding` per lane, with every scalar minted via `Trace.from_source` or routed to
  `unextracted[]` under a read-anchored coverage identity **enforced in code** (`RuntimeError` on any
  silent drop). PyYAML lives behind a lazy `[config]` extra; a bare `pip install .` runs the spine
  yaml-free (LANE-01..04).

- **ABSTRACT-EVERYTHING made executable:** the abstraction guard (a denylist source-scanner) fired
  **3× on real leaks** and out-enforced the plan's own suggested defaults — the strongest evidence in
  the repo that the principle is a live invariant, not an aspiration (LANE-03).

- **Module-scope composer (`compose.py`):** a pure `compute_delta` + a kind-agnostic
  `compose_module_report` assemble `SectionBinding[]` into a **byte-stable Draft REPORT `Surface`** —
  per-lane KPI strip (Δ at compose time into `KpiItem.delta`, never a fabricated 0) + traced claims,
  honest `missing[]` routing, stable `R-NNN`. Research Holes A + B closed **at the composer** with
  adversarial planted-cheat guards; no-auto-publish proven on the composed surface (COMP-01..04).

- **Worked synthetic Module Report:** a committed `module-a` config composes + renders end-to-end
  (loader → composer → ledger → render → Library) into a self-contained `content/module/` corpus with
  its own R-001 ledger, 33 claim-beside-verbatim-trace rows, a populated honesty panel, and a
  byte-stable committed==fresh-build guarantee; `newsletters check --corpus module` runs the same
  unforked merge-block gate (MODA-01..02).

- **Signals-voice `ship` contract:** PR bodies now read as evidence-first six-section dispatches
  (Start here / signal / learned / verified-verbatim / not-here-yet / how-to-verify), gate output
  byte-verbatim, guarded against silent installer clobber — dogfooded on the loop's own PRs (VOICE-01/02).

- **Formal GSD close (deep-review loop, 10 rounds):** reconstructed every missing per-phase
  VERIFICATION/VALIDATION/LEARNINGS under fresh adversarial eyes, plus four cross-cut reviews
  (trust invariants, config reconciliation, tests-as-promises, ontology/drift) — turning
  "shipped" into "closed."

**Stats:**

- 4 phases, 12 plans, ~23 tasks
- 12/12 v1.1 requirements satisfied (LANE·COMP·MODA·VOICE ×2–4 each)
- Test growth: **574 → 626** (587 at Phase-1 merge → 623 at Phase-4 merge → 626 after the loop's
  Round-9 collaboration guard); 2 import contracts KEPT; 3 byte-stable corpora

- **Build PRs:** #4 (`07f1a60`) · #5 (`22396ce`) · #6 (`65bbea8`) · #7 (`57b79f8`) · #8 (`fd96ea0`)
- **Deep-review close PRs:** #9–#16 (per-phase triads #10/#11 + cross-cut reviews #12–#15 +
  collaboration contract #16); this close is PR #17

- 1 day (functional build overnight 2026-07-02; formal close same day via the deep-review loop)

**Git range:** `feat(01)` `07f1a60` → `feat(04)` `fd96ea0` (build); `docs(close)` deep-review Rounds 1–10

**Known deferred items at close:** 12 (DEF-01..12, below) + the B1–B20 unguarded-arm backlog
(`reviews/2026-07-02-deep-review/07-tests-as-promises.md`).

**Known gaps (accepted, recorded — see `milestones/v1.1-MILESTONE-AUDIT.md`):**

- Process: the verifier + Nyquist artifacts were **backfilled** by the loop (never ran at build time);
  the REQUIRED `code_review_gate` and `security_enforcement` **never ran** (no `*-REVIEW.md`/`SECURITY.md`);
  per-phase RESEARCH skipped. Maintainer decision to run them per-phase going forward (reviews/06).

- Honest trust limits: the faithfulness gate's **Option-A structural fallback** is the chain's
  weakest link (an un-addressed trace passes with no content check) and **Hole A is composer-only** —
  both must be hardened before an untrusted AI producer (DEF-11) is admitted (reviews/05).

- B1–B20: 12 unguarded-arm one-test remedies (fix-batch PR) + 3 doc/spec-drift (2 fixed in Round 8)
  + 5 maintainer decisions. A well-sampled core with a named, cheap-to-close fringe.

**Deferred features (recorded, not built — v1.1 seed §7):**

- DEF-01 Area roll-up (multi-module aggregation) · DEF-02 Project-kind report sections ·
  DEF-03 Interview/sit-down-kind sections · DEF-04 Owner-audit workflow · DEF-05 Quarter-editorial
  (ARTICLE) template · DEF-06 Report→newsletter persona re-cut · DEF-07 Self-assessment leadership
  re-cut · DEF-08 Learning re-cut of the module report · DEF-09 MOR/IQ defect-project ↔ `Problem`
  tie-in · DEF-10 `Kpi` start/baseline model change · DEF-11 DistillPort AI backend (robot
  journalist, eval-first) · DEF-12 Problem Board Portfolio Surface (v1.0 Phase 14 carry-over).

**What's next:** Maintainer's call — the integration→main merge, then a fix-batch PR (B1–B20), then
the next milestone (candidate: DEF-04 owner-audit or DEF-05 quarter-editorial, with DEF-11's
admission requirements from reviews/05). Set via `/gsd-new-milestone`.

---
