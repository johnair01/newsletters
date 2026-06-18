# Phase 11 — Context & Decisions (Work-Surface Installation)

**Goal:** Prove the whole pipeline on a real work codebase — install Newsletters, point read-only
adapters at the code (data stays LOCAL, no external calls on content), author a Report by hand, and
publish a Library that shows HOW the work was done (Provenance/Lineage on each surface).

**Requirements:** WORK-01 (pip install + read-only adapters at a work codebase, data local), WORK-02
(author a Report by hand via the manual backend, inheriting traced structure), WORK-03 (published
Library shows process via Provenance/Lineage on each surface).
**Depends on:** Phase 1 (manual authoring / `capture.py`), Phases 4–7 (adapters, all local-file +
stdlib), Phases 8–10 (Site model, renderer, provenance surfacing + honesty panel + fan-out lineage).

## Current state (verified)
- `capture.py` (`WorkSession`/`Decision`/`capture_session`/`build_report`) is the hand-authoring path.
- NO filesystem/code/text adapter exists (adapters are email/excel/pptx/powerbi — none ingest source
  code/markdown). So WORK-01 "read-only adapters at a work codebase" needs a small read-only local-file
  source ingest (code/text → `Source`), OR a documented reuse.
- Provenance/lineage is LARGELY BUILT: claim→source links (Phase 9), the Phase-10 honesty panel +
  claim-beside-verbatim-trace, the fan-out block/`FanoutLink` (lineage). WORK-03 mostly = surface/
  assemble these into a "how the work was done" view, not build from scratch.
- **External-call flag:** `render.py:104` loads Google Fonts via `@import url('https://fonts.googleapis.
  com/...')` on every page — an external call baked into the output. CLAUDE.md: "no external calls
  baked in"; WORK-01: "data staying local." This must be resolved for a true offline/self-hosted/
  no-external-call guarantee (self-host the 3 fonts OR a system-font fallback with the web fonts as
  progressive enhancement). Research to recommend.

## Interpretation / decisions (autonomous — the "work-surface interview" never happened)
1. **Dogfood on THIS repo as the "real work codebase."** The Newsletters build is itself the work, and
   it's richly recorded (`.planning/`, `WHERE-WE-ARE.md`, `RETRO.md`, the source tree). So: point a
   read-only local-file ingest at this repo's files, author a Report BY HAND about how the work was
   done (the build), and publish it with provenance (claims→the actual repo files) + lineage (fan-out).
   This is the honest, achievable demonstration without external interview content.
2. **WORK-01 — a read-only, local, no-network file source ingest.** Add a minimal `capture_files(paths)`
   / lightweight filesystem source reader (stdlib, read-only: `Path.read_text`, no writes to the target,
   no network) that turns selected local code/text files into `Source`s (content-addressable, so claims
   can trace to them). Plus a GUARANTEE/test that the pipeline makes ZERO external calls on content
   (and resolve the Google-Fonts external `@import` so the rendered site is genuinely self-contained).
3. **WORK-02 — author a Report by hand via the manual backend / `capture.py`.** A hand-authored Report
   about the build, whose claims trace (content-addressed) to the real repo files ingested in WORK-01 —
   inheriting the traced structure (the manual backend / build_report path, zero AI).
4. **WORK-03 — Provenance/Lineage visible on each surface.** Surface "how the work was done": each
   claim → its source file (provenance, Phase 9/10), and the fan-out/lineage (this Report → its
   surfaces). If a dedicated "Provenance / Lineage" view/section beyond what Phase 9/10 already render
   is needed, add it; otherwise wire/assemble the existing devices. The Phase-10 forward note (wire an
   on-disk/work corpus into `newsletters check`) is in scope here.
5. **Scope guard:** keep it a demonstration + the minimal new capability (local-file ingest +
   no-external-call guarantee + the hand-authored Report + provenance/lineage surfacing). Do NOT build
   the AI backend (v2) or a full code-analysis adapter. Read-only on the target (never writes to the
   work codebase). AI-optional + all prior contracts stay green.

## Research-locked choices (11-RESEARCH.md accepted 2026-06-18, HIGH confidence)

- **L1 — WORK-02 (hand-authored work Report):** reuse `capture.build_report` (capture.py:81) + the
  `dogfood._address_report` content-addressing pattern (locate each claim verbatim in its file, pin via
  `Trace.from_source`). New module `src/newsletters/worksurface.py` (NOT dogfood.py — that's the sample
  corpus). New corpus at `content/work/` with its own append-only ledger. Claims that paraphrase (don't
  content-address) route to `missing[]` (honesty panel shows them) — NEVER fabricate an offset.
- **L2 — WORK-01 (read-only local ingest):** `capture_files(paths) -> list[Source]` — stdlib,
  `Source(id=posix_relpath, transcript=Path(p).read_text())`, `sorted()` + `EPOCH_ZERO` timestamp
  (reuse `adapters/_timestamps.py`) for determinism. Read-only BY CONSTRUCTION (no write to target, no
  network). The relpath `id` is already recognized by `_is_file_path_locator` (render.py:62) → claims
  link to working repo files for free. Ingest a CURATED file list (the files the claims cite), not a
  broad glob (no orphan sources).
- **L3 — Font fix (the no-external-call correctness fix):** REMOVE the external Google-Fonts `@import`
  (render.py:104) — that kills the baked-in external call regardless of what replaces it. Preferred
  replacement: VENDOR the three OFL woff2 (DM Serif Display, DM Mono, Instrument Sans — all SIL OFL,
  well-established) under e.g. `content/rev1/site/fonts/` + `@font-face`, INCLUDING the `OFL.txt`
  license file. If the in-env fetch of the woff2 is unavailable/blocked, FALL BACK to a system-font
  stack with the DM families named first (graceful degradation) + a documented "vendor the OFL woff2 in
  production" note + the `@font-face` scaffold ready. EITHER path → zero external calls. No reviewer
  checkpoint: OFL for these three is established public fact and the license file travels with the
  fonts; if vendoring, the executor confirms `OFL.txt` is present. `design-system.md:65` already
  mandates self-hosting in production.
- **L4 — WORK-03 (provenance/lineage):** REUSE the Phase 9/10 devices (claim→file links via
  `link_for_source`, `_claim_spans` verbatim trace, `_honesty_panel`, the fan-out chain + masthead
  `captured via`/`derived from`). The ONE minimal addition: populate `Surface.lineage`
  (`derived_from` = ingested file ids, `produced` = fan-out ids) so the EXISTING masthead line becomes
  a real provenance/lineage summary — no new renderer code (verify `Surface.lineage` exists or add the
  field minimally).
- **L5 — `check`/`build` corpus selector:** add `--corpus {rev1|work}` to the CLI; `review_blockers`
  is already corpus-agnostic (review.py:58). The work corpus runs through the SAME merge-block gate.
- **L6 — Tests:** (a) NO-EXTERNAL-CALL — generated HTML contains no auto-loading resource URL
  (`fonts.googleapis.com`, `@import url('http`, `src="http`, `<link ... href="http`) — scoped to
  AUTO-LOADED resources, NOT clickable `repo_url`/source links (A2); (b) read-only ingest produces
  content-addressed Sources + writes nothing to the target; (c) WORK-02 the hand-authored Report
  inherits the traced structure (claims content-address to the ingested files; un-locatable → missing[]);
  (d) WORK-03 provenance + lineage are visible on the work surface.
- **A2 lock:** the no-external-call assertion targets auto-fetched resources only; `repo_url` and
  `link_for_source` anchors are navigation (correct) and stay absolute.

## Hard rules in play
- **Open by default / self-hostable / NO external calls baked in** — WORK-01's "data stays local" makes
  this literal; resolve the font `@import`. No analytics, no phone-home, no calls on content.
- **Read-only on the work codebase** — the adapters/ingest only READ; never mutate the target repo.
- **Every published claim traces to evidence** — the hand-authored Report's claims trace to the real
  repo files (content-addressed); provenance visible (Phase 10).
- **No auto-publish / faithful-not-suggestive / AI-optional** — all intact; manual backend is zero-AI.
- **Determinism** — the demo Report + site regenerate deterministically (SITE-06).

## Research note (dispatch BEFORE planning)
Validate against the LIVE codebase: how `capture.py`/`build_report` author a Report by hand + emit a
Surface (the WORK-02 path); the cleanest minimal read-only local-file → `Source` ingest (stdlib,
content-addressed via `Trace.from_source`, no network, read-only) for WORK-01; whether Phase 9/10
provenance+fan-out already satisfy WORK-03 or a dedicated Provenance/Lineage view is needed; the
Google-Fonts external-`@import` fix (self-host vs system-font fallback) to honor "no external calls";
how to wire the on-disk/work corpus into `newsletters check` (Phase-10 forward note); and a test
proving ZERO external calls on content. Confirm zero NEW runtime dependency. Record in 11-RESEARCH.md.
