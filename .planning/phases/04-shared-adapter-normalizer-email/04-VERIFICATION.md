---
phase: 04-shared-adapter-normalizer-email
verified: 2026-06-17T00:00:00Z
status: passed
score: 3/3 success criteria verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
gaps: []
human_verification: []
---

# Phase 4: Shared Adapter Normalizer & Email Adapter — Verification Report

**Phase Goal:** Put the faithful-extraction rule in exactly one place (the shared `normalize()`) and
prove it with the first, simplest adapter — Email, stdlib-only, no extra.
**Verified:** 2026-06-17 (independent re-run on branch `claude/youthful-fermi-dly6mi`)
**Status:** passed (3/3 success criteria) — one robustness LIMITATION documented (non-blocking)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A shared `normalize()` converts any adapter's raw extraction into typed `Claim(+Trace)` with source locators, and the faithful-extraction rule lives in EXACTLY ONE place | VERIFIED | `normalize.py:50-117` is the only function minting claims; structural one-place finding below |
| 2 | The Email adapter extracts structured content from `.eml` into `Claim(+Trace)` and reports unextracted parts (forwarded rfc822, charset losses) in `unextracted[]` | VERIFIED | `email_adapter.py` U1-U8 routing; live charset-ladder + U+FFFD probes pass |
| 3 | A golden-file test (fixture `.eml` → expected typed claims+traces) covers the Email adapter and asserts ZERO silent drops | VERIFIED | `test_email_golden.py` — 49 tests, 8 fixtures, accounting identity per fixture; re-run = `49 passed` |

**Score: 3/3 success criteria verified.**

---

## Criterion 1 — The One-Place Rule (the central structural claim)

**VERIFIED — the faithful-extraction rule is genuinely in exactly one place.**

Evidence from live `grep` across `src/newsletters/adapters/`:

- **`Trace.from_source` is called in exactly ONE adapter file:** `normalize.py:111` (`trace = Trace.from_source(source, idx, end)`). `email_adapter.py` contains **zero** calls to `Trace.from_source` — it only hands verbatim `units: list[str]` to `normalize()` (`email_adapter.py:322`). The other `Trace.from_source` reference in `adapters/` is a docstring mention (`normalize.py:13,31,71,87,108`), not a call.
- **Zero hand-minted hashes in adapters:** `grep -nE "hashlib|sha256|content_hash ="` over `adapters/` returns **no code matches** — neither `normalize.py` nor `email_adapter.py` computes a hash. Hashing is delegated to `Trace.from_source` (`semantic.py:109-153`), which validates offsets before slicing.
- **`email` is imported in exactly ONE module:** `grep -rln "import email" src/newsletters/` → only `src/newsletters/adapters/email_adapter.py` (lines 30-32). `normalize.py` imports only `..semantic`, `..locators`, `..distill.coverage` — it never imports `email` or any adapter-specific module, so the trust rule is format-agnostic.
- **The adapter routes through `normalize()`, never bypasses it:** `email_adapter.distill()` (`email_adapter.py:308-338`) calls `normalize(source, units)` (line 322) for every source; the only claims it emits come from that return value. There is no alternate claim-minting path.

The other `Trace.from_source` callers in the repo (`dogfood.py:112`) are the Phase-3 re-mint path, **outside** `adapters/` — they do not duplicate the adapter faithfulness rule. The one-place invariant holds.

---

## Criterion 2 — Email Adapter Extraction + `unextracted[]` Honesty

**VERIFIED** via independent live probes (temp scripts, not committed, since deleted).

**Charset ladder (CONTEXT decision 7) — `faithful_decode`, `email_adapter.py:62-85`:**

| Probe | Input | Result | Verdict |
|-------|-------|--------|---------|
| Unknown charset name | `decode(b"hello", "x-unknown-charset")` | `LookupError` caught → falls to `utf-8`, `fell_back=True` | ✓ LookupError handled |
| Mislabeled utf-8 | `decode(b"caf\xe9", "utf-8")` | `UnicodeDecodeError` caught → `latin-1`, `fell_back=True` (faithful `café`) | ✓ UnicodeDecodeError handled |
| Declared latin-1 valid | `decode(b"caf\xe9", "latin-1")` | `latin-1`, `fell_back=False` | ✓ no spurious fallback |
| No declared + valid utf-8 | `decode(b"hello", None)` | `utf-8`, `fell_back=False` | ✓ |

Both `UnicodeDecodeError` AND `LookupError` are caught (`email_adapter.py:77`); `latin-1 strict` is total so the ladder always terminates.

**U+FFFD detection (U4):** a live `.eml` whose 8bit body already contains `U+FFFD` → routed to `unextracted[]` with reason `"undecodable bytes replaced with U+FFFD — text not faithful"`, `complete=False` (`email_adapter.py:250-253`).

**Forwarded `message/rfc822` (U1):** `_walk_attachments` (`email_adapter.py:260-286`) iterates ALL of `iter_attachments()` and detects `get_content_maintype()=="message"` — correctly catching the inline-rfc822 gotcha (RESEARCH Pitfall 3) where `is_attachment()==False`. Golden fixture `forwarded_rfc822.eml`: U1 fires, nested body `"This is the forwarded body."` never leaks into a claim or transcript (`test_email_golden.py:241-249`).

**Coverage honesty:** `distill()` sets `Coverage(complete=(len(merged_unextracted)==0), ...)` (`email_adapter.py:328-333`). Live probes confirm `complete==False` whenever anything is unextracted; the `Coverage` validator makes "complete with drops" unrepresentable.

---

## Criterion 3 — Golden-File Test, ZERO Silent Drops

**VERIFIED.** `tests/test_email_golden.py` (8 byte-exact fixtures, 49 tests) re-run independently:
`pytest tests/test_email_golden.py -q` → **`49 passed in 0.18s`**.

Per fixture it asserts (parametrized over all 8):
- **`test_zero_silent_drops`** — the accounting identity `len(claims) + len(unextracted) == pinned total units`, AND the `unextracted[].reason` strings match the U1-U8 contract exactly and in order (`test_email_golden.py:107-131`).
- **`test_claims_are_verbatim_and_content_addressed`** — `claim.text == trace.span` AND `source.transcript[start:end] == claim.text` (re-slice of live transcript) AND `trace.is_addressed` (`:134-153`).
- **`test_coverage_honesty`** — `complete == (len(unextracted)==0)` (`:156-163`).
- **`test_conformance_and_json_roundtrip`** — `assert_conforms(...)` + explicit lossless JSON round-trip per fixture (`:166-176`).
- **`test_determinism`** — parse twice → EQUAL result (`:179-184`).

Plus targeted routing tests pinning U1/U2/U3/U5/U7 and the multipart-alternative no-double-count. All 8 fixtures exist on disk (`test_corpus_is_eight_committed_fixtures`).

---

## Zero-Silent-Drops Robustness Assessment (skeptical)

I tried to break the accounting identity with adversarial inputs beyond the 8 fixtures. Findings:

| Adversarial probe | Result | Verdict |
|-------------------|--------|---------|
| **Deeply nested** multipart/mixed → multipart/alternative + a deep `image/png` attachment | plain body claimed once; deep png routed to U2; `complete=False` | ✓ airtight — `iter_attachments()` reaches nested parts |
| **Empty** `text/plain` body | 4 header claims, 0 body claims, 0 drops, `complete=True` | ✓ honest — empty body has nothing to extract; no fabrication |
| **multipart/alternative** html twin not counted, not dropped | by MIME semantics the html alt is the SAME content as the plain part (`get_body` picks plain; html alt is not in `iter_attachments()`) | ✓ defensible — not a silent drop |

**The identity is internally airtight for the adapter's OWN enumeration** (headers + body paragraphs + `iter_attachments()` parts + defect-bearing parts via `msg.walk()`). Container/structural parts (the multipart wrappers themselves) are correctly NOT counted as droppable content units — they carry no prose.

### LIMITATION found (documented, NON-BLOCKING)

**The U1-U7 adapter-side drops are only recoverable when `distill()` runs on the SAME adapter instance that `parse()`d the Source.** They are stored in an in-memory dict keyed by `source.id` (`email_adapter.py:134, 203, 364`). I confirmed the gap live:

- **Path A (documented entrypoint):** `a.parse(raw, path)` then `a.distill([src])` → U1 forwarded-rfc822 drop present, `complete=False`. ✓ Correct.
- **Path B (JSON round-trip → fresh adapter):** `Source.model_validate_json(src.model_dump_json())` then `EmailAdapter().distill([src2])` → **U1 drop LOST, `unextracted==[]`, `complete=True`** — a fresh adapter has no `_adapter_unextracted` record for that `source.id`, so `.get(source.id, [])` returns empty.

**Why this is NOT a Phase-4 BLOCKER:**
- The phase goal, success criteria, and documented contract (04-02-SUMMARY "Golden-corpus usage") all specify the `parse()`-then-`distill()` same-instance flow, which is faithful. Criterion 3 ("the golden test asserts zero silent drops") is met on that flow.
- The body/paragraph CLAIMS still mint faithfully on Path B (they are reconstructable from the transcript); only the format-specific U1-U7 *disclosures* (a stripped attachment leaves no transcript trace) are lost.
- This is a known design seam the adapter documents (`email_adapter.py:340-352`): "A `Source` not produced by this adapter's `parse` simply has no recorded drops."

**Why it is still worth flagging:** a downstream `DistillPort` consumer that persists `Source`s and later calls `resolve("email").distill(sources)` on a fresh process/instance would get `complete=True` while a forwarded `message/rfc822` part was silently dropped — a faithful-extraction violation on that path. The golden test does NOT exercise Path B (`test_conformance_and_json_roundtrip` re-`parse()`s with the fresh adapter first, so the record exists). **Recommendation (future hardening, not a Phase-4 gap):** make the adapter U1-U7 drops reconstructable from the `Source` itself (e.g. persisted on `Source.context`/metadata) so `distill()` is stateless, OR have `assert_conforms`/the socket assert coverage parity across a JSON round-trip with a fresh adapter.

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/newsletters/adapters/normalize.py` | shared faithful normalize() | ✓ VERIFIED | 117 lines; sole `Trace.from_source` caller; no hash; imports no `email` |
| `src/newsletters/adapters/email_adapter.py` | Email .eml adapter | ✓ VERIFIED | 366 lines; only `email` importer; U1-U8 routing; never publishes |
| `src/newsletters/adapters/_html_text.py` | deterministic html→text | ✓ VERIFIED | stdlib `html.parser`; always-lossy; skips script/style/head |
| `src/newsletters/adapters/__init__.py` | package + registry registration | ✓ VERIFIED | `register(EmailAdapter())`; `resolve("email")` live |
| `tests/test_normalize.py` | normalize unit tests | ✓ VERIFIED | present, in full suite |
| `tests/test_email_adapter.py` | adapter tests | ✓ VERIFIED | present, in full suite |
| `tests/test_email_golden.py` | golden corpus test | ✓ VERIFIED | 49 passed independently |
| `tests/fixtures/eml/*.eml` | 8 byte-exact fixtures | ✓ VERIFIED | 8 `.eml` + `_author_fixtures.py` on disk |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `email_adapter.distill` | `normalize()` | `normalize(source, units)` call | WIRED | `email_adapter.py:322` |
| `normalize()` | `Trace.from_source` | sole minting path | WIRED | `normalize.py:111` |
| `adapters/__init__` | `distill.register` | `register(EmailAdapter())` | WIRED | live `resolve("email")` returns instance |
| `distill` package | `adapters` | (must be absent — acyclic) | CORRECTLY ABSENT | no `import adapters` in `distill/` |

### Probe Execution (independent live runs)

| Probe | Command | Result | Status |
|-------|---------|--------|--------|
| Charset ladder | `faithful_decode` matrix | LookupError + UnicodeDecodeError caught, fallbacks flagged | PASS |
| U+FFFD detection | live 8bit `.eml` | U4 fires, complete=False | PASS |
| Nested multipart | mixed→alternative + deep png | plain claimed, png→U2 | PASS |
| Empty body | empty text/plain | 0 fabricated claims, no spurious drop | PASS |
| Silent-drop gap | JSON round-trip + fresh `distill` | U1 LOST, complete=True | LIMITATION (documented) |

### Gate Results (re-run independently via `.venv/bin/python` — actual output)

| Gate | Command | Output | Status |
|------|---------|--------|--------|
| Full suite | `pytest -q` | `177 passed, 1 xfailed in 5.14s` | PASS |
| Golden test | `pytest tests/test_email_golden.py -q` | `49 passed in 0.18s` | PASS |
| mypy | `mypy src/newsletters/adapters src/newsletters/distill` | `Success: no issues found in 11 source files` | PASS |
| Import linter | `lint-imports` | `Contracts: 1 kept, 0 broken` (forbid-ai-in-core KEPT) | PASS |
| Renderer build | `newsletters build --out /tmp/...` | `rendered 9 surfaces + the library index` | PASS |
| AI-optional runtime guard | `pytest tests/test_ai_optional.py -q` | `4 passed, 1 xfailed` | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ADAPT-01 | 04-01 | shared normalize() — rule in one place | ✓ SATISFIED | normalize.py sole minting path |
| ADAPT-02 | 04-02 | Email .eml adapter + unextracted reporting | ✓ SATISFIED | email_adapter.py + live probes |
| ADAPT-06 | 04-03 | golden-file tests | ✓ SATISFIED | test_email_golden.py 49 passed |

### Hard-Rule Status

| Hard rule | Status | Evidence |
|-----------|--------|----------|
| AI-optional core | ✓ HELD | `lint-imports` KEPT (logfire in forbidden list, no static edge); no new static AI import in adapters; logfire appearing in `sys.modules` is the documented pydantic-plugin auto-activation leak (`.importlinter:8-15`), not a Phase-4 regression — closed by `test_ai_optional.py` + bare-install CI |
| Faithful, not suggestive | ✓ HELD | normalize() only mints verbatim substrings; non-locatable → unextracted; no paraphrase |
| No auto-publish | ✓ UNTOUCHED | adapters never call `Surface.publish`/set `PUBLISHED`/build `Review`; publish-gate tests green (27 passed) |
| No new dependency | ✓ HELD | `git diff HEAD -- pyproject.toml` empty; `.importlinter` unmodified; stdlib `email`/`html.parser` only |
| Every published claim traces to evidence | ✓ HELD | every claim has exactly one content-addressed `Trace` (golden test asserts `is_addressed`) |

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX`/`HACK`/`PLACEHOLDER`/"not yet implemented" markers in any of the 6
Phase-4 source/test files. No stubs (all artifacts are fully wired and exercised end-to-end on real bytes).

### Human Verification Required

None — all criteria are programmatically verifiable and were verified by re-running gates and live probes.

### Gaps Summary

No blocking gaps. All 3 ROADMAP success criteria are achieved in live code and proven by an
independently re-run golden corpus. The one-place faithful-extraction rule is structurally verified
(single `Trace.from_source` call site, zero adapter hashing, `email` imported in one module). All
hard rules hold; all gates re-run green independently.

**One non-blocking robustness LIMITATION** is documented: the adapter's U1-U7 `unextracted[]`
disclosures are recoverable only on the same-instance `parse()`→`distill()` flow; a fresh-adapter
`distill()` on a JSON-round-tripped `Source` silently loses them and reports `complete=True`. This is
outside the phase's documented contract and goal, body claims still mint faithfully, and it is an
acknowledged design seam — but it is a faithful-extraction risk worth hardening before adapters are
consumed via persisted `Source`s downstream (Phases 5-7 reuse this template).

---

_Verified: 2026-06-17_
_Verifier: Claude (gsd-verifier) — independent gate re-run + live adversarial probes on branch claude/youthful-fermi-dly6mi_
