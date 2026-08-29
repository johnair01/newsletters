---
phase: 01-specify-de-risk
reviewed: 2026-08-29T04:06:26Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - tests/fixtures/weekly/_determinism.py
  - tests/fixtures/weekly/_author_template.py
  - tests/fixtures/weekly/_record_determinism_evidence.py
  - tests/test_pptx_determinism.py
  - tests/fixtures/pptx/_author_fixtures.py
  - docs/weekly-spec.md
  - docs/architecture.md
findings:
  critical: 1
  warning: 7
  info: 4
  total: 12
status: issues_found
---

# Phase 1: Code Review Report

**Reviewed:** 2026-08-29T04:06:26Z
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the determinism-spike code (stdlib zip normalizer, double-write test with negative
control, evidence recorder, template author) and the two spec docs. The core engineering is
sound and was verified live: all 5 tests pass, `--check` re-verifies the committed evidence
(exit 0), the committed template is idempotent under `normalize_opc_zip` and its core
properties are scrubbed, `_determinism.py` is genuinely stdlib-only, and every quantitative
claim in the docs (11-member `Block` union, bare `return ""` fall-through in `_block_html`,
64-char sha256 example) checks out against the live repo.

Three classes of defect were found and **proven**, not inferred:

1. **The skipif guard in `test_pptx_determinism.py` does not guard** — a module-level
   `from pptx import Presentation` errors at pytest *collection* on a bare install; the
   `pytestmark` skip never gets a chance to fire (reproduced with a minimal demo module:
   `Interrupted: 1 error during collection`). The sibling pptx tests avoid exactly this with
   lazy in-function imports.
2. **`normalize_opc_zip` and `part_digest` are wrong on duplicate-member-name archives**
   (reproduced): the normalizer silently *rewrites part bytes* — violating its own headline
   contract — and two archives with *different content* produce the *same* `part_digest`.
   Unreachable from python-pptx output today, but the module's own docstring extends its
   threat model to malicious operator-supplied templates (T-01-06) and designates
   `part_digest` as the Phase-4 trust-gate assertion.
3. **Several load-bearing comments/docstrings state falsehoods** — a promised fail-loud
   scrub guard that does not exist in any test, an "imported rather than re-minted" comment
   over a hand-minted second epoch sentinel, and `_author_fixtures.py` still asserting in a
   function docstring the exact claim its own module header marks as false. In a repo whose
   stated method is "specs are the source of truth" and "a decision without evidence is a
   vibe", these are not cosmetic.

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: `pytestmark` skipif does not protect the module-level `pptx` import — bare-install `pytest tests/` errors at collection instead of skipping

**File:** `tests/test_pptx_determinism.py:62`
**Issue:** Line 62 executes `from pptx import Presentation` at module import time. A
`pytestmark = pytest.mark.skipif(...)` marker is evaluated *per collected test item*; it does
not prevent pytest from importing the module during collection. On an install without the
`[pptx]` extra, collection of this file raises `ModuleNotFoundError` and the run aborts
(`Interrupted: 1 error during collection` — reproduced empirically with an identical minimal
module). This directly contradicts the module's own docstring (lines 41–43: "the only
sanctioned way for `tests/` to touch the optional extra — that is what keeps the bare-install
CI gate green") and violates the phase hard rule "pptx only behind the sanctioned skipif
guard". The repo's actual sanctioned pattern is visible in the siblings:
`tests/test_pptx_golden.py` and `tests/test_pptx_adapter.py` carry the same `pytestmark` but
import all pptx-dependent code **lazily inside functions** ("imported lazily so this module
imports without the [pptx] extra"), and `newsletters/adapters/pptx_adapter.py` has no
top-level `pptx` import. Note the CI `bare-install` job currently runs only three named test
files, so CI stays green — which makes this a *silent* landmine for any bare-env
`pytest tests/` run rather than a caught one.
**Fix:**
```python
# replace line 62
pptx = pytest.importorskip("pptx", reason="optional [pptx] extra (python-pptx) not installed")
Presentation = pptx.Presentation
```
(`importorskip` raises `Skipped` at module level, which pytest converts to a module skip —
the one sanctioned way to touch the extra at import time; `tests/test_pptx_loader.py:54`
already uses it.) Alternatively move `from pptx import Presentation` inside `_render_bytes`
and `test_normalized_archive_is_valid_and_reopens_with_marker_intact`, matching the golden
test's lazy-import convention.

## Warnings

### WR-01: `normalize_opc_zip` silently rewrites part bytes, and `part_digest` collides, on duplicate-member-name archives

**File:** `tests/fixtures/weekly/_determinism.py:86-88, 109-113`
**Issue:** Both functions read entries **by name** (`zin.read(n)`, dict keyed on
`i.filename`). The ZIP format permits multiple entries under one name; `ZipFile.read(name)`
resolves to the *last* one. Proven live: for an archive containing `evil.xml` twice
(`FIRST-CONTENT`, then `SECOND-CONTENT`), the normalizer emits **two entries both carrying
`SECOND-CONTENT`** — i.e. it changed part bytes, violating the module's headline contract
"Part BYTES are never touched" (line 17) — and `part_digest` returns **the same digest** for
two archives whose first `evil.xml` bytes differ. This matters because the module itself
claims a security property for *operator-supplied* (untrusted) templates (T-01-06, lines
36–41), instructs Phase 2 to inherit that property "by reusing this module", and designates
`part_digest` as the Phase-4 committed==fresh trust assertion (line 34). Duplicate-name
shadowing is a classic archive-smuggling trick precisely because different consumers pick
different entries. python-pptx never emits duplicates, so nothing shipped in this phase
misbehaves — but the trust primitive has a documented contract it provably does not meet.
**Fix:** iterate `infolist()` and read via handles, and refuse duplicate names loudly:
```python
with zipfile.ZipFile(io.BytesIO(raw)) as zin:
    infos = zin.infolist()
    names = [i.filename for i in infos]
    if len(names) != len(set(names)):
        raise ValueError(f"duplicate member names in archive: refusing to normalize")
    entries = [(i.filename, i.external_attr, zin.open(i).read()) for i in infos]
```
Apply the same duplicate check (or per-`ZipInfo` reads) in `part_digest` and
`differing_parts`, and add a duplicate-name regression test.

### WR-02: The promised fail-loud scrub guard for the template's core properties does not exist

**File:** `tests/fixtures/weekly/_author_template.py:27-28` (and `tests/test_pptx_determinism.py`)
**Issue:** The docstring states "`test_pptx_determinism.py` asserts the absence against the
written `docProps/core.xml`, so a regeneration that forgot to scrub fails loudly." No such
assertion exists: the read-back test checks only `category`, `content_status`, `created`
and `modified` (lines 231–235), and a repo-wide grep for `Steve Canny` /
`last_modified_by` / `author` assertions in `tests/` returns nothing. A regeneration of
`template.pptx` that skipped `_CORE_PROPERTIES` (shipping "Steve Canny" and the
"generated using python-pptx" marketing string into the fixture corpus — the exact
embarrassment the docstring names) would pass the entire suite. The guard is promised, not
implemented — precisely the drift the project's own conventions forbid.
**Fix:** in `test_normalized_archive_is_valid_and_reopens_with_marker_intact` (or a new
test), assert against the **committed** template, not just the rendered deck:
```python
tpl = Presentation(str(TEMPLATE))
cp = tpl.core_properties
assert cp.author == "newsletters fixture author", cp.author
assert cp.last_modified_by == "newsletters fixture author", cp.last_modified_by
assert "python-pptx" not in (cp.comments or "").lower() or "regenerate" in cp.comments
assert normalize_opc_zip(TEMPLATE.read_bytes()) == TEMPLATE.read_bytes()  # committed idempotence
```
(The last line also turns `_author_template.py`'s "anyone can run" idempotence claim,
line 34, into an enforced one.)

### WR-03: `_EPOCH_NAIVE` is a hand-minted second epoch sentinel under a comment claiming it is imported

**File:** `tests/fixtures/weekly/_record_determinism_evidence.py:70-71`
**Issue:** The comment reads "EPOCH_ZERO, tz-stripped … **Imported rather than re-minted
below**" — and the very next line re-mints it: `_EPOCH_NAIVE = datetime(1970, 1, 1, 0, 0, 0)`.
`EPOCH_ZERO` is never imported in this file. `tests/test_pptx_determinism.py:117` states the
repo rule this breaks: "One epoch sentinel for the whole repo — never mint a second." The
value happens to be equal today, so behavior is correct — but the comment asserts the
opposite of the code, and a future change to the canonical sentinel would silently diverge
the evidence recorder from the durable test.
**Fix:**
```python
from newsletters.adapters._timestamps import EPOCH_ZERO
_EPOCH_NAIVE = EPOCH_ZERO.replace(tzinfo=None)  # dcterms reads back tz-naive
```

### WR-04: A mistyped flag silently overwrites the committed evidence artifact

**File:** `tests/fixtures/weekly/_record_determinism_evidence.py:258-262`
**Issue:** `main()` runs `check()` only when `"--check" in sys.argv[1:]`; **any other
argument** (`--chek`, `check`, `--verify`) falls through to `record()`, which overwrites
`.planning/notes/2026-08-29-pptx-determinism-evidence.json` without warning. For a script
whose entire stated purpose is defeating fabricated/repudiable evidence (T-01-03), "a typo
during verification destructively re-records the evidence being verified" is the wrong
failure mode.
**Fix:**
```python
def main() -> int:
    args = sys.argv[1:]
    if args == ["--check"]:
        return check()
    if args:
        print(f"unknown argument(s) {args!r}; usage: _record_determinism_evidence.py [--check]")
        return 2
    record()
    return 0
```

### WR-05: `_normalize_zip`'s docstring re-asserts the exact claim the module header marks as false

**File:** `tests/fixtures/pptx/_author_fixtures.py:135`
**Issue:** The module docstring (lines 15–19) says, in bold, that the claim "python-pptx …
writes a fixed zip-entry `date_time`" **"is false, and it is superseded here"** — measured
and committed as evidence on 2026-08-29. Yet the `_normalize_zip` function docstring at line
135 still opens with "python-pptx already writes a fixed zip date_time, but two paths still
drift cross-process". The same file now carries the falsehood and its correction, and the
function-level text is the one a maintainer editing `_normalize_zip` will read. It also
misstates *why* the normalizer exists for all nine fixtures (it is load-bearing for every
fixture's `date_time`, not just the SmartArt/chart paths).
**Fix:** rewrite the function docstring to match the corrected header, e.g.: "python-pptx
stamps `time.localtime()` into every entry (str arcname → stdlib `ZipInfo`; see module
header) — this rewrite to `_FIXED_ZIP_DATE_TIME` is what makes ALL fixtures byte-stable.
Additionally: (1) the SmartArt fixture rebuilds the archive after XML injection; (2) the
chart fixture embeds a nested `.xlsx` whose openpyxl core.xml carries a wall-clock — pinned
via `_normalize_embedded_xlsx`."

### WR-06: `AssetBlock.evidence` "≥1 by construction" contradicts the spec's own type-level-enforcement doctrine

**File:** `docs/weekly-spec.md:181` (AssetBlock definition)
**Issue:** The spec specifies `evidence: list[Trace] = Field(default_factory=list)` with the
comment "≥1 by construction". Two paragraphs later it argues (D-02) that the whole point of
`asset: AssetRecord` being required is that the invariant is "**unrepresentable** rather
than merely policed by a check somebody can forget to call." The evidence invariant gets
the opposite treatment: an `AssetBlock` with zero traces is fully representable by the
specified schema, and only a construction-site convention keeps it non-empty. An asset
block that lost its traces is exactly "an asset the record does not vouch for" reaching a
surface.
**Fix:** specify `evidence: list[Trace] = Field(min_length=1)` (Pydantic v2 enforces this at
validation), or state explicitly in the spec *why* this invariant is deliberately left to
construction while `asset` is not.

### WR-07: The "no discretion left to the implementer" routing table leaves two paths unrouted

**File:** `docs/weekly-spec.md:46, 38, 253-266`
**Issue:** The routing section claims completeness, but two authored-input failure modes
have no specified outcome, leaving Phase 3 exactly the discretion the spec says it removes:
1. **A dangling `photo:` key** — `team[].photo` "holds an asset **key**" (line 169), but
   nothing specifies what happens when the key names no `assets:` entry, or names an asset
   that was **not placed** (provenance incomplete, hash mismatch). Is that a teaching
   error (like an unknown top-level key), a `missing[]` disclosure, or a silently
   photo-less member? Each is defensible; the spec must pick one.
2. **An unresolvable recognition `source:`** — line 38 says `source:` is "a Source id /
   message id that evidences it", but only the *absent* case is routed (rule 6). A `source:`
   that resolves to no known `Source` is neither absent nor evidence; unspecified, an
   implementer could mint an empty `Trace`, drop the field silently, or fail loud.
**Fix:** add two rows to the routing table (recommended, consistent with the existing
grammar: dangling `photo:` key → member carried, photo not rendered, disclosed in
`missing[]` as `team member {name!r}: photo key {key!r} names no placed asset`; unresolvable
`source:` → recognition carried with `evidence=[]` exactly as if `source` were absent, plus
a disclosure naming the unresolvable id — never a fabricated trace).

## Info

### IN-01: `recorded` date is hardcoded, so any future re-record writes a stale date

**File:** `tests/fixtures/weekly/_record_determinism_evidence.py:179`
**Issue:** `"recorded": "2026-08-29"` is a literal. A re-record after a python-pptx upgrade
in 2027 would produce fresh measurements labeled as recorded in 2026 — misleading evidence
metadata. (If the literal is deliberate no-wall-clock policy, say so in `NOTES`; the
`recorded` field is *about* wall-clock time, so `date.today().isoformat()` is arguably the
honest value here — determinism of the evidence file across days is not a goal the way it
is for fixtures.)
**Fix:** either `datetime.now(timezone.utc).date().isoformat()` or a `NOTES["recorded"]`
entry explaining the pin.

### IN-02: `_author_fixtures` zip helpers leak handles and do not pin `create_system`

**File:** `tests/fixtures/pptx/_author_fixtures.py:141, 160`
**Issue:** `zin = zipfile.ZipFile(io.BytesIO(raw))` in `_normalize_zip` and
`_normalize_embedded_xlsx` is never closed (the canonical weekly module uses `with`), and
`create_system` is not pinned — regenerating the nine golden binaries on Windows
(`create_system=0` there vs 3 on unix) would change every committed byte. The file's own
docstring records the divergence and schedules delegation to the canonical normalizer in
Phase 2; noting here so the review record carries it too.
**Fix:** resolved by the scheduled Phase-2 delegation to `normalize_opc_zip`; until then,
wrap `zin` in `with`.

### IN-03: `sys.path.insert` of the fixture dir mutates process-global state for the whole pytest session

**File:** `tests/test_pptx_determinism.py:69` (also `_author_template.py:55`, `_record_determinism_evidence.py:47`)
**Issue:** Importing the test module prepends `tests/fixtures/weekly` to `sys.path` for the
entire pytest process, and the generic module name `_determinism` is now claimable by any
later fixture directory that grows a same-named module (silent shadowing depends on import
order). Fine in the standalone scripts; in the shared test process it is a latent collision.
**Fix:** when Phase 2 promotes the normalizer to `src/newsletters/_pptx_writer.py` this
disappears; until then, `importlib.util.spec_from_file_location("weekly_determinism", ...)`
avoids the path mutation.

### IN-04: A third fixed-instant convention (`_FIXED = 2026-01-01`) alongside `EPOCH_ZERO`

**File:** `tests/fixtures/weekly/_author_template.py:63`
**Issue:** The template author pins core properties to `datetime(2026, 1, 1)` (mirroring
`_author_fixtures.py`) while the renderer path pins `EPOCH_ZERO` and the repo rule says
"never mint a second" sentinel. Deterministic and harmless today (the renderer overwrites
`created`/`modified` anyway), but it is a second convention the scheduled Phase-2
normalizer consolidation should fold in — worth a line in that plan.
**Fix:** consolidate on `EPOCH_ZERO`-derived values when `_author_fixtures` delegates to the
canonical normalizer (already the scheduled moment for the `_FIXED_ZIP_DATE_TIME` → DOS
epoch swap and corpus regeneration).

---

## Verified claims (checked against the live repo, no finding)

- `_determinism.py` imports only `hashlib`, `io`, `zipfile` — genuinely stdlib-only, no
  `pptx` import; AI-optional hard rule holds.
- All 5 tests in `test_pptx_determinism.py` pass (3.13s, single module-scoped sleep).
- `--check` re-verifies the committed evidence: exit 0, negative control holds
  (`raw_bytes_equal: false`, `varying_zip_fields: ["date_time"]`, `varying_parts: []`).
- `normalize_opc_zip(committed template) == committed template` (idempotence on the
  committed artifact) holds; committed core properties are scrubbed
  (`author == last_modified_by == "newsletters fixture author"`).
- `Block` union has exactly 11 members (`semantic.py:449-464`); `_block_html` has 11
  `isinstance` branches ending in a bare `return ""` (`render.py:544-620`) — the
  "eleven to fifteen" and dispatch-contract claims in both docs are accurate.
- `GlossaryTerm.definition: Claim` exists (`semantic.py:433`); `casespec.py` exists with the
  exactly-N-key teaching error; `weeklyspec.py` correctly does not exist yet (spec phase).
- The example `sha256` in `docs/weekly-spec.md` is a valid 64-hex-char string.
- No fixture/org-specific names leak into `src/` — all reviewed code lives in `tests/`.
- The evidence JSON's keys match the recorder's output shape and every `NOTES` key maps to
  a real field.

---

_Reviewed: 2026-08-29T04:06:26Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
