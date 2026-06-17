---
phase: 04-shared-adapter-normalizer-email
plan: 02
subsystem: adapters
tags: [email, eml, mime, charset-ladder, html-strip, unextracted, U1-U8, DistillPort, stdlib]

# Dependency graph
requires:
  - phase: 04-01
    provides: "shared normalize(source, units) — the sole verbatim-locate + content-addressed Trace minting path"
  - phase: 01-distill-socket
    provides: "DistillPort protocol, DistillationResult, Coverage/Unextracted honesty contract, register/resolve/available, assert_conforms"
  - phase: 03-content-addressed-provenance-faithfulness
    provides: "Trace.from_source content-addressing + SpanContainmentFaithfulness gate (inherited via normalize + assert_conforms)"
provides:
  - "EmailAdapter — the first stdlib-only DistillPort backend, registered under name 'email'"
  - "faithful_decode(raw_bytes, declared) — the deterministic charset ladder declared->utf-8->latin-1 (strict)"
  - "strip_html(html) -> (text, lossy) — deterministic stdlib html.parser tag-stripper (always lossy)"
  - "Canonical decoded-text transcript layout (header block + blank line + paragraph body) for .eml Sources"
  - "U1-U8 unextracted[] routing for email — zero silent drops"
affects: [04-03-golden-file-tests, future-adapters-excel-pptx-powerbi]

# Tech tracking
tech-stack:
  added: []  # stdlib only (email, email.policy, html.parser) — no new dependency (CONTEXT decision 5)
  patterns:
    - "Adapter does format-specific extraction + decision-making; normalize() owns faithfulness (one trust rule, one place)"
    - "Charset faithfulness: never trust get_content() (silent U+FFFD); re-decode with a strict ladder and route fallbacks to unextracted[]"
    - "Emit-both for HTML-only: best-effort paragraph claims AND a U5 lossy disclosure (CONTEXT decision 6)"
    - "Parse records per-source adapter unextracted[] so contract-exact distill(sources) recovers format-specific drops (mirrors manual.py constructor-injection)"

key-files:
  created:
    - src/newsletters/adapters/email_adapter.py
    - src/newsletters/adapters/_html_text.py
    - tests/test_email_adapter.py
  modified:
    - src/newsletters/adapters/__init__.py

key-decisions:
  - "distill(sources) stays signature-exact with DistillPort; parse(raw, path) is the bytes-first entrypoint that builds the Source and records the adapter's U1-U7 drops, recovered in distill via a per-source-id dict (manual.py-style state carry)"
  - "ONE whitespace rule for transcript+units: each body paragraph is the strip()-ed run of non-blank lines; the transcript body is rebuilt as '\\n\\n'.join(paragraphs) so every unit is by construction an exact substring (normalize locates all)"
  - "HTML emit-both: stripped paragraphs become real claims (verbatim in the stripped-text transcript) AND a U5 entry discloses the lossy strip (resolves RESEARCH open-Q via CONTEXT decision 6)"
  - "Source.timestamp from msg['Date'].datetime when present (not now()); Source.id == Source.context == raw file path (CONTEXT decision 2)"

requirements-completed: [ADAPT-02]

# Metrics
duration: 6min
completed: 2026-06-17
---

# Phase 04 Plan 02: Email `.eml` Adapter Summary

**The first stdlib-only `DistillPort` backend: one `.eml` → one `Source` with a canonical DECODED transcript (header block + paragraph body); verbatim header + paragraph units flow through the shared `normalize()` for content-addressed `Claim(+Trace)`, while a deterministic charset ladder + U+FFFD detection + HTML-only emit-both route U1–U8 to `Coverage.unextracted[]` with zero silent drops — registered under `"email"`, conforming to the socket.**

## Performance
- **Duration:** ~6 min
- **Started:** 2026-06-17T14:34Z
- **Completed:** 2026-06-17T14:41Z
- **Tasks:** 3 (Task 1 + Task 2 implemented together as one cohesive feature; Task 3 = the upfront TDD test file + gate re-run)
- **Files:** 3 created, 1 modified

## Accomplishments
- `EmailAdapter` parses `.eml` bytes via `email.message_from_bytes(raw, policy=email.policy.default)` (modern `EmailMessage` API), builds the canonical decoded transcript, and returns a `DistillationResult(backend="email")` through the `DistillPort` socket — never publishing (HARD RULE, mirrors `manual.py:13-17`).
- `faithful_decode` implements the fixed `declared → utf-8 → latin-1` strict ladder, catching **both** `UnicodeDecodeError` and `LookupError` (RESEARCH Pitfall 2); latin-1 strict is total so the ladder always terminates.
- `strip_html` is a deterministic stdlib `html.parser` tag-stripper (`convert_charrefs=True`, block-tag newline injection, `script`/`style`/`head` skipped) — always lossy by construction; `<script>` content never reaches a claim (injection mitigation T-04-06).
- All of U1–U8 route to `unextracted[]` with descriptive reasons; the accounting identity (claims + unextracted == units/parts/defects walked) holds; `coverage.complete` is False whenever anything was dropped.
- Registered under `"email"` on package import; `assert_conforms(EmailAdapter(), [source])` passes (span-containment + lossless JSON round-trip).
- 29 new adapter tests, all green; full suite 128 passed / 1 xfailed (was 99/1; +29, no regression).

## The public API (contract for the 04-03 golden-corpus executor)

**Registered name:** `"email"` — `from newsletters.adapters import EmailAdapter` (importing the package auto-registers it; `newsletters.distill.resolve("email")` returns the instance).

**Entrypoints:**
```python
class EmailAdapter:
    name = "email"
    def parse(self, raw: bytes, path: str) -> tuple[Source, list[str], list[Unextracted]]: ...
    def distill(self, sources: list[Source]) -> DistillationResult: ...   # DistillPort-exact
```
- `parse(raw, path)` is the **bytes-first** entrypoint: it builds the `Source` (transcript, timestamp, context), returns the transcript-order units it will hand to `normalize()`, and the adapter's own U1–U7 `unextracted[]`. It **records** those drops keyed by `source.id`.
- `distill(sources)` is signature-exact with `DistillPort`. For each `Source` it re-derives the units from the transcript (same whitespace rule), calls `normalize(source, units)`, and **merges** the recorded adapter U1–U7 drops + `normalize`'s U8 drops into the final `Coverage`.
- **Golden-corpus usage:** `adapter = EmailAdapter(); src, _, _ = adapter.parse(eml_bytes, path); result = adapter.distill([src])`.

**Transcript layout produced** (CONTEXT decision 2; the offset-stable contract):
```
From: <decoded value>
To: <decoded value>
Subject: <decoded value>
Date: <decoded value>

<paragraph 1>

<paragraph 2>
```
- Fixed header order From/To/Subject/Date; a **missing header emits no line** (no offset-shifting blank line). Header *value* (text after `": "`) is the verbatim span a header claim locates.
- Exactly one `"\n\n"` separates the header block from the body (omitted if either side is empty).
- Body line endings normalized to `\n` **once** before assembly (Pitfall 4). Body = `"\n\n".join(paragraphs)` where each paragraph is the `strip()`-ed run of non-blank lines — so every unit is by construction an exact substring.

**`Source` fields:** `id = context = path` (the raw file path, CONTEXT decision 2); `timestamp = msg['Date'].datetime` when present, else the model default `_utcnow()`.

**Units handed to `normalize()`, in transcript order:** the 4 (or fewer) present header values, then the body paragraphs. Header values first, paragraphs after — the cursor advances monotonically.

## U1–U8 mapping as implemented (the reason strings 04-03 pins)

| # | Condition | Detection | Reason string (exact) |
|---|-----------|-----------|------------------------|
| U1 | Forwarded / nested mail | `iter_attachments()` part with `get_content_maintype() == "message"` (detected even when `is_attachment()` is False) | `"forwarded message/rfc822 — nested mail not extracted (scope)"` |
| U2 | Non-text attachment | `iter_attachments()` part with `get_content_maintype() not in {"text","message"}` | `"non-text attachment ({ctype}, filename={name}) — not extracted"` |
| U3 | Charset fallback | `faithful_decode` returned `fell_back=True` (declared charset failed/absent-match) | `"charset fallback: declared {declared} failed, decoded as {enc} — interpretation may be unfaithful"` |
| U4 | Residual U+FFFD | `'�' in decoded_text` after decode | `"undecodable bytes replaced with U+FFFD — text not faithful"` |
| U5 | HTML-only lossy strip (emit-both) | body is `text/html` (no plain alternative); `strip_html` returns `lossy=True` (always) | `"html-only body — deterministic tag-strip is lossy (structure/links dropped)"` |
| U6 | No readable body | `get_body(preferencelist=("plain","html")) is None` (or its payload is not bytes) | `"no text/plain or text/html body part found"` |
| U7 | Malformed MIME | any part in `msg.walk()` has non-empty `.defects` | `"MIME defect(s): {defects}"` (comma-joined defect class names, e.g. `CloseBoundaryNotFoundDefect`) |
| U8 | Non-locatable unit | delegated to `normalize()` (`transcript.find(unit, cursor) == -1`) | `"unit not verbatim-locatable in transcript (faithful, not suggestive)"` |

**Zero-silent-drop identity:** `len(claims) + len(coverage.unextracted) == (header units + body paragraphs + non-body parts + defect-bearing parts)`. `Coverage.complete = (merged_unextracted == [])` — the `Coverage` validator makes "complete with drops" unrepresentable.

## Files Created/Modified
- `src/newsletters/adapters/email_adapter.py` (created, 365 lines) — `faithful_decode`, `_segment_paragraphs`, `EmailAdapter.parse/distill` + the MIME walk (`_decode_body`, `_walk_attachments`, `_collect_defects`). The ONLY module importing `email`; computes no hash.
- `src/newsletters/adapters/_html_text.py` (created, 77 lines) — `strip_html`, the deterministic `html.parser` stripper.
- `src/newsletters/adapters/__init__.py` (modified) — imports `register` + `EmailAdapter`, registers under `"email"` on import, exports `EmailAdapter`.
- `tests/test_email_adapter.py` (created, 415 lines) — 29 tests: charset ladder, `strip_html` determinism/skip, transcript layout, RFC2047 decode, verbatim paragraphs, happy path, U1–U7 + inline-rfc822 gotcha, U4 residual U+FFFD, accounting identity, faithful content-addressed spans, timestamp/context, registry + `assert_conforms`, determinism, FreeLocator content anchor.

## Decisions Made
- **`distill(sources)` signature-exact + bytes-first `parse(raw, path)`.** The `DistillPort` contract gives `distill` only `Source` objects, but the adapter's U1–U7 drops come from the raw MIME walk (lost once you have just the decoded transcript). Resolution mirrors `manual.py` constructor-injecting its `WorkSession`: `parse` records each source's adapter-unextracted keyed by `source.id`; `distill` recovers them. A `Source` not produced by this adapter simply has no recorded drops — its header/paragraph claims are still minted faithfully.
- **One whitespace rule.** Each paragraph = `strip()`-ed run of non-blank lines; the transcript body is `"\n\n".join(paragraphs)`. This guarantees every unit is an exact substring (no strip-then-store mismatch → no faithful paragraph wrongly routed to `unextracted[]`).
- **HTML emit-both (CONTEXT decision 6).** Stripped paragraphs become real claims (verbatim in the stripped-text transcript, so they pass the gate) AND a U5 entry discloses the lossy strip — partial value preserved, information-loss never silent.
- **Body via `get_payload(decode=True)` then `faithful_decode`, NOT `get_content()`** — `get_content()` silently injects U+FFFD (RESEARCH Pitfall 1); decoding the raw bytes ourselves with the strict ladder is the only faithful path.

## Deviations from Plan
None — plan executed as written. Task 1 and Task 2 were implemented together because `faithful_decode`, the transcript build, and `distill()` live in one cohesive module (`email_adapter.py`) with interdependent behavior; both `<verify>` gates and the full standing-gate suite passed. Task 3's test file was authored upfront (TDD RED) and made green by the implementation, then the Task 3 gate chain was re-run independently.

## Gate Results (re-run independently — actual output)
- **`pytest tests/test_email_adapter.py -q`** → `29 passed in 0.07s`
- **`pytest tests/test_email_adapter.py tests/test_normalize.py -x -q`** → `43 passed in 0.08s`
- **`pytest -q` (full suite)** → `128 passed, 1 xfailed in 4.69s` (baseline 99 passed / 1 xfailed; +29 new, no regression)
- **`mypy src/newsletters/adapters src/newsletters/distill`** → `Success: no issues found in 11 source files`
- **`lint-imports`** → `Contracts: 1 kept, 0 broken` — `Core (newsletters) must not import any AI/LLM package KEPT` (the adapter is stdlib/AI-free)
- **`newsletters build`** → `rendered 9 surfaces + the library index -> /tmp/site_p04_02` (renderer/dogfood build unbroken)
- **No hand-minted hashes:** `hashlib|sha256|content_hash =` in non-comment lines of `email_adapter.py` → `0` (all minting flows through `normalize()` → `Trace.from_source`)
- **`email` import isolation:** only `src/newsletters/adapters/email_adapter.py` imports `email`

## TDD Gate Compliance
- RED gate present: `e602151` (`test(04-02): …`) — failed at collection (`ModuleNotFoundError: No module named 'newsletters.adapters._html_text'`) before implementation.
- GREEN gate present: `914b791` (`feat(04-02): …`) — the 29 failing tests passed after implementation.
- No REFACTOR commit (implementation was clean as written).

## Known Stubs
None — the adapter is fully wired: real `.eml` parse, real charset decode, real claims via `normalize()`, real U1–U8 routing. No placeholders, no hardcoded empties flowing to a UI.

## Issues Encountered
- The pre-existing `mypy` finding in `capture.py` (noted in 04-01) is OUT OF SCOPE (not in `adapters`/`distill`); the plan-specified mypy scope is clean.

## Next Phase Readiness (for 04-03 golden corpus)
- **Registered name:** `"email"`. **Entrypoint:** `EmailAdapter().parse(raw_bytes, path)` then `.distill([source])`.
- **Transcript layout, U1–U8 reason strings, and `Source.timestamp`/`context` semantics are pinned above** — the golden `*.expected.json` fixtures should match these exactly.
- Standing invariants all green; ready for the wave-3 golden corpus and `/gsd-verify-work`.

## Self-Check: PASSED
- Created files verified on disk: `adapters/email_adapter.py`, `adapters/_html_text.py`, `tests/test_email_adapter.py`, `04-02-SUMMARY.md`.
- Modified file verified: `adapters/__init__.py` (registers `EmailAdapter`).
- Commits verified in git log: `e602151` (test/RED), `914b791` (feat/GREEN).

---
*Phase: 04-shared-adapter-normalizer-email*
*Completed: 2026-06-17*
