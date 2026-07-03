# Phase 2 — One publish channel — CONTEXT

**Requirements:** PUB-01, PUB-02, PUB-04, PUB-05. **Defined:** 2026-07-03.
**Grounding:** milestone decisions (`.planning/STATE.md` §Decisions) + the forensics research
doc. The channel choice (force-push `gh-pages`), the artifact choice (rendered record, not
`web/`), and the committed-bytes-only rule were all locked at milestone open by the
Editor-in-Chief.

## Decisions specific to this phase

1. **Assembly is a library function, not workflow shell.** `publish.assemble_site()` — stdlib
   only, deterministic, fail-loud on a missing corpus — so the same code path is unit-tested,
   CLI-exposed (`newsletters assemble`), and CI/deploy-exercised. Bash `cp` in YAML is exactly
   the untested seam that let the two-site divergence go unnoticed.
2. **Clobber protection:** `assemble_site` refuses to overwrite a non-empty `out_dir` unless it
   recognizes it as a previous assembly (its own `.nojekyll` present). Deterministic re-runs;
   never eats an arbitrary directory.
3. **The four guarantees live in `tests/test_publish.py`** and run in BOTH places: the new CI
   `site-integrity` job (every push/PR) and the deploy workflow's pre-publish gate. Same tests,
   no bash re-implementation — one definition of "publishable".
4. **CI `merge-block` gains work+module** (today rev1-only). `[test,config]` install is
   justified in-YAML: PyYAML is non-AI and lazy; the `bare-install` job remains untouched as
   the AI-free source of truth (PKG-03).
5. **Deploy = plain-git single-commit force-push** to `gh-pages` from `main` only
   (`workflow_dispatch` ref-guarded). One visible gate (`contents: write`); deliberately avoids
   the `github-pages` environment protection that killed runs 1–4 (RETRO 2026-07-02). gh-pages
   history is a mirror; provenance = the publish commit names its source SHA. A warn-only
   preflight (`gh api repos/…/pages`) surfaces any future Pages-source flip.
6. **404.html is written at assemble time** (embeds the base path — a tree property), per
   Phase 1 CONTEXT d4.
