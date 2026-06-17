# Phase 4 — Context & Decisions (Shared Adapter Normalizer & Email Adapter)

**Goal:** Put the faithful-extraction rule in exactly one place (the shared `normalize()`), and prove
it with the first, simplest adapter — Email, stdlib-only, no extra.

**Requirements:** ADAPT-01 (shared normalize), ADAPT-02 (Email .eml adapter), ADAPT-06 (golden-file tests).
**Depends on:** Phase 1 (DistillPort/registry/coverage seam), Phase 3 (`Trace.from_source` content-addressing + faithfulness gate).

## Decisions (reviewer 2026-06-17 — smart-discuss; defaults accepted under the uninterrupted directive)

1. **Architecture — shared normalize() at the socket (ADAPT-01).** New `src/newsletters/adapters/`
   package. Each adapter is a registered `DistillPort` backend that (a) does format-specific raw
   extraction into intermediate "raw units," then (b) calls ONE shared `normalize()` that mints typed
   `Claim(+Trace)`. **The faithful-extraction rule lives only in `normalize()`:** every Claim's text
   must be a verbatim, content-addressed span of its Source (via `Trace.from_source`); anything not
   verbatim-locatable is routed to `unextracted[]`, never fabricated. Adapters never hand-mint hashes.

2. **Email → Source model (decoded-text transcript).** One `.eml` → one `Source`. `Source.transcript`
   is a **canonical DECODED text** rendering (a headers block + the decoded body) so spans are verbatim
   and content-addressable; Trace offsets index into that transcript. The raw file path/identifier
   lives in `Source.context`. (Not the raw RFC822 bytes — that leaks encodings and yields ugly offsets.)

3. **Granularity — headers + paragraphs.** Key headers (From / To / Subject / Date) each become a
   Claim with a Trace into the transcript's header block; the decoded body is segmented into paragraphs,
   each its own Claim(+Trace). Auditable atoms, real per-claim provenance.

4. **`unextracted[]` — broad, no silent drops (success criterion).** Route to `unextracted[]`:
   forwarded/nested `message/rfc822`, non-text attachments, charset/decoding fallbacks, HTML-only
   bodies where deterministic tag-stripping is lossy, and anything `normalize()` cannot verbatim-locate.
   The golden-file test asserts **zero silent drops** (every input part is either a Claim or an
   `unextracted[]` entry).

5. **Scope / stdlib.** Python stdlib only — `email` (RFC822/MIME parsing), `email.policy.default`,
   `html.parser` for deterministic HTML→text. **No new dependency**, no Package-Legitimacy gate. Keep
   the AI-optional contract (`lint-imports`) and bare-install gate green. `.msg` (GPL `extract-msg`) is
   explicitly OUT (REQUIREMENTS Out-of-Scope).

## Hard rules in play
- **Faithful, not suggestive** — `normalize()` only extracts verbatim spans; it never paraphrases or
  editorializes. Non-verbatim → `unextracted[]`.
- **Every published claim traces to evidence** — adapters produce content-addressed Traces; the
  Phase-3 faithfulness gate then holds them strictly (adapter claims ARE content-addressed).
- **AI-optional core** — stdlib-only adapter; no AI import reachable; contract + bare-install stay green.
- **No silent drops** — the coverage manifest / `unextracted[]` contract from Phase 1 is the mechanism.

## Research note
Per the operating directive, dispatch a researcher for best-known methods BEFORE planning:
Python `email` stdlib best practices (EmailMessage + `policy.default`, `get_body()`, `iter_attachments`,
`get_content()` charset handling), robust charset fallback, deterministic HTML→text via `html.parser`
(avoid non-deterministic third-party), MIME multipart/alternative vs mixed handling, and golden-file
test patterns for parsers. Record findings + citations in 04-RESEARCH.md.
