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
- Steps 6-7 done. v0.md, learnings.md (with Retro), promises.md written. Retro top item (client test not run) is addressed in the only way open tonight: v0.md names it as the Editor-in-Chief's gate.
- Lane D complete for tonight. Waiting on the Editor-in-Chief's gate. Nothing merged.
- Orchestrator ruling (7:06 PM PT, public repo): names replaced with roles in all lane files; v0.md drops person-named slugs and uses /Users/YOU paths. Spec O1 (client-name filter) + skipped candidate test added; D9 logged. Earlier commit d05d30a still holds old wording in history; rewriting it is the Maintainer's call. Tests: 17 passed, 1 skipped (the candidate).
