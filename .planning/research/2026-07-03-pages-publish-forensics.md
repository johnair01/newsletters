# Research — GitHub Pages publish forensics (why v1.2 exists)

> Session investigation, 2026-07-03. Every claim below was verified against the live GitHub
> API / live site during the session; run numbers and URLs are the evidence trail.

## The question

The record renders beautifully and passes every gate — so why does the *published* site keep
feeling incomplete (stale links, missing reports, "we fixed this already")?

## Findings (verified live)

### F1 — What's live is a manual snapshot, not a pipeline output

- `https://johnair01.github.io/newsletters/` serves bytes **identical** to
  `content/rev1/site/index.html` (verified by byte-compare) — the Python renderer's output.
- It is served from the **`gh-pages` branch**, which holds three hand-pushed commits:
  `7bce8ca` "Publish rendered site (Rev2, Phases 1-13) for UAT" (2026-06-19),
  `74d5318` / `6201434` persona re-renders (2026-06-27). Root = rev1 snapshot + `work/`;
  **no `module/`** — hence `/module/report-module-a.html` (and PR #20's
  `/reports/module/…` expectation) 404s live today.
- Nothing regenerates this branch. Every content change since 6/27 is invisible to readers.

### F2 — The automated deploy publishes the wrong site and has never succeeded

- `.github/workflows/deploy-pages.yml` builds the **Next.js `web/` "Signals" app** —
  hand-authored placeholder data (`web/lib/data.ts`), decoupled from the real corpus —
  and deploys via `actions/deploy-pages` into the `github-pages` **environment**.
- All 4 runs of that workflow **failed at the `deploy` job** (build green, deploy rejected):
  run #1 `28304887250` + #2 `28304952371` (branch `claude/new-session-kz7u69`, 6/27),
  **run #3 `28305361949` (branch `main`, 6/27)**, run #4 `28585997081`
  (branch `claude/swimlane-report-composer-1i8vxt`, 7/02, PR #8's reports bundling).
- RETRO 2026-07-02 ("two gates") diagnosed the environment-protection allowlist for run #4.
  **Run #3 failing on `main` is the sharper fact:** the channel is broken even from the
  allowed-by-assumption branch. PR #20's "merging to main publishes the reports" premise
  is therefore unverified-and-likely-false.
- Latent hazard: had the workflow ever succeeded, the placeholder app would have **replaced
  the real reviewed record at the site root** — a faithfulness violation, not just a bug.

### F3 — Two divergent site systems

| | Python renderer (`content/*/site/`) | Next.js `web/` (deployed target) |
|---|---|---|
| Content | the reviewed, evidence-traced record | hand-authored sample data |
| Guarantees | byte-stable, merge-block gated, 626 tests | none of the trust chain |
| Fidelity | design-system exact, self-hosted fonts | design-system port, own font copies |
| Links | relative, no-dead-link tested per corpus | app-router absolute under basePath |
| Deployed? | only via the manual gh-pages snapshot | never (4/4 failures) |

### F4 — Guard gaps that let this happen silently

- CI's merge-block job gates **rev1 only**; `work`/`module` corpora are un-gated in CI.
- Only `module` has a committed==fresh byte test; rev1/work drift would pass CI.
- No test anywhere covers the **assembled published tree** (cross-corpus links, fonts,
  404) — each corpus is only ever checked in isolation, which is exactly where the live
  404 class lives.

## Decisions taken (Editor-in-Chief, via structured question, 2026-07-03)

1. **Site root = the rendered record** (rev1 at root, `/work/`, `/module/`, cross-linked);
   `web/` stops deploying — retained for a future phase that wires it to real data.
2. **Deploy = force-push an assembled tree to `gh-pages`** — the channel proven live; one
   visible gate (`contents: write`) instead of the invisible environment allowlist.
3. **Base = the v1.1 branch** (fast-forward, verified zero-conflict); PR sequencing with
   #20 is the maintainer's call, stated in the PR.
4. **Design authority** for any new UI (Records strip, 404): `docs/design-system.md` +
   the Claude design handoffs in `design-reference/` (esp. `signals-navigation/` —
   "no surface a dead-end").

## What this rules out

- Fixing pages by hand (or re-pushing gh-pages manually) — treats the symptom, recreates F1.
- "Just fix the environment allowlist" — repo-settings-only, invisible to CI, and still
  publishes the wrong artifact (F2/F3).
- Deploying the `web/` app "because the workflow already exists" — violates *faithful, not
  suggestive*; placeholder data must not wear the product's URL.
