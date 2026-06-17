---
phase: 04-shared-adapter-normalizer-email
plan: 03
subsystem: adapters
tags: [email, eml, golden-file, fixtures, zero-silent-drops, accounting-identity, conformance, determinism, U1-U8, stdlib]

# Dependency graph
requires:
  - phase: 04-02
    provides: "EmailAdapter registered as 'email' — parse(raw,path) + distill([source]); the canonical decoded transcript + U1-U8 unextracted[] routing under test here"
  - phase: 04-01
    provides: "shared normalize() — the verbatim-locate + content-addressed Trace minting the golden test asserts is faithful"
  - phase: 01-distill-socket
    provides: "assert_conforms (shape + return-type + coverage honesty + span-containment + lossless JSON round-trip), DistillationResult, Coverage"
provides:
  - "tests/fixtures/eml/*.eml — a committed 8-fixture golden corpus spanning the full email routing matrix (clean / RFC2047 / multipart-alternative / html-only / mixed+pdf / forwarded-rfc822 / mislabeled-charset / malformed-boundary)"
  - "tests/test_email_golden.py — the executable proof of CONTEXT decision 4: zero silent drops (the accounting identity) across the matrix, plus verbatim+content-addressed claims, coverage honesty, conformance+round-trip, and determinism"
  - "_author_fixtures.py — byte-exact fixture regenerator (committed test-data tooling)"
affects: [future-adapters-excel-pptx-powerbi, gsd-verify-work]

# Tech tracking
tech-stack:
  added: []  # stdlib only (email, email.policy, pathlib) + pytest (already in [dev]); NO new dependency
  patterns:
    - "Golden fixtures authored as EXACT bytes via a committed generator script — an editor cannot be trusted to preserve CRLF headers or a deliberate lone latin-1 0xe9 byte"
    - "The expected per-fixture counts/routing are derived by driving the LIVE adapter (verify-the-object, not assume), then PINNED inline as the contract the matrix must keep holding"
    - "The accounting identity (len(claims)+len(unextracted) == units walked) is the executable form of 'no silent drops' — a silent drop is, by construction, a test failure (threat T-04-08)"

key-files:
  created:
    - tests/fixtures/eml/plain_simple.eml
    - tests/fixtures/eml/rfc2047_subject.eml
    - tests/fixtures/eml/multipart_alternative.eml
    - tests/fixtures/eml/html_only.eml
    - tests/fixtures/eml/mixed_with_pdf.eml
    - tests/fixtures/eml/forwarded_rfc822.eml
    - tests/fixtures/eml/mislabeled_charset.eml
    - tests/fixtures/eml/malformed_boundary.eml
    - tests/fixtures/eml/_author_fixtures.py
    - tests/test_email_golden.py
  modified: []

key-decisions:
  - "Fixtures authored as byte-exact .eml via a committed generator (_author_fixtures.py) rather than hand-typed text — the corpus depends on CRLF wire headers and a deliberate raw 0xe9 latin-1 byte that text editors normalize; the generator documents the exact provenance and makes the corpus reproducible byte-for-byte"
  - "Expected counts/routing pinned inline (the Expected table) and derived from a one-shot probe of the LIVE adapter — the test encodes the contract, not a guess; the identity asserts len(claims)+len(unextracted) equals that pinned total with zero unaccounted units"
  - "The html-only injection check is scoped to BODY claims — header values legitimately contain '<' (e.g. 'Team <team@example.com>'), so a blanket no-'<' assertion was a false positive; the real invariant is that the stripped body paragraphs carry no markup"

requirements-completed: [ADAPT-06]

# Metrics
duration: 4min
completed: 2026-06-17
---

# Phase 04 Plan 03: Email Golden-File Corpus Summary

**Eight tiny, committed `.eml` fixtures drive `EmailAdapter` across its full routing matrix, and `tests/test_email_golden.py` asserts — for every one — the zero-silent-drops accounting identity (`#claims + #unextracted == #units walked`), verbatim + content-addressed claims, coverage honesty, `assert_conforms` (span-containment + lossless JSON round-trip), and determinism: the executable proof that no email content is ever silently dropped (CONTEXT decision 4, ADAPT-06).**

## Performance
- **Duration:** ~4 min
- **Started:** 2026-06-17T14:45Z
- **Completed:** 2026-06-17T14:49Z
- **Tasks:** 2 (fixtures, then the golden test + gate re-run)
- **Files:** 10 created, 0 modified

## Accomplishments
- Authored **8 byte-exact `.eml` golden fixtures** under `tests/fixtures/eml/`, each exercising one corner of the email routing matrix with explicit `Content-Transfer-Encoding`/`charset` so the decode path is exercised, not incidental. All 8 parse under `email.policy.default`.
- Wrote **`tests/test_email_golden.py`** (49 tests via parametrization over the corpus + targeted routing tests) asserting the six core invariants per fixture and the U1/U2/U3/U5/U7 routing + no-double-count of the html alternative.
- **The zero-silent-drops accounting identity holds for ALL 8 fixtures** — verified live (see table below). The success criterion "no content is silently dropped" is now demonstrated by a committed corpus, not asserted by prose.
- All standing-invariant gates re-run independently and green; full suite grew 128 → 177 passed (+49), no regression.

## The 8 fixtures + what each exercises (the live accounting identity)

| Fixture | Exercises | Claims | unextracted[] (U#) | `complete` | Identity (claims + unx) |
|---------|-----------|:------:|--------------------|:----------:|:-----------------------:|
| `plain_simple.eml` | text/plain ASCII, 2 paragraphs — the clean complete case | 6 (4 hdr + 2 body) | — | True | 6 = 6 ✓ |
| `rfc2047_subject.eml` | `=?utf-8?q?…?=` Subject → DECODED unicode `Quarterly — café results`, verbatim in transcript | 5 (4 hdr + 1 body) | — | True | 5 = 5 ✓ |
| `multipart_alternative.eml` | text/plain + text/html alternatives → body from PLAIN; html alt **not** double-counted, **not** dropped | 5 (4 hdr + 1 body) | — | True | 5 = 5 ✓ |
| `html_only.eml` | text/html, no plain alt → emit-both: stripped paragraph claims **+ U5** | 6 (4 hdr + 2 body) | 1 — **U5** html lossy strip | False | 7 = 7 ✓ |
| `mixed_with_pdf.eml` | multipart/mixed, text body + `application/pdf` attachment (never decoded) **+ U2** | 5 (4 hdr + 1 body) | 1 — **U2** non-text attachment | False | 6 = 6 ✓ |
| `forwarded_rfc822.eml` | nested `message/rfc822` → top body claims **+ U1**; nested mail NOT extracted | 5 (4 hdr + 1 body) | 1 — **U1** forwarded rfc822 | False | 6 = 6 ✓ |
| `mislabeled_charset.eml` | declares utf-8, body has a lone latin-1 `0xe9` → faithful latin-1 fallback **+ U3** (no U4) | 5 (4 hdr + 1 body) | 1 — **U3** charset fallback | False | 6 = 6 ✓ |
| `malformed_boundary.eml` | missing close boundary → readable body still extracted **+ U7** `CloseBoundaryNotFoundDefect` | 5 (4 hdr + 1 body) | 1 — **U7** MIME defect | False | 6 = 6 ✓ |

**The identity holds for all 8** — `len(claims) + len(unextracted) == units walked`, exactly, with zero unaccounted units. The headline success criterion (ADAPT-06, CONTEXT decision 4) is met.

Notable matrix confirmations the test pins:
- **RFC2047 Subject decodes to unicode** (`Quarterly — café results`) and is verbatim in the transcript — the claim text is the decoded form, not the encoded word.
- **multipart/alternative draws from the plain part once** — the html alternative is the SAME content, so it is neither double-counted nor recorded as a drop (it is not lost; it is the same text).
- **mislabeled charset falls back faithfully** — a lone `0xe9` invalid as standalone utf-8 decodes via the strict ladder to latin-1 `é` (faithful `Café`), firing **U3** with **no** residual U+FFFD, so U4 correctly does **not** fire.
- **forwarded nested mail stays out of scope** — `This is the forwarded body.` never leaks into a claim or the transcript; only the U1 disclosure records its existence.

## What the golden test asserts (every fixture)
1. **Zero silent drops** — `len(claims) + len(unextracted) == pinned total units` (threat T-04-08); the `unextracted[].reason` strings match the U1–U8 contract exactly and in order.
2. **Faithful spans** — `claim.text == claim.evidence[0].span` AND `source.transcript[trace.start:trace.end] == claim.text` (re-slice of the live transcript).
3. **Content-addressed** — every claim's trace `is_addressed` (minted through `Trace.from_source`).
4. **Coverage honesty** — `coverage.complete == (len(coverage.unextracted) == 0)`.
5. **Conformance + round-trip** — `assert_conforms(EmailAdapter(), [source])` passes (span-containment + lossless JSON round-trip, `conformance.py:38-94`).
6. **Determinism** — parsing the same fixture twice yields an EQUAL `DistillationResult` (threat T-04-09).

## Files Created
- `tests/fixtures/eml/{plain_simple,rfc2047_subject,multipart_alternative,html_only,mixed_with_pdf,forwarded_rfc822,mislabeled_charset,malformed_boundary}.eml` — the 8 committed golden fixtures (233–627 bytes each).
- `tests/fixtures/eml/_author_fixtures.py` — the byte-exact generator (CRLF headers, the deliberate lone latin-1 byte); committed test-data tooling so the corpus is reproducible.
- `tests/test_email_golden.py` — the golden test (49 tests: 5 parametrized invariant suites × 8 fixtures + a corpus-completeness check + 8 targeted routing tests).

## Decisions Made
- **Byte-exact fixtures via a committed generator.** The corpus hinges on CRLF wire headers and a deliberate raw `0xe9` byte that a text editor would normalize. A small generator (`_author_fixtures.py`) authors them as exact bytes and documents the provenance, so anyone can regenerate the corpus byte-for-byte and audit precisely what each fixture sends.
- **Expected counts pinned from the LIVE adapter, not assumed.** Per the project's "the agent says green ≠ green" discipline, the expected per-fixture counts/routing were derived by probing the running adapter once, then encoded inline as the contract the test enforces.
- **Injection check scoped to body claims.** A first pass asserted no claim contains `<`; that is a false positive because a `To:`/`From:` header value legitimately contains `<` (`Team <team@example.com>`). The real invariant — the stripped html body carries no markup — is asserted against the body paragraph claims specifically.

## Deviations from Plan
None — plan executed as written. Task 1 (fixtures) and Task 2 (golden test) were committed atomically and in order. One self-caught test bug during authoring (the over-broad `<` injection assertion) was fixed before the Task 2 commit; it never reached a commit, so it is noted as a decision rather than a deviation.

## Real Adapter Bugs Found
**None.** Every fixture behaved exactly as the 04-02 contract documents: the accounting identity held on all 8 with zero unaccounted units, every claim was verbatim and content-addressed, charset fallback was faithful (U3, no spurious U4), and the forwarded/attachment/defect paths routed correctly. `email_adapter.py` was NOT modified (it is owned by 04-02 and out of this plan's file scope); no escalation was needed.

## Gate Results (re-run independently — actual output)
- **`pytest tests/test_email_golden.py -q`** → `49 passed in 0.20s`
- **`pytest -q` (full suite)** → `177 passed, 1 xfailed in 5.12s` (baseline 128 passed / 1 xfailed; +49 new golden tests, no regression)
- **`mypy src/newsletters/adapters src/newsletters/distill`** → `Success: no issues found in 11 source files`
- **`lint-imports`** → `Contracts: 1 kept, 0 broken` — `Core (newsletters) must not import any AI/LLM package KEPT` (AI-optional core intact; the corpus + test are stdlib/pytest only)
- **`newsletters build` (`python -m newsletters.cli build --out /tmp/site_p04_03`)** → `rendered 9 surfaces + the library index -> /tmp/site_p04_03` (renderer/dogfood build unbroken)

## Known Stubs
None — the corpus drives the real adapter end-to-end on real `.eml` bytes; no placeholders, mock data, or hardcoded empties. The fixtures are committed test data (not gitignored).

## Threat Flags
None — this plan adds test fixtures + a test file only; it introduces no new network endpoints, auth paths, file-access patterns, or schema changes. The fixtures stand in for untrusted mail and the test is the proof the adapter's untrusted-input handling routes to `unextracted[]` rather than crashing or fabricating (the mitigation for T-04-08 / T-04-09 in the plan's threat register).

## Next Phase Readiness
- **Phase 4 is COMPLETE** (3/3 plans): shared `normalize()` (04-01), the Email adapter (04-02), and now the golden corpus proving zero silent drops (04-03).
- The golden-fixture pattern (byte-exact corpus + accounting-identity + `assert_conforms` + determinism) is the reusable template for the Excel / PPTX / Power BI adapters (Phases 5–7).
- Ready for `/gsd-verify-work`.

## Self-Check: PASSED
- All 9 created files (8 `.eml` fixtures + `_author_fixtures.py`) and `tests/test_email_golden.py` verified present on disk.
- Both commits verified in git log: `f777a3a` (test/fixtures), `84756b8` (test/golden).

---
*Phase: 04-shared-adapter-normalizer-email*
*Completed: 2026-06-17*
