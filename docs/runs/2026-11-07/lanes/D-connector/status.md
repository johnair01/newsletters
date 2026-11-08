# Lane D status

Branch: `connector-v0`. Nothing merges to main.

## Plan

1. [x] Discuss: find the real Library format, write spec.md and decisions.md
2. [ ] Fixture Library (labelled FIXTURE) in tests/fixtures/library-fixture/
3. [ ] Reader module `mcp/library/library_reader.py` (stdlib only) + tests
4. [ ] MCP server `mcp/library/server.py` (three read-only tools) + registration and stdio tests
5. [ ] Validate: full test suite, conformance on content/rev1
6. [ ] Ship: v0.md, learnings.md, promises.md, push
7. [ ] Retro in learnings.md

## Log

- Step 1 done. No Pulse IQ Library in this repo; fixture + content/rev1 plan in decisions D3.
- Shared files: none touched. Avoiding WHERE-WE-ARE.md, RETRO.md, pyproject.toml, web/ (D4, D8).
