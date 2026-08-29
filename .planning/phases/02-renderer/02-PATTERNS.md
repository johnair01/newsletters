# Phase 2: Renderer - Pattern Map

**Mapped:** 2026-08-29
**Files analyzed:** 9 (1 new src module, 1 new test module, 6 modified, 1 CI workflow)
**Analogs found:** 9 / 9 (all in-repo; no file lacks an analog)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/newsletters/pptx_writer.py` (NEW) | service / renderer behind an optional extra | file-I/O + transform | `src/newsletters/adapters/_pptx_loader.py` (lazy boundary + teaching error) · `tests/fixtures/weekly/_determinism.py` (the module being promoted, verbatim) · `src/newsletters/publish.py` (single `write_bytes`) | exact (composite) |
| `tests/test_pptx_writer.py` (NEW) | test (integration + guard) | request-response / read-back | `tests/test_pptx_determinism.py` (importorskip, 3s-gap module fixture, read-back assertions, teaching failure messages) | exact |
| `.github/workflows/ci.yml` (EDIT — new `pptx` job) | config / CI | batch | the `site-integrity` job (same shape: install extras, run a named test-file list) | exact |
| `tests/test_pptx_determinism.py` (EDIT) | test | — | itself; only the import block changes | exact |
| `tests/fixtures/weekly/_author_template.py` (EDIT) | fixture author script | file-I/O | itself + `tests/fixtures/pptx/_author_fixtures.py` (`_FIXED` convention) | exact |
| `tests/fixtures/weekly/_record_determinism_evidence.py` (EDIT) | evidence script | file-I/O | itself (same `sys.path.insert` deletion) | exact |
| `tests/fixtures/weekly/_determinism.py` (DELETE — promoted) | utility (stdlib) | transform | `src/newsletters/adapters/_timestamps.py` (leaf, stdlib-only, `__all__`, WHY-first docstring) | role-match |
| `tests/fixtures/pptx/_author_fixtures.py` (EDIT — IN-02 delegation) | fixture author script | file-I/O | its own `_normalize_zip` → delegates to promoted `normalize_opc_zip` | exact |
| `pyproject.toml` (EDIT — `python-pptx>=1.0.2`) | config | — | existing `[pptx]` extra line | exact |

---

## Pattern Assignments

### `src/newsletters/pptx_writer.py` (NEW — service, file-I/O + transform)

**Analog A — the lazy-extra boundary:** `src/newsletters/adapters/_pptx_loader.py`

*Module docstring shape* (lines 1–16) — WHY-first, names the invariant, ends by naming the guard
test that enforces it. Copy this shape verbatim in structure:

```python
"""Lazy python-pptx boundary — the optional ``[pptx]`` extra, imported only on use (ADAPT-04).

WHY THIS MODULE EXISTS ... the AI-optional / minimal-core invariant still demands that a bare
``pip install .`` (no ``[pptx]``) can ``import newsletters`` ...

This module itself must therefore have NO top-level ``import pptx`` / ``from pptx ...`` — the
bare-install gate (``tests/test_ai_optional.py``) asserts column-0 import count 0 for those edges.
"""
```

*The lazy import idiom, incl. the exact noqa/type-ignore comment* (lines 54–61):

```python
    try:
        # python-pptx ships no stubs; we deliberately do NOT add a types-* package ... PLC0415: lazy on
        # purpose (optional [pptx] extra, T-06-03).
        import pptx  # type: ignore[import-untyped]  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(MISSING_PPTX_MESSAGE) from exc
    return pptx
```

**Do NOT re-implement this.** Per RESEARCH Pattern 1, `pptx_writer.py` calls the existing boundary
from *inside* its render function:

```python
def render_surface_pptx_bytes(surface, *, template, slots) -> bytes:
    from .adapters._pptx_loader import _load_pptx   # noqa: PLC0415 — lazy on purpose ([pptx] extra)
    from .adapters._timestamps import EPOCH_ZERO    # noqa: PLC0415

    pptx = _load_pptx()
    prs = pptx.Presentation(str(template))
```

*Typing precedent* (line 28): `Presentation = Any  # ... kept ``Any`` to avoid a stub dependency`.
Do the same — no `types-*` package, `Any`-typed Presentation objects, real annotations everywhere else.

*`__all__` at the end* (line 87): `__all__ = ["_load_pptx", "load_presentation", "MISSING_PPTX_MESSAGE"]`.

**Analog B — the promoted normalizer:** `tests/fixtures/weekly/_determinism.py` (203 lines, whole file)

The promotion is a **verbatim move**, docstring included (it is the best explanation of the mechanism
in the repo, and RESEARCH §Security requires a reviewer to be able to diff it and see nothing was
"tidied"). Promote these five names to module level of `pptx_writer.py`, stdlib-only:

```python
__all__ = [
    "DOS_EPOCH",
    "normalize_opc_zip",
    "part_digest",
    "differing_parts",
    "differing_zipinfo_fields",
]

DOS_EPOCH = (1980, 1, 1, 0, 0, 0)
_COMPARED_FIELDS = ("date_time", "compress_type", "create_system", "external_attr", "CRC")
```

*The security-critical in-memory write loop* (lines 121–130) — preserve verbatim; the zip-slip
property is "closed by construction" only because no member name reaches the filesystem:

```python
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name in names:
            info = zipfile.ZipInfo(filename=name, date_time=DOS_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            # 0 = MS-DOS; the stdlib default is platform-dependent (3 on unix)
            info.create_system = 0
            info.external_attr = attrs[name]  # preserve python-pptx's value verbatim
            zout.writestr(info, data[name])
    return buf.getvalue()
```

*The fail-loud refusal house style* (lines 87–103) — teaching error: what happened, why it is
ambiguous, what the operator should do:

```python
        raise ValueError(
            f"duplicate member names in archive: {duplicated!r} — ZIP permits shadowed "
            "entries and ZipFile.read(name) silently picks the last one, so a by-name pass "
            "would rewrite part bytes and collide part_digest. Refusing to touch this "
            "archive; if it is an operator-supplied template, rebuild it without duplicate "
            "entries."
        )
```

Every new raise in the writer (duplicate shape name, unknown slot, unfilled `NL_` slot, non-text
slot, template-owns-watermark, empty-run slot) copies this three-part shape. RESEARCH Pattern 2 and
Pattern 3 already carry drafted texts in exactly this voice — use them.

**Analog C — the leaf-module precedent for placement:** `src/newsletters/adapters/_timestamps.py`

Stdlib-only, `from __future__ import annotations`, `__all__` immediately after imports, module
constant with a comment explaining why *this* value:

```python
from __future__ import annotations

from datetime import datetime, timezone

__all__ = ["EPOCH_ZERO", "deterministic_timestamp"]

# The deterministic "no intrinsic date" sentinel: tz-aware UTC 1970-01-01T00:00:00+00:00.
EPOCH_ZERO = datetime(1970, 1, 1, tzinfo=timezone.utc)
```

**Reuse `EPOCH_ZERO` — never mint a second sentinel.** At the OPC boundary strip the tz:
`cp.created = EPOCH_ZERO.replace(tzinfo=None)` (RESEARCH Pitfall 8).

**Analog D — the single disk write:** `src/newsletters/publish.py:80,87`

```python
            target.write_bytes(f.read_bytes())
    nojekyll.write_bytes(b"")
```

One `Path.write_bytes` of complete, already-normalized bytes. Never `prs.save(path)` then rewrite.

**Not re-exported from `__init__.py`** — follow the `adapters` precedent (RESEARCH §Project Structure).

---

### `tests/test_pptx_writer.py` (NEW — test, integration + guard)

**Analog:** `tests/test_pptx_determinism.py`

*The optional-extra guard — `importorskip` at module scope, NOT `pytestmark`* (lines 59–65). The
comment explaining why is load-bearing; copy it:

```python
# `importorskip` raises Skipped at module level, which pytest converts into a module skip — so a
# bare install (no [pptx] extra) SKIPS this file instead of erroring at collection. Same pattern
# as tests/test_pptx_loader.py.
pptx = pytest.importorskip(
    "pptx", reason="optional [pptx] extra (python-pptx) not installed"
)
Presentation = pptx.Presentation

from newsletters.adapters._timestamps import EPOCH_ZERO  # noqa: E402
```

Alternative guard, for a module whose src imports are all bare-safe — `tests/test_pptx_golden.py:50`:

```python
pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("pptx") is None,
    reason="optional [pptx] extra (python-pptx) not installed",
)
```

Use `importorskip` for `test_pptx_writer.py` (it binds `Presentation` at module scope for the
read-back assertions).

*The 3-second module-scoped fixture* (lines 128–139) — the sleep is load-bearing and happens once:

```python
@pytest.fixture(scope="module")
def time_separated_writes() -> tuple[bytes, bytes]:
    """Two REAL writes of identical content, separated by a real 3-second gap.

    Module-scoped so the suite sleeps once, not once per assertion.
    """
    raw_a = _render_bytes("2026-W35")
    # DOS timestamps have 2-SECOND granularity, so 3 seconds guarantees the boundary is crossed.
    # A shorter gap is the false-green trap: two same-second writes are already byte-identical.
    time.sleep(3)
    raw_b = _render_bytes("2026-W35")
    return raw_a, raw_b
```

*The read-back assertion block* (lines 232–242) — reopen the WRITTEN bytes/file, never trust the
writer's return value:

```python
    written = Presentation(io.BytesIO(normalized))  # reopen the WRITTEN bytes
    cp = written.core_properties
    assert cp.category == MARKER, cp.category
    assert cp.content_status == GATE_STATE, cp.content_status
    # dcterms:created serializes as W3CDTF and reads back tz-NAIVE (01-RESEARCH §Pitfall 5).
    assert cp.created == EPOCH_ZERO.replace(tzinfo=None), cp.created
    assert cp.modified == EPOCH_ZERO.replace(tzinfo=None), cp.modified

    read_back = sorted(shape.name for shape in written.slides[0].shapes)
    lost = f"named shapes did not survive the write/normalize round trip: {read_back}"
    assert read_back == ALL_SHAPE_NAMES, lost
```

*Failure-message style* — every assert carries a message that explains what the red means, not what
the values were (lines 153–159 is the canonical example):

```python
    assert raw_a != raw_b, (
        "the negative control has stopped controlling: two un-normalized writes "
        "3s apart are byte-equal. ... Until this inequality "
        "holds, the byte-equality result in test_normalized_double_write_is_byte_identical "
        "is NOT attributable to the normalizer and proves nothing."
    )
```

*The `pytest.raises` + regex idiom for fail-loud tests* (lines 283–290):

```python
    with pytest.raises(ValueError, match="duplicate member names.*evil.xml"):
        normalize_opc_zip(shadowed)
```

Use this shape for `test_unknown_slot_name_raises`, `test_unfilled_reserved_slot_raises`,
`test_duplicate_shape_name_raises`, `test_slot_without_text_frame_raises`,
`test_template_owning_watermark_name_raises`.

*The corpus guard* (lines 245–254) — copy if the weekly fixture set grows:

```python
def test_weekly_fixture_corpus_is_exactly_the_committed_template() -> None:
    on_disk = sorted(p.name for p in FIXTURE_DIR.glob("*.pptx"))
    assert on_disk == ["template.pptx"], on_disk
    assert TEMPLATE.is_file()
```

**Guard-test analogs from `tests/test_ai_optional.py`** — copy both, retargeted at `pptx_writer.py`:

*No column-0 pptx import* (`tests/test_ai_optional.py:459–479`):

```python
def test_pptx_loader_has_no_toplevel_pptx_import() -> None:
    source = PPTX_LOADER_PATH.read_text()
    toplevel_edges = [
        line
        for line in source.splitlines()
        # column-0 (module-top) import statements only — indented ones live inside functions or
        # the TYPE_CHECKING guard and are not executed on a bare runtime import.
        if line.startswith("import pptx") or line.startswith("from pptx")
    ]
    assert not toplevel_edges, (
        f"_pptx_loader.py has top-level pptx import(s) — breaks the bare install: "
        f"{toplevel_edges}"
    )
```

*Bare-install importability via a meta-path blocker in a subprocess*
(`tests/test_ai_optional.py:482–517`) — retarget the last import lines to
`from newsletters import pptx_writer`:

```python
    code = (
        "import sys\n"
        "from importlib.abc import MetaPathFinder\n"
        "class _Block(MetaPathFinder):\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'pptx' or name.startswith('pptx.'):\n"
        "            raise ImportError('blocked pptx (simulated bare install)')\n"
        "        return None\n"
        "sys.modules.pop('pptx', None)\n"
        "sys.meta_path.insert(0, _Block())\n"
        "import newsletters\n"
        "from newsletters import pptx_writer\n"
        "assert 'pptx' not in sys.modules, sys.modules.get('pptx')\n"
    )
    env = {**os.environ, "PYDANTIC_DISABLE_PLUGINS": "true"}
    proc = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=REPO_ROOT
    )
    assert proc.returncode == 0, f"...:\n{proc.stdout}{proc.stderr}"
```

**Draft-stays-Draft test analog:** `tests/test_semantic.py:59–83` — the gate-proof idiom is a plain
state assertion plus `pytest.raises` on the illegal transition; no fixtures, no mocks:

```python
def test_published_without_approval_is_rejected():
    with pytest.raises(ValueError):
        Review(state=ReviewState.PUBLISHED, policy=ARTICLE.review_policy, author="Claude")
```

For SC-4 write it as the *before/after* form RESEARCH specifies (the analog has no equivalent, so
this is the new shape): capture `before = surface.model_dump()`, render, then assert
`surface.review.state is ReviewState.DRAFT` and `surface.model_dump() == before`.

---

### `.github/workflows/ci.yml` (EDIT — add a `pptx` job)

**Analog:** the `site-integrity` job (lines 113–135) — the exact idiom to copy. Note the four-part
job shape: a WHY comment block above `name:`, checkout, setup-python 3.12, an install step, then one
run step with a named test-file list.

```yaml
  site-integrity:
    # PUB-01..05 (v1.2): the published-tree guarantees run on EVERY push/PR — ...
    # One definition of "publishable"; no bash re-implementation anywhere.
    name: site integrity (PUB-01..05)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install with test + config extras (PyYAML for the module corpus; non-AI)
        run: |
          python -m pip install --upgrade pip
          pip install ".[test,config]"

      - name: Run the published-tree guarantees + the site/render guards
        run: |
          python -m pytest tests/test_publish.py tests/test_render.py tests/test_site.py \
                           tests/test_worksurface.py tests/test_modulesite.py -q
```

New job, same idiom (`pip install ".[test,pptx]"`, named pptx test files, `-q`). **The comment must
name W21** — that no job installed `[pptx]`, so every pptx test was silently `s`-skipped.

**The bare-install job stays untouched.** Its own comment states the rule (lines 30–32):
`# `[test]` adds ONLY pytest ... Do NOT add [ai]/[dev]/[panel].` The `merge-block` job's comment
(lines 99–101) is the precedent for *why* a non-AI extra goes in a separate job rather than into
`bare-install`: "the bare-install job above remains the canonical AI-free source of truth (PKG-03)
and does NOT get this." Copy that reasoning for `[pptx]`.

---

### `tests/test_pptx_determinism.py` (EDIT — retarget the import)

Delete lines 69–79's `sys.path.insert` mechanism (closes IN-03):

```python
sys.path.insert(0, str(FIXTURE_DIR))

from _determinism import (  # noqa: E402
    differing_parts, differing_zipinfo_fields, normalize_opc_zip, part_digest,
)
```

becomes a plain package import beside the existing one at line 67
(`from newsletters.adapters._timestamps import EPOCH_ZERO  # noqa: E402`):

```python
from newsletters.pptx_writer import (  # noqa: E402
    differing_parts, differing_zipinfo_fields, normalize_opc_zip, part_digest,
)
```

Drop the now-unused `import sys`. **Keep the negative control test** (assertion C) — RESEARCH names
it the assertion most likely to be dropped as redundant once the writer exists.

### `tests/fixtures/weekly/_author_template.py` and `_record_determinism_evidence.py` (EDIT)

Same edit, same two lines each (`_author_template.py:55,57`;
`_record_determinism_evidence.py:49,51`). Keep `_FIXED = datetime(2026, 1, 1, 0, 0, 0)`
(`_author_template.py:63`) **deliberately different from `EPOCH_ZERO`** and add a comment naming it
a *falsifiability control* — RESEARCH Open Question 3 / assumption B3.

### `tests/fixtures/pptx/_author_fixtures.py` (EDIT — IN-02 second half, own commit, last)

`_normalize_zip` (lines 132–176) delegates to the promoted `normalize_opc_zip`; the module docstring
at lines 32–38 already predicts this edit ("delegates to it **then, not now**") — update that
paragraph in the same change. Regenerates nine binaries, zero assertion changes (W23).

---

## Shared Patterns

### Lazy optional-extra import
**Source:** `src/newsletters/adapters/_pptx_loader.py:40-61`
**Apply to:** `pptx_writer.py` — by *calling* `_load_pptx()`, not by re-implementing it.
The teaching message constant `MISSING_PPTX_MESSAGE` (lines 32–37) is exposed "so tests can assert
against it without string-duplication drift" — the same anti-drift argument the writer inherits.

### Fail-loud teaching errors
**Source:** `tests/fixtures/weekly/_determinism.py:96-103`
**Apply to:** every raise in `pptx_writer.py`. Three parts: what was found (with `!r` values), why it
cannot be resolved silently, what the operator does next. "Refusing to guess" is the house phrase.

### WHY-first module docstrings
**Source:** `_timestamps.py:1-33`, `_pptx_loader.py:1-16`, `_determinism.py:1-56`
**Apply to:** `pptx_writer.py`, `tests/test_pptx_writer.py`. Structure: WHY THIS EXISTS → THE FIX →
SCOPE OF THE CLAIM → SECURITY PROPERTY → the guard that enforces it. Not optional in this repo.

### Read the gate, never write it
**Source:** `tests/test_pptx_determinism.py:114-121` (writes `cp.content_status` from a constant),
`src/newsletters/semantic.py` (untouched, byte-for-byte)
**Apply to:** the writer's core-properties block. `not surface.is_published` is a *read* of a
computed property; there is no assignment to any `Surface` field anywhere in the writer.

### Generated-by marker
**Source:** `src/newsletters/render.py:738` — `f"<!-- generated by newsletters.render; do not hand-edit -->"`;
asserted by `tests/test_publish.py:217 test_every_assembled_page_carries_generated_marker` against
the constant `_MARKER` at `tests/test_publish.py:22`.
**Apply to:** the deck's `cp:category = "generated-by:newsletters"` — same intent, different carrier
(OPC core properties). Follow the precedent of a single module constant asserted by a named test.

### Stdlib-only leaf module with `__all__`
**Source:** `src/newsletters/adapters/_timestamps.py:35-42`
**Apply to:** the promoted normalizer half of `pptx_writer.py` — it must stay bare-importable, which
is what lets the duplicate-member and idempotence tests run on the bare-install job for the first time.

## No Analog Found

| File / behaviour | Role | Data Flow | Reason |
|------|------|-----------|--------|
| The reuse-and-clone paragraph fill primitive (`copy.deepcopy(p0._p)`) | writer internal | transform | No existing repo code *writes* pptx text; the loader only reads. Use RESEARCH §Pattern 3 verbatim — it is measured code, not sketch. |
| The group-recursive `_walk` binding map | writer internal | transform | The Phase 1 spike's `{shape.name: shape for shape in slide.shapes}` (`test_pptx_determinism.py:110`) is an **anti-pattern here** (W17: blind to group nesting). Use RESEARCH §Pattern 2. |
| The watermark add | writer internal | transform | No precedent. RESEARCH §Pattern 4 carries measured code. |
| Sample `Surface(REPORT)` fixture for the CI render | test fixture | — | `tests/test_semantic.py`'s `_report()` helper is the nearest constructor idiom; check whether it is importable/reusable before authoring a new one. |

## Metadata

**Analog search scope:** `src/newsletters/` (incl. `adapters/`), `tests/`, `tests/fixtures/{weekly,pptx}/`, `.github/workflows/`
**Files scanned:** 12 read; 5 grepped
**Pattern extraction date:** 2026-08-29
