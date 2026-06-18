---
phase: 11-work-surface-installation
plan: 02
subsystem: ingest
tags: [pathlib, stdlib, source, content-address, read-only, determinism, ai-optional]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: "Source / Trace.from_source — the content-address spine capture_files builds on"
  - phase: 04-07-adapters
    provides: "adapters/_timestamps.EPOCH_ZERO — the deterministic no-intrinsic-date sentinel reused for byte-stable Sources"
  - phase: 08-10-site-render
    provides: "render._is_file_path_locator / link_for_source — why a POSIX-relpath id resolves to a repo link for free"
provides:
  - "capture_files(paths, *, root) -> list[Source]: read-only, no-network, stdlib local-file ingest (WORK-01)"
  - "content-addressable work-corpus Sources whose transcript IS the verbatim file text"
  - "the AI-isolation gate extended to police newsletters.worksurface on the bare install (PKG-03 carried)"
  - "the Wave-0 end-to-end operator-flow test scaffold (skipped) for 11-03/04/05 to fill"
affects: [11-03-work-report, 11-04-publish-render, 11-05-check-corpus, work-surface, provenance]

# Tech tracking
tech-stack:
  added: []  # ZERO new runtime dependency — stdlib pathlib + existing core deps only
  patterns:
    - "Read-only-by-construction file ingest: Path.read_text only; never open('w'), never network"
    - "Deterministic ingest: sorted() input + EPOCH_ZERO timestamp => byte-stable Sources (SITE-06)"
    - "POSIX-relpath Source id => recognized by render._is_file_path_locator => repo link for free"
    - "V5 path-traversal bound: resolve().relative_to(root) raises if a path escapes root"
    - "Never hand-mint content_hash — Trace.from_source is the SOLE pinning path"

key-files:
  created:
    - src/newsletters/worksurface.py
    - tests/test_worksurface.py
  modified:
    - tests/test_ai_optional.py

key-decisions:
  - "New top-level module worksurface.py (not dogfood.py, not an adapters/ adapter) — keeps the sample-vs-real corpus boundary honest; a plain hand-authored reader is not a DistillPort modality extractor"
  - "Edge-case policy: missing/unreadable file -> raise (never skip-silently); non-UTF-8 -> raise UnicodeDecodeError (text corpus only, no lossy decode); abs vs rel path -> normalized to a repo-relative POSIX id via resolve().relative_to(root)"
  - "capture_files signature widened to Iterable[str | Path] (accepts str or Path, any order) for a friendlier call surface; output always sorted by id"

patterns-established:
  - "Read-only file ingest proven by snapshotting mtime_ns + sha256 of every scanned file and asserting unchanged"
  - "AI-isolation gate extended per new core module via a fresh-subprocess import + call under PYDANTIC_DISABLE_PLUGINS=true"

requirements-completed: [WORK-01]

# Metrics
duration: 4min
completed: 2026-06-18
---

# Phase 11 Plan 02: Read-only local-file Source ingest Summary

**`capture_files(paths, *, root) -> list[Source]` — a read-only, no-network, stdlib `pathlib` ingest that turns selected repo files into content-addressable POSIX-relpath `Source` records (deterministic via `sorted()` + `EPOCH_ZERO`), plus the AI-isolation gate extended to police it on the bare install.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-06-18T13:41:22Z
- **Completed:** 2026-06-18T13:45:03Z
- **Tasks:** 3
- **Files modified:** 3 (2 created, 1 extended)

## Accomplishments
- WORK-01's one genuinely new capability: a ~30-line read-only local-file `Source` ingest, stdlib-only, zero new dependency.
- Read-only BY CONSTRUCTION (only `Path.read_text`) — proven by a test that snapshots mtime + sha256 of every scanned file and asserts nothing changed.
- Content-addressable: each `Source.transcript` is the verbatim file text and a `Trace.from_source` over it round-trips; ids are POSIX relpaths recognized by `render._is_file_path_locator` (claims link to the working repo for free).
- Deterministic (sorted + `EPOCH_ZERO`) so the work corpus is byte-stable (SITE-06 carried).
- The AI-isolation gate (`tests/test_ai_optional.py`) extended so `import newsletters.worksurface` + a `capture_files` call are proven AI-free on the bare no-extras path (PKG-03 carried) — all prior assertions kept.
- The skipped end-to-end operator-flow scaffold is in place for Plans 11-03/04/05.

## Task Commits

Each task was committed atomically and pushed:

1. **Task 1: Read-only content-addressed ingest test (RED) + e2e scaffold** — `ddac1ab` (test)
2. **Task 2: Implement capture_files — read-only stdlib ingest (GREEN)** — `12e1237` (feat)
3. **Task 3: Extend the AI-isolation gate to police worksurface** — `bf7861f` (test)

_TDD: Task 1 = RED (test fails, module missing), Task 2 = GREEN (minimal implementation passes). No REFACTOR commit needed — the implementation was minimal and clean._

## Files Created/Modified
- `src/newsletters/worksurface.py` — `capture_files(paths, *, root) -> list[Source]`; read-only stdlib ingest, content-addressable, deterministic, AI-free.
- `tests/test_worksurface.py` — read-only + content-addressed + determinism + path-traversal-bound tests, and the skipped `test_operator_flow_end_to_end` Wave-0 scaffold.
- `tests/test_ai_optional.py` — added `test_worksurface_import_loads_no_ai_module` (policed surface extended to the new module); all existing assertions intact.

## The ingest API (for Plan 11-03 to build on)

```python
def capture_files(paths: Iterable[str | Path], *, root: Path | None = None) -> list[Source]: ...
```

**Source shape per file:**
- `id` = the POSIX relpath under `root`, e.g. `"src/newsletters/semantic.py"` (recognized by `render._is_file_path_locator` → resolves to a working repo link).
- `context` = `f"work-codebase:{relpath}"`.
- `transcript` = the verbatim UTF-8 file text (so claims content-address to REAL content via `Trace.from_source` — the SOLE pinning path; `capture_files` never mints a `content_hash`).
- `timestamp` = `EPOCH_ZERO` (deterministic, byte-stable).
- Result list is `sorted()` by `id`.

**Edge-case policy (documented in the module docstring):**
- missing / unreadable file → **raise** (`FileNotFoundError`) — a curated list cites real files; never skip-silently.
- non-UTF-8 file → **raise** `UnicodeDecodeError` — text corpus only, no lossy decode.
- absolute vs relative path input → **normalized** to a repo-relative POSIX `id` via `resolve().relative_to(root)`.
- path escaping `root` → **raise** `ValueError` (V5 path-traversal bound — `relative_to` raises).

**For 11-03:** `build_work_report` consumes this list — author `Decision`s whose `source_id` is a real file `id`, then content-address each claim's trace by locating its verbatim span in the matching `Source.transcript` and pinning via `Trace.from_source` (mirror `dogfood._address_report`). Un-locatable claims route to `Surface.missing[]` — never fabricate an offset.

## Decisions Made
- **New top-level `worksurface.py`** (not `dogfood.py`, not an `adapters/` adapter) — keeps the "sample (dogfood) vs real (worksurface)" corpus boundary honest; a hand-authored file reader is not a `DistillPort` modality extractor (matches 11-RESEARCH L1/L2 + the alternatives table).
- **Signature widened to `Iterable[str | Path]`** (plan specified `list[str]`) for a friendlier, order-independent call surface; the output is always `sorted()` by `id` so determinism is unaffected. This is a non-behavioral superset of the planned contract.
- **`resolve()` before `relative_to(root)`** so abs/rel inputs normalize to the same canonical id and symlink/`..` escapes are caught by the traversal bound.

## Deviations from Plan

None — plan executed exactly as written. (The `Iterable[str | Path]` signature is a backward-compatible widening of the planned `list[str]`, documented above as a decision, not a deviation: every `list[str]` call still type-checks and behaves identically.)

## Issues Encountered
None. RED failed for the right reason (`ModuleNotFoundError: newsletters.worksurface`); GREEN passed on first implementation; all gates green on first run.

## Threat surface scan
No new security surface beyond the plan's `<threat_model>`. The three mitigations are implemented and tested:
- **T-11-04 (write-back):** read-only by construction (`read_text` only); the read-only test asserts no scanned file's mtime/hash changes.
- **T-11-05 (path traversal):** `resolve().relative_to(root)` raises on escape; `test_capture_files_rejects_path_escaping_root` proves it.
- **T-11-06 (hand-minted hash):** `capture_files` constructs `Source` only; content-addressing goes through `Trace.from_source` exclusively.

## Known Stubs
None. `capture_files` is fully wired (no empty/placeholder data). The skipped `test_operator_flow_end_to_end` is an intentional, documented Wave-0 scaffold whose later stages are owned by Plans 11-03/04/05 (named in its skip reason) — not a stub blocking this plan's goal.

## Verification (re-run independently — actual output)
- `pytest tests/test_worksurface.py -q` → **3 passed, 1 skipped** (the e2e scaffold).
- `pytest tests/test_ai_optional.py -q` → **15 passed, 1 xfailed** (xfail = pre-existing ambient logfire pydantic-plugin caveat; all prior assertions intact).
- `pytest -q` (full) → **529 passed, 1 skipped, 1 xfailed** (baseline 524 passed + my 4 new passing tests + concurrent 11-01 additions; green).
- `lint-imports` → **1 kept / 0 broken** (worksurface.py AI-free).
- `mypy src/newsletters/worksurface.py` → **Success: no issues found**.
- `mypy src/newsletters` → **exactly 12 pre-existing errors** (dogfood.py et al.); **0 new** (none in worksurface.py).
- `python -c "import newsletters.worksurface"` → imports clean, bare path, no AI.

## Next Phase Readiness
- WORK-01 ingest is ready: Plan 11-03 (`build_work_report`) extends `worksurface.py` using `capture_files` per the API + edge-case policy above.
- No blockers. Concurrent Plan 11-01 (font fix: render.py / fonts / test_render.py) was untouched — exclusive-file discipline held (`git add` by explicit path only).

## Self-Check: PASSED
- FOUND: src/newsletters/worksurface.py
- FOUND: tests/test_worksurface.py
- FOUND: .planning/phases/11-work-surface-installation/11-02-SUMMARY.md
- FOUND commit: ddac1ab (Task 1 RED)
- FOUND commit: 12e1237 (Task 2 GREEN)
- FOUND commit: bf7861f (Task 3 AI-gate)

---
*Phase: 11-work-surface-installation*
*Completed: 2026-06-18*
