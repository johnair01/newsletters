# Lane D status

Branch: `connector-v0`. Nothing merges to main.

## Plan

1. [x] Discuss: find the real Library format, write spec.md and decisions.md
2. [x] Fixture Library (labelled FIXTURE) in tests/fixtures/library-fixture/
3. [x] Reader module `mcp/library/library_reader.py` (stdlib only) + tests
4. [x] MCP server `mcp/library/server.py` (three read-only tools) + registration and stdio tests
5. [x] Validate: full test suite, conformance on content/rev1
6. [x] Ship: v0.md, learnings.md, promises.md, push
7. [x] Retro in learnings.md

## Log

- Step 1 done. No Pulse IQ Library in this repo; fixture + content/rev1 plan in decisions D3.
- Shared files: none touched. Avoiding WHERE-WE-ARE.md, RETRO.md, pyproject.toml, web/ (D4, D8).
- Steps 2-4 done. Fixture built by a Haiku subagent, checked by hand (README label, ids.json, no page for the missing-html entry).
- Found and fixed while testing: (a) adjacent inline tags ran together ("The ReportPublished"); (b) title counted twice in search; (c) MCP SDK 2.x hides any non-ToolError message, so refusals reached Claude as "Error executing tool" with no reason. Now raises ToolError; the stdio test proves the reason arrives.
- tests/test_library_connector.py: 17 passed.
- Step 5 done. Full suite 663 passed, 1 skipped. Server command run against content/rev1 over stdio with MCP SDK 2.3 and 1.30 (throwaway venv). Not run: Claude Code / Desktop themselves, lint-imports (not installed).
- Steps 6-7 done. v0.md, learnings.md (with Retro), promises.md written. Retro top item (client test not run) is addressed in the only way open tonight: v0.md names it as JJ's gate.
- Lane D complete for tonight. Waiting on JJ's gate. Nothing merged.
