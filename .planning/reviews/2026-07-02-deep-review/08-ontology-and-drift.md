# Round 8 — Ontology, semantic drift & compass coherence (total history)

> Deep-review loop, Round 8. Subject: the repo's **language** across its whole git/PR history —
> how the load-bearing terms evolved, where superseded terms still sit in docs/planning TODAY, and
> the compass fixes. Standing lenses: delta-to-reality · **semantic/ontological drift** · total-
> history honesty.
>
> **Framing (Editor-in-Chief).** "We are storytellers, truth tellers." The language *is* part of
> the product; drift in language is drift in truth. This round reviews and — uniquely among the
> rounds — is allowed to **edit prose** (docs/planning only; never code, tests, or config).
>
> **Method.** Every turn-point cites a commit/PR read at this SHA (`git show -s`). Every "stale text
> remains" entry is a live `file:line` verified this round. Dispositions: **fixed-this-round**
> (edited in place) · **annotated** (history preserved, drift noted in place) · **maintainer-
> decision** (governed doc or genuine ambiguity — surfaced, not unilaterally rewritten).

---

## The meta-point worth naming first: this repo enforces terminology in CODE

Most projects police vocabulary in review comments, if at all. Newsletters makes two of its
ontological distinctions **executable invariants** — a reserved-verb / distinct-type test, not a
convention:

- `test_problemstate_distinct_from_reviewstate` — the Problem lifecycle enum (axis 3) must be a
  different type from the Surface review-gate enum (axis 1); a merge that collapses them goes RED.
- `test_lifecycle_verb_collides_with_no_axis_verb` — the axis-3 mutator verb (`transition`) may not
  be a verb already owned by axis 1 (`advance`/`publish`) or axis 2 (`fan out`/`derive`).

That is the rare, honest thing here: the ontology has *teeth in the type system* (07 ledger inv#10,
`structural`). Its limit — also honest — is that the guards prove the **enums and verbs** are
disjoint, **not the free-text copy**. So the code cannot drift the axes together, but the *prose*
can still call the surface fan-out a "promotion chain" — and it does (see D2). Executable ontology
closes the code door; this round closes the prose door the test can't see.

---

## The drift ledger

Legend — Disposition: **F** fixed-this-round · **A** annotated (history kept) · **M** maintainer-decision.

| # | Term | Old meaning → new meaning | Turn point (commit/PR + why) | Where stale text remains TODAY | Disp. |
|---|------|---------------------------|------------------------------|-------------------------------|-------|
| D1 | **Signals → Newsletters** | "Signals" *was* the product name → **Newsletters** is the product/repo; "Signals" survives, narrowed, in three legitimate senses: the **editorial design language** (`design-system.md` title), the **"Signals dispatch" PR-body voice** (Phase 4), and **`design-reference/` prototype filenames**. | Repo/product renamed to Newsletters; `docs/design-system.md:1` codifies the split ("Newsletters (the 'Signals' editorial language)"). The design-reference package handoff `cb72d97` (2026-06-27) kept the `Signals *.html` filenames. | `docs/surfaces.md` (many `Signals *.html` file refs — **legitimate**, they name real prototype files); `docs/architecture.md:23`; `docs/roadmap.md:19,73-101`; `docs/design-system.md:132` ("pre-converged 'Signals'"). | A |
| D2 | **promotion chain → fan-out (axis 2)** | The surface derivation Sources→Report→Article→Newsletter was a "**promotion chain**" → it is a **fan-out**: one reviewed record fans out into audience-tuned surfaces (report/article/newsletter/show/learning). | Three-axes seed `promotion-terminology-guard.md` (2026-06-17): "A *fan-out*, not a *promotion*"; SITE-05 renamed the site device to fan-out (Phase 9); the `fan-out stub` shipped in `e9eaf17` (Phase 2). "promote/promotion" reserved *out* of axis 2 to avoid collision with axis 3. | `WHERE-WE-ARE.md:348` "**one promotion chain**"; `.planning/PROJECT.md:51,61,158`; `.planning/research/FEATURES.md:49`; `docs/architecture.md:191` ("two human-gated promotions"). | A (WHERE-WE-ARE) / M (PROJECT, architecture, FEATURES) |
| D3 | **Claim→KPI / Report→Article = "promotion"** | Still called a **promotion** — and correctly. | Rev1 `5aca6f2` (`promotions`, capture). The seed reserves "promotion" *away from the surface fan-out*, but the **human-gated grammar steps** `Claim→KPI` and `Report→Article` are genuinely promotions (a thing rising in status), not fan-out. | `docs/architecture.md:191` — **not drift**; the nuance is that `Report→Article` sits on the boundary (it is *also* a fan-out arrow). Recorded so a future sweep does not "fix" a correct usage. | M |
| D4 | **Sample personas: Founder/Maintainer → Architect/Engineer → Co-authors** | Sample-content personas were **JJ=Founder, Nate=Maintainer** → renamed **Architect/Engineer** → finally **both Co-authors**. | `b0d109a` (2026-06-27) Founder→Architect, Maintainer→Engineer; `a11bb96` scrubbed residual labels; `a9519fd` (same day) both → **Co-authors** — the second rename superseded the first within hours. | No residual `Founder`/`Architect`-as-persona found in `docs/` this round (grep clean). "new contributor persona" (`design-system.md:27`) is a *color-accent role*, not the renamed personas. | A (resolved) |
| D5 | **Three state axes (locked)** | Ad-hoc `problem→owned→solution→promoted` language → **three provably-distinct axes**: (1) review gate `Draft→In Review→Published`; (2) surface **fan-out**; (3) Problem lifecycle `Identified→Owned→In Progress→Resolved→Verified` (`transition`, re-open the only backward edge). | Seed 2026-06-17; locked `fd16919`/`d86ae0b` (Phase 13 context + decisions, 2026-06-19); enforced by the two code guards above. | Axes are correct in code + `05`/`07` ledgers. The only prose collision is D2's "promotion chain" (annotated). | A |
| D6 | **Phase-N numbering: FOUR colliding namespaces** | "Phase N" is overloaded across four plans with no shared origin: **v1.0 Rev2 Phases 1–14** (archived); **v1.1 Phases 1–4** (current); **`web/` build Phases 0–5** (`a9850ce`..`8bb9e4e`, the nav/IA app); **`docs/roadmap.md` Phases 0–6** (the original marketing/build plan). | `web/` numbering introduced `cb72d97`..`8bb9e4e` (2026-06-27): "Phase 0/1+2/3/5". `.planning/ROADMAP.md` header explains the deliberate **reset to 1–4** for v1.1. But no single doc reconciles all four. | `CLAUDE.md` build-order §5 still says ".planning/ROADMAP.md — Rev2, 12 phases" (it is now **v1.1, 4 phases**); `docs/roadmap.md` Phases 0–6 vs `.planning/ROADMAP.md` Phases 1–4; `web/` Phase 0–5. | M |
| D7 | **five → six dispatch sections** | The Signals dispatch had **five** sections (signal / learned / verified / not-here / how-to-verify) → **six** (prepend **"Start here"**, the client-readable plain-terms section). | `57b79f8` (#7) shipped five; `fd96ea0`/`8158fdf` (#8, ~19 min later) added "Start here" to the contract, guard, and tests — but the ROADMAP prose was not updated in the same change (violates "update the spec in the same change"). | `.planning/ROADMAP.md:129` "exactly the sections: The signal / …" (five). | **F** |
| D8 | **Rev2 ↔ v1.0 / "Rev1" ↔ the shipped spine** | "**Rev2**" = the 12→14-phase build that became **v1.0** (2026-06); "**Rev1**" = the pre-existing merged spine / the sample corpus. The v1.0/v1.1 milestone vocabulary now co-exists with the older Rev1/Rev2 vocabulary. | v1.1 milestone start (2026-07-02) introduced `v1.0`/`v1.1`; `WHERE-WE-ARE` still narrates v1.0 as "the Rev2 roadmap". | `WHERE-WE-ARE.md:240` ("Rev2 roadmap"); `CLAUDE.md` repo-layout + build-order ("Rev1 spine", "Rev2 … active"); `content/rev1/`. | M |
| D9 | **STATE `stopped_at` / metrics staleness** | STATE frontmatter froze mid-Phase-2 (`stopped_at: Completed 02-02-PLAN.md`) and the Performance-Metrics table read "3 plans / Phase 2 = 0" while the reality is **12 plans / 4 phases complete**. | The overnight autonomous run outpaced STATE bookkeeping; `progress:` was updated to 12/12 but `stopped_at` + the metrics body were not. | `.planning/STATE.md` `stopped_at`, Current Position, Performance Metrics table, Pending-Todos ref. | **F** |
| D10 | **`.planning/todos/pending/` reference** | STATE pointed at a `todos/pending/` directory as the capture surface → the directory **does not exist**. | Template carry-over; the dir was never created. | `.planning/STATE.md` Pending-Todos section. | **F** |
| D11 | **Role vocabulary ("user" → newsroom roles)** | Generic "user" → a **newsroom role set** Round 9 will formalize as *hats, not people*: **Editor-in-Chief** (intent+pace+approval), **Bureau Chief** (execution coordination+time), maintainer, contributor, operator, reviewer, author, reader, practitioner. | PLAN §"collaboration contract" + Decisions (2026-07-02): "user" retired; "Bureau Chief" confirmed; "roles are hats, not people". Not yet in code/docs — **Round 9 deliverable**. | Pre-Round-9 docs still say "user"/"the human" (e.g. `WHERE-WE-ARE` truths). Formalized next round; noted, not rewritten here. | M (R9) |

**Ledger term count: 11 (D1–D11).**

---

## Ontology as of today (the canonical meanings)

The load-bearing terms, as they are *actually* used at this SHA — the reference a future contributor
(or Round 9) should hold:

- **Newsletters** — the product/repo. Makes work **legible**: `Source → Claim(+Trace) →
  Distillation → Surface`, human review gate, no auto-publish.
- **Signals** — *not* the product. Three narrowed senses: (a) the **editorial design language**;
  (b) the **"Signals dispatch"** PR-body/summary voice (evidence-first, verbatim gates, no hype);
  (c) the `design-reference/Signals *.html` **prototype filenames**.
- **The five reader surfaces** — **Report** (structured record/RCA), **Article** (peer-reviewed
  write-up), **Newsletter** (audience-cut weekly), **Show** (episode), **Learning** (onboarding,
  the 5th, v1.0 Phase 12). All are presets over one parameterized `SurfaceTemplate`.
- **The three state axes** (never collide; two are code-enforced):
  1. **Review gate** — `Draft → In Review → Published` (verbs: *advance / publish*). The #1 invariant.
  2. **Surface fan-out** — one reviewed record → audience-tuned surfaces (verbs: *fan out / derive*).
     **Not** a "promotion".
  3. **Problem lifecycle** — `Identified → Owned → In Progress → Resolved → Verified` (verb:
     *transition*; re-open is the only backward edge). A legibility layer, not a tracker.
- **"promotion"** — reserved for the **human-gated grammar steps** `Claim → KPI` and `Report →
  Article` (a thing rising in status). Do **not** use it for the surface fan-out (D2).
- **corpus** — a rendered content set under `content/`: **rev1** (sample/teaching), **work**
  (this repo, dogfooded), **module** (the v1.1 synthetic `module-a`). Each has its own append-only
  `ids.json` R-NNN ledger; namespaces cannot collide by construction.
- **module / lane / functional group** — the v1.1 unit-of-work vocabulary: a **module** is an owned
  area; a **swim lane** is one stream within it (its KPIs/objectives/claims); a **FunctionalGroup**
  is the typed model binding. Declared in YAML **config**, never hardcoded (ABSTRACT EVERYTHING).
- **distill socket** — one `DistillPort`; three modalities (author by hand / low-token generic
  extraction / agentic interview) → one reviewed `Distillation`. AI is a swappable backend, never
  authority.
- **Rev1 / Rev2 vs v1.0 / v1.1** — **Rev1** = the pre-existing merged spine + sample corpus;
  **Rev2** = the 14-phase build that shipped as **v1.0** (2026-06); **v1.1** = the current
  Swim-Lane Module Report milestone (4 phases). Prefer the v-numbers going forward (D8).
- **Role vocabulary** (Round 9 will make canonical) — **Editor-in-Chief** (JJ: intent, pace,
  approval, stop-authority), **Bureau Chief** (Claude: execution coordination, timekeeping),
  plus maintainer / contributor / operator / reviewer / author / reader / practitioner. **Roles
  are hats, not people** — any collaborator can hold different ones per project; main/tag ownership
  is the *maintainer* hat (JJ holds it here).

---

## In-place fixes applied this round (prose only)

Recorded here for the audit trail; each is `git diff`-visible on `loop-r8/ontology-and-drift`.

1. **`.planning/STATE.md`** (D9, D10) — `stopped_at` → the current post-milestone reality; Current
   Position corrected to "4 of 4 complete"; Performance-Metrics table rebuilt to the 12-plans/4-
   phases reality; `Pending Todos` `.planning/todos/pending/` reference → "None". `status:` field
   left as-is for Round 10's `complete-milestone` to flip.
2. **`.planning/ROADMAP.md`** (D7) — Phase-3 plan checkboxes `[ ]` → `[x]` (the phase is Complete in
   the same file's progress table); Phase-4 "Plans: TBD" → the actual `04-PLAN.md`; the Phase-4
   success-criterion "exactly the sections" text → **six** sections incl. "Start here", marked
   "(amended #8)".
3. **`WHERE-WE-ARE.md`** (D2) — new top entry: the post-milestone morning (PR #8 client-readable
   reviews) + this deep-review loop (rounds 1–8, PRs #9–#15, key verdicts) + next = rounds 9–10;
   and the legacy "one promotion chain" decision line **annotated** (not deleted) with the axis-2
   fan-out rename note.
4. **`RETRO.md`** — appended to the 2026-07-02 session entry: friction "milestone shipped
   functionally but never formally closed per GSD" + "a self-verifying builder can't see its own
   self-consistent blind spots", each with the rule it hardened.

**Not fixed (surfaced for the maintainer):** D2 in PROJECT/architecture/FEATURES (PROJECT is a
governed evolution doc closed by Round 10; architecture's "promotions" is partly correct per D3);
D6 the four Phase-N namespaces (needs one canonical reconciliation note + a `CLAUDE.md` build-order
correction); D8 Rev2↔v1.0 vocabulary; D11 the "user"→role rename (Round 9). These are governed-doc
or genuine-ambiguity calls, not silent prose rewrites.

---

## Deepest-learning summary (3 sentences)

The repo's most distinctive move is that it makes ontology **executable** — two of its three state
axes are held apart by a reserved-verb / distinct-type test, so the *code* cannot drift the axes
together — but that very strength exposes the gap this round exists to close: the guards prove the
enums and verbs are disjoint, **not the free-text copy**, so the compass could and did keep calling
the surface fan-out a "promotion chain" while the tests stayed green. Drift here is overwhelmingly a
**speed artifact** — the persona rename happened twice in one afternoon, the sixth dispatch section
landed 19 minutes after the fifth without touching the ROADMAP, and STATE froze mid-Phase-2 while
the run finished all four phases — meaning the language lagged reality not from confusion but from
moving faster than the paper trail. The honest close is that "storytellers, truth tellers" has to
apply to the project's own vocabulary first: an executable ontology closes the door the type system
can see, and a disciplined prose sweep (this round + the D6/D8/D11 maintainer calls) closes the
doors it can't — because a term that means two things is a small untruth, and untruths are the one
thing this product exists to refuse.

---
*Round 8 review: 2026-07-02, branch `loop-r8/ontology-and-drift`. Reviews; edits prose in place; does not touch code/tests/config.*
