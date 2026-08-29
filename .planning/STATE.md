---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: milestone
status: executing
stopped_at: "Completed 03-02-PLAN.md; next: 03-03-PLAN.md (asset placement + the weekly Surface)"
last_updated: "2026-08-29T07:45:00Z"
last_activity: 2026-08-29 — Phase 3 plan 03-02 executed (span minter promoted; the Weekly Spec schema + loader)
progress:
  total_phases: 4
  completed_phases: 2
  total_plans: 10
  completed_plans: 8
  percent: 80
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-29)

**Core value:** Make work legible and trustworthy — every published claim traces to evidence; nothing publishes without a human. The deterministic, auditable trust layer is what makes legibility believable; AI is an optional accelerator, never an authority.
**Current focus:** Phase 3 — Weekly compose (WKLY-02/03/04)

## Current Position

Phase: Phase 3: Weekly compose (WKLY-02..04) — executing (2 of 4 plans complete)
Plan: 03-02 complete; next 03-03 (asset placement + `build_weekly_report`)
Status: Ready to execute 03-03
Last activity: 2026-08-29 — Phase 3 plan 03-02 executed (span minter promoted to `specspan.py`; the Weekly Spec eight-key schema + `load_weekly_spec`)

## Performance Metrics

**Velocity:**

- v1.3: 8 plans complete (roadmap defined 2026-08-29; 4 phases). Phase 1 executed in 3 waves, ~48min total; Phase 2 executed in 3 waves, ~31min total.
- v1.2: 2 plans across 2 phases (closed 2026-08-29, archived).
- v1.1: 12 plans across 4 phases (closed 2026-07-02, archived). v1.0: Phases 1–14 (archived).

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Specify + de-risk | 3/3 | Plans complete — awaiting phase verification |
| 2. Renderer (WKLY-01) | 3/3 | Plans complete — awaiting phase verification (SC-1..SC-5 proved locally; the `pptx` job's first CI green and the real-PowerPoint open are PR-review items) |
| 3. Weekly compose (WKLY-02/03/04) | 2/4 | Executing — 03-01 landed the four block kinds, their render branches and the replacement gate freeze; 03-02 landed the promoted `SpanMinter` and the Weekly Spec load half |
| 4. Sample corpus + recipe (WKLY-05/06) | 0/0 (unplanned) | Not started |

**Per-plan execution:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 1 P01 | 12min | 3 tasks | 6 files |
| Phase 1 P02 | 14min | 2 tasks | 3 files |
| Phase 1 P03 | 22min | 3 tasks | 5 files |
| Phase 2 P01 | 12min | 3 tasks | 8 files |
| Phase 2 P02 | 7min | 3 tasks | 2 files |
| Phase 2 P03 | 12min | 3 tasks | 2 files |
| Phase 3 P01 | 11min | 3 tasks | 8 files |
| Phase 3 P02 | 42min | 3 tasks | 8 files |

**Recent Trend:**

- v1.3 opened from a committed seed (`.planning/seeds/v1.3-weekly-one-shot.md`) whose
  current-state claims were verified against the live repo first. Fully autonomous run
  authorized by the EiC (2026-08-29): no between-phase human stop; the human gate is the
  final PR. The ONE discussion round is done — new questions are decided per the recorded
  recommendations and logged.

- Roadmap mirrors the seed's approved 4-phase table; phase numbering resets to 1–4 (prior
  phase dirs archived under `.planning/milestones/`, `.planning/phases/` empty — no collision).

- Plan 01-01 landed the `.pptx` determinism spike as a durable test rather than scratch code:
  the measurement is committed evidence, re-verifiable by `--check`, and the determinism
  assertion carries a negative control so it can actually fail. Zero production surface touched.

- Plan 01-02 turned that measurement into the recorded decision (one outcome, one scope, one
  normalizer contract) and closed the two places where the repo said something different — the
  ADAPT-06 golden-fixture docstring's byte-stability claim was measurably false and is corrected
  and superseded in writing, not silently contradicted.

- Plan 02-02 landed the writer itself. The pattern worth carrying: every deck assertion reopens the
  WRITTEN bytes, and the two hardest properties are asserted in their INVERTED form too (the
  Published deck must have NO watermark; the Surface must be `model_dump()`-identical after a
  render). An unconditional watermark and a writer with a gate write-path would both have passed a
  one-directional suite. Two amendments were raised for the PR body rather than resolved silently:
  the `cp:contentStatus` tri-state (P-04) and the `cp:identifier`→`dc:identifier` wording (W20).

- Plan 02-03 closed the two things the writer alone could not prove, and one of them was a *gate that
  never ran*. W21: no CI job installed `[pptx]`, so every pptx test module skipped itself on every CI
  run — a green that meant "not run". The lesson worth carrying past this phase is that a test suite
  and the job that runs it are two different artifacts, and only the second one is evidence. The
  other half is the negative control: the byte-equality proof is now accompanied by an assertion
  that the UN-normalized pair genuinely differs (in exactly `date_time`), captured from the writer's
  own output rather than from a rebuilt copy of it — so the green is attributable to the normalizer
  and not to two writes landing in one second.

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table. Decisions taken at v1.3 open
(Editor-in-Chief, structured question round, 2026-08-29 — the ONE round; recorded also in
WHERE-WE-ARE.md):

- [Milestone]: Weekly deck reuses `Surface(REPORT)` — the PPTX renderer is an output format, not a new semantic kind.
- [Milestone]: Asset provenance minimum = folder + date + event label; deep link optional EXCEPT a BI screenshot standing in for values (WKLY-04), where it is required. No provenance → `missing[]`, never placed silently.
- [Milestone]: Template contract = named placeholders; missing/unknown names fail loud. The renderer never invents layout.
- [Milestone]: v1.2 formally closed on live evidence (EiC pages review 2026-08-29).
- [Run]: Fully autonomous through all v1.3 phases; the human gate is the final PR. Branch: `claude/new-session-gw8tik` serves the seed's `gsd/v1.3-*` integration-branch role (harness-designated; v1.1 precedent). Never touch `main`.
- [Run]: Milestone-level ecosystem research skipped — the seed encodes it and phase-level research + the Phase 1 determinism spike cover the real unknowns (logged per the no-more-questions contract).
- [Roadmap, 2026-08-29]: Phase 1 carries no WKLY requirement — it de-risks WKLY-01/02 and ships spec + a recorded determinism decision with evidence. WKLY-01→P2, WKLY-02/03/04→P3, WKLY-05/06→P4.
- [Phase 1-01]: Determinism outcome recorded as BYTE-STABLE via a declared post-save OPC-zip normalization (not the content-stable fallback), measured on a real 3s-separated python-pptx 1.0.2 double write — raw_bytes_equal=false with varying_parts=[] and varying_zip_fields=[date_time]; normalized_bytes_equal=true. Evidence committed at .planning/notes/2026-08-29-pptx-determinism-evidence.json and re-verifiable via --check.
- [Phase 1-01]: Byte-identity is scoped in writing to a fixed (python-pptx, zlib) pair; part_digest (sorted name+sha256 of each unzipped part) is the implementation-independent assertion a committed==fresh gate must use — DEFLATE output is zlib-implementation-dependent (zlib vs zlib-ng); a full-file hash across environments would be green locally and red in CI with identical part content.
- [Phase 01-specify-de-risk]: Determinism recorded as BYTE-STABLE via a declared post-save OPC-zip normalization, scoped in writing to a fixed (python-pptx, zlib) pair; the committed==fresh gate asserts the implementation-independent part_digest, never a full-file hash
- [Phase 01-specify-de-risk]: Generated-by marker lives in OPC core properties (cp:category / cp:contentStatus / dcterms EPOCH_ZERO / cp:identifier), not a notes slide — zero new parts, asserted by reopening the WRITTEN file
- [Phase 01-specify-de-risk]: Template contract: fill existing template slides (add_slide regenerates placeholder names); NL_ reserved prefix; the name-to-shape map raises on duplicate names; bind over slide.shapes
- [Phase 01-specify-de-risk]: ONE normalizer contract: _determinism.normalize_opc_zip is canonical and _author_fixtures._normalize_zip delegates to it in Phase 2, not in a spec phase that would rebuild the golden corpus
- [Phase 1]: The Weekly Spec's home is a new docs/weekly-spec.md — a sibling document AND a sibling loader — The casespec mechanism is reused verbatim (safe_load only, normalized file text as evidence, Trace.from_source spans, root containment, config bound but never claimed); the key set stays separate, because widening casespec's exactly-eight-key validator would make each format silently accept the other's fields (Q1)
- [Phase 1]: AssetBlock.asset is REQUIRED — a provenance-less asset placement is unrepresentable, not merely policed — The type carries the invariant instead of a check somebody can forget to call, the same move GlossaryTerm.definition: Claim already makes in this codebase (D-02, threat T-01-18)
- [Phase 2-01]: The OPC normalizer is promoted VERBATIM to `src/newsletters/pptx_writer.py` (no leading underscore — it carries the phase's public entry point) and `tests/fixtures/weekly/_determinism.py` is DELETED. Exactly one `normalize_opc_zip` is reachable from the writer path; git records the move as a rename so a reviewer can diff it and see nothing was tidied. Module level is stdlib-only, so it imports on a bare install; the writer half reaches python-pptx lazily via the existing `adapters._pptx_loader._load_pptx()` boundary.
- [Phase 2-01]: The writer's public API will be `render_surface_pptx_bytes` / `render_surface_pptx`, NOT `render_weekly_deck`, and it takes an explicit `slots` mapping — the Surface→slots derivation is Phase 3's, because only the composer knows which authored block belongs in which Selection-Pane name (P-02/P-03).
- [Phase 2-01]: IN-04 REJECTED and IN-02's second half satisfied the other way CONTEXT permits. `_author_template._FIXED` stays `2026-01-01` as a *falsifiability control* (consolidating onto EPOCH_ZERO would make 02-02's marker read-back pass on a deck the writer never touched); `_author_fixtures._normalize_zip` is not delegated this phase — the weekly copy is SUPERSEDED instead, and the ADAPT-06 delegation is carried to Phase 4 with its cost (it would force all nine golden binaries to be regenerated) (P-05/P-08).
- [Phase 2-01]: The committed `tests/fixtures/weekly/template.pptx` is NOT regenerated by Phase 2 — its `part_digest_a`/`part_digest_b` are the committed determinism evidence and sit in the recorder's CHECKED_FIELDS. The realistic and pathological decks are authored in-test into `tmp_path` (P-06).
- [Phase 2-01]: The `[pptx]` extra carries a FLOOR pin `python-pptx>=1.0.2` — the exercised version, scoping the determinism claim — not a ceiling; `test_pptx_extra_declared` passes unmodified because `_req_name` strips specifiers (W19 closed by execution, not by reading the test).
- [Phase 1]: An asset path that escapes the project root RAISES; it is never routed to missing[] — missing[] is for content that is absent, never for a request the loader will not serve. Collapsing the two would let a future implementer 'disclose' a path traversal (T-01-16)
- [Phase 2-02]: `cp:contentStatus` is implemented VERBATIM per the decision note (`"draft"` if not published else `""`). `ReviewState` has three members, so an IN_REVIEW deck is labelled the same as a DRAFT one — the tri-state amendment is RAISED IN THE PR BODY, never deviated from silently (P-04).
- [Phase 2-02]: `core_properties.identifier` serializes as `dc:identifier`, NOT `cp:identifier` — a wording correction to the decision note's field table (W20), recorded in code, with no code consequence. Fix the note's sentence when it is next touched.
- [Phase 2-02]: The fill primitive INHERITS and never constructs. python-pptx has no bullet API, so paragraph 0 is the formatting carrier and each extra line is a `deepcopy` of it; `text_frame.text =` is banned on an operator's shape (it erases rPr AND pPr) and `TextFrame.fit_text()` is banned outright by name (it reads system-installed font files, making output machine-dependent — T-02-15).
- [Phase 2-02]: The Draft watermark is ADDED, never toggled off an operator-supplied element. W13 disproved the decision note's *mechanical* objection (removal is deterministic and exactly reversible), but the binding one stands: a toggle would make correct gate behaviour depend on operator template content. Recorded in code so it is not reopened.
- [Phase 2-03]: The negative control's RAW pair is INTERCEPTED from the writer — a temporary wrapper around `newsletters.pptx_writer.normalize_opc_zip` records the bytes `prs.save(BytesIO)` produced — rather than rebuilt in the fixture. Rebuilding an "identical" presentation would be a second implementation of the writer, drifting from the first exactly as a second normalizer would. The fixture raises if it captures anything other than two payloads, so a refactor cannot silently leave the control measuring nothing.
- [Phase 2-03]: NO TEST MAY COMPARE A RENDERED DECK TO THE TEMPLATE — not bytes, not `part_digest`, not part order. Opening the committed template and saving it unchanged already yields a different digest (`""` core properties serialize as `<cp:keywords></cp:keywords>` and come back as `<cp:keywords/>`), and part emission order differs between a built package and a reopened one. Both are python-pptx load-path properties, not regressions. **Phase 4's golden deck must come from the writer, never from re-saving the template.**
- [Phase 2-03]: The `[pptx]` extra gets its OWN CI job (`pptx renderer + adapter (WKLY-01)`), on the `merge-block` precedent: it is a non-AI optional extra, and `bare-install` stays the canonical AI-free, extra-free source of truth (PKG-03), byte-untouched. Phase 4 EXTENDS this job with the golden committed==fresh gate — it is the only job where a pptx test executes rather than skips.
- [Phase 2-02]: The `Surface` annotation is imported under `TYPE_CHECKING` only, so `pptx_writer.py`'s module level stays stdlib-only and the bare-install claim in its docstring — which two CI guards are written against — remains literally true rather than approximately true.
- [Phase 3-01]: The milestone base ref (`git merge-base HEAD origin/main`) is resolved ONCE, in `tests/conftest.py::milestone_base_ref`, and consumed by both diff-shape gates. Two copies of a base ref drift exactly as two copies of a normalizer do (the Phase 2-01 "ONE normalizer" precedent). The fixture FAILS rather than skips when the ref cannot be resolved, and names `fetch-depth: 0` as the fix — a gate that is green because it never ran is the W21 failure, already paid for once.
- [Phase 3-01]: `semantic.py`'s blanket byte-freeze is RETIRED and replaced, in the same phase that makes it obsolete, by (a) sha256 pins over `inspect.getsource` of the eight functions that ARE the review gate, with a non-vacuity arm proving the digest discriminates, and (b) a zero-deleted-lines diff against the milestone base. The old guard shelled `git diff HEAD`, which compares the WORKING TREE to the last commit — red on an uncommitted edit, green the instant it was committed, never capable of failing in CI's clean checkout. The four other protected files stay under the blanket freeze, now rebased onto the milestone ref and non-vacuous for the first time.
- [Phase 3-01]: `AssetBlock` renders TEXT ONLY (`figure.diagram` + `.dh` + `<figcaption>`, no `<img>`), pinned by a `"<img" not in html` assertion. Relative-path resolution for the published tree is unsolved and no success criterion asks for it; `DiagramBlock`'s unescaped `{b.svg}` is the renderer's sole raw interpolation and is explicitly NOT a precedent.
- [Phase 3-01]: ZERO bytes of `render._CSS` moved, enforced by a sha256 pin whose message states that regenerating `content/rev1/site` and `content/work` is a separate DECLARED task with its own reviewed diff — never a side effect of adding a block kind.

### Pending Todos

None. (B1–B20 fix-batch backlog remains parked in `reviews/2026-07-02-deep-review/07-tests-as-promises.md`, maintainer-gated.)

### Blockers/Concerns

- [v1.3 Phase 1 — RETIRED 2026-08-29]: The `.pptx` byte-stability risk is closed. Measured on a real 3s-separated double write (`.planning/notes/2026-08-29-pptx-determinism-evidence.json`) and recorded as BYTE-STABLE via a declared post-save OPC-zip normalization, scoped to a fixed (python-pptx, zlib) pair; re-proved every run by `tests/test_pptx_determinism.py` (negative control included).
- [v1.3 Phase 2 — RETIRED 2026-08-29 by plan 02-03]: W21 (no CI job installed `[pptx]`, so every
  pptx test module `s`-skipped itself on every run) is closed at the mechanism. The `pptx` job now
  installs `.[test,pptx]` and runs all five pptx modules; the job's exact command was verified
  locally at **117 passed, 0 skipped**. `bare-install` is byte-untouched.

- [v1.3 Phase 2 — OPEN, PR-REVIEW]: "A normalized deck opens correctly in real PowerPoint" is still
  unproven here (no `.pptx` consumer in this environment; `libreoffice-core` ships without the
  Impress filters). Recorded `checkpoint:human-verify` for the PR review under
  `workflow.human_verify_mode: end-of-phase` — not a phase gap, and not a mid-phase stop.

- [v1.3 Phase 2 — OPEN, PR-REVIEW]: The new `pptx` job's FIRST CI green has not been observed from
  this environment (no `gh` CLI). Its command is proved locally; the run itself is a PR-review
  confirmation. Stated, not assumed — the whole point of W21 is that an unobserved job is not
  evidence.

- [v1.3 Phase 3 — RETIRED 2026-08-29 by plan 03-01]: `render.py`'s bare `return ""` block-dispatch fall-through is gone. All fifteen union members have a branch (proved by a `typing.get_args`-driven coverage test, not a hand-written list) and the fall-through is now a teaching `ValueError` naming the unhandled `block.kind`. It stays unreachable by construction — `Surface.blocks` is a discriminated `list[Block]` — and a comment in `_block_html` records that keeping it unreachable is the point.

- [v1.3 Phase 3 — OPEN, CI]: `tests/test_semantic_gate_frozen.py` Half B and `test_compose.py`'s byte-freeze both need the full history. The CI job that runs them MUST set `fetch-depth: 0` on its checkout, or both FAIL by design (the `milestone_base_ref` fixture names the fix in its own message). Not yet wired — the weekly CI job is plan 03-03/03-04's. Stated, not assumed: the test and the job that runs it are two different artifacts (W21).
- [Carried]: `v1.1`/`v1.2` tags exist locally only — the environment's git proxy drops tag pushes; maintainer creates them via the Releases UI.
- [Carried]: ledgers (`content/*/ids.json`) are append-only — any diff on regenerate is a stop-the-line bug.

## Deferred Items

Carried from v1.1 (full list in `.planning/milestones/v1.1-ROADMAP.md`): DEF-01..12.
New at v1.2 open: DEF-13 (wire `web/` to real data), DEF-14 (adopt the environment deploy
channel iff maintainer aligns repo settings). Plus the B1–B20 fix-batch (maintainer-gated) and,
new at v1.3 open, the ADAPT-05 value-side extension (values come via export this milestone).

New at v1.3 Phase 2 (2026-08-29): **DEF-15 — give `isort` a `profile = "black"` and reformat once.**
The repo declares `isort` in `[dev]` with no profile, so isort and black disagree on every
parenthesized multi-line import; several committed files already fail `isort --check-only` and one
fails `black --check`. Until it is fixed, every plan that adds an import pays a "is this failure
mine?" tax. Maintainer-gated because the fix is a repo-wide reformat.

## Session Continuity

Last session: 2026-08-29 — Phase 3 plan 03-02 executed. `_SpanMinter` and `_absent` were
PROMOTED verbatim out of `casespec.py` into `src/newsletters/specspan.py` as `SpanMinter`,
`absent` and `GATE` (131 deletions vs 7 insertions — a move, not a rewrite), so exactly ONE
honest-span implementation exists and both spec loaders import it; `tests/test_casespec.py`
passes UNMODIFIED. `src/newsletters/weeklyspec.py` then shipped the strict eight-key schema
with teaching errors at BOTH levels (a mistyped field inside a recognition, a team member or
an asset fails as loudly as a mistyped top-level key) and `load_weekly_spec`: file-order
minting (the correctness condition — proved by mutation, see below), `config:` carried and
never claimed, every absence disclosed in schema order including "no lowlights", and
recognition evidence as a span-less POINTER or a named disclosure, never a fabricated span.
Two mutation observations are recorded in `03-02-SUMMARY.md`: reversing the mint order makes
`team[0].name` steal the RECOGNITION's line and turns five authored values into "could not be
located" disclosures (and the ascending-spans sweep stays GREEN through it — the line-number
assertion is the real guard); emptying the new weekly denylist turns the planted-leak arm red.
Suite: 661 passed / 64 skipped (baseline 626/64), `lint-imports` 2 kept, `newsletters check`
clean on all three corpora.

Previously (03-01): the four weekly block kinds joined the
typed `Block` union as a **zero-deletion insertion** (verified: `git diff <merge-base> --
src/newsletters/semantic.py | grep '^-'` counts 0), taking it to fifteen members, with D-02
encoded in the TYPE — `AssetBlock.asset` required and `evidence` `min_length=1`, so a
provenance-less asset placement is unrepresentable rather than policed, asserted in both refusal
directions AND with a constructing non-vacuity arm. Each kind got an HTML branch built only from
classes `_CSS` already defines (zero new CSS; both committed corpora still equal a fresh render),
and `_block_html`'s silent `return ""` became a teaching `ValueError` naming the unhandled kind,
with a `get_args`-driven coverage test so a future member added without a branch fails there. The
`semantic.py` byte-freeze — which shelled `git diff HEAD` and had therefore never been capable of
failing in CI — was replaced by source-hash pins over the eight gate functions plus a
zero-deleted-lines diff against the milestone base, and **proved capable of failing once**: a
blank line planted inside `Surface.publish` turned the pin RED (539d5296… → a8650c12…), and
`git checkout -- src/newsletters/semantic.py` returned it to 11 passed. Full suite 626 passed /
64 skipped (baseline 601/64, +25 tests, zero regressions); `lint-imports` KEPT; `content/` diff
empty. The lesson worth carrying: the mutation was caught by the source-hash half ONLY — the
zero-deletion half stayed green, because inserting a line deletes nothing. Two halves, two
failure modes; neither alone is the protection.
Stopped at: Completed 03-01-PLAN.md; next: 03-02-PLAN.md (the `weeklyspec.py` loader/composer)
Resume file: `.planning/phases/03-weekly-compose/03-01-SUMMARY.md`

Preceding session: 2026-08-29 — Phase 2 plan 02-03 executed, completing the phase's three plans. The
determinism battery now proves SC-2 against the WRITER: two renders of one Surface across a real
3-second gap are byte-identical, the un-normalized pair (captured from inside the writer) differs in
exactly `date_time` with no part content moving, and `part_digest` matches on the raw pair — the
assertion Phase 4's committed==fresh gate inherits. A sample `Surface(REPORT, Draft)` renders end to
end through the COMMITTED synthetic template with all five phase criteria asserted against the
reopened file, including that the unprefixed `Footer` was left untouched. W21 is closed: the new
`pptx` CI job installs `.[test,pptx]` and runs all five pptx modules (verified locally: 117 passed,
0 skipped), while `bare-install` stays byte-untouched. Full suite 595 passed / 64 skipped (baseline
588/64); `lint-imports` KEPT; determinism `--check` exit 0; zero committed binary changed.
Stopped at: Completed 02-03-PLAN.md; next: Phase 2 verification, then Phase 3 planning
Resume file: `.planning/phases/02-renderer/02-03-SUMMARY.md`

Earlier: 2026-08-29 — Phase 2 plan 02-02 executed (the writer itself): the group-recursive
binding map with its five teaching refusals, the reuse-and-clone fill primitive that inherits the
operator's 20pt bold bullets rather than constructing its own, the Draft watermark, the OPC
core-properties marker and the two public entry points — 19 tests, every deck assertion made by
reopening the WRITTEN file, and the two hardest properties asserted in their inverted form too.
Stopped at: Completed 02-02-PLAN.md; next: 02-03-PLAN.md (the proof + the [pptx] CI job)
Resume file: `.planning/phases/02-renderer/02-02-SUMMARY.md`

Earlier: 2026-08-29 — Phase 2 plan 02-01 executed (the renderer's foundation, no rendering
yet). The Phase 1 spike's OPC normalizer moved VERBATIM into `src/newsletters/pptx_writer.py`
(git recorded a rename) and `tests/fixtures/weekly/_determinism.py` was deleted, leaving exactly one
normalizer in the writer path; all three `sys.path.insert` lines and the stale `__pycache__` went
with it (IN-03 closed at the mechanism). Two bare-install guards for the writer were added to
`tests/test_ai_optional.py` — deliberately NOT to `test_pptx_writer.py`, which skips itself without
the extra — and the `[pptx]` extra took a floor pin `python-pptx>=1.0.2`. `tests/test_pptx_writer.py`
landed with five in-test deck builders (group nesting, duplicate names, template-owned watermark,
non-text `NL_` slot, empty-run slot), `RICH_SLOTS`, and a self-test that re-proves W17 in-repo.
Full suite 571 passed / 64 skipped (baseline 567/64); `lint-imports` KEPT; the determinism evidence
`--check` exits 0 and ZERO committed binary changed. All five builders were smoke-verified
independently, not accepted on the tests' green.
Stopped at: Completed 02-01-PLAN.md; next: 02-02-PLAN.md (the writer itself)
Resume file: `.planning/phases/02-renderer/02-01-SUMMARY.md` + `02-02-PLAN.md` +
`.planning/notes/2026-08-29-pptx-determinism-decision.md` (binding input, not open questions)

Earlier: 2026-08-29 — Phase 1 plan 01-03 executed: `docs/weekly-spec.md` written (281
lines — the eight-key annotated schema, the seven loader rules, the four block kinds field by
field, the asset-evidence record and its `missing[]` routing), `docs/architecture.md`'s
pre-existing `diagram`/`glossary` block-list drift fixed in the same edit that added the four new
kinds, the sibling pointer added to `docs/case-spec.md`, and the compass + RETRO brought current.
Phase 1 has no production surface: `git diff --exit-code -- src/newsletters/` exits 0.

Earlier: 2026-08-29 — plan 01-02 turned plan 01-01's committed measurement into
the recorded decision (`.planning/notes/2026-08-29-pptx-determinism-decision.md`, 340 lines) —
BYTE-STABLE via a declared post-save OPC-zip normalization, scoped to a fixed (python-pptx, zlib)
pair; the core-properties marker with its literal read-back assertion; the fill-existing-slides
template contract with the `NL_` prefix and the duplicate-name raise; D-01/D-02/D-03 each with a
testable consequence; Q1–Q5 closed. The two contradicting claims in
`tests/fixtures/pptx/_author_fixtures.py` were corrected and superseded in place (docstring only —
no golden binary regenerated). Full suite 565 passed, 64 skipped.
(That session stopped at 01-02-PLAN.md and resumed into 01-03; both are now closed.)
