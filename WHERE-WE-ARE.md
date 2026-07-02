# WHERE WE ARE

> The human compass. Newest entry on top. If you read only this file, you should know where the
> build is, what's decided, and why. Updated whenever the state of the world changes — a stale
> compass is a bug. Machine-state (phases/plans/metrics) lives in `.planning/STATE.md`; this file
> is the plain-language "where + why" it complements.

## Where we are right now

**2026-07-02 (evening) — v1.1 FORMALLY CLOSED. The 10-round deep-review loop is COMPLETE (10/10,
PRs #9–#17, every round its own reviewable PR).** The milestone audit **PASSED** (12/12
requirements, three-source cross-check, 4/4 phases verified); the milestone is archived
(`.planning/milestones/v1.1-*`), logged (`MILESTONES.md`), retrospected (`RETROSPECTIVE.md`),
synthesized (`.planning/reviews/2026-07-02-deep-review/10-synthesis.md` — read this first).
626 tests green; all three corpora clean; the collaboration contract is canon
(`docs/collaboration.md`: roles as hats — Editor-in-Chief/Bureau Chief/Reporters/Maintainer —
guarded by test). **One known limitation:** the `v1.1` tag exists locally only — this
environment's git proxy drops tag pushes; the maintainer creates it in one click (Releases →
new tag `v1.1` @ `979f191`; noted on PR #17). **Three decisions wait on the
Editor-in-Chief/Maintainer:** (1) the B1–B20 fix-batch PR (12 one-test guards — see
`reviews/07-tests-as-promises.md`); (2) integration→main merge (the branch holds the complete,
closed milestone); (3) the next milestone (evidence: DEF-04 or DEF-05, DEF-11 gated on mandatory
content-addressed traces per `reviews/05-trust-invariants.md`). A fresh session starts from
`.planning/loops/2026-07-02-deep-review/RESUME-PROMPT.md` — the repo alone carries the full record.

**2026-07-02 (after the morning) — CLIENT-READABLE REVIEWS SHIPPED, then a 10-round DEEP-REVIEW
LOOP to close v1.1 honestly.** Two things happened after the milestone's code was done. First, JJ's
morning review landed a hard truth — the Signals-dispatch PR bodies were hype-free but still
unreadable to the person they were for ("I don't understand what the shit is going on") — so **PR #8**
added a mandatory plain-terms **"Start here"** section (what we built / why it matters / how to
review) and deployed the rendered report corpora to Pages, so review means clicking an artifact, not
diffing. Second, the milestone was **functionally done but never formally closed per GSD** (no
per-phase VERIFICATION/VALIDATION/**LEARNINGS**, no milestone archive/tag, and STATE/ROADMAP/PROJECT
carried internal contradictions). The fix is a **10-round deep-review /loop** (PRs #9–#15) where each
round's deep review *is* the capture vehicle — reviewing Phase N produces its honest triad. Rounds so
far: **1–4** the per-phase retroactive triads (all verified; accepted gaps recorded, not fabricated);
**5** the 12 trust invariants mapped as one system (weakest link named: the Option-A structural
faithfulness fallback passes an un-addressed trace with no content check); **6** the 16 GSD config
toggles reconciled (4 honored / 2 backfilled / 6 accepted / 5 maintainer recommendations — lesson:
independence, not correctness, is what a fresh-context review buys); **7** the whole suite read as a
promise ledger (62 promises, 11 unguarded arms, 2 vacuous guards → backlog **B1–B20**, all one-test
remedies); **8** (this round) ontology & semantic drift across total history + these compass fixes.
The standing lenses every round: delta-to-reality, semantic drift, total-history honesty. **Next:
Round 9 — the collaboration contract (roles as hats: Editor-in-Chief / Bureau Chief / maintainer /
…, `docs/collaboration.md` + a presence guard mirroring the voice guard); Round 10 — the formal GSD
close (`audit-milestone` → `complete-milestone`: MILESTONES.md, archive, RETROSPECTIVE, tag v1.1 on
the integration branch — the maintainer merges to `main`).**

**2026-07-02 (morning) — MILESTONE v1.1 CORE COMPLETE: all 4 phases shipped, verified, and
squash-merged to the integration branch (`claude/swimlane-report-composer-1i8vxt`). `main`
untouched. 622 tests green; every enforced gate re-run independently on the merged result.**
The composer JJ asked for exists and is config-driven end to end: **Phase 1** (PR #4) — the
traced YAML loader `swimlane.py`: every scalar content-addressed to the raw file text or
disclosed, PyYAML behind `[config]`, the abstraction guard enforcing "models in code, specifics
in config" (it fired on three real leaks during the night — the principle is a test, not a
convention). **Phase 2** (PR #5) — `compose.py`: one Draft `Surface(REPORT)` per module,
compose-time Δ from two traced endpoints (declared-but-single endpoint disclosed; point-in-time
`value:` never falsely flagged — the endpoint accumulator carries the movement form only),
sourced-or-omit quote, fanout stub, `R-NNN` via reused Ledger, both research gate-holes closed
by adversarial tests with zero edits to existing gates. **Phase 3** (PR #6) — the worked
synthetic `module-a` report rendered at `content/module/site/report-module-a.html` (36
claim-beside-trace rows, populated honesty panel, R-001, own ledger), `newsletters check
--corpus module` proven to fire on a planted blocker; method-docs sub-task skipped honestly
(`_incoming/` absent). **Phase 4** (PR #7) — `/gsd ship` PR bodies are now Signals dispatches
(five sections, verbatim gate output, no fact-asserting fallbacks), guarded by test against
installer reversion. **One stall JJ caught live:** a backgrounded CI-wait that could never
succeed (container restart + dead unauthenticated curl + watching a docs-only SHA that never
triggered CI) — rules hardened in `RETRO.md` 2026-07-02: background monitors notify, never
sequence. **Next: JJ's morning review of PRs #4–#7 (merged into the integration branch) and
the integration→main decision, which JJ owns.** After that, the §7 deferrals (DEF-01..12 in
REQUIREMENTS/ROADMAP) are the menu — the owner-audit workflow (DEF-04) or the quarter-editorial
re-cut (DEF-05) are the natural next loops; the DistillPort AI backend (DEF-11) stays
eval-first and deliberately last.

**2026-07-02 — MILESTONE v1.1 STARTED: Swim-Lane Module Report (Stage A locked with JJ; Stage B
running overnight).** v1.0 is complete and archived (Phases 1–13 shipped; Phase 14 → DEF-12). The
new milestone builds the **missing composer**: a config-driven machine that cuts one owned module
across its swim lanes into a Draft, evidence-traced `Surface(REPORT)`. **JJ's locked principle:
ABSTRACT EVERYTHING** — models in code, module/lane/owner specifics in YAML config, zero fixture
names in `src/` (enforced by test). Exactly 4 phases (`.planning/ROADMAP.md`): (1) traced YAML
loader `swimlane.py` — every value content-addressed via `Trace.from_source` to the raw YAML text,
read-anchored zero-silent-drops, PyYAML behind a `[config]` extra; (2) composer `compose.py` —
kind-agnostic `SectionBinding` seam, compose-time Δ from two traced endpoints (`delta=None` +
`missing[]` when an endpoint is absent, never a fabricated 0), own `content/module/ids.json`
ledger, Draft only; (3) worked synthetic `module-a` into the Library as a third `module` corpus;
(4) Signals-voice PR bodies from the `ship` workflow. Research (4 agents + synthesis, committed in
`.planning/research/`) found **two real holes in the existing gate** — `_published_claims()` scans
only `ClaimsBlock` (Hole A) and un-addressed traces pass entailment free (Hole B) — closed by new
adversarial tests in Phases 1–2, never by editing `faithfulness.py`/`coverage.py`. Gate policy:
enforced set = pytest / lint-imports / `newsletters check` (all corpora) / byte-stable double-render
/ bare-install CI (all green at the 2026-07-02 baseline, 574 tests); mypy/black/isort = no-NEW-
failures vs the recorded baseline (repo pre-dates a global format pass — 9 mypy errors, ~59
unformatted files are v1.0 debt, out of scope). Run model: one draft PR per phase off integration
branch `claude/swimlane-report-composer-1i8vxt` (the session-designated branch, serving the seed's
`milestone/swimlane-report` role), squash-merged phase-by-phase; **`main` untouched**; max 2
attempts per phase; Phase-1 circuit breaker stops the run if the loader isn't cleanly green.
Synthetic data only — no real org/tool/metric/site/program names anywhere. **Next: Phase 1 —
plan-phase → execute-phase → self-verify → ship.**

**2026-06-19 — Phase 13 SHIPPED & VERIFIED (3/3): Problem Lifecycle Entity (PROB-01/03). THE CUT IS
COMPLETE — Phases 1–13 all shipped & verified.** A first-class typed `Problem` sits ABOVE `Source`
(`src/newsletters/problem.py`, AI-free leaf, acyclic — `semantic` never imports it): aggregates ≥1
traced Source (≥1 enforced), carries its own `ProblemState` ladder (Identified→Owned→In Progress→
Resolved→Verified, re-open the only backward edge), advanced ONLY through a human-gated `transition(to,
by)` (empty actor → raises; illegal move → raises; never auto-advances). It is a **legibility layer,
NOT a tracker** — the no-write-back boundary is proven FOUR ways (a 2nd import-linter contract
`forbid-external-write-in-problem` → "2 kept, 0 broken"; a runtime delta-guard; an API allow-list with
no Jira/ADO/export path; a spine-unchanged `content_hash` proof). The three state axes stay provably
distinct (terminology guard; verb `transition`). The verifier caught a real loophole — a bare
`p.state = …` bypassed the gate (mutable pydantic model) — **closed** with a `__setattr__` guard so
`transition` is the *literal* sole mutator (claim==reality). 573 tests pass. PROB-02/04 (portfolio +
board) are Phase 14, deliberately deferred. **Next: UAT — open the PR + publish the live GitHub Pages
site.**

**2026-06-18 — Phase 12 SHIPPED & VERIFIED (3/3): Learning & Onboarding Surface (LEARN-01/02/03).** The
**5th surface type**. A `learning` SurfaceTemplate (distance 4, GREEN) + a typed `GlossaryBlock` whose
`GlossaryTerm.definition` IS a traced `Claim` (a `str`/invented definition raises `ValidationError` —
faithfulness enforced by the type, not discipline). The `learning_surface()` preset re-cuts a reviewed
record for a newcomer: ordered no-JS progressive-disclosure sections (Start here / Prerequisites / Going
deeper), an in-context glossary (each term defined by its traced claim), prerequisite links — it
SELECTS/ORDERS/LINKS existing traced claims and **never invents prose** (verifier proved *VIOLATIONS:
NONE*; un-glossable terms → `missing[]`/honesty panel). `OnboardingPath` sequences records into an
ordered track (NOT a Surface, no review gate). Dogfood: `report-datamodel` re-cut → **L-001** (Draft) +
the `show-ep01 → report-datamodel → learning-datamodel` track, both built into the site. Notably, an
executor tried to *publish* the learning surface and the **merge-block gate caught it** (open `missing[]`
→ blocker) → reverted to Draft: the system enforced its own rule. 559 tests pass; AI-optional +
byte-stable + zero-external-calls held. **Next: Phase 13 — Problem Lifecycle Entity (the final phase).**

**2026-06-18 — Phase 11 SHIPPED & VERIFIED (3/3): Work-Surface Installation (WORK-01/02/03).** The
whole pipeline is now proven on a real codebase — by dogfooding on Newsletters' own source. New
`worksurface.py`: `capture_files()` (a read-only, stdlib, no-network local-file → `Source` ingest;
proven read-only by mtime+sha256), `build_work_report` (a hand-authored Report whose 7 claims
content-address VERBATIM to real repo files — `CLAUDE.md`/`semantic.py`/`capture.py`/`architecture.md`
— with a deliberate paraphrase honestly routed to `missing[]`, never fabricated; Draft, no auto-publish),
and `build_work_site` → `content/work/site/` reusing the Phase 9/10 provenance/lineage devices
(claim→repo-file links, verbatim trace-spans, honesty panel, masthead `derived from`/`captured via`,
fan-out). `--corpus {rev1|work}` runs the SAME merge-block gate on the work corpus (clean→0, planted
blocker→1). **No-external-call is now LITERAL:** the Google-Fonts `@import` is gone — the three SIL-OFL
fonts (DM Serif Display / Instrument Sans / DM Mono) are vendored as self-hosted `@font-face` woff2 +
`OFL.txt` across both sites (zero auto-loading external URLs; full fidelity kept). 537 tests pass;
AI-optional + byte-stable + rev1-untouched held. **Next: Phase 12 — Learning & Onboarding Surface.**

**2026-06-18 — Phase 10 SHIPPED & VERIFIED (3/3): Reviewer Surfacing & Merge-Block Gate (PROV-03/04).**
The human review gate is now REAL, not a rubber stamp. (1) Every reader surface renders an amber
"what's not here / not verified" honesty panel (`Surface.missing[]` + the Source `unextracted[]`) and
shows each claim **next to its verbatim `Trace.span` by default** (no click, no JS) with an inline
STALE/unfaithful badge — the unfaithful thing is visible without a click. (2) A new pure AI-free
`review.py` (`review_blockers` → `Blocker{stale|unentailed|open_missing}`, published-only scope, reusing
`Claim.is_stale` + `SpanContainmentFaithfulness.entails`) backs a `newsletters check` CLI that exits
nonzero on any blocked published surface, wired as a **third CI job** (`merge-block`, bare `.[test]`,
AI-free) so an unsafe surface cannot merge. Proven to BLOCK on a live crafted corpus (STALE / un-entailed
/ open-missing → exit 1; clean → 0; Draft/In-Review exempt) — a gate that only sees clean input proves
nothing. 524 tests pass; no-auto-publish gate unchanged (only the additive `Surface.missing` field);
AI-optional + byte-stable build held. CI jobs: `[bare-install, merge-block, import-linter]`.
> 📌 Forward note: `newsletters check` enumerates the in-code dogfood corpus; wire an on-disk/work
> corpus into the gate in **Phase 11** (carried, not a Phase-10 gap). **Next: Phase 11 — Work-Surface Installation.**

**2026-06-18 — Phase 9 SHIPPED & VERIFIED (5/5): Rev2 Site IA, Navigation & Source Links
(SITE-02..06).** The deployed site now has a real **8-section marketing Home** at `index.html`
(recreated from the approved `design-reference` prototype, design-system tokens matched), a separate
**Library status-board** at `library.html` (3 CSS-grid columns by gate state — `Page.gate` now
load-bearing — no JS), **four nav destinations** (Start here/Newsletters/Articles/The Show) +
breadcrumbs + within-type prev/next, and **working source links** (cited file → repo blob, session →
in-site anchor, neither → plain text — never a dead link) with `FanoutLink.href` populated + SVG fan-out
anchors. All output regenerates from `render.py` (generated marker + byte-stable; SITE-06). 502 tests
pass. UI audit PASS 23/24 (the only <prototype gap is the static no-JS persona demo, deferred to the
`web/` phase). **Two issues my independent verification caught + fixed:** (1) a 09-01 *stale-green* —
the executor ran pytest before regenerating content, so `test_existing_links_do_not_rot` (which reads
the built dir) didn't see the new `library.html`; (2) SC4 links were well-formed but **404'd** (stale
`nneibaue` handle vs the real `johnair01/newsletters`; two locators missing the `src/newsletters/`
prefix) — fixed + guarded by a test that every repo-blob link points at a file that EXISTS. **Next:
Phase 10 — Reviewer Surfacing & Merge-Block Gate.**

**2026-06-18 — Phase 8 SHIPPED & VERIFIED (2/2): Site Content Model & Stable IDs (SITE-01).** The
pivot from extraction to surfaces. New typed `Site → Collection → Page` model (`src/newsletters/site.py`,
stdlib+Pydantic, AI-free) + a stdlib `slugify` + an **append-only ID ledger** (`content/rev1/ids.json`,
`slug → {ref,type,issue,date}`, sort_keys). Stable per-type refs (`R-001`..`R-004`, `EP01`, `A-001`;
newsletters cadenced) are **content-derived / ledger-assigned, never positional** — the Library no
longer numbers by `enumerate` (`{i:02d}` rot removed); it renders `Page.ref`. Proven: reorder + insert
→ every existing `slug→ref` byte-identical, links resolve, new surface gets a fresh ref
(`test_reorder_and_insert_preserve_ids` + `test_existing_links_do_not_rot`). Filenames + ledger stay
byte-stable on rebuild. Spec gap FILLED (hard rule): the ID convention is now in `docs/surfaces.md` +
the Site/Collection/Page model in `docs/architecture.md`. 458 tests pass; contracts green. Scope held —
NO Home/nav/gate-board yet (that's Phase 9/10); `Collection` groups by type, `Page.gate` merely carried.
**Next: Phase 9 — Rev2 Site IA, Navigation & Source Links.**

**2026-06-18 — Phase 7 SHIPPED & VERIFIED (3/3): Power BI adapter. ALL FOUR ADAPTERS DONE (Phases 4–7).**
Registry = `['email','excel','powerbi','pptx']`; 448 tests pass. Two events worth remembering (RETRO
2026-06-18): (1) the Phase-7 Wave-1 background agents **stalled ~16h** when the remote container
idle-reclaimed mid-flight — recovered by rebuilding the missing `_pbir.py` inline from its committed
test; rule hardened: a completion notification ≠ liveness, commit/push every task, diagnose the live
repo on long silence. (2) The verifier caught a **real silent-drop bug** — `_tmdl.py` read `model`/
`ref table` lines then dropped them (the golden's `claims+misses==units` identity couldn't see it; the
fixture was authored *around* the bug). Fixed: recognize `model` (props → `Model.*`), extract `ref`
references, DISCLOSE any orphan/unknown line (`_R_TMDL_UNPARSED`), and anchor the golden to LINES READ
(`test_no_line_is_read_but_undisclosed`). The no-silent-drops invariant now holds against the source,
not just the parser's output. **Next: Phase 8 — Site Content Model & Stable IDs** (pivot from
extraction to the site/reviewer surfaces).

**(superseded) 2026-06-18 — Phase 7 BUILD COMPLETE (4/4 plans), awaiting verification.**
All four 07 plans are executed and green. `PowerBiAdapter` (registered `"powerbi"`) is **stdlib-only —
ZERO new dependency** (the headline difference from excel/pptx, which need openpyxl/python-pptx): a
PBIP project (plain-text TMDL semantic model + PBIR JSON report) becomes a content-addressed
`Distillation`. The Wave-1 stdlib `_tmdl` parser (indent-structured TMDL → verbatim units; a measure's
DAX is extracted as **text, never evaluated**) and `_pbir` reader (page/visual text + the row-cap
detection taxonomy) compose onto the shared `normalize()` spine. **Fail-loud is the headline behavior:**
every row-cap/aggregation signal routes to a precise `_R_*` `unextracted[]` reason (`_R_TOPN` /
`_R_FILTER` / `_R_AGGREGATED` / `_R_MEASURE_VALUE` / `_R_DIRECTQUERY` / `_R_ROWLIMIT`), and a
categorical `_R_NO_DATA_ROWS` fires once per model export → `Coverage.complete=False` (PBIP is a
*definition* format with no data rows; a value is **never fabricated**). A `.pbix` binary defers to
`_R_PBIX_BINARY` (the ZIP is never decompressed; pbixray DEFERRED). **07-04 (this plan)** authored the
golden corpus: a hand-authored, byte-reproducible PBIP/TMDL fixture tree written with stdlib
`write_text` (**no authoring dependency** — the big win over the excel/pptx fixtures) + a `.pbix`
deferral fixture, and a golden test that drives the LIVE adapter to PROVE zero silent drops (21 units →
21 content-addressed verbatim claims), the exact row-cap taxonomy (pinned by driving, not guessing —
A1), conformance, Source determinism (EPOCH_ZERO), and round-trip coverage parity. The golden has **no
skip-mark** (stdlib-only → runs on a bare install). **447 tests pass, 1 xfailed**; mypy clean;
AI-isolation `1 kept / 0 broken`; registry now includes `powerbi`. Next: run the Phase-7 verification
gate, then ship.
> 📌 The slide/cell/object locator still lives in the transcript prefix (recoverable via the
> content-addressed offset), not a typed `Trace.locator` field — the consistent accepted pattern since
> Phase 4; promote it to a typed field when the reviewer/site surfaces need rich locator display.

**2026-06-17 (night) — Phase 6 SHIPPED: PowerPoint adapter (3rd adapter).**
✅ **Phase 6 — PowerPoint Adapter** (ADAPT-04/06, verified 4/4). `PptxAdapter` (registered `"pptx"`,
`python-pptx` behind a lazy `[pptx]` extra) walks slides/shapes in order, **recurses grouped shapes**
(extracting readable members, the group node itself neither claim nor drop), extracts
title/body/textbox/table-cell/notes text as per-paragraph claims via the shared `normalize()`, and
routes everything the high-level API can't read — **SmartArt (detected via `graphicData @uri`), charts,
pictures, media, OLE** — to `unextracted[]`. 9 byte-reproducible fixtures (incl. SmartArt + nested
groups) prove zero silent drops with exact nested accounting. Also ✅ the **timestamp front-fix (L1)**:
a shared `deterministic_timestamp`/`EPOCH_ZERO` helper killed the `now()` fallback across ALL adapters
(email/excel/pptx) — excel needed a raw-XML `intrinsic_created` read because openpyxl *fabricates*
`created`; python-pptx doesn't. This fully closed the Phase-5 determinism edge. 383 tests pass;
AI-optional + acyclic-import contracts held; registry = `['email','excel','pptx']`.
> 📌 **Forward note (non-blocking, all adapters):** the slide/shape/`Sheet!A1` locator lives in the
> transcript prefix (recoverable via the content-addressed offset), not a typed `Trace.locator` field —
> a consistent accepted pattern since Phase 4. Candidate enhancement: promote it to a typed field when
> the reviewer/site surfaces (Phase 9/10) need rich locator display — that's a cross-adapter
> `normalize()` change, deliberately out of adapter-phase scope. See `06-VERIFICATION.md`.

**2026-06-17 (late+) — Phase 5 SHIPPED: Excel adapter + the adapter pattern hardened.**
✅ **Phase 5 — Excel Adapter** (ADAPT-03/06, verified 3/3). `ExcelAdapter` (registered `"excel"`,
`openpyxl` behind a lazy `[excel]` extra) double-loads `.xlsx` (formula view + data view), serializes
the workbook into a canonical `Sheet!A1\tvalue` transcript, canonicalizes values faithfully
(bool→TRUE/FALSE, int→`str`, float→`repr`, dates→`isoformat`), anchors merged cells once, and routes
everything openpyxl can't resolve — **uncomputed formula cells (no cache), error cells, charts,
images** — to `unextracted[]`, never a fake `0`. 8 byte-reproducible golden fixtures prove zero
silent drops. Also ✅ **Task Zero** (carried Phase-4 fix): adapter `unextracted[]` now travels on a
typed `Source.extraction` carrier (leaf `locators.py`, excluded from `content_hash`), so coverage
survives a `Source` JSON round-trip — proven by a parity matrix passing for BOTH email + excel; the
in-memory dict is gone; an R2 safety-net reports `complete=False` (never false `complete=True`) when
coverage can't be reconstructed. 280 tests pass; AI-optional + acyclic-import contracts held.
> ⚠ **Carried risks (non-blocking) → address at Phase 6 front (before PPTX copies the pattern):**
> (1) **Adapter timestamp determinism** — `Source.timestamp` is sourced from the document's intrinsic
> date (email `Date`, xlsx `properties.created`); if a real-world file lacks it, the adapter falls back
> to `now()` → non-deterministic output (breaks the determinism/parity property). Add a deterministic
> fallback (fixed epoch / content-derived), applied across ALL adapters. (2) The image→`unextracted`
> branch is correct but not yet exercised e2e (openpyxl drops images on reload; no real image in corpus)
> — add a real-image fixture when convenient. See `05-VERIFICATION.md`.

**2026-06-17 (late) — Phase 4 SHIPPED: first adapter + the shared faithful normalizer.**
✅ **Phase 4 — Shared Adapter Normalizer & Email Adapter** (ADAPT-01/02/06, verified 3/3). The
faithful-extraction rule now lives in exactly ONE place: `adapters/normalize.py` (the only code that
calls `Trace.from_source`) locates each raw unit verbatim in `Source.transcript` and content-addresses
it; non-locatable → `unextracted[]`. The stdlib-only `EmailAdapter` (registered `"email"`) parses
`.eml` via `email.policy.default`, builds a canonical decoded transcript, extracts header + paragraph
claims, applies a deterministic charset ladder (declared→utf-8→latin-1 strict) with U+FFFD detection,
HTML-only emit-both, and routes U1–U8 to `unextracted[]`. 8 golden `.eml` fixtures prove the
**zero-silent-drops** identity (`#claims + #unextracted == #units walked`). No new dependency; 177
tests pass; AI-optional contract held.
> ⚠ **Carried risk → harden in Phase 5 (task zero):** adapter `unextracted[]` drops live in an
> in-memory dict keyed by `source.id`, so re-`distill()`ing a *persisted* `Source` on a fresh adapter
> silently loses U1–U7 drops and falsely reports `complete=True`. Body claims still mint faithfully, so
> Phase 4 passed — but the pattern must be hardened (coverage reconstructable from the `Source` +
> round-trip parity test) BEFORE the Excel/PPTX/PowerBI adapters copy it. See `RETRO.md` 2026-06-17.

**2026-06-17 (eve) — Phases 1–3 SHIPPED end-to-end. The trust spine is now formally enforced.**
Running the Rev2 roadmap autonomously (discuss → plan → execute → verify per phase, gates re-run
independently each time, every plan committed + pushed).

- ✅ **Phase 1 — Distill Socket Contract:** one `DistillPort` + registry + zero-AI `ManualBackend` +
  coverage manifest (`unextracted[]`) + conformance suite + the injectable faithfulness seam
  (`FaithfulnessCheck`/`_enforce`). Verified 4/4.
- ✅ **Phase 2 — AI-Optional Packaging Boundary:** core deps cut to `pydantic/typer/sqlmodel`;
  `pydantic-ai` behind `[ai]`; `langsmith/langchain/langgraph` dropped. `.importlinter` forbids
  core→AI; CI (`.github/workflows/ci.yml`) runs a **bare-install** full-pipeline gate + lint-imports
  on every push. This *closed a real leak found in Phase 1* — the bare-install isolation test passes
  strictly (the dev venv's ambient `logfire` pydantic-plugin is the only reason it xfails locally).
  Verified 4/4 (PKG-01..04).
- ✅ **Phase 3 — Content-Addressed Provenance & Faithfulness Gate:** `Trace` now pins SHA-256(full
  source) + char offsets + verbatim span via `Trace.from_source`; **STALE is computed** (live hash ≠
  recorded hash) — editing a source flips dependent claims to STALE, never silent mis-attribution.
  The no-AI **faithfulness gate** (`SpanContainmentFaithfulness`, normalized containment) is defaulted
  at the socket seam so every backend inherits it; unfaithful claims route to `missing[]`, never
  surfaced. Rev1 sample corpus migrated in place (20 traces addressed, 0 stale, build byte-identical).
  Verified 3/3 (PROV-01/02). All stdlib; AI-optional contract stayed green throughout.

**Next step:** Phase 4 — Shared Adapter Normalizer & Email Adapter (research → plan → execute).
The faithful-extraction rule lands in one shared `normalize()`; the Email `.eml` adapter is the first
stdlib adapter, minting traces via `Trace.from_source` (so adapter claims are content-addressed and
come under the strict gate automatically).

> **⚙ OPERATING DIRECTIVE (2026-06-17, reviewer):** *Run uninterrupted through Phase 13 (then 14).*
> Do **not** ask the reviewer questions unless absolutely necessary (destructive/irreversible, a hard-
> rule conflict, or genuinely unresolvable from spec + research). At **each** phase: **research best-
> known methods first** (dispatch a researcher; cite sources), record decisions in the phase CONTEXT,
> then plan → execute (independent gate re-runs) → verify → close + update this compass. Keep
> committing + pushing every plan. This directive persists across context resets.

**2026-06-17 — A2 design pass routed (no code). The roadmap grew two phases.** A `/gsd-explore`
session settled the long-open A1-vs-A2 question: does Signals stay a pure capture→trust→publish
membrane (A1), or add a first-class Problem/Solution lifecycle layer (A2)? **Decision: A2, scoped as
a *legibility layer*, not a tracker.** The hinge was one test — *someone needs to query across
problems* (bottlenecks across modules; the leadership pattern view), and you can't aggregate over
state you don't model. Two new phases appended (don't touch 1–12): **Phase 13 — Problem Lifecycle
Entity**, **Phase 14 — Problem Board Portfolio Surface**. Reqs PROB-01..04 added. Full rationale +
boundary reconciliation: `.planning/notes/a2-problem-lifecycle-decision.md`. Phase 1 is still the
next thing to *execute*.

**2026-06-14 — Phase 1 planned, peer-reviewed, and replanned. Ready to execute (no code yet).**

- ✅ **Shipped:** GSD installed (`.claude/`), full plan seeded (`.planning/`: PROJECT, REQUIREMENTS
  31 reqs, ROADMAP 12 phases, research). Rev1 spine **merged** onto this branch. `CLAUDE.md` rewritten
  to carry the working method (teaching build). This compass + `RETRO.md` created. **Phase 1 (Distill
  Socket Contract) is planned** — 2 plans, 2 waves — then put through an independent cross-AI review
  (`01-REVIEWS.md`), which caught a real **circular import**; the plans were **replanned** to fix it and
  re-verified by the plan-checker. All SOCK-01..05 + D-01..06 covered. The `DistillPort` shape is now
  resolved in the plans (no longer `[OPEN]`).
- ◐ **In progress:** Nothing mid-flight — at the execute/iterate fork for Phase 1.
- ○ **Not started:** Phase 1 **code** (plans ready). The work-surface interview (real content for
  Phase 11) hasn't happened. The Home 8-section spec needs confirming in writing before Phase 9.

**Next step:** `/gsd-execute-phase 1` — plans verified and committed. Wave 1 builds the leaf
`locators.py`, the `DistillPort`/registry/`Coverage` contract, and the zero-AI `ManualBackend`
end-to-end; Wave 2 adds the conformance suite + the hard-rule tests.

## The truths (load-bearing — break one, it's a conversation, not a commit)

1. **The trust layer is the product, not the generation.** Make work legible *and believable* —
   every published claim traces to evidence; nothing publishes without a human.
2. **AI is optional, never an authority.** The deterministic spine runs with zero AI; AI is a
   swappable backend behind one boundary.
3. **Faithful, not suggestive.** Distil extracts and traces; it never editorialises.
4. **Low-token & generic by default.** Cheapest models; format consistency is the lever that keeps
   extraction cheap; manual authoring is the floor. **Agents are interviewers** — of you, your work,
   your codebase. (Refined 2026-06-14 from "manual-first": there *is* AI at work, just budgeted.)
5. **Teaching build.** Understanding the *why* is the bar; "it works" is not.

## Decisions, and why (teaching log — decide once, don't re-litigate)

- **Faithfulness gate scope — "Option A": strict containment only where there's content-addressed
  evidence; un-addressed traces fall back to structural (is-traced)** (2026-06-17, Phase 3). An
  executor caught that the live capture path mints *empty-span* traces, so a strict "claim text must
  appear in span" rule would falsely reject every Rev1/capture claim — violating *faithful-not-
  suggestive* (no false positives). Resolution mirrors the approved STALE rule: **absence of content-
  addressing means "not applicable," never a false verdict.** So the gate has teeth exactly where
  there's a real verbatim span to check, and **self-strengthens** as the pipeline adopts content-
  addressing. *Accepted scope boundary (forward note, not a gap):* claims born on the live `capture.py`
  path get the structural pass until that path is content-addressed — which happens naturally as the
  **adapters** (Phase 4+) mint traces via `Trace.from_source`. Rejected Option B (harden `capture.py`
  now) as scope creep into a phase whose criteria were already met. Verifier confirmed 3/3 criteria in
  live code; the only reason it flagged `human_needed` was to get this scope call on record — now made.
- **A2 over A1 — model the problem lifecycle, but as a legibility layer, not a tracker** (2026-06-17).
  The scattered `problem→owned→solution→promoted` lifecycle gets a first-class `Problem` entity above
  `Source` *because* someone needs to query the portfolio across problems (A1 can't aggregate state it
  doesn't model). The guardrail that keeps it from becoming a second Jira: **no write-back; solving
  stays external** (`semantic.py` boundary holds) — Signals owns record-legibility, not execution.
  → Phases 13–14, PROB-01..04. **Terminology watch:** this adds a *third* state axis; the existing
  "**promotion chain**" decision below names axis-2 (surface fan-out) — that word now collides with the
  axis-3 lifecycle ladder. Resolve naming before Phase 13 code (seed:
  `promotion-terminology-guard.md`).
- **Merge Rev1 in, don't rebuild** — the spine already existed on `claude/magical-einstein-hfd1np`;
  merging (conflict-free) beats duplicating proven work.
- **Distill is a *socket*, not "the AI step"** — one interface, backends: by-hand / OSS tool / AI. This
  is what makes the system AI-optional and the manual path first-class.
- **Format adapters first (PPT / Power BI / Excel / Email)** — deterministic, low-token; pull the
  structure already in the file. AI only for the messy residue.
- **Open-core: V2 Newsletters (this, open) / V3 PulseIQ (private, learns over runs).** Product-line
  versions — *not* the same axis as GSD's 12 phases (which are the current build of V2).
- **Learning/onboarding is a first-class surface** (Phase 12); a connection/relationship-map view is
  **parked** (CONN-01) until after core V2.
- **Adopt the crew working method here** — teaching build, this compass + `RETRO.md`, and execution
  discipline layered on GSD (verify each subagent against the live repo; one dependent change at a time).
- **Design the surface first, then hunt the data** — decide what the artifact should look like, then
  go find the inputs.
- **The engine is one promotion chain** — Sources → Report → Article → Newsletter, each human-gated.
  Grounded in five worked contexts (work quality-events, work weeklies-by-swim-lane, interns, PulseIQ,
  Newsletters itself). See `PROJECT.md` → How it's used.
  > 🔤 **Ontology annotation (deep-review R8, 2026-07-02 — history preserved, not rewritten):** the
  > canonical term for this axis-2 device is now **fan-out**, *not* "promotion chain" — one reviewed
  > record **fans out** into audience-tuned surfaces (report / article / newsletter / show / learning).
  > "promotion" was reserved *away* from this axis when A2 added the third state axis (the Problem
  > lifecycle ladder, `transition`), so "promote/promotion" would not collide across axes; SITE-05
  > renamed the site device to fan-out (Phase 9). "Promotion" now belongs only to the human-gated
  > grammar steps `Claim → KPI` / `Report → Article`. See the three-axes seed
  > (`.planning/seeds/promotion-terminology-guard.md`) and the drift ledger
  > (`.planning/reviews/2026-07-02-deep-review/08-ontology-and-drift.md`, D2).
- **The distill socket has three modalities** — author by hand / generic low-token extraction /
  agentic interview — all emitting one reviewed `Distillation` (Phase-1 decision; see
  `.planning/phases/01-distill-socket-contract/01-CONTEXT.md`).
- **The `Locator` union lives in a top-level leaf `src/newsletters/locators.py`, not under `distill/`**
  — so `semantic.py` can import it (`from .locators`, mirroring `from .templates`) without triggering
  the `distill/__init__` barrel → `ports` → `..semantic` import cycle. Caught by cross-AI review, which
  reproduced the cycle the in-flow plan-checker had missed; guarded now by a fresh-interpreter
  import-order acceptance check on the affected tasks.
- **Generic, not template-specific** — extraction handles formats (PowerPoint, email, …) generically;
  no bespoke per-report parsers.
