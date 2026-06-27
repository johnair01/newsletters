---
phase: 04-shared-adapter-normalizer-email
plan: 01
subsystem: adapters
tags: [normalize, faithful-extraction, content-addressing, Trace.from_source, coverage, unextracted, stdlib]

# Dependency graph
requires:
  - phase: 01-distill-socket
    provides: "Coverage / Unextracted honesty contract; DistillationResult wrapper"
  - phase: 03-content-addressed-provenance-faithfulness
    provides: "Trace.from_source content-addressing (sole hash-minting path); SpanContainmentFaithfulness gate"
provides:
  - "Shared normalize(source, units) — the ONE place the faithful-extraction rule lives"
  - "Cursor-advancing verbatim location: duplicate units get distinct, forward-only offsets"
  - "Non-locatable units routed to a returned unextracted[] with a FreeLocator content anchor (never fabricated)"
  - "newsletters.adapters package (stdlib/Pydantic-only, AI-free) for the Email adapter (04-02) to import"
affects: [04-02-email-adapter, 04-03-golden-file-tests, future-adapters-excel-pptx-powerbi]

# Tech tracking
tech-stack:
  added: []  # stdlib + Pydantic only — no new dependency (CONTEXT decision 5)
  patterns:
    - "One trust rule, one place: faithful-or-unextracted lives only in normalize()"
    - "Cursor-advancing str.find for per-claim provenance (distinct offsets for duplicate units)"
    - "Trace.from_source as the SOLE trace-minting path; adapters never hand-mint hashes"

key-files:
  created:
    - src/newsletters/adapters/__init__.py
    - src/newsletters/adapters/normalize.py
    - tests/test_normalize.py
  modified: []

key-decisions:
  - "Empty unit ('') is a locatable ZERO-WIDTH span (str.find('') == cursor) -> mints Claim(text='', span=''); does not advance cursor"
  - "Cursor is forward-only: overlapping/out-of-order units that begin before the cursor route to unextracted[], enforcing non-overlapping provenance"
  - "confidence=0.0 passed explicitly to Claim() to keep mypy (no pydantic plugin) clean — 0.0 is the existing default, no behavior change"

patterns-established:
  - "Pattern 1: faithful normalize() — verbatim-locate-or-unextracted, content-addressed via Trace.from_source"
  - "Pattern 2: FreeLocator content-preview anchor for unextracted units (never an ordinal index, locators.py:17-19)"

requirements-completed: [ADAPT-01]

# Metrics
duration: 12min
completed: 2026-06-17
---

# Phase 04 Plan 01: Shared Adapter Normalizer Summary

**The shared `normalize(source, units)` — the ONE place the faithful-extraction rule lives: cursor-advancing verbatim location mints content-addressed `Claim(+Trace)` via `Trace.from_source`, routing anything not verbatim-locatable to a returned `unextracted[]` (never fabricated).**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-06-17T14:18Z
- **Completed:** 2026-06-17T14:31Z
- **Tasks:** 2
- **Files modified:** 3 (all created)

## Accomplishments
- New `src/newsletters/adapters/` package, stdlib/Pydantic-only and AI-free (import-linter `forbid-ai-in-core` stays KEPT — `source_modules = newsletters` already covers the sub-package, no `.importlinter` edit).
- `normalize()` locates each unit by a cursor-advancing `transcript.find(unit, cursor)`, mints a content-addressed `Trace` through `Trace.from_source` (the sole hash-minting path — zero `hashlib`/`sha256` in the adapter), and emits one `Claim(text=unit, evidence=[trace])` per locatable unit.
- Non-locatable units (absent, over-length, or already consumed before the cursor) route to a returned `unextracted[]` as `Unextracted(locator=FreeLocator(text=unit[:60]), reason="unit not verbatim-locatable …")` — a CONTENT anchor, never an ordinal index, never a fabricated claim.
- 14 unit tests cover the full `<behavior>` block plus gate survival: every emitted claim passes `SpanContainmentFaithfulness().entails()`, and the `unextracted[]` shape composes with the `Coverage` honesty validator.

## The public API (contract for the 04-02 Email-adapter executor)

```python
from newsletters.adapters import normalize
# also importable as: from newsletters.adapters.normalize import normalize

def normalize(source: Source, units: list[str]) -> tuple[list[Claim], list[Unextracted]]: ...
```

- **Input `source`:** the `Source` whose `transcript` the units were sliced from. `transcript` is the single source of truth; traces are content-addressed against `source.content_hash()`.
- **Input `units`:** an ordered `list[str]` of raw unit strings the adapter extracted, **in transcript order** (e.g. each `"<Header>: <value>"` value, then each body paragraph). Order matters — the cursor advances monotonically. Units the adapter ALREADY knows are unreadable (PDF attachment, forwarded `message/rfc822`, charset fallback, lossy HTML strip — U1–U7) are the adapter's OWN `unextracted[]` entries and are **not** passed here; `normalize()` only handles the verbatim-locate decision (U8).
- **Returns `(claims, unextracted)`:**
  - `claims: list[Claim]` — one per locatable unit, in input order; each has exactly one evidence `Trace` with `is_addressed is True`, `span == claim.text == transcript[start:end]`.
  - `unextracted: list[Unextracted]` — one per non-locatable unit; `locator` is a `FreeLocator` carrying a ≤60-char content preview, `reason` is the fixed string `"unit not verbatim-locatable in transcript (faithful, not suggestive)"`.
- **Offsets:** CHARACTER-based (matching `Trace.from_source`), not byte-based.
- **How the adapter assembles the result:** wrap `claims` in a `Distillation`, and build `Coverage(complete=(len(all_unextracted) == 0), unextracted=adapter_unextracted + normalize_unextracted)`. The `Coverage` validator makes "complete with dropped content" unrepresentable, so a non-empty `unextracted[]` forces `complete=False`.

### Edge-case behavior (documented decisions)

| Case | Behavior |
|------|----------|
| Empty `units` list | `([], [])` |
| Empty unit `""` | `str.find("", cursor) == cursor` ⇒ locatable ZERO-WIDTH span; mints `Claim(text="", span="")`; cursor not advanced. Faithful — `""` is a substring of anything. |
| Unit absent or longer than remaining transcript | `find == -1` ⇒ routed to `unextracted[]` |
| Duplicate identical units | resolved to DISTINCT, increasing offsets via the cursor (e.g. `"ab\n\nab"` ⇒ starts 0 and 4) |
| Overlapping / out-of-order units | cursor is forward-only; a unit beginning BEFORE the cursor is not re-located backwards ⇒ `unextracted[]` (non-overlapping provenance) |

## Task Commits

1. **Task 1 (RED): failing tests for normalize()** - `9e3f281` (test)
2. **Task 1 (GREEN): shared faithful normalize()** - `81069fb` (feat)
3. **Task 2: mypy-clean construction fix** - `035bae3` (fix)

_TDD Task 1 produced the test→feat pair; Task 2's standing-gate run surfaced the one deviation below._

## Files Created/Modified
- `src/newsletters/adapters/__init__.py` - new package; exports `normalize`; documents the one-trust-rule architecture and AI-free property.
- `src/newsletters/adapters/normalize.py` - the shared faithful `normalize()`; cursor-advancing location + `Trace.from_source` minting + `unextracted[]` routing.
- `tests/test_normalize.py` - 14 tests: happy path, offset positions, duplicate disambiguation, non-locatable + already-consumed + over-length + overlapping routing, content-addressing, Phase-3 gate survival, Coverage composition, empty-list and empty-unit edge cases, return-type shape.

## Decisions Made
- **Empty unit ⇒ zero-width Claim** (not unextracted): `str.find("")` returns the cursor, so `""` is genuinely a (zero-width) substring; emitting a faithful empty span is more honest than inventing an "unlocatable" reason for it. Cursor is not advanced (no consumption).
- **Forward-only cursor for overlapping units:** chose non-overlapping, forward-only provenance over backtracking. A unit overlapping an already-claimed span routes to `unextracted[]` rather than being re-pointed inside consumed text — preserves correct per-claim provenance (the whole reason the cursor exists, RESEARCH Pitfall 5).
- **`confidence=0.0` passed explicitly** to `Claim()` — extraction is faithful, not a judgement; 0.0 is the existing default, so this is the established `capture.py` explicit-construction style and changes no behavior.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Explicit `confidence=0.0` for mypy-clean `Claim()` construction**
- **Found during:** Task 2 (standing-invariant gate run)
- **Issue:** `mypy src/newsletters/adapters src/newsletters/distill` reported `Missing named argument "confidence" for "Claim"` on `Claim(text=unit, evidence=[trace])`. The repo has no pydantic mypy plugin configured, so mypy did not infer the `Field(0.0, …)` default as optional — the mypy gate (a definition-of-done gate per CLAUDE.md) would have failed.
- **Fix:** Passed `confidence=0.0` explicitly (the existing default; the established explicit-construction style in `capture.py`). No behavior change.
- **Files modified:** `src/newsletters/adapters/normalize.py`
- **Verification:** `mypy` → `Success: no issues found in 9 source files`; `test_normalize.py` still 14 passed; full suite 99 passed / 1 xfailed.
- **Committed in:** `035bae3`

---

**Total deviations:** 1 auto-fixed (1 blocking).
**Impact on plan:** Necessary to keep the mypy DoD gate green; zero behavior change, no scope creep.

## Gate Results (re-run independently — actual output)

- **`pytest tests/test_normalize.py -q`** → `14 passed in 0.02s`
- **`pytest -q` (full suite)** → `99 passed, 1 xfailed in 4.71s` (baseline was 85 passed / 1 xfailed; +14 new, no regression)
- **`mypy src/newsletters/adapters src/newsletters/distill`** → `Success: no issues found in 9 source files`
- **`lint-imports`** → `Contracts: 1 kept, 0 broken` — `Core (newsletters) must not import any AI/LLM package KEPT` (proves `normalize` is stdlib/AI-free)
- **`grep -v '^#' normalize.py | grep -c 'hashlib\|sha256'`** → `0` (no hand-minted hashing; `Trace.from_source` is the sole minting path)
- **Inline plan verify** (`normalize(s, ['ab','ab'])` ⇒ 2 claims, starts 0 & 4, all addressed) → `normalize OK`

## TDD Gate Compliance
- RED gate present: `9e3f281` (`test(04-01): …`) — failed on `ModuleNotFoundError: No module named 'newsletters.adapters'` before implementation.
- GREEN gate present: `81069fb` (`feat(04-01): …`) — the failing tests passed after implementation.
- No REFACTOR commit (implementation was clean as written; the later `035bae3` is a `fix`, not a refactor).

## Known Stubs
None — `normalize()` is fully wired; no placeholders, no hardcoded empties flowing to a UI.

## Issues Encountered
- A pre-existing `mypy` finding in `capture.py` (`Argument "locator" to "Trace" has incompatible type "str"`) is OUT OF SCOPE for this plan (not in `adapters`/`distill`, not caused by this task) — left untouched per the scope boundary. The plan-specified mypy scope (`adapters` + `distill`) is clean.

## Next Phase Readiness
- 04-02 (Email adapter) can import `from newsletters.adapters import normalize` and call it with transcript-order units; the public API, raw-unit input contract, `unextracted[]` entry shape, offset/cursor semantics, and edge-case behavior are documented above.
- Standing invariants all green; ready for `/gsd-verify-work` after the wave completes.

## Self-Check: PASSED
- Created files verified on disk: `adapters/__init__.py`, `adapters/normalize.py`, `tests/test_normalize.py`, `04-01-SUMMARY.md`.
- Commits verified in git log: `9e3f281` (test), `81069fb` (feat), `035bae3` (fix).

---
*Phase: 04-shared-adapter-normalizer-email*
*Completed: 2026-06-17*
