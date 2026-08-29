# Phase 3: Weekly compose - Research

**Researched:** 2026-08-29
**Domain:** In-repo archaeology — extending the live Case Spec lift mechanism, the typed `Block`
union, the HTML block dispatch, and the Phase-2 slots renderer into a weekly composer.
**Confidence:** HIGH (every load-bearing claim below was executed against the live repo in `.venv`;
no web sources were needed or used)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Binding (recorded, no reopening):**
1. Reuse `Surface(REPORT)` (D-01) — no new kind; blocks join the existing discriminated union.
2. Provenance minimum = folder + date + event label; deep link REQUIRED only for a BI screenshot
   standing in for values (D-02). `AssetBlock.asset` required; `AssetBlock.evidence`
   min_length=1 — provenance-less placement unrepresentable, not policed.
3. Named placeholders / NL_ prefix contract (D-03) — the composer produces the `slots` mapping
   for Phase 2's `render_surface_pptx` explicit-slots API.
4. Faithful-not-suggestive: narrative byte-verbatim (Case Spec block-scalar mechanism);
   `config:` bound never claimed; absences → `missing[]` with the spec's named reasons;
   planted-editorialization guard test (v1.1 planted-cheat precedent).
5. **Close the render fall-through**: every new block kind gets an HTML render branch using
   existing design-system tokens, AND the `return ""` fall-through at the end of `_block_html`
   becomes fail-loud so an unrecognized block can never again be silently droppable (ROADMAP
   SC-1; the fall-through is unreachable today — keep it that way by construction).

### Claude's Discretion

Module layout (e.g. `weeklyspec.py` beside `casespec.py`; a small `assets.py` if warranted), exact
compose entry point name, how the weekly composer reuses `compose.py`'s KPI-strip/claims machinery.

### Deferred Ideas (OUT OF SCOPE)

Sample corpus + operator recipe are Phase 4's. Carried Phase-2 items (template regeneration,
fixture delegation, layout-walk contract) stay Phase 4/PR items.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| WKLY-02 | Weekly Spec YAML path + the four new block kinds compose into a Draft `Surface(REPORT)`, narrative byte-verbatim with real-span traces, `config:` bound never claimed, absences → `missing[]` | §Union surgery (exact insertion points, the two gates that fire), §The Case Spec lift (what is reusable **verbatim** — `_SpanMinter` proven to handle the entire weekly shape by execution), §Loader rules → mechanism map (all 7), §Determinism |
| WKLY-03 | Asset evidence: record-is-the-Source, sha256 content address, provenance minimum, four-condition `missing[]` routing, `AssetBlock` unrepresentable without provenance | §The asset evidence path (each routing row → concrete code path), §Pydantic proof that `asset` required + `evidence` min_length=1 fire at construction, §Security (read-only, never decode the image) |
| WKLY-04 | BI values via the **existing** ADAPT-03 excel adapter fed an export; no new adapter; ADAPT-05 unchanged | §Values-via-export path (the live `DistillPort` → `Claim` → `SectionBinding` seam), §Environment Availability (**openpyxl is NOT installed here and NOT installed by any CI job** — blocking), §ADAPT-05 clean-diff gate |
</phase_requirements>

## Summary

This phase has no unknowns in its technology and one genuinely hard problem in its *mechanism*: the
weekly must be lifted by the **same** span-minting machinery the Case Spec uses, and that machinery
is a private, forward-only cursor whose correctness depends on the caller walking the parsed
document in **file order**. I executed the live `casespec._SpanMinter` against a full weekly-shaped
YAML document (eight keys, quoted scalars, a block-scalar highlight, a list of mappings, a nested
list inside a mapping inside a list, and an `assets:` mapping-of-mappings): **every one of the 17
authored values minted a content-addressed `Claim` with a real span that the live
`SpanContainmentFaithfulness` gate entails on its strict branch.** Nothing needs re-implementing.
I then broke it deliberately: processing two identical values (`"Devi R."` appearing in both
`recognitions:` and `team:`) out of file order silently **swaps their spans** — both claims still
pass the gate, because the text is identical, so no gate can catch it. File-order iteration is
therefore not a style preference in this loader; it is the correctness condition.

The second cluster of findings is about *which gates will actually fire*. Three of them are weaker
or more dangerous than they read: (a) `tests/test_compose.py::test_faithfulness_..._untouched` runs
`git diff HEAD -- semantic.py`, which compares the **working tree** to HEAD — I proved it goes red
on an uncommitted edit and green again the moment that edit is committed, so it is vacuous in CI's
clean checkout and cannot be the durable proof that the review gate survived this phase; (b) any
addition to `render._CSS` changes the inlined `<style>` on **every** page and breaks
`test_publish.py::test_committed_{rev1,work}_equals_fresh_build` — I proved this by planting one CSS
rule and watching both go red, which is exactly why `docs/weekly-spec.md`'s class map allows the
implementer no visual discretion; (c) **no CI job installs the `[excel]` extra**, so all 64 skips in
the local baseline are excel skips and a WKLY-04 values-via-export test would skip silently in CI —
the precise W21 friction ("the gate that was green because it never ran") recorded in `RETRO.md`
three commits ago.

The third finding is a scope gap the planner must decide about before writing tasks: Phase 2's
writer has **no image-placement path at all** (`grep add_picture src/newsletters/pptx_writer.py` →
nothing; only text slots exist, and `bind_slots` refuses any slot that cannot hold text). Phase 1
*measured* `add_picture` determinism, and `docs/weekly-spec.md` carries a "Determinism of placed
images" paragraph, but no code consumes it. So an `AssetBlock` can reach the HTML surface this phase
and can contribute its caption text to a deck slot, but the image itself cannot reach the `.pptx`
without new writer work that no success criterion asks for.

**Primary recommendation:** Ship `src/newsletters/weeklyspec.py` as a *sibling* of `casespec.py`
that **imports** the promoted span minter rather than copying it; put the four block models and
`AssetRecord` in `semantic.py` as a **pure-insertion** diff (zero deleted lines — verified
achievable), and replace the now-vacuous byte-diff gate with a function-source-hash pin over the
seven gate functions; add zero CSS; and add a CI job that installs `[test,config,excel,pptx]` and
asserts `0 skipped`, or WKLY-04's proof does not exist.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Weekly Spec parse + validation (8 keys, teaching errors) | Core / loader (`weeklyspec.py`) | `_yaml_loader` (lazy `[config]`) | Mirrors `casespec._validate`; YAML is data, `safe_load` only, behind the extra |
| Span minting (`Trace.from_source` real spans) | Core / shared span minter | `semantic.Trace` | The pinning constructor lives in `semantic.py` and nowhere else; the cursor logic is `casespec`'s and must be reused, not forked |
| Asset provenance routing + content-address check | Core / loader | stdlib `hashlib` + `Path.read_bytes` | Read-only; the *record text* is the Source, the image is never parsed |
| Block type definitions (the 4 kinds + `AssetRecord`) | Core / `semantic.py` | — | Every block sub-model in this repo (`KpiItem`, `Chapter`, `GlossaryTerm`, `FanoutLink`) already lives there; the discriminated union must see the classes |
| Surface assembly (blocks + `missing[]` + Draft) | Core / composer | `compose.py` (`compute_delta`), `templates.REPORT` | Composer selects/orders/links; it never authors |
| BI values ingestion | Adapter tier (`adapters/excel_adapter.py`, **unchanged**) | `distill` socket (`resolve("excel")`) | WKLY-04 forbids a new adapter module; the socket is the seam |
| HTML presentation of the 4 kinds | Render tier (`render._block_html`) | `_CSS` (**read-only this phase**) | Existing classes only; `_CSS` is inlined per page and byte-pinned by the committed corpus |
| `.pptx` presentation | Render tier (`pptx_writer`, **unchanged**) | composer-derived `slots` mapping | D-03: the composer owns the Surface→slots derivation; the writer stays layout-blind |
| Review gate | `semantic.Review` / `Surface.publish` — **frozen** | — | Sanctioned diff is the union + new models ONLY |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.13.5 (installed) | Typed blocks, discriminated union, `Field(min_length=1)` type-level invariants | Already the spine's only core runtime dep [VERIFIED: `.venv/bin/python -c "import pydantic"`] |
| stdlib `hashlib` | 3.11.15 | `sha256` of the asset file bytes | `Source.content_hash()` already uses it; no new dep, D-1 discipline |
| stdlib `pathlib` | — | `read_text` / `read_bytes`, `resolve()`, `relative_to()` root containment | `casespec.load_case_spec` precedent, verbatim |
| PyYAML | 6.0.3 (installed, `[config]` extra) | `safe_load` only, via `_yaml_loader.load_config` | Lazy boundary already built; never a top-level `import yaml` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| openpyxl | **NOT INSTALLED** (`[excel]` extra) | ADAPT-03 workbook read for WKLY-04 | Only inside `adapters/_openpyxl_loader`; tests must `importorskip` **and** a CI job must install it |
| python-pptx | 1.0.2 (installed, `[pptx]` extra) | SC-5 deck render through Phase 2's writer | Only via `adapters/_pptx_loader._load_pptx()` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reusing `casespec._SpanMinter` | A weekly-local minter | Rejected. Two implementations of "pin a span honestly" drift exactly as two normalizers would — the explicit reason `pptx_writer.py` exists (its docstring: "ONE normalizer contract"). [CITED: src/newsletters/pptx_writer.py:1-16] |
| `AssetRecord` in `semantic.py` | `assets.py` imported by `semantic.py` (the `locators.py` precedent) | Either works; `semantic.py` is simpler because *every* other block sub-model lives there and `assets.py` would have to stay semantic-free to avoid a cycle. Recommend `semantic.py`. |
| Widening the Case Spec validator | — | Explicitly forbidden by `docs/weekly-spec.md:11-17`: it would make each spec silently accept the other's keys, destroying the strict-schema teaching error in both directions. |
| `.csv` export input (ROADMAP wording) | — | **Not available**: the excel adapter is `.xlsx`-only (`grep -c csv adapters/*.py` → 0). A `.csv` path would require a new adapter, which WKLY-04 forbids. Scope WKLY-04 to `.xlsx`. |

**Installation:** No new packages. One environment change is required:

```bash
.venv/bin/pip install '.[excel]'      # openpyxl — needed for any WKLY-04 test to actually run
```

## Package Legitimacy Audit

**Not applicable — this phase installs no new external packages.** Every dependency it touches
(pydantic, PyYAML, openpyxl, python-pptx) is already declared in `pyproject.toml` and already
audited in earlier milestones. The only environment action is installing the *already-declared*
`[excel]` extra locally and in CI.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
  weekly.yml (authored, in a PR)          exported .xlsx (BI values)        asset image file
        |                                        |                                 |
        | Path.read_text (CRLF→LF)               | resolve("excel").distill()      | Path.read_bytes
        v                                        v                                 | (hash ONLY —
  Source(id=rel, context="weekly-spec:{rel}",  Source(transcript=canonical         |  never decoded)
         transcript=<normalized text>,                Sheet!A1<TAB>value lines)    |
         timestamp=EPOCH_ZERO)                        + Coverage/unextracted[]     |
        |                                        |                                 |
        | _yaml_loader.load_config (safe_load)   | normalize() → content-addressed |
        v                                        v   Claim(+Trace)                 |
  _validate: exactly-8-keys, types              traced value Claims                |
        |                                        |                                 |
        v  FILE ORDER walk (correctness condition, not style)                       |
  _SpanMinter.mint(...) ──► Claim(+Trace.from_source) ──► live GATE.entails?        |
        |                        |                              |                   |
        |                        └── no ──────────────────────► missing[]           |
        |                                                                           |
        ├── week / module ──────────────────► title / eyebrow                       |
        ├── highlights ─────────────────────► NarrativeBlock(tone="highlight")      |
        ├── lowlights ──────────────────────► NarrativeBlock(tone="lowlight")       |
        ├── recognitions ───────────────────► RecognitionsBlock (evidence may be [])|
        ├── team ───────────────────────────► TeamBlock (photo = asset KEY)         |
        ├── assets ─────────────────────────► routing ◄─────────────────────────────┘
        |                                       |          (4 conditions + 2 reference rows)
        |                                       ├── all minimums + link-if-values + hash match
        |                                       |        → AssetBlock(asset=..., evidence=[≥1])
        |                                       ├── missing minimum / missing link / hash ≠
        |                                       |        → missing[] (NOT placed)
        |                                       └── path escapes root → ValueError (REFUSAL)
        └── config ─────────────────────────► WeeklySpec.config  (bound, NEVER claimed)
                                                    |
                    excel Claims ──► KpiStripBlock + ClaimsBlock (compose.py machinery)
                                                    |
                                                    v
                            Surface(REPORT, Draft, created=EPOCH_ZERO,
                                    blocks=[...], missing=[...], traces=[Source...])
                                       |                          |
              render_surface (HTML) ◄──┘                          └──► weekly_slots(surface)
              _block_html: 15 branches, fall-through RAISES              {"NL_*": [lines]}
              honesty panel prints missing[]                                  |
                                                            render_surface_pptx(surface,
                                                              template=..., slots=...)
                                                            → bind_slots fail-loud both ways
                                                            → normalize_opc_zip → bytes
```

### Recommended Project Structure

```
src/newsletters/
├── semantic.py         # + NarrativeItem/NarrativeBlock, Recognition/RecognitionsBlock,
│                       #   TeamMember/TeamBlock, AssetRecord/AssetBlock, + 4 union members
│                       #   (PURE INSERTION — zero deleted lines)
├── specspan.py         # (recommended) the PROMOTED _SpanMinter + _absent(), moved verbatim
│                       #   from casespec.py; casespec imports it, weeklyspec imports it
├── casespec.py         # unchanged except the import of the promoted minter
├── weeklyspec.py       # NEW: _validate (8 keys), load_weekly_spec(), asset routing,
│                       #   build_weekly_report(), weekly_slots()
├── render.py           # + 4 branches in _block_html; fall-through → raise. NO _CSS EDIT.
└── compose.py          # unchanged, or + one exported section-assembly helper (not protected)

tests/
├── fixtures/weekly/    # weekly-full.yml, weekly-sparse.yml, weekly-assets-*.yml + a PNG
└── test_weeklyspec.py  # the proof suite (see Validation Architecture)
```

### Pattern 1: The union surgery — a pure-insertion diff

**What:** The four block classes and their sub-models go into `semantic.py`'s "Content blocks"
section (currently `semantic.py:333-464`), and the four names are appended to the `Union[...]`
list at `semantic.py:449-464`, after `GlossaryBlock,`.

**Where exactly:**
- Sub-models (`NarrativeItem`, `Recognition`, `TeamMember`, `AssetRecord`) beside `KpiItem` /
  `Chapter` / `GlossaryTerm` — this repo puts every block's sub-model in `semantic.py`
  [VERIFIED: `semantic.py:333-446`].
- Block classes immediately before `Block = Annotated[...]` at line 449.
- Union members appended after `GlossaryBlock,` (line 461) → **insertion only, no line deleted**.

**What adding a member touches (audited, exhaustive):**

| Surface | Effect | Action |
|---------|--------|--------|
| Discriminator resolution | `kind` `Literal` per member; JSON round-trip resolves the right model | **Verified by execution**: a two-member discriminated union with the proposed models round-tripped byte-identically and re-hydrated the right classes |
| `Surface.content` serialization | `model_dump_json` gains the new fields only when present | none |
| `Source.content_hash()` | Hashes `transcript` only — **unaffected** by block changes [CITED: semantic.py:71-83] | none |
| Count-pinning tests | **There are none.** `grep -rn "get_args\|__args__\|eleven" tests/` → zero hits in `tests/`; the "eleven members" statements live only in `docs/architecture.md:31` and `docs/weekly-spec.md:204,211` | update BOTH doc lines from "eleven→fifteen" phrasing to the shipped state |
| `newsletters/__init__.py` re-export | `GlossaryBlock` is **not** re-exported (precedent) [VERIFIED: `__init__.py:19-44,60-81`] | optional; re-exporting is safe but not required. Do not widen the bare-install blast radius without a reason. |
| `tests/test_compose.py::test_faithfulness_coverage_semantic_templates_site_are_untouched` | **RED while the edit is uncommitted** | see Pattern 2 |
| bare-install CI job | runs `tests/test_semantic.py` on `pip install .[test]` | new models must be pydantic+stdlib only — they are |

**The sanctioned-vs-forbidden diff, named precisely.** Sanctioned this phase: the *additive*
regions above. Forbidden — the gate — is this exact set of functions in `semantic.py`, which must
be byte-identical afterwards:

| Function / member | Location today | Why it is the gate |
|---|---|---|
| `Review.satisfied` | `semantic.py:271-277` | the policy arithmetic |
| `Review._published_requires_satisfied_policy` | `semantic.py:279-287` | the no-auto-publish validator |
| `Surface._published_claims` | `semantic.py:545-550` | what invariant 2 inspects |
| `Surface.open_pull_request` | `semantic.py:552-564` | untraced-claim refusal |
| `Surface.approve` | `semantic.py:566-573` | approval recording |
| `Surface.publish` | `semantic.py:575-588` | the only Published path |
| `Trace.from_source` | `semantic.py:126-170` | the sole pinning constructor |
| `Source.content_hash` | `semantic.py:71-83` | the content address |

### Pattern 2: Replacing a gate that was already vacuous

**What goes wrong today:** `tests/test_compose.py:533-552` shells `git diff HEAD --exit-code --
<gate_files>` including `src/newsletters/semantic.py`. `git diff HEAD` compares the **working tree**
to HEAD, so it reports only *uncommitted* edits.

**Proven, not assumed** [VERIFIED by execution in this session]:
- clean tree → `1 passed in 0.03s`
- append one comment line to `semantic.py` → `FAILED ... AssertionError` at `test_compose.py:550`
- `git checkout --` → passes again

So the moment the union addition is committed the test is green again, and in CI (always a clean
checkout) it has never been capable of failing. It is an uncommitted-edit tripwire, not a
protection of the gate.

**How to replace it (recommended shape):**

```python
# tests/test_semantic_gate_frozen.py  (or inside the weekly suite)
import hashlib, inspect
from newsletters.semantic import Review, Source, Surface, Trace

# The gate's source text, pinned. A change to ANY of these bodies is a conversation,
# not a commit (CLAUDE.md: "A change that breaks one is a conversation").
_FROZEN = {
    "Review.satisfied": "<sha256 of inspect.getsource(Review.satisfied)>",
    "Review._published_requires_satisfied_policy": "...",
    "Surface._published_claims": "...",
    "Surface.open_pull_request": "...",
    "Surface.approve": "...",
    "Surface.publish": "...",
    "Trace.from_source": "...",
    "Source.content_hash": "...",
}

def _digest(fn) -> str:
    return hashlib.sha256(inspect.getsource(fn).encode("utf-8")).hexdigest()
```

Pair it with the *diff-shape* assertion that makes the union addition self-policing:

```python
# every semantic.py change in this phase is an ADDITION; a deleted line means
# something was rewritten, not extended.
out = subprocess.run(["git", "diff", BASE_REF, "--", "src/newsletters/semantic.py"], ...)
removed = [l for l in out.stdout.splitlines() if l.startswith("-") and not l.startswith("---")]
assert not removed, removed
```

`BASE_REF` must be the milestone base (e.g. the merge-base with `main`), **not** `HEAD` — that is
the bug being fixed. Keep the other four protected files (`faithfulness.py`, `coverage.py`,
`templates.py`, `site.py`) in the existing list, and consider upgrading that list to `BASE_REF`
too, since the same vacuity applies to all five.

### Pattern 3: The Case Spec lift — what is reusable verbatim

`casespec.py` decomposes into five reusable mechanisms. **Executed against a full weekly-shaped
document in this session; all 17 authored values minted real, gate-entailed spans:**

```
key order: ['week','module','highlights','lowlights','recognitions','team','assets','config']
  week                      -> CLAIM (7,15)     entails=True
  module                    -> CLAIM (26,43)    entails=True
  highlights[0]             -> CLAIM (62,118)   entails=True     (quoted scalar, exact find)
  highlights[1]             -> CLAIM (123,182)  entails=True     (BLOCK SCALAR, item region)
  lowlights[0]              -> CLAIM (198,227)  entails=True
  recognitions[0].person    -> CLAIM (256,263)  entails=True     (mapping inside a sequence)
  recognitions[0].reason    -> CLAIM (278,325)  entails=True
  recognitions[1].person    -> CLAIM (373,379)  entails=True
  team[0].name              -> CLAIM (434,441)  entails=True     (duplicate of a value above!)
  team[0].lines[0]          -> CLAIM (487,525)  entails=True     (list inside mapping inside list)
  assets[k].sha256          -> CLAIM (640,704)  entails=True     (the hash traces verbatim)
  ... (17/17 CLAIM, 0 disclosures)
```

| Mechanism | Where | Reuse verdict |
|---|---|---|
| Root containment + read-only read + newline-normalized transcript | `casespec.load_case_spec:331-336` | **Copy the 6 lines verbatim** into `weeklyspec.load_weekly_spec`. Identical policy, teaching-identical errors. Not worth a shared helper (it is 6 lines and the error identity differs). |
| `Source(id=rel, context="...:{rel}", transcript, timestamp=EPOCH_ZERO)` | `casespec.py:338-343` | Same shape, `context="weekly-spec:{rel}"` per `docs/weekly-spec.md:92-96`. |
| `_SpanMinter` (forward cursor, exact-find → field region → item region, gate-checked) | `casespec.py:175-288` | **PROMOTE, do not fork.** Proven above to handle every weekly shape unchanged. Promote to `specspan.py` (pure move, keep the docstring verbatim so the diff shows nothing was "tidied" — the `pptx_writer` promotion precedent) and import from both loaders. A private cross-module `from .casespec import _SpanMinter` also works but has no precedent in `src/` [VERIFIED: grep found zero private cross-module imports]. |
| `_route()` closure (empty → None + later disclosure; Claim → claims; str → missing) | `casespec.load_case_spec:350-361` | Re-implement (10 lines, closes over the weekly's own `claims`/`missing`). |
| Enforced-by-construction gate sweep (`RuntimeError` if any emitted claim fails `_GATE.entails`) | `casespec.py:390-396` | **Copy.** This is what makes "every emitted claim passes the LIVE gate" a fact rather than a hope. |
| `_absent(field)` disclosure wording | `casespec.py:291-292` | Reuse the exact phrasing for the weekly's absent-field notes so the honesty panel reads consistently. |
| `build_case_report` shape (blocks list, `missing` → `Surface.missing`, `Review(policy=REPORT...)`, `created=EPOCH_ZERO`) | `casespec.py:415-466` | Structural template for `build_weekly_report`. |

**The seven loader rules → the mechanism, one by one:**

| Rule (`docs/weekly-spec.md:63-88`) | Mechanism | Gap? |
|---|---|---|
| 1. Exactly these top-level keys, unknown key fails loud | `_validate` pattern from `casespec.py:120-172` with `_KNOWN_KEYS` = the 8 weekly keys | None. Note it must be a **separate** validator (spec §11-17). |
| 2. Narrative fields are strings | The `_STR_KEYS` type check `casespec.py:133-139` | None. Weekly needs it recursively (`recognitions[].person/reason/source`, `team[].name/role/lines[]/photo`, `assets[].{file,sha256,folder,date,event,link,stands_in_for,caption,alt}`) — more shapes to validate than the Case Spec has, all with the same teaching-error voice. |
| 3. `highlights`/`lowlights` byte-verbatim | `_route` carries the parsed value into `NarrativeItem.text` untouched; the `Claim` carries the same string | None mechanically. The *enforcement* is the planted-editorialization guard (see Validation Architecture). |
| 4. Every absent/empty field disclosed, incl. "no lowlights" | `_disclose_gaps` pattern `casespec.py:295-314` | None. Weekly's list must name every one of the 8 keys plus per-item absences. |
| 5. `config:` bound never claimed | `casespec.py:365-366` — `config` short-circuits before minting | None. The Case Spec's `test_config_never_in_claims` is directly portable. |
| 6. Recognition with no `source` still carried + disclosed | `Recognition.evidence: list[Trace] = Field(default_factory=list)` (empty legal, by design) + a `missing[]` note | None. Deliberate contrast with `AssetBlock.evidence` min_length=1 — the spec calls this out at `weekly-spec.md:193-199`. |
| 7. Read-only; a path escaping root raises | `resolved.relative_to(root_path)` raises `ValueError` [CITED: casespec.py:335] | **One real widening:** the weekly also resolves the *asset file* path, which is a second containment check, on a path from inside the document rather than from the caller. Do it with the same `resolve()/relative_to()` idiom, before `read_bytes()`, so a `../../etc/passwd` never reaches the filesystem call. |

**The one genuine gap between the doc and the mechanism** (neither blocking nor a doc error, but the
planner must know it): `docs/weekly-spec.md` says each authored value is minted "via
`Trace.from_source` — real character spans of *your* file". For a **block-scalar** value the span is
the raw *item region*, not the folded value (the value is not a substring of the file at all), and
the claim survives only because the live gate normalizes whitespace and still entails it
[VERIFIED: `highlights[1]` above, span `(123,182)`, `entails=True`]. That is exactly what the Case
Spec does and it is honest — but "real span" means "the region that contains your text", not "the
exact bytes of your text", for block scalars only. Do not let a test assert
`transcript[start:end] == item.text` unconditionally; assert
`_normalize(text) in _normalize(span)` (the gate's own rule) plus `transcript[start:end] == span`.

### Pattern 4: The asset evidence path

**The record is the Source, the image is a hash inside it.** `Source.transcript` is a `str` and
`content_hash()` hashes that string [CITED: semantic.py:71-83], so a binary can never be a Source.
The weekly YAML file's own text already *is* the Source and the `sha256:` hex string is a literal
substring of it — I minted it and it traced verbatim, `entails=True`, at offsets `(640,704)` in the
probe above. **No separate asset-record file is needed for the synthetic corpus**: the `assets:`
subtree of the weekly spec is the record, and its Source is the spec file. If a later phase wants
standalone record files, the same machinery applies with a second `Source`; nothing here forecloses
it. Recommend keeping it in-document for Phase 3 — one Source, one hash, one containment check.

**Hashing the image, read-only, and never decoding it:**

```python
digest = hashlib.sha256(resolved_image.read_bytes()).hexdigest()   # stdlib only
```

No Pillow, no `imghdr`, no python-pptx image handling. The loader must **never** decode or parse
image bytes — that would add a dependency, a decompression-bomb surface, and an opinion about
content. (Pillow is present in `.venv` transitively; do not reach for it.)

**Every routing row → its concrete code path:**

| Condition (`weekly-spec.md:265-273`) | Code path | Outcome |
|---|---|---|
| any of `folder`/`date`/`event` absent or empty | `if not str(rec.get(f, "")).strip()` per field, **in field order** so the first-named field is deterministic | append the spec's exact `asset {key!r}: provenance field {field!r} is absent — ...` string to `missing[]`; `continue` (no block) |
| `stands_in_for == "values"` and `link` absent/empty | checked after the minimums | spec's deep-link disclosure string; no block |
| file missing on disk **or** `sha256` mismatch | `resolved.exists()` then `hashlib.sha256(read_bytes())` compared **case-insensitively** to the recorded hex | spec's content-address disclosure string; no block. Note: `Path.exists()` on a dangling path returns False — no exception to catch; but wrap `read_bytes()` for `OSError`/`PermissionError` and route to the same disclosure rather than crashing |
| `file` path escapes the project root | `(root / rec["file"]).resolve().relative_to(root)` → `ValueError` | **raise** — a refusal, not an absence. Re-raise with the teaching voice naming the key and the path. |
| all minimums + link-if-required + hash match | mint ≥1 `Trace.from_source` over the record's own spans (e.g. the `sha256` value span, or the whole asset-key region) | `AssetBlock(asset=AssetRecord(...), evidence=[trace, ...])` |
| `team[].photo` names no `assets:` entry, or an unplaced one | resolve `photo` against the set of **placed** keys, after asset routing | member carried, `photo=None`; spec's `team member {name!r}: photo key {key!r} names no placed asset — ...` |
| recognition `source:` resolving to no known `Source` | membership test against the known-Source ids (the spec Source + any adapter Sources passed in) | `Recognition(evidence=[])` + spec's unresolvable-id disclosure. **Never** a minted empty `Trace`. |

**Ordering note:** because `team[].photo` routing depends on which assets were *placed*, and
`assets:` appears after `team:` in the schema, the loader needs two passes over the parsed
document — pass 1 mints spans in strict file order (correctness condition, see Pitfall 1), pass 2
resolves references. Keep the minting pass file-ordered and do reference resolution afterwards from
already-minted data; never re-enter the minter out of order.

**Type-level unrepresentability — proven, not asserted** [VERIFIED by execution]:

```
AssetBlock(asset=rec, evidence=[])  -> ValidationError  too_short  ('evidence',)
AssetBlock(evidence=[Trace(...)])   -> ValidationError  missing    ('asset',)
```

### Pattern 5: Composition, and how the weekly reuses `compose.py`

`compose.compose_module_report` is a whole-Surface builder with its own identity (`report-{slug}`),
its own `Ledger` ref, its own fan-out stub and its own quote slot — it is not a block factory, so
the weekly cannot call it. What the weekly *should* reuse:

- **`compute_delta`** — public, pure, in `__all__` [CITED: compose.py:59,108]. Import it directly.
- **The `SectionBinding` seam** — `compose.py`'s docstring states the composer is kind-agnostic and
  invites "any other `SectionBinding` kind with zero composer change" [CITED: compose.py:150-157].
  The cleanest WKLY-04 shape is: excel `Claim`s → one or more `SectionBinding`s → the same
  KPI/claims assembly.
- **The traced-or-missing policy** (`_addressed(claim)` → keep, else → `missing[]`,
  `compose.py:191-193,356-362`) — copy this predicate's *behaviour*; it is four lines.

Two viable structures (planner's choice; both honour "the composer selects, never authors"):

1. **Extract a shared helper** into `compose.py` (not a protected file) — e.g.
   `section_blocks(binding, missing) -> list[Block]` — and call it from both composers. DRY, one
   new public name, `compose_module_report` becomes a caller of it (a behaviour-preserving refactor
   its 20+ existing tests will police).
2. **Weekly builds its own KpiStrip/Claims** from `compute_delta` + `_addressed`. Less coupling, a
   small duplication of the routing policy.

Recommend (1) if the refactor stays byte-behaviour-identical under the existing `test_compose.py`;
fall back to (2) if it does not.

**Block order in the weekly Surface must be fixed and documented** (it is part of the determinism
claim). A defensible order that matches the spec's own prose at `weekly-spec.md:103-111`:
`ProseBlock`(connective, numeral-free) → `KpiStripBlock`* → `ClaimsBlock` → `NarrativeBlock`
(highlight) → `NarrativeBlock`(lowlight) → `RecognitionsBlock` → `TeamBlock` → `AssetBlock`*
(in `assets:` **file order**). Fix it in code, assert it in a test.

### Pattern 6: The render branches, and the fail-loud fall-through

`_block_html` is at `render.py:544-620`; its only caller is `render.py:886`
(`render_surface`) [VERIFIED: `grep -n _block_html render.py` → 2 hits]. Because `Surface.blocks`
is `list[Block]` with a discriminator, pydantic guarantees every element is a union member, so
converting `return ""` (line 620) into a raise cannot fire on valid data — which is exactly the
"unreachable by construction" property `docs/weekly-spec.md:208-219` asks Phase 3 to preserve.

The raise must be a teaching error naming the kind:

```python
raise ValueError(
    f"no HTML branch for block kind {getattr(b, 'kind', type(b).__name__)!r} — a block that "
    "was authored, traced and reviewed would otherwise render as the empty string, with no "
    "error anywhere. Add a branch to _block_html using existing design-system tokens "
    "(docs/design-system.md; docs/weekly-spec.md's class map) — the renderer never silently "
    "drops a block."
)
```

**HARD CONSTRAINT — add ZERO new CSS.** `_CSS` is inlined into every page (`_page`,
`render.py:740`), and `tests/test_publish.py::test_committed_rev1_equals_fresh_build` /
`test_committed_work_equals_fresh_build` compare committed corpus HTML against a fresh render.
**Proven in this session:** planting a single `.nl-scratch{color:red}` rule turned both red
(`2 failed, 8 passed`). Adding CSS would force a full regeneration of `content/rev1/site` and
`content/work/` — a large, noisy diff no success criterion asks for.

The classes in `docs/weekly-spec.md:224-229` all exist today [VERIFIED: `render.py:147-245`]:

| Block | Markup to emit | Existing CSS |
|---|---|---|
| `NarrativeBlock` | `div.block` + `h3.block-h` + per line `div.item` > `span.sg-tag.cat` (tone) + `div.bo` (verbatim text) | `.block:201`, `.block-h:202`, `.sg-tag.cat:148`, `.item:231`, `.item .bo:233` |
| `RecognitionsBlock` | `div.block` + `h3.block-h` + per recognition `div.item` > `div.ti` (person) + `div.bo` (reason) | `.item .ti:232`, `.item .bo:233` |
| `TeamBlock` | `div.block` + `h3.block-h` + per member `div.chapter` > `div.t` (role) + `div` > `div.ti` (name) + `div.bo` (lines) | `.chapter:227` is a **2-column grid (`64px 1fr`)** — mirror `ChaptersBlock`'s exact wrapper structure (`render.py:585-592`), i.e. `div.t` then a wrapper `<div>` holding `.ti`/`.bo`, or the layout breaks |
| `AssetBlock` | `div.block` + `figure.diagram` > `div.dh` (heading) + `<figcaption>` (caption) | `.diagram:242`, `.diagram .dh:244`, `.diagram figcaption:245` |

Every interpolation goes through `_e()` (the module's escaper) — `render.py` escapes every
user-derived string today and the honesty panel's own tests assert it. **`AssetBlock` must not emit
an `<img>` this phase** unless the plan also solves relative-path resolution for the published tree;
the spec's class map deliberately says `figure.diagram` + `dh` + `figcaption` (text only).

### Pattern 7: Deriving Phase 2's slots

`render_surface_pptx(surface, template=..., slots=...)` takes `slots` as a **required keyword** and
`bind_slots` fails loud in both directions [CITED: pptx_writer.py:613-624, 371-480]. So the composer
owns a pure function:

```python
def weekly_slots(surface: Surface) -> dict[str, list[str]]:
    """Derive the NL_-prefixed content mapping from a composed weekly Surface. Pure + ordered."""
```

Rules the derivation must obey, each with a reason:

1. **Deterministic key order** — build the dict by iterating `surface.blocks` in order; dict
   insertion order is the serialization order. (Fill order does not affect output bytes — measured
   in Phase 2, `pptx_writer.py:645-647` — but a stable mapping is still what the test asserts.)
2. **Omit empty slots, never pad.** `fill_slot` raises on `[]` or all-blank lines
   [CITED: pptx_writer.py:538-544]. A weekly with no lowlights must **omit** `NL_LOWLIGHTS`, not
   emit `["none"]` — emitting a placeholder would be the composer authoring content, and the
   absence is already disclosed in `missing[]` (rule 4). The consequence is designed and must be
   documented: if the operator's template *does* carry `NL_LOWLIGHTS`, `bind_slots`'s unfilled-slot
   refusal fires — a teaching error, correctly.
3. **Only `NL_`-prefixed names** — an unprefixed key is refused [CITED: pptx_writer.py:441-448].
4. **Every line is authored text, verbatim.** If a slot needs two authored fields on one line
   (a recognition's person + reason), the joining string is a declared module constant asserted
   byte-exactly by a test — or, safer, emit two lines. Never reorder, never summarize.
5. **Images do not go through slots.** `bind_slots` raises for any shape without a text frame
   [CITED: pptx_writer.py:470-478] and **the writer has no `add_picture` path at all**
   [VERIFIED: `grep -n "add_picture\|image" pptx_writer.py` → one comment, no code]. An asset can
   contribute its caption to a text slot; the image cannot reach the deck this phase.

### Anti-Patterns to Avoid

- **Forking the span minter.** Two "pin a span honestly" implementations drift exactly as two
  normalizers would; `pptx_writer.py`'s existence is the repo's recorded lesson.
- **Widening `casespec._validate` to accept weekly keys.** Explicitly forbidden
  (`weekly-spec.md:11-17`) — it destroys the strict-schema guarantee in both directions.
- **Adding CSS "just one rule".** Proven to break two committed-corpus tests.
- **Inferring `stands_in_for` from a filename/folder/image.** That is the composer forming an
  opinion about content (`weekly-spec.md:258-262`). Author-declared only.
- **Minting an empty `Trace` for an unresolvable recognition `source:`.** Fabrication. Route to
  `evidence=[]` + a disclosure naming the id.
- **Emitting `["—"]` / `["none"]` into an empty slot** to dodge `fill_slot`'s refusal.
- **Asserting the deck is byte-identical across environments.** DEFLATE is implementation-dependent;
  use `part_digest` for cross-environment claims and bytes only for an in-process double render
  [CITED: pptx_writer.py:85-92].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Pin a claim to a real span | a `find`+slice helper | `casespec._SpanMinter` (promoted) + `Trace.from_source` | forward-cursor duplicate handling, block-scalar item regions, and gate-checking are already solved and proven against the weekly shape |
| Decide "is this faithful?" | a containment check | `distill.faithfulness.SpanContainmentFaithfulness()` (the LIVE gate instance) | one definition of faithful; `casespec` already routes gate-failures to `missing[]` |
| Parse YAML | `import yaml` | `_yaml_loader.load_config` | `safe_load` only + the lazy `[config]` boundary the bare-install gate polices |
| Deterministic timestamps | `datetime(1970,...)` | `adapters._timestamps.EPOCH_ZERO` | one epoch sentinel; a second one drifts |
| Read a spreadsheet | anything | `distill.resolve("excel")` / `ExcelAdapter` | WKLY-04 forbids a new adapter; the formula-cache faithfulness fork is already right |
| Normalize a `.pptx` | any zip rewrite | `pptx_writer.normalize_opc_zip` | ONE normalizer contract |
| Slugify / assign a ref | string munging | `site.slugify`, `site.Ledger.ref_for` | the ledger is append-only and immutable on re-sight |
| Hash content | anything | `hashlib.sha256` (+ `Source.content_hash` for Sources) | D-1 |
| Escape HTML | f-string concatenation | `render._e` | every existing branch does |

**Key insight:** every "new" capability this phase needs already exists one import away, and each
one is guarded by a test somebody wrote *because* the naive version failed. The phase's real work is
schema, routing and disclosure — not mechanism.

## Runtime State Inventory

Not a rename/refactor/migration phase. Two adjacent categories are still worth stating explicitly,
because both are committed artifacts that a code change can silently invalidate:

| Category | Items Found | Action Required |
|---|---|---|
| Committed rendered corpora | `content/rev1/site/*.html`, `content/work/*`, `content/module/*` are byte-compared against a fresh render by `test_publish.py::test_committed_{rev1,work}_equals_fresh_build` and `test_modulesite.py::test_committed_equals_fresh_build` | **No `_CSS` edit** (proven to break them). If a render change ever becomes unavoidable, regenerating the corpora is a separate, declared task. |
| Ledgers | `content/rev1/ids.json`, `content/module/ids.json` — `compose` never `save()`s; the caller owns persistence | none this phase (the weekly composer should likewise not write) |
| Stored data / live service config / OS-registered state / secrets | **None** — this phase adds no datastore, no service, no scheduled task, no env var or secret. Verified by reading the phase scope and grepping `src/` for network/subprocess edges (the `problem.py` import-linter contract already forbids them there). | none |
| Build artifacts | The editable install `newsletters 0.1.0` in `.venv`; adding a module needs no reinstall (editable, `src` layout on `pythonpath`) | none |

## Common Pitfalls

### Pitfall 1: Out-of-file-order minting silently swaps spans

**What goes wrong:** two identical authored values in different sections (e.g. a person named in
both `recognitions:` and `team:`) get each other's spans.
**Why it happens:** `_SpanMinter` is a forward-only cursor (`casespec.py:175-186`): `mint` does
`raw.find(value, self._cursor)` and then advances. If the caller mints the *later* field first, the
cursor lands on the *earlier* occurrence.
**Proven** [VERIFIED by execution]: minting `team[0].name` before `recognitions[0].person` for the
same string `"Devi R."` produced `team.name → offsets (44,51) LINE 3` (the recognition's line) and
`rec.person → offsets (91,98) LINE 6` (the team's line). **Both claims pass the faithfulness gate**,
because the text is identical — no gate can catch this.
**How to avoid:** walk `parsed.items()` and every nested collection in **document order**
(PyYAML's `safe_load` preserves it; `casespec.py:364` relies on this already). Do reference
resolution (`photo:` keys, recognition `source:` ids) in a *second* pass over already-minted data.
**Warning signs:** a test that asserts spans are strictly ascending across the whole document, or
that a duplicated value's two traces land on the expected lines, will catch it. Write that test.

### Pitfall 2: The `semantic.py` protection you think you have is a working-tree tripwire

Covered in Pattern 2. **Warning sign:** the test passes in CI on every run and has never failed —
that is the shape of a gate that never runs.

### Pitfall 3: An excel-dependent test that silently skips

`openpyxl` is **not installed in `.venv`** and **no CI job installs `[excel]`**
[VERIFIED: `pip list` has no openpyxl; `grep -n excel .github/workflows/ci.yml` → no match]. The
local baseline's 64 skips are *all* excel skips. A WKLY-04 test written with `importorskip` would
therefore be green-because-not-run in both places — verbatim the W21 friction in `RETRO.md:7-42`.
**How to avoid:** install `[excel]` locally, and add (or extend) a CI job that installs
`.[test,config,excel,pptx]` and runs the weekly + excel modules with an assertion that the run
reports `0 skipped`.

### Pitfall 4: New tests that no CI job runs

Beyond excel: **`tests/test_casespec.py`, `test_compose.py`, `test_swimlane.py`,
`test_abstraction_guard.py`, `test_faithfulness_gate.py` are in no CI job at all**
[VERIFIED: the only `pytest` invocations in `ci.yml` are lines 76, 142, 172, covering 12 modules].
A new `tests/test_weeklyspec.py` will not run in CI unless a job names it.

### Pitfall 5: `.chapter` is a two-column grid

`TeamBlock`'s markup must mirror `ChaptersBlock`'s wrapper structure exactly
(`div.t` + a wrapper `<div>` containing `.ti`/`.bo`, `render.py:585-592`), or the member's name and
lines land in the wrong grid cell. The CSS (`render.py:227-230`) is scoped as
`.chapter .t / .chapter .ti / .chapter .bo`.

### Pitfall 6: `fill_slot` on a bare `str`

A bare `str` is a `Sequence[str]` of characters. Phase 2 fixed this inside `fill_slot`
(`pptx_writer.py:535-537`), but a composer that builds `slots` values should still emit `list[str]`
explicitly so the intent is visible.

### Pitfall 7: The abstraction guard scans `src/` only, and it will scan your new module

`tests/test_abstraction_guard.py` walks every `*.py` under `src/newsletters/`. No fixture key
(`lane-throughput`, a person's name, a module name) may appear in `weeklyspec.py`. Structural keys
(`week`, `module`, `highlights`, `assets`, `folder`, `event`) are generic and fine. Choose fixture
identifiers for the weekly corpus that are **not** plausible generic source tokens, and consider
adding them to the denylist so the guard stays non-vacuous for this phase's fixtures.

### Pitfall 8: `Surface` has `validate_assignment=True`

`Surface.model_config = ConfigDict(validate_assignment=True)` (`semantic.py:501`) — every assignment
re-validates. Build the blocks list first and pass it to the constructor; do not mutate
`surface.blocks` after construction.

### Pitfall 9: The `[config]` extra is genuinely optional

`weeklyspec.py` must have **no** column-0 `import yaml` (policed by
`test_ai_optional.py::test_yaml_loader_has_no_toplevel_yaml_import` and its siblings). Import
`_yaml_loader.load_config` and let it raise the teaching `ImportError`.

## Code Examples

### Loading a weekly spec (the shape, mirroring the live Case Spec loader)

```python
# Source: src/newsletters/casespec.py:317-407 (the live, proven loader), adapted
def load_weekly_spec(path, *, root=None) -> WeeklySpecLoad:
    root_path = (root or Path.cwd()).resolve()
    candidate = Path(path)
    absolute = candidate if candidate.is_absolute() else (root_path / candidate)
    resolved = absolute.resolve()
    rel = resolved.relative_to(root_path).as_posix()      # ValueError if it escapes root
    transcript = resolved.read_text(encoding="utf-8")     # READ ONLY, CRLF folds to LF

    source = Source(id=rel, context=f"weekly-spec:{rel}",
                    transcript=transcript, timestamp=EPOCH_ZERO)
    parsed = _validate(_parse_config(transcript))         # safe_load, exactly-8-keys

    minter = _SpanMinter(source)                          # PROMOTED, not forked
    claims, missing = [], []
    for key, value in parsed.items():                     # FILE ORDER — the correctness condition
        ...
    for claim in claims:                                  # enforced by construction
        if not _GATE.entails(claim):
            raise RuntimeError(...)
```

### Minting an asset's evidence, read-only

```python
# Source: this session's verified probe + semantic.Trace.from_source:126-170
image = (root_path / record["file"]).resolve()
image.relative_to(root_path)                       # ValueError => refusal, not missing[]
if not image.is_file():
    missing.append(_ASSET_CONTENT_ADDRESS.format(key=key, file=record["file"]))
    continue
digest = hashlib.sha256(image.read_bytes()).hexdigest()   # bytes are hashed, never decoded
if digest.lower() != str(record["sha256"]).strip().lower():
    missing.append(_ASSET_CONTENT_ADDRESS.format(key=key, file=record["file"]))
    continue
```

### The union addition (pure insertion)

```python
# Source: src/newsletters/semantic.py:449-464 — append AFTER GlossaryBlock, no line removed
Block = Annotated[
    Union[
        ProseBlock, ClaimsBlock, KpiStripBlock, QuoteBlock, ChaptersBlock,
        ItemsBlock, PromptBlock, FanoutBlock, RationaleBlock, DiagramBlock,
        GlossaryBlock,
        NarrativeBlock, RecognitionsBlock, TeamBlock, AssetBlock,   # + 4, insertion only
    ],
    Field(discriminator="kind"),
]
```

### Verified pydantic behaviour of the new invariants

```
AssetBlock(asset=rec, evidence=[])        -> ValidationError: too_short  ('evidence',)
AssetBlock(evidence=[Trace(source_id=s)]) -> ValidationError: missing    ('asset',)
Holder(blocks=[AssetBlock, NarrativeBlock]).model_dump_json() round-trips byte-identically
and re-hydrates ['AssetBlock', 'NarrativeBlock']
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Spike normalizer under `tests/fixtures/weekly/_determinism.py` | promoted to `src/newsletters/pptx_writer.py` | v1.3 Phase 2 | The house precedent for **promoting a mechanism rather than importing it privately or copying it** — apply it to `_SpanMinter` |
| Blanket `git diff HEAD` file-freeze gates | (unchanged, and now known to be working-tree-only) | — | Replace with a base-ref diff and/or function-source pins |
| No CI job for `[pptx]` | `pptx` job added (WKLY-01, W21) | v1.3 Phase 2 | The template to copy for the `[excel]`/weekly job |
| Blocks: eleven union members | fifteen after this phase | this phase | Update `docs/architecture.md:28-36` and `docs/weekly-spec.md:203-211` from future tense to shipped |

**Deprecated/outdated:**
- ROADMAP Phase 3 SC-4's "`.xlsx`/`.csv`" wording: **there is no CSV path** in the live adapter.
  Scope to `.xlsx` and note the correction rather than building a CSV reader (WKLY-04 forbids a new
  adapter module).

## Project Constraints (from CLAUDE.md)

| Directive | Consequence for this phase |
|---|---|
| **No auto-publish, ever** | `build_weekly_report` returns `Draft`; never calls `publish()`/`open_pull_request()`; prove with a test that a bare `publish()` raises and the state stays `DRAFT` (the `test_casespec.py:244-258` pattern) |
| **Every published claim traces to evidence** | every emitted claim passes the LIVE gate at load time; failures → `missing[]` |
| **AI-optional core** | `weeklyspec.py` imports stdlib + pydantic + core modules only; no column-0 `import yaml`/`openpyxl`/`pptx`; `lint-imports` stays KEPT |
| **Faithful, not suggestive** | no summarizing/reordering/merging of authored lines; connective prose stays numeral- and fact-free; `stands_in_for` never inferred |
| **Interactive until trusted** | the composer writes no files and sends nothing; `render_surface_pptx`'s `out_path` stays caller-supplied |
| **Secrets in git-ignored env files** | n/a — nothing secret here |
| **Specs are source of truth** | `docs/weekly-spec.md` is the contract: implement it, and update it in the same change if anything must differ (e.g. the block-scalar span nuance, the deck's lack of image placement) |
| **One task, one atomic commit; branch + PR only** | plan tasks accordingly; note the semantic.py gate goes red *within* the editing task and green on commit — do not treat that red as a failure signal (see Pattern 2) |
| **Typed everything / visual fidelity is not optional** | pydantic models end to end; the class map in `weekly-spec.md:224-229` leaves no visual discretion |
| **Abstraction guard: no fixture names in `src/`** | `tests/test_abstraction_guard.py` will scan `weeklyspec.py` |

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python | everything | ✓ | 3.11.15 (`.venv`) | — (CI uses 3.12) |
| pydantic | core models | ✓ | 2.13.5 | — |
| PyYAML (`[config]`) | Weekly Spec parse | ✓ | 6.0.3 | none needed |
| python-pptx (`[pptx]`) | SC-5 deck render | ✓ | 1.0.2 | none needed |
| **openpyxl (`[excel]`)** | **WKLY-04 values-via-export** | **✗** | — | **none — the test cannot run without it** |
| git | the diff-shape gate | ✓ | repo is a git repo, branch `claude/new-session-gw8tik` | — |
| pytest | the suite | ✓ | baseline **601 passed, 64 skipped in 17.45s** [VERIFIED this session] | — |
| import-linter | `lint-imports` contract | ✓ | 2.14 | — |

**Missing dependencies with no fallback:**
- `openpyxl` — install with `.venv/bin/pip install '.[excel]'` **and** add it to a CI job.
  Without it WKLY-04's success criterion has no executable proof anywhere.

**Missing dependencies with fallback:** none.

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | pytest (via `[test]` extra) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — `pythonpath=["src"]`, `testpaths=["tests"]` |
| Quick run command | `.venv/bin/python -m pytest tests/test_weeklyspec.py -q` |
| Full suite command | `.venv/bin/python -m pytest -q` (baseline: 601 passed / 64 skipped) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| WKLY-02 | Four kinds join the union; JSON round-trip resolves each by discriminator | unit | `pytest tests/test_weeklyspec.py::test_new_block_kinds_round_trip_through_the_union -x` | ❌ Wave 0 |
| WKLY-02 | **Fail-loud dispatch**: every union member has an HTML branch; a fabricated non-member raises a teaching error naming the kind | unit (adversarial) | `pytest tests/test_weeklyspec.py::test_block_dispatch_covers_every_union_member_and_fails_loud -x` | ❌ Wave 0 |
| WKLY-02 | **No new CSS**: `render._CSS` is byte-identical to base, and the committed corpora still equal a fresh render | structural + regression | `pytest tests/test_publish.py tests/test_modulesite.py -q` | ✅ exists |
| WKLY-02 | **Verbatim narrative with real spans**: each `NarrativeItem.text` equals the parsed YAML value byte-for-byte; each claim is content-addressed, non-stale, re-sliceable, and entailed on the gate's **strict** branch | unit | `pytest tests/test_weeklyspec.py::test_narrative_is_byte_verbatim_with_real_spans -x` | ❌ Wave 0 |
| WKLY-02 | **Planted-editorialization guard**: a fixture whose highlights contain a summarizable pair, an out-of-order pair, and a mergeable pair — assert the surface contains each line **separately, in file order, byte-identical**, and that no block text exists that is not a substring of the authored file (excluding declared connective constants) | unit (adversarial) | `pytest tests/test_weeklyspec.py::test_composer_never_editorializes -x` | ❌ Wave 0 |
| WKLY-02 | **Span-swap regression** (Pitfall 1): a value duplicated across two sections traces to the correct line each time; spans strictly ascend in file order | unit (adversarial) | `pytest tests/test_weeklyspec.py::test_duplicate_values_trace_to_their_own_occurrence -x` | ❌ Wave 0 |
| WKLY-02 | `config:` values appear in no claim and no block text, but are carried on the typed spec | unit | `pytest tests/test_weeklyspec.py::test_config_never_in_claims -x` (port `test_casespec.py:274-290`) | ❌ Wave 0 |
| WKLY-02 | Absences disclosed — incl. "no lowlights authored"; each unknown top-level key raises a teaching error | unit | `pytest tests/test_weeklyspec.py::test_missing_honesty_and_schema_teaching_errors -x` | ❌ Wave 0 |
| WKLY-02 | Draft on arrival; `publish()` without approval raises; state does not advance | unit | `pytest tests/test_weeklyspec.py::test_surface_is_draft_and_cannot_publish_without_gate -x` | ❌ Wave 0 |
| WKLY-03 | **Unrepresentable provenance-less asset**: `AssetBlock(evidence=[])` and `AssetBlock()` without `asset` both raise `ValidationError` | unit (type-level) | `pytest tests/test_weeklyspec.py::test_assetblock_without_provenance_is_unrepresentable -x` | ❌ Wave 0 |
| WKLY-03 | **All routing conditions** — parametrized over the 4 `missing[]` rows + the 2 reference rows + the happy row: each asserts (a) no `AssetBlock` for that key, (b) the **exact** disclosure string from `docs/weekly-spec.md`, (c) for the root-escape row a `ValueError` and **not** a `missing[]` entry | unit (adversarial, parametrized) | `pytest tests/test_weeklyspec.py::test_asset_routing -x` | ❌ Wave 0 |
| WKLY-03 | Content-address substitution: record describes image A, image B on disk → not placed | unit (adversarial) | `pytest tests/test_weeklyspec.py::test_asset_routing[hash-mismatch] -x` | ❌ Wave 0 |
| WKLY-03 | The image file is never opened for anything but hashing (no decode); the loader writes nothing | structural | `pytest tests/test_weeklyspec.py::test_loader_is_read_only -x` (assert mtime/size unchanged; assert no Pillow/imghdr import in the module text) | ❌ Wave 0 |
| WKLY-04 | Values via ADAPT-03: a synthetic `.xlsx` → `resolve("excel").distill()` → traced claims → the weekly's KPI/claims blocks, every claim content-addressed | integration | `pytest tests/test_weeklyspec.py::test_bi_values_arrive_through_the_existing_excel_adapter -x` (**needs `[excel]`**) | ❌ Wave 0 |
| WKLY-04 | **No new adapter module**: `src/newsletters/adapters/` gains no file; `weeklyspec.py` contains no openpyxl/xlsx parsing | structural | `pytest tests/test_weeklyspec.py::test_no_new_adapter_module -x` | ❌ Wave 0 |
| WKLY-04 | **ADAPT-05 untouched**: `git diff <base-ref> -- src/newsletters/adapters/powerbi*` is empty | structural (git) | `pytest tests/test_weeklyspec.py::test_powerbi_adapter_is_untouched -x` | ❌ Wave 0 |
| SC-5 | **Byte-identical double compose**: two `build_weekly_report` calls over two independent loads produce identical `model_dump_json()`; `created == EPOCH_ZERO`; `review.state is DRAFT` | unit | `pytest tests/test_weeklyspec.py::test_double_compose_is_byte_identical -x` | ❌ Wave 0 |
| SC-5 | **Slots derivation determinism**: `weekly_slots(surface)` is byte-identical across calls, key order stable, every key `NL_`-prefixed, no empty/blank value lists, and empty sections **omitted** rather than padded | unit | `pytest tests/test_weeklyspec.py::test_weekly_slots_are_deterministic_and_never_padded -x` | ❌ Wave 0 |
| SC-5 | End-to-end deck: composed weekly + a synthetic template renders twice to equal `part_digest` (and equal bytes in-process), carries the marker, and is Draft-watermarked | integration | `pytest tests/test_weeklyspec.py::test_weekly_renders_to_a_deterministic_draft_deck -x` (**needs `[pptx]`**) | ❌ Wave 0 |
| gate | **Review gate frozen**: the eight gate functions' source digests match their pins; the `semantic.py` diff against the milestone base has **zero deleted lines** | structural | `pytest tests/test_semantic_gate_frozen.py -q` | ❌ Wave 0 |

**Non-vacuity is mandatory for every adversarial test** (RETRO rule "assert the inversion, or you
have not asserted the condition"): each guard above must have a sibling arm proving the scanner
fires — e.g. the editorialization guard must catch a *planted* paraphrase inserted into a copy of
the composed surface, exactly as `test_abstraction_guard.py::test_guard_detects_planted_leak` does
for the abstraction scanner.

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_semantic.py tests/test_render.py -q`
- **Per wave merge:** `.venv/bin/python -m pytest -q` — **and read the skip count**, not just the colour
- **Phase gate:** full suite green with **0 unexpected skips** (i.e. after `pip install '.[excel]'`,
  the 64 excel skips must become passes), plus `lint-imports`, plus the CI job that actually runs
  the new module.

### Wave 0 Gaps

- [ ] `tests/test_weeklyspec.py` — the whole proof suite above (covers WKLY-02/03/04 + SC-5)
- [ ] `tests/test_semantic_gate_frozen.py` — the replacement for the vacuous byte-diff gate
- [ ] `tests/fixtures/weekly/weekly-full.yml` — all eight keys, a block-scalar highlight, a
      recognition with a `source:` and one without, a team member with and without a `photo:`,
      three assets (one clean, one values-without-link, one provenance-incomplete), a `config:`
      subtree with values the guard can prove never leak
- [ ] `tests/fixtures/weekly/weekly-sparse.yml` — `week` + `module` only (every other absence
      disclosed, including "no lowlights")
- [ ] `tests/fixtures/weekly/*.png` — reuse the 1×1 PNG byte literal at
      `tests/test_pptx_adapter.py:35-41` (no Pillow, deterministic) rather than committing binaries,
      or commit one tiny PNG and pin its sha256 in the fixture YAML
- [ ] **Environment:** `.venv/bin/pip install '.[excel]'`
- [ ] **CI:** a job installing `.[test,config,excel,pptx]` that runs
      `tests/test_weeklyspec.py tests/test_casespec.py tests/test_compose.py tests/test_excel_adapter.py`
      and asserts `0 skipped` (the `pptx` job at `ci.yml:156-176` is the template)
- [ ] Framework install: none — pytest is present

## Security Domain

### Applicable ASVS Categories (Level 1)

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | no identities, no sessions; this is a local library |
| V3 Session Management | no | — |
| V4 Access Control | **yes (human-gate flavour)** | the `Review` gate is the only path to Published; the composer never advances it. Frozen this phase — see Pattern 2. |
| V5 Input Validation | **yes** | `yaml.safe_load` only (never `yaml.load`); exactly-eight-key strict schema with teaching errors; per-field type checks; **path containment** via `resolve()/relative_to(root)` on both the spec path and every `assets[].file` path; asset bytes are hashed, never decoded/parsed |
| V6 Cryptography | **yes (hashing only)** | `hashlib.sha256` for content addressing; no key material, no signing. Do not treat the content address as authenticity — it proves the file matches the record, not that the record is true (the same caveat `pptx_writer.py:32-34` records for the deck marker) |
| V12 Files & Resources | **yes** | read-only file access; no `extract`/`extractall`; no path is ever joined from untrusted content to a write; `render_surface_pptx`'s `out_path` stays caller-supplied (never derived from Surface content — `pptx_writer.py:690-693`) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| YAML deserialization RCE | Elevation of Privilege | `safe_load` only, via `_yaml_loader` (already enforced + tested) |
| Path traversal via `assets[].file` (`../../etc/id_rsa`) | Information Disclosure | `resolve().relative_to(root)` **before** any filesystem call → `ValueError`, a refusal (spec row 4) |
| Symlink escape (a contained path whose target is outside root) | Information Disclosure | `Path.resolve()` follows symlinks before the containment check, so the resolved target is what is tested — **verify this in a test**, it is the non-obvious half |
| Decompression bomb / malicious image | Denial of Service | the loader never decodes an image; it hashes bytes with a streaming-safe stdlib call. Consider a size guard if very large files are plausible |
| Content substitution (record describes A, B is on disk) | Tampering | sha256 re-checked **at placement time**, not trusted from authoring time (spec row 3) |
| Fabricated evidence (an invented `Trace` for an unresolvable `source:`) | Repudiation | routed to `evidence=[]` + a named disclosure; never a minted empty trace |
| Silent block drop (`return ""`) | Tampering / Repudiation | the fall-through becomes a teaching raise (SC-1) |
| Auto-publish via a composer side effect | Elevation of Privilege | composer returns Draft, never calls `publish()`; gate functions frozen and pinned |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The four block models and `AssetRecord` should live in `semantic.py` rather than a new `assets.py` | Pattern 1 | Low — both work; `assets.py` must stay semantic-free to avoid a cycle. A one-line planning decision, not a rework. |
| A2 | Promoting `_SpanMinter` into a shared module is preferable to a private cross-module import | Pattern 3 | Low — a pure move; if `test_casespec.py` reveals a coupling, importing the private name still works |
| A3 | A `checkpoint`-worthy scope call: image placement into the `.pptx` is out of scope this phase | Summary / Pattern 7 | **Medium** — if SC-5 is read as requiring the *image* in the deck, new writer work (`add_picture`, media-order determinism) appears that no plan currently budgets. Confirm with the Editor-in-Chief. |
| A4 | The recommended weekly block order matches the reviewer's expectation | Pattern 5 | Low — cosmetic and testable; change is one list |
| A5 | The joining convention for a recognition's `person`/`reason` in a deck slot (two lines vs. one joined line) | Pattern 7 rule 4 | Low-Medium — a joined line is arguably composer-authored connective text; two lines is the conservative reading of faithful-not-suggestive |
| A6 | Extracting a shared section-assembly helper into `compose.py` will be behaviour-identical under the existing `test_compose.py` | Pattern 5 | Low — the fallback (weekly builds its own strip) is stated |

## Open Questions

1. **Does SC-5 require the asset *image* in the deck, or only the composed Surface rendering
   through the writer?**
   - What we know: Phase 2 shipped text slots only; `bind_slots` refuses non-text shapes; there is
     no `add_picture` in `pptx_writer.py`. Phase 1 *measured* image determinism and
     `docs/weekly-spec.md:290-294` records it, but nothing consumes it.
   - What's unclear: whether "renders through Phase 2's writer to a deck" is satisfied by a
     text-only deck derived from a Surface that *contains* `AssetBlock`s.
   - Recommendation: plan for text-only (caption/alt into a slot), record the gap explicitly in
     `docs/weekly-spec.md`, and raise it as a `checkpoint:human-verify` before the SC-5 task.

2. **What is the milestone base ref for the diff-shape gate?**
   - What we know: the current gate uses `HEAD`, which makes it vacuous in CI.
   - Recommendation: `git merge-base HEAD origin/main` computed in the test, with a clear skip-with-
     reason if no remote is present — never a silent pass.

3. **Should the empty-slot omission be surfaced to the operator more loudly than `missing[]`?**
   - What we know: a weekly with no lowlights omits `NL_LOWLIGHTS`; a template that carries that
     slot then fails `bind_slots`'s unfilled-slot refusal with a message about templates, not about
     an unauthored section.
   - Recommendation: keep the behaviour (it is correct and fail-loud) and make the composer's
     docstring say so; consider a `missing[]` note that names the slot consequence.

4. **Which weekly fixture identifiers go on the abstraction-guard denylist?**
   - Recommendation: add the weekly fixture's asset keys/person names to
     `tests/test_abstraction_guard.py` alongside `_CASESPEC_CONFIG_VALUES`, so the guard stays
     non-vacuous for the new corpus.

## Sources

### Primary (HIGH confidence — executed against the live repo in this session)

- `.venv/bin/python -m pytest -q` → **601 passed, 64 skipped, 17.45s** (baseline confirmed)
- `.venv/bin/python -m pytest -q -rs` → all 64 skips are `[excel]`/openpyxl skips
- Probe 1: `casespec._SpanMinter` over a full weekly-shaped YAML → 17/17 gate-entailed claims with
  real spans (quoted scalars, block scalar, mapping-in-sequence, list-in-mapping-in-sequence,
  mapping-of-mappings)
- Probe 2/3: out-of-file-order minting swaps spans for a duplicated value; both claims still pass
  the gate (`team.name → LINE 3`, `rec.person → LINE 6`)
- Probe 4: proposed pydantic models — `evidence` `too_short`, `asset` `missing`, discriminated
  round-trip byte-identical
- Gate experiment: appended one line to `semantic.py` → `test_faithfulness_..._untouched` FAILED;
  `git checkout --` → passed (proving working-tree-only scope)
- CSS experiment: planted `.nl-scratch{color:red}` in `_CSS` → `test_committed_rev1_equals_fresh_build`
  and `test_committed_work_equals_fresh_build` both FAILED
- `grep -n "add_picture\|image" src/newsletters/pptx_writer.py` → no image code path
- `grep -n excel .github/workflows/ci.yml` → no match (no CI job installs `[excel]`)
- `grep -rn "get_args\|__args__\|eleven" tests/` → no count-pinning test exists
- `pip list` → pydantic 2.13.5, PyYAML 6.0.3, python-pptx 1.0.2, **no openpyxl**

### Primary (HIGH confidence — in-repo authority, read in full)

- `docs/weekly-spec.md` — the contract (schema, 7 rules, 4 block kinds, `AssetRecord`, routing table,
  class map, dispatch contract)
- `src/newsletters/casespec.py`, `semantic.py`, `compose.py`, `pptx_writer.py`,
  `render.py:500-620,724-914`, `swimlane.py:120-160`, `_yaml_loader.py`,
  `adapters/excel_adapter.py:1-86`, `distill/ports.py`, `distill/registry.py`,
  `distill/faithfulness.py:1-80`, `__init__.py`
- `tests/test_casespec.py`, `test_compose.py:520-552`, `test_abstraction_guard.py:1-210`,
  `test_pptx_writer.py:134-160,1100-1140`, `test_publish.py:138-180`, `test_excel_adapter.py:1-40`,
  `test_pptx_adapter.py:30-45`
- `.planning/ROADMAP.md` Phase 3 (5 success criteria), `.planning/phases/03-weekly-compose/03-CONTEXT.md`
- `.github/workflows/ci.yml`, `.importlinter`, `pyproject.toml`
- `CLAUDE.md`, `RETRO.md:7-78`, `docs/architecture.md:15-40`, `docs/design-system.md:94-100`

### Secondary (MEDIUM confidence)

- None required.

### Tertiary (LOW confidence)

- None. **No web search was performed** — this phase extends live in-repo mechanisms, and every
  claim above is either executed or cited to a file and line in this repository.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; every version read from the live `.venv`
- Architecture: HIGH — every mechanism read in full and the load-bearing ones executed
- Pitfalls: HIGH — Pitfalls 1, 2, 3 and the CSS constraint were each reproduced by experiment, not
  inferred
- Scope gap (deck image placement): MEDIUM — the absence of code is verified; the *intent* of SC-5
  is a human call (Open Question 1)

**Research date:** 2026-08-29
**Valid until:** 2026-09-28 (stable, in-repo domain; invalidated early only by a change to
`semantic.py`, `casespec.py`, `render._CSS`, `pptx_writer.py` or `.github/workflows/ci.yml`)
