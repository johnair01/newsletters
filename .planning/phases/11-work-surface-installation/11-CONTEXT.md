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
