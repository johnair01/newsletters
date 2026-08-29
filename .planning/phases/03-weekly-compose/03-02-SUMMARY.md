---
phase: 03-weekly-compose
plan: 02
subsystem: core
tags: [pydantic, yaml, safe-load, span-trace, content-address, strict-schema, promotion, forward-cursor]

# Dependency graph
requires:
  - phase: 01-specify-de-risk
    provides: "docs/weekly-spec.md — the eight-key schema, the seven loader rules and the reference-routing rows"
  - phase: 03-weekly-compose
    provides: "03-01: the four block kinds + AssetRecord in semantic.py; the conftest milestone_base_ref fixture; the gate freeze that can fail"
provides:
  - "src/newsletters/specspan.py — the promoted SpanMinter + absent() + GATE: ONE honest-span implementation, imported by both spec loaders"
  - "src/newsletters/weeklyspec.py — the strict eight-key schema with teaching errors at BOTH levels, the permissive authored-side models, and load_weekly_spec"
  - "Byte-verbatim narrative into a typed spec with gate-entailed claims at real spans of the author's own file"
  - "config: carried and never claimed; every absence disclosed in missing[] in schema order, including 'no lowlights'"
  - "Recognition evidence as a POINTER (span-less Trace) or a named disclosure — never a fabricated span"
  - "tests/fixtures/weekly/{weekly-full.yml,weekly-sparse.yml,assets/bay-cycle-throughput.png} — the committed corpus every later Phase-3 proof is written against"
  - "tests/test_weeklyspec.py — the casespec-ported proof suite plus the span-swap regression"
affects: [03-03, 03-04, 04-sample-corpus-recipe]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Promotion over fork: a mechanism two modules need moves to its own module VERBATIM (the pptx_writer precedent), never copied and never privately cross-imported"
    - "File-order iteration as a stated CORRECTNESS CONDITION, with a line-number-asserting regression whose RED was observed once"
    - "Reference resolution as a SECOND PASS over already-minted data, so the forward cursor is never re-entered out of order — by construction, not convention"
    - "Permissive authored-side models vs the strict placement shape: an incomplete entry must be representable long enough to be DISCLOSED"
    - "A denylist addition is proved non-vacuous by a planted-leak arm through the guard's own matcher"

key-files:
  created:
    - src/newsletters/specspan.py
    - src/newsletters/weeklyspec.py
    - tests/test_weeklyspec.py
    - tests/fixtures/weekly/weekly-full.yml
    - tests/fixtures/weekly/weekly-sparse.yml
    - tests/fixtures/weekly/assets/bay-cycle-throughput.png
  modified:
    - src/newsletters/casespec.py
    - tests/test_abstraction_guard.py

key-decisions:
  - "The span minter is PROMOTED to specspan.py, not forked and not privately cross-imported. `_GATE` is promoted with it as the public `GATE` for the same reason the other two names lost their underscore: a name two modules import is not private. casespec's diff is 131 deletions vs 7 insertions — a move, not a rewrite."
  - "weeklyspec.py sits beside casespec.py; there is no assets.py. Every block sub-model already lives in semantic.py, and a separate module would have to stay semantic-free to avoid an import cycle for no gain."
  - "Nested unknown keys fail loud too. Rule 1 names the top level; a mistyped `resaon:` inside a recognition drops authored content just as silently, so it earns the same refusal naming the container, the key and the exact allowed field list."
  - "A recognition's `evidence` is a POINTER, never an invented span. A resolved `source:` gets exactly one SPAN-LESS Trace (the loader has not read that source's text); absent or unresolvable gets `evidence=[]` plus a named disclosure. `person` and `reason` are separately evidenced as gate-entailed claims of the spec file."
  - "WeeklySpec.assets is a LIST, not a mapping: file order is part of the determinism claim, and an explicit sequence states that rather than leaning on dict insertion order surviving every round-trip. The `assets:` key is carried on AuthoredAsset.key."
  - "The `assets:` mapping KEY is not minted as a claim — it is a spec-local handle, not authored narrative. Every record SCALAR is routed, including the sha256 hex, which is a literal substring of the file and traces verbatim."
  - "_disclose_gaps deliberately does NOT disclose asset provenance fields; that wording belongs to plan 03-03's placement routing, and duplicating it would show the reviewer the same gap twice in two different voices. It also does not disclose `recognitions[].source`, which the reference pass owns so the absent and unresolvable cases sit adjacent."

patterns-established:
  - "Pattern: a mutation observation is captured with a BACKUP COPY first, never `git checkout --` on a file carrying uncommitted work (this run lost the guard edits once and had to redo them)."
  - "Pattern: two guards that look redundant are kept when a mutation proves they catch different things — the ascending-spans sweep stayed GREEN under the reversed-order mutation that the line-number assertion caught."
  - "Pattern: the fixture's own SHAPE is asserted (block scalar present, person duplicated across sections, three asset conditions), so a later fixture edit cannot silently make the proofs vacuous."

requirements-completed: []

# Metrics
duration: 42min
completed: 2026-08-29
---

# Phase 3 Plan 02: The Weekly Spec load half — Summary

**One `SpanMinter` now exists in the package (promoted out of `casespec.py` as a pure 131-deletions-for-7-insertions move) and `newsletters.weeklyspec` lifts a hand-authored weekly into a content-addressed `Source` with 35 gate-entailed claims at real spans of the author's own file, an honest `missing[]`, and a `config:` subtree that is carried and never claimed — byte-identically on every load.**

## Performance

- **Duration:** ~42 min
- **Started:** 2026-08-29T07:00Z
- **Completed:** 2026-08-29T07:42Z
- **Tasks:** 3
- **Files modified:** 8 (6 created, 2 modified)

## Accomplishments

- **Exactly one honest-span implementation.** `SpanMinter` and `absent` moved verbatim into `src/newsletters/specspan.py`; `casespec.py` and `weeklyspec.py` both import them, and `newsletters.casespec.SpanMinter is newsletters.specspan.SpanMinter` is asserted at the interpreter. `tests/test_casespec.py` passes **unmodified** (`git diff --exit-code` exits 0) — the promotion changed no Case Spec behavior by one byte.
- **A Weekly Spec's typo fails loud at BOTH levels.** An unknown top-level key, an unknown key inside a recognition / a team member / an asset, and a type-coerced scalar each raise a teaching `ValueError` naming the offender, its container, the exact allowed field list and the fix. `casespec._validate` was **not** widened (`git diff --exit-code` clean across Task 2 and 3).
- **Every authored line reaches the record byte-verbatim, traced to its own line.** 35 claims off `weekly-full.yml`, spans strictly ascending, each entailed by the LIVE `SpanContainmentFaithfulness` gate on its strict branch. The person named in **both** `recognitions:` and `team:` traces to L18 and L24 respectively — its own occurrence, not its twin's.
- **Honest absences, and a config that is bound but never claimed.** `weekly-sparse.yml` discloses all six unwritten keys in schema order, `'lowlights'` named explicitly; `weekly-full.yml` discloses its per-item gaps (`team[1].photo`) while still carrying the member and their lines. No `config:` leaf appears in any claim or any disclosure, and `load.spec.config` equals the parsed subtree exactly.
- **Two loads are byte-identical and the loader writes nothing** — asserted on the filesystem (`st_mtime_ns` + `st_size` unchanged after a load), not merely intended.

## Task Commits

1. **Task 1: Promote the span minter into `specspan.py` (a pure move)** — `8ced72f` (refactor)
2. **Task 2: The eight-key schema, the typed spec, and the fixtures the whole phase is proved against** — `9a56938` (feat)
3. **Task 3: `load_weekly_spec` — file-order minting, config short-circuit, honest absences** — `9c95b3d` (feat)

All three pushed to `origin/claude/new-session-gw8tik`.

## The mutation observations (required by the plan — an unproven guard is a vibe)

### 1. The span-swap regression, observed RED under deliberately reversed mint order

The plan requires the span-swap test to be proved capable of failing. The mutation reversed the two mint calls by walking `team` before `recognitions`:

```python
_mutated = list(parsed.items())  # MUTATION: reverse the two mint calls
_mutated.sort(key=lambda kv: {'team': 4, 'recognitions': 5}.get(kv[0], _KNOWN_KEYS.index(kv[0])))
for key, value in _mutated:
```

**Observed effect on the duplicated person `"Miles O'Brien"`** (probe under the mutation):

```
  team.name              L18  (957,970) "Miles O'Brien"      <- the RECOGNITION's line
  team.name              L29  (1343,1356) 'Julian Bashir'
  MISSING notes mentioning 'could not be located':
   - field 'recognitions.person' could not be located as a span of the authored file — ...
   - field 'recognitions.reason' could not be located as a span of the authored file — ...
   - field 'recognitions.source' could not be located as a span of the authored file — ...
   - field 'recognitions.person' could not be located as a span of the authored file — ...
   - field 'recognitions.reason' could not be located as a span of the authored file — ...
```

**RED**, verbatim:

```
        recognition_claims = [
            c
            for c in load.distillation.claims
            if c.topics == ["recognitions.person"] and c.text == person
        ]
        team_claims = [ ... ]
>       assert len(recognition_claims) == 1 and len(team_claims) == 1
E       assert (0 == 1)
E        +  where 0 = len([])

tests/test_weeklyspec.py:403: AssertionError
FAILED tests/test_weeklyspec.py::test_duplicated_person_traces_to_its_own_line_not_its_twins
FAILED tests/test_weeklyspec.py::test_block_scalar_highlight_is_traced_to_its_own_item_region
FAILED tests/test_weeklyspec.py::test_recognition_without_source_is_carried_and_disclosed
3 failed, 31 passed in 0.22s
```

**GREEN.** Restored from a backup copy, then `pytest tests/test_weeklyspec.py tests/test_casespec.py -q` → `42 passed in 0.21s`, and `grep -c MUTATION src/newsletters/weeklyspec.py` → `0`. The revert was clean.

**The observation worth keeping** (and the reason two apparently redundant guards are both retained): `test_claim_spans_ascend_strictly_in_document_order` stayed **GREEN** under this mutation. The stolen span still ascends — the recognition fields simply became disclosures instead of claims, and a whole-document ascending sweep cannot tell that apart from an honest walk. **The ascending-spans sweep is not the protection; the line-number assertion is.** The reversal was also *worse* than 03-RESEARCH's prediction: it did not merely swap two spans, it silently converted five authored recognition values into "could not be located" disclosures — which the honesty panel would have shown a reviewer as gaps in a weekly where nothing was actually missing.

### 2. The abstraction-guard denylist addition, observed RED when emptied

Adding tokens to a denylist proves nothing on its own. Emptying `_WEEKLYSPEC_FIXTURE_VALUES` (leaving the union intact) turned the new planted-leak arm red:

```
        hits = _scan_text(planted)
>       assert "bay-cycle-throughput" in hits, hits
E       AssertionError: set()
E       assert 'bay-cycle-throughput' in set()

FAILED tests/test_abstraction_guard.py::test_guard_detects_planted_weekly_fixture_leak
1 failed, 2 passed in 0.09s
```

Restored from backup; `3 passed`, and `git diff --stat` showed exactly the intended `72 insertions(+), 2 deletions(-)`.

## The promotion's diff shape (a move, not a rewrite)

```
 src/newsletters/casespec.py | 138 +++-----------------------------------------
 1 file changed, 7 insertions(+), 131 deletions(-)
```

Every one of the seven insertions:

```
+from .specspan import GATE, SpanMinter, absent
+            gaps.append(absent(key))
+        gaps.append(absent(_DESIGN_KEY))
+        gaps.append(absent(_REASONING_KEY))
+        gaps.append(absent(_PORTABLE_KEY))
+    minter = SpanMinter(source)
+        if not GATE.entails(claim):
```

One new import line plus six call-site renames. The plan's action text said "the two call sites updated"; there are in fact **six**, because `_absent` had four callers inside `_disclose_gaps` in addition to `_SpanMinter(source)` and `_GATE.entails`. Nothing else in `casespec.py` changed; the 131 deletions are the moved block (120 lines), the `_GATE` construction (3), and the two imports that became unused with it (`SpanContainmentFaithfulness`, `Trace`).

## The exact fixture identifiers added to the abstraction-guard denylist

`_WEEKLYSPEC_FIXTURE_VALUES`, unioned into `_DENY_LITERALS`:

| Class | Tokens |
|---|---|
| period labels | `2374-W35`, `2374-W36` |
| module + crew names | `Shuttlebay Operations`, `Miles O'Brien`, `Kira Nerys`, `Julian Bashir` |
| `assets:` keys | `bay-cycle-throughput`, `crew-rota-board`, `crew-manifest-scan` |
| recognition source id | `mail:23740824-rota` |
| provenance labels | `Weekly review pack`, `Friday bay review` |
| `config:` values | `Bay Rotation Registry Delta`, `Docking Clamp Cycle Count` |

None collides with an existing denylist token (`Shuttlebay Ops Console Seven` and `Bay Cycle Chronometer Reading` are separate word-bounded literals). `grep -v '^#' src/newsletters/weeklyspec.py | grep -c "Shuttlebay Operations\|Miles O'Brien\|bay-cycle-throughput"` prints `0`.

## The recognition-evidence decision, as implemented

`_resolve_recognition_evidence` runs as a **second pass over already-minted data**, so the forward cursor is never re-entered out of order — by construction, not by convention. Three outcomes:

| Authored `source:` | `evidence` | Disclosure |
|---|---|---|
| absent | `[]` | `field 'recognitions[N].source' is absent or empty — disclosed, never fabricated` |
| resolves to a known `Source` (the spec's own id, or one passed in `known_sources`) | exactly **one** `Trace(source_id=...)` with **no span**, `is_addressed == False` | none |
| resolves to nothing | `[]` | `recognition for {person!r}: source {source!r} does not resolve to a known Source — carried, with the unresolvable id disclosed` |

The span-less trace is the whole point: the loader has not read that source's text, so minting a span for it would be fabrication. The author's own word is separately evidenced — `person` and `reason` are gate-entailed claims at real spans of the spec file — which is why the recognition survives in every row rather than being dropped.

## Files Created/Modified

- `src/newsletters/specspan.py` (new, 171 lines) — the promoted `SpanMinter` + `absent` + `GATE`, bodies verbatim. Module docstring states the ONE-implementation contract, cites `pptx_writer.py`'s "ONE normalizer contract" as the precedent and 03-RESEARCH Pitfall 1 as why the forward-cursor / file-order rule is a correctness condition.
- `src/newsletters/weeklyspec.py` (new, 565 lines) — the eight-key `_KNOWN_KEYS`, the recursive `_validate`, `AuthoredRecognition` / `AuthoredMember` / `AuthoredAsset` / `WeeklySpec` / `WeeklySpecLoad`, `_resolve_recognition_evidence`, `_disclose_gaps`, `load_weekly_spec`.
- `src/newsletters/casespec.py` — the pure-move diff above; behavior byte-unchanged.
- `tests/test_weeklyspec.py` (new, 658 lines) — the ported eight-test shape plus the span-swap regression, the ascending-spans sweep, the fixture-shape non-vacuity test and the filesystem read-only assertion.
- `tests/fixtures/weekly/weekly-full.yml` (new) — all eight keys, an ordinary and a block-scalar highlight, one lowlight, two recognitions (exactly one sourced), two team members with a person duplicated from `recognitions:`, three assets (complete / deep-link-required-without-link / provenance-incomplete), a `config:` subtree.
- `tests/fixtures/weekly/weekly-sparse.yml` (new) — `week` + `module` only.
- `tests/fixtures/weekly/assets/bay-cycle-throughput.png` (new, 75 bytes) — the constant 1×1 PNG byte literal (no Pillow); its real sha256 `84549424…527080` is pinned verbatim in `weekly-full.yml`.
- `tests/test_abstraction_guard.py` — `_WEEKLYSPEC_FIXTURE_VALUES` + the union + the planted-leak arm.

## Test counts, before and after

| Point | Result |
|---|---|
| Baseline (03-01 final) | **626 passed, 64 skipped** |
| After Task 1 | 626 passed, 64 skipped (`test_casespec.py` + `test_compose.py`: 21 passed) |
| After Task 2 | `test_weeklyspec.py` + `test_abstraction_guard.py`: **20 passed, 0 skipped** |
| After Task 3 (final) | **661 passed, 64 skipped** |

Net: **+35 tests, zero regressions.** Skips stayed at 64 (all `[excel]`/`[pptx]`-extra skips; the `[excel]` install is plan 03-04's). `.venv/bin/lint-imports`: **2 contracts kept, 0 broken.** `newsletters check --corpus {rev1,work,module}`: all three "All published surfaces clean — no blockers."

## Where docs and implementation had to differ

**Nowhere.** Every key name, every teaching-error reason and every disclosure string came from `docs/weekly-spec.md`. Two places where the doc is silent and the implementation had to choose are recorded as decisions above (the `assets:` mapping key is a handle rather than a minted claim; asset provenance disclosures belong to 03-03's placement routing rather than to `_disclose_gaps`). No spec edit was needed in this plan.

## Decisions Made

All seven are in the frontmatter `key-decisions`. The three most load-bearing:

- **`GATE` is promoted alongside the minter.** The plan said "if `casespec` still needs its own reference, import the promoted one rather than constructing a second gate instance". A private cross-module `from .specspan import _GATE` has no precedent in `src/` (03-RESEARCH verified zero such imports), so the gate lost its underscore for the same reason `SpanMinter` and `absent` did: a name two modules import is not private. Cost: one extra changed line in `casespec.py` (`_GATE.entails` → `GATE.entails`), visible in the seven-insertion diff above.
- **The authored-side models are permissive and the placement shape is strict.** `AuthoredAsset` defaults every field empty; `semantic.AssetRecord` requires its provenance minimums. An incomplete asset must be *representable* long enough to be disclosed — a spec that refused to parse one would fail the whole weekly instead of naming the single absent field — while a *placed* one must be unrepresentable without its provenance. Both directions are asserted in one test so neither can be quietly relaxed.
- **`WeeklySpec.assets` is a list.** Order is part of the determinism claim (media parts are numbered in add order), and an explicit sequence states that rather than leaning on dict insertion order surviving every JSON round-trip.

## Deviations from Plan

### Auto-fixed / adjusted

**1. [Rule 3 - Blocking] `_GATE` had to be promoted, not privately cross-imported**
- **Found during:** Task 1
- **Issue:** The plan left the gate's disposition open ("import the promoted one"). The literal reading — `from .specspan import _GATE` — is a private cross-module import, a pattern 03-RESEARCH verified does not exist anywhere in `src/` and which the plan's own promotion reasoning ("a name two modules import is not private") argues against.
- **Fix:** `_GATE` moved as the public `GATE`, listed in `specspan.__all__`, with the reasoning in the module docstring. `casespec`'s single usage renamed.
- **Files modified:** `src/newsletters/specspan.py`, `src/newsletters/casespec.py`
- **Verification:** `tests/test_casespec.py` passes unmodified; `lint-imports` 2 kept; the casespec diff is still 131 deletions vs 7 insertions.
- **Committed in:** `8ced72f`

**2. [Rule 2 - Missing critical] `_disclose_gaps` deliberately withholds two disclosure classes**
- **Found during:** Task 3
- **Issue:** The plan asked `_disclose_gaps` to cover "all eight keys in schema order plus per-item absences". Read literally that includes `recognitions[].source` (which the reference pass already discloses, in two different wordings depending on absent-vs-unresolvable) and every `assets[]` provenance field (whose exact wording `docs/weekly-spec.md` assigns to the placement routing, i.e. plan 03-03). Emitting both would show a reviewer the same gap twice in two different voices — the opposite of an honesty panel's job.
- **Fix:** `_disclose_gaps` covers the eight keys plus `recognitions[].person/reason` and every `team[]` field; `source` is owned by `_resolve_recognition_evidence` and the asset provenance fields are left to 03-03. The exclusion and its reasoning are in `_disclose_gaps`'s own docstring, so 03-03 cannot re-add a duplicate without reading why.
- **Files modified:** `src/newsletters/weeklyspec.py`
- **Verification:** `test_sparse_spec_discloses_every_absent_key_in_schema_order` asserts the disclosed order equals the absent-key order; `test_full_spec_discloses_its_per_item_absences` asserts the `team[1].photo` gap; no duplicate note appears in either fixture's `missing[]`.
- **Committed in:** `9c95b3d`

**3. [Rule 3 - Blocking / process] One commit per task, not one per TDD gate**
- **Found during:** Tasks 2 and 3 (both `tdd="true"`)
- **Issue:** The GSD TDD flow asks for separate `test(...)` RED and `feat(...)` GREEN commits. `CLAUDE.md` states "One task, one atomic commit" as an execution-discipline rule, and plan 03-01's shipped history follows it (one commit per task, tests included).
- **Fix:** CLAUDE.md takes precedence: one commit per task. The TDD substance — observing a RED that the implementation then turns GREEN — was executed and is recorded above with verbatim output for both mutations, which is the teaching purpose the split commits exist to serve.
- **Files modified:** none (process)
- **Verification:** `git log --oneline` shows three task commits matching plan 03-01's shape.
- **Committed in:** n/a

---

**Total deviations:** 3 (2 blocking, 1 correctness). **Impact:** no scope creep. Each removed a duplication, prevented a private cross-module import with no precedent, or kept the honesty panel from repeating itself.

## Issues Encountered

- **A `git checkout --` destroyed uncommitted work, once.** While setting up the first denylist mutation I reverted `tests/test_abstraction_guard.py` with `git checkout --`, which discarded my *uncommitted* additions along with the mutation. The edits were re-applied and every subsequent mutation used a scratchpad backup copy (`cp file $SP/file.bak` → mutate → `cp $SP/file.bak file`). Recorded here rather than smoothed over; it is worth a RETRO rule (see below).
- **The first denylist mutation was a silent no-op.** The `str.replace` target omitted a trailing comma, so nothing changed and the suite passed — which would have read as "the guard is vacuous" if taken at face value. The retry asserted `new != t` before writing. Every mutation script in this plan now fails loudly rather than reporting a green that means nothing.
- **DEF-15 (carried, maintainer-gated).** `black --check` / `isort --check-only` still fail on the pre-existing house width; the new modules follow the committed ~100-column style. No CI job runs either tool. Unchanged by this plan.

## Threat Flags

None. Every `<threat_model>` disposition was implemented as written:

| Threat | Disposition | Evidence |
|---|---|---|
| T-03-04 (YAML parse EoP) | mitigated | parses only via `_yaml_loader.load_config` (`safe_load`); `grep -c '^import yaml\|^from yaml'` → 0 in both new modules; `test_ai_optional.py` green |
| T-03-01 (path info disclosure) | mitigated | `resolve()` then `relative_to(root_path)` **before** `read_text`; asserted with a raising arm AND a constructing arm, and asserted absent from `missing[]` |
| T-03-06 (source repudiation) | mitigated | three-outcome table above; a resolved id gets a span-less `Trace` only, asserted `not trace.is_addressed` |
| T-03-11 (narrative tampering) | mitigated | values carried byte-verbatim (asserted field by field against the parsed fixture); every emitted claim swept against the LIVE gate, raising rather than emitting |
| T-03-12 (duplicate-value span swap) | mitigated | strict file-order minting + the line-number regression, RED observed once |
| T-03-13 (fixture vocabulary in `src/`) | mitigated | `_WEEKLYSPEC_FIXTURE_VALUES` in `_DENY_LITERALS` + a planted-leak arm, proved non-vacuous by mutation |
| T-03-18 (two drifting minters) | mitigated | one `SpanMinter` in the package; `grep -c 'class _SpanMinter' casespec.py` → 0; identity asserted at the interpreter |
| T-03-SC (package installs) | accepted, unchanged | this plan installed nothing |

## Known Stubs

None. Everything this plan renders comes from an authored file. The two deliberately *unimplemented* surfaces are scoped, not stubbed, and are named in code: `load_weekly_spec` does no asset placement (docstring: "THIS FUNCTION DOES NO PLACEMENT") and `_disclose_gaps` does not emit asset provenance disclosures (docstring names plan 03-03 as the owner). Neither is a placeholder that would reach a reviewer as content.

## User Setup Required

None — no external service configuration, no new dependency.

## Next Phase Readiness

- **Ready for 03-03 (asset placement + the Surface).** The typed authored-side records exist and round-trip; `AuthoredAsset` carries every field placement needs (including the `sha256` hex as a traced claim); the committed corpus already exercises all three placement conditions (complete / deep-link-required-without-link / provenance-incomplete) and a `photo:` key pointing at an asset that *will* be placed. The load/place seam is documented on both sides.
- **Carried for 03-03/03-04 or the PR (unchanged from 03-01):** `tests/test_weeklyspec.py` is in **no CI job** (03-RESEARCH Pitfall 4 — `ci.yml`'s three pytest invocations cover 12 modules, and this is not one of them). A job must name it or these 35 tests are green-because-not-run. The gate-freeze jobs still need `fetch-depth: 0`.
- **No blockers.**

## Self-Check: PASSED

All eight claimed files exist on disk. All three claimed commits (`8ced72f`, `9a56938`, `9c95b3d`) are in the log and pushed to `origin/claude/new-session-gw8tik`. Artifact minimum line counts met: `src/newsletters/weeklyspec.py` 565 (min 250), `tests/test_weeklyspec.py` 658 (min 280). All three `key_links` patterns match: `from .specspan import` in both `weeklyspec.py` and `casespec.py`, `from ._yaml_loader import load_config` in `weeklyspec.py`.

---
*Phase: 03-weekly-compose*
*Completed: 2026-08-29*
