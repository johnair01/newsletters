# Phase 4: Sample corpus + recipe - Research

**Researched:** 2026-08-29
**Domain:** In-repo archaeology — corpus wiring, published-tree integration, `.pptx` golden gate, operator documentation
**Confidence:** HIGH (every load-bearing claim verified by executing the live code in this repo)

## Summary

Phase 4 adds **no new capability**. Every mechanism it needs already exists and is green:
`load_weekly_spec` → `build_weekly_report` → `weekly_slots` → `render_surface_pptx` (Phase 3 + 2),
`render_surface` / `render_library` / `Ledger` / `Site` (v1.1), `publish.assemble_site` (v1.2), and
the `weekly` + `pptx` CI jobs. What Phase 4 does is **wire a fourth corpus into an existing
four-corner harness** (builder · ledger · publish assembly · gate) and **write the recipe**. The
technical risk is therefore not "can it be built" — it is **"which integration points get missed."**
That risk is enumerable, and this document enumerates it exhaustively (16 sites, §Integration Point
Inventory).

I built a working prototype of the whole phase in a scratch tree and ran it against the live
package. Result: a sibling `content/weekly/` corpus composes a `Surface(REPORT, Draft)` at
`EPOCH_ZERO`, gets `R-001` from its own fresh ledger, renders to HTML with a populated honesty panel
and `claim-span`s and zero `href="None"`, produces all four `NL_` deck slots, and renders a **28,774
byte deck that is byte-identical across a real 3-second wall-clock boundary** with an equal
`part_digest`. The three planted absences the roadmap demands all appeared in `missing[]`, verbatim
(§The Honesty-Path Fixture). Nothing in `src/` had to change to get there.

**Primary recommendation:** ship a **sibling `content/weekly/` corpus** built by a new
`src/newsletters/weeklysite.py` (a thin mirror of `modulesite.py`), whose **binding source is the
existing committed `content/module/*.yml`** — that is the literal "in the `content/module` lineage"
the seed asks for, it needs no second fabricated lane config, and it supplies the required
"lane with no KPIs" honesty row for free. Keep the deck **out of `site/`** (`content/weekly/deck/`)
so the published tree stays HTML-only and no new render device or CSS is needed; commit the deck
**plus a `.digest` sidecar** and assert the digest in two tiers (stdlib-only tamper check on every
install; `[pptx]`-gated fresh==committed in the `weekly` job). Add **one** new CLI command,
`newsletters weekly`, so `docs/weekly.md`'s commands are the shipped CLI rather than a `python -c`.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Binding:** all milestone decisions + Phase 1–3 recorded decisions carry. The deck is
**text-only** (recorded); the sample commits **both the `.pptx` binary and its part_digest**,
asserting the digest (Phase 1 decision Q3). Ledgers append-only. Zero new CSS.

**Corpus placement — decide per precedent, log the choice:** the seed says "in the
`content/module` lineage". The repo's established pattern for a new content family is a
sibling corpus with its own builder, `ids.json` ledger, library page and `--corpus` gate wiring
(work → module precedent) — that keeps committed==fresh gates one-builder-per-corpus. Lean that
way (e.g. `content/weekly/` built by a `weeklysite.py`-style builder or an extension of
`modulesite.py`) unless research shows extending `content/module` in place is genuinely
smaller WITHOUT mixing builders in one byte-stable corpus. Whatever is chosen: the publish
assembly (`publish.assemble_site`), `newsletters check`, the site-integrity tests and the
Records strip must all see the new pages — no dead ends (PUB-03 carries).

**Phase boundary:** The sample ships Draft, watermarked — nothing publishes, nothing touches `main`.

### Claude's Discretion

Synthetic fixture content (abstraction-guard denylist grows), recipe structure of
`docs/weekly.md`, CLI surface (e.g. `newsletters weekly compose|render` or reuse of existing
entry points).

### Deferred Ideas (OUT OF SCOPE)

Carried to PR: real-PowerPoint open; first CI green of pptx/weekly jobs; deck images (round
two); contentStatus tri-state; template regeneration + fixture delegation (P-06/P-08 carry).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| **WKLY-05** | A synthetic sample weekly in the `content/module` lineage (fabricated everything; honesty-path coverage: a lane with no KPIs, a recognition with no source email, an asset with no provenance) composes and renders to `.pptx` under the carried gate set: pytest · lint-imports · `newsletters check` over all corpora · double-render stability (including `.pptx` per WKLY-01's recorded definition) · bare-install untouched · mypy/black/isort no-new-failures. | §Corpus Placement Decision (route + evidence) · §The Honesty-Path Fixture (all three absences produced and their exact `missing[]` strings captured by execution) · §The Deck in the Corpus (two-tier `part_digest` gate) · §Integration Point Inventory (the 16 wiring sites) · §Gates Inventory (baselines measured today) |
| **WKLY-06** | `docs/weekly.md` lets an operator who is not the author point the adapters at a real workbook / template deck / `.eml` drop / photo folder (read-only, data stays local — the WORK-01 pattern), author the Weekly Spec, run compose + render, and review the result. | §`docs/weekly.md` — Shape and Honest Commands (the WORK-01 five-step pattern, the command inventory split into *exists* vs *needs adding*, the carried P-07 `word_wrap` guidance, the SC-4 "executed against the synthetic corpus" proof mechanism) |
</phase_requirements>

## Architectural Responsibility Map

The tiers here are this repo's layers, not web tiers.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Authored weekly content (week, narrative, recognitions, team, assets, config) | **Corpus data** (`content/weekly/*.yml`) | — | ABSTRACT EVERYTHING: specifics live in YAML, never in `src/` (`tests/test_abstraction_guard.py` walks every `*.py` under `src/newsletters/`) |
| Lane/KPI evidence (incl. the no-KPI lane) | **Corpus data** (`content/module/*.yml`, reused) | Core spine (`swimlane.load_swimlanes`) | The existing committed module config already declares a KPI-less lane; reusing it *is* the "content/module lineage" and avoids a duplicated fabricated fixture |
| Recognition evidence source | **Corpus data** (`content/weekly/inbox/*.eml`) | Adapter (`adapters.email_adapter`, stdlib-only) | ADAPT-02 exists; verified extra-free at import |
| Load → typed spec → `Distillation` | **Core spine** (`weeklyspec.load_weekly_spec`) | — | Phase 3; asset placement + all disclosure wording already lives there |
| Compose → `Surface(REPORT, Draft)` | **Core spine** (`weeklyspec.build_weekly_report`) | — | Phase 3; gate untouched by construction |
| Corpus build seam (ledger → Site → HTML → Library → fonts) | **Builder** (new `src/newsletters/weeklysite.py`) | `site.Ledger`, `render.*`, `worksurface._emit_fonts` | `compose.py` is a COMP-contract leaf (must not import `render`/`site`), so the build-and-render seam must be a sibling builder — exactly `modulesite.py`'s stated rationale |
| Deck slots + `.pptx` bytes | **Core spine** (`weekly_slots`) → **writer** (`pptx_writer`) | Builder (default args) | Phase 2/3; `[pptx]` stays lazy inside the writer |
| Corpus → published tree | **Publish** (`publish._CORPUS_LAYOUT`) | Records strips declared per builder | `render.py` stays corpus-blind by design (01-CONTEXT d3) |
| Corpus selection / operator entry points | **CLI** (`cli.py`) | — | `--corpus` routes the *builder*, never forks the gate (T-11-13) |
| Merge-block + published-tree guarantees | **CI** (`ci.yml`, `deploy-pages.yml`) | `tests/test_publish.py` | One definition of "publishable"; no bash re-implementation |
| Operator instruction | **Docs** (`docs/weekly.md`) | CLI (commands must exist) | WKLY-06; SC-4 requires the commands be executed against the synthetic corpus |

## Project Constraints (from CLAUDE.md)

Directives the planner must not plan around. All are treated with locked-decision authority.

| Directive | Consequence for this phase |
|-----------|---------------------------|
| **No auto-publish, ever.** `Draft › In Review › Published` with a recorded reviewer; enforced in `semantic.py`; prove with a test. | The sample surface stays `Draft`; `semantic.py` byte-unchanged; the pinned gate-freeze test (`tests/test_semantic_gate_frozen.py`) must stay green. Deck ships watermarked. |
| **Every published claim traces to evidence**; unsubstantiated → `missing[]`, shown to the reviewer. | The three planted absences must be **visible in the built HTML honesty panel**, asserted by test — not merely present in the model. |
| **AI-optional core.** `core` imports stdlib + Pydantic only; AI behind `[ai]`, lazy. | No new import edges; `lint-imports` must stay 2 kept / 0 broken. `weeklysite.py` may import `render`/`site`/`weeklyspec`/`swimlane` (all in-package) but must not import `pptx` at module level. |
| **Faithful, not suggestive.** Distill extracts and traces; never editorialises. | No composer changes. The sample's narrative is carried byte-verbatim; the planted-editorialization guard stays green. |
| **Interactive until trusted** — no auto-approve of outward-facing actions. | No CI step may advance the gate or push to `main`. Deck generation is an explicit operator command. |
| **Secrets in git-ignored env files; private corpora local + encrypted.** | The sample is 100% synthetic; the recipe must tell the operator their workbook/`.eml`/photos stay local and are never committed. |
| **Branch + PR only. Never push to `main`.** Human gate between phases. | Phase 4 lands on a feature branch; the deploy workflow (main-only) is not to be triggered by this phase. |
| **One task, one atomic commit.** Determinism over cleverness. Commit + push. | See §Commit/Wave Ordering — some edits are only green *together*. |
| **Specs are source of truth**; update spec in the same change. | `docs/architecture.md` §9 and `docs/surfaces.md` §Records strip both say "**three corpora**" — a fourth corpus makes both stale in the same commit it lands. |
| **Visual fidelity is not optional**; match `docs/design-system.md`. | Zero new CSS (also a CONTEXT lock). The weekly's blocks already have branches built from existing `_CSS` classes. |
| **DoD gates re-run independently**; `WHERE-WE-ARE.md` + `RETRO.md` updated. | SC-5. Gate baselines measured in §Gates Inventory. |

## Corpus Placement Decision

**Recommendation: Route (a) — a sibling `content/weekly/` corpus with its own builder
(`src/newsletters/weeklysite.py`) and its own ledger.** [VERIFIED: prototype executed against the
live package]

### Route (a) — sibling corpus: the full cost, enumerated

Nothing here is speculative; each row was located by grep/read in the live repo.

| # | Integration point | File | Edit |
|---|---|---|---|
| 1 | Builder module | `src/newsletters/weeklysite.py` (new) | `build_weekly_surfaces()` + `build_weekly_site()` + `build_weekly_deck()` |
| 2 | Corpus content | `content/weekly/` (new) | spec `*.yml`, `inbox/*.eml`, `assets/*.png`, `template.pptx`, `ids.json`, `site/`, `deck/` |
| 3 | Publish assembly | `src/newsletters/publish.py:35-39` `_CORPUS_LAYOUT` | `+ ("content/weekly/site", "weekly")` |
| 4 | CLI corpus enum | `cli.py:16-33` `CorpusName` | `weekly = "weekly"` + docstring |
| 5 | CLI default out | `cli.py:38-42` `_DEFAULT_OUT` | `CorpusName.weekly: "content/weekly/site"` |
| 6 | CLI build branch | `cli.py:81-95` | `elif corpus is CorpusName.weekly:` → `build_weekly_site` |
| 7 | CLI check branch | `cli.py:167-178` | `elif corpus is CorpusName.weekly:` → `build_weekly_surfaces` |
| 8 | Records strip — rev1 | `dogfood.py:807-810` `_REV1_RECORDS` | `+ ("The weekly record", "weekly/library.html")` |
| 9 | Records strip — work | `worksurface.py:438-442` | `+ ("The weekly record", "../weekly/library.html")` |
| 10 | Records strip — module | `modulesite.py:203-208` | `+ ("The weekly record", "../weekly/library.html")` |
| 11 | Records strip — weekly (new builder declares its 3 neighbours) | `weeklysite.py` | rev1 / work / module, assembled-tree-relative |
| 12 | **Regenerate the 4 chrome pages** the strip actually appears on | `content/rev1/site/{index,library}.html`, `content/work/site/library.html`, `content/module/site/library.html` | `newsletters build --corpus {rev1,work,module}` |
| 13 | Records-strip shape test | `tests/test_render.py:852-854` | third assertion `href="weekly/library.html"` |
| 14 | Published-tree tests | `tests/test_publish.py:37-49` (assemble assertions), `:207` (fonts dir tuple `out/"weekly/fonts"`) | add weekly |
| 15 | CI merge-block + deploy gate 1 | `.github/workflows/ci.yml:122`, `.github/workflows/deploy-pages.yml:72` | `newsletters check --corpus weekly` |
| 16 | CI test-module lists | `ci.yml` `site-integrity` step, `weekly` step | add `tests/test_weeklysite.py` (site-integrity) and the pptx-gated deck module (weekly job) — **see the split rule below** |

**Docs that go stale in the same commit** (CLAUDE.md "specs win, or update them and say why"):
`docs/architecture.md` §9 ("the **three** committed corpora", and §"The `--corpus {rev1|work}`
selector" which is already stale at *two*), `docs/surfaces.md` §Cross-corpus Records strip ("composes
**three corpora**"), `CLAUDE.md` repo-layout table (`content/{rev1,work,module}/`),
`content/README.md` (currently says "Empty until then" — already stale).

**Measured, not assumed:** exactly **4** committed HTML files carry
`<section class="nl-records">` (`grep -rl '<section class="nl-records"' content/`). A naive
`grep -rl nl-records content/` returns **17** because `.nl-records` is styled in every page's
inline `_CSS` — do not size the regen from that number. [VERIFIED: grep, this repo]

### Route (b) — extend `content/module` in place: the cost

**Avoided:** rows 3–16 above (~16 mechanical edit sites) and the 4-page chrome regen.

**Incurred:**
- `modulesite._discover_config` takes `sorted(corpus.glob("*.yml"))[0]` — a second root-level YAML
  in `content/module/` would be silently mis-selected. A weekly would need a filename or
  sub-directory convention *inside* the module corpus, i.e. **two builders in one byte-stable
  corpus** — the exact thing CONTEXT names as the disqualifier.
- One ledger, one committed==fresh gate, one `site/` for two composers: a change in either
  composer moves the same committed HTML set, and a drift diagnosis has to disambiguate which
  builder moved.
- Three existing tests need rework, not extension: `tests/test_modulesite.py::_report_page_name`
  (`build_module_surfaces()[0]` assumes one surface), `::test_committed_equals_fresh_build` (its
  all-files loop would trip over a deck binary in the corpus), `::test_r001_stable_across_rebuild`.
- The module ledger gains `R-002` (fine, append-only) but the module Library board then mixes a
  swim-lane report and a weekly report under one record's front door.

**Verdict.** Route (b) trades one architectural invariant ("one builder per byte-stable corpus" —
the boundary this repo deliberately preserves *at the ledger layer*, `modulesite.py:178`,
`worksurface.py:415`) for ~16 individually-trivial edits that are **cheap once enumerated and
expensive only when discovered late**. They are enumerated above. Route (a) wins.

### The lineage link — reuse the module's lane config, do not duplicate it

`build_weekly_report(load, author=..., bindings=...)` takes `bindings: Sequence[SectionBinding]`
from `swimlane.load_swimlanes`. Rather than fabricate a second lane config, the weekly builder
should load **the committed `content/module/*.yml`**:

- it is literally "the weekly for the module in `content/module`" — the seed's "lineage" wording;
- it **already declares a KPI-less lane** (`MOR/IQ tools & defect projects`), which is honesty-path
  row 1 for free, with zero new fabricated content [VERIFIED: executed — see §The Honesty-Path Fixture];
- one fabricated module, one source of truth (this repo's anti-duplication norm: `specspan`,
  `compose_kpi_item`, `normalize_opc_zip` were all promoted for exactly this reason);
- coupling risk is bounded and loud: a change to `module-a.yml` moves both corpora's committed HTML
  and **both** committed==fresh gates go red in the same run.

Discovery stays generic (LANE-03): `sorted((root/"content/module").glob("*.yml"))[0]`, mirroring
`modulesite._discover_config` — no fixture filename in source.

## The Deck in the Corpus

**Recommendation: `content/weekly/deck/` — a corpus artifact, NOT a served page.**

### Where it lives

```
content/weekly/
├── weekly-<week>.yml              # the ONE root *.yml — discovered by sorted glob
├── template.pptx                  # the operator-supplied template (byte-copy of the committed
│                                  #   synthetic fixture; P-06: copied, never regenerated)
├── inbox/<name>.eml               # the synthetic recognition source
├── assets/<name>.png              # the one placed asset
├── ids.json                       # own append-only ledger — R-001
├── deck/
│   ├── weekly-<week>.pptx         # produced BY THE WRITER (never by re-saving the template)
│   └── weekly-<week>.pptx.digest  # the committed part_digest, one hex line
└── site/                          # the ONLY thing publish.assemble_site copies
    ├── weekly-<week>.html
    ├── library.html
    └── fonts/…
```

`assemble_site` copies `content/*/site` only, so a deck under `deck/` **cannot** reach the
published tree — the "nothing publishes" half of SC-3 holds structurally, not by discipline.

**`template.pptx` in the corpus, with a byte-equality guard.** `src/` must not read from `tests/`,
and the recipe must be able to point at a real template. Copy
`tests/fixtures/weekly/template.pptx` → `content/weekly/template.pptx` and add a one-line test
asserting the two are byte-identical, so P-06 ("the fixture template is not regenerated") holds on
both copies and neither can drift. [CITED: `.planning/phases/02-renderer/02-VALIDATION.md` P-06/P-07]

### The two-tier committed==fresh gate for a binary

The recorded determinism decision is explicit: *"the committed==fresh gate asserts the
**part-content digest** — sha256 over sorted `(part name, sha256(part bytes))` — which is
implementation-independent"*, because DEFLATE output varies between zlib and zlib-ng.
[CITED: `.planning/notes/2026-08-29-pptx-determinism-decision.md`]

| Tier | Assertion | Needs `[pptx]`? | Runs in |
|------|-----------|-----------------|---------|
| **1 — tamper** | `part_digest(committed_deck_bytes) == committed .digest` | **No** — `part_digest` is stdlib (`zipfile` + `hashlib`) and `pptx_writer`'s module level is stdlib-only | every install, incl. `site-integrity` and bare |
| **2 — drift** | `part_digest(fresh render) == part_digest(committed deck)` | **Yes** (rendering needs python-pptx) | the `weekly` (or `pptx`) CI job only |

**Measured today, in this repo:** two renders of the prototype weekly separated by a real
`time.sleep(3)` gave `bytes_a == bytes_b → True` and `part_digest equal → True`
(`5d960e38…e13b3b`, 28,774 bytes). [VERIFIED: executed with `.venv/bin/python`]

⚠️ **The trap the planner must not fall into.** `tests/test_publish.py::_assert_committed_equals_fresh`
compares `read_bytes() == read_bytes()` over **every** file under a corpus dir. If the deck ever
lands inside `content/weekly/site/`, that loop (a) demands the HTML-only builder produce it and
(b) compares raw zip bytes across environments — a cross-zlib false red. Keeping the deck out of
`site/` avoids both without an exclusion clause.

### Should the site link the deck for download?

**Recommendation: no, this phase.** Cost of the alternative, costed honestly:

- `render._block_html` escapes every text field (`_e()`); there is no raw-HTML block except
  `DiagramBlock.svg`, which the `AssetBlock` branch explicitly refuses as a precedent
  (`render.py:669-672`). So a `<a href="…pptx">` cannot be authored through existing block text.
- **There is a zero-CSS route if it is ever wanted:** `FanoutBlock` → `_fanout_row` renders
  `link.href` verbatim as `<a class="lib-title" …>` (`render.py:475-486`), and `worksurface.py`
  already uses `FanoutBlock`. A `FanoutLink(kind="deck", title="…", href="weekly-<week>.pptx")`
  would produce a real download link with **no render.py change and no new CSS**.
- But it forces the deck into `content/weekly/site/` (so
  `test_assembled_internal_links_resolve` can resolve it), which re-opens the byte-comparison trap
  above and force-pushes a 28 KB binary to `gh-pages` on every publish.

No success criterion asks for a downloadable deck; SC-1 asks it *render*, SC-3 asks it ship Draft +
watermarked. **An unlinked, unserved file is not a dead link** — PUB-03's no-dead-end rule is about
hrefs in published HTML. Record the `FanoutBlock` route as the cheap upgrade path (round two,
alongside deck images) rather than building it.

## Ledger / ID Convention

**The weekly reuses `R-NNN` in its own `content/weekly/ids.json`, starting at `R-001`.**
[VERIFIED: prototype assigned `R-001`]

Reasoning, from live code:
- `site._REF_FORMAT` maps `report → "R-{:03d}"`; the ref format is keyed on **`Surface.kind`**
  (`Ledger.ref_for(slug, surface.kind)`), and `build_weekly_report` returns
  `Surface(template=REPORT)` — kind `"report"`. A `W-` prefix would require a new template kind,
  which contradicts milestone decision **D-01** ("Reuse `Surface(REPORT)`. The PPTX renderer is an
  output *format*, not a new semantic kind"). [CITED: `docs/weekly-spec.md`, `.planning/ROADMAP.md`]
- The per-corpus precedent is exact: `content/rev1/ids.json`, `content/work/ids.json`
  (`R-001`), `content/module/ids.json` (`R-001`) — three ledgers, each restarting at `R-001`;
  `worksurface.py:415` and `modulesite.py:178` both state the corpus boundary is preserved *at the
  ledger layer*. `docs/surfaces.md:231` fixes `Report → R-NNN … sequential per type`.
- Slug: `build_weekly_report` derives `id = f"weekly-{slugify(stem).removeprefix('weekly-') or 'spec'}"`
  → for `weekly-2374-w35.yml` the id is `weekly-2374-w35`, so the page is
  `weekly-2374-w35.html`. Slug-clean, so `Site.from_surfaces` uses it directly.
- **Append-only invariant:** `build_weekly_site` must be the SOLE ledger writer (load → build Site →
  `ledger.save()`), and — per `modulesite.py`'s documented shared-ledger caveat — it saves to the
  **fixed committed path**, not `out_dir`. Tests that build into `tmp_path` must snapshot
  `content/weekly/ids.json` and assert it is byte-unchanged.

## The Honesty-Path Fixture

Every string below was produced by running the live loader/composer on a prototype corpus.
[VERIFIED: executed, 2026-08-29]

### What each planted absence needs, and the exact `missing[]` text it produces

| # | SC-1 requirement | How to plant it | Exact `missing[]` entry (verbatim from execution) | Owner in code |
|---|---|---|---|---|
| 1 | **a lane with no KPIs** | a `lanes:` entry in the bound module config with no `kpis:` key — **already present** in `content/module/module-a.yml` (`MOR/IQ tools & defect projects`) | `section 'MOR/IQ tools & defect projects' declares no KPIs — strip omitted` | `compose.NO_KPIS`, appended by `build_weekly_report`'s binding loop |
| 2 | **a recognition with no source email** | a `recognitions:` entry with `person` + `reason` and **no** `source:` | `field 'recognitions[1].source' is absent or empty — disclosed, never fabricated` | `weeklyspec._resolve_recognition_evidence` → `specspan.absent` |
| 3 | **an asset with no provenance** | an `assets:` entry omitting one of `folder`/`date`/`event` | `asset 'crew-manifest-scan': provenance field 'folder' is absent — the minimum is folder + date + event label; disclosed, never placed` | `weeklyspec._ASSET_PROVENANCE_ABSENT` via `_place_assets` |

Two more rows come along for free from the reused module config and are worth keeping (they make
the panel read like a real week, not a demo): `KPI 'defect-rate' declares period movement but only
one endpoint is usable — no delta derived (never a fabricated 0)`.

**Routing order matters and is already correct:** provenance is checked *before* the file read, so
the no-provenance asset needs **no file on disk** (the existing `weekly-full.yml` fixture relies on
exactly this — it names three assets and commits one PNG). [VERIFIED: executed]

### The contrast that makes the honesty path non-vacuous

Plant a **second** recognition **with** a `source:` that resolves. Without `known_sources`, a
`source:` id produces the *unresolvable* disclosure instead:

```
recognition for "…": source '…' does not resolve to a known Source — carried, with the
unresolvable id disclosed
```

Passing the parsed `.eml` `Source` as `known_sources=[src]` flips it to real evidence:
`recognition: <person> | evidence: ['content/weekly/inbox/rota.eml']`, and the unresolvable line
disappears from `missing[]`. [VERIFIED: executed both ways]

**The `.eml` is worth including.** `EmailAdapter().parse(raw, path)` is **stdlib-only and pulls no
optional extra** (verified: importing `newsletters.adapters.email_adapter` leaves `openpyxl`,
`pptx`, `yaml` absent from `sys.modules`), so it adds **no CI extra** to the merge-block or deploy
jobs, and it makes the `.eml` drop in `docs/weekly.md` demonstrable against the shipped sample.

### The `.xlsx` — do NOT put it in the corpus build path

WKLY-04's values-via-export is already proven by `tests/test_weekly_values.py` (workbook authored
in-memory with openpyxl, never committed — the module's own stated fixture policy). Feeding the
sample corpus from an `.xlsx` would make `build_weekly_surfaces()` require `[excel]`, which
`newsletters check --corpus weekly` runs in **both** the `merge-block` CI job and the
**deploy-pages** gate — neither installs `[excel]`. Keep bindings on the YAML lane path
(`[config]` only, already installed in both). SC-1 does not ask for values-via-export in the
sample. Describe the workbook route in the recipe instead.

### Fixture content rules

- Fabricated, Star-Trek-flavoured, LANE-03-safe — matching `tests/fixtures/weekly/weekly-full.yml`'s
  stated policy. Do **not** reuse names on `tests/test_abstraction_guard.py`'s `_SAMPLE_TEAM_NAMES`
  or `tests/test_modulesite.py::_REAL_LOOKING_LITERALS` denylists (`Jean-Luc Picard`, `USS Enterprise`,
  `Warp Core Stability`, …). The existing weekly fixtures use `Miles O'Brien` / `Kira Nerys` /
  `Julian Bashir`, none of which is on either list.
- **The `.eml` collides with the confidentiality scanner.** `tests/test_modulesite.py::_EMAIL_RE`
  (`\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b`) treats any email address as a real-name *shape*. A weekly
  corpus containing an `.eml` will carry `From:`/`To:`/`Message-ID:` addresses. Use RFC 6761
  reserved `@example.invalid` and make the weekly's scan allow that exact domain (or exclude
  `inbox/*.eml` from the address scan and scan it against the *name* denylist only). This is the
  single most likely "green turns red for a surprising reason" in the phase.
- **Grow the abstraction guard** (CONTEXT discretion, explicitly logged): add the new corpus's
  fabricated ids to `tests/test_abstraction_guard.py`'s denylist so a future leak into `src/` fails
  loudly. The guard scans `src/` only, so the corpus's own use of those names is safe.
- **Confidentiality scanner: promote, don't copy.** `test_modulesite.py::test_committed_content_is_synthetic`
  is a corpus-parameterisable scanner living in one module. This repo's norm is promotion over a
  second copy (`specspan.SpanMinter`, `compose.compose_kpi_item`, `pptx_writer.normalize_opc_zip`
  were all promoted for exactly this reason). Recommend lifting the denylist + `_scan_real_looking`
  into a shared `tests/_corpus_scan.py` used by both modules. *Alternative if scope discipline
  wins:* a self-contained weekly scanner, accepting the two-copies drift and saying so in the plan.

## Standard Stack

**No new packages.** Every dependency this phase needs is already declared and installed.

### Core (all already present)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | `>=2` | typed spine (`Surface`/`Claim`/`Trace`) | core runtime dep, non-AI |
| typer[all] | (unpinned) | CLI | core runtime dep; `newsletters = "newsletters.cli:app"` |

### Supporting (extras, all already declared)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyYAML | `>=6.0.3` (`[config]`) | `safe_load` for the Weekly Spec + lane config | needed by `newsletters check --corpus weekly`; already installed in `merge-block`, `site-integrity`, `deploy-pages`, `weekly` |
| python-pptx | `>=1.0.2` (`[pptx]`) | deck render | needed only by the deck path; installed in the `pptx` + `weekly` jobs |
| openpyxl | (`[excel]`) | ADAPT-03 workbook route | **recipe only** — must not enter the corpus build path |
| pytest | (`[test]`) | the gate | every job |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sibling `content/weekly/` | extend `content/module` | ~16 fewer edits, but two builders in one byte-stable corpus (CONTEXT's stated disqualifier) — see §Corpus Placement Decision |
| deck under `content/weekly/deck/` | deck under `…/site/` + `FanoutBlock` download link | satisfies "linkable" literally; costs a byte-comparison exclusion in the committed==fresh loop and publishes a binary to gh-pages |
| one `newsletters weekly` command | `newsletters weekly compose\|render` sub-app | more CLI surface + more tests for no SC gain |
| one `newsletters weekly` command | no new command, recipe uses `python -c …` | fails SC-4's "commands that match the shipped CLI" in spirit |

**Installation:** none. `pip install '.[test,config,pptx]'` is the existing dev shape.

## Package Legitimacy Audit

**Not applicable — this phase installs no external package.** No `pip install`, no new entry in
`[project.optional-dependencies]`, no new import of a third-party module. Verified against
`pyproject.toml` (unchanged by this phase's plan) and by the fact that every mechanism the phase
uses was executed today with the existing `.venv`.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

If a plan proposes any new dependency, that is a scope escape — stop and re-run the legitimacy gate.

## Architecture Patterns

### System Architecture Diagram

```
 AUTHORED / SYNTHETIC INPUTS (content/, read-only)
 ┌───────────────────────────┐  ┌──────────────────────┐  ┌───────────────────┐
 │ content/weekly/*.yml      │  │ content/weekly/      │  │ content/module/   │
 │  (the Weekly Spec)        │  │  inbox/*.eml         │  │  *.yml (lanes —   │
 │  + assets/*.png           │  │                      │  │  the lineage link)│
 └────────────┬──────────────┘  └──────────┬───────────┘  └─────────┬─────────┘
              │ read_text (UTF-8, LF)      │ read_bytes             │ read_text
              ▼                            ▼                        ▼
   load_weekly_spec(root=…)      EmailAdapter().parse()      load_swimlanes()
   • Source(EPOCH_ZERO)          • Source (Date header)      • SectionBinding[]
   • SpanMinter → Claims           └──── known_sources ──┐     (incl. a KPI-less lane)
   • _place_assets: provenance →                        │             │
     AssetBlock  ── or ──► missing[]                    │             │
              │                                         │             │
              └──────────────► build_weekly_report(load, author=…, bindings=…) ◄┘
                                            │
                    Surface(REPORT, Draft, created=EPOCH_ZERO)
                    blocks: prose · kpi* · claims · narrative×2 · recognitions · team · asset*
                    missing[]: the honesty panel  ── the gate is NEVER touched
                                            │
                    ┌───────────────────────┴────────────────────────┐
                    ▼ (HTML branch — [config] only)                  ▼ (deck branch — [pptx])
        Ledger.load(content/weekly/ids.json)                weekly_slots(load, surface)
                    │  ref_for(slug,"report") → R-001               │  4 × NL_ keys, fixed order
        Site.from_surfaces([surface])                       render_surface_pptx(
                    │  ledger.save()  ← SOLE writer            template=content/weekly/template.pptx,
                    ▼                                          out_path=content/weekly/deck/…)
        render_surface → weekly-<week>.html                          │
        render_library(records=…) → library.html              normalize_opc_zip → one atomic write
        _emit_fonts → fonts/                                         │
                    ▼                                                ▼
        content/weekly/site/  ────────────────┐          content/weekly/deck/<slug>.pptx
                                              │                      + <slug>.pptx.digest
   publish.assemble_site (byte-copy only) ◄───┘          (NOT copied by assemble — never published)
        rev1→/ · work→/work · module→/module · weekly→/weekly
        + .nojekyll + 404.html (the only fresh render)
                    │
                    ▼
        CI: merge-block (check ×4) · site-integrity (test_publish + corpus tests)
            weekly job ([config,excel,pptx], fetch-depth 0, 0-skipped assertion)
                    │
                    ▼  main only, human-merged
        deploy-pages: gate 1 (check ×4) → gate 2 (test_publish) → assemble → gh-pages
```

### Recommended Project Structure

```
src/newsletters/
└── weeklysite.py          # NEW — the corpus builder seam (mirror of modulesite.py)
content/weekly/            # NEW — the corpus (layout in §The Deck in the Corpus)
tests/
├── test_weeklysite.py     # NEW — HTML corpus: no [pptx] → safe in site-integrity
└── test_weekly_golden.py  # NEW — deck: [pptx]-gated → weekly job only
docs/weekly.md             # NEW — the WKLY-06 operator recipe
```

### Pattern 1: The corpus builder seam
**What:** a top-level sibling module that wires loader → composer → ledger → renderer over a
committed corpus. Never in `compose.py` (a COMP-contract leaf that must not import `render`/`site`).
**When to use:** any new committed content family.
**Example** (`src/newsletters/modulesite.py:174-216`, the shape to mirror):
```python
out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
surfaces = build_module_surfaces(config_path, root=root)
ledger = Ledger.load(_LEDGER_PATH)          # the FIXED committed path, never out_dir
site = Site.from_surfaces(surfaces, ledger=ledger)
ledger.save()                                # SOLE writer; compose only reads/assigns
for page in site.pages():
    (out / page.href).write_text(
        render_surface(page.surface, site=site, page=page, home_href="../index.html"), "utf-8")
library.write_text(render_library(site, records=(...), home_href="../index.html"), "utf-8")
worksurface._emit_fonts(out)                 # zero-edit reuse; zero external call
```

### Pattern 2: Structural discovery, never a fixture filename in `src/`
**What:** the builder discovers its config by a sorted glob, so no config-specific name lands in
source (LANE-03 / the abstraction guard).
**Example** (`modulesite._discover_config`): `sorted(corpus.resolve().glob("*.yml"))[0]`, raising a
teaching `FileNotFoundError` when the corpus is unpopulated. `Path.glob` is **non-recursive**, so a
root-level spec and a `lanes/`-style subdirectory never collide.

### Pattern 3: Two-tier assertion for a committed binary
**What:** a stdlib-only tamper check everywhere; an extra-gated drift check where the extra exists.
**Why:** `part_digest` is implementation-independent (sorted `(name, sha256(part))` rows,
length-prefixed to close the WR-01 collision) while raw zip bytes are zlib-dependent.
```python
# tier 1 — no [pptx] needed; runs on every install
assert part_digest(DECK.read_bytes()) == DIGEST.read_text().strip()
# tier 2 — [pptx]-gated; the weekly CI job
fresh = render_surface_pptx_bytes(surface, template=TEMPLATE, slots=slots)
assert part_digest(fresh) == part_digest(DECK.read_bytes())
```

### Pattern 4: CLI corpus selector routes the builder, never forks the gate
**Example** (`cli.py:167-178`): `check` picks a `build_*_surfaces()` by `--corpus`, then runs the
**one** `review.review_blockers` over whatever it got (T-11-13). Adding `weekly` is two `elif`s
plus an enum member plus a `_DEFAULT_OUT` entry — nothing else.

### Anti-Patterns to Avoid
- **Rendering the deck inside `build_weekly_site`.** It would drag `[pptx]` into
  `site-integrity` (installs `[test,config]`) and into the deploy gate. Keep HTML and deck on
  separate entry points.
- **Putting a `[pptx]`-gated test in a module the `site-integrity` job runs.** That job has **no
  `0 skipped` assertion**, so the test would skip silently — the exact W21 shape ("a green that
  means 'not run'") this repo has already paid for twice.
- **Comparing the committed deck to the template.** python-pptx's *load* path re-serializes empty
  core properties and re-orders parts; the golden deck must come from the **writer**.
  [CITED: `.planning/phases/02-renderer/02-03-SUMMARY.md`]
- **Sizing the chrome regen from `grep -rl nl-records content/`** (17 files — the CSS class is on
  every page). The strip markup is on 4.
- **Hand-editing a committed corpus file.** Regenerate via `newsletters build --corpus …` in the
  same commit as the change; drift is a stop-the-line bug.
- **Letting a builder write the ledger to `out_dir`.** The committed path is the contract; tests
  snapshot it and assert byte-equality after a `tmp_path` build.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "is this deck the same deck?" | a full-file sha256, or an XML normalizer | `pptx_writer.part_digest` | zlib-implementation-independent; length-prefixed rows close a real name-collision spoof (WR-01); already tested |
| zip metadata determinism | a custom re-zip | `pptx_writer.normalize_opc_zip` | the promoted, single normalizer; a second copy drifts (the reason the fixture copy was deleted) |
| "why do these two decks differ?" | ad-hoc diffing | `differing_parts` / `differing_zipinfo_fields` | already written, already tested, gives a teaching answer |
| span-traced claims from authored YAML | a new minter | `specspan.SpanMinter` via `load_weekly_spec` | forward-only cursor; file order is a *correctness* condition (a value repeated in two sections silently swaps spans otherwise) |
| a disclosure string | a new sentence | `specspan.absent` / `compose.NO_KPIS` / `weeklyspec._ASSET_*` | one rule, one wording — the honesty panel must read consistently; `dedup_in_order` already de-duplicates |
| self-hosted fonts in a new corpus | re-vendoring woff2 | `worksurface._emit_fonts(out)` | copies the canonical rev1 set + OFL licenses; zero external call for free |
| ref assignment | a counter | `site.Ledger.ref_for` | append-only, immutable on re-sight, byte-stable JSON |
| "is this corpus synthetic?" | a fresh regex | promote `test_modulesite`'s scanner | it already has a **planted-leak self-check** proving it is non-vacuous |
| YAML parsing | `yaml.load`, or a second `try: import yaml` | `_yaml_loader.load_config` | `safe_load` only, behind the lazy `[config]` boundary; config is data, not code |
| the base commit for a diff gate | `git diff HEAD` | `conftest.milestone_base_ref` | `git diff HEAD` compares the *working tree*, so it is green in every clean CI checkout — a bug that already shipped once here |

**Key insight:** every trust primitive this phase needs was written, reviewed and hardened in
Phases 1–3 *specifically so Phase 4 could inherit it*. A hand-rolled equivalent is not just extra
work — it re-opens a closed review finding.

## Common Pitfalls

### Pitfall 1: The missed integration point
**What goes wrong:** the corpus lands, tests pass locally, and CI or the deploy workflow goes red on
a wiring site nobody listed (fonts tuple, deploy gate line, a stale "three corpora" doc).
**Why:** the wiring is spread across 6 files + 2 workflows + 4 docs, and `assemble_site` fails
*loud but late* (`FileNotFoundError` before any write).
**How to avoid:** work §Integration Point Inventory as an explicit checklist artifact in the plan;
after wiring, re-run `newsletters assemble --out /tmp/x` and `pytest tests/test_publish.py` before
claiming green.
**Warning signs:** `test_fonts_referenced_are_present` failing on a `fonts_dir` that does not exist.

### Pitfall 2: The `[pptx]` skip that reads as green (W21, the third time)
**What goes wrong:** a deck test lands in a module run by `site-integrity`, which installs only
`[test,config]` and has **no skip assertion**; the test skips forever.
**How to avoid:** two test modules, split by extra requirement (§Recommended Project Structure);
put the deck module in the `weekly` job, whose step greps `[0-9]+ skipped` and fails.
**Warning signs:** an `s` where a `.` was expected in the CI log.

### Pitfall 3: Comparing the committed binary by raw bytes
**What goes wrong:** the gate passes locally and fails on a runner with a different zlib.
**How to avoid:** `part_digest` for every `.pptx` assertion; never `read_bytes() == read_bytes()`
on a zip. Keep the deck out of any directory that a byte-loop walks.

### Pitfall 4: The email address trips the confidentiality scanner
**What goes wrong:** the synthetic `.eml`'s `From:` header matches `_EMAIL_RE`, and the
"committed content is synthetic" test fails on a *deliberately* synthetic file.
**How to avoid:** `@example.invalid` (RFC 6761 reserved) plus an explicit allowance in the weekly
scanner, stated in the test's docstring so the exception is legible rather than mysterious.

### Pitfall 5: The chrome regen is done by hand
**What goes wrong:** the Records strip is edited into a committed HTML file, and committed==fresh
goes red (or, worse, drifts undetected until the next regen).
**How to avoid:** edit the builder constant, then run `newsletters build --corpus {rev1,work,module}`
and commit the 4 regenerated chrome pages **in the same commit** as the constant.

### Pitfall 6: Ledger mutation from a `tmp_path` build
**What goes wrong:** `build_weekly_site(tmp_path)` re-saves the **committed** `ids.json` (documented
`modulesite` caveat). Harmless while idempotent — a stop-the-line bug the moment it is not.
**How to avoid:** every test that builds into `tmp_path` snapshots `content/weekly/ids.json` bytes
first and asserts they are unchanged after (`test_modulesite.py:264-268` is the exact idiom).

### Pitfall 7: The `weekly` corpus's `newsletters check` is vacuously green
**What goes wrong:** `review_blockers` returns `[]` immediately for any non-Published surface
(`review.py:94-96`), and the sample is **Draft by design** — so `check --corpus weekly` exits 0
without checking anything, and a reader mistakes the wiring for a proof.
**How to avoid:** wire it anyway (consistency + the gate must exist before it is ever needed), and
say so plainly in the plan and the docs. The real trust proof for this corpus is the honesty-panel
test, not the merge-block exit code. `test_module_cli.py:75-91` shows the existing idiom for
proving the gate *blocks* (monkeypatch a surface to Published, assert nonzero) — mirror it.

### Pitfall 8: The weekly Surface carries only the spec `Source` in `traces`
**What goes wrong:** `build_weekly_report` sets `traces=[load.source]`. Claims contributed by
`bindings` (from the module lane config) and by a resolved `.eml` recognition therefore reference
Sources the Surface does not carry.
**Consequences, measured:** *not* a rendering break — `Claim.is_stale` skips a `source_id` absent
from the lookup (no false STALE, `semantic.py:212-216`), and `link_for_source` renders a repo-blob
`https://…` link for a path-shaped locator, which the assembled-link test excludes. Verified: the
rendered page contains **no** `href="None"`.
**Why it still matters:** if this corpus were ever advanced to Published, a lane-config drift would
be invisible to `review_blockers`. Record it as a known limitation of the Draft sample; do **not**
change `weeklyspec.build_weekly_report` in this phase (Phase 3 code is frozen and reviewed).

## Code Examples

### Compose the sample weekly (the exact call shape, executed)
```python
# Source: verified by execution against src/newsletters/ (2026-08-29)
from newsletters.adapters.email_adapter import EmailAdapter
from newsletters.swimlane import load_swimlanes
from newsletters.weeklyspec import load_weekly_spec, build_weekly_report, weekly_slots

eml = Path("content/weekly/inbox/rota.eml")
src, _units, _unex = EmailAdapter().parse(eml.read_bytes(), eml.as_posix())

load = load_weekly_spec(spec_path, root=repo_root, known_sources=[src])
swim = load_swimlanes(module_config, root=repo_root)     # the content/module lineage link
surface = build_weekly_report(load, author=author, bindings=swim.bindings)
# → Surface(id='weekly-2374-w35', gate=draft, created=EPOCH_ZERO)
# → blocks: prose, kpi×4, claims, narrative, narrative, recognitions, team, asset
slots = weekly_slots(load, surface)   # {'NL_WEEK_TITLE','NL_MODULE','NL_HIGHLIGHTS','NL_LOWLIGHTS'}
```

### The deck, and the digest that gates it
```python
# Source: src/newsletters/pptx_writer.py + .planning/notes/2026-08-29-pptx-determinism-decision.md
from newsletters.pptx_writer import render_surface_pptx, render_surface_pptx_bytes, part_digest

render_surface_pptx(surface, template=TEMPLATE, slots=slots, out_path=DECK)   # one atomic write
DIGEST.write_text(part_digest(DECK.read_bytes()) + "\n", encoding="utf-8")
# measured: two renders 3s apart → bytes equal AND part_digest equal (28,774 bytes)
```

### Records strip — the assembled-tree-relative idiom
```python
# Source: src/newsletters/modulesite.py:199-210 (a subdir corpus declares its neighbours)
render_library(site, records=(
    ("The Rev1 record",   "../index.html"),
    ("The work record",   "../work/library.html"),
    ("The module record", "../module/library.html"),
), home_href="../index.html")
```

## `docs/weekly.md` — Shape and Honest Commands

### The pattern to follow
`docs/architecture.md` §"the WORK-01 flow" (lines 220–252) is the repo's operator-recipe shape:
**numbered steps, each naming the exact function/command, each stating the trust property it
preserves** (read-only, data local, no network, no auto-publish). `docs/case-spec.md` (3 headings:
*Writing one* / *What happens to it*) is the authoring-doc shape. `docs/weekly-spec.md` is the
**authoring contract** and must not be duplicated — `docs/weekly.md` links to it.

Recommended headings:

1. **What you need** — a template deck (`.pptx` with named shapes), a workbook export (optional),
   an `.eml` drop (optional), a photo folder (optional). *Everything stays on your machine.*
2. **Install** — `pip install '.[config,pptx]'`; `[excel]` only if you use a workbook. Bare install
   is AI-free.
3. **Prepare the template** — Selection Pane names must start with `NL_`; the writer fills the
   operator's **existing** slides and never invents layout; an unmatched name in either direction
   fails loud. **Carried P-07:** set `word_wrap=True` / `auto_size=NONE` on your text boxes, or
   long lines overflow the slide silently. **Carried IN-07:** slots are looked up on document
   slides; layout/master placeholders are not walked.
4. **Author the Weekly Spec** — link `docs/weekly-spec.md`; show the eight keys; state rule 4
   (absences are disclosed, never fabricated) and rule 7 (a path escaping the root **raises**).
5. **Point the read-only adapters at your data** — `.eml` drop → `EmailAdapter().parse`;
   workbook → the existing ADAPT-03 `excel` adapter (export the BI view to `.xlsx`; there is no CSV
   reader and no Power BI value reader — WKLY-04/ADAPT-05 scope, stated plainly); photos →
   `assets:` records with folder + date + event (deep link **required** for a values screenshot).
   *Read-only, no network, nothing committed.*
6. **Compose + render** — the commands (below).
7. **Review** — open the HTML, read the honesty panel, check the deck's Draft watermark; the
   `Draft › In Review › Published` gate is the only way out, and it needs a human.
8. **What the sample looks like** — point at `content/weekly/` as the worked example.

### Command inventory: what exists vs what must be added

| Recipe step | Command | Status |
|---|---|---|
| Render the corpus HTML | `newsletters build --corpus weekly --out …` | **needs the `--corpus weekly` wiring** (rows 4–6 of the inventory) |
| Gate the corpus | `newsletters check --corpus weekly` | **needs row 7** (and is vacuous for Draft — Pitfall 7) |
| Assemble the site | `newsletters assemble --out dist/site` | exists |
| **Render an operator's deck** | *nothing today* | **needs a new command** |

**Recommendation: one new command, `newsletters weekly`.** Smallest addition that makes SC-4's
"copy-pasteable commands that match the shipped CLI" literally true, consistent with `cli.py`'s
idioms (a flat `@app.command()`, `typer.Option` with help text, **lazy imports inside the body**,
echo each written path then a summary line):

```
newsletters weekly --spec content/weekly/weekly-2374-w35.yml \
                   --lanes content/module/module-a.yml \
                   --template content/weekly/template.pptx \
                   --author "your-name" \
                   --out content/weekly/deck/weekly-2374-w35.pptx
```

- lazy-imports `weeklyspec` + `pptx_writer` so the bare install stays light and the existing
  teaching `ImportError` (`pip install '.[pptx]'`) is the one that fires;
- `--out` is **caller-supplied**, never derived from Surface content (threat T-02-08 path traversal,
  stated in `render_surface_pptx`'s docstring — keep that property);
- also writes the `.digest` sidecar, so regenerating the sample is one command;
- test idiom: `typer.testing.CliRunner`, per `tests/test_module_cli.py`.

*Rejected:* a `weekly compose|render` Typer sub-app (more surface, more tests, no SC gain); no new
command at all (a `python -c` in the recipe is copy-pasteable but is not "the shipped CLI").

### SC-4 — "verified by executing them against the synthetic corpus"

Two complementary proofs; the repo has precedent for both:
1. **A doc-contract test** (`tests/test_collaboration_contract.py` is the presence-guard idiom):
   assert every fenced `newsletters …` command line in `docs/weekly.md` names a command/option that
   the live Typer app exposes — so a renamed flag turns the suite red instead of rotting the doc.
2. **Execution in the plan itself**: run each documented command against `content/weekly/` during
   the phase and paste the output into the plan summary. CONTEXT: *"copy-pasteable = actually
   pasted"*.

## Runtime State Inventory

Not a rename/refactor/migration phase — **section omitted by design.** For completeness, the two
pieces of state this phase *does* touch, both in-repo and both gated:
`content/weekly/ids.json` (new, append-only, `R-001`) and the four regenerated chrome HTML pages.
No datastore, no OS registration, no secret, no external service.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | ✓ | 3.11 in `.venv` (CI pins 3.12) | — |
| pytest | the gate | ✓ | via `.venv` | — |
| PyYAML (`[config]`) | spec + lane load | ✓ | installed | none — the corpus cannot build without it |
| python-pptx (`[pptx]`) | deck render | ✓ | `>=1.0.2` floor pin | tier-1 digest check still runs without it |
| openpyxl (`[excel]`) | recipe only | ✓ | installed | not on the corpus path by design |
| import-linter | PKG-04 gate | ✓ | `.venv/bin/lint-imports` | — |
| mypy / black / isort | baseline gates | ✓ | `.venv/bin/*` | — |
| git with `origin/main` reachable | `conftest.milestone_base_ref` diff gates | ✓ locally; CI needs `fetch-depth: 0` | — | **none — it FAILS rather than skips, by design** |
| a real PowerPoint client | "the deck opens" | ✗ | — | carried to PR review (Phase 2/3 carry, unchanged) |

**Missing dependencies with no fallback:** none for the automated gates.
**Missing with fallback:** real-PowerPoint open → human confirmation at PR (already a carried item).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (`[tool.pytest.ini_options]`: `pythonpath=["src"]`, `testpaths=["tests"]`) |
| Config file | `pyproject.toml` §78-80; shared fixtures in `tests/conftest.py` |
| Quick run command | `.venv/bin/python -m pytest tests/test_weeklysite.py -q` |
| Full suite command | `.venv/bin/python -m pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| WKLY-05 | the sample composes to a Draft `Surface(REPORT)` at `EPOCH_ZERO`, every claim traced + content-addressed | unit | `pytest tests/test_weeklysite.py -k traced_and_addressed -x` | ❌ Wave 0 |
| WKLY-05 | **honesty path**: the 3 planted absences appear in `missing[]` **and** are `html.escape`d into the rendered honesty panel | integration | `pytest tests/test_weeklysite.py -k honesty_panel -x` | ❌ Wave 0 |
| WKLY-05 | committed `content/weekly/site/` == a fresh build, byte-for-byte; committed ledger unchanged | integration | `pytest tests/test_weeklysite.py -k committed_equals_fresh -x` | ❌ Wave 0 |
| WKLY-05 | byte-stable double render of the HTML corpus | integration | `pytest tests/test_weeklysite.py -k byte_stable -x` | ❌ Wave 0 |
| WKLY-05 | `R-001` stable across a rebuild (fresh tmp ledger) | unit | `pytest tests/test_weeklysite.py -k r001 -x` | ❌ Wave 0 |
| WKLY-05 | committed content is synthetic (denylist + planted-leak self-check, `.eml` addresses handled) | unit | `pytest tests/test_weeklysite.py -k synthetic -x` | ❌ Wave 0 |
| WKLY-05 | zero external calls in the weekly output (self-hosted fonts) | unit | `pytest tests/test_weeklysite.py -k external -x` | ❌ Wave 0 |
| WKLY-05 | **deck tier 1** — committed deck's `part_digest` == committed `.digest` (stdlib only) | unit | `pytest tests/test_weeklysite.py -k deck_digest -x` | ❌ Wave 0 |
| WKLY-05 | **deck tier 2** — fresh render `part_digest` == committed deck `part_digest` | integration (`[pptx]`) | `pytest tests/test_weekly_golden.py -k committed_deck -x` | ❌ Wave 0 |
| WKLY-05 (SC-3) | the deck reads back **Draft-watermarked** + marked, and rendering leaves the Surface `Draft` (full `model_dump()` before/after) | integration (`[pptx]`) | `pytest tests/test_weekly_golden.py -k draft -x` | ❌ Wave 0 |
| WKLY-05 (SC-3) | `content/weekly/template.pptx` bytes == `tests/fixtures/weekly/template.pptx` bytes (P-06 no-regeneration guard) | unit | `pytest tests/test_weeklysite.py -k template_copy -x` | ❌ Wave 0 |
| WKLY-05 (SC-2) | the assembled tree carries `/weekly/library.html` + the weekly page; every href resolves; fonts + OFL present; marker on every page | integration | `pytest tests/test_publish.py -q` | ✅ extend |
| WKLY-05 (SC-2) | Records strip on rev1 chrome names the weekly record | unit | `pytest tests/test_render.py -k records_strip -x` | ✅ extend |
| WKLY-05 (SC-2) | `newsletters check --corpus weekly` exits 0 clean **and** blocks when a surface is forced Published | unit | `pytest tests/test_weeklysite.py -k cli -x` | ❌ Wave 0 |
| WKLY-06 | every `newsletters …` command line in `docs/weekly.md` names a live command/option | unit | `pytest tests/test_weeklysite.py -k recipe_commands -x` | ❌ Wave 0 |
| WKLY-06 | `docs/weekly.md` carries the load-bearing anchors (read-only, data stays local, no auto-publish, `word_wrap`) | unit | `pytest tests/test_weeklysite.py -k recipe_anchors -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `.venv/bin/python -m pytest tests/test_weeklysite.py tests/test_publish.py -q`
- **Per wave merge:** `.venv/bin/python -m pytest -q` **plus** `lint-imports` **plus**
  `newsletters check --corpus {rev1,work,module,weekly}`
- **Phase gate:** the full §Gates Inventory, re-run independently, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_weeklysite.py` — the HTML-corpus suite (no `[pptx]` import anywhere in it)
- [ ] `tests/test_weekly_golden.py` — the `[pptx]`-gated deck suite (`requires_pptx` skipif idiom
      from `tests/test_weeklyspec.py:1454-1457`, **not** a module-level `importorskip`)
- [ ] `tests/_corpus_scan.py` (optional promotion) — the shared synthetic-content scanner
- [ ] No framework install needed; no `conftest.py` change expected

## Gates Inventory (SC-2 / SC-5)

Baselines **measured today on this branch**, so "no NEW failures" is checkable rather than
aspirational. [VERIFIED: executed 2026-08-29]

| # | Gate | Command | Baseline (today) | Phase-4 expectation |
|---|---|---|---|---|
| 1 | pytest | `.venv/bin/python -m pytest -q` | **837 passed, 0 skipped**, 1 warning, 19.6 s | > 837, still **0 skipped** |
| 2 | import contracts | `.venv/bin/lint-imports` | **2 kept, 0 broken** | unchanged |
| 3 | merge-block, all corpora | `newsletters check --corpus {rev1,work,module}` | all three: `All published surfaces clean — no blockers.` | **four** corpora clean |
| 4a | committed==fresh, HTML | `pytest tests/test_publish.py -q` + per-corpus tests | green | green incl. `content/weekly/site/` |
| 4b | committed==fresh, **`.pptx`** | tier 1 (stdlib) + tier 2 (`[pptx]`) `part_digest` | n/a (new) | both green; **never** raw-byte equality |
| 5 | bare-install | CI job `bare-install` (`pip install '.[test]'`) | untouched | **byte-untouched** — no new extra, no new top-level import |
| 6a | mypy | `.venv/bin/mypy src/newsletters` | **15 errors in 5 files**: `dogfood.py` 8, `weeklyspec.py` 3, `specspan.py` 2, `_yaml_loader.py` 1, `capture.py` 1 | no NEW error, and **0** in `weeklysite.py` |
| 6b | black | `.venv/bin/black --check src tests` | **69 would reformat / 29 clean** | no increase attributable to this phase |
| 6c | isort | `.venv/bin/isort --check-only src tests` | fails on several pre-existing files | no increase attributable to this phase |
| 7 | ledgers append-only | `git diff --exit-code -- content/*/ids.json` after a rebuild | clean | clean; the **new** `content/weekly/ids.json` is the only added ledger |
| 8 | gate freeze | `pytest tests/test_semantic_gate_frozen.py -q` (source-hash pins + zero-deleted-lines vs `merge-base`) | green | green — `semantic.py` untouched. **Needs `origin/main` reachable** (`fetch-depth: 0`) |
| 9 | abstraction guard | `pytest tests/test_abstraction_guard.py -q` | green | green with the denylist **grown** |
| 10 | deploy workflow | read the diff | main-only, 2 gates | gate 1 gains `--corpus weekly`; nothing else changes; **no push to `main` this phase** |

**Where SC-5's compass work lands:** `WHERE-WE-ARE.md` (newest-on-top state entry + the
decisions-and-why log: corpus placement, deck placement, ledger convention, the new CLI command),
`RETRO.md` (milestone friction + any rule hardened into a guard test), and the spec updates listed
in §Corpus Placement Decision.

## Commit / Wave Ordering (dependency-driven)

Some edits are only green *together* — `assemble_site` raises `FileNotFoundError` if a
`_CORPUS_LAYOUT` entry has no directory, and the Records-strip link test requires the target page to
exist in the assembled tree. Suggested atomic sequence:

1. **Builder + corpus + committed HTML + its own tests.** Safe alone: `assemble_site` ignores a
   directory it does not know about, so nothing else moves.
2. **Publish layout + CLI wiring + `test_publish` extensions + CI/deploy `check` lines.** Must land
   *after* (1) exists, and the layout edit + the fonts-tuple edit must land *together*.
3. **Records strips (×4 builders) + the 4 regenerated chrome pages + `test_render` assertion.** The
   constant edit and the regeneration are one commit or committed==fresh goes red.
4. **Deck + digest + `newsletters weekly` + the `[pptx]`-gated golden module + CI job edits.**
5. **`docs/weekly.md` + the doc-contract tests + `docs/architecture.md` / `docs/surfaces.md` /
   `CLAUDE.md` / `content/README.md` updates + `WHERE-WE-ARE.md` + `RETRO.md`.**

## Security Domain

ASVS level 1, `security_enforcement: true`. This phase adds no network surface, no authn/authz, no
user input path — it adds committed synthetic data, a builder, and a CLI command over local files.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard control |
|---------------|---------|------------------|
| V2 Authentication | no | no accounts, no sessions anywhere in the package |
| V3 Session Management | no | static site; renders without JavaScript |
| V4 Access Control | **yes (workflow-level)** | publishing is gated by PR review into `main` + the `Draft › In Review › Published` gate with a recorded reviewer; `deploy-pages.yml` is `if: github.ref == 'refs/heads/main'` and this phase adds no bypass |
| V5 Input Validation | **yes** | `yaml.safe_load` only (never `yaml.load`) via `_yaml_loader`; strict eight-key schema at both nesting levels with teaching errors; `_e()` HTML-escapes every interpolation in `render.py`; `slugify` restricts output to `[a-z0-9-]`, closing T-08-01 |
| V6 Cryptography | **yes (integrity only)** | `hashlib.sha256` for content addressing and `part_digest`; no secrets, no keys, nothing hand-rolled |
| V12 File & Resources | **yes** | root containment: `load_weekly_spec` and `_place_assets` `resolve()` then `relative_to(root)` and **raise** on escape (a refusal, never a `missing[]` entry); `render_surface_pptx`'s `out_path` is caller-supplied and never derived from Surface content (T-02-08) |
| V14 Configuration | **yes** | the `bare-install` job proves the deterministic spine runs with zero AI and zero extras; `lint-imports` forbids any core→AI edge |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard mitigation (already in place — do not weaken) |
|---------|--------|--------------------------------------------------------|
| YAML deserialization RCE | Elevation of Privilege | `safe_load` only, behind one lazy boundary |
| Path traversal via an authored `file:` / `photo:` / `--out` | Tampering | root containment raises; CLI out-path never derived from content |
| Zip member-name shadowing to spoof a digest | Tampering | `_reject_duplicate_member_names` + **length-prefixed** rows in `part_digest` (WR-01) |
| Content substitution (record describes image A, image B on disk) | Tampering | content address re-checked **at placement time**, not trusted from authoring |
| HTML/script injection through authored content | Tampering | every block field goes through `_e()`; `DiagramBlock.svg` is the sole raw interpolation and is explicitly refused as a precedent |
| Confidential data leaking into a public corpus | Information Disclosure | the synthetic-content scanner (denylist + email shape) with a planted-leak self-check; the recipe tells operators their data stays local |
| Unreviewed content reaching production | Repudiation / EoP | one publish channel; `assemble_site` copies **committed bytes only**; the gate is byte-frozen and source-hash pinned |
| Supply chain (new dependency) | Tampering | **no new package this phase** — see §Package Legitimacy Audit |

**No new threat is introduced by this phase.** The one new *asset class* is a committed binary
(`.pptx`), and its integrity control is the committed `part_digest` sidecar (tier 1), which detects
a hand-edited or substituted deck without needing the optional extra.

## State of the Art

| Old approach | Current approach | When changed | Impact on this phase |
|--------------|------------------|--------------|----------------------|
| `render.py`'s `_block_html` ended in `return ""` | teaching `raise` naming the unhandled `block.kind` | Phase 3 (03-01) | a new block kind can never render as the empty string |
| two normalizers (fixture copy + writer) | one promoted `normalize_opc_zip`; the fixture copy deleted | Phase 2 (02-01) | never re-introduce a local zip normalizer |
| span minting duplicated in `casespec` | promoted `specspan.SpanMinter` | Phase 3 (03-02) | one honest-span implementation |
| KPI disclosure wording duplicated | promoted `compose.compose_kpi_item` | Phase 3 (03-review WR-04) | one wording for the endpoint policy |
| `git diff HEAD` as a diff-gate base | `conftest.milestone_base_ref` (`merge-base HEAD origin/main`) | Phase 3 | any new diff gate must use the fixture and the job must set `fetch-depth: 0` |
| only `rev1` gated in CI | `newsletters check` over **all** corpora | v1.2 | a fourth corpus must be added to **both** `ci.yml` and `deploy-pages.yml` |
| `.pptx` byte equality as the cross-env gate | `part_digest` (implementation-independent) | Phase 1 decision | never `read_bytes()==read_bytes()` on a zip across environments |

**Deprecated/outdated in the docs (fix in this phase):** `docs/architecture.md` §"The
`--corpus {rev1|work}` selector" is stale at *two* corpora and its §9 says *three*;
`docs/surfaces.md` §Records strip says *three*; `content/README.md` still says "Empty until then".

## Assumptions Log

| # | Claim | Section | Risk if wrong |
|---|-------|---------|---------------|
| A1 | The Editor-in-Chief accepts the deck being a corpus artifact rather than a download link on the published page | §The Deck in the Corpus | Rework: move the deck into `site/`, add a `FanoutBlock` link (zero CSS), add a byte-comparison exclusion to the committed==fresh loop. The `FanoutBlock` route is verified available, so the rework is bounded (~1 task). |
| A2 | "in the `content/module` lineage" means *the weekly for the module in `content/module`* (bindings read from the module's committed lane config), not *a file physically inside `content/module/`* | §Corpus Placement Decision | If read literally, route (b) is forced and the CONTEXT's "no mixed builders" constraint has to be re-decided by the EiC. |
| A3 | Adding a fourth corpus to the Records strip on all three existing corpora is wanted (rather than a one-way link into the weekly) | inventory rows 8–12 | If only the weekly links outward, rows 8–10 + 12 + 13 drop; the weekly library becomes an orphan reachable only by URL. |
| A4 | One flat `newsletters weekly` command is the right CLI surface (vs. a `compose\|render` sub-app) | §Command inventory | CLI shape churn only; the recipe text changes with it. Explicitly listed as Claude's discretion in CONTEXT. |
| A5 | Copying `tests/fixtures/weekly/template.pptx` into `content/weekly/` (with a byte-equality guard) is preferable to `src/` reaching into `tests/` | §The Deck in the Corpus | A second committed binary (~28 KB). Alternative is a corpus without a template, which weakens the recipe. |
| A6 | Promoting `test_modulesite`'s synthetic-content scanner into a shared test helper is in scope | §Fixture content rules | If out of scope, write a self-contained weekly scanner and record the two-copies drift explicitly. |
| A7 | The `.eml`-sourced recognition is worth its cost (a second honesty row + the `_EMAIL_RE` allowance) | §The Honesty-Path Fixture | If dropped, the sample shows only the *absent* recognition case with no sourced contrast, and the recipe's `.eml` step is undemonstrated. |
| A8 | `mypy`/`black`/`isort` "no-NEW-failures" is measured against **today's** numbers (15 / 69 / several) rather than the 2026-07-02 baseline document | §Gates Inventory | If the older baseline is authoritative and is lower, some pre-existing failures would be misattributed to this phase. Recommend recording today's numbers in the plan before any edit. |

## Open Questions (RESOLVED — see 04-VALIDATION.md Wave 0: no deck link (costed reversal recorded); check --corpus weekly proven to block; Phase 3 untouched; content/weekly/; measured 2026-08-29 baselines authoritative)

1. **Does the published weekly page need a deck download?**
   - What we know: no success criterion requires it; `FanoutBlock`/`_fanout_row` makes it a
     zero-CSS, zero-render-change addition if the deck lives in `site/`.
   - What's unclear: whether the EiC reads "no dead ends" as "the artifact must be reachable".
   - Recommendation: ship without it; record the `FanoutBlock` route in the plan as a one-task
     upgrade so the decision stays cheap to reverse.

2. **`newsletters check --corpus weekly` is vacuously green (Draft-only corpus).**
   - What we know: `review_blockers` returns `[]` for any non-Published surface, by design.
   - What's unclear: nothing — but a reader could mistake the exit code for a trust proof.
   - Recommendation: wire it for consistency, prove it *blocks* with the monkeypatch idiom from
     `test_module_cli.py:75-91`, and say plainly in the docs that the honesty-panel test is this
     corpus's real proof.

3. **Should `build_weekly_report` carry the binding/`.eml` Sources in `Surface.traces`?**
   - What we know: it carries only `[load.source]`; measured consequence is *no* rendering break and
     *no* false STALE, but a lane-config drift would be invisible to `review_blockers` if the
     surface were ever Published.
   - Recommendation: **do not change Phase 3 code in Phase 4.** Record it in RETRO/`WHERE-WE-ARE.md`
     as a known limitation of a Draft sample and, if it matters, raise it as a v1.4 item.

4. **`content/weekly/` vs `content/module-weekly/` as the directory name.**
   - What we know: the URL becomes `/newsletters/weekly/` either way it is mapped; the corpus name
     also becomes the `--corpus` value and the Records-strip label.
   - Recommendation: `content/weekly/`, `--corpus weekly`, label "The weekly record" — shortest and
     reads correctly in the strip; the lineage is documented in the builder docstring.

5. **Which baseline do `black`/`isort` compare against?**
   - What we know: the repo is broadly non-conformant today (69 files would reformat) and the gate
     is worded "no-NEW-failures vs the 2026-07-02 baseline".
   - Recommendation: record today's exact numbers in the plan's pre-flight, and format **only**
     the files this phase creates.

## Sources

### Primary (HIGH confidence — executed or read in this repo, 2026-08-29)
- Live execution of `load_weekly_spec` / `load_swimlanes` / `build_weekly_report` / `weekly_slots` /
  `render_surface` / `render_library` / `Ledger` / `Site` / `EmailAdapter.parse` /
  `render_surface_pptx_bytes` / `part_digest` on a prototype `content/weekly/` corpus (scratch tree,
  deleted; nothing committed) — the honesty strings, `R-001`, the block list, the 3-second deck
  determinism result and the 28,774-byte deck all come from that run
- `src/newsletters/`: `modulesite.py`, `worksurface.py`, `dogfood.py`, `publish.py`, `cli.py`,
  `site.py`, `render.py`, `weeklyspec.py`, `pptx_writer.py`, `compose.py`, `swimlane.py`,
  `review.py`, `specspan.py`, `adapters/email_adapter.py`
- `tests/`: `test_publish.py`, `test_modulesite.py`, `test_render.py`, `test_weeklyspec.py`,
  `test_weekly_values.py`, `test_module_cli.py`, `test_abstraction_guard.py`,
  `test_collaboration_contract.py`, `conftest.py`, `fixtures/weekly/*`
- `.github/workflows/ci.yml`, `.github/workflows/deploy-pages.yml`
- Gate runs: `pytest -q` (837/0), `lint-imports` (2 kept), `newsletters check` ×3,
  `mypy src/newsletters` (15/5 files), `black --check`, `isort --check-only`

### Secondary (HIGH — repo documents, read directly)
- `.planning/ROADMAP.md` (Phase 4 goal + 5 success criteria + the enforced gate set),
  `.planning/REQUIREMENTS.md` (WKLY-05/06), `.planning/phases/04-sample-corpus-recipe/04-CONTEXT.md`
- `.planning/notes/2026-08-29-pptx-determinism-decision.md` (byte-stable via declared normalization;
  `part_digest` is the cross-environment gate)
- `.planning/phases/02-renderer/{02-01-PLAN,02-01-SUMMARY,02-03-SUMMARY,02-VALIDATION,02-REVIEW}.md`
  (P-06 / P-07 / P-08 / IN-07 carries; "the golden deck comes from the writer")
- `.planning/phases/03-weekly-compose/{03-04-SUMMARY,03-VALIDATION,03-VERIFICATION}.md`
- `docs/weekly-spec.md` (routing table + disclosure wording), `docs/architecture.md` §9 + WORK-01
  flow, `docs/surfaces.md` (ID conventions §223-245, Records strip §293-307), `docs/case-spec.md`,
  `CLAUDE.md`

### Tertiary (LOW confidence)
- None. No web search was used; no claim in this document rests on training knowledge about an
  external library's behaviour — the python-pptx determinism facts are cited from this repo's own
  measured evidence file.

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — no new packages; every extra verified installed and import-clean
- Corpus placement / integration inventory: **HIGH** — all 16 sites located by grep/read in the live
  tree; the 4-file chrome-regen count measured, not estimated
- Honesty-path fixture: **HIGH** — all three `missing[]` strings produced by executing the live loader
- Deck determinism + digest gate: **HIGH** — reproduced across a real 3-second boundary today
- Gate baselines: **HIGH** — every number measured today on this branch
- Architecture patterns / pitfalls: **HIGH** — each drawn from a shipped module or a recorded review
  finding in this repo
- `docs/weekly.md` shape: **MEDIUM** — the pattern is verified (WORK-01 §, case-spec §), but the
  final structure is Claude's discretion per CONTEXT and may be reshaped by the EiC

**Research date:** 2026-08-29
**Valid until:** while this branch's `src/newsletters/` and `.github/workflows/` are unchanged. The
integration inventory is line-referenced and will drift if Phase 3's files move — re-grep
`_CORPUS_LAYOUT`, `CorpusName`, `records=` and `<section class="nl-records"` before planning if any
intervening commit touches `publish.py`, `cli.py`, or the builders.
