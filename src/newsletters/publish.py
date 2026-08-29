"""Assemble the published site tree (PUB-01/PUB-02) — the ONE definition of "the site".

The published GitHub Pages site is the **rendered record**: the four committed corpora
composed into a single tree, plus the two pieces of assembly chrome (``.nojekyll`` and the
base-path-absolute ``404.html``). This module is deliberately a *library function* rather
than workflow shell: the exact code path that publishes is the one the unit tests, the CI
``site-integrity`` job, and the deploy workflow all exercise — an untested ``cp`` in YAML is
the seam that let the site rot unnoticed (see
``.planning/research/2026-07-03-pages-publish-forensics.md``).

Trust properties:

* **Committed bytes only.** What was reviewed is what publishes — every corpus file is
  byte-copied from ``content/*/site``; nothing is freshly rendered here except the 404 page,
  which is assembly chrome (it embeds the base path, a property of the tree, not of any
  corpus) and is deterministic renderer output like everything else.
* **Fail loud, never partial.** A missing corpus raises before a single file is written; a
  non-empty ``out_dir`` that is not a previous assembly is refused, never clobbered. "Previous
  assembly" means OUR markers, plural (WR-05): the ``.nojekyll`` chrome **and** the renderer's
  generated-by marker in ``index.html`` — ``.nojekyll`` alone is every GitHub Pages tree's
  furniture, not an ownership proof, and treating it as one made any static-site checkout one
  mistyped ``--out`` away from ``rmtree``. ``force=True`` is the explicit human override.
* **Deterministic.** Sorted walk, byte-copy, no timestamps — two assemblies of the same tree
  are byte-identical (proven by test).

Stdlib + in-package imports only (the AI-optional core contract applies).
"""

from __future__ import annotations

import shutil
from pathlib import Path

# corpus source dir (relative to the repo root) → destination inside the assembled tree.
# The rev1 sample record fronts the site at the ROOT; the real work record, the synthetic
# module worked-example and the synthetic weekly worked-example sit alongside. The Records
# strips rendered into each corpus's chrome pages (Phase 1, PUB-03) assume exactly this
# layout — the assembled-tree link test is the contract that keeps the two in agreement.
#
# ONLY ``content/*/site`` is copied, and that is load-bearing rather than incidental: the
# weekly corpus also commits a rendered ``.pptx`` under ``content/weekly/deck/``, and it is
# unpublishable HERE, by layout, rather than by anyone remembering to exclude it (T-04-08).
_CORPUS_LAYOUT: tuple[tuple[str, str], ...] = (
    ("content/rev1/site", "."),
    ("content/work/site", "work"),
    ("content/module/site", "module"),
    ("content/weekly/site", "weekly"),
)


def _is_previous_assembly(out: Path) -> bool:
    """True iff ``out`` looks like a tree THIS tool assembled — the pre-``rmtree`` proof.

    Ownership needs BOTH markers (WR-05): the ``.nojekyll`` assembly chrome AND the renderer's
    generated-by marker inside ``index.html``. ``.nojekyll`` alone is the standard furniture of
    essentially every GitHub Pages checkout, so it proves "a static site lives here" — exactly
    the tree the clobber guard exists to protect, not license to destroy. The marker sentence is
    read from ``render.GENERATED_MARKER`` (one source of truth; the same sentence
    ``test_every_assembled_page_carries_generated_marker`` enforces on every page we emit), so a
    previous assembly ALWAYS carries it and a foreign tree essentially never does.
    """
    if not (out / ".nojekyll").is_file():
        return False
    index = out / "index.html"
    if not index.is_file():
        return False
    from .render import GENERATED_MARKER  # in-package; kept lazy beside the CLI's lazy style

    try:
        return GENERATED_MARKER in index.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False  # unreadable index == unproven ownership == refuse


def assemble_site(
    out_dir: str | Path = "dist/site",
    *,
    base_path: str = "/newsletters/",
    repo_root: str | Path = ".",
    force: bool = False,
) -> list[Path]:
    """Compose the committed corpora into the publishable tree at ``out_dir``.

    Returns every written path (files only) in deterministic write order. ``base_path`` is
    the URL prefix the tree will be served under (GitHub project pages →
    ``/newsletters/``); it is embedded ONLY in ``404.html`` — every other page keeps the
    corpus's relative links and works under any prefix. A non-empty ``out_dir`` is replaced
    only when it proves it is OURS (see :func:`_is_previous_assembly`) or when the caller
    passes ``force=True`` — the explicit, human "yes, clobber that tree" that no marker
    heuristic should ever imply.
    """
    root = Path(repo_root)
    missing = [src for src, _ in _CORPUS_LAYOUT if not (root / src).is_dir()]
    if missing:
        raise FileNotFoundError(
            f"cannot assemble the published site — committed corpus dir(s) missing: {missing}. "
            "Every corpus publishes or none does (no partial site)."
        )

    out = Path(out_dir)
    if out.exists() and not out.is_dir():
        raise FileExistsError(
            f"refusing to overwrite {out} — it is a FILE, not a directory. assemble_site only "
            "replaces a directory that proves it is a previous assembly; pick a new --out."
        )
    if out.is_dir() and any(out.iterdir()) and not force and not _is_previous_assembly(out):
        raise FileExistsError(
            f"refusing to overwrite {out} — it is non-empty and does not prove it is a previous "
            "assembly of THIS tool (that takes BOTH the .nojekyll chrome AND the generated-by "
            "marker in its index.html; .nojekyll alone is every GitHub Pages tree's furniture, "
            "not an ownership proof). Pick an empty/new out dir — or pass --force only if you "
            "are certain this tree is yours to destroy."
        )
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    written: list[Path] = []
    for src, dest in _CORPUS_LAYOUT:
        src_dir = root / src
        dest_dir = out if dest == "." else out / dest
        for f in sorted(p for p in src_dir.rglob("*") if p.is_file()):
            target = dest_dir / f.relative_to(src_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(f.read_bytes())
            written.append(target)

    # Assembly chrome. .nojekyll stops GitHub Pages' Jekyll pass (a plain static tree needs
    # none, and Jekyll would eat underscore paths); it doubles as this module's "previous
    # assembly" marker for the clobber guard above.
    nojekyll = out / ".nojekyll"
    nojekyll.write_bytes(b"")
    written.append(nojekyll)

    from .render import render_404  # in-package; kept lazy beside the CLI's lazy style

    page_404 = out / "404.html"
    page_404.write_text(render_404(base_path=base_path), encoding="utf-8")
    written.append(page_404)
    return written
