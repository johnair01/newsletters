# Lane D spec: Library connector v0

## Purpose

Let a client's Claude read one Library. A small local MCP server, read-only, with three tools:
list editions, read an edition, search the Library. Pulse IQ is the first and only client.

## What a Library is on disk (found in this repo, not invented)

The engine already writes Libraries. There are three in `content/`: `rev1/`, `work/`, `module/`.
Each one is a folder with this shape:

```
<library>/
  ids.json            the ledger: slug -> {ref, type, issue, date}. Append-only, sorted.
  site/
    <slug>.html       one rendered edition per ledger slug (written by newsletters.render)
    library.html      the index page (not an edition)
    index.html        a landing page in rev1 only (not an edition)
    fonts/            self-hosted fonts
```

Facts the connector relies on, each checked against the files:

- **The ledger is the list of editions.** `docs/architecture.md` calls `ids.json` the source of
  truth for refs. An edition is a slug that is in `ids.json` AND has `site/<slug>.html`.
  Pages not in the ledger (`library.html`, `index.html`, `onboarding-newcomer.html`) are not
  editions.
- **Each edition HTML carries its title and its review state.** Title: `<h1 class="... mast-title">`.
  State: the first status tag in the masthead, emitted by `render._status_tag`:
  `sg-tag published` = Published, `sg-tag review` = In Review, `sg-tag draft` = Draft, and
  `sg-tag peer` ("Peer review") = an Article that is In Review.
- **The readable body is inside `<main>`.** Navigation, styles and the theme script sit outside it.
- **Not every edition on disk is Published.** In `content/rev1` today: 6 Published, 2 In Review
  (`report-plan`, `report-rev1`), 1 Article in peer review, 1 Draft. `work/` and `module/` are all
  Draft.

## No Pulse IQ Library exists in this repo

Searched the repo for it. Pulse IQ is named only in docs and comments. So v0 ships with:

- a **fixture Library** at `tests/fixtures/library-fixture/`, clearly labelled FIXTURE in its
  README and in every page title, in the real format, used by the tests; and
- instructions to point the server at `content/rev1` (the engine's own sample Library, real
  engine output) for the Editor-in-Chief's hands-on test, because it has enough real content to ask questions of.

When Pulse IQ has a Library folder of the same shape, the Editor-in-Chief points the server at it. No code change.

## The three tools

All three read only Published editions (see decision D2). All return plain JSON-able dicts.

1. `list_editions()` returns
   `{library, editions: [{slug, ref, type, title, status, issue, date}], withheld_unpublished: N}`.
   Order: ledger order (slug sorted, as `ids.json` is written). `withheld_unpublished` says how
   many editions exist but are not Published, so the reader knows the list is filtered.
2. `read_edition(slug)` returns `{slug, ref, type, title, status, issue, date, text}` where `text`
   is the edition's `<main>` as plain text with paragraph breaks. Unknown slug or non-Published
   edition: an error that says which, and nothing else.
3. `search_library(query, limit=10)` returns
   `{query, results: [{slug, ref, type, title, hits, snippet}]}`. Case-insensitive; every word in
   the query must appear in the edition (title or text). Ranked by total hits, then slug. Snippet:
   about 240 characters around the first hit.

## Deliberately out of v0

- **Writes of any kind.** No create, edit, approve, publish. The review gate stays where it is.
- **Unpublished editions.** Draft and In Review content is not served.
- **More than one Library or client.** One server process, one Library folder.
- **Hosting and remote access.** stdio transport only, runs on the Editor-in-Chief's machine.
- **Auth.** None needed for local stdio; none built.
- **Client data.** None used. Fixture plus the engine's own sample only.
- **Reading the semantic model (claims, traces).** The connector reads published HTML, which is
  what a reader sees. Trace-level reading is a later version.
- **Changes to `src/newsletters/` or `pyproject.toml`.** The connector lives in `mcp/library/` so
  core stays stdlib + Pydantic and the MCP SDK never touches it.

## How the Editor-in-Chief tests it

`v0.md` has the exact steps: install the MCP SDK, add the server to Claude Code (`claude mcp add`)
and Claude Desktop (`claude_desktop_config.json`), then ask three questions:

1. "What editions are in my Library?" (expects list_editions)
2. "Read me the kickoff report." (expects read_edition on `report-kickoff`)
3. "Where does my Library talk about the review gate?" (expects search_library)

## Acceptance

- Tests over the fixture: list, read, search, unknown slug, unpublished slug refused, path
  traversal refused, empty query, HTML to text strips script/style/nav.
- A conformance test over the real `content/rev1` Library: every ledger edition parses, gets a
  title and a known status.
- A test that the MCP server registers exactly the three tools, all marked read-only (skipped if
  the MCP SDK is not installed).
- A real stdio round trip: start the server as a subprocess and call the tools through an MCP
  client session.

## Open items

- **O1. Client-name filter before serving a real Library.** The real Pulse IQ issues name a client
  throughout. Serving them, even locally, without a filter would put client names in front of
  any Claude the Library is attached to, and loading them into this public repo would publish
  them. So: no real issues are loaded into this repo tonight, and before a real Library is served
  the connector needs a name filter. Shape (candidate): a local, git-ignored list of names to
  redact, applied to every tool output (titles, text, snippets), with search refusing to match a
  redacted name. Candidate test: `test_candidate_client_name_filter` in
  `tests/test_library_connector.py`, skipped until the filter exists. It uses an invented name only.
- **O2. Names on the public branch.** The Orchestrator ruled at 7:06 PM PT: no client or person
  names anywhere on this branch. Lane files now use roles. The sample Library `content/rev1`
  (already on main) has audience cuts named after people; v0.md no longer repeats those slugs.
  The first lane commit (`d05d30a`) still holds the earlier wording in history. Rewriting branch
  history is the Maintainer's call, not done here.
