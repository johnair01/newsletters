# Vision — Newsletters

> Turn information into conversation. Conversation into action.

This is the **north star** — the *why beneath the why*. `product-spec.md` describes what we
build and how it behaves; this document says what it is *for*. When the two seem to point
different directions, the product spec governs the mechanism and this governs the intent —
reconcile them, don't let them drift.

---

## The thing we are really building

A **city**. An economy of active engagement between humans and robots, where the medium of
exchange is **attention** and the trust infrastructure is **traceable, reviewed truth**.

Newsletters is the **public square** of that city — the surface where it reads about itself
and decides what is true enough to act on. We spend time. We write. We tell good, honest
stories. That is not overhead on the work; it *is* the work. Telling a story well is how a
system finds where its problems actually are, gets closer to the issues, and figures out
**where to put the next calories**.

The city runs on co-learning: everyone learning everywhere, all the time, humans and robots
together. Newsletters is the surface to learn about the **"truths"** — and the quotation
marks are load-bearing. A truth here is not a decree. It is a claim with its evidence
attached, reviewed by a person, and **legible enough to be challenged**. We are not building
an oracle. We are building a way for a community to converge on what is real, with every
step on the record.

---

## What the city needs — and where it already lives in the system

These are not aspirations bolted on later. Most are already load-bearing in the typed model
(`architecture.md §1`). The vision is real to the degree it is *enforced*, not professed.

| The city needs… | …and the system carries it as |
|---|---|
| **Traceability** | Every `Claim` holds `Trace`s back to a `Source`. A truth is a statement with its evidence attached — provenance you can follow. |
| **Trust** | Nothing reaches the square unreviewed: `Draft › In Review › Published`, with a named reviewer. No auto-publish path. Trust is enforced, not assumed. |
| **Psychological safety** | The `missing[]` list is the quiet hero: it is *safe to say "I could not substantiate this."* Gaps are surfaced to a reviewer, never hidden or punished. |
| **Rules** | The invariants are checked in code, not just documented — the city's laws are executable, the same for every participant, human or agent. |
| **Security** | Private corpora stay **local and encrypted**, reached only through MCP servers, and are **never serialized into a surface**. Private knowledge shapes emphasis without leaking. |
| **Adaptability** | One reviewed truth fans out, **re-cut per reader** from their own corpus. The model is swappable behind one `distill()` boundary. The method travels; the specifics are configurable. |
| **Domain-informed** | "Strip the proprietary, preserve the personal." The practitioner's voice and reasoning are the point — corpora carry role, ownership, and what each reader cares about. |
| **Co-learning, everywhere, all the time** | The same fact lands differently for the on-call engineer and the lead; what each reader has seen feeds what they see next. Authoring is agentic journalism — interviewing the work to capture what matters. |
| **Efficiency** | Relevance is the whole point. Personalization is the city deciding **where attention is worth spending** — where to put the calories. |

---

## What "truth" means here (and what it does not)

Traceability gives you **provenance, not correctness.** A perfectly traced claim can still be
wrong. That is exactly why the human review gate and `missing[]` exist: the system is built
to be **auditable and correctable**, not authoritative. Truth is something the city
*converges on* through co-learning — drafted by agents, decided by humans, and revisable when
the evidence changes. Rigor is how the output earns trust, not ceremony.

So the design refuses two failure modes by construction:
- **The confident fabrication** — an agent cannot publish an unsubstantiated claim; untraced
  material is blocked and relegated to `missing[]` for a human to see.
- **The silent gap** — what could not be shown is surfaced, not swallowed. Not knowing is a
  first-class, safe state.

---

## How this layer relates to the rest of the spec

- `product-spec.md` — the four surfaces, the publish loop, personalization. The *mechanism*
  that delivers this vision.
- `architecture.md` — the typed semantic model that makes the values above enforceable.
- `design-system.md` / `surfaces.md` — the editorial, human, legible feel of the public square.
- `roadmap.md` — the order we build it in. Today the **trust skeleton** exists (typed truths,
  evidence links, the review gate). The **living half** — the agentic journalist that
  interviews, distills, and drafts, and the feedback loops that make the learning genuinely
  *co*-learning — is the hard, interesting frontier ahead (Phase 4+).

---

*Spend time. Write it down well. Make it traceable. That is how we get closer to where the
issues are — and how the city learns.*
