# Lane D learnings

- 2026-11-07: A Library already has a real format on disk (`ids.json` + `site/<slug>.html`). Reading what the engine writes beat inventing an export.
- 2026-11-07: Rendered Libraries mix states. `content/rev1` holds 6 Published, 3 In Review (one is an Article in peer review), 1 Draft. A reader that ignored the status tag would have served unreviewed work.
- 2026-11-07: In MCP Python SDK 2.x, any exception other than `ToolError` reaches the model only as "Error executing tool <name>". A refusal with no reason is useless to Claude. Only the stdio round-trip test caught this; the unit tests on the reader could not.
- 2026-11-07: SDK 2.x also renamed `FastMCP` to `MCPServer` and switched result attributes to snake_case (`is_error`, `read_only_hint`). Code and tests that must run on a user's machine should tolerate both majors.
- 2026-11-07: The rendered h1 title sits inside `<main>`, so adding the title to the search text counted it twice. Read the markup before adding "helpful" extras.
- 2026-11-07: Delegating the fixture to a Haiku subagent with an exact brief (file names, required words, words that must not leak) gave a fixture that was correct on first check. The brief named its own checks, which made verifying it fast.

## Retro

Ranked most severe first.

1. **The client test is the one thing not run.** Nobody has added this server to a real Claude Code or Claude Desktop. The stdio round trip proves the protocol, not the setup steps or how Claude uses the tools. Fix: JJ's run of v0.md is the gate; until then v0 is unproven where it matters. Built: v0.md says this plainly under "Not checked".
2. **Silent refusals nearly shipped.** Before the stdio test, the server raised `ValueError`, and SDK 2.x would have hidden every refusal reason. A reader-level test suite passed while the user-facing behaviour was wrong. Rule: any MCP server in this repo gets a real stdio round-trip test that asserts on the error text a model sees. Built: `test_stdio_round_trip` asserts the "not published" reason arrives.
3. **The 1.x SDK path has no automated test.** I checked it by hand in a throwaway venv. If someone breaks the fallback import, CI will not notice. Not built tonight: it needs a second CI job or a pinned extra, which touches files outside this lane.
4. **The compass is stale by one feature.** `WHERE-WE-ARE.md` was not updated, on purpose, to avoid colliding with Lane B (decision D8). That is a known, chosen staleness, not an accident, but it needs a single entry at merge time.
5. **`lint-imports` was not available.** The AI-optional contract was not re-run. Low risk (no `src/` change), but the gate was not run, so it is listed as not checked rather than assumed green.
