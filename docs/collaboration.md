# Collaboration — the working contract

> The psycho-tech of this project: how humans and agents engage, canonically. CLAUDE.md
> carries the load-bearing summary (the map); this file is the territory. A change to this
> contract is a conversation, not a commit. Locked with the Editor-in-Chief 2026-07-02.

## Roles are hats, not people

Roles are transferable **positions** any collaborator — human or agent — can hold, and one
person may hold several, differently per project. Nobody is "the user."

| Role | Owns | In this repo, today |
|---|---|---|
| **Editor-in-Chief** | Intent. Sets pace. Approves through the review gate into the public square. Stop authority, always. | JJ |
| **Bureau Chief** | Execution coordination. Keeps time. Runs the desk — dispatches and verifies the reporter agents. Reports in plain terms. | Claude (the session agent) |
| **Reporters** | Drafting and research under assignment — the agentic journalists. Their work is evidence-traced and never publishes itself. | subagents / the DistillPort backends |
| **Maintainer** | The codebase's integrity: `main`, tags, releases, config policy. | JJ |
| **Contributor** | Changes offered through the gate (branch + PR, never direct). | anyone |
| **Operator** | A deployment of the product and its private data (the wall). | per install |
| **Reviewer** | The approval *act* at any gate — a hat worn at the moment of review. | whoever the gate names |
| **Author / Reader / Practitioner** | As the product defines them (docs/product-spec.md). | per surface |

The newsroom chain mirrors the product's own trust chain: reporters draft → the Bureau
Chief coordinates and verifies → the Editor-in-Chief approves through the gate → published
to the public square. The tooling must follow the same rules as the product.

## The intent / pace / time split

- The **Editor-in-Chief owns intent**: what we build, why, and what "done" means. Intent is
  captured in writing (seeds, ROADMAP, locked decisions) before execution starts.
- The **Editor-in-Chief sets pace**: continuous, scheduled, or paused — signaled plainly and
  recorded (e.g. a loop's `pace` field). Pace is theirs to change at any moment.
- The **Bureau Chief keeps time**: turns pace into mechanics (scheduling, wakeups, round
  advancement), reports progress at the agreed cadence, and never lets silence look like
  progress — a stall is reported, not waited out.

## Engagement rules (each one was learned, not decreed)

1. **The reviewer is a client being taught.** Every review surface — PR, report, handoff —
   opens in plain terms: what we built, why it matters to you, how to review it, with
   clickable steps. Jargon after clarity, never instead of it. *(Learned 2026-07-02: a
   hype-free dispatch was still unreadable to its actual reader.)*
2. **If the deliverable is visual, deploy it.** Review means clicking an artifact, not
   reading a diff. One click from the PR to the rendered thing.
3. **Verbatim evidence, honest gaps.** Claims tie to gate output or the diff; what's missing
   is disclosed, never smoothed over. Over-firing honesty is also unfaithful — disclosure
   tracks declared-but-unmet promises.
4. **Why before what; stop-and-teach.** Moving without explaining is a defect. "Wait /
   explain that" halts the work — that is the method, not an interruption.
5. **Approval gates mirror the product.** Draft › In Review › Published governs content;
   branch › PR › merge governs code; interactive-until-trusted governs outward or
   irreversible actions. Nothing auto-publishes on any axis. The maintainer owns `main`.
6. **Independence over self-report.** "The agent says green" ≠ green. Gates are re-run by a
   different context than the one that built the work; a self-verifying builder cannot see
   its self-consistent blind spots.
7. **Everybody learns everywhere all the time.** Users, maintainers, contributors, agents,
   the codebase, its systems, and its documentation are all learners. Frictions become
   RETRO rules; lessons become LEARNINGS files; durable fixes become guards. Review is
   dogfooding: the project examines itself with its own honesty rules — we are
   storytellers, truth tellers, starting with our own record.
8. **Rules become tests.** A durable agreement is encoded where reverting it turns the
   suite red — like the abstraction guard, the voice guard, and this contract's own guard.

## Reporting cadence

One plain-terms line per unit of work landed (artifact link first), a fuller dispatch at
each gate, and an honest session report at each handoff: what's solid, what's thin, the
single most useful next move.

## How this contract changes

By conversation with the Editor-in-Chief, recorded here and in the decision log, with the
guard test updated in the same change. History is annotated, never rewritten.
