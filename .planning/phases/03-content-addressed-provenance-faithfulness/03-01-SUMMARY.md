---
phase: 03-content-addressed-provenance-faithfulness
plan: 01
subsystem: semantic-spine
tags: [provenance, sha256, hashlib, content-addressing, stale-detection, trace, pydantic]

# Dependency graph
requires:
  - phase: 01-distill-socket
    provides: typed Locator union (FreeLocator/SessionLocator), Trace.span field, injectable faithfulness seam
  - phase: 02-ai-optional-packaging
    provides: import-linter AI-optional contract (core = stdlib + pydantic only)
provides:
  - Source.content_hash() — stdlib SHA-256 hex digest of the full transcript
  - Trace optional content-address fields (content_hash, start, end) — backward-compatible
  - Trace.from_source(source, start, end, *, locator=None) — the single self-verifying content-address constructor
  - Trace.is_addressed property and Trace.is_stale_against(source) — computed per-trace STALE
  - Claim.is_stale(sources) — computed per-claim STALE
  - Distillation.stale_claims(sources=None) — computed per-distillation STALE list
affects: [03-02, 03-03, faithfulness-gate, source-migration, adapters]

# Tech tracking
tech-stack:
  added: []  # stdlib hashlib only — zero new dependency, AI-optional contract preserved
  patterns:
    - "Content-addressing: pin SHA-256 of full Source content + char offsets + verbatim span, not a fragile position"
    - "STALE is a COMPUTED property comparing live hash to recorded hash — never a stored mutable flag"
    - "Optional additive model fields (default None) preserve Rev1 backward-compat"
    - "Single canonical constructor (Trace.from_source) owns all pinning logic; offsets validated before slicing"

key-files:
  created:
    - tests/test_provenance.py
  modified:
    - src/newsletters/semantic.py

key-decisions:
  - "D-1: SHA-256 (stdlib hashlib) of the FULL Source.transcript + CHARACTER offsets (start/end) + verbatim span"
  - "D-2: STALE is computed (live hash != recorded hash) at trace/claim/distillation granularity; no stored flag"
  - "D-4: content-address fields are OPTIONAL (default None) so Rev1 traces + existing tests stay green"
  - "Un-addressed traces (content_hash=None) are never STALE and never raise — refuses false positives"
  - "from_source validates offsets (negative/inverted/out-of-range) with a teaching ValueError before slicing — faithful, not suggestive"

patterns-established:
  - "Content-addressed evidence: Trace.from_source is the one mint point for content-addressed traces"
  - "Computed STALE: recompute drift from live source hashes every call; no flag-vs-reality divergence possible"

requirements-completed: [PROV-01]

# Metrics
duration: ~12min
completed: 2026-06-17
---

# Phase 3 Plan 01: Content-Addressed Provenance Summary

**Content-addressed self-verifying `Trace` (stdlib SHA-256 of full Source + char offsets + verbatim span) with STALE as a purely computed property at trace/claim/distillation granularity — zero new dependency, full Rev1 backward-compat.**

## Performance

- **Duration:** ~12 min
- **Tasks:** 3 (all TDD)
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments
- `Source.content_hash()` returns the stdlib SHA-256 hex digest of the full `transcript` (deterministic; empty transcript hashes to SHA-256 of `b""`, no special-casing).
- `Trace` gained three OPTIONAL content-address fields (`content_hash`, `start`, `end`) defaulting to `None` — every Rev1 Trace and the bare-string-locator coercion path stay valid.
- `Trace.from_source(source, start, end, *, locator=None)` is the single self-verifying content-address constructor: it pins the hash, the character offsets, and `span = transcript[start:end]`, and refuses bad offset ranges with a teaching `ValueError` before slicing.
- STALE is a purely COMPUTED property at three granularities — `Trace.is_stale_against`, `Claim.is_stale`, `Distillation.stale_claims` — with no stored mutable flag anywhere.

## The Trace public API (for Wave 2 — Plans 03-02 / 03-03)

This is the contract the dependent plans build on. Field names, signatures, and STALE semantics are stable:

```python
class Source(BaseModel):
    id: str
    transcript: str = ""
    # ...
    def content_hash(self) -> str: ...
        # hashlib.sha256(self.transcript.encode("utf-8")).hexdigest()

class Trace(BaseModel):
    source_id: str
    locator: Locator = FreeLocator()      # unchanged; bare str still coerces
    span: str = ""                        # verbatim source snippet (pre-existing)
    # NEW — all OPTIONAL, default None (D-4 backward-compat):
    content_hash: Optional[str] = None    # SHA-256 of FULL source at capture time
    start: Optional[int] = None           # char offset, inclusive
    end: Optional[int] = None             # char offset, exclusive

    @classmethod
    def from_source(
        cls, source: Source, start: int, end: int,
        *, locator: Optional[Locator] = None,
    ) -> Trace: ...
        # pins content_hash=source.content_hash(), start/end, span=transcript[start:end]
        # raises ValueError if start<0, end<start, or end>len(transcript)
        # locator defaults to FreeLocator() when None

    @property
    def is_addressed(self) -> bool: ...      # content_hash is not None

    def is_stale_against(self, source: Source) -> bool: ...
        # is_addressed and source.content_hash() != self.content_hash
        # un-addressed Trace -> always False, never raises

class Claim(BaseModel):
    def is_stale(self, sources: dict[str, Source]) -> bool: ...
        # True iff ANY evidence trace is stale against sources[trace.source_id]
        # traces whose source_id is absent from `sources` are skipped (no KeyError)

class Distillation(BaseModel):
    def stale_claims(self, sources: Optional[dict[str, Source]] = None) -> list[Claim]: ...
        # when sources is None, lookup is built from self.traces ({s.id: s})
        # returns the drifted claims; [] when nothing drifted
```

**STALE semantics (load-bearing for Wave 2):**
- STALE = live `source.content_hash()` differs from the Trace's recorded `content_hash`.
- An un-addressed Trace (`content_hash is None`, the Rev1 path) is `is_addressed == False`, is **never** STALE, and **never raises** — absence of a hash means "not content-addressed / unknown", never a false positive.
- There is **no** stored stale boolean on `Trace`/`Claim`/`Distillation` — it is recomputed from live hashes every call (guarded by `test_stale_is_purely_computed_no_stored_flag`).

## Task Commits

Implemented as a TDD plan (RED → GREEN; no refactor needed):

1. **RED — failing provenance tests** (all three tasks' behavior) — `83ca83a` (test)
2. **GREEN — content-addressed Trace + computed STALE** (Tasks 1–3) — `08ae510` (feat)

_Note: the three plan tasks (content-address fields, self-verifying `from_source`, computed STALE) form one cohesive feature; the GREEN implementation landed them together after a single RED gate covering all of their behavior._

## Gate Results (re-run independently via .venv/bin/python)

- `pytest -q` (full suite): **53 passed, 1 xfailed** (baseline was 36 passed, 1 xfailed — +17 new provenance tests, zero regressions; Rev1 coercion + JSON round-trip in test_distill_socket.py stay green).
- `pytest tests/test_provenance.py -q`: **17 passed**.
- `mypy src/newsletters/semantic.py src/newsletters/distill`: **Success: no issues found in 7 source files**.
- `lint-imports`: **Contracts: 1 kept, 0 broken** (AI-optional contract intact — stdlib `hashlib` only, zero AI import).

## Files Created/Modified
- `tests/test_provenance.py` (created) — RED-first tests for content-addressing, self-verification, STALE detection at all three granularities, and Rev1 backward-compat (optional fields default None, bare-string coercion, JSON round-trip).
- `src/newsletters/semantic.py` (modified) — added `import hashlib`; `Source.content_hash()`; `Trace.{content_hash,start,end}` fields + `from_source` + `is_addressed` + `is_stale_against`; `Claim.is_stale`; `Distillation.stale_claims`.

## Decisions Made
None beyond the fixed phase decisions (D-1, D-2, D-4) — followed the plan and 03-CONTEXT.md exactly. Two specifications worth restating because Wave 2 depends on them:
- Un-addressed Trace STALE behavior: resolved as "never STALE / unknown, never a false positive" (matches the plan's recommendation and `<critical_correctness>`).
- Offset validation: refuse (teaching `ValueError`) rather than clip — "faithful, not suggestive".

## TDD Gate Compliance
- RED gate present: `test(03-01)` commit `83ca83a` (15 failing, 2 guard tests already green).
- GREEN gate present: `feat(03-01)` commit `08ae510` after RED.
- REFACTOR: none required — implementation was minimal and clean at GREEN.

## Deviations from Plan
None — plan executed exactly as written.

## Known Stubs
None.

## Threat Flags
None — the changes mitigate the planned threats (T-03-01 STALE computed property; T-03-02 self-verifying span; T-03-04 offset validation) and introduce no new security surface (T-03-03: only the public SHA-256 integrity tag is stored, not the transcript). No new dependency (T-03-SC).

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- The `Trace.from_source` constructor and the STALE properties are the public API that Plan 03-02 (Source migration / minting content-addressed traces for sample sources) and Plan 03-03 (faithfulness/entailment gate at the socket seam) build on. Signatures and STALE semantics are documented above.
- The injectable faithfulness seam from Phase 1 (`distill/ports.py::_enforce`) is untouched and ready for the Phase-3 deterministic span-containment gate (Plan 03-03's swap point).

## Self-Check: PASSED
- FOUND: tests/test_provenance.py
- FOUND: src/newsletters/semantic.py
- FOUND: .planning/phases/03-content-addressed-provenance-faithfulness/03-01-SUMMARY.md
- FOUND commit: 83ca83a (RED)
- FOUND commit: 08ae510 (GREEN)

---
*Phase: 03-content-addressed-provenance-faithfulness*
*Completed: 2026-06-17*
