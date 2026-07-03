# Requirements — Milestone v1.2 (The Published Record: one channel, production-ready)

> Fresh file for v1.2 (v1.1 requirements archived at `.planning/milestones/v1.1-REQUIREMENTS.md`).
> Grounding: `.planning/research/2026-07-03-pages-publish-forensics.md` (the live-verified evidence
> for why the publish system, not the pages, is the thing to fix).

**Defined:** 2026-07-03 · **Count:** 5 (PUB-01..05) · **Scope discipline:** the v1.1 rule carries —
requirements are locked at milestone open; anything new is a seed for the next milestone.

## The one-sentence contract

The site a reader sees at `https://johnair01.github.io/newsletters/` is exactly the reviewed
record a human merged to `main` — republished by one automated channel, with no dead link,
no drift, and no manual step.

## Requirements

### PUB-01 — One publish channel
The deploy workflow is the ONLY way the site publishes: it triggers on push to `main` (plus
maintainer `workflow_dispatch` from `main`), re-runs the merge-block gate and the byte-drift
checks over the **committed** corpora, assembles, and force-pushes a single commit to
`gh-pages` naming its source SHA. Manual `gh-pages` pushes are retired. The workflow never
renders fresh content into production — what was reviewed is what publishes.

### PUB-02 — The published site is the rendered record
Site root = `content/rev1/site` (Home/Library/surfaces); `content/work/site` at `/work/`;
`content/module/site` at `/module/`; `.nojekyll` + a design-system-compliant `404.html`.
The `web/` Next.js app is **not deployed** (retained in-repo for a future phase that wires
it to real data). Assembly is a typed, tested library function (`newsletters assemble`),
never ad-hoc workflow shell.

### PUB-03 — No dead ends
Every corpus chrome page carries a cross-corpus "Records" strip (designed per
`docs/design-system.md` + the `design-reference/signals-navigation/` handoff: no surface a
dead-end). Every `href`/`src` in the **assembled** tree resolves to a real file — guarded by
a test that runs on every PR, not by discipline. (This test, run against today's live tree,
would have caught the `/module/` 404.)

### PUB-04 — No drift, any corpus
Committed corpus == fresh render, byte-for-byte, for **all three** corpora (v1.1 guarded
module only), plus ledger-append-only checks — enforced in CI on every PR and again
pre-publish in the deploy workflow.

### PUB-05 — Every corpus gated in CI
`newsletters check` (the merge-block gate) runs for rev1 AND work AND module in CI (today:
rev1 only) and again as the deploy workflow's first gate. Fonts-present and
generated-marker invariants join the same PR-blocking test module.

## Requirement → phase map

| Req | Phase |
|-----|-------|
| PUB-03 (strip + 404 design + per-corpus link exemptions) | Phase 1 — Site IA & linkability |
| PUB-01, PUB-02, PUB-04, PUB-05 (assembly, tests, CI, workflow) | Phase 2 — One publish channel |

## Out of scope (seeds, not slippage)

- Wiring `web/` to real corpus data (its own future phase; DEF-class).
- Retiring/adopting the `github-pages` environment channel (`actions/deploy-pages`) — a
  maintainer-settings decision documented in the PR; the workflow carries a warn-only preflight.
- The B1–B20 v1.1 fix-batch (separate PR, maintainer-gated).
