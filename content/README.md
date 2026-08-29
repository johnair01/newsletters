# content/ — the Library

The **committed record**: every corpus this project publishes, rendered to standalone HTML and
reviewed in a pull request before it lands. "Review = a pull request" lives here — a draft surface
opens as a PR against this directory, and merging is what makes it publishable. Nothing in here
was rendered by the deploy workflow; what publishes is a byte-copy of what a human read.

## The four committed corpora

| Directory | What it is | Published at |
|---|---|---|
| `rev1/` | The synthesized Rev1 **sample** corpus (`dogfood.py`) — the product demonstrating itself | the site **root** |
| `work/` | The **real** hand-authored work corpus (`worksurface.py`) — the install/dogfood record over this codebase | `/work/` |
| `module/` | The synthetic swim-lane **worked example** (`modulesite.py`) — a fabricated module's config composed and rendered | `/module/` |
| `weekly/` | The synthetic **weekly record** (`weeklysite.py`, WKLY-05) — a hand-authored Weekly Spec composed against the `module` lane config, with three absences planted on purpose | `/weekly/` |

Each corpus is self-contained and keeps its **own append-only ledger** (`ids.json`), so reference
numbers never collide and the sample/real boundary is preserved at the ledger layer. A ledger diff
on a rebuild is a stop-the-line bug, not a merge conflict to resolve.

`content/weekly/deck/` holds the weekly's `.pptx` deck and its `part_digest` sidecar. It sits
**outside** `content/weekly/site/`, which is why no deck can reach the published tree — see below.

## The one publish channel

`publish.assemble_site()` — exposed as `newsletters assemble --out dist/site` — composes those
four `content/*/site` directories (plus `.nojekyll` and the base-path-absolute `404.html`) into
the publishable tree. It copies **`content/*/site` only**, byte-for-byte; it never renders content
fresh. `.github/workflows/deploy-pages.yml` then runs the merge-block gate per corpus and the
published-tree guarantees, assembles via that same function, and force-pushes a single commit to
`gh-pages` — **from `main` only**. There is no other path to production, and no feature branch has
one. See `docs/architecture.md` §9.
