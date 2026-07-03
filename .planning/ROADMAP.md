# Roadmap: Newsletters — Milestone v1.2 (The Published Record)

> **Fresh file for v1.2.** v1.1 (Swim-Lane Module Report) SHIPPED 2026-07-02 and is archived:
> roadmap at `.planning/milestones/v1.1-ROADMAP.md`, requirements at
> `.planning/milestones/v1.1-REQUIREMENTS.md`, audit at `.planning/milestones/v1.1-MILESTONE-AUDIT.md`.
> Phase numbering resets to 1–2 for this milestone (the v1.1 phase dirs are archived; no collision).

**Milestone:** v1.2 The Published Record: one channel, production-ready
**Defined:** 2026-07-03
**Granularity:** fine
**Phases:** 2 (locked by approved milestone scope)
**Coverage:** 5/5 v1.2 requirements mapped ✓ (PUB-01..05 — see `.planning/REQUIREMENTS.md`)
**Research:** `.planning/research/2026-07-03-pages-publish-forensics.md` (live-verified evidence)

## Overview

The product renders a reviewed, evidence-traced record — but the **publish system doesn't ship
it**: the live site is a stale hand-pushed `gh-pages` snapshot, the automated deploy builds the
wrong artifact (the placeholder `web/` app) and has failed 4/4 runs (including from `main`), and
no test anywhere covers the assembled published tree. This milestone makes the published site a
*product output*: the rendered record IS the site, one workflow republishes exactly what a human
merged, and the linkability/drift/gating invariants become PR-blocking tests instead of
discipline. Design authority for new UI: `docs/design-system.md` + the Claude design handoffs in
`design-reference/` (esp. `signals-navigation/`: *no surface a dead-end*).

## Enforced gate set (definition of "green" for every phase — carried from v1.1)

Re-run independently (agent "green" ≠ green):

1. **pytest** — full suite (626 at open) incl. each phase's new guard tests
2. **lint-imports** — contracts held (AI-optional core; no-external-write)
3. **`newsletters check`** — over ALL corpora (rev1, work, module)
4. **byte-stable double-render** — committed == fresh for every corpus (incl. regenerated output)
5. **bare-install CI** — untouched; stays the AI-free source of truth

`mypy`/`black`/`isort`: no-NEW-failures vs the 2026-07-02 baseline (carried).

## Phases

- [ ] **Phase 1: Site IA & linkability** (PUB-03)
- [ ] **Phase 2: One publish channel** (PUB-01, PUB-02, PUB-04, PUB-05)

## Phase Details

### Phase 1: Site IA & linkability

**Goal**: No corpus is a dead end. Each corpus's chrome pages (Home/Library) carry a cross-corpus
"Records" strip designed per the design system + the `signals-navigation` handoff, a
design-system `404.html` renderer exists for the assembled site, and every corpus regenerates
byte-stably with the new chrome.
**Depends on**: Nothing (first phase).
**Requirements**: PUB-03
**Success Criteria** (what must be TRUE):

  1. `render_home`/`render_library` accept an optional `records` sequence and render a Records
     strip using existing `_CSS` tokens only (DM Mono eyebrow, hairline rules, radius 0); records
     omitted/empty → no strip markup (proven by test). *(Amended from "byte-identical to before"
     — the strip's CSS lands in the shared inline `_CSS`, so all pages change bytes once this
     phase regardless; see 01-CONTEXT decision 5.)*
  2. The strip appears on chrome pages ONLY (rev1 `index.html` + `library.html`; work + module
     `library.html`); no per-surface page carries it (proven by test).
  3. `render_404(base_path=…)` emits a page through `_page` (generated marker + full token CSS)
     whose hrefs AND font urls are base-path-absolute, because GitHub Pages serves 404.html at
     arbitrary depth (proven by test).
  4. All three corpora are regenerated in the same commit; `test_committed_equals_fresh_build`
     (module) and the double-render invariants stay green; every `ids.json` ledger is unchanged.
  5. `tests/test_render.py::test_no_dead_link_every_internal_href_resolves` treats cross-corpus
     hrefs (containing `/`) as out-of-corpus references whose resolver of record is Phase 2's
     assembled-tree test — never silently skipped, listed explicitly.

**Plans**: 1 plan

  - [ ] 01-01-PLAN.md — Records strip + 404 renderer + builder wiring + corpus regeneration + guard tests + `docs/surfaces.md` deltas

### Phase 2: One publish channel

**Goal**: One automated channel republishes exactly what a human merged: a typed assembly
function composes the committed corpora into the published tree, four invariants
(links/drift/fonts/marker) are PR-blocking tests, CI gates all three corpora, and the deploy
workflow gate-checks then force-pushes `gh-pages` from `main` only.
**Depends on**: Phase 1 (corpora final before assembly tests pin bytes; the assembled-tree link
test resolves Phase 1's cross-corpus hrefs).
**Requirements**: PUB-01, PUB-02, PUB-04, PUB-05
**Success Criteria** (what must be TRUE):

  1. `publish.assemble_site(out_dir, base_path=…)` (stdlib-only, AI-free, deterministic) composes
     rev1→root, work→`work/`, module→`module/`, writes `.nojekyll` + `404.html`, copies committed
     bytes verbatim (never a fresh render), and fails loudly on a missing corpus — proven by
     tests incl. byte-stable double-assemble. `newsletters assemble` exposes it; `dist/` ignored.
  2. `tests/test_publish.py` proves, on every PR: (a) every `href`/`src` in the assembled tree
     resolves relative to its page (404.html's base-path-absolute links asserted against tree
     root); (b) committed == fresh for rev1 AND work (module already guarded) + ledgers
     append-only; (c) every font url referenced resolves to a shipped woff2 + the OFL licenses
     travel; (d) every assembled page carries the generated-by marker.
  3. CI runs a `site-integrity` job (the publish/render/site tests) on every push/PR, and the
     merge-block job gates all three corpora; the bare-install job is untouched.
  4. `deploy-pages.yml` triggers only on push to `main` (+ `workflow_dispatch` guarded to main),
     needs only `contents: write`, re-runs `newsletters check` ×3 and `tests/test_publish.py`,
     assembles via the CLI, and force-pushes a single commit to `gh-pages` naming the source SHA.
     No `web/` build, no stale branch triggers, no third-party publish action, warn-only Pages
     source preflight.

**Plans**: 1 plan

  - [ ] 02-01-PLAN.md — `publish.py` + `assemble` CLI + `test_publish.py` guarantees + CI wiring + `deploy-pages.yml` rewrite

## Progress

**Execution Order:** 1 → 2 (strictly ordered).

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Site IA & linkability | 0/1 | Not started | — |
| 2. One publish channel | 0/1 | Not started | — |

## Deferred — un-scheduled (carried from v1.1 close, unchanged)

- **DEF-01..DEF-12** — see `.planning/milestones/v1.1-ROADMAP.md` §Deferred (area roll-up,
  project/interview kinds, owner-audit, quarter-editorial, persona/leadership/learning re-cuts,
  MOR/IQ↔Problem, Kpi baseline, DistillPort AI backend, Problem Board).
- **DEF-13 (new, this milestone's scope decision)** — wire `web/` (the Signals Next.js app) to
  the real corpus data; until then it is not deployed.
- **DEF-14 (new)** — adopt the `actions/deploy-pages` environment channel iff the maintainer
  aligns the repo settings (Pages source + environment allowlist); until then gh-pages push is
  the one channel.

---
*Roadmap created: 2026-07-03 for milestone v1.2. v1.1 archived at `.planning/milestones/`.*
