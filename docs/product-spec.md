# Product Spec — Newsletters

> Turn information into conversation. Conversation into action.

This is the canonical description of **what** Newsletters is and does. Architecture lives in
`architecture.md`; the visual contract in `design-system.md`; per-screen detail in
`surfaces.md`. When code and this spec disagree, this spec wins (or you update it and say why).

---

## 1. Why this exists

In a world flooded with information, **relevance wins.** Most of what a team learns
evaporates — it lives in a thread, an unrecorded call, a dashboard one person reads. The
knowledge is there; it never gets distilled, attributed, or relayed.

Newsletters is the **semantic bridge** between structured data and human understanding. It
captures work as it happens and hands each person the version that matters to them —
without endless meetings or manual gathering. It is a *learning surface*: infrastructure for
a team that wants to learn everywhere, all the time, and relay what it learns to exactly the
people it helps.

### Principles — working in the open
1. **Public storytelling** — set context in the open: what we are doing and why, as we do it.
2. **Community contribution** — make it easy for anyone to pick up, fork, and add to the work.
3. **Prototyping in the wild** — ship rough, learn fast, in view of the people it is for.
4. **Reflection & documentation** — talk openly about mistakes, changes, and what we learned.
5. **Remixable products** — leave behind records others reuse, not heroics they can only admire.

These five are not decoration — they shape the product. The home surface presents them as
"the thesis," and the whole system is built to be forked and self-hosted.

---

## 2. Information architecture

A single top-nav spine. Everything else nests beneath it.

```
Start here  ·  Newsletters  ·  Articles  ·  The Show
                                            └─ (Report and Library are reached from inside these)
```

| Nav item        | Role |
|-----------------|------|
| **Start here**  | The home / charter. What this is, the operating rhythm, how it publishes, the invitation. (V1 = `Newsletters - Home.html`.) |
| **Newsletters** | The weekly signal — one shared edition plus a personalized variant re-cut per reader. |
| **Articles**    | Peer-reviewed write-ups; every claim traced to a source. Published to the Library. |
| **The Show**    | Recorded practitioner conversations — the raw material everything is distilled from. |
| *Report*        | The reusable structured record a surface is built on. Reached from a surface, not the top nav. |
| *Library*       | The durable archive of published Articles and records. |

---

## 3. The four surfaces

Each surface is a different distance from the raw work. One reviewed record fans out into
all of them.

- **The Show** — recorded conversations. Practitioners walking through real work and the
  reasoning behind it. *Cadence: every other week.*
- **Newsletters** — the weekly signal, per reader. A level-headed digest of what changed and
  why it matters, automatically re-cut for each reader from their own corpus. One shared
  edition, many personal ones. *Cadence: weekly, ~6-min read.*
- **The Articles** — peer-reviewed write-ups generated from conversations and system outputs.
  Every claim traced to evidence, human-validated before publish.
- **The Report** — the reusable record. The structured object a surface is built on,
  regenerated per event so the next person inherits the shape, not a blank page.

---

## 4. The publishing engine — human in the loop

Agents do the drafting. People do the deciding. Nothing publishes without passing review.

```
Ingest  →  Distill  →  Review  →  Publish
(event)    (agent)     (human/PR)  (system)
```

1. **Ingest** — a conversation or event (a recorded walk-through, an incident, a merged
   change) is structured into a `Source` record.
2. **Distill** — the agentic journalist synthesizes the record into surfaces, tuned to each
   audience corpus.
3. **Review** — the draft opens as a **pull request**. A human edits, questions, and approves.
   Rigor is how the output earns trust — not ceremony.
4. **Publish** — on merge it ships to the Show, the Letters, and the Articles; the Library
   remembers it.

**Review gate**, carried on every artifact and visible in every surface:
`Draft › In Review › Published`.

---

## 5. Personalization

The same reviewed `Source` produces a different letter for each reader. **No new facts — new
emphasis.** This is the product's signature interaction; the home surface demonstrates it
live (switch reader, watch the letter re-cut).

- **Codify once.** The event is reviewed and recorded a single time, every claim traced to its source.
- **Tune to a corpus.** Each reader carries a private corpus (role, owned services, what they
  have read). It stays **local and encrypted**.
- **Re-cut on send.** The agent reorders, reframes, and trims the same record against that corpus.

Worked example — one source (a latency regression four dashboards disagreed about) seen
three ways:

| Reader            | Leads with | Why |
|-------------------|-----------|-----|
| A maintainer      | Root cause + the fix + what to watch | Owns the affected service. |
| A new contributor | How we debug here + the reusable record + glossary | First month; needs orientation. |
| An eng lead       | Time-to-cause, what it unblocks, the quarter's pattern | Sponsors the team; wants outcomes. |

The three personas, their accents, and the exact per-reader copy used in V1 are specified in
`surfaces.md` → Home → personalization demo.

---

## 6. Audience & deployment shape

- **Primary users:** members of a team that produces structured work (engineers, analysts,
  operators) and the readers who need to stay current without attending everything.
- **Two roles in the loop:** *authors/reviewers* (draft via agent, approve via PR) and
  *readers* (receive personalized surfaces).
- **Deployment:** self-hosted. Private corpora and source data stay in the operator's
  environment, reached through modular **MCP servers** (see `architecture.md`).
- **Openness:** MIT-licensed, forkable. Every surface is a slot-marked template so any team
  can repopulate it with their own specifics — the method travels, the design comes with it.

---

## 7. Status & roadmap (product-level)

- [x] Design language + surface templates (Show, Newsletter, Articles, Report, Hub, Start-here)
- [x] Converged open-source home (V1 — `Newsletters - Home.html`)
- [ ] Implement surfaces in the real stack (this build)
- [ ] Standalone personalization surface
- [ ] Standalone "How it publishes" engine surface
- [ ] First agentic-journalist prototype + PR review flow
- [ ] Private corpus creation & management
- [ ] MCP server integrations
- [ ] Open-source release

The engineering breakdown of these is in `roadmap.md`.
