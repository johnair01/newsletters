"""Assemble the published site tree (PUB-01/PUB-02) — the ONE definition of "the site".

The published GitHub Pages site is the **rendered record**: the three committed corpora
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
  non-empty ``out_dir`` that is not a previous assembly is refused, never clobbered.
* **Deterministic.** Sorted walk, byte-copy, no timestamps — two assemblies of the same tree
  are byte-identical (proven by test).

Stdlib + in-package imports only (the AI-optional core contract applies).
"""

from __future__ import annotations

import shutil
from pathlib import Path

# corpus source dir (relative to the repo root) → destination inside the assembled tree.
# The rev1 sample record fronts the site at the ROOT; the real work record and the synthetic
# module worked-example sit alongside. The Records strips rendered into each corpus's chrome
# pages (Phase 1, PUB-03) assume exactly this layout — the assembled-tree link test is the
# contract that keeps the two in agreement.
_CORPUS_LAYOUT: tuple[tuple[str, str], ...] = (
    ("content/rev1/site", "."),
    ("content/work/site", "work"),
    ("content/module/site", "module"),
)


def assemble_site(
    out_dir: str | Path = "dist/site",
    *,
    base_path: str = "/newsletters/",
    repo_root: str | Path = ".",
) -> list[Path]:
    """Compose the committed corpora into the publishable tree at ``out_dir``.

    Returns every written path (files only) in deterministic write order. ``base_path`` is
    the URL prefix the tree will be served under (GitHub project pages →
    ``/newsletters/``); it is embedded ONLY in ``404.html`` — every other page keeps the
    corpus's relative links and works under any prefix.
    """
    root = Path(repo_root)
    missing = [src for src, _ in _CORPUS_LAYOUT if not (root / src).is_dir()]
    if missing:
        raise FileNotFoundError(
            f"cannot assemble the published site — committed corpus dir(s) missing: {missing}. "
            "Every corpus publishes or none does (no partial site)."
        )

    out = Path(out_dir)
    if out.exists() and any(out.iterdir()) and not (out / ".nojekyll").exists():
        raise FileExistsError(
            f"refusing to overwrite {out} — it is non-empty and not a previous assembly "
            "(no .nojekyll marker). Pick an empty/new out dir."
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
