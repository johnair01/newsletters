---
gsd_state_version: 1.0
milestone: v1.3
milestone_name: milestone
status: verifying
stopped_at: "v1.3 BUILD COMPLETE + AUDIT PASSED. PR #25 open to main (https://github.com/johnair01/newsletters/pull/25) — the human gate. Milestone completion/cleanup deliberately NOT run; happens after the EiC review. Session watching PR CI (pptx/weekly jobs first green)."
last_updated: "2026-08-29T10:41:18.203Z"
last_activity: 2026-08-29
progress:
  total_phases: 4
  completed_phases: 4
  total_plans: 13
  completed_plans: 13
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-29)

**Core value:** Make work legible and trustworthy — every published claim traces to evidence; nothing publishes without a human. The deterministic, auditable trust layer is what makes legibility believable; AI is an optional accelerator, never an authority.
**Current focus:** Phase 4 — Sample corpus + recipe (WKLY-05/06)

## Current Position

Phase: — (all 4 phases complete, verified)
Plan: — (13 of 13 complete)
Status: DONE-CONDITION MET — PR #25 open from claude/new-session-gw8tik to main, left for the EiC's review. Audit passed; ADAPT-04 round-trip green; open items listed in the PR body.
Last activity: 2026-08-29 — Phase 4 closed; running milestone audit


## Performance Metrics

**Velocity:**

- v1.3: 9 plans complete (roadmap defined 2026-08-29; 4 phases). Phase 1 executed in 3 waves, ~48min total; Phase 2 executed in 3 waves, ~31min total.
- v1.2: 2 plans across 2 phases (closed 2026-08-29, archived).
- v1.1: 12 plans across 4 phases (closed 2026-07-02, archived). v1.0: Phases 1–14 (archived).

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Specify + de-risk | 3/3 | Plans complete — awaiting phase verification |
| 2. Renderer (WKLY-01) | 3/3 | Plans complete — awaiting phase verification (SC-1..SC-5 proved locally; the `pptx` job's first CI green and the real-PowerPoint open are PR-review items) |
| 3. Weekly compose (WKLY-02/03/04) | 4/4 | Plans complete — awaiting phase verification. 03-01 landed the four block kinds, their render branches and the replacement gate freeze; 03-02 landed the promoted `SpanMinter` and the Weekly Spec load half; 03-03 closed WKLY-03 (asset routing) and the composition half of WKLY-02 (`build_weekly_report`); 03-04 closed WKLY-04 (values via the existing ADAPT-03 adapter) and SC-5 (`weekly_slots` + the end-to-end deck), and added the `weekly` CI job — the first job that runs the compose path at all |
| 4. Sample corpus + recipe (WKLY-05/06) | 3/3 | Plans complete — awaiting phase verification. **WKLY-05 and WKLY-06 are both COMPLETE.** 04-03 landed `docs/weekly.md` (the eight-step operator recipe, every fenced command EXECUTED against the committed corpus in document order — the deck regeneration reproduced the committed bytes and `git status` stayed clean), three doc-guard tests (the recipe's commands validated against the LIVE Typer app with a non-vacuity floor; the recipe's trust anchors; the four-corpora shape of `architecture`/`surfaces`/`CLAUDE`/`content README`), the spec deltas that made those four documents true again plus the deploy-pages header comment 04-02 had recorded, and the phase's ten-row gate sweep re-run independently (862/0 · 2 kept · 4 cleans · 15 mypy · 69 black · no new isort · ledgers clean). Earlier: **WKLY-05 is COMPLETE.** 04-01 landed the committed `content/weekly/` corpus (spec · `.eml` · PNG · template copy · `R-001` ledger · `site/` · `deck/` + digest sidecar), `weeklysite.py`, the promoted `tests/_corpus_scan.py` scanner and the `newsletters weekly` command. 04-02 wired the fourth corpus into all seventeen integration sites — `_CORPUS_LAYOUT`, the `build`/`check` selector, both workflow gates, all four Records strips, the four builder-regenerated chrome pages — and proved the two things the corpus could not prove about itself: `check --corpus weekly` FIRES on a planted blocker, and the committed deck equals a fresh render under `part_digest`. Remaining: 04-03 (`docs/weekly.md`, WKLY-06) |

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
| Phase 3 P03 | 22min | 2 tasks | 5 files |
| Phase 3 P04 | 14min | 3 tasks | 7 files |
| Phase 4 P01 | 22min | 3 tasks | 24 files |
| Phase 4 P02 | 28min | 3 tasks | 15 files |
| Phase 4 P03 | 22min | 3 tasks | 9 files |

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

- [Phase 3-03]: `compose._addressed` is PROMOTED to the public `compose.addressed` and IMPORTED by the weekly composer, never copied — it is the trust predicate deciding whether a claim may reach a reviewed block, and two copies of a trust predicate drift exactly as two normalizers do. `tests/test_compose.py` passed UNMODIFIED across the rename.
- [Phase 3-03]: An asset path escaping the root RAISES and a mutation proved WHY the distinction is not pedantry: with the containment check deleted the loader did not error — it PLACED a file from outside the project root onto the Surface, fully vouched for, with no disclosure anywhere. A `missing[]` route would have made that same read look honest.
- [Phase 3-03]: The editorialization guard compares block strings to the transcript through the faithfulness gate's OWN `_normalize` (case-folded, whitespace-collapsed), not a raw `in`. A YAML block scalar's parsed value is folded, so a raw substring test flags the author's own multi-line highlight while still letting a reformatted paraphrase through. Found by a RED, not by reasoning.
- [Phase 3-03]: `CONNECTIVE_CONSTANTS` holds the lead AND the section labels (eight strings, all numeral-free). `RecognitionsBlock`/`TeamBlock` carry composer text by MODEL DEFAULT, so a lead-only allowlist would have hidden those defaults from the guard rather than removing them.
- [Phase 3-03]: `stands_in_for` is CLOSED to `'values'` at validation. `AssetRecord` types it `Literal["values"]`, so an unknown kind carried to placement would raise a Pydantic error naming a TYPE instead of naming the author's typo — the one place in the module where a typo would not teach.
- [Phase 3-03]: `weekly-editorial-bait.yml` is COMMITTED, not authored into `tmp_path`: "do not summarize, sort or merge these six lines" is a contract 03-04 and every later composer must keep passing, and a tmp_path fixture dies with the test that wrote it.

- [Phase 3-04]: `weekly_slots` ALWAYS emits all four declared `NL_` keys, and an empty section's single slide line **is** that section's own `missing[]` disclosure — membership-checked against `surface.missing` before emission, raising a teaching `ValueError` otherwise. This SUPERSEDES 03-RESEARCH's "omit empty slots" rule for slots the template DECLARES, for two reasons: `bind_slots` refuses an unfilled `NL_` shape (so a weekly with no lowlights would fail to render at all), and inventing filler would be the composer editorialising on the most consequential line in the deck. Mutation-proved: emitting a literal `"—"` turns 6 tests RED, and the refusal fires BEFORE any render.
- [Phase 3-04]: The deck is **TEXT-ONLY** this milestone. `pptx_writer` has no `add_picture` path and `bind_slots` refuses any shape without a text frame; no phase criterion budgets image placement. Phase 1's measured image-determinism property is RECORDED BUT NOT YET CONSUMED. Written into `docs/weekly-spec.md` as a decision with a round-two flag — an absence that is written down is a scope call.
- [Phase 3-04]: `SLOT_PREFIX` is IMPORTED into `weeklyspec.py` from `pptx_writer`, never re-spelled. That module's level is stdlib-only, so the edge costs the bare install nothing, and one spelling of the reserved prefix cannot drift from another (the ONE-normalizer precedent).
- [Phase 3-04]: The excel adapter's claim TEXT is the cell VALUE, not the canonical `Sheet!A1<SEP>value` line the plan's wording claimed — the prefix exists to separate adjacent values so duplicates still get distinct, ordered spans. Verified against the LIVE adapter before the assertion was written; the test asserts both halves (the transcript's canonical lines AND the claim's re-sliceable span).
- [Phase 3-04]: The `.csv` in WKLY-04's wording is a CLARIFICATION, not a scope cut: the live ADAPT-03 adapter is `.xlsx`-only and a CSV path would be exactly the new adapter module the requirement forbids. Recorded in `tests/test_weekly_values.py`'s docstring and in REQUIREMENTS traceability.
- [Phase 3-04]: The `weekly` CI job is SEPARATE and installs `.[test,config,excel,pptx]`; `bare-install` stays the canonical AI-free, EXTRA-FREE source of truth (PKG-03) and is byte-untouched — the `ci.yml` diff against the milestone base is 0 deletions. It sets `fetch-depth: 0` (three guards resolve `git merge-base HEAD origin/main` and FAIL rather than skip without it) and fails on any reported skip.

- [Phase 4-01]: The load-and-compose sequence is ONE private helper (`weeklysite._load_and_compose`), shared by `build_weekly_surfaces` and `build_weekly_deck` rather than written twice as the plan's wording allowed. The failure mode two copies would create is not cosmetic: `weekly_slots(load, surface)` validates its disclosure lines against `surface.missing`, so two drifting loads would eventually check one record's slides against another record's honesty panel.
- [Phase 4-01]: The byline REFUSES rather than defaults. `_resolve_author` takes the explicit `--author`, else the spec's `config: author:`, else raises a teaching `ValueError` naming BOTH. Every other absence in this system is disclosed; a byline is different, because a name on a record is a claim about who stands behind it — a fabricated default would be an abstraction-guard leak AND an unsigned record wearing somebody's name.
- [Phase 4-01]: The confidentiality scanner was PROMOTED to `tests/_corpus_scan.py` (the repo's first shared test helper; `test_modulesite.py` passes at the SAME 9 tests across the move). Its ONE allowance is the RFC 6761 `@example.invalid` domain, and it carries TWO planted arms — a real-looking name, and a NON-reserved address (`ops@starfleet.int`) that must still trip THROUGH the allowance. Without the second arm the allowance is one refactor away from "ignore every address" and nobody would notice.
- [Phase 4-01]: The tier-1 deck gate carries a non-vacuity arm that digests a DIFFERENT committed `.pptx` (`content/weekly/template.pptx`) and asserts it does NOT match the sidecar — otherwise `part_digest(deck) == sidecar` could be comparing a string to itself. The deck lives at `content/weekly/deck/`, OUTSIDE `site/`, so "nothing publishes" holds structurally (`assemble_site` copies `content/*/site` only) rather than by discipline.
- [Phase 4-01]: The weekly's bindings read the COMMITTED `content/module/*.yml` (W0-1), so the "a lane with no KPIs" honesty row comes from content that already exists rather than from content invented to make a demo look honest. The coupling is bounded and loud: a change to the module config moves both corpora's committed HTML and turns both committed==fresh gates red in the same run.
- [Phase 4-02]: The `check --corpus weekly` branch imports the MODULE OBJECT (`from . import weeklysite`) and resolves the builder at CALL time — a TESTABILITY CONTRACT written into the source and stated in the docstring, not a style choice. Binding the function at import time would leave the blocking proof's `monkeypatch.setattr` patching a name nobody reads: the test would go green while the gate stayed unproven. A gate that cannot be shown to fire is not a gate (T-04-09).
- [Phase 4-02]: T-04-10 ("no blocked/Published state leaks into the committed corpus") is asserted IN THE TEST, via a sha256-per-file fingerprint over `content/` compared before and after — not left to a reviewer running `git status`. A path-keyed map fails on a file that APPEARED or VANISHED, not only on an edit; the same assertion on `test_build_weekly_smoke` turns the shared-ledger-path caveat from an assumption about idempotence into a check of it.
- [Phase 4-02]: Tier 2 renders through `build_weekly_deck` — the shipped entry point `newsletters weekly` calls and the one that produced the committed binary — rather than reassembling load → slots → writer in the test. A test that rebuilds the pipeline asserts against its own copy of it and keeps passing after the shipped one changes. A SECOND arm asserts the freshly written `.digest` equals the COMMITTED sidecar: tier 1 ties the deck to its sidecar, so without this a deck and a digest that drifted TOGETHER would still pass as a matched pair.
- [Phase 4-02]: Both workflow module-list additions are placed MID-CONTINUATION (a new backslash-continued line inserted BEFORE the last one) so each edit is a pure insertion. The zero-deleted-lines invariant over `.github/workflows/` is what makes T-04-12 reviewable at a glance; appending to the final line would have cost it for no gain. `deploy-pages.yml`'s whole diff is one line.
- [Phase 4-02]: `deploy-pages.yml`'s "WHAT PUBLISHES" header comment still enumerates three corpora. Left deliberately stale to hold the one-added-line/zero-deletion criterion in the one file where the diff IS the evidence — RECORDED in `04-02-SUMMARY.md` rather than fixed silently, as a one-line follow-up for the PR review.
- [Phase 4-01]: isort/black hygiene was fixed on this plan's OWN files only (no repo-wide reformat; DEF-15 stays maintainer-gated). No import in them is a multi-line parenthesized one — that shape is exactly what isort and black disagree about. A `black` run that reformatted two untouched `cli.py` lines was reverted by hand, so the `cli.py` diff is a pure 69-line insertion with 0 deletions.

- [Phase 4-03]: `docs/weekly.md` documents the CLI **as it ships**, including the two asymmetries an operator would otherwise find the hard way: `build --corpus weekly` renders the corpus at `content/weekly/` and takes no `--spec` (only the deck command takes explicit paths), and there is **no `--workbook` flag** — carrying an export's claims into a weekly is a Python-API seam this milestone (`resolve("excel")` → `SectionBinding` → `build_weekly_report(..., bindings=[...])`). Both stated out loud rather than implied by a flag that does not exist.
- [Phase 4-03]: The doc-contract test drives its expected set from the LIVE Typer app (invoke `<command> --help`, parse the option tokens out of the help body), never from a hand-written list, and carries a `>= 4` command-line floor plus two discriminating arms. A regex that silently matches nothing passes forever — which is the precise failure a doc-contract test exists to prevent.
- [Phase 4-03]: `test_docs_describe_four_corpora` asserts over PROSE — code fences and HTML comments stripped, whitespace collapsed — because `three committed corpora` spans a hard line break in `docs/architecture.md`. A raw `in` check would have passed on the stale document; the first in-memory mutation used to prove the guard discriminates initially did nothing for exactly that reason, and that near-miss is recorded in the summary.
- [Phase 4-03]: `deploy-pages.yml`'s stale "WHAT PUBLISHES" comment (recorded-not-fixed by 04-02) is PAID. It costs that file's one-added-line/zero-deletion diff shape — now 5 insertions / 2 deletions vs the milestone base — and **every changed line is a comment**: gates, conditions, steps and the publish command are byte-unchanged, quoted in full in the summary rather than asserted.

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

- [v1.3 Phase 3 — RETIRED 2026-08-29 by plan 03-04]: both CI gaps are closed at the mechanism. The
  new `weekly` job (`.github/workflows/ci.yml`) installs `.[test,config,excel,pptx]`, sets
  **`fetch-depth: 0`** so the base-ref gates can execute, and names all NINE previously-unrun
  compose-path modules — `test_weeklyspec.py` (now **88 tests**), `test_weekly_blocks.py`,
  `test_weekly_values.py`, `test_semantic_gate_frozen.py`, `test_casespec.py`, `test_compose.py`,
  `test_swimlane.py`, `test_abstraction_guard.py`, `test_excel_adapter.py` — with an explicit
  **`0 skipped`** assertion whose failure message names the W21 lesson. The job's exact command was
  verified locally at **174 passed, 0 skipped**; `bare-install` is byte-untouched (0 deletions in
  the `ci.yml` diff vs the milestone base).

- [v1.3 Phase 3 — OPEN, PR-REVIEW]: the `weekly` job's FIRST CI green has not been observed from
  this environment (no `gh` CLI), exactly as for the `pptx` job. Its command is proved locally; the
  run itself is a PR-review confirmation. Stated, not assumed — an unobserved job is not evidence.

- [v1.3 Phase 3 — OPEN, TOOLING]: `gsd-tools query state.advance-plan` **errored and mutated**
  again on this STATE.md (`{"error": "Cannot parse Current Plan or Total Plans in Phase"}` with 6
  insertions written), and `state.update-progress` **returned `percent: 100` while writing
  `percent: 75`** — a successful call whose reported value contradicts the file on disk. Both were
  reverted from a scratchpad backup and STATE.md was hand-edited. W24's rule held (diff the file
  after ANY state call, success or failure) and is now extended: *the return envelope is not
  evidence of what was written.*

- [v1.3 Phase 4 — OPEN, TOOLING — THIRD occurrence, 2026-08-29 by plan 04-02]:
  `state.advance-plan` **errored and mutated again**, identically: same
  `{"error": "Cannot parse Current Plan or Total Plans in Phase"}`, 6 insertions / 4 deletions
  written — truncating `stopped_at` mid-sentence and injecting two blank lines INTO a markdown
  paragraph (which silently breaks the prose into fragments). W24 caught it; the file was reverted
  from HEAD and hand-edited. **The same blank-line-injection corruption also appeared in
  `requirements.mark-complete`**, which otherwise worked — it flipped the checkbox correctly but
  added a stray blank line in the Deferred list, and it did NOT update the traceability table its
  contract claims to update (done by hand). `roadmap.update-plan-progress` was correct and clean.
  Standing rule, now three-for-three: **hand-edit `.planning/STATE.md`; run the other verbs but
  diff every one of them before committing.** Three occurrences is a tool bug, not bad luck —
  worth a RETRO rule rather than a fourth rediscovery.

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

Last session: 2026-08-29 — **Phase 4 plan 04-03 executed. WKLY-06 is CLOSED and Phase 4 is
complete (3/3 plans).** `docs/weekly.md` now takes an operator who is not the author from a
template deck / workbook export / `.eml` drop / photo folder through authoring, composing,
rendering and reviewing — read-only, local, nothing committed, nothing published — and **all six
of its fenced commands were EXECUTED against the committed corpus in document order**, with the
deck-regenerating one reproducing the committed deck AND sidecar **byte for byte** (`64d296e5…`,
`c93497c4…`; digest `d61ce632…396259`) and `git status --porcelain` empty afterwards. The two
things execution forced into the DOC rather than into a summary: `build --corpus weekly` takes no
`--spec` (it renders the corpus), and there is no `--workbook` flag (the export path is a
Python-API seam) — both now stated beside the "no CSV reader / no Power BI value reader" scope
line. Three guards keep it that way: the commands are validated against the LIVE Typer app with a
`>= 4` floor and two discriminating arms (renaming `--lanes` → `--lane` gives `unknown option
--lane on weekly`), the recipe's trust anchors are a presence guard (read-only · stays on your
machine · no network · commits nothing · the named gate · `word_wrap` · the scope statement), and
`test_docs_describe_four_corpora` holds four documents to the shipped shape. That last one taught
the lesson worth carrying: it reads prose with fences stripped and whitespace collapsed, because
`three committed corpora` spans a line break — the first mutation written to prove the guard
discriminates silently did nothing, and a raw `in` check would have passed on a stale document.
Spec deltas landed in the same change that made them stale (CLAUDE.md's own rule): the
`--corpus` section of `architecture.md` was stale at **two** corpora and is now a four-row table
naming each builder, default out dir and its own ledger; §9 says four and records the deck's
non-publication as STRUCTURAL (`assemble_site` copies `content/*/site` only) with the costed
one-task reversal named but not built; `surfaces.md`, `CLAUDE.md` and `content/README.md`
("Empty until then", untrue since v1.1) fixed; and `deploy-pages.yml`'s header comment — 04-02's
recorded follow-up — paid, comment-only, with the full diff quoted. Gate sweep, re-run
independently, once each: **862 passed / 0 skipped** (baseline 859/0, +3 guards); `lint-imports`
**2 kept / 0 broken**; **four** `check` cleans; committed==fresh 49 passed + deck tier 1 (2) +
tier 2 (6); `ci.yml` **0 deleted lines** and the `bare-install` job block **byte-identical** to
the milestone base; `mypy` **15/5** unchanged; `black` **69/33** unchanged; `isort` 57 files, the
touched test NOT among them; all four ledgers byte-unchanged after rebuilding every corpus; gate
freeze 11 passed; abstraction guard 3 passed; the `site-integrity` job's exact command **114
passed** and the `weekly` job's **189 passed / 0 skipped** with its fail-on-skip grep clean.
Nothing publishes: read end to end, the only file that can publish is main-gated three ways, its
sole outbound call is a warn-only preflight, and this phase pushed nothing to `main`.
Stopped at: Completed 04-03-PLAN.md — Phase 4 complete; next: phase verification, then the
milestone PR
Resume file: `.planning/phases/04-sample-corpus-recipe/04-03-SUMMARY.md`

Previously: 2026-08-29 — **Phase 4 plan 04-02 executed. WKLY-05 is CLOSED.** The fourth corpus
is now registered in every place that knew about three — `publish._CORPUS_LAYOUT`, the
`build`/`check` selector, the `merge-block` and deploy gate lines, and the Records strip on all
four builders — and the two things the corpus could not prove about itself are proven. The
checklist held: sixteen enumerated integration sites, and a **seventeenth found by a red test**
(`test_render.py`'s dead-link guard pins cross-corpus hrefs to an allow-list that was a
three-corpus tuple). That is the shape the plan wanted — loud and immediate, in the same command
as the change, not a late CI or deploy surprise. The decision worth carrying: the `check` branch
imports the MODULE OBJECT and resolves the builder at call time, and that is a *testability
contract*, not a style choice — bind the function at import time and the blocking proof's
`monkeypatch` patches a name nobody reads, so the test goes green while the gate stays unproven.
Proven BOTH ways: clean exits 0 (with a docstring saying plainly that this is DRAFT-VACUOUS by
design and naming the two tests that carry the real trust), and a planted PUBLISHED blocker exits
nonzero with `BLOCK` + `merge blocked` — with `content/` asserted byte-unchanged afterwards by an
in-test sha256 fingerprint, so T-04-10 is executable in CI rather than a promise. Tier 2 renders
through `build_weekly_deck` (the shipped entry point, not a test-local rebuild of the pipeline)
and asserts `part_digest(fresh) == part_digest(committed)` for the deck AND its sidecar — the
second arm because a deck and a digest that drifted *together* would otherwise pass as a matched
pair. Suite: **859 passed / 0 skipped** (baseline 850/0, +9); the `weekly` CI job's EXACT command
run locally at **189 passed / 0 skipped**; `assemble` now writes 61 files / 20 pages / 180
resolving internal links; four `newsletters check` cleans; `lint-imports` 2 kept; `mypy` 15/5
unchanged; `black` 69 reformat / 33 clean (+1, the new golden module); no new `isort` failure; all
four `ids.json` byte-unchanged; **zero deleted lines in either workflow** and `bare-install`
byte-untouched. Exactly four chrome HTML files regenerated by their builders, one line each.
Recorded, not fixed: `deploy-pages.yml`'s header comment still names three corpora — a one-line
PR-review follow-up, kept out of the diff so that file's evidence stays a single added line.
Stopped at: Completed 04-02-PLAN.md; next: 04-03-PLAN.md (`docs/weekly.md`, the operator recipe —
WKLY-06)
Resume file: `.planning/phases/04-sample-corpus-recipe/04-02-SUMMARY.md`

Previously: 2026-08-29 — **Phase 4 plan 04-01 executed. WKLY-05's first half is committed**: a
fourth corpus, `content/weekly/`, whose fabricated weekly composes to a Draft `Surface(REPORT)` at
`EPOCH_ZERO`, takes `R-001` from its OWN ledger, renders to HTML with a populated honesty panel and
to a `.pptx` deck whose integrity is checkable without the optional extra. All **three** planted
absences appeared verbatim as research had captured them and each is asserted BOTH in
`surface.missing` AND `html.escape`d into the rendered page — "in `missing[]`" and "shown to the
reviewer" are two different claims and only the second is the product's promise:
`section 'MOR/IQ tools & defect projects' declares no KPIs — strip omitted` ·
`field 'recognitions[1].source' is absent or empty — disclosed, never fabricated` ·
`asset 'manifest-annex-photo': provenance field 'folder' is absent — the minimum is folder + date

+ event label; disclosed, never placed`. Each is located by the composer's OWN format string

(`compose.NO_KPIS` / `specspan.absent` / `weeklyspec._ASSET_PROVENANCE_ABSENT`), so no disclosure
sentence is typed into a test or a fixture. The deck was produced by running the shipped
`newsletters weekly` command — not an ad-hoc script — so the sample and the recipe (04-03) cannot
drift on day one; 28,885 bytes, sidecar `d61ce632…396259`, one hex line + newline. Two things worth
carrying: the confidentiality scanner was PROMOTED rather than copied (`tests/_corpus_scan.py`, the
first shared test helper here) and its `@example.invalid` allowance needed a SECOND planted arm —
a non-reserved address must still trip THROUGH it, or the allowance quietly becomes "ignore every
address"; and the byline REFUSES rather than defaults, because a name on a record is a claim about
who stands behind it. Suite: **850 passed / 0 skipped** (baseline 837/0, +13, zero regressions);
`lint-imports` 2 kept; `mypy` 15/5 files unchanged with **0** in `weeklysite.py`; `black` 69 would
reformat unchanged (3 new files clean); no new `isort` failure; `content/{module,rev1,work}/ids.json`
byte-unchanged; the eight gate pins green; `newsletters check` clean on all three wired corpora;
`git diff --stat -- src/newsletters/` names exactly two files. Recorded, not patched (W0-4):
`build_weekly_report` carries only the spec `Source` in `traces`, measured to break nothing on a
Draft sample — written into `weeklysite.py`'s docstring.
Stopped at: Completed 04-01-PLAN.md; next: 04-02-PLAN.md (publish layout + `--corpus weekly` +
the four Records strips + the 4 regenerated chrome pages + the `[pptx]` tier-2 golden gate + the
CI/deploy `check` lines)
Resume file: `.planning/phases/04-sample-corpus-recipe/04-01-SUMMARY.md`

Previously: 2026-08-29 — Phase 3 plan 03-04 executed; **Phase 3 is complete (4/4 plans,
WKLY-02/03/04 all closed).** A composed weekly now renders through Phase 2's writer to a deck, and
the decision worth carrying is how an empty section behaves: the template declares an
`NL_LOWLIGHTS` box and `bind_slots` refuses an unfilled `NL_` shape, so omitting the slot would
make a weekly with no lowlights fail to render at all — while padding it with prose would be the
composer editorialising on the most consequential line in the deck. `weekly_slots` therefore emits
all four declared keys and, for an empty section, emits the record's OWN `missing[]` disclosure,
asserting membership in `surface.missing` before it prints. Mutating that line to a literal `"—"`
turned **6 tests RED** and — the part worth keeping — the refusal fired *before* any render, so an
invented line never becomes a deck somebody reviews; the non-vacuity arm went red too, because it
asserts WHICH slot is named. Determinism is asserted twice for two different reasons (raw bytes
in-process, `part_digest` cross-environment), every deck property is read back off the WRITTEN
file, and the Surface is `model_dump()`-identical afterwards. WKLY-04 landed with **no new
adapter**: a synthetic `.xlsx` through `resolve("excel")` reaches the weekly's KPI strip (delta
from two independently traced endpoint cells) and ClaimsBlock, with three *absence* guards
(adapters directory gained no file; ADAPT-05 byte-unchanged; no workbook token in `weeklyspec.py`)
asserted by diff against the milestone base rather than promised. The real find was infrastructural:
**nine test modules ran in no CI job at all** — including the 88-test authoring path — and three
consecutive summaries had recorded "64 skipped" without reading it. The `weekly` job now names all
nine, installs `[excel]`, sets `fetch-depth: 0` and fails on any skip (verified locally: 174 passed,
0 skipped). Suite: **812 passed / 0 skipped** (baseline 699/64 — the first 0-skipped run of this
milestone); `lint-imports` 2 kept; the eight gate pins green; `newsletters check` clean on all
three corpora; determinism `--check` exit 0 with zero committed binary changed. Two items carried
to the PR body: the text-only deck (round two) and the real-PowerPoint open.
Stopped at: Completed 03-04-PLAN.md — Phase 3 complete; next: Phase 4 planning (WKLY-05/06)
Resume file: `.planning/phases/03-weekly-compose/03-04-SUMMARY.md`

Previously: 2026-08-29 — Phase 3 plan 03-03 executed. An image now reaches a `Surface`
ONLY as a root-contained, provenance-complete file that still hashes to what its record says:
`load_weekly_spec` places assets at load time (the hash check needs the filesystem), checking
containment FIRST — `resolve()` follows symlinks, then `relative_to(root)` — so a traversal never
reaches `read_bytes()`, then the three provenance minimums in field order, then the deep link
required iff `stands_in_for: values`, then existence and a placement-time sha256 over the file
BYTES. All seven routing rows carry `docs/weekly-spec.md`'s EXACT disclosure strings and are
proved both ways: 13 parametrized cases, each refusal paired with a well-formed asset in the same
document that still places. `build_weekly_report` then assembles a Draft `Surface(REPORT)` at
`EPOCH_ZERO` in a fixed asserted block order, byte-identical across two composes, with zero
gate-advancing calls in the module. Two mutation observations are recorded verbatim in
`03-03-SUMMARY.md`: deleting the containment check did not merely fail to refuse — it SILENTLY
PLACED an out-of-root file with full provenance and no disclosure; and a composer mutated to merge
the author's highlight lines turned four tests red, including the planted-paraphrase arm's
"the untampered surface is clean" half. The one wrong first implementation this plan shipped was
caught by a test, not by reasoning: the editorialization guard's raw substring check flagged
`weekly-full.yml`'s own BLOCK SCALAR, because YAML folds it — it now compares through the
faithfulness gate's own `_normalize`. Suite: 699 passed / 64 skipped (baseline 661/64, +38 tests,
zero regressions); `lint-imports` 2 kept; the eight gate pins still green; `newsletters check`
clean on all three corpora. WKLY-02 and WKLY-03 are now COMPLETE.
Stopped at: Completed 03-03-PLAN.md; next: 03-04-PLAN.md (the weekly deck + the CI job)
Resume file: `.planning/phases/03-weekly-compose/03-03-SUMMARY.md`

Previously: 2026-08-29 — Phase 3 plan 03-02 executed. `_SpanMinter` and `_absent` were
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
