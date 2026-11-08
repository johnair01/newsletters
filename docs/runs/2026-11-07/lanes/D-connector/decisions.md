# Lane D decisions (all candidate until JJ's gate)

## D1. A Library is the folder the engine already writes: `ids.json` + `site/<slug>.html`

- Options considered: (a) read the rendered folder; (b) import `newsletters` and rebuild the
  Site in memory from Python sample data; (c) invent a new export format (JSON per edition).
- Why (a): it is what a published Library actually is on disk today, it needs nothing but the
  folder, and it is exactly what a reader sees. (b) only works for corpora that are built from
  code in this repo, so it cannot serve a client's Library. (c) adds a format before anyone needs it.
- What would change it: the engine starts writing a structured export next to the HTML (for
  example JSON with claims and traces). Then the connector should read that instead of parsing HTML.
- Status: candidate.

## D2. Serve Published editions only; say how many were withheld

- Options considered: (a) Published only; (b) everything, with status shown; (c) a flag to
  include unpublished.
- Why (a): the product's most important rule is no auto-publish. A client's Claude quoting a
  Draft as if it were the Library would route around the review gate. `withheld_unpublished`
  keeps it honest that the list is filtered.
- What would change it: JJ wants an operator mode where reviewers ask Claude about drafts. That
  would be a separate, clearly named tool or server, not a default.
- Status: candidate.

## D3. Fixture Library for tests, the engine's own `content/rev1` for JJ's hands-on test

- Options considered: (a) fixture only; (b) `content/rev1` only; (c) both.
- Why (c): the kickoff asks for a clearly labelled fixture when no Pulse IQ Library exists, and
  tests should not break when rev1 is rebuilt. But a three-page fixture gives thin answers in a
  real conversation; rev1 is real engine output with real content. Neither is client data.
- What would change it: a Pulse IQ Library folder exists. Then v0.md points there.
- Status: candidate.

## D4. Code lives in `mcp/library/`, outside the core package, with no `pyproject.toml` change

- Options considered: (a) `mcp/library/` standalone script; (b) `src/newsletters/connector.py`
  plus a `[connector]` extra.
- Why (a): hard rule, core imports only stdlib + Pydantic. The reader module is stdlib only and
  the MCP wiring is a thin separate file. Not editing `pyproject.toml` also avoids a file Lane B
  could plausibly need tonight. `mcp/README.md` already reserves this folder for MCP servers.
- What would change it: the connector ships as part of `pip install newsletters`. Then it
  becomes an extra with an entry point, decided at merge time.
- Status: candidate.

## D5. Support MCP Python SDK 1.x and 2.x

- Options considered: pin one major version; support both with a two-line import fallback.
- Why: this container has `mcp` 2.3 (where `FastMCP` was renamed `MCPServer`). JJ's machine may
  have 1.x. A fallback import costs two lines and avoids a setup failure on his first try.
- What would change it: we pin dependencies when the connector becomes a packaged extra.
- Status: candidate.

## D6. Slugs are looked up in the ledger, never joined into a path from user input

- Options considered: validate the slug with a regex; only accept slugs present in `ids.json`.
- Why: ledger lookup is simpler and closes path traversal completely: a slug that is not a ledger
  key never reaches the filesystem.
- What would change it: nothing likely.
- Status: candidate.

## D7. Search is plain word matching, no index, no ranking model

- Options considered: (a) all-words substring match with hit counts; (b) a BM25 index; (c)
  embeddings.
- Why (a): a Library is tens of editions, so a scan per query is instant. It is deterministic and
  explainable. Claude does the reasoning on top. (c) would also break the zero-AI spirit.
- What would change it: Libraries grow to thousands of editions, or JJ finds answers missed
  because of wording. Then (b).
- Status: candidate.

## D8. Do not touch `WHERE-WE-ARE.md` or `RETRO.md` tonight

- Options considered: update the compass as CLAUDE.md asks; keep notes in the lane folder.
- Why: those are shared root files and Lane B is in the same repo. Two branches editing the top of
  the same file is a guaranteed merge conflict. The lane folder holds everything; the compass gets
  one entry when JJ merges.
- What would change it: JJ says lanes should write the compass directly.
- Status: candidate.
