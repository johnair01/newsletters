# Phase 2 — VERIFICATION (2026-07-03)

**Verdict: PASSED 4/4** — gates re-run independently in a clean tree after the final commit.

| # | Success criterion (ROADMAP) | Evidence |
|---|---|---|
| 1 | `assemble_site` deterministic, committed-bytes-only, fail-loud, clobber-guarded; CLI exposed | `test_assemble_composes_three_corpora_and_chrome` / `_is_byte_stable` / `_copies_committed_bytes_verbatim` / `_fails_loud_on_missing_corpus` / `_refuses_foreign_out_dir` all green; `newsletters assemble --out …` run live (49 files) |
| 2 | Four PR-blocking guarantees | `tests/test_publish.py` 10 tests green: (a) assembled-tree links resolve — **caught a real live bug** (work/module nav/breadcrumb/fan-out pointed at a nonexistent corpus-local `index.html`; fixed via `home_href` threading, commit `2250fb9`); (b) committed==fresh rev1+work (+ module's existing test, ledgers unchanged); (c) fonts+OFL present; (d) marker on every page |
| 3 | CI: `site-integrity` job + 3-corpus merge-block; bare-install untouched | `ci.yml` diff: merge-block runs `check` ×3 on `.[test]`+`.[config]`; new `site-integrity` job runs publish/render/site/worksurface/modulesite tests on `[test,config]`; `bare-install` byte-untouched |
| 4 | Deploy workflow: main-only, `contents: write` only, gates → assemble → single-commit force-push, preflight | `deploy-pages.yml` rewritten (commit `a57f31e`): push→main paths-filtered + ref-guarded dispatch; Gate 1 = check ×3, Gate 2 = `pytest tests/test_publish.py`; `newsletters assemble --out _site`; plain-git force-push naming `${GITHUB_SHA}`; warn-only `gh api …/pages` preflight; YAML parses |

## Gate set (re-run 2026-07-03, this tree, post-final-commit)

```
python -m pytest -q                      639 passed          (629 → 639: +10 publish guards)
lint-imports                             Contracts: 2 kept, 0 broken.
newsletters check --corpus rev1|work|module   all clean, exit 0
git status                               clean (regen == committed)
newsletters assemble --out <scratch>     49 files; strips + /module/report-module-a.html + 404 verified
headless-chromium screenshots            404 edge-state panel + Records strip visually per design system
```

## The find worth remembering

The assembled-tree link test did on its FIRST run exactly what it exists to do: it failed on
`module/library.html → index.html` — a dead link **live on the production site today**
(`/work/`+`/module/` pages' "Start here"/Home/fan-out all 404). No per-corpus test could see
it; only the composed tree exposes it. The fix (corpus-aware `home_href`) also makes the IA
*more* coherent: from inside a sub-record, "Start here" now goes to the site's front door.

## Deliberate scope notes

- The gh-pages push itself is untestable pre-merge by design (main-only) — the PR body carries
  the post-merge UAT checklist; publishing stays human-gated.
- rev1's committed==fresh comparison is `*.html`-only: its `fonts/` are vendored assets (the
  canonical source `_emit_fonts` copies FROM), never renderer output — presence/resolvability
  is guaranteed by `test_fonts_referenced_are_present` instead. Recorded in-test.
