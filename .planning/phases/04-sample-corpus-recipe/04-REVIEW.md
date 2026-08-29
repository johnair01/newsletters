---
phase: 04-sample-corpus-recipe
reviewed: 2026-08-29T00:00:00Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - src/newsletters/weeklysite.py
  - src/newsletters/cli.py
  - src/newsletters/publish.py
  - tests/test_weeklysite.py
  - tests/test_weekly_golden.py
  - tests/_corpus_scan.py
  - docs/weekly.md
  - .github/workflows/ci.yml
  - .github/workflows/deploy-pages.yml
findings:
  critical: 0
  warning: 5
  info: 5
  total: 10
status: fixed
fixed: 2026-08-29
fixed_outcomes:
  WR-01: fixed (623851d)
  WR-02: fixed (f492110)
  WR-03: fixed (d666dc6)
  WR-04: fixed (3f11647)
  WR-05: fixed (5d8766e)
  IN-01: carried
  IN-02: carried
  IN-03: fixed (d7bd0fb)
  IN-04: carried
  IN-05: fixed (d0cfa14)
---

# Phase 4: Code Review Report

**Reviewed:** 2026-08-29
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

Adversarial review of the Phase-4 weekly corpus: `weeklysite.py` builder, `newsletters weekly`
CLI, corpus wiring in `publish.py`/CI/deploy, the two test modules, the promoted scanner and
`docs/weekly.md`. All hard rules the phase claims were **independently re-verified against the
live repo**, not taken from the summary:

- **Sample ships Draft / no gate-advancing call:** confirmed. `grep` over `weeklysite.py`,
  `cli.py`, `publish.py`, `weeklyspec.py`, `swimlane.py`, `compose.py` finds no `.publish(`,
  `.approve(`, `open_pull_request(` call (docstring mentions only). Composer output asserted
  Draft by `test_every_claim_traced_and_addressed` and re-read from the written deck in
  `test_rendered_deck_reads_back_draft_watermarked_and_marked`.
- **Deck structurally unpublishable:** confirmed. `publish._CORPUS_LAYOUT` copies
  `content/*/site` only (publish.py:39-44); `content/weekly/deck/` sits outside every copied
  source dir; `test_deck_is_not_in_the_published_tree` additionally asserts no `.pptx` under
  `site/`.
- **No external calls:** confirmed — no `requests`/`urllib`/`socket` import anywhere on the
  weekly path; fonts self-hosted and asserted by `test_no_external_calls`.
- **Root containment:** confirmed in `weeklyspec._place_assets` (resolve-before-read,
  `relative_to(root)` raises — weeklyspec.py:541-551) and in `_load_inbox_sources`
  (weeklysite.py:145 computes `relative_to(root_path)` *before* `read_bytes`). Slug-based HTML
  write paths are traversal-safe (`site.slugify` restricted to `[a-z0-9-]`, site.py:48-60).
- **Determinism / EPOCH_ZERO / append-only ledger:** confirmed by running the suite
  (`.venv/bin/pytest tests/test_weeklysite.py tests/test_weekly_golden.py` → 25 passed) and by
  reading `Ledger.save` (byte-stable `sort_keys` + trailing newline, site.py:161-167).
- **Synthetic-only committed content:** the committed yml/eml/ledger/HTML are scanned and the
  planted arms are non-vacuous — but the committed **binaries are a scanner blind spot**
  (WR-04 below). I extracted and scanned the XML parts of both committed `.pptx` files myself:
  currently clean, but unguarded.
- **Read-only claims in docs/weekly.md match the code** for every shipped invocation — with
  one exception the docstrings themselves mis-state: the `root=` parameter of
  `build_weekly_site` is only half-honored (WR-01, reproduced live).

No Critical findings. Five Warnings, five Info items.

## Warnings

### WR-01: `build_weekly_site(root=X)` reads the corpus from `root` but writes the ledger to — and reads the fonts from — the *cwd*

**File:** `src/newsletters/weeklysite.py:79-83, 266-268, 297` (plus `src/newsletters/worksurface.py:353, 368-369`)
**Issue:** `_LEDGER_PATH = "content/weekly/ids.json"` is a cwd-relative string. `build_weekly_surfaces` resolves the spec, lanes and inbox against `root` (weeklysite.py:109, 140), but `Ledger.load(_LEDGER_PATH)` / `ledger.save()` resolve against the process cwd, and `worksurface._emit_fonts` reads the cwd-relative `content/rev1/site/fonts` and **skips silently** when absent. Reproduced live: calling `build_weekly_site(out, root=Path("/home/user/newsletters"))` from another directory (a) created a stray `content/weekly/ids.json` tree under that directory — a write to a path the caller never named, violating the module's own "the only writes are the ledger, the rendered output" contract and the test-suite claim that "the ledger path is the FIXED COMMITTED one" (test_weeklysite.py:29-33), and (b) emitted **no fonts at all, silently**, so the output violates the self-hosted-fonts property (`test_no_external_calls` would fail on that output, but only runs from the repo root). No *shipped* caller passes a foreign `root` (CLI uses cwd; the golden tests pass `root=REPO_ROOT` only to `_load_and_compose`/`build_weekly_deck`), so the committed corpus is not at risk — but the parameter is public, documented ("the repo root the paths resolve against"), and wrong.
**Fix:** resolve both cwd-relative paths against `root`:
```python
root_path = (Path(root) if root is not None else Path.cwd()).resolve()
ledger = Ledger.load(root_path / _LEDGER_PATH)
...
worksurface._emit_fonts(out)  # and give _emit_fonts a fonts_dir=root_path/"content/rev1/site/fonts" seam
```
(Same defect exists in the mirrored `modulesite.py` / `build_work_site` — inherited, so fix the family or drop `root` from `build_weekly_site`'s signature and fail loud.)

### WR-02: a second `*.yml` in the corpus silently renders the *wrong* (oldest) week

**File:** `src/newsletters/weeklysite.py:99-115`
**Issue:** `_discover_one_yml` docstring asserts "Each corpus is self-contained with exactly one root-level config", but the code never enforces it: `sorted(...)[0]` silently picks the alphabetically-first file. The natural operator workflow — drop `weekly-2374-w42.yml` beside the committed `weekly-2374-w41.yml` and run `newsletters build --corpus weekly` — deterministically renders **last week's** spec (w41 sorts first) with exit 0 and no hint that a file was ignored. `docs/weekly.md` §6 explicitly tells operators to "put your spec in that corpus directory", making this trap the documented path.
**Fix:** fail loud on ambiguity, matching the module's own fail-loud norm:
```python
if len(candidates) > 1:
    raise FileExistsError(
        f"multiple {what} '*.yml' under {corpus}: {[c.name for c in candidates]} — "
        "one corpus, one spec; pass --spec to choose"
    )
```

### WR-03: the no-byline error tells the operator to pass `--author` — on a command that has no `--author`

**File:** `src/newsletters/weeklysite.py:92-96` (raise site: 151-158); `src/newsletters/cli.py:64-79`
**Issue:** `_NO_AUTHOR` says "pass author=... (the CLI's --author) or give the spec a 'config: author:' value". The command most likely to raise it for an operator authoring their own spec is `newsletters build --corpus weekly` (the HTML path `docs/weekly.md` §6 prescribes for "your own week"), and that command exposes only `--out` — verified live: `build --corpus weekly --author X` → exit 2, "No such option: --author". `build_weekly_site` even accepts an `author=` kwarg (weeklysite.py:234) that the CLI never plumbs through. The operator follows the error, hits a second error, and the only working path (`config: author:`) is buried behind a dead suggestion. The raw `ValueError` also surfaces as a Typer traceback rather than a clean message.
**Fix:** either add `--author` to `build` (pass it to `build_weekly_site` for the weekly branch), or scope the message: "pass --author (the `newsletters weekly` deck command) or give the spec a 'config: author:' value (the only option for `newsletters build`)". Catch the `ValueError` in the CLI and `raise typer.Exit` after echoing it.

### WR-04: the synthetic-content scanner never reads the committed binaries — `template.pptx`, `deck/*.pptx` and asset filenames are outside T-04-02's guard

**File:** `tests/test_weeklysite.py:92-99` (`_corpus_files`)
**Issue:** `test_committed_content_is_synthetic` claims "every committed content/weekly/ file carries only synthetic fabricated names" but `_corpus_files` collects only `*.yml`, `inbox/*.eml`, `ids.json` and `site/*.html`. The committed `template.pptx` and `deck/weekly-2374-w41.pptx` are public repo content whose XML parts carry human-readable text (slide text, core properties, author fields), and `assets/*` filenames are also visible content — none are scanned. A template footer naming a real person, or a real name typed into a slide the writer doesn't fill, would land in the public repo with the guard green. I extracted both zips' `.xml`/`.rels` parts and ran `scan_real_looking` over them: currently clean — so this is a guard hole, not a live leak. Related narrowness: the `@example.invalid` allowance (test_weeklysite.py:81-89) subtracts the whole hit, so a real name encoded in an address local part (`jean.luc.picard@example.invalid`) would be swallowed (the literal scan only matches the space-separated form).
**Fix:** extend `_corpus_files`/the test with a binary arm:
```python
for pptx in [CORPUS / "template.pptx", *sorted((CORPUS / "deck").glob("*.pptx"))]:
    with zipfile.ZipFile(io.BytesIO(pptx.read_bytes())) as z:
        for part in z.namelist():
            if part.endswith((".xml", ".rels")):
                leaks = _scan_weekly(z.read(part).decode("utf-8", errors="ignore"))
                assert not leaks, f"{pptx.name}!{part}: {sorted(leaks)}"
```
and scan `p.name` for files under `assets/`.

### WR-05: `assemble_site` `rmtree`s any directory containing a `.nojekyll` — a marker every GitHub Pages checkout has

**File:** `src/newsletters/publish.py:69-76`
**Issue:** the clobber guard treats "contains `.nojekyll`" as "is a previous assembly of ours" and then `shutil.rmtree`s the whole directory. `.nojekyll` is the standard marker in essentially *every* static Pages tree, so `newsletters assemble --out <path to any gh-pages checkout or other static site>` silently destroys it — a data-loss path reachable from one mistyped `--out`, guarded by the weakest possible sentinel. The docstring's promise ("a non-empty out_dir that is not a previous assembly is refused, never clobbered") is only as true as the marker is distinctive, and it is not distinctive at all.
**Fix:** write and check a marker only this tool produces:
```python
_MARKER = ".newsletters-assembly"   # written beside .nojekyll at assemble time
if out.exists() and any(out.iterdir()) and not (out / _MARKER).exists():
    raise FileExistsError(...)
```
(keep emitting `.nojekyll` for Pages; just stop using it as the ownership proof). Also guard `out.is_dir()` before `out.iterdir()` — a file at `out` currently dies with a bare `NotADirectoryError`.

## Info

### IN-01: deploy workflow prose contradicts itself — "never renders fresh content into production" vs. the fresh `npm run build`

**File:** `.github/workflows/deploy-pages.yml:27-29, 108-113`
**Issue:** the header states "it never renders fresh content into production … the sole rendered file is the deterministic, tested 404 chrome", but the workflow then builds the Next.js preview from source (`npm ci && npm run build`) into `_site/web` on every publish — fresh, untested-at-publish-time output on the production origin. The preview is an acknowledged DEF-13 amendment, but the "sole rendered file" sentence is now false in the same file. Specs and code must not drift silently (CLAUDE.md convention).
**Fix:** amend the comment: "the sole rendered *record* file is the 404 chrome; the /web/ design preview is additionally built fresh, carries placeholder data, and is not part of the record."

### IN-02: the no-gate source scan matches only dotted call syntax

**File:** `tests/test_weekly_golden.py:255-273`
**Issue:** `test_no_gate_transition_in_the_weekly_build_path` greps `weeklysite.py` for `.publish(`, `.approve(`, `.open_pull_request(`. A direct state write (`surface.review.state = ReviewState.PUBLISHED`), a `getattr(surface, "publish")(...)`, or a bare `publish(surface)` helper would all pass the scan; conversely a *docstring* containing `.publish(` would fail it (the current docstring survives only because it writes `publish()` without the dot). Fine as defense-in-depth — the real gate lives in `semantic.py` — but the test's claim ("it holds even for a code path no test happens to execute") overstates what a substring scan proves.
**Fix:** additionally scan for `ReviewState.PUBLISHED` and `review.state` assignments, or AST-walk the module for attribute calls named `publish`/`approve` instead of substring matching.

### IN-03: symlink-escaping `.eml` fails with a bare `ValueError`, and the containment is untested

**File:** `src/newsletters/weeklysite.py:144-146`
**Issue:** an `inbox/*.eml` that is a symlink out of the root is correctly refused *before* the read (`path.resolve().relative_to(root_path)` raises), but as an uncaught `ValueError: ... is not in the subpath of ...` — not the teaching refusal voice `weeklyspec` uses for the same threat (weeklyspec.py:203) — and no test pins this behavior, so a refactor that computes `rel` differently (e.g. `os.path.relpath`, which never raises) would silently reopen the read.
**Fix:** catch the `ValueError` and re-raise with the corpus's refusal wording; add a symlink-escape test beside the loader's existing root-containment tests.

### IN-04: `build_weekly_site` cannot override the lane config

**File:** `src/newsletters/weeklysite.py:230-236`
**Issue:** `build_weekly_deck` exposes `lanes_path` and `build_weekly_surfaces` accepts it, but `build_weekly_site` neither accepts nor forwards it — so the HTML render of a copied corpus is permanently bound to whatever single yml sits under `content/module` at the cwd/root. The asymmetry is undocumented (the docstring says it "exactly mirrors build_module_site" without noting the missing seam).
**Fix:** add `lanes_path: str | Path | None = None` to `build_weekly_site` and pass it through to `build_weekly_surfaces` (which needs the same passthrough — it already forwards to `_load_and_compose`).

### IN-05: discovery is `*.yml`-only; a `.yaml` spec reports "the corpus is not populated"

**File:** `src/newsletters/weeklysite.py:110-115`
**Issue:** `_discover_one_yml` globs `*.yml` only. An operator whose editor default-saves `.yaml` (both extensions are conventional) gets `FileNotFoundError: no Weekly Spec '*.yml' found … the corpus is not populated` while looking straight at their populated corpus. Neither `docs/weekly.md` nor `docs/weekly-spec.md` (per the recipe's references) states the `.yml`-only restriction.
**Fix:** either glob both (`sorted([*corpus.glob("*.yml"), *corpus.glob("*.yaml")])`, keeping WR-02's ambiguity check) or say `.yml`, not YAML, in the recipe's "one YAML file" row.

---

## Fix outcomes (2026-08-29)

All five Warnings fixed; two zero-risk Info items fixed; three Info items carried. One commit per
finding, plus one style-baseline commit. Every gate re-run after the last fix: **871 passed / 0
skipped** (862 baseline + 9 new regression tests), `lint-imports` 2 kept / 0 broken, all four
`newsletters check` corpora clean, all four corpora rebuilt IN PLACE with `git status` clean
(committed==fresh + ledgers byte-unchanged), `tests/test_pptx_determinism.py` green, and the
`docs/weekly.md` fenced commands re-executed (the deck command against the doc's exact inputs to
a scratch `--out`: its digest equals the committed sidecar byte-for-byte). Style baselines held
exactly: mypy 15 errors / 5 files, black 69/33, isort 57 (DEF-15 set), no NEW failure anywhere.

| Finding | Outcome | Commit | What landed |
|---|---|---|---|
| WR-01 | **fixed** | `623851d` | `build_weekly_site` resolves the ledger AND the vendored-fonts dir against `root`; a fontless root REFUSES loudly before any write; `_emit_fonts` gains a `fonts_dir` seam (cwd-anchored callers unchanged); foreign-cwd regression test pins no-stray-writes + fonts-present + committed-ledger-unchanged. |
| WR-02 | **fixed** | `f492110` | `_discover_one_yml` enforces its own "exactly one": ambiguity is a `FileExistsError` naming every candidate and the ways out; `docs/weekly.md` §6 now says **replace** and states the refusal; regression test plants the w41/w42 trap. |
| WR-03 | **fixed** | `d666dc6` | `newsletters build` exposes `--author`, plumbed to `build_weekly_site` (weekly-only; other corpora refuse it loudly); both weekly commands echo a builder `ValueError` as a teaching message + exit 1, no Typer traceback; tests prove the flag reaches the rendered byline. |
| WR-04 | **fixed** | `3f11647` | New test unzips `template.pptx` + `deck/*.pptx` and scans every `.xml`/`.rels` part with the SAME scanner/allowance, plus `assets/*` filenames; parts-count floor + planted-zip arm keep it non-vacuous. (The `@example.invalid` local-part narrowness the finding notes in passing is carried — the literal denylist never matched dotted-lowercase forms in any file.) |
| WR-05 | **fixed** | `5d8766e` | `assemble_site` ownership proof is now BOTH markers — `.nojekyll` AND `render.GENERATED_MARKER` (promoted to a named constant, byte-identical output) in `index.html` — or the new explicit `force=True` / `--force`; a FILE at `out` is a teaching refusal; near-miss + file-at-out regression tests; all four publish guarantees stayed green. |
| IN-01 | carried | — | Deploy-workflow prose amendment; doc-only, next docs pass. |
| IN-02 | carried | — | AST-walk upgrade of the no-gate scan; defense-in-depth only (the real gate is `semantic.py`). |
| IN-03 | **fixed** | `d7bd0fb` | Symlink-escaping `inbox/*.eml` now refuses in the corpus's teaching voice (mirrors `_ASSET_ESCAPES_ROOT`), pinned by a test so an `os.path.relpath` refactor can never silently reopen the read. |
| IN-04 | carried | — | `lanes_path` passthrough on `build_weekly_site`; new seam, not a defect in a shipped path. |
| IN-05 | **fixed** | `d0cfa14` | Discovery globs `*.yml` AND `*.yaml`; the not-found error names both; the WR-02 ambiguity guard spans both extensions; `docs/weekly.md` §6 updated. |

Style-baseline conformance commit: `38827bd` (black/isort on the two touched baseline-clean files;
no behavior change). WR-01's mirrored family defect (`modulesite.py` / `build_work_site` ledger
paths are also cwd-relative) is **carried**: no shipped caller passes a foreign `root` to those
builders, and the disposition scoped the fix to the weekly builder — the family fix is a recorded
follow-up, not a silent skip.

_Reviewed: 2026-08-29_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
_Fixed: 2026-08-29 — Claude (gsd-code-fixer)_
