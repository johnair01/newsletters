---
phase: 03-weekly-compose
reviewed: 2026-08-29T08:10:43Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - src/newsletters/weeklyspec.py
  - src/newsletters/specspan.py
  - src/newsletters/semantic.py
  - src/newsletters/render.py
  - src/newsletters/compose.py
  - src/newsletters/casespec.py
  - tests/test_weeklyspec.py
  - tests/test_weekly_blocks.py
  - tests/test_weekly_values.py
  - tests/test_semantic_gate_frozen.py
  - .github/workflows/ci.yml
findings:
  critical: 1
  warning: 6
  info: 7
  total: 14
status: issues_found
---

# Phase 3: Code Review Report

**Reviewed:** 2026-08-29T08:10:43Z
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

The weekly compose path is well-built where the phase said it would be: root containment
runs before every filesystem read (spec and assets, symlinks resolved first), the image is
hashed and never decoded, no gate-advancing call exists in `weeklyspec.py`, composition is
`EPOCH_ZERO`-deterministic in file order, PyYAML stays behind the lazy `[config]` boundary,
and the test suite is unusually honest (non-vacuity arms, observed-red regressions, the
`0 skipped` CI assertion). All four phase test modules pass locally (123 passed, 0 skipped).

Adversarial probing found real gaps, each **proven by execution** in this review, not
inferred:

1. **Duplicate YAML keys silently drop authored content** — the exact failure the strict
   schema exists to refuse (Critical).
2. The forward exact-find minter can **pin a claim's span to a YAML comment** — a
   mis-attributed trace the faithfulness gate provably cannot catch (Warning).
3. The D-02 "unrepresentable" claim is overstated: an `AssetBlock` with **empty-string
   provenance minimums constructs fine** — only the loader's runtime check enforces
   non-emptiness (Warning).
4. Invariant 2's enforcement surface (`Surface._published_claims`,
   `open_pull_request`, and `review.review_blockers` in the merge-block CI gate) inspects
   **only `ClaimsBlock`** — the claims this phase put on `NarrativeBlock.items[].claim`
   and the traces on `AssetBlock.evidence` are invisible to the PR gate and to
   `newsletters check` (Warning).

The gate-pin suite (`test_semantic_gate_frozen.py`) does cover the eight functions it
names, and `templates.py` (the policy *data* the pinned arithmetic reads) remains under
the milestone-base blanket freeze in `test_compose.py` — noted below as Info because that
second guard is a softer, editable freeze than the pins claim to be.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: Duplicate YAML keys silently drop authored content — validator accepts, nothing disclosed

**File:** `src/newsletters/weeklyspec.py:342` (`_validate`), `src/newsletters/_yaml_loader.py:85` (`load_config`)
**Issue:** `yaml.safe_load` keeps only the **last** occurrence of a duplicated mapping key.
A weekly authored with `highlights:` twice (a plausible mistake when appending to a long
file, or after a merge-conflict resolution) loses the entire first list before `_validate`
ever sees it. Proven by execution against the live loader:

```python
load_config('week: "W1"\nhighlights:\n  - "first block line"\nhighlights:\n  - "second block line"\n')
# -> {'week': 'W1', 'highlights': ['second block line']}   # first list GONE
_validate(...)  # -> ACCEPTED, no error, no missing[] entry
```

The dropped lines are never minted, never disclosed, and the published weekly is
incomplete with no trace anywhere — precisely the failure the module's own contract names
("Refusing to drop authored content silently", `docs/weekly-spec.md` rule 1, and the
"STRICT SCHEMA, AT BOTH LEVELS" banner). The same hole exists for duplicated fields
*inside* a recognition/member/asset mapping, and is shared by `casespec.py` and the
swimlane loader (all parse through the same `load_config`).
**Fix:** Detect duplicates at the parse boundary — one implementation, in `_yaml_loader`,
so all three loaders inherit it:

```python
def load_config(text: str) -> Any:
    yaml = _load_yaml()

    class _NoDuplicates(yaml.SafeLoader):
        pass

    def _mapping(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in seen:
                raise ValueError(
                    f"duplicate key {key!r} at line {key_node.start_mark.line + 1} — "
                    "YAML keeps only the last occurrence, silently dropping the first. "
                    "Refusing to drop authored content silently."
                )
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep)

    _NoDuplicates.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping
    )
    return yaml.load(text, Loader=_NoDuplicates)  # SafeLoader subclass — still safe-only
```

Add a red-first test (`_validated('highlights: ["a"]\nhighlights: ["b"]')` raises) and
check the fix does not disturb the byte-identical committed-corpus gates (it should not —
the fixtures carry no duplicates).

## Warnings

### WR-01: The exact-find cursor can pin a claim's span to a YAML comment — mis-attributed evidence the gate cannot catch

**File:** `src/newsletters/specspan.py:82` (`SpanMinter.mint`, the `str.find` branch)
**Issue:** `self._raw.find(value, self._cursor)` searches the whole remaining raw text —
including comments and other never-minted text. If a value appears verbatim in a comment
between the cursor and its own field, the claim's trace pins the **comment**, not the
authored field. Proven by execution:

```yaml
highlights:
  - "A line."
# reviewer note: Devi R. did great work this week
team:
  - name: "Devi R."
```

The minted `team.name` claim's span lands on line 5 (the comment), not line 7 (the field).
The faithfulness gate passes (identical text), so — exactly like the span-swap failure
03-RESEARCH proved — no gate can catch it; the reviewer clicking through to evidence sees
a comment vouching for a team member. The module was promoted verbatim (casespec shares
this), but the weekly is the first spec kind where authors realistically write comments
alongside people's names.
**Fix:** Before the whole-text `find`, locate the value **within the field/item region
first** (`self._raw.find(value, region_start, region_end)` using `_field_region(key)` /
`_item_region()`), falling back to the current behavior only when the region search fails.
Add a red-first test with a comment carrying the duplicated value.

### WR-02: "Provenance-less placement is unrepresentable" is overstated — empty-string minimums construct fine

**File:** `src/newsletters/semantic.py:404` (`AssetRecord`), `src/newsletters/semantic.py:561` (`AssetBlock`)
**Issue:** The docstrings (and `docs/weekly-spec.md` D-02) claim the *type* makes an asset
without provenance unrepresentable. Pydantic only enforces *presence*, not non-emptiness —
proven by execution:

```python
AssetRecord(key="k", file="f", sha256="s", folder="", date="", event="")  # constructs
AssetBlock(asset=that_record, evidence=[one_trace])                        # constructs
```

The real enforcement lives solely in `_place_assets`' runtime `.strip()` check
(`weeklyspec.py:551-560`); any other code path (a future composer, a hand-built Surface, a
JSON round-trip of tampered data) can put a provenance-empty `AssetBlock` on a Surface
with no `ValidationError`. The type-level half of D-02 is currently a presence check
wearing an unrepresentability claim.
**Fix:** `folder: str = Field(min_length=1)` (likewise `date`, `event`, `file`, `sha256`,
`key`) on `AssetRecord`. Note the Half-B insertion-only guard
(`test_semantic_py_diff_deletes_no_line`) means this edit belongs to the next milestone
window, with the docstring corrected in the meantime — or make it now and update the
guard's expectation deliberately, in the same commit, with the reason stated.

### WR-03: Invariant-2 enforcement ignores the new claim carriers — `NarrativeBlock` claims and `AssetBlock` traces are invisible to every gate

**File:** `src/newsletters/semantic.py:687` (`Surface._published_claims`), `src/newsletters/review.py:86-87` (`review_blockers`)
**Issue:** Both the PR-gate untraced check (`open_pull_request` → `_published_claims`) and
the CI merge-block checker (`newsletters check` → `review_blockers`) iterate
`surface.blocks` looking **only** for `ClaimsBlock`. This phase added real `Claim` objects
to `NarrativeBlock.items[].claim` and real `Trace`s to `AssetBlock.evidence`, and neither
is inspected:

- a `NarrativeItem` carrying an untraced or un-entailed claim passes `open_pull_request`;
- a **published** weekly whose spec file later drifts has stale narrative claims and stale
  asset traces that `review_blockers` never re-checks — and the HTML `NarrativeBlock`
  branch renders no evidence chip, span, or STALE badge (`render.py:629-638`, per the
  class map), so the drift is invisible in the render too.

The loader constructs these honestly today, but the repo's stated bar is structural
enforcement ("prove it with a test"), not constructor discipline. The hard rule "every
published claim traces to evidence" is currently enforced for one block kind out of the
four claim-carrying ones.
**Fix:** Extend `review_blockers` (it lives outside the frozen gate functions) to walk
`NarrativeBlock` items' claims and `AssetBlock.evidence` with the same
stale/entailed/addressed predicates; add a red-first test planting a stale narrative claim
on a published weekly. Extending `_published_claims` itself touches a pinned function —
that is a conversation (update the pin in the same commit), or route the widened check
through `review_blockers` only and record the decision.

### WR-04: `_kpi_item` re-implements `compose._compose_kpi_item` and re-declares its disclosure wording — the exact two-copies drift this phase's own promotions exist to prevent

**File:** `src/newsletters/weeklyspec.py:860-913` (`_NO_KPIS`, `_UNCOMPUTABLE_DELTA`, `_ONE_ENDPOINT`, `_kpi_item`)
**Issue:** The endpoint policy and all three disclosure strings are duplicated
byte-for-byte from `compose.py:203-233` (where they are inline f-strings). The repo's own
recorded rule — the reason `specspan.py` exists, the reason `addressed` was promoted this
very phase — is that "two copies of a trust predicate drift exactly as two normalizers
do." If Phase-N edits `compose._compose_kpi_item`'s policy or wording, the weekly's copy
drifts silently; the honesty panel then reads two voices for one rule.
**Fix:** Promote `_compose_kpi_item` to a public `compose.compose_kpi_item` (with the
wording as module constants) and import it in `weeklyspec`, the same move `addressed`
already made. Delete `_kpi_item` and the three duplicated constants.

### WR-05: Blank authored list items are dropped with no disclosure — contradicts "anything absent, empty … lands in missing[]"

**File:** `src/newsletters/weeklyspec.py:736-741` (narrative filter), `:756-764` (team lines)
**Issue:** The module banner promises "EVERY ABSENCE IS DISCLOSED. Anything absent, empty
or unlocatable lands in `Distillation.missing[]`." A blank item *inside* a non-empty list
(`highlights: ["kept", ""]`, or a `~` null entry, or a blank team line) is filtered out by
`_route` returning `None` with **no** `missing[]` entry — proven by execution: the load
carries `['kept']` and `missing[]` mentions nothing. `weekly_slots`' docstring even relies
on this drop ("the loader drops blank list items"), so the two docstrings currently
contradict each other. No authored *text* is lost, but a positionally-authored empty line
disappears without the disclosure the contract promises.
**Fix:** In the narrative/lines comprehensions, append
`absent(f"{key}[{index}]")` to `missing` when `_route` returns `None` for a present-but-blank
item (mirroring `_disclose_gaps`' per-item style), or amend the banner and
`docs/weekly-spec.md` to state blank items are dropped undisclosed — one of the two, in
the same commit.

### WR-06: A placed asset with no alt/caption renders as an empty bordered box carrying zero information

**File:** `src/newsletters/render.py:662-668` (`AssetBlock` branch)
**Issue:** The branch emits only `heading` (the authored `alt`, Optional) and `caption`
(Optional). Both fields default to absent, so a fully provenance-complete, placed asset
whose author wrote no `alt`/`caption` renders as
`<div class="block"><figure class="diagram"></figure></div>` — `.diagram` has a border and
24px padding, so the reviewer sees a visible **empty box** and can learn nothing about the
asset (no key, file, folder, date, event, or link is ever rendered). The composer's own
rule is "an empty block would render an empty div.block and assert nothing"
(`weeklyspec.py:938-940`), and the class map gives the branch a `dh` + `figcaption` shape
without requiring either to exist. The committed fixture happens to author both fields, so
no test observes this state.
**Fix:** Render the record's provenance line as the guaranteed content (it is always
non-empty for a *placed* asset), e.g.
`<figcaption class="sg-mono">{_e(b.asset.folder)} · {_e(b.asset.date)} · {_e(b.asset.event)}</figcaption>`
alongside the optional heading/caption — all through `_e()` — and update the class map in
`docs/weekly-spec.md` in the same change (spec and code must not drift). Note `_CSS` is
byte-frozen (`test_weekly_blocks._CSS_SHA256`); the suggested markup uses existing classes
only.

## Info

### IN-01: `build_weekly_report` does not dedupe `missing[]`

**File:** `src/newsletters/weeklyspec.py:959,989-992`
**Issue:** `compose_module_report` runs `_dedup_in_order(missing)`; the weekly composer
does not, so a `binding.missing` entry that repeats a loader disclosure (or a dropped
claim text equal to an existing note) renders twice in the honesty panel.
**Fix:** Reuse `compose._dedup_in_order` (promote it) before constructing the Surface.

### IN-02: A file named `weekly.yml` gets the id `weekly-weekly`

**File:** `src/newsletters/weeklyspec.py:1056`
**Issue:** `removeprefix('weekly-')` only strips the hyphenated prefix; the bare stem
`weekly` survives, producing `weekly-weekly` (`casespec` has the analogous `case-case`).
Cosmetic; ids stay deterministic.
**Fix:** `slug = slugify(stem); slug = slug.removeprefix("weekly-") if slug != "weekly" else ""` or equivalent.

### IN-03: Stale docstring in `pptx_writer.py` cites the removed semantic byte-freeze

**File:** `src/newsletters/pptx_writer.py` (module banner, "THE WRITER READS THE REVIEW GATE" paragraph)
**Issue:** It names "the standing `git diff --exit-code -- src/newsletters/semantic.py`
gate" as a durable guard — this phase deliberately removed that guard and replaced it with
the pin suite (`test_semantic_gate_frozen.py`). A reader auditing the no-auto-publish
defenses would go looking for a gate that no longer exists.
**Fix:** Point the banner at `tests/test_semantic_gate_frozen.py`.

### IN-04: Non-string asset mapping keys fail with a raw Pydantic error, not the teaching voice

**File:** `src/newsletters/weeklyspec.py:416,785`
**Issue:** `_validate` never checks that `assets:` mapping keys are strings; a YAML key
like `42:` survives validation and explodes later as `AuthoredAsset(key=42)` →
`ValidationError` naming a type instead of the typo — exactly the failure shape the
`stands_in_for` check at `:427-437` exists to pre-empt for values.
**Fix:** In the `assets` branch of `_validate`, refuse non-`str` keys with the same
teaching wording (quote the key).

### IN-05: The gate pins freeze the arithmetic but not the policy data it compares against

**File:** `tests/test_semantic_gate_frozen.py:47-58`, `tests/test_compose.py:553-558`
**Issue:** `Review.satisfied` reads `policy.min_approvals` / `policy.require_peer` —
values defined in `templates.py` (`ReviewPolicy`, `REPORT.review_policy`). Changing those
to `min_approvals=0` defeats "no auto-publish" while all eight pinned digests stay green.
Today `templates.py` is covered only by the milestone-base blanket freeze in
`test_compose.py` — a guard a future phase will legitimately edit, with none of the pin
suite's "update in the same commit and justify" teeth. The pin suite's claim ("the eight
functions that ARE the gate") should either be true or say what it excludes.
**Fix:** Pin `ReviewPolicy` (source hash of the class, or the `REPORT.review_policy`
values) in `test_semantic_gate_frozen.py`, or document the exclusion in its module
docstring naming `test_compose.py` as the covering guard.

### IN-06: `compose_module_report` still emits an empty `ClaimsBlock` per section

**File:** `src/newsletters/compose.py:370`
**Issue:** When every claim in a binding is routed to `missing[]`, `ClaimsBlock(claims=[])`
is still appended — rendering the "Findings — every claim traced" heading over nothing.
Pre-existing Phase-2 behavior (this phase only touched the `addressed` rename in this
file), but it now contrasts with the weekly composer's explicit omit-empty rule; one of
the two conventions should be declared canonical. Also `blocks: list = []` at `:319` is
untyped where `list[Block]` is the codebase norm.
**Fix:** Guard with `if kept:` plus a disclosure, or record the asymmetry as deliberate.

### IN-07: The `weekly` CI job enumerates modules by hand

**File:** `.github/workflows/ci.yml:220-224`
**Issue:** The job lists nine test files. A tenth weekly-path module added in a later plan
runs nowhere unless someone remembers to append it here — the same "green because never
run" shape (W21) this job exists to close, one level up. The `0 skipped` assertion cannot
catch a module that is never named.
**Fix:** Consider a marker (`-m weekly`) or a `tests/weekly/` directory glob so new
modules are collected by construction; at minimum, note the maintenance duty in the job
comment.

---

_Reviewed: 2026-08-29T08:10:43Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
