# Phase 4: Sample corpus + recipe - Pattern Map

**Mapped:** 2026-08-29
**Files analyzed:** 14 new/modified (5 new source/test/doc files, 9 wiring edits)
**Analogs found:** 14 / 14 (every file has an in-repo analog — this phase invents no new shape)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/newsletters/weeklysite.py` (new) | builder | batch / file-I/O | `src/newsletters/modulesite.py` | **exact** (module builder mirrors `worksurface`; weekly mirrors module) |
| `content/weekly/*.yml` + `inbox/*.eml` + `assets/` (new) | corpus data | file-I/O | `tests/fixtures/weekly/weekly-full.yml` + `content/module/module-a.yml` | exact |
| `content/weekly/ids.json` (new) | ledger/state | append-only store | `content/module/ids.json` | exact |
| `content/weekly/deck/*.pptx` + `.digest` (new) | committed binary artifact | file-I/O | `tests/fixtures/weekly/template.pptx` + `pptx_writer.part_digest` | role-match (first committed *rendered* deck) |
| `src/newsletters/publish.py` (mod) | config/registry | batch copy | its own `_CORPUS_LAYOUT` tuple | exact (append a row) |
| `src/newsletters/cli.py` (mod) | CLI | request-response | its own `module` branches | exact |
| `src/newsletters/cli.py` — new `weekly` command | CLI | file-I/O | `cli.assemble` / `cli.build` (lazy import + echo idiom) | exact |
| `dogfood.py` / `worksurface.py` / `modulesite.py` Records strips (mod) | builder constant | — | `_REV1_RECORDS`, the two inline `records=` tuples | exact |
| 4 regenerated chrome HTML pages | generated content | — | committed==fresh discipline | exact |
| `tests/test_weeklysite.py` (new) | test | — | `tests/test_modulesite.py` | **exact** |
| `tests/test_weekly_golden.py` (new) | test (`[pptx]`) | — | `tests/test_weeklyspec.py` `requires_pptx` idiom + `test_pptx_golden.py` | exact |
| `tests/test_publish.py` (mod) | test | — | its own 4 loops | exact |
| `tests/test_render.py` (mod) | test | — | its records-strip shape test | exact |
| `docs/weekly.md` (new) | doc | — | `docs/architecture.md` §WORK-01 flow + `docs/case-spec.md` | exact |
| `.github/workflows/{ci,deploy-pages}.yml` (mod) | CI config | — | the existing `--corpus` gate lines | exact |

---

## Pattern Assignments

### 1. `src/newsletters/weeklysite.py` (builder, batch/file-I/O)

**Analog:** `src/newsletters/modulesite.py` — copy the *whole shape*.

**Module docstring contract** (`modulesite.py:1-38`) — mirror all four properties verbatim in
structure (READ-ONLY/NO NETWORK · CONTENT-ADDRESSED/FAITHFUL · DETERMINISTIC/BYTE-STABLE ·
AI-FREE/MINIMAL-CORE), plus the "WHY a new top-level module" paragraph (`compose.py` is a COMP
leaf that must not import `render`/`site`, so the build-and-render seam is a sibling builder).

**Imports pattern** (`modulesite.py:40-52`) — in-package only, no `yaml`/`pptx` at module level:
```python
from __future__ import annotations

from pathlib import Path

from . import worksurface
from ._yaml_loader import load_config as _parse_config
from .compose import compose_module_report
from .render import render_library, render_surface
from .semantic import Claim, Surface
from .site import Ledger, Site
from .swimlane import SwimlaneLoad, load_swimlanes

__all__ = ["build_module_surfaces", "build_module_site"]
```
Weekly equivalent adds `from .weeklyspec import build_weekly_report, load_weekly_spec, weekly_slots`
and keeps `pptx_writer` **out** of module scope (lazy-import inside `build_weekly_deck` only).

**Fixed corpus constants** (`modulesite.py:54-59`) — generic paths, never a fixture filename:
```python
_CORPUS_DIR = "content/module"
_LEDGER_PATH = "content/module/ids.json"
_SITE_DIR = "content/module/site"
```

**Structural discovery, never a filename in `src/`** (`modulesite.py:67-82`):
```python
def _discover_config(root: Path | None) -> Path:
    corpus = (Path(root) if root is not None else Path.cwd()) / _CORPUS_DIR
    candidates = sorted(corpus.resolve().glob("*.yml"))
    if not candidates:
        raise FileNotFoundError(
            f"no module-config '*.yml' found under {corpus} — the corpus is not populated"
        )
    return candidates[0]
```
Weekly needs **two** of these: `_discover_spec()` over `content/weekly/*.yml` and
`_discover_lanes()` over `content/module/*.yml` (the lineage link — same sorted-glob rule).

**Compose entry point signature** (`modulesite.py:112-136`) — the exact shape `cli check` calls:
```python
def build_module_surfaces(
    config_path: str | Path | None = None, *, root: Path | None = None
) -> list[Surface]:
    config = Path(config_path) if config_path is not None else _discover_config(root)
    load = load_swimlanes(config, root=root)
    quote, owner = _select_owner_quote(load)
    surface = compose_module_report(load, quote=quote, owner=owner)
    return [surface]
```
Weekly: `build_weekly_surfaces(spec_path=None, *, root=None) -> list[Surface]` →
`EmailAdapter().parse(...)` → `load_weekly_spec(spec, root=root, known_sources=[src])` →
`load_swimlanes(module_config, root=root)` → `build_weekly_report(load, author=..., bindings=swim.bindings)`.
Note the composer never touches the ledger — same as here.

**Site entry point + the committed==fresh discipline** (`modulesite.py:139-216`) — the
load → Site → **`ledger.save()` at the FIXED committed path** → per-page render → library →
fonts sequence, in this order:
```python
def build_module_site(
    out_dir: str | Path = _SITE_DIR,
    *,
    root: Path | None = None,
    config_path: str | Path | None = None,
) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    surfaces = build_module_surfaces(config_path, root=root)

    # The module corpus has its OWN ledger (R-001 starts fresh) — the corpus boundary is preserved
    # at the ledger layer. Load → build the Site → persist any newly-assigned refs (SOLE writer).
    ledger = Ledger.load(_LEDGER_PATH)
    site = Site.from_surfaces(surfaces, ledger=ledger)
    ledger.save()

    written: list[Path] = []
    for page in site.pages():
        p = out / page.href
        p.write_text(
            render_surface(page.surface, site=site, page=page, home_href="../index.html"),
            encoding="utf-8",
        )
        written.append(p)

    library = out / "library.html"
    library.write_text(
        render_library(
            site,
            records=(
                ("The Rev1 record", "../index.html"),
                ("The work record", "../work/library.html"),
            ),
            home_href="../index.html",
        ),
        encoding="utf-8",
    )
    written.append(library)

    worksurface._emit_fonts(out)   # zero-edit reuse; zero external call

    return written
```
Load-bearing details to carry: `_LEDGER_PATH` is the **committed** path, *not* `out_dir` (this is
what makes `test_committed_equals_fresh_build`'s ledger-snapshot assertion necessary);
`home_href="../index.html"` because a subdir corpus has no index of its own; `_emit_fonts` is
reused, never re-vendored; return order is pages-then-library.

**Deck entry point (no analog for the *seam*, exact analog for the *calls*)** — a third,
separate function so `[pptx]` never enters `build_weekly_site`:
```python
def build_weekly_deck(out_path, *, root=None, spec_path=None, template=None) -> Path:
    from .pptx_writer import render_surface_pptx, part_digest   # lazy — bare install stays light
```
`render_surface_pptx(surface, *, template, slots, out_path)` — `out_path` is **caller-supplied and
never derived from Surface content** (T-02-08, stated in its docstring `pptx_writer.py:688-693`).

---

### 2. Corpus wiring (config/registry edits)

**`publish.py:30-39`** — append one row; the comment above it names the Records-strip contract:
```python
_CORPUS_LAYOUT: tuple[tuple[str, str], ...] = (
    ("content/rev1/site", "."),
    ("content/work/site", "work"),
    ("content/module/site", "module"),
)
```
`assemble_site` raises `FileNotFoundError` **before any write** if the dir is absent
(`publish.py:56-61`) — so the layout edit and the committed `content/weekly/site/` must land in the
same commit.

**`cli.py:16-42`** — enum member + docstring bullet + default-out entry:
```python
class CorpusName(str, Enum):
    rev1 = "rev1"
    work = "work"
    module = "module"

_DEFAULT_OUT: dict[CorpusName, str] = {
    CorpusName.rev1: "content/rev1/site",
    CorpusName.work: "content/work/site",
    CorpusName.module: "content/module/site",
}
```

**`cli.py:81-95` (build) and `cli.py:167-178` (check)** — the branch idiom, lazy import inside:
```python
    elif corpus is CorpusName.module:
        from .modulesite import build_module_site
        written = build_module_site(target)
        index_name = "library.html"
```
```python
    elif corpus is CorpusName.module:
        from . import modulesite
        surfaces = modulesite.build_module_surfaces()
```
Note `check` imports the **module object** (not the function) — that is what makes the
`monkeypatch.setattr(modulesite, "build_module_surfaces", ...)` blocking proof work. Keep it.

**New `newsletters weekly` command** — copy `cli.assemble` (`cli.py:103-131`): flat `@app.command()`,
`typer.Option` with help text, lazy import in the body, echo each written path then a summary line:
```python
    from .publish import assemble_site

    written = assemble_site(out, base_path=base_path)
    for p in written:
        typer.echo(f"  {p}")
    typer.echo(f"\nassembled {len(written)} files -> {out}")
```

**The four `tests/test_publish.py` loops that must see the new corpus:**

1. *assemble assertions* (`:37-49`) — add `(out / "weekly" / "library.html").is_file()` and the
   weekly report page; the function name `test_assemble_composes_three_corpora_and_chrome` goes
   stale and should be renamed in the same edit.
2. *link resolution* (`:104-133`) — no edit needed structurally, but it is the **resolver of record**
   for the new strip hrefs; the floor `assert checked > 100` rises for free. It also enforces
   `'href="None"' not in text`.
3. *committed==fresh* (`:141-193`) — `_assert_committed_equals_fresh(corpus_dir, fresh_dir, ledger,
   html_only=False)` walks `rglob("*")` and compares `read_bytes()`. **This is the trap**: the deck
   must stay out of `content/weekly/site/` or this loop compares raw zip bytes cross-zlib. The
   weekly's own committed==fresh lives in `tests/test_weeklysite.py` (module precedent, see the
   comment at `test_publish.py:137-139`).
4. *fonts tuple* (`:207`) — the literal edit site:
```python
    for fonts_dir in (out / "fonts", out / "work/fonts", out / "module/fonts"):
        ofls = list(fonts_dir.glob("OFL-*.txt"))
        assert len(ofls) == 3, f"{fonts_dir} must carry the three OFL license files, has {ofls}"
```
5. *marker* (`:217-226`) — `_MARKER = "generated by newsletters.render; do not hand-edit"` is asserted
   on **every** assembled `*.html`; the weekly pages get it free from `render_surface`/`render_library`.

**Records strip data flow** — the builder owns its corpus's position, `render.py` stays corpus-blind
(01-CONTEXT d3). Three edit sites, three shapes:
- `dogfood.py:807-810` — root corpus, no `../`:
```python
_REV1_RECORDS = (
    ("The work record", "work/library.html"),
    ("The module record", "module/library.html"),
)
```
- `worksurface.py:438-444` and `modulesite.py:203-207` — inline `records=` tuples inside the
  `render_library(...)` call, assembled-tree-relative (`"../module/library.html"`).
- `weeklysite.py` declares its three neighbours the same way.

**Strip shape test** (`tests/test_render.py:847-858`) — the third assertion goes here:
```python
        if page.name in chrome:
            assert 'class="nl-records"' in text, f"{page.name} is chrome but has no strip"
            assert 'href="work/library.html"' in text, f"{page.name} strip misses work"
            assert 'href="module/library.html"' in text, f"{page.name} strip misses module"
```

**Deploy gate** (`deploy-pages.yml:68-75`) — gate 1 gains one line; gate 2 is untouched:
```yaml
      - name: "Gate 1 — merge-block every corpus (no unsafe surface publishes)"
        run: |
          newsletters check --corpus rev1
          newsletters check --corpus work
          newsletters check --corpus module

      - name: "Gate 2 — the published-tree guarantees (links/drift/fonts/marker)"
        run: python -m pytest tests/test_publish.py -q
```
`ci.yml:120-122` carries the identical three lines (merge-block job); `ci.yml:145` lists the
site-integrity test modules; `ci.yml:220-226` is the weekly job's module list + the
`grep -Eq '[0-9]+ skipped'` fail-on-skip guard.

---

### 3. `tests/test_weeklysite.py` (test)

**Analog:** `tests/test_modulesite.py` — mirror module-for-module, including the docstring that
states the SHARED-LEDGER-PATH caveat (`test_modulesite.py:25-29`).

**Anchor + derived page name** (`:43-65`) — never hardcode the page filename:
```python
REPO_ROOT = Path(__file__).resolve().parent.parent

def _report_page_name() -> str:
    return f"{build_module_surfaces()[0].id}.html"
```

**Honesty panel visible in the HTML** (`:102-126`) — locate the disclosure by the composer's
*phrasing* in `surface.missing`, then assert `html.escape(entry) in page`. This is the exact idiom
for the three planted absences:
```python
    surface = build_module_surfaces()[0]
    disclosures = [m for m in surface.missing if _SINGLE_ENDPOINT_PHRASE in m]
    assert disclosures, "fixture invariant: ..."
    page = _build_and_read_report(tmp_path)
    assert 'class="honesty"' in page
    assert 'class="claim-span"' in page
    for entry in disclosures:
        assert html.escape(entry) in page
```

**Committed==fresh with the ledger snapshot** (`:248-278`) — the exact idiom Pitfall 6 requires:
```python
    ledger_before = committed_ledger.read_bytes()
    build_module_site(tmp_path)
    assert committed_ledger.read_bytes() == ledger_before, \
        "the fresh build mutated the committed ledger — the rebuild must be idempotent (R-001 held)"

    committed_files = sorted(p for p in committed_site.rglob("*") if p.is_file())
    assert committed_files, "no committed module site files to compare against"
    for src in committed_files:
        rel = src.relative_to(committed_site)
        built = tmp_path / rel
        assert built.exists(), f"fresh build is missing committed file {rel}"
        assert built.read_bytes() == src.read_bytes(), f"{rel} differs ..."
```

**R-001 stability, proven by rebuild on a fresh tmp ledger** (`:223-245`) — never assert a literal
twice; `Ledger.load(tmp) → Site.from_surfaces → save → reload → rebuild → same ref`.

**Byte-stable double render** (`:202-220`) — two builds into `a`/`b`, compare file sets then bytes.

**No external calls** (`:148-193`) — the `forbidden` tuple + `css_url_fetch` / `link_href_http`
regexes + the `fonts/*.woff2` presence check. Copy verbatim.

**`_EMAIL_RE` — the exact pattern the `.eml` fixture must design around** (`:310-337`):
```python
_REAL_LOOKING_LITERALS = frozenset({
    "Jean-Luc Picard", "William Riker", "Geordi La Forge", "Beverly Crusher",
    "Starfleet Division", "USS Enterprise", "Warp Core Stability",
    "Dilithium Efficiency Index", "starfleet.int",
})

_EMAIL_RE = re.compile(r"\b[\w.-]+@[\w.-]+\.[A-Za-z]{2,}\b")

_FABRICATED_MARKERS = ("module-a", "area-bem", "owner-", "eng-", "toolset-")

def _scan_real_looking(text: str) -> set[str]:
    hits = {tok for tok in _REAL_LOOKING_LITERALS if tok in text}
    hits.update(_EMAIL_RE.findall(text))
    return hits
```
Any `From:` / `To:` / `Message-ID:` address in the `.eml` matches this. Use RFC 6761
`@example.invalid` and add an explicit, docstring-explained allowance (e.g. subtract
`{h for h in hits if h.endswith("@example.invalid")}`) — or scan `inbox/*.eml` against the *name*
denylist only.

**Planted-leak self-check** (`:375-379`) — keeps the clean pass non-vacuous; carry it:
```python
    planted = "owner: Jean-Luc Picard\ncontact: ops@starfleet.int\n"
    planted_hits = _scan_real_looking(planted)
    assert "Jean-Luc Picard" in planted_hits, planted_hits
    assert any("@" in h for h in planted_hits), planted_hits
```

**CLI gate proof** (`tests/test_module_cli.py:62-95`) — clean-exits-zero is Draft-vacuous *by
design and says so in its docstring*; the blocking direction is what proves the gate:
```python
    monkeypatch.setattr(
        modulesite, "build_module_surfaces", lambda *a, **k: [_blocked_published_module_surface()]
    )
    blocked = runner.invoke(app, ["check", "--corpus", "module"])
    assert blocked.exit_code != 0, blocked.output
    assert "sfc-module-blocked" in blocked.output
    assert "BLOCK" in blocked.output
    assert "merge blocked" in blocked.output
```

---

### 4. `tests/test_weekly_golden.py` — the committed deck + digest sidecar (`[pptx]`-gated test)

**Analog A — the skip guard** (`tests/test_weeklyspec.py:1445-1458`). Use `requires_pptx`, **not** a
module-level `importorskip`:
```python
try:  # noqa: SIM105 — the guard needs the bound name, not just the suppression
    import pptx as _pptx
except ImportError:  # pragma: no cover
    _pptx = None

requires_pptx = pytest.mark.skipif(
    _pptx is None, reason="optional [pptx] extra (python-pptx) not installed"
)
```
This module goes in the **`weekly` CI job** (`ci.yml:220-226`, which fails on `[0-9]+ skipped`) —
never in `site-integrity`, which installs only `[test,config]` and has no skip assertion (W21).

**Analog B — the digest primitive** (`src/newsletters/pptx_writer.py:236-265`). `part_digest(raw)`
is stdlib-only (`zipfile` + `hashlib`), sorted `(name, sha256(part))` rows, **length-prefixed**
(WR-01 — do not "simplify" to delimiters), and raises `ValueError` on duplicate member names.

**The two tiers** (never `read_bytes() == read_bytes()` on a zip):
```python
# tier 1 — stdlib only; lives in tests/test_weeklysite.py, runs on every install
assert part_digest(DECK.read_bytes()) == DIGEST.read_text(encoding="utf-8").strip()

# tier 2 — [pptx]-gated; lives in tests/test_weekly_golden.py, weekly job only
fresh = render_surface_pptx_bytes(surface, template=TEMPLATE, slots=slots)
assert part_digest(fresh) == part_digest(DECK.read_bytes())
```
`render_surface_pptx_bytes(surface, *, template, slots) -> bytes` (`pptx_writer.py:616-621`);
`render_surface_pptx(surface, *, template, slots, out_path) -> Path` (`:681-687`) writes once,
already normalized.

**Template handling** (`tests/fixtures/weekly/template.pptx`, P-06: copied, never regenerated) —
`content/weekly/template.pptx` is a byte-copy, guarded by a one-line equality test so neither can
drift. Never compare the committed deck to the template (python-pptx's load path re-serializes);
the golden deck comes from the **writer**.

---

### 5. `docs/weekly.md` (doc)

**Analog A — the operator-recipe shape:** `docs/architecture.md:218-252` (the WORK-01 flow).
Numbered steps, each naming the exact function/command, each stating the trust property it
preserves. The load-bearing language to carry into `docs/weekly.md` and into `weeklysite.py`'s
docstrings:

> 2. **Point the read-only ingest at the code.** `worksurface.capture_files(paths, root=...)`
>    reads a *curated list* of local files **READ-ONLY** (`Path.read_text` only — never a write
>    to the scanned tree, **no network call**) into content-addressed `Source` records. […]
>    Data stays local; nothing is transmitted […]
> 5. **Gate it through the SAME trust gate.** `newsletters check --corpus work` runs the
>    corpus-agnostic `review.review_blockers` […] The selector routes the *builder*, never forks
>    the gate […]

Also mirror the closing `**The --corpus {rev1|work} selector.**` subsection — **and fix it**, it is
stale at two corpora and §9 says "three".

**Analog B — the authoring-doc shape:** `docs/case-spec.md` — three headings
(`# <title>` → `## Writing one` → `## What happens to it`), an opening paragraph naming the trust
spine (`Source → Claim(+Trace) → Distillation → Surface` → Draft Report → the review gate), one
fenced YAML skeleton with inline `<placeholder>` comments, then a bulleted "Rules the loader
enforces (teaching errors, never silent drops)" block ending on the honesty rule:

> - Every field is optional. An absent or empty field is **disclosed** in
>   `Distillation.missing[]` (and the surface's honesty panel) — never fabricated.

`docs/case-spec.md:8-9` also shows the **link-don't-duplicate** idiom — `docs/weekly.md` must link
`docs/weekly-spec.md` (the authoring contract), never restate its schema.

**CLI command-example idiom** — fenced block, one command per line, long invocations backslash-wrapped
(the `newsletters weekly --spec … \` shape in 04-RESEARCH.md:694-699), matching the shipped Typer
options exactly (the doc-contract test asserts this).

---

### 6. Synthetic weekly fixture family (corpus data)

**Analog A — the spec file:** `tests/fixtures/weekly/weekly-full.yml`. Copy its **header comment
policy** and its key order (all eight keys, `week` / `module` / `highlights` / `lowlights` /
`recognitions` / `team` / `assets` / `config`):
```yaml
# SYNTHETIC TEST DATA — fabricated, Star-Trek-flavored content only (no real org/tool/
# metric/site/program names). […]
week: "2374-W35"
module: "Shuttlebay Operations"
highlights:
  - "Cut the bay turnaround checklist from nine manual steps to two."
  - |
    A second duty officer joined the rota this week, so no single
    approval point is left anywhere in the launch sequence.
recognitions:
  - person: "Miles O'Brien"
    reason: "Found the launch-ordering fault the drills were blind to."
    source: "mail:23740824-rota"        # ← resolves via known_sources=[eml_source]
  - person: "Kira Nerys"
    reason: "Rewrote the turnaround note so the next shift could read it cold."
                                        # ← NO source: → honesty row 2
assets:
  bay-cycle-throughput:
    file: "…/assets/bay-cycle-throughput.png"
    sha256: "84549424…"
    folder: "Weekly review pack"
    date: "2374-08-24"
    event: "Friday bay review"
    caption: "Bay cycle throughput, week 35."
    alt: "Bar chart, four bays, week 35."
```
Honesty row 3 is an `assets:` entry **omitting `folder`** — provenance is checked *before* the file
read, so it needs no PNG on disk (`weekly-full.yml` already relies on this: three assets, one PNG).
Names in use (`Miles O'Brien` / `Kira Nerys` / `Julian Bashir`) are on **neither** denylist — safe.

**Analog B — the bindings source (reused per the recorded decision):** `content/module/module-a.yml`
is the only root-level `*.yml` in `content/module/` (alongside `ids.json` and `site/`), loaded via
`load_swimlanes(config, root=root)`. It already declares a KPI-less lane → honesty row 1 free.

**Analog C — the abstraction-guard denylist** (`tests/test_abstraction_guard.py:76-96, 177-189`) —
add a `_WEEKLYSITE_CORPUS_VALUES` frozenset into the same union, following the existing grouping
(ids / full names / functional-group names), plus a `_DENY_PATTERNS` regex if the new ids are a
numbered family:
```python
_SAMPLE_TEAM_NAMES = frozenset({
    # ids
    "jean-luc", "williamr", "geordila", "dataf606", "beverlyc", "deannatr", "worf9e03",
    # full names
    "Jean-Luc Picard", "William Riker", "Geordi La Forge", "Beverly Crusher", "Deanna Troi", "Worf",
    # functional-group / org / module names
    "Bridge Operations", "Engineering Corps", "Medical & Wellbeing", …
})
…
        | _SAMPLE_TEAM_NAMES
        | _SEED_SCHEME
        | _CASESPEC_CONFIG_VALUES
        | _WEEKLYSPEC_FIXTURE_VALUES,
        key=len, reverse=True,
…
_DENY_PATTERNS = (re.compile(r"\beng-\d{2,}\b"), …)
```
The guard scans `src/` **only**, so the corpus's own use of those names is safe — the point is that
a future leak of a corpus value into source fails loudly.

---

## Shared Patterns

### Lazy optional-extra import (AI-optional core / PKG-04)
**Source:** `cli.py:48,82,125,165` · `modulesite.py:45` (`._yaml_loader`) · `pptx_writer` never at
module scope in a builder.
**Apply to:** `weeklysite.py`, the new `weekly` CLI command, both test modules.
Every optional dependency is imported **inside the function body**, so `lint-imports` stays
2 kept / 0 broken and the bare install is untouched.

### The builder is the SOLE ledger writer, at the committed path
**Source:** `modulesite.py:180-182` + the caveat docstring `test_modulesite.py:25-29`.
**Apply to:** `weeklysite.build_weekly_site`; every test that builds into `tmp_path`.
```python
ledger = Ledger.load(_LEDGER_PATH)   # committed path, NEVER out_dir
site = Site.from_surfaces(surfaces, ledger=ledger)
ledger.save()
```

### Honesty routing — one wording, never a new sentence
**Source:** `compose.NO_KPIS` · `specspan.absent` · `weeklyspec._ASSET_PROVENANCE_ABSENT`.
**Apply to:** all fixture design and all assertions. Read the string from `surface.missing`;
never author a disclosure literal in a test or in `src/`.

### Generated-marker + zero-external-call
**Source:** `test_publish.py:222` (`_MARKER`) · `test_modulesite.py:160-193`.
**Apply to:** every new published page. Free from `render_surface` / `render_library` /
`worksurface._emit_fonts` — but assert it.

### Fail-loud, never partial
**Source:** `publish.py:56-68` (missing corpus raises before any write; foreign out-dir refused) ·
`modulesite.py:79-81` (teaching `FileNotFoundError` on an unpopulated corpus).
**Apply to:** `weeklysite`'s two discovery helpers and `build_weekly_deck`.

### Prove it blocks, not just passes
**Source:** `test_module_cli.py:75-95` (monkeypatched Published surface → nonzero) ·
`test_modulesite.py:375-379` (planted-leak self-check).
**Apply to:** the weekly CLI gate test and the weekly synthetic-content scanner. Draft-only corpora
make "exit 0" vacuous — say so in the docstring and prove the other direction.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `content/weekly/deck/*.pptx.digest` | integrity sidecar | file-I/O | No committed digest sidecar exists yet. `part_digest` is the primitive (`pptx_writer.py:236`) and the two-tier scheme is specified in `.planning/notes/2026-08-29-pptx-determinism-decision.md`; the *file convention* (one hex line + `\n`, `<name>.pptx.digest`) is new in this phase. |
| `tests/_corpus_scan.py` (optional promotion) | test helper | — | No shared test-helper module exists under `tests/` today. Promotion precedent is in `src/` (`specspan.SpanMinter`, `compose.compose_kpi_item`, `pptx_writer.normalize_opc_zip`); if promotion is out of scope, write a self-contained weekly scanner and record the two-copies drift explicitly (RESEARCH A6). |
| `docs/weekly.md` "doc-contract" test | test | — | `tests/test_collaboration_contract.py` is the nearest presence-guard idiom, but asserting fenced `newsletters …` lines against the live Typer app is a new assertion shape. |

---

## Metadata

**Analog search scope:** `src/newsletters/` (`modulesite`, `worksurface`, `dogfood`, `publish`,
`cli`, `pptx_writer`, `weeklyspec`), `tests/` (`test_modulesite`, `test_publish`, `test_render`,
`test_module_cli`, `test_weeklyspec`, `test_abstraction_guard`), `content/module/`,
`tests/fixtures/weekly/`, `docs/` (`case-spec`, `architecture`), `.github/workflows/`
**Files scanned:** 18 read, ~40 grepped
**Pattern extraction date:** 2026-08-29
