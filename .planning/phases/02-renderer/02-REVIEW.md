---
phase: 02-renderer
reviewed: 2026-08-29T05:48:20Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - src/newsletters/pptx_writer.py
  - tests/test_pptx_writer.py
  - tests/test_ai_optional.py
  - tests/fixtures/weekly/_author_template.py
  - tests/fixtures/weekly/_record_determinism_evidence.py
  - tests/test_pptx_determinism.py
  - .github/workflows/ci.yml
  - pyproject.toml
findings:
  critical: 0
  warning: 6
  info: 7
  total: 13
status: fixed
fixed_at: 2026-08-29T06:10:00Z
fixed: 9
carried: 4
---

# Phase 2: Code Review Report

**Reviewed:** 2026-08-29T05:48:20Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** fixed (all 6 Warnings + 3 trivial Info fixed; 4 Info carried)

## Fix Outcomes (2026-08-29)

All six Warnings fixed; the three trivial zero-risk Info findings fixed; the four Info findings
needing CI-wiring / atomic-write / template-regeneration / layout-walk decisions carried to the
phase backlog. Gates after fixes, each run once: full suite **601 passed / 64 skipped** (baseline
595 + the 6 new regression tests), `lint-imports` **2 kept / 0 broken**,
`_record_determinism_evidence.py --check` **OK** (6 fields re-verified live),
`git diff --exit-code -- src/newsletters/semantic.py content/ tests/fixtures/pptx/*.pptx
tests/fixtures/weekly/template.pptx` **clean** (no committed binary moved; the evidence JSON and
decision note changed per WR-01, as sanctioned). mypy/black clean on touched files; isort
no-new-failures (DEF-15 debt unchanged).

| Finding | Outcome | Commit |
|---------|---------|--------|
| WR-01 | **Fixed** — `part_digest` rows length-prefixed (8-byte BE name length); evidence re-recorded via the sanctioned recorder (`part_digest` `606c2464…` → `d7ff171a…`; `normalized_a_sha256` re-measured byte-identical, proving no content moved); decision note amended with a dated addendum | `1f4dce0` |
| WR-02 | **Fixed** — duplicate-name refusal scoped to `NL_`-prefixed names; unprefixed duplicates bind first-seen; two-slide auto-name regression test added; contract clarification recorded as a dated addendum in the decision note | `530d996` |
| WR-03 | **Fixed** — a bare `str` slot value is treated as ONE paragraph (`[line]`), never per-character explosion; annotations widened to `Union[str, Sequence[str]]`; tested both via `fill_slot` and end to end through the render path | `2763126` |
| WR-04 | **Fixed** — `lint-imports` resolved next to `sys.executable` (with `shutil.which` fallback); the no-op `python -m importlinter.cli` fallback refused — importlinter-installed-but-script-missing now FAILS loud; only a truly bare env skips | `f58031d` |
| WR-05 | **Fixed** — both files import `MARKER` and `DRAFT_STATUS` (aliased `GATE_STATE`) from `newsletters.pptx_writer` instead of re-declaring literals | `b1b5a3d` |
| WR-06 | **Fixed** — `bind_slots` refuses any `slots` key without the `NL_` prefix (sixth refusal, teaching error); `Footer`-binding regression test added; recorded as a dated addendum in the decision note | `2a7e393` |
| IN-01 | **Fixed** — module docstring no longer claims the contracts run on the bare-install job; states the bare install proves importability and the contracts execute in the `pptx` CI job | `062a2d2` |
| IN-02 | **Fixed** — `fill_slot` refuses all-blank line lists (`[""]`, whitespace-only) like `[]`; a blank spacer among real content stays legitimate and is tested as such | `b0f71fd` |
| IN-03 | **Carried** — wiring `--check` into the `pptx` CI job needs the python-pptx-floor-pin tradeoff decided (an upstream upgrade could legitimately redden a wired check); not zero-risk, deferred with the counterweight recorded in the finding | — |
| IN-04 | **Fixed** — `_walk` bounded at `_MAX_GROUP_DEPTH=64` with a teaching `ValueError`; both sides of the bound tested | `3e94648` |
| IN-05 | **Carried** — atomic `os.replace` write is a behavior change to the disk entry point; deferred (the finding records the fix shape) | — |
| IN-06 | **Carried** — adding overflow-safe settings to `_author_template.py` is dead code until the next regeneration, which is frozen this phase by P-06; apply on regeneration per the finding | — |
| IN-07 | **Carried** — layout/master slot walking is a template-contract scope decision (walk-and-refuse vs document-slides-only), owned by the Phase-4 operator recipe | — |

## Summary

Reviewed the Phase 2 deterministic template-driven PPTX writer, its test battery, the fixture
authors, and the CI wiring. Hard rules were verified against the live repo, not the tests' word:

- **No auto-publish:** confirmed. `pptx_writer.py` contains no assignment to any `Surface` field;
  the gate is read via `surface.is_published` only (lines 581, 592). `test_render_does_not_touch_the_gate`
  re-proves it via `model_dump()` equality.
- **AI-optional core:** confirmed. Module level is stdlib-only; the only pptx imports are indented
  inside `bind_slots` (line 370) and `render_surface_pptx_bytes` (line 568, via the existing
  `_pptx_loader` boundary). `newsletters/__init__.py` does not export the module. The subprocess
  meta-path-block tests are real, not string checks alone.
- **Determinism:** confirmed. No wall-clock in the write path; `EPOCH_ZERO` core properties
  (tz-stripped at the OPC boundary); `prs.save(BytesIO)` is the only clock and `normalize_opc_zip`
  removes its trace. Ran the full battery independently: **56 passed, 1 skipped** (the documented
  ambient-plugin xfail path), in 11.6s.

Findings below were **reproduced live in the .venv** where marked, not inferred from reading.
Six warnings: a hash-domain-separation gap in the Phase-4 trust primitive, three contract gaps
in the writer's fail-loud surface (two reproduced), one false-green test fallback (reproduced),
and one string-drift violation of the module's own anti-drift rule. No blocker: every defect
found fails loud or is off the shipped happy path; none produces silently wrong output for the
committed template + composer-supplied slots flow this phase ships.

## Warnings

### WR-01: `part_digest` row encoding lacks domain separation — crafted member names can collide the Phase-4 trust digest

**File:** `src/newsletters/pptx_writer.py:245-251`
**Issue:** Rows are serialized as `name_utf8 + b"\0" + hex_digest_ascii + b"\n"`. Member names are
attacker-controlled bytes (a ZIP name may contain NUL and newline), so the row boundaries are
ambiguous: a single member named `"a\0" + <64 hex chars> + "\nb"` whose content hashes to `H`
serializes to exactly the same byte stream as the two-member archive `{a: A, b: B}` where
`sha256(A)` is those 64 hex chars and `sha256(B) == H`. Two archives with entirely different part
content can therefore share a `part_digest`. The docstring sells this digest as "the exact spoof
the Phase-4 trust gate must catch" (line 237) — this construction is precisely such a spoof. The
duplicate-name refusal does not prevent it (one member, one name).
**Fix:** Make the encoding injective by length-prefixing the name:
```python
for name, part in rows:
    encoded = name.encode("utf-8")
    digest.update(len(encoded).to_bytes(8, "big"))
    digest.update(encoded)
    digest.update(part.encode("ascii"))
```
Note this changes every recorded digest, so `.planning/notes/2026-08-29-pptx-determinism-evidence.json`
(`part_digest_a`/`part_digest_b`) must be re-recorded in the same change — which is exactly what
`_record_determinism_evidence.py` (no args) exists for. Must land before Phase 4 builds the
committed==fresh gate on this primitive.

### WR-02: `bind_slots` duplicate-name refusal is deck-wide over ALL shapes — real multi-slide PowerPoint decks with default auto-names are always refused

**File:** `src/newsletters/pptx_writer.py:372-383`
**Issue:** The collision check covers every shape on every slide, including unprefixed decorative
shapes never referenced by `slots`. PowerPoint (and python-pptx) auto-name shapes *per slide*
("Title 1", "TextBox 1"), so any real two-slide operator deck with default names collides.
**Reproduced live:** a two-slide deck with one default-named textbox per slide yields
`['TextBox 1', 'TextBox 1']` and `bind_slots(prs, {})` raises
`"template has two shapes named 'TextBox 1'..."` — even with an *empty* slots mapping. The
binding is only actually ambiguous for names in `slots` or carrying the `NL_` prefix; a collision
between two unreferenced decorative shapes drops nothing. The decision note itself flags the
template contract as "MEDIUM confidence because no real operator deck was available to test
against; flagged for confirmation at the Phase 2 human-verify checkpoint" — this is that
confirmation failing. Fail-loud (not silent), hence Warning not Critical, but the shipped contract
rejects ordinary decks the moment an operator adds a second slide without renaming every box.
**Fix:** Refuse collisions only for names that matter to the contract — keep last-wins impossible
where it has consequences:
```python
ambiguous = shape.name in slots or shape.name.startswith(SLOT_PREFIX)
if shape.name in by_name and ambiguous:
    raise ValueError(...)
by_name.setdefault(shape.name, shape)
```
(or record the deck-wide scope as a deliberate decision in the decision note AND extend the
teaching error to name the default-auto-name cause, since "rename one in the Selection Pane" will
be the operator's every-deck experience otherwise).

### WR-03: `fill_slot` accepts a bare `str` as `lines` and silently explodes it into per-character paragraphs

**File:** `src/newsletters/pptx_writer.py:426, 543-548`
**Issue:** `lines: Sequence[str]` — but `str` *is* a `Sequence[str]`, so neither mypy nor any
refusal catches `slots={"NL_X": "hello"}`. **Reproduced live:** `fill_slot(tf, "hello")` produces
five paragraphs `['h', 'e', 'l', 'l', 'o']` — a silently misrendered deck from the single most
likely caller typo, in a module whose entire design ethos is "refuse every ambiguity rather than
guessing." Both `fill_slot` and `render_surface_pptx_bytes` (via its `slots` mapping) are exposed
to this.
**Fix:** Add a refusal at the top of `fill_slot` (covers both entry points):
```python
if isinstance(lines, (str, bytes)):
    raise ValueError(
        f"slot content must be a sequence of lines, got a bare {type(lines).__name__} "
        f"({lines!r:.60}) — a str is a Sequence[str] of its characters, and filling with it "
        "would ship one paragraph per character. Wrap it: [line]."
    )
```

### WR-04: `test_import_linter_contract_holds` fallback path is a no-op that always passes

**File:** `tests/test_ai_optional.py:119-141`
**Issue:** When `.venv/bin/lint-imports` is absent but `importlinter` is importable, the test runs
`python -m importlinter.cli lint`. **Verified live:** `importlinter/cli.py` has no
`if __name__ == "__main__"` block and there is no `importlinter/__main__.py`, so `-m` imports the
module, executes nothing, and exits 0 with empty output — the contract assertion passes
unconditionally, including with a broken core→AI edge. In that environment this guard test is a
false green (contrast: the real `.venv/bin/lint-imports` prints "Contracts: 2 kept, 0 broken").
The hardcoded `.venv/bin/` path also fails on Windows (`Scripts/`) and any non-`.venv` env,
making the broken fallback the *normal* path there. The CI `import-linter` job invokes
`lint-imports` directly and is unaffected — this is the local/defense-in-depth half going soft.
**Fix:** Resolve the console script relative to the running interpreter and fail loud (not pass)
when it's missing while importlinter is installed:
```python
script = Path(sys.executable).parent / ("lint-imports.exe" if os.name == "nt" else "lint-imports")
if not script.exists():
    found = shutil.which("lint-imports")
    if found is None:
        pytest.skip(...) if _importlinter_absent() else pytest.fail(
            "importlinter installed but lint-imports script not found — refusing the "
            "python -m importlinter.cli fallback, which is a no-op that exits 0")
    script = Path(found)
proc = subprocess.run([str(script)], cwd=REPO_ROOT, capture_output=True, text=True)
```

### WR-05: `MARKER` / `GATE_STATE` re-declared as local string literals despite the writer's canonical constants — the exact drift the module forbids

**File:** `tests/test_pptx_determinism.py:81-82`; `tests/fixtures/weekly/_record_determinism_evidence.py:63-64`
**Issue:** `pptx_writer.py:158-177` states the constants exist "for the same anti-drift reason
`_pptx_loader.MISSING_PPTX_MESSAGE` is one: the writer, its tests and the fixture authors must
assert against ONE spelling of each, not against a string literal copied into four files that
silently diverge." Yet both files re-declare `MARKER = "generated-by:newsletters"` and
`GATE_STATE = "draft"` locally — and both *already import other names from `pptx_writer`*, so the
canonical `MARKER` / `DRAFT_STATUS` were one import away. If the writer's spelling ever changes,
the determinism suite and the evidence recorder each keep asserting their own local literal and
stay green while measuring a marker the writer no longer writes (the recorder's comment "identical
to the ones test_pptx_determinism.py writes" is enforced only by eyeball).
**Fix:** In both files, replace the local literals with
`from newsletters.pptx_writer import MARKER, DRAFT_STATUS` (aliasing `DRAFT_STATUS as GATE_STATE`
where the local name is load-bearing for readability).

### WR-06: Content bound to an UNPREFIXED shape name is silently filled — operator decorative content can be overwritten with no refusal

**File:** `src/newsletters/pptx_writer.py:393-399, 413-423, 578-579`
**Issue:** `SLOT_PREFIX`'s contract (line 163-165) is "only shapes named `NL_*` are renderer
slots." But `bind_slots`' unknown-name check only requires the name to *exist* in the deck:
`slots={"Footer": ["renderer text"]}` passes every refusal and `render_surface_pptx_bytes` fills
the operator's footer, silently overwriting their content. The prefix currently discriminates in
one direction only (unfilled-slot), while the fill direction accepts any existing name. A composer
bug — or a hand-written slots mapping — that targets a decorative shape produces exactly the
"operator's logo/footer modified" failure `test_sample_surface_renders_through_the_committed_template`
asserts against, with no teaching error. In a module that refuses five other ambiguities, this
asymmetry is the remaining silent-write path into operator content.
**Fix:** Add a sixth refusal in `bind_slots`:
```python
unprefixed = sorted(name for name in slots if not name.startswith(SLOT_PREFIX))
if unprefixed:
    raise ValueError(
        f"content is bound to unprefixed shape name(s) {unprefixed!r} — only "
        f"{SLOT_PREFIX!r}-prefixed shapes are renderer slots; unprefixed shapes are the "
        "operator's (logos, footers, page numbers) and are never written. Rename the shape "
        "with the reserved prefix if it is meant to be a slot."
    )
```
plus a test binding content to `"Footer"` and asserting the raise.

## Info

### IN-01: Module docstring claims the duplicate-member and idempotence contracts "run on the bare-install CI job" — they don't run there

**File:** `src/newsletters/pptx_writer.py:43-45`; `.github/workflows/ci.yml:76`
**Issue:** The bare-install job runs only `tests/test_semantic.py tests/test_distill_socket.py
tests/test_ai_optional.py`. The duplicate-member/idempotence contracts live in
`test_pptx_determinism.py` / `test_pptx_writer.py`, which are not in that list and would
`importorskip`-skip on a bare install anyway; they actually run in the `pptx` job (with the
extra). The bare install only proves the module *imports*. The justification is sound; the
coverage claim is false and would mislead a coverage audit.
**Fix:** Reword to "which is what keeps the normalizer importable (and its contracts testable) on
a bare install; the contracts themselves execute in the `pptx` CI job."

### IN-02: `fill_slot` refuses `[]` but accepts `[""]` — the blank box ships anyway

**File:** `src/newsletters/pptx_writer.py:469-474`
**Issue:** The empty-list refusal exists because "an empty slot ships a blank box to a reader,"
but `[""]` (and whitespace-only lines) pass and produce the same visually blank box.
**Reproduced live:** `fill_slot(tf, [""])` succeeds, run text `''`. If blank-box-to-reader is the
harm, the refusal should cover the equivalent input; if `[""]` is a legitimate spacer, say so in
the docstring so the asymmetry is a decision, not an accident.
**Fix:** Either extend the refusal (`if not lines or not any(line.strip() for line in lines)`),
or document the `[""]`-spacer allowance explicitly.

### IN-03: `_record_determinism_evidence.py --check` is not wired into any CI job — the evidence gate is manual-only

**File:** `tests/fixtures/weekly/_record_determinism_evidence.py`; `.github/workflows/ci.yml:145-174`
**Issue:** `test_pptx_writer.py:20-28` leans on "regenerating [the template] would turn this
phase's own `_record_determinism_evidence.py --check` gate red" — but no workflow runs `--check`,
so the gate only goes red on a machine where someone remembers to run it. The compared fields are
implementation-independent (safe cross-environment). Counterweight: the `python-pptx>=1.0.2`
floor pin means an upstream upgrade in CI could legitimately shift part bytes and redden a wired
check without any repo change — if that tradeoff is why it stays manual, record it; otherwise add
`python tests/fixtures/weekly/_record_determinism_evidence.py --check` as a step in the `pptx` job.

### IN-04: `_walk` has unbounded recursion — a hand-crafted deeply-nested-group template raises `RecursionError`, not a teaching error

**File:** `src/newsletters/pptx_writer.py:335-338`
**Issue:** ~1000 nested groups in an untrusted template blows the Python stack inside
`bind_slots` — a stack trace, which is the failure shape the five refusals exist to prevent.
Pathological-input only (no real deck nests that deep), so Info.
**Fix:** Either an explicit-stack iteration, or a depth counter with a `ValueError` naming the
absurd nesting.

### IN-05: `render_surface_pptx` write is not atomic — a partial write leaves a truncated deck at `out_path`

**File:** `src/newsletters/pptx_writer.py:624-627`
**Issue:** The docstring's "ONE write of complete, already-normalized bytes" guards against the
raise-mid-rewrite shape, but `Path.write_bytes` can still partially write (disk full, SIGKILL),
leaving a truncated `.pptx` a later reader cannot distinguish from a complete one — the same
"un-normalized deck on disk with no way to tell" class the docstring worries about.
**Fix:** Write to `out_path.with_suffix(".pptx.tmp")` (same directory) then `os.replace` onto
`out_path`.

### IN-06: The committed template keeps `add_textbox`'s overflow-unsafe defaults that the in-test builders explicitly fix

**File:** `tests/fixtures/weekly/_author_template.py:110-117`; contrast `tests/test_pptx_writer.py:197-213`
**Issue:** `_textbox` in the test module sets `word_wrap = True` / `auto_size = NONE` and calls
the defaults "the worst combination" (overflow escapes the slide silently — P-07 / Pitfall 3).
`_author_template.py` — which produces the artifact the repo actually ships and renders SC-5
through — does neither, so the committed template carries exactly that worst combination. Frozen
this phase by P-06 (regeneration would redden the evidence digests), and the P-07 recipe is
deferred to Phase 4's `docs/weekly.md` — but nothing in `_author_template.py` records that its own
output violates P-07. On the next regeneration, add the two settings and note the P-07 tie.
**Fix:** Add `frame.word_wrap = True; frame.auto_size = MSO_AUTO_SIZE.NONE` to the builder now
(dead until regeneration, but the drift is then impossible), with a comment citing P-06 for why
the committed bytes lag.

### IN-07: `NL_`-prefixed shapes on slide layouts/masters are invisible to `bind_slots` — neither fail-loud direction can fire for them

**File:** `src/newsletters/pptx_writer.py:373`
**Issue:** The walk covers `prs.slides` only. An operator who authors a slot on a slide *layout*
(footer-style editing in Slide Master view is ordinary PowerPoint hygiene) gets a shape that
renders on every slide, carries the reserved prefix, and is never bound: content bound to its name
is refused as "unknown" (loud — fine), but with no content bound, the unfilled-slot refusal
cannot fire and the deck ships the layout's placeholder text silently — the exact blank-box-class
gap refusal 4 exists to prevent. Speculative frequency, hence Info.
**Fix:** Either walk layout/master shapes for `NL_`-prefixed names and refuse them with a teaching
error ("slots must live on slides, not layouts"), or document the slides-only scope in the
template contract / operator recipe.

---

_Reviewed: 2026-08-29T05:48:20Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
