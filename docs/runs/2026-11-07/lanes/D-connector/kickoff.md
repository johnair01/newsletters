# Lane D kickoff (pasted verbatim from the Orchestrator)

Launched by the Orchestrator session session_01Ry6baVDY2yBHG6Fdb17TCq in the Pulse IQ repo.
Sat 7 Nov 2026, Pacific time. Person and client names are replaced with roles at the Orchestrator's request: this repo is public. Otherwise verbatim.

---

You are Lane D of tonight's run (Sat 7 Nov 2026, Pacific time), launched by the Orchestrator session session_01Ry6baVDY2yBHG6Fdb17TCq in the Pulse IQ repo. The Editor-in-Chief is busy as a client for the next hour; make the best call on open questions, write it in decisions.md as a candidate, and go on.

Your branch: connector-v0 in this repo (johnair01/newsletters), from its default branch. Keep your lane folder IN THIS REPO on your branch at docs/runs/2026-11-07/lanes/D-connector/ with kickoff.md (paste this message), spec.md, decisions.md, learnings.md, promises.md, status.md, v0.md. Commit and push status.md after each step. Another lane (B, operator view) works in this same repo on branch operator-view-v0: never write its files; if you both need the same file, stop and say so in status.md.

Rules: one lane, one folder, one branch. Nothing merges to main tonight. Nothing client-facing changes without tests and the Editor-in-Chief's gate. Plain language, no em dashes, no hype.

Lane protocol: Discuss -> Specify (spec.md) -> Plan (steps at the top of status.md, updated as each lands) -> Implement (delegate grunt work like scaffolding and test stubs to Sonnet or Haiku subagents; keep design calls yourself) -> Validate (tests pass; say what you checked and did not) -> Ship (push; decisions.md holds each decision as: decision, options considered, why, what would change it, status candidate; learnings.md dated lines; promises.md one candidate promise per line) -> Retro (if no /retro command, do it by hand under a "Retro" heading in learnings.md, ranked most severe first; build the top item only if it is a doc, test or check inside your folder or branch).

Lane D. Connector v0: a client's Claude reads their Library. Purpose: an MCP server that lets a Claude read one Library: list editions, read an edition, search the Library. Read-only. Pulse IQ's own Library is the first and only client. No client data, no remote auth tonight; local only. This lane is Discuss-heavy: write in spec.md and decisions.md, before code, what a Library is on disk (find the engine's real format in this repo), what the three tools return, what is deliberately out (writes, other clients, hosting, auth), how the Editor-in-Chief will test it from their own Claude.

Kickoff: Build v0 of the Library connector on branch connector-v0: a local, read-only MCP server over one newsletters-engine Library with three tools, list editions, read an edition, search. Pulse IQ's own Library is the only target (if no Pulse IQ Library exists in this repo, use a small fixture Library clearly labelled as such and say so). Then implement with tests. Finish with v0.md including the exact steps for the Editor-in-Chief to add it to their own Claude (Claude Code and Claude Desktop) and ask it three questions about their Library. Do not touch main. Close with the retro. Last message to the Editor-in-Chief: five lines or fewer.
