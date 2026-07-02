# Architecture Research

**Domain:** Config-driven, module-scope swim-lane Report **composer** integrated into the existing Newsletters trust spine (brownfield).
**Researched:** 2026-07-02
**Confidence:** HIGH (every claim below is grounded in the live `src/newsletters/` tree; file:line cited).

> Scope: how the NEW loader + composer bolt onto what already exists. Not re-deriving the spine.

---

## Standard Architecture (the integration seam)

### System Overview

```
┌───────────────────────────────────────────────────────────────────────┐
│  CONFIG (YAML)          module-a fixture + sample_team/*.yml            │
│  functional_groups.yml · q2_okrs.yml · team_members.yml                 │
└───────────────┬───────────────────────────────────────────────────────┘
                │ read-only Path.read_text  (mirror capture_files)
                ▼
┌───────────────────────────────────────────────────────────────────────┐
│  NEW · swimlane.py  (the LOADER — leaf, I/O + parse)                    │
│   • each YAML file → Source(id=relpath, transcript=<file text>,         │
│                            timestamp=EPOCH_ZERO)                        │
│   • select configured lane(s) from the parsed dict (NO FunctionalGroup  │
│     instantiation — see tension §Anti-Patterns)                         │
│   • each verbatim value → Claim, Trace.from_source(find(...))           │
│   • find()==-1 or declared-but-unevidenced slot → missing[]             │
│   • emits: list[Source] + list[SectionBinding]                         │
└───────────────┬───────────────────────────────────────────────────────┘
                │ typed bindings + Sources (in memory, no disk)
                ▼
┌───────────────────────────────────────────────────────────────────────┐
│  NEW · compose.py  (the COMPOSER — semantic assembly, AI-free)         │
│   • SectionBinding[] → per-lane (KpiStripBlock + ClaimsBlock)          │
│   • KpiItem.delta computed at compose time (NO Kpi model change)        │
│   • unevidenced → Surface.missing[]                                     │
│   • Surface(REPORT, Draft) via templates.REPORT + Review(light)         │
│   • build_module_surfaces() / build_module_site()  (mirror worksurface) │
└───────────────┬───────────────────────────────────────────────────────┘
                │ list[Surface]                     ledger: content/module/ids.json
                ▼
┌───────────────────────────────────────────────────────────────────────┐
│  EXISTING (reused unchanged)                                            │
│   site.Site/Ledger  →  R-NNN   │  render.render_surface/render_library  │
│   review.review_blockers (gate) │  cli --corpus {rev1|work|+module}     │
└───────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | New / Modified / Reused |
|-----------|----------------|-------------------------|
| `swimlane.py` (loader) | YAML files → `Source` (transcript=file text), select configured lanes, mint traced `Claim`/`KpiItem` or route to `missing[]` | **NEW** |
| `compose.py` (composer) | `SectionBinding[]` → `Surface(REPORT, Draft)`; per-lane `KpiStripBlock`(Δ) + `ClaimsBlock`; `build_module_site` | **NEW** |
| `content/module-a/*.yml` fixture | Synthetic, fabricated-naming module config (the worked example) | **NEW** (config, not `src/`) |
| `semantic.Source/Trace/Claim/Surface`, `Trace.from_source` | The pinning + honesty primitives | **REUSED** — `semantic.py:126` (`from_source`), `:187` (Claim), `:493` (Surface) |
| `semantic.KpiStripBlock/KpiItem/ClaimsBlock` | The typed slots the composer fills | **REUSED** — `semantic.py:333,364,370` |
| `templates.REPORT` | Report preset + `ReviewPolicy.light()` (self-approve) | **REUSED** — `templates.py:121,129` |
| `site.Site/Ledger` | Stable `R-NNN`, `content/module/ids.json` | **REUSED** — `site.py:82,223` |
| `render.render_surface/render_library` | Claim-beside-span, honesty panel, file-path claim links | **REUSED** — no renderer change (worksurface precedent) |
| `review.review_blockers` | The corpus-agnostic merge gate | **REUSED unchanged** — `review.py:58` |
| `cli.CorpusName` + `build`/`check` | Add `module` corpus branch | **MODIFIED** — `cli.py:16,34,75,123` |

---

## Answers to the Five Integration Questions

### (a) Where the modules live + import edges — TWO top-level siblings

**Recommendation: two new top-level modules, siblings of `worksurface.py`** — `swimlane.py` (loader) and `compose.py` (composer). Not `adapters/`, not `distill/`.

Rationale, grounded in the precedent:
- `worksurface.py:7-15` documents exactly why a hand-authored, file-backed corpus is a **top-level module, not** an `adapters/` `DistillPort` (that framework is for *modality* extraction routed through a distiller) and not `dogfood.py` (the synthesized *sample*). The swim-lane loader is the same shape: a plain read-only file reader over a curated config set — top-level is the honest fit.
- **Why split loader from composer (two, not one like `worksurface.py`)**: `worksurface.py` folds capture+author+site into one module because it is tiny and hand-authored. Here the two halves have *different import edges and different reuse futures*:
  - The **loader** carries the only new third-party edge (`yaml`) and the disk I/O; it is a near-leaf like `locators.py`.
  - The **composer** is pure in-memory semantic assembly (no `yaml`, no disk) and is where the generic section abstraction (question d) lives, so future project/interview kinds import the composer, not the loader.
  - Splitting keeps the composer unit-testable with hand-built bindings (no YAML fixture needed) and keeps the loader testable for determinism/missing-routing without constructing a Surface.
  - *Fallback:* if the roadmapper wants minimal surface area, one `modulereport.py` mirroring `worksurface.py` is acceptable — but the loader/composer seam is the durable boundary and should at least be two functions with no disk access in the composer half.

**Import edges (all keep `lint-imports` green — `yaml` is not in the forbidden AI list, `.importlinter:28-36`):**

| Module | Imports | Must NOT import |
|--------|---------|-----------------|
| `swimlane.py` | stdlib `pathlib`; `yaml`; `.semantic` (Source, Trace, Claim); `.adapters._timestamps.EPOCH_ZERO` (reuse, `worksurface.py:44`) | `distill/`, any AI pkg, `render`, `site` |
| `compose.py` | `.semantic` (blocks, Surface); `.templates` (REPORT); `.capture` (optional, `build_report`); `.swimlane`; `.site` (Ledger/Site) only in the `build_module_site` fn | `yaml`, `distill/`, any AI pkg |

**New core dependency:** `yaml` (PyYAML) must be added to `pyproject.toml [project] dependencies` (currently only `pydantic>=2`, `typer[all]`, `sqlmodel` — `pyproject.toml:17-20`). PyYAML 6.0.1 is present in the env but **undeclared**; declare it. It is AI-free, so it does not violate the AI-optional-core contract (`.importlinter:23-36`) and stays importable on a bare install. Add a one-line note to the bare-install CI reasoning.

### (b) YAML text as `Source.transcript` so `Trace.from_source` offsets work — YES

**Mirror `capture_files` exactly** (`worksurface.py:66-119`). Each config file becomes:

```python
Source(id="<posix relpath>", context="module-config:<relpath>",
       transcript=path.read_text("utf-8"), timestamp=EPOCH_ZERO)
```

Then each loaded value becomes a `Claim` content-addressed via the **sole** pinning constructor `Trace.from_source(src, start, start+len(value))` where `start = src.transcript.find(value)` — the identical verbatim-or-missing dance already proven in `worksurface.build_work_report` (`worksurface.py:196-221`):
- `find() >= 0` → verbatim slice → `Trace.from_source` pins `content_hash` + `start`/`end` + `span` (`semantic.py:126-170`). Gives STALE detection (`semantic.py:177`) and the render claim-beside-span for free.
- `find() < 0` (a *declared slot* with no verbatim evidence, per PROJECT.md) → append text to `Surface.missing[]`, **never fabricate an offset** (`worksurface.py:216-220`). This is the honesty routing.

Two subtleties the composer must respect:
1. **The Δ is NOT traced.** A KPI title like `Dilithium Efficiency Index` appears verbatim in `q2_okrs.yml:4` → traces fine. But a compose-time delta (`start→close Δ`) does **not** appear in the YAML text, so it is **not** a Claim — it lives only in `KpiItem.delta` (a free `str`, `semantic.py:336`), computed by the composer. This is exactly the "Δ at compose time, no `Kpi` baseline field" decision (PROJECT.md:161). Keep KPI *labels/values* traced; keep Δ derived.
2. **Free claim-to-file link:** because `Source.id` is the posix relpath, `render.link_for_source` turns each claim into a working link to the YAML file (`worksurface.py:210-217` documents the same device). This requires the fixture config to be **committed inside the repo/site tree** so the link resolves — flag for the worked-example phase.

Determinism (SITE-06): `sorted()` inputs + `EPOCH_ZERO` + no `datetime.now()` → byte-stable Sources, same as `worksurface.py:116-118`.

### (c) Site build + ledger + `check --corpus` — a THIRD corpus (`module`)

**Add a third corpus, do not extend `work`.** The `work` corpus is "how *this build* was done" over *real repo files* (`worksurface.py:122-135`); the module report is a *config-driven, synthetic* artifact (`module-a`, fabricated naming). Mixing them muddies the sample/real/config boundary — the same argument `worksurface.py:9-15` makes for keeping `work` out of `dogfood.py`. The `CorpusName` enum already generalizes this pattern (`cli.py:16-37`).

Concrete edits (all in `cli.py`, the selector-routes-the-builder pattern, gate never forked — `cli.py:114-115`):
- `CorpusName` enum (`cli.py:28-29`): add `module = "module"`.
- `_DEFAULT_OUT` (`cli.py:34-37`): add `CorpusName.module: "content/module/site"`.
- `build` (`cli.py:75`): add `elif corpus is CorpusName.module: from .compose import build_module_site`.
- `check` (`cli.py:123`): add the parallel branch → `compose.build_module_surfaces()`.

**Own ledger:** `content/module/ids.json`, loaded/saved via the existing `Ledger` (`site.py:82`, `worksurface.py:417-419` precedent). Report kind → `R-{:03d}` (`site.py:69`); the first module report gets **R-001 in its own ledger**, independent of rev1/work — stable and append-only (`site.py:129-159`). `build_module_site` mirrors `build_work_site` (`worksurface.py:378-436`) beat for beat: `Ledger.load → Site.from_surfaces → ledger.save → render each page → render_library → _emit_fonts`.

**Gate behaviour (be honest about it):** `check --corpus module` runs the *identical* `review_blockers` (`review.py:58`). Because the composed report is **Draft**, `review_blockers` returns `[]` immediately (published-only boundary, `review.py:77-79`) — so the module gate passes *vacuously* while Draft, exactly like the `work` corpus's Draft report. That is the correct current state, not a gap to paper over; the gate becomes load-bearing only if/when a module report is published.

### (d) Keeping the per-lane section abstraction generic (project/interview kinds later)

Build the composer around a **generic section abstraction**, not a swim-lane-specific type — this is the milestone's "section abstraction stays generic" mandate (PROJECT.md:44-46).

- Define a small `SectionBinding` (or `SectionDraft`) dataclass/BaseModel the **loader** emits: `{ heading: str, kpi_items: list[KpiItem], claims: list[Claim], missing: list[str] }`. This is *kind-agnostic* — a section is "a scope label + its KPI strip + its traced claims + its gaps."
- The **swim-lane binding** is the first producer: one `SectionBinding` per configured lane. A future **project-kind** binding produces one per initiative; an **interview-kind** binding one per topic. The composer's assemble step (`SectionBinding[] → Surface.blocks`) never changes — it just interleaves, per section, a `KpiStripBlock(heading=section.heading, items=...)` (the `heading` field exists, `semantic.py:372`) followed by a `ClaimsBlock(claims=...)`, and unions `missing[]`.
- **Reuse existing blocks, add no new block type** — `render.py` already renders `KpiStripBlock`/`ClaimsBlock` (dogfood inserts them at `dogfood.py:252,466`), so the composer inherits the renderer unchanged, exactly as `worksurface.py` reused the Phase 9/10 devices.
- **No hardcoded lane/module/owner names in `src/`** (PROJECT.md:39-42, 93): the binding reads *keys from the parsed config*, never literals. Enforce with the abstraction-guard test that fails if a fixture name (e.g. `module-a`, a lane name) appears anywhere under `src/`.

The seam: **loader owns "which sections and what's in them" (config-specific); composer owns "sections → a Draft Report" (kind-agnostic).** New kinds are new loader bindings, zero composer change.

### (e) Build order across the 4 fixed phases

Dependencies are strictly linear for 1→2→3; phase 4 is independent tooling.

1. **Loader (`swimlane.py`)** — YAML→`Source(transcript=file text)`, config→`SectionBinding[]`, verbatim `Trace.from_source` + `missing[]` routing, `EPOCH_ZERO` determinism. Declare `yaml` dep. Land the **abstraction-guard test** here (or phase 3). *Depends on:* `semantic` (exists). Testable with fixture YAML, no Surface needed.
2. **Composer (`compose.py`)** — `SectionBinding[] → Surface(REPORT, Draft)`; per-lane `KpiStripBlock` with **compose-time Δ** into `KpiItem.delta`; `ClaimsBlock`; `missing[]` union; `Review(policy=REPORT.review_policy, author=...)`; stable `R-NNN` via `Ledger`. This is where the generic section abstraction crystallizes. *Depends on:* phase 1 + `templates` + `capture` + `site`.
3. **Worked example + corpus wiring** — commit the synthetic `module-a` fixture config (fabricated naming, self-consistent so links resolve); `build_module_surfaces`/`build_module_site` mirroring `worksurface.py:378`; extend `CorpusName` + `build`/`check` branches; `content/module/ids.json`; render into `content/`, verify Library-visible with claim-beside-trace + honesty panel. *Depends on:* phases 1+2.
4. **Signals-voice PR bodies (ship workflow)** — generate PR bodies from `git diff` + **verbatim** `newsletters check` output; **must not weaken any gate** (PROJECT.md:37, quality gate). *Depends on:* nothing in 1-3 structurally (it edits the ship workflow/script, not the composer); ordered last per the milestone and because it *quotes* the gate output. Low coupling — the only shared surface is the CLI `check` command it shells out to.

---

## Anti-Patterns (specific to this integration)

### Anti-Pattern 1: Instantiating `FunctionalGroup`/`Kpi` from the raw sample YAML
**What people do:** load `functional_groups.yml` straight into `models.FunctionalGroup`.
**Why it's wrong (live tension, confirmed):** `FunctionalGroup.owner` is typed `str` but `team_members` is `list[TeamMember]` (`models.py:68-69`), while the sample YAML supplies **string idsids** for both (`functional_groups.yml:5-9`: `owner: dataf606`, `team_members: [deannatr, ...]`). Worse, the `ensure_owners_are_team_members` validator (`models.py:78-86`) compares `ownable.owner` (typed `TeamMember`, `models.py:50`) against `team_member_names` (`list[str]`, `models.py:74`) — a type mismatch that cannot pass — and `team_members.yml` uses an `idsid` key that isn't even a `TeamMember` field (`team_members.yml:6` vs `models.py:14-17`). **Direct instantiation fails.**
**Do this instead:** the loader works at the **parsed-dict level** — select the configured lane, pull the KPI titles/statuses/owner it needs, and emit `Claim`/`KpiItem` directly. The composer needs a lane label, its KPIs, and its owner — *not* the full validated OKR object graph. This also honours the constraint **"no `Kpi` model change for baselines."** (If typed lane objects are ever wanted, resolve `idsid → TeamMember` first — out of scope for v1.1.)

### Anti-Pattern 2: Hand-minting `content_hash` or fabricating char offsets
**What people do:** compute a hash or guess a `start`/`end` for a value that isn't verbatim in the YAML.
**Why it's wrong:** breaks the single-pinning-path invariant; `worksurface.py:26` calls hand-minting an anti-pattern.
**Do this instead:** `Trace.from_source` only (`semantic.py:126`); non-verbatim/declared-slot → `missing[]` (`worksurface.py:216-220`).

### Anti-Pattern 3: Forking the gate for the module corpus
**What people do:** add module-specific checks to `review_blockers` or a parallel checker.
**Why it's wrong:** the selector routes the *builder*, never the gate (`cli.py:114-115`, T-11-13).
**Do this instead:** reuse `review.review_blockers` unchanged; the module corpus passes the identical contract.

### Anti-Pattern 4: A new renderer or block type for lane sections
**What people do:** invent a `SwimLaneBlock` + renderer branch.
**Why it's wrong:** couples presentation to one report kind; the renderer already handles `KpiStripBlock`/`ClaimsBlock`.
**Do this instead:** compose per-lane pairs of existing blocks using `KpiStripBlock.heading` (`semantic.py:372`) as the lane header — zero renderer change.

---

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `swimlane.py` ↔ config YAML | read-only `Path.read_text` | mirror `capture_files`; `EPOCH_ZERO`; posix-relpath `id` |
| `swimlane.py` → `compose.py` | `list[Source]` + `list[SectionBinding]` | in-memory; composer never touches disk |
| `compose.py` → `site.Site/Ledger` | `Surface[]` + `content/module/ids.json` | R-NNN append-only (`site.py:223`) |
| `compose.py` → `render.py` | `render_surface`/`render_library` | reused unchanged (`worksurface.py:422-430`) |
| `cli.py` → `compose.py` | lazy import in `build`/`check` branch | keeps bare install light (`cli.py:76`) |
| `compose.py` → `review.py` | via `check --corpus module` | Draft ⇒ `review_blockers` returns `[]` (`review.py:77`) |

### External Services
None. Self-hostable, no network, no external call on content (PROJECT.md constraints; `worksurface.py` read-only precedent).

---

## Scaling Considerations

Not a throughput problem — this is a deterministic, few-file config compile. Realistic axes:

| Scale | Adjustment |
|-------|-----------|
| 1 module, few lanes (v1.1) | The design as-is; one report, one ledger. |
| Many modules | Parameterize `build_module_site` by a config path/dir; one ledger per module tree OR a shared `content/module/ids.json` keyed by slug (append-only handles it, `site.py:150`). Keep the `module` corpus, vary the config. |
| Many report *kinds* (project/interview) | New `SectionBinding` producers only; composer + renderer + gate untouched (question d). |

---

## Sources

- `src/newsletters/worksurface.py` (the closest analog — capture_files, build_work_report, build_work_site, own ledger) — HIGH
- `src/newsletters/site.py` (Ledger append-only R-NNN, Site.from_surfaces) — HIGH
- `src/newsletters/semantic.py` (Trace.from_source, Claim, KpiItem/KpiStripBlock/ClaimsBlock, Surface) — HIGH
- `src/newsletters/capture.py` (build_report precedent, Draft Report assembly) — HIGH
- `src/newsletters/models.py` (FunctionalGroup/Kpi tension) — HIGH
- `src/newsletters/cli.py` (`--corpus` selector routing) — HIGH
- `src/newsletters/review.py` (corpus-agnostic gate, published-only boundary) — HIGH
- `sample_team/*.yml` (config shape, idsid vs TeamMember mismatch) — HIGH
- `.importlinter`, `pyproject.toml` (AI-free contract; yaml undeclared) — HIGH
- `docs/architecture.md` §7-8 (Rev1 + Phase-11 as-built) · `.planning/PROJECT.md` (milestone scope, decisions) — HIGH

---
*Architecture research for: v1.1 Swim-Lane Module Report composer (brownfield integration)*
*Researched: 2026-07-02*
