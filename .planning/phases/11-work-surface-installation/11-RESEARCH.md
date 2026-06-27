# Phase 11: Work-Surface Installation - Research

**Researched:** 2026-06-18
**Domain:** Dogfood install of the trust pipeline on a real codebase — read-only local-file ingest, hand-authored Report, no-external-call guarantee, provenance/lineage surfacing
**Confidence:** HIGH (all findings grounded in the live codebase; zero new runtime dependency confirmed)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. **Dogfood on THIS repo as the "real work codebase."** Point a read-only local-file ingest at this repo's files, author a Report BY HAND about how the work was done (the build), publish it with provenance (claims→actual repo files) + lineage (fan-out).
2. **WORK-01 — a read-only, local, no-network file source ingest.** Add a minimal `capture_files(paths)` / lightweight filesystem source reader (stdlib, read-only: `Path.read_text`, no writes to the target, no network) turning selected local code/text files into `Source`s (content-addressable). Plus a GUARANTEE/test of ZERO external calls on content (and resolve the Google-Fonts external `@import`).
3. **WORK-02 — author a Report by hand via the manual backend / `capture.py`.** A hand-authored Report about the build whose claims trace (content-addressed) to the real repo files ingested in WORK-01 — inheriting the traced structure (manual backend / `build_report`, zero AI).
4. **WORK-03 — Provenance/Lineage visible on each surface.** Surface "how the work was done": each claim → its source file (Phase 9/10), and the fan-out/lineage. Add a dedicated view ONLY if Phase 9/10 devices are insufficient; otherwise wire/assemble existing devices. The Phase-10 forward note (wire an on-disk/work corpus into `newsletters check`) is in scope here.
5. **Scope guard:** demonstration + minimal new capability only. Do NOT build the AI backend (v2) or a full code-analysis adapter. Read-only on the target (never writes). AI-optional + all prior contracts stay green.

### Claude's Discretion
- Exact module placement for the new ingest (new `worksurface.py` vs extend `dogfood.py` vs `adapters/`).
- Which file globs to ingest for the dogfood corpus.
- Font no-external-call fix: self-host woff2 vs system-font fallback vs drop-`@import` (research recommends ONE).
- Whether WORK-03 reuses Phase 9/10 devices or adds a thin lineage summary.
- CLI shape for wiring the work corpus into `check`/`build`.

### Deferred Ideas (OUT OF SCOPE)
- The AI backend (v2: AI-01/02).
- A full code-analysis / AST adapter.
- External interview content / non-dogfood corpora.
- Any write-back to the target codebase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WORK-01 | `pip install` Newsletters and point read-only adapters at a work codebase, data staying local (no external calls on content) | Q-B (read-only `capture_files` ingest, stdlib `Path.read_text`, content-addressed via `Trace.from_source`) + Q-C (resolve `render.py:104` Google-Fonts `@import`; test asserts zero external URLs) |
| WORK-02 | Author a Report by hand (manual backend) inheriting the traced structure | Q-A (`build_report`/`capture_session` path + the `_address_report` content-addressing pattern, mirrored for the work corpus) |
| WORK-03 | Published Library shows how the work was done via Provenance/Lineage on each surface | Q-D (Phase 9/10 already render claim→source links, honesty panel, claim-beside-trace, fan-out + provenance masthead bits — recommend REUSE + one thin lineage summary) + Q-E (`check`/`build` corpus wiring) |
</phase_requirements>

## Summary

Phase 11 is a **demonstration phase with one genuinely new capability** (a read-only local-file `Source` ingest) plus **one correctness fix** (kill the baked-in Google-Fonts external call). Everything else — the hand-authored Report path, content-addressing claims to real files, provenance surfacing, fan-out lineage, the honesty panel, the merge-block `check` gate — **already exists and works** in the live codebase from Phases 1, 3, 9, and 10. The job is to *assemble* those proven pieces over a corpus built from this repo's own files, and to close the one open hole (the font `@import`) that violates "no external calls baked in."

The WORK-02 path is fully built: `capture.build_report(session, …)` (capture.py:81-113) lifts a `WorkSession` (hand-authored `Decision[]` + `Source[]`) into a Draft Report `Surface` with a traced `ClaimsBlock` + `Provenance`. The `dogfood._sources_and_reports()` / `_address_report()` (dogfood.py:191-209) pattern then content-addresses each claim's trace to its source transcript via the canonical `Trace.from_source`. WORK-01 needs only a small stdlib reader that turns selected repo files into `Source(id=path, transcript=Path(path).read_text())` so the hand-authored claims can trace (content-addressed) to *real file content* instead of a synthesized session transcript. WORK-03 is satisfied by the existing renderer: `link_for_source` (render.py:70-97) already turns a file-path locator into a working repo link, `_honesty_panel` (render.py:716-750) shows gaps on every surface, `_claim_spans` (render.py:465-476) shows the verbatim trace beside each claim, the masthead emits provenance + `derived_from` lineage (render.py:775-778), and `_fanout_row` (render.py:432-442) renders the fan-out chain — recommend reusing these plus adding **one thin per-surface "Provenance / Lineage" summary block** so the "how the work was done" story is explicit rather than scattered.

**Primary recommendation:** Add `src/newsletters/worksurface.py` with a read-only stdlib `capture_files(paths) -> list[Source]` and a hand-authored `build_work_report(...)` that mirrors the `dogfood` content-addressing pattern; fix `render.py:104` by **self-hosting the three woff2 fonts with a `@font-face` block + a system-font fallback stack** (design-system.md:65 explicitly says "self-host in production"); wire the work corpus into `newsletters build`/`check` via a `--corpus work` selector; reuse Phase 9/10 provenance/lineage devices plus a thin lineage summary. **Zero new runtime dependency** — self-hosted fonts are static binary assets, not a pip dep.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Read local repo files → `Source[]` | Core (package API) | — | Pure stdlib `Path.read_text`; belongs beside `capture.py` in `src/newsletters/`, read-only, no I/O beyond reads |
| Content-address claims to file content | Core (`Trace.from_source`) | — | The single canonical pinning path (semantic.py:126-170); never re-implemented |
| Hand-author the work Report | Core (`capture.build_report`) | — | Manual backend / zero-AI authoring path already exists (capture.py:81) |
| Render provenance + lineage | Render (static HTML) | — | All devices live in render.py (Phases 9/10); no client tier, no JS |
| No-external-call guarantee (fonts) | Render / Static assets | — | Self-hosted woff2 are static files emitted beside the HTML; CSS `@font-face` references them relatively |
| Merge-block gate over the work corpus | `review.py` + CLI | CI | `review_blockers` is corpus-agnostic; only the corpus selection changes (cli.py:40) |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib `pathlib` | 3.12 (runtime) | `Path.read_text()` read-only file ingest | Already the project's I/O idiom (dogfood.py:14, site.py); zero dep, read-only by construction |
| `pydantic` | >=2 (already a core dep) | `Source`/`Claim`/`Trace`/`Surface` models | The spine is already Pydantic; the ingest only constructs existing models |
| `typer[all]` | already a core dep | `newsletters build`/`check` corpus selector | CLI is already Typer (cli.py) |

**No new package is added. [VERIFIED: pyproject.toml:17-21 — core deps are pydantic>=2, typer[all], sqlmodel; nothing else needed for a stdlib file reader]**

### Supporting (static assets, NOT pip deps)
| Asset | Purpose | When to Use |
|-------|---------|-------------|
| DM Serif Display / Instrument Sans / DM Mono `.woff2` | Self-hosted fonts (offline visual fidelity) | Emitted into `content/.../site/fonts/` and referenced via `@font-face`; replaces the external `@import` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Self-host woff2 | System-font fallback only (drop `@import`, rely on `--font-*` fallbacks already in the CSS) | Zero repo weight + zero external call, but loses the DM Serif/Mono/Instrument identity — violates "visual fidelity is not optional" (CLAUDE.md) on machines without the fonts installed |
| Self-host woff2 | Keep `@import` as optional progressive enhancement | Still bakes an external URL into every page → fails the "no external calls" test; rejected |
| `capture_files` (new module) | Extend `dogfood.py` | `dogfood.py` is the Rev1 *sample* corpus; mixing the work ingest into it muddies the "sample vs real" boundary the file documents (dogfood.py:9) |
| `capture_files` in `src/newsletters/` | An `adapters/` adapter | The adapter framework (normalize.py) is for *modality* extraction (email/excel/pptx) and routes through `DistillPort`; a plain file reader is simpler and the corpus here is hand-authored, not auto-distilled. A new top-level module is the honest fit. |

**Installation:** None. `pip install .` already provides everything (PKG-01).

**Version verification:** No package to verify — all stdlib + already-pinned core deps. **[VERIFIED: pyproject.toml:17-21, 62-67]**

## Package Legitimacy Audit

> **Not applicable — Phase 11 installs ZERO new packages.**

| Package | Registry | Verdict | Disposition |
|---------|----------|---------|-------------|
| (none) | — | — | No external package added; stdlib `pathlib` + existing core deps only |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

Self-hosted fonts are static binary assets committed to the repo, not registry packages. They carry their own licenses (DM Serif Display / DM Mono / Instrument Sans are all SIL Open Font License — compatible with the MIT/open-by-default posture). **[CITED: Google Fonts metadata — all three families ship under OFL; verify the downloaded woff2 licenses are committed alongside the assets]**

## Architecture Patterns

### System Architecture Diagram

```
  [ this repo's files ]                          (WORK-01 — read-only, stdlib, no network)
   src/**.py  docs/**.md                                  |
   .planning/**.md  CLAUDE.md  RETRO.md                    v
   WHERE-WE-ARE.md                          capture_files(paths)
                                                  |  Path.read_text()  (READ ONLY)
                                                  v
                                       Source(id=relpath, transcript=text)
                                                  |  content_hash() pins each
                                                  v
  [ operator hand-authors ]   ----------> Decision[] / claims about "how the work was done"
   (WORK-02, zero AI)                              |  build_work_report(...)
                                                  v   capture.build_report  ->  Surface (Draft Report)
                                       claim.evidence[0] = Trace.from_source(file_source, start, end)
                                                  |  span = verbatim file slice (content-addressed)
                                                  v
                                       Surface.publish(reviewer)  (review gate, no auto-publish)
                                                  |
                  +-------------------------------+-------------------------------+
                  v                               v                               v
        render_surface()               review_blockers()               build_site() -> Library
        (WORK-03 provenance)           (Phase-10 gate over             index + library.html
         - claim -> repo file link       the WORK corpus)
         - verbatim span beside claim          |
         - honesty panel (gaps)                v
         - provenance + lineage         exit 0 / nonzero  (newsletters check --corpus work)
           masthead + fan-out
                  |
                  v
        content/work/site/*.html  +  self-hosted fonts/  (NO external URL anywhere)
```

### Recommended Project Structure
```
src/newsletters/
├── worksurface.py        # NEW: capture_files(paths) read-only ingest + build_work_report + build_work_site
├── capture.py            # REUSE: build_report / capture_session (WORK-02 author path)
├── render.py             # EDIT: replace line-104 @import with self-hosted @font-face; optional lineage summary
├── review.py             # REUSE: review_blockers (corpus-agnostic)
└── cli.py                # EDIT: build/check accept --corpus {rev1|work}

content/work/             # NEW: the work corpus output
├── ids.json              # append-only ledger (mirror content/rev1/ids.json)
└── site/
    ├── *.html
    └── fonts/            # NEW: 3 self-hosted woff2 (+ their OFL license files)
```

### Pattern 1: Read-only local-file ingest (WORK-01)
**What:** Turn selected repo files into content-addressable `Source` records, never writing the target.
**When to use:** WORK-01 — the corpus's evidence must be the *actual file content* so claims trace to real files.
**Example:**
```python
# Source: pattern grounded in semantic.py:49-83 (Source/content_hash) + dogfood.py:14 (pathlib idiom)
from pathlib import Path
from .semantic import Source

def capture_files(paths: list[str], *, root: Path | None = None) -> list[Source]:
    """Read-only: build one content-addressed Source per file. NEVER writes the target."""
    root = root or Path.cwd()
    sources: list[Source] = []
    for p in sorted(paths):                      # sorted => deterministic order (SITE-06)
        fp = (root / p)
        rel = fp.relative_to(root).as_posix()    # POSIX relpath => stable id + a file-path locator
        sources.append(Source(
            id=rel,                              # e.g. "src/newsletters/semantic.py"
            context=f"work-codebase:{rel}",
            transcript=fp.read_text(encoding="utf-8"),   # READ ONLY — no open('w'), no network
        ))
    return sources
```
- The `id` is the POSIX relative path, which is exactly what `_is_file_path_locator` (render.py:62-67) recognizes, so `link_for_source` resolves it to a working repo link **for free** (render.py:88-90).
- Claims trace via the canonical `Trace.from_source(file_source, start, end)` (semantic.py:126-170) — the SOLE pinning path; never hand-mint a hash.

### Pattern 2: Hand-authored work Report inheriting traced structure (WORK-02)
**What:** Author claims about "how the work was done," each tracing (content-addressed) to a real file span.
**When to use:** WORK-02.
**Example:**
```python
# Source: capture.py:81-113 (build_report) + dogfood.py:191-209 (_address_report content-addressing)
from .capture import Decision, WorkSession, build_report
from .semantic import ClaimsBlock, Trace

def build_work_report(sources, *, surface_id, title, author, narrative) -> Surface:
    # Author Decisions whose source_id is a real file id, and whose text is a VERBATIM slice
    # of that file (so it content-addresses), OR set the trace span explicitly and pin it.
    decisions = [
        Decision(text="...verbatim line from CLAUDE.md...", source_id="CLAUDE.md",
                 topics=["process"]),
        # ...
    ]
    session = WorkSession(id="work-build", title="How this build was done",
                          tool="Claude Code", sources=sources, decisions=decisions)
    report = build_report(session, surface_id=surface_id, title=title,
                          eyebrow="Report · how the work was done", author=author,
                          narrative=narrative)
    # Content-address each claim trace to its file span (mirror dogfood._address_report):
    lookup = {s.id: s for s in sources}
    for block in report.blocks:
        if isinstance(block, ClaimsBlock):
            for claim in block.claims:
                for tr in claim.evidence:
                    src = lookup[tr.source_id]
                    start = src.transcript.find(claim.text)   # verbatim locate
                    if start >= 0:
                        pinned = Trace.from_source(src, start, start + len(claim.text))
                        tr.content_hash, tr.start, tr.end, tr.span = (
                            pinned.content_hash, pinned.start, pinned.end, pinned.span)
                    # else: leave un-addressed OR route to missing[] (faithful, never fabricate)
    return report
```
- This is the **same faithful content-addressing** the shipped Rev1 corpus uses (dogfood.py:85-150) — reuse `Trace.from_source`; do not reinvent.
- A claim whose text is not verbatim-locatable in its file goes to `Surface.missing[]` (semantic.py:487) → shown by the honesty panel, never published as fact.

### Pattern 3: Self-hosted fonts via `@font-face` (WORK-01 no-external-call)
**What:** Replace the `@import url('https://fonts.googleapis.com/...')` (render.py:104) with a local `@font-face` block + emit the woff2 beside the HTML.
**When to use:** WORK-01's literal "data stays local / no external calls."
**Example:**
```css
/* Source: replaces render.py:104; fonts emitted to ./fonts/ beside each page */
@font-face{font-family:'DM Serif Display';src:url('fonts/dm-serif-display.woff2') format('woff2');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:'DM Serif Display';src:url('fonts/dm-serif-display-italic.woff2') format('woff2');font-weight:400;font-style:italic;font-display:swap}
@font-face{font-family:'Instrument Sans';src:url('fonts/instrument-sans.woff2') format('woff2');font-weight:400 600;font-style:normal;font-display:swap}
@font-face{font-family:'DM Mono';src:url('fonts/dm-mono.woff2') format('woff2');font-weight:400 500;font-style:normal;font-display:swap}
```
- The existing `--font-*` token fallbacks (render.py:113: `Georgia,serif` / `system-ui` / `'Courier New',monospace`) stay, giving a graceful system-font fallback if a woff2 is missing.
- Relative `fonts/...` URLs keep the output self-contained and host-agnostic (open-by-default, CLAUDE.md).

### Anti-Patterns to Avoid
- **Hand-minting a `content_hash`** in the new ingest. Always go through `Trace.from_source` (semantic.py:126) — the single pinning path; normalize.py:108-111 documents this rule.
- **Writing anything into the target repo during ingest.** `capture_files` must only `read_text`. A test asserts no file in the scanned tree is modified.
- **Keeping the Google-Fonts `@import` as "optional."** Any baked external URL fails the no-external-call test. Remove it entirely.
- **Building a code-analysis/AST adapter.** Out of scope (CONTEXT decision 5) — a plain text reader is the right size.
- **Fabricating a claim whose text isn't in its file.** Route to `missing[]` (semantic.py:487) — faithful, not suggestive.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Content-addressing a trace | Custom SHA/offset logic | `Trace.from_source` (semantic.py:126-170) | Validates offsets before slicing, pins hash + span; the SOLE minting path |
| Verbatim-locating a claim in a source | A new locator | `str.find` + `Trace.from_source` (dogfood.py:105-113 precedent) | Already the faithful pattern; cursor logic in normalize.py:94-115 if duplicates matter |
| Showing claim → source link | New link renderer | `link_for_source` / `_ev_chip` (render.py:70-97) | File-path locators already resolve to repo links |
| Showing the verbatim trace beside a claim | New view | `_claim_spans` (render.py:465-476) | Already renders addressed spans inline, no click |
| Showing what's missing/unverified | New panel | `_honesty_panel` (render.py:716-750) | Renders on EVERY surface from `missing[]` + `extraction.unextracted[]` |
| Merge-block gate over the corpus | New checker | `review_blockers` (review.py:58-121) | Corpus-agnostic; only the corpus selection changes |
| Site assembly + stable ids | New builder | `build_site` / `Site.from_surfaces` / `Ledger` (dogfood.py:651-687, site.py) | Stable refs, byte-stable regen (SITE-06) |
| Provenance/lineage masthead | New section | masthead `meta_bits` (render.py:775-778) | Already emits `captured via <tool>` + `derived from <lineage>` |

**Key insight:** Phase 11 is ~90% assembly of proven Phase-1/3/9/10 machinery over a new corpus. The ONLY genuinely new code is the ~25-line read-only `capture_files` reader and the font-asset swap. Anything bigger is scope creep against CONTEXT decision 5.

## Runtime State Inventory

> Phase 11 adds a NEW corpus + assets; it is not a rename/refactor. The relevant "what persists" check:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | New `content/work/ids.json` append-only ledger (mirrors `content/rev1/ids.json`) | Create + commit; ledger refs are immutable once assigned (site.py `Ledger`) |
| Live service config | None — no external service; the pipeline is fully local (verified: only external URL is the font `@import`, being removed) | None |
| OS-registered state | None | None — verified: no scheduler/daemon registration in the repo |
| Secrets/env vars | None — ingest reads repo files, no creds | None |
| Build artifacts | `content/work/site/` generated HTML + `fonts/*.woff2` static assets | Generated deterministically by `build_work_site`; fonts committed once |

**Nothing found:** No external service, no secret, no OS registration is touched by this phase — verified by grep for `http`/scheduler/daemon patterns; the sole external URL is `render.py:104` (the font `@import`, removed) and `repo_url` (render.py:53, used only to construct outbound source-link hrefs, not a baked fetch).

## Common Pitfalls

### Pitfall 1: Claim text not verbatim in its file → un-addressable trace
**What goes wrong:** A hand-authored claim paraphrases the file, so `str.find(claim.text)` returns -1 and the trace can't content-address.
**Why it happens:** Natural authoring summarizes; files contain code/markdown, not prose claims.
**How to avoid:** Either (a) make the claim's `span` an explicit verbatim slice of the file and pin via offsets, or (b) route the claim to `Surface.missing[]` (semantic.py:487) so it's shown to the reviewer, never published as fact. The dogfood corpus solves this by making the *transcript* literally contain the decision statements (dogfood.py:180-188); the work corpus can't (real files aren't decision lists), so prefer explicit spans or `missing[]`.
**Warning signs:** `MigrationReport.unlocated` non-empty (dogfood.py:81-82 pattern); honesty panel shows `unsubstantiated` entries.

### Pitfall 2: A leftover external URL slips the no-external-call test
**What goes wrong:** Removing the `@import` but an SVG diagram, favicon, or analytics snippet still references an absolute `http(s)://` URL on the page.
**Why it happens:** `repo_url` (render.py:53) builds source-link hrefs that are legitimately outbound; the test must distinguish "baked-in fetch that loads on render" from "a user-clickable link."
**How to avoid:** Scope the test to **resource-loading** URLs (`@import`, `src=`, `url(...)` in CSS, `<link href>`) — those fetch automatically. Anchor `href="https://..."` (a clickable repo link) is permitted. Recommended: assert no `fonts.googleapis.com` / no `@import url('http` / no `src="http` in generated HTML. Diagrams are inline SVG (render.py:16, diagrams.py) — already local.
**Warning signs:** Test passes locally but a page makes a network request when opened offline (DevTools → Network).

### Pitfall 3: Non-deterministic ingest order breaks SITE-06 byte-stability
**What goes wrong:** `Path.glob`/`os.walk` returns files in filesystem order, so the corpus (and its rendered HTML) differs run-to-run.
**Why it happens:** Directory iteration order is platform-dependent.
**How to avoid:** `sorted(paths)` in `capture_files` (shown in Pattern 1) and a fixed `Source.timestamp` if it's rendered — note `Source.timestamp` defaults to `_utcnow()` (semantic.py:53) which is NON-deterministic. The adapters solved this with `EPOCH_ZERO`/`deterministic_timestamp` (adapters/_timestamps.py). **Reuse that** for `capture_files` so the work corpus is byte-stable like the adapter corpora.
**Warning signs:** `test_site_is_byte_stable_across_two_renders` (test_render.py:549) fails for the work corpus.

## Code Examples

### Wire the work corpus into the CLI (WORK-03 / Phase-10 forward note)
```python
# Source: cli.py:26-73 — add a corpus selector; review_blockers is already corpus-agnostic
import typer
from enum import Enum

class CorpusName(str, Enum):
    rev1 = "rev1"
    work = "work"

@app.command()
def build(out: str = typer.Option("", help="Output dir (default per corpus)"),
          corpus: CorpusName = typer.Option(CorpusName.rev1, help="Which corpus to render")):
    if corpus is CorpusName.work:
        from .worksurface import build_work_site
        written = build_work_site(out or "content/work/site")
    else:
        from .dogfood import build_site
        written = build_site(out or "content/rev1/site")
    for p in written: typer.echo(f"  {p}")

@app.command()
def check(corpus: CorpusName = typer.Option(CorpusName.rev1, help="Which corpus to gate")):
    if corpus is CorpusName.work:
        from .worksurface import build_work_surfaces as build_surfaces
    else:
        from .dogfood import build_surfaces
    from .review import review_blockers
    surfaces = build_surfaces()
    sources = {s.id: s for surf in surfaces for s in surf.traces}
    blockers = [b for surf in surfaces for b in review_blockers(surf, sources)]
    if blockers:
        for b in blockers: typer.echo(f"BLOCK [{b.kind.value}] {b.surface_id}: {b.detail}")
        raise typer.Exit(1)
    typer.echo("All published surfaces clean — no blockers.")
```

### Optional thin Provenance/Lineage summary (WORK-03)
The masthead already emits `captured via <tool>` and `derived from <lineage.derived_from>` (render.py:775-778), and `_fanout_row` renders the produced chain. If a more explicit "how the work was done" block is wanted, **populate `Surface.lineage`** (semantic.py:452-456 — `derived_from` = the ingested file ids, `produced` = the fan-out surface ids) so the existing masthead line becomes a real provenance/lineage summary with **no new renderer code**. This is the recommended minimal addition.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Fonts via Google-Fonts `@import` (prototype) | Self-host woff2 + `@font-face` | design-system.md:65 explicitly mandated "self-host in production" | Phase 11 finally executes the spec's standing instruction; removes the last baked external call |
| Positional source ids / synthesized session transcripts (Rev1 dogfood) | File-id sources whose transcript IS the file content (work corpus) | Phase 11 | Claims trace to real, openable repo files; `link_for_source` resolves them automatically |

**Deprecated/outdated:**
- The `@import url('https://fonts.googleapis.com/...')` at render.py:104 — remove entirely; do not keep as progressive enhancement.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | DM Serif Display / DM Mono / Instrument Sans ship under SIL OFL (license-compatible to commit the woff2) | Package Legitimacy Audit | If a family is non-OFL, committing the woff2 could be a license issue — verify the downloaded font license before committing |
| A2 | The no-external-call test should permit clickable `<a href="https://...">` repo links and only forbid resource-loading URLs | Pitfall 2 / Tests | If the intended guarantee is "zero absolute http(s) anywhere," the source-link `repo_url` (render.py:53) would also need to become relative — a larger change. Recommend confirming the test's intended strictness. |
| A3 | The work corpus should live at `content/work/` with its own ledger | Project Structure | If it should instead extend `content/rev1/`, the build wiring differs slightly |

**If this table is empty:** it is not — A1/A2 in particular should be confirmed before locking.

## Open Questions

1. **How strict is "no external calls"?**
   - What we know: WORK-01 says "data stays local"; CLAUDE.md says "no external calls baked in." The font `@import` clearly violates this.
   - What's unclear: whether *clickable* outbound repo links (`repo_url`, render.py:53) also count. They don't auto-fetch, but a maximalist reading would relativize them too.
   - Recommendation: Default to forbidding only **auto-loading resource URLs** (`@import`, `src=`, CSS `url()`, `<link>`), permit clickable `<a href>`. Flag for confirmation (A2).

2. **Which files to ingest for the dogfood corpus?**
   - What we know: the build is richly recorded in `.planning/`, `WHERE-WE-ARE.md`, `RETRO.md`, `CLAUDE.md`, and `src/`.
   - What's unclear: the exact glob (whole `src/` tree? just the spine files referenced by claims?).
   - Recommendation: ingest a curated, fixed list (the files the hand-authored claims actually cite — e.g. `CLAUDE.md`, `src/newsletters/semantic.py`, `src/newsletters/capture.py`, `docs/architecture.md`, `.planning/ROADMAP.md`) rather than a broad glob, so every ingested `Source` is actually traced (no orphan sources) and the corpus stays byte-stable and small.

3. **Where do the woff2 files come from / get committed?**
   - What we know: design-system.md:65 mandates self-hosting; no `.woff2` exists in the repo today (verified).
   - Recommendation: download the 3 OFL families' woff2 once, commit under `content/.../fonts/` (+ their license files), and have the renderer emit/copy them into each site output. A `checkpoint:human-verify` for the font download+license is prudent (the only external-fetch step, done once at authoring time, not at render time).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 + stdlib `pathlib` | `capture_files` ingest | ✓ | runtime | — |
| pydantic >=2 | models | ✓ (core dep) | >=2 | — |
| typer[all] | CLI corpus selector | ✓ (core dep) | — | — |
| woff2 font files | self-hosted `@font-face` | ✗ (not in repo) | — | system-font fallback stack already in `--font-*` tokens (render.py:113) |
| Network (font download) | one-time authoring step only | n/a | — | If unavailable, ship system-font fallback only and defer woff2 |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** the woff2 files — until downloaded, the existing `Georgia/system-ui/Courier New` fallbacks render the site (degraded fidelity, but offline and functional).

## Validation Architecture

> nyquist_validation is not explicitly false in config → section included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, testpaths=["tests"], pythonpath=["src"]) |
| Quick run command | `pytest tests/test_worksurface.py -x` (new file) |
| Full suite command | `pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WORK-01 | `capture_files` reads files read-only into content-addressed Sources; never writes the target | unit | `pytest tests/test_worksurface.py::test_capture_files_read_only_content_addressed -x` | ❌ Wave 0 |
| WORK-01 | Generated HTML contains ZERO external resource-loading URLs (no `fonts.googleapis.com`, no `@import url('http`, no `src="http`) | unit | `pytest tests/test_worksurface.py::test_no_external_calls_in_output -x` | ❌ Wave 0 |
| WORK-02 | Hand-authored Report inherits traced structure (each claim has ≥1 addressed Trace to a file, or is in missing[]) | unit | `pytest tests/test_worksurface.py::test_work_report_inherits_traced_structure -x` | ❌ Wave 0 |
| WORK-03 | Provenance/lineage visible on each surface (claim→file link, verbatim span, honesty panel, lineage masthead all present in HTML) | unit | `pytest tests/test_worksurface.py::test_provenance_lineage_visible -x` | ❌ Wave 0 |
| WORK-03 | `newsletters check --corpus work` gates the work corpus (exit 0 clean / nonzero on a planted blocker) | e2e | `pytest tests/test_worksurface.py::test_check_gates_work_corpus -x` | ❌ Wave 0 |
| SITE-06 (carried) | Work site is byte-stable across two renders | unit | `pytest tests/test_worksurface.py::test_work_site_byte_stable -x` | ❌ Wave 0 |
| PKG-03 (carried) | Bare no-extras install still runs build/check on the work corpus (no AI, no new dep reachable) | gate | existing AI-isolation gate (test_ai_optional.py) extended to import worksurface | ✅ extend |

**Recommended test designs:**
- **no-external-call:** `build_work_site(tmp_path)`, read every `*.html`, assert none contain `fonts.googleapis.com`, `@import url('http`, `src="http`, or `url(http` (CSS). Permit `<a ... href="https://...">` (clickable, not auto-loading). This is the WORK-01 guarantee test.
- **read-only ingest:** snapshot mtimes/hashes of the scanned tree, run `capture_files`, assert no file changed; assert each returned `Source` has `is_addressed`-able content (its transcript hashes; a trace minted via `Trace.from_source` round-trips).
- **traced structure:** build the work Report, assert every `ClaimsBlock` claim either has `evidence[0].is_addressed and evidence[0].source_id` ∈ ingested file ids, or appears in `surface.missing` (faithful — nothing untraced sneaks through; mirrors `open_pull_request` invariant 2, semantic.py:525-531).
- **provenance/lineage visible:** render the work Report, assert the HTML contains a repo-file link (`link_for_source` output), a `claim-span` div (verbatim trace), the `honesty` panel, and a `derived from`/`captured via` masthead bit.
- **check gate:** mirror `test_review_cli.py` — assert exit 0 on the clean work corpus; plant a STALE/open-missing surface and assert nonzero.

### Sampling Rate
- **Per task commit:** `pytest tests/test_worksurface.py -x`
- **Per wave merge:** `pytest`
- **Phase gate:** full suite green + `newsletters check --corpus work` exit 0 before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_worksurface.py` — covers WORK-01/02/03 + byte-stability
- [ ] `src/newsletters/worksurface.py` — `capture_files`, `build_work_report`, `build_work_surfaces`, `build_work_site`
- [ ] Font assets `content/.../fonts/*.woff2` (+ OFL licenses) — one-time download (checkpoint:human-verify)
- [ ] Extend `tests/test_ai_optional.py` to import `worksurface` on the bare install (PKG-03 carried)

## Security Domain

> security_enforcement not false in config → included. This phase has a NARROW surface (local file reads + static HTML render), so most ASVS categories are N/A.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth in this phase |
| V3 Session Management | no | No sessions |
| V4 Access Control | no | Local CLI tool |
| V5 Input Validation | yes | File reads are decoded `utf-8`; path traversal bounded by an explicit curated file list (not arbitrary user input). HTML output `_e`-escapes all interpolations (render.py `_e`). |
| V6 Cryptography | no | `content_hash` is SHA-256 for addressing (integrity, not secrecy) — already in semantic.py:71-83, not re-implemented |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal / reading outside the repo | Information Disclosure | Ingest a fixed curated list resolved under `root`; `relative_to(root)` raises if a path escapes |
| External call / phone-home baked into output | Information Disclosure | Remove the font `@import`; the no-external-call test enforces it (WORK-01) |
| HTML/script injection via file content in claims/spans | Tampering | `_e` (html.escape) on every interpolation; span/free text never enters an `href` (render.py:82-83, 470) |
| Accidental write to the target codebase | Tampering | `capture_files` uses only `read_text`; read-only test asserts no file changed |

## Sources

### Primary (HIGH confidence — live codebase)
- `src/newsletters/capture.py:37-113` — `WorkSession`/`Decision`/`capture_session`/`build_report` (WORK-02 author path)
- `src/newsletters/semantic.py:49-83, 86-184, 443-456, 464-559` — `Source`/`content_hash`, `Trace.from_source`, `Provenance`/`Lineage`, `Surface`/`publish`/`missing`
- `src/newsletters/dogfood.py:85-209, 651-687` — content-addressing pattern (`_address_trace`/`_address_report`) + `build_site`/`Site`/`Ledger`
- `src/newsletters/render.py:53-97, 104, 432-476, 716-818` — `repo_url`/`link_for_source`, the Google-Fonts `@import`, `_fanout_row`/`_claim_spans`, `_honesty_panel`/`render_surface` masthead provenance+lineage
- `src/newsletters/review.py:36-121` — corpus-agnostic `review_blockers` merge-block gate
- `src/newsletters/cli.py:26-73` — `build`/`check` commands to extend
- `src/newsletters/adapters/normalize.py:50-117` — the single faithful-extraction rule (`Trace.from_source` is the sole minting path)
- `src/newsletters/adapters/_timestamps.py` (referenced) — `EPOCH_ZERO`/`deterministic_timestamp` for byte-stable Sources
- `docs/design-system.md:65, 69-71` — "self-host in production" + the three font families
- `pyproject.toml:17-21, 23-47, 62-67` — core deps (zero new dep needed), extras discipline, pytest config
- `tests/test_render.py:549-559`, `tests/test_review_cli.py` — byte-stability + CLI-gate test precedents

### Secondary (MEDIUM confidence)
- `.planning/REQUIREMENTS.md:54-56` — WORK-01/02/03 statements
- `.planning/ROADMAP.md:290-303` — Phase 11 goal + 3 success criteria

### Tertiary (LOW confidence)
- Font OFL licensing (A1) — based on training knowledge of Google Fonts; verify the actual downloaded license files.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new dep, all stdlib + existing core deps verified against pyproject.toml
- Architecture (reuse map): HIGH — every reused device cited at file:line in the live tree
- Pitfalls: HIGH — drawn from real constraints (determinism, content-addressing, escaping) already encoded in the codebase
- Font decision: HIGH (recommendation) / MEDIUM (license detail A1)
- No-external-call test strictness: MEDIUM — depends on confirming A2

**Research date:** 2026-06-18
**Valid until:** 2026-07-18 (stable — internal codebase, no fast-moving external dependency)
