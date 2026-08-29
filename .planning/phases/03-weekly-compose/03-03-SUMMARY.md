---
phase: 03-weekly-compose
plan: 03
subsystem: core
tags: [content-address, provenance, root-containment, symlink, draft-gate, determinism, faithful-not-suggestive]

# Dependency graph
requires:
  - phase: 03-weekly-compose
    provides: "03-01: AssetRecord / AssetBlock (evidence min_length=1) and the four block kinds in the typed union"
  - phase: 03-weekly-compose
    provides: "03-02: load_weekly_spec, the authored-side models, specspan.SpanMinter, the committed weekly corpus"
provides:
  - "src/newsletters/weeklyspec.py — asset placement (all seven routing rows) and build_weekly_report"
  - "WeeklySpecLoad.assets — the PLACED AssetBlocks, in assets: file order, each standing on its record's own sha256 span"
  - "src/newsletters/compose.py — the public compose.addressed: ONE trust predicate shared by both composers"
  - "A Draft Surface(REPORT) at EPOCH_ZERO in a fixed, asserted block order, byte-identical across two composes"
  - "CONNECTIVE_CONSTANTS — the declared allowlist the editorialization guard consults"
  - "tests/fixtures/weekly/weekly-editorial-bait.yml — the summarizable / out-of-order / mergeable highlight pairs"
affects: [03-04, 04-sample-corpus-recipe]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Containment BEFORE the read: resolve() (which follows symlinks) then relative_to(root), so a traversal never reaches read_bytes() and never becomes a disclosure"
    - "A refusal and an absence are different outcomes with different mechanisms — raise vs missing[] — and a test asserts the refusal's message is NOT one of the disclosures"
    - "The content address is re-checked at PLACEMENT, never trusted from authoring time (the substitution case)"
    - "Hash, never decode: the module's own source is grepped for imaging tokens, and the asset file's mtime/size are asserted unchanged"
    - "Every refusal case carries a well-formed sibling in the SAME document, so no refusal proof can pass on a loader that places nothing"
    - "A substring guard over composed block strings, compared through the faithfulness gate's OWN normal form so a folded block scalar passes and a paraphrase does not"

key-files:
  created:
    - tests/fixtures/weekly/weekly-editorial-bait.yml
  modified:
    - src/newsletters/weeklyspec.py
    - src/newsletters/compose.py
    - tests/test_weeklyspec.py
    - tests/test_abstraction_guard.py

key-decisions:
  - "compose._addressed became the PUBLIC compose.addressed and is imported by the weekly composer rather than copied. Two copies of a trust predicate drift exactly as two normalizers do; test_compose.py polices the rename and passed unmodified."
  - "stands_in_for is CLOSED at validation to the single declared kind 'values' (Rule 2). AssetRecord types it as Literal['values'], so an unknown kind carried to placement would surface as a Pydantic error naming a type instead of naming the typo."
  - "The editorialization guard compares through the gate's own _normalize (case-folded, whitespace-collapsed), not a raw `in`. A YAML block scalar's parsed value is folded, so a raw substring test would flag the author's own multi-line highlight as editorializing while still letting a reformatted paraphrase through."
  - "CONNECTIVE_CONSTANTS holds the lead AND the section labels, not the lead alone: RecognitionsBlock/TeamBlock carry composer-authored headings by MODEL DEFAULT, so a one-string allowlist would have forced heading=None (and the defaults would still have fired invisibly)."
  - "The bait fixture is COMMITTED beside the other two rather than authored into tmp_path: it is a contract the deck composer (03-04) and every later composer must keep passing, and a tmp_path fixture dies with the test that wrote it."
  - "The spec carries the authored photo: key VERBATIM; it is the COMPOSER that renders photo=None for an unplaced key. Mutating the spec would have made the load's own byte-verbatim guarantee false and produced a duplicate 'absent' disclosure."
  - "One ClaimsBlock aggregating every binding's addressed claims (the fixed order shows one, unstarred), with all KPI strips ahead of it in binding order."

patterns-established:
  - "Pattern: a mutation script asserts its target exists and that the text actually changed before writing — a silent no-op mutation reads as 'the guard is vacuous'."
  - "Pattern: mutations are reverted from a scratchpad backup copy, never with git checkout -- (RETRO W23)."
  - "Pattern: the mutation is chosen to be the mistake a future implementer would actually make (delete the containment check; merge the author's lines), not an artificial break."

requirements-completed: [WKLY-03]

# Metrics
duration: 22min
completed: 2026-08-29
---

# Phase 3 Plan 03: Asset placement and the weekly Surface — Summary

**An image now reaches a `Surface` only as a root-contained, provenance-complete file that still hashes to what its record says — every other outcome is the spec's exact disclosure, and a path escaping the project root raises instead — and a loaded weekly composes to a Draft `Surface(REPORT)` at `EPOCH_ZERO` in a fixed, asserted block order carrying no text the author did not write except one declared set of connective constants.**

## Performance

- **Duration:** ~22 min (first task commit 07:31, last 07:38, plus the gates and this summary)
- **Tasks:** 2 (both `tdd="true"`)
- **Files modified:** 5 (1 created, 4 modified)

## Accomplishments

- **All seven routing rows implemented and proved both ways.** 13 `asset_routing` test cases: three provenance minimums (checked in field order, so the field a disclosure names is deterministic), the deep-link rule, a file absent on disk, the **substitution** case (record describes A, B on disk), the happy row, the two `team[].photo` reference rows plus the surviving one, and the two escape rows. **Every refusal case carries a well-formed asset in the same document and asserts that it DID place** — without that arm each refusal assertion would pass on a loader that places nothing at all.
- **A refusal is not an absence, and the test says so in both directions.** A root escape raises a message naming the key, the authored path, the resolved target and the root; the test asserts the message contains neither `"disclosed, never placed"` nor `"does not match its recorded content address"`, and pairs the raise with a constructing arm (the same record loads once the root legitimately contains the file).
- **The symlink half is asserted, because it is the non-obvious one.** `Path.resolve()` follows the link before the containment test, so an in-root symlink pointing outside is refused exactly like a literal `../` — a containment check written against the authored *string* would have missed it.
- **The image is hashed, never decoded.** `hashlib.sha256(read_bytes())` and nothing else; the module's own source is grepped for imaging/sniffing tokens (0 hits) and the asset file's `mtime`/`size` are asserted unchanged after a load that read it.
- **The composed weekly is a Draft that has never touched the gate.** `Surface(REPORT)`, `review.state is DRAFT`, `created == EPOCH_ZERO`, `publish()` without an approval raises and the state does **not** advance, and the module contains zero `publish` / `approve` / `open_pull_request` calls. Two composes over two independent loads are byte-identical, for all three fixtures.
- **Nothing the author did not write reaches a block.** Every display string on a composed surface is either authored (compared through the faithfulness gate's own normal form) or one of eight declared connective constants — enforced for all three fixtures, with the guard's firing observed twice (a planted paraphrase, and a genuinely merging composer).
- **One trust predicate, not two.** `compose._addressed` → public `compose.addressed`, imported by the weekly composer. `tests/test_compose.py` passed **unmodified** (13 passed) across the rename.

## Task Commits

1. **Task 1: Asset routing — every row of the table, proved both ways** — `250ea66` (feat)
2. **Task 2: `build_weekly_report` — fixed block order, Draft on arrival, no editorializing** — `db4e2b3` (feat)

Both pushed to `origin/claude/new-session-gw8tik`.

## The two required mutation observations

### 1. The containment check deleted → the escape rows RED (and worse than expected)

Backup taken first (`cp` to the scratchpad — never `git checkout --`, RETRO W23); the mutation script asserted its target existed and that the text actually changed before writing.

```
        try:
            resolved.relative_to(root_path)
        except ValueError as exc:  # a REFUSAL — never a missing[] disclosure
            raise ValueError(...)                 ->  # MUTATION: containment check deleted
```

**RED**, verbatim:

```
        record["file"] = "../outside.png"
        path = _write_weekly(root, {"shot": record}, files={})

>       with pytest.raises(ValueError) as excinfo:
E       Failed: DID NOT RAISE ValueError

tests/test_weeklyspec.py:910: Failed
FAILED tests/test_weeklyspec.py::test_asset_routing_root_escape_raises_and_never_reaches_missing
FAILED tests/test_weeklyspec.py::test_asset_routing_refuses_a_symlink_resolving_outside_the_root
2 failed, 47 deselected
```

**The observation worth keeping** is what the mutant did *instead* of raising. A probe under the mutation:

```
PLACED: ['shot'] -> ['../outside.png']
missing mentions the escape: False
```

It did not merely fail to refuse — it **placed a file from outside the project root onto the Surface, with full provenance and no disclosure anywhere**. The failure mode of a missing containment check is not an error; it is a silent, fully-vouched-for exfiltration path (T-03-02). That is precisely why the routing table makes this row a raise rather than a `missing[]` entry: a disclosure would have made the same read *look* honest.

**GREEN.** Restored from the backup: `grep -c MUTATION` → `0`, `grep -c relative_to` → `3`, `pytest tests/test_weeklyspec.py tests/test_casespec.py -q` → `57 passed`.

### 2. A composer that merges the author's lines → the editorialization guard RED

The plan asks for a planted paraphrase. The non-vacuity arm plants one *into a composed surface* and asserts the scanner fires (`test_editorialization_guard_detects_a_planted_paraphrase`); to observe the guard catching a *real* mistake, the composer itself was mutated into the summarizer a future implementer would plausibly write:

```python
                items=[  # MUTATION: a composer that merges the author's lines
                    NarrativeItem(text="; ".join(lines), claim=minted.take(key, lines[0]))
                ],
```

**RED**, verbatim (three tests, two of them on fixtures the mutation was not aimed at):

```
E       AssertionError: block string 'The rota was rewritten this week.; The rota rewrite removed
        the last single approval point.; Bay four reopened on Thursday.; Bay two reopened on
        Tuesday.; The clamp check moved to the morning slot.; The clamp check now runs before the
        readiness drill.' is neither authored in the spec file nor a declared connective constant
        — the composer editorialized

FAILED tests/test_weeklyspec.py::test_every_block_string_is_authored_or_a_declared_connective_constant[weekly-full.yml]
FAILED tests/test_weeklyspec.py::test_every_block_string_is_authored_or_a_declared_connective_constant[weekly-editorial-bait.yml]
FAILED tests/test_weeklyspec.py::test_composer_carries_baited_lines_separately_in_order_byte_identical
FAILED tests/test_weeklyspec.py::test_editorialization_guard_detects_a_planted_paraphrase
```

Note the fourth failure: the planted-paraphrase test *also* went red, on its `assert _unauthored(surface, transcript) == []` arm — the guard is discriminating, not merely strict, and the arm proves the untampered surface is clean. **GREEN** after restoring from backup: `72 passed`.

## Where the editorialization fixture lives, and why

`tests/fixtures/weekly/weekly-editorial-bait.yml` is **committed beside the other two**, not authored into `tmp_path`. It is a *contract*, not a scenario: "the composer must not summarize, sort or merge these six lines" is a promise the deck composer (03-04) and every later surface must keep, and a fixture that dies with the test that wrote it cannot be inherited. It joins `FIXTURES`, so the faithfulness, determinism, read-only and double-compose sweeps all run over it too. Its three baited pairs are documented in the file's own header:

| Pair | Bait |
|---|---|
| `highlights[0..1]` | **summarizable** — the second restates the first with its consequence |
| `highlights[2..3]` | **out-of-order** — Thursday is authored before Tuesday; a sorter would swap them |
| `highlights[4..5]` | **mergeable** — two clauses about one change, begging for a comma |

`"2374-W37"` was added to `test_abstraction_guard.py`'s `_WEEKLYSPEC_FIXTURE_VALUES` (LANE-03 discipline: fixture vocabulary must never appear in `src/`). Everything else in the fixture reuses already-denylisted tokens or is ordinary prose.

## The connective-constant allowlist, in full

`weeklyspec.CONNECTIVE_CONSTANTS` — eight strings, each numeral-free (asserted by `test_connective_constants_author_no_facts`) and fact-free:

| Constant | Text |
|---|---|
| `LEAD_HEADING` | `The week, as authored` |
| `LEAD_TEXT` | `This weekly was authored by hand and lifted into the reviewed record without interpretation: every line below is the author's own, traced to a span of the file they wrote, carried in their order and never summarised, merged or reordered. Anything the spec leaves blank — and every image whose provenance record was incomplete — is disclosed in the honesty panel rather than filled in. Org-specific slots stay in config and are never rendered as claims.` |
| `CLAIMS_HEADING` | `Bound sections — every claim traced` |
| `HIGHLIGHTS_HEADING` | `What went well` |
| `LOWLIGHTS_HEADING` | `What did not` |
| `RECOGNITIONS_HEADING` | `Recognitions` |
| `TEAM_HEADING` | `The team` |
| `EYEBROW_FALLBACK` | `Report · weekly` |

## The block order the test pins

`test_weekly_report_block_order_is_fixed` asserts, for `weekly-full.yml`:

```python
["prose", "narrative", "narrative", "recognitions", "team", "asset"]
```

plus `[b.tone for b in narratives] == ["highlight", "lowlight"]` and `[b.asset.key for b in assets] == ["bay-cycle-throughput"]` (`assets:` file order). The full declared order, including the binding-fed blocks that `weekly-full.yml` does not exercise, is in `build_weekly_report`'s docstring and is asserted piecewise by `test_kpi_delta_comes_from_compute_delta_and_is_never_re_derived` (`kinds.index("kpi") < kinds.index("claims")`):

```
ProseBlock → KpiStripBlock* (binding order) → ClaimsBlock → NarrativeBlock(highlight)
→ NarrativeBlock(lowlight) → RecognitionsBlock → TeamBlock → AssetBlock* (assets: file order)
```

`weekly-sparse.yml` composes to `["prose"]` and nothing else, with all five absences in `surface.missing`.

## Discretion the plan asked to be logged verbatim

All four recorded decisions were implemented as written:

- **The asset record lives in the weekly document.** The `assets:` subtree is the record and the spec file is its `Source`; the block's evidence is the record's own `sha256` claim (`_record_evidence`), so one `Source`, one hash, one containment check. Every placed block's trace is asserted to be content-addressed, to point at `load.source.id`, and to address a span containing the recorded hex.
- **`compose._addressed` → public `compose.addressed`**, imported, not copied. Rename verified with a script that excluded the legitimate `Trace.is_addressed` substring; five call sites, `__all__` updated, `test_compose.py` unmodified and green.
- **`title = spec.week`, `eyebrow = spec.module`, never joined.** Fallbacks are the file stem (`Bay Week Nine` from `bay-week-nine.yml`) and the declared `EYEBROW_FALLBACK` — asserted by `test_weekly_report_falls_back_without_inventing_when_identity_is_absent`.
- **Empty sections produce no block.** Asserted on the sparse fixture, together with the loader's disclosure of each absent key — the absence is in the honesty panel, not in an empty `div.block`.

Pitfall 8 was honoured: the blocks list is built in full and passed to the constructor; `surface.blocks` is never mutated.

## Files Created/Modified

- `src/newsletters/weeklyspec.py` (565 → **1058** lines) — the four routing disclosure constants + the escape refusal, `_record_evidence`, `_place_assets`, `_resolve_team_photos`, `WeeklySpecLoad.assets`, the `stands_in_for` refusal in `_validate`, the eight connective constants + `CONNECTIVE_CONSTANTS`, `_MintedClaims`, `_kpi_item` and `build_weekly_report`.
- `src/newsletters/compose.py` — `_addressed` → `addressed` (13 insertions, 6 deletions: the rename, `__all__`, and the docstring recording why it is public).
- `tests/test_weeklyspec.py` (658 → **1304** lines, 34 → **72** tests) — sections 11 (asset routing) and 12 (the composer + the editorialization guard).
- `tests/fixtures/weekly/weekly-editorial-bait.yml` (new) — the three baited pairs.
- `tests/test_abstraction_guard.py` — `"2374-W37"`.

## Test counts, before and after

| Point | Result |
|---|---|
| Baseline (03-02 final) | **661 passed, 64 skipped** |
| After Task 1 | 676 passed, 64 skipped |
| After Task 2 (final) | **699 passed, 64 skipped** |

Net **+38 tests, zero regressions**; skips unchanged at 64 (all `[excel]`/`[pptx]`-extra skips). `tests/test_weeklyspec.py`: 72 passed, **0 skipped**; `-k asset_routing` collects **13**.

## Verification, run once each

| Gate | Result |
|---|---|
| `.venv/bin/python -m pytest -q` | 699 passed, 64 skipped (1 pre-existing `zipfile` warning from `test_pptx_determinism.py`) |
| `.venv/bin/python -m pytest tests/test_weeklyspec.py tests/test_compose.py tests/test_casespec.py -q` | 93 passed, 0 skipped |
| `.venv/bin/lint-imports` | 2 contracts kept, 0 broken |
| `.venv/bin/python -m pytest tests/test_semantic_gate_frozen.py -q` | 11 passed (the eight gate pins still match; zero deleted lines vs the milestone base) |
| `newsletters check --corpus {rev1,work,module}` | all three "All published surfaces clean — no blockers" |
| `grep -v '^#' weeklyspec.py \| grep -c 'PIL\|Pillow\|imghdr'` | `0` |
| `grep -c 'hashlib.sha256' weeklyspec.py` | `2` (≥1) |
| `grep -c 'relative_to' weeklyspec.py` | `3` (≥2 — the spec path and every asset path) |
| `grep -v '^#' weeklyspec.py \| grep -c '\.publish(\|\.approve(\|\.open_pull_request('` | `0` |
| `grep -c 'def addressed' compose.py` / `'def _addressed'` | `1` / `0` |
| the plan's double-compose one-liner | exit 0 (`weekly-full`, 6 blocks, `draft`) |

## Deviations from Plan

### Auto-fixed / adjusted

**1. [Rule 2 - Missing critical] `stands_in_for` is closed at validation**
- **Found during:** Task 1
- **Issue:** `_validate` only required `stands_in_for` to be a string, but `semantic.AssetRecord` types it `Literal["values"] | None`. An authored `stands_in_for: "trends"` would have cleared the schema, cleared the routing (it is not `"values"`, so no deep link is demanded) and then crashed at `AssetRecord(...)` with a Pydantic error naming a *type* — the one place in this module where a typo does not get a teaching error.
- **Fix:** a teaching `ValueError` naming the container, the offending value, the one declared kind and the fact that it is author-declared and never inferred.
- **Files modified:** `src/newsletters/weeklyspec.py`
- **Verification:** `test_unknown_stands_in_for_value_fails_loud`.
- **Committed in:** `250ea66`

**2. [Rule 1 - Bug] The editorialization scan compares through the gate's normal form, not a raw `in`**
- **Found during:** Task 2 (observed as a real RED, not reasoned about)
- **Issue:** The plan's wording is "a substring of `load.source.transcript`". Implemented literally, the guard failed on `weekly-full.yml`'s **block-scalar highlight**: YAML folds a block scalar's line breaks and indentation, so the author's own text is not a byte-substring of the author's own file. A guard that flags the author for the parser's whitespace is a false alarm, and the obvious "fix" (allowlisting the line) would have punched a hole in the guard.
- **Fix:** compare `_normalize(text) in _normalize(transcript)` — the *same* case-folding, whitespace-collapsing normal form `SpanContainmentFaithfulness` already uses to decide entailment. It forgives whitespace and nothing else; the planted paraphrase and the merged line both still fire.
- **Files modified:** `tests/test_weeklyspec.py`
- **Verification:** all three fixtures pass the guard; both non-vacuity arms (planted paraphrase, merging composer) fire.
- **Committed in:** `db4e2b3`

**3. [Rule 2 - Missing critical] The connective allowlist holds the section headings too**
- **Found during:** Task 2
- **Issue:** The plan says to put "it, and only it" (the lead) into the allowlist. But `RecognitionsBlock.heading` and `TeamBlock.heading` carry composer text **by model default** — passing `heading=None` would not remove authored text from the codebase, it would only hide those defaults from the guard, and a headingless weekly is not what `docs/weekly-spec.md`'s class map describes.
- **Fix:** every composer-authored string is a *declared, named, exported* constant collected in `CONNECTIVE_CONSTANTS`; the guard consults that set, and `test_connective_constants_author_no_facts` holds the whole set to the lead's own standard (no numerals). The allowlist is still the plan's mechanism — a composer that starts writing prose must change a declared constant to do it.
- **Files modified:** `src/newsletters/weeklyspec.py`, `tests/test_weeklyspec.py`
- **Verification:** the guard passes on all three fixtures and fires on both plants.
- **Committed in:** `db4e2b3`

**4. [Rule 3 - Blocking / process] One commit per task, not one per TDD gate**
- **Found during:** both tasks (`tdd="true"`)
- **Issue:** the GSD TDD flow asks for separate `test(...)`/`feat(...)` commits; `CLAUDE.md` states "One task, one atomic commit", and plans 03-01/03-02 shipped that shape.
- **Fix:** CLAUDE.md takes precedence. The TDD substance was executed — a RED was observed before each implementation (15 failing tests before Task 1's code; the import error and then the block-scalar failure during Task 2) and both required mutation REDs are recorded above with verbatim output.
- **Files modified:** none (process)
- **Committed in:** n/a

---

**Total deviations:** 4 (2 correctness, 1 bug, 1 process). **Impact:** no scope creep. Two closed holes the plan's literal wording would have left open; one was found by a test failing, not by reading.

## Issues Encountered

- **A mutation script's own assertion fired first, and that was the point.** The Task 2 rename check `assert "_addressed" not in new` failed even though the rename was complete — `Trace.is_addressed` legitimately contains the substring. Caught by the script rather than by a wrong commit; the retry excluded the known-good name by regex.
- **The block-scalar false alarm** (deviation 2) is the one place this plan's first implementation was *wrong*, and it was found by running the guard rather than by reasoning about it.
- **DEF-15 (carried, maintainer-gated).** `black --check` / `isort --check-only` still fail on the pre-existing house width; the new code follows the committed ~100-column style. No CI job runs either tool.

## Threat Flags

None. Every `<threat_model>` disposition was implemented as written:

| Threat | Disposition | Evidence |
|---|---|---|
| T-03-02 (path escape) | mitigated | `resolve()` + `relative_to(root)` before `read_bytes()`; raises, contributes nothing to `missing[]`; mutation-proved (and the mutant was observed placing an out-of-root file silently) |
| T-03-03 (symlink escape) | mitigated | dedicated test: an in-root link to an out-of-root target is refused, and the message names the resolved target |
| T-03-05 (content substitution) | mitigated | sha256 re-checked at placement, case-insensitively; explicit substitution case (record describes A, B on disk) |
| T-03-10 (malicious image) | mitigated | `hashlib.sha256(read_bytes())` only; source grep for imaging tokens → 0; `OSError` guard routes to the same disclosure rather than crashing |
| T-03-19 (traceless AssetBlock) | mitigated | `_record_evidence` mints from the record's own sha256 claim; `min_length=1` left to refuse an empty list rather than being worked around |
| T-03-09 (auto-publish) | mitigated | zero `publish`/`approve`/`open_pull_request` calls (grep test); `publish()` raises and the state stays DRAFT |
| T-03-11 (editorialization) | mitigated | the block-string scan + the bait fixture; firing observed twice |
| T-03-SC (package installs) | accepted, unchanged | this plan installed nothing |

## Known Stubs

None. Two scoped absences, both named in code rather than left as placeholders: `AssetBlock` still renders text-only (03-01's recorded decision — no `<img>`, relative-path resolution for the published tree is unsolved and no criterion asks for it), and `build_weekly_report`'s `bindings` seam is empty for a hand-authored weekly, which is disclosed in `missing[]` (`"no section bindings were supplied…"`) rather than hidden.

## User Setup Required

None — no external service configuration, no new dependency.

## Next Phase Readiness

- **Ready for 03-04 (the deck + the CI job).** `build_weekly_report` returns exactly the `Surface(REPORT, Draft)` the pptx writer takes, with the block order the slot mapping can rely on; `WeeklySpecLoad.assets` gives the deck its media in `assets:` file order (the ordering the media-part numbering depends on).
- **Carried for 03-04 or the PR (unchanged, and now larger):** `tests/test_weeklyspec.py` is in **no CI job** — 72 tests that are green because they are not run (Pitfall 4 / W21). A job must name it. The gate-freeze jobs still need `fetch-depth: 0`.
- **No blockers.**

## Self-Check: PASSED

- Files claimed exist: `src/newsletters/weeklyspec.py`, `src/newsletters/compose.py`, `tests/test_weeklyspec.py`, `tests/test_abstraction_guard.py`, `tests/fixtures/weekly/weekly-editorial-bait.yml` — all FOUND.
- Commits claimed exist: `250ea66`, `db4e2b3` — both in `git log` and pushed to `origin/claude/new-session-gw8tik`.
- `key_links` patterns match: `hashlib.sha256` in `weeklyspec.py` ✓, `from .compose import addressed, compute_delta` ✓, `REPORT` ✓ (`Surface(template=REPORT, review=Review(policy=REPORT.review_policy, …))`).
- `must_haves.artifacts`: `weeklyspec.py` exports `load_weekly_spec` and `build_weekly_report` ✓; `compose.py` contains `def addressed` ✓.

---
*Phase: 03-weekly-compose*
*Completed: 2026-08-29*
