---
phase: 2
phase_name: "Module-scope Report composer"
project: "Newsletters"
generated: "2026-07-02"
counts:
  decisions: 6
  lessons: 4
  patterns: 3
  surprises: 3
missing_artifacts:
  - "02-UAT.md (no conversational UAT was run this phase)"
---

# Phase 2 Learnings: Module-scope Report composer

> Retroactively extracted (2026-07-02) from the phase paper trail (02-CONTEXT, 02-PATTERNS, four
> PLANs/SUMMARYs), the live code (`compose.py`, the `swimlane.py` endpoint additions, `test_compose.py`,
> `test_swimlane_endpoints.py`), and git history (`f682620`…`6aae29f`; the two mid-phase fixes
> `4031af1`/`efb635a`; squash-merged as `22396ce` PR #5).

## Decisions

### Δ is a derivation, never a Claim
The delta lives ONLY in `KpiItem.delta`/`.dir`; it is computed at compose time from two independently
content-addressed endpoints and is never itself minted as a `Claim`, never traced, never rendered as a
claim.

**Rationale:** A derived number that appears nowhere in the config is the milestone's #1 faithfulness
surface (Hole A). Keeping it out of the claim graph means it can never masquerade as sourced fact; its
honesty is enforced by the reproducibility test (recompute from endpoints) standing in for a trace.
**Source:** 02-CONTEXT.md §"The Δ contract", compose.py:22-26, 02-02-SUMMARY §Decisions

### Endpoints paired by reference, on the loader — not text-matched in the composer
The composer needs each KPI's two period endpoints, but the as-built `SectionBinding` buried them in a
flat `claims` list with no back-reference and ambiguous duplicate text. The pairing was added as an
additive `SectionBinding.kpi_endpoints` field populated by *referencing* the already-minted Claims.

**Rationale:** Deriving Δ by text-matching endpoints would be non-unique (the trap fixture repeats a
value across KPIs) and fragile (endpoint counts aren't recorded). An explicit, reference-only pairing
means a delta is only ever derived from two genuinely traced Claims — and adds zero mints, so the
read-anchored coverage identity is untouched.
**Source:** 02-PATTERNS.md "Endpoint-pairing finding", 02-01-SUMMARY, swimlane.py:131-146, 373-405

### `Surface.created = EPOCH_ZERO` passed explicitly (the composed-surface analog has the bug)
`compose_module_report` passes `created=EPOCH_ZERO` explicitly; it does NOT inherit the `now()` default.
The composed-surface precedents (`capture.build_report`, `worksurface.build_work_report`) both inherit
`now()` and are therefore NOT byte-stable — the analog carries the exact bug this phase must not copy.

**Rationale:** Byte-identical `model_dump_json` across two composes (SITE-06 lineage) is impossible if
`created` reads a clock. This is the first composed surface to be byte-stable; it treats the analog as
a determinism trap, not a copy target.
**Source:** 02-PATTERNS.md "DETERMINISM TRAP", compose.py:394, `test_two_composes_are_byte_identical`

### Ledger: caller-owns-save (compose is disk-write-free)
`compose_module_report` reads/assigns the in-memory `Ledger` via `ref_for` but never calls `save()`;
persistence is deferred to Phase 3's `build_module_site` (mirroring `build_work_site`).

**Rationale:** Keeping compose free of disk writes keeps its tests hermetic and byte-stable, and
mirrors how `Site.from_surfaces` reads/extends the in-memory ledger while the caller owns the single
write. The ref comes SOLELY from the reused `site.Ledger` — never an inline `R-NNN` format, never a
`len()+1` ordinal (kept out of docstrings too, so a grep-based ref-format audit is unambiguous).
**Source:** 02-03-PLAN §LEDGER DECISION, 02-03-SUMMARY, compose.py:305-325

### Sourced-or-omit quote wired via kwargs, not a SectionBinding extension
The owner/manager quote flows through explicit `quote: Claim | None` + `owner: str | None` keyword
params — a parallel structure the caller supplies — because `swimlane.py` was frozen after Plan 02-01.
A `QuoteBlock` is emitted only from a content-addressed quote claim; absent → omit + `missing[]` note;
unowned → `"unassigned"` honesty marker. Quote text is never fabricated.

**Rationale:** Extending `SectionBinding` again would touch the frozen loader spine; a parallel kwarg
keeps the composer loader-agnostic and the swimlane untouched (a CONTEXT discretion resolved cleanly).
**Source:** 02-03-SUMMARY §Decisions, compose.py:265-303, `test_unowned_and_sourced_quote_honesty`

### Δ arithmetic via `Decimal` + a single regex parser
`compute_delta` parses each endpoint with one regex (`^\s*([+-]?\d+(?:\.\d+)?)\s*(\S*)\s*$`), does the
arithmetic in `Decimal` once, then formats once: an int pair renders `"+10"` (not `"+10.0"`), floats
strip trailing zeros, a trailing unit is preserved only when BOTH endpoints carry the SAME unit.

**Rationale:** `Decimal` avoids binary-float artifacts and is deterministic; formatting once (no
rounding inside a format string) keeps the output reproducible. Conservative unit handling never
invents a unit.
**Source:** 02-02-SUMMARY §Decisions, compose.py:74-146

---

## Lessons

### Over-firing honesty is ALSO unfaithful — disclosure must track declared-but-unmet promises
The false-disclosure lesson, learned live across `4031af1` → `efb635a`. Fix 1 added a `missing[]` note
for any KPI with a single endpoint (COMP-02 letter: an absent endpoint must be disclosed). But because
a point-in-time `value:` KPI still carried one endpoint, that note then fired on EVERY point-in-time
KPI — a disclosure claiming a "declared movement" that was never promised. Fix 2 moved the boundary
into the loader: only the `values:` (movement) form pairs endpoints, so a `value:` KPI carries zero
and never triggers a movement note.

**Context:** A note that fires when nothing was promised erodes trust exactly as a silent omission
does — noise is unfaithful too. The right predicate for "disclose this gap" is *was a movement
declared and left unmet*, not *is an endpoint missing*. And the declaration distinction (`values:` vs
`value:`) lives in the loader, so the fix belongs there, not as a patch in the composer.
**Source:** commits `4031af1` (symptom patch) + `efb635a` (semantic resolution), compose.py:196-226,
swimlane.py:360-368

### `Surface.created` defaulting to `now()` is a live trap every composer inherits
The `semantic.py` `created: datetime = Field(default_factory=_utcnow)` default silently defeats
byte-determinism for any surface builder that forgets to pass `created`. Two existing builders
(`capture.build_report`, `worksurface.build_work_report`) already carry this latent non-determinism.

**Context:** This is a shared foot-gun, not a compose-specific one; the fix is per-caller
(`created=EPOCH_ZERO`) because `semantic.py` is on the forbidden list. Any future composer must pass
`created` explicitly or inherit the bug. Worth a future semantic-layer change (make `created`
required, or default it to a sentinel) once the freeze lifts.
**Source:** 02-PATTERNS.md "No Analog Found" / "DETERMINISM TRAP", compose.py:394

### The trust-guard suite IS the deliverable — enforce with adversarial planted cheats, not docstrings
Every guarantee is proven by a test that plants the violation and asserts it is caught: a zero-trace
claim AND an un-addressed-trace claim routed to `missing[]`; a poisoned `ProseBlock("we shipped 42
features")` caught by the numeral scan; a direct `Review(state=PUBLISHED,…)` raising. A green positive
alone would be vacuous.

**Context:** Pitfall 10 — guarantees enforced by docstrings drift; guarantees enforced by a test that
demonstrably fires hold for every future edit. The suite also asserts the protected gate files are
byte-untouched via `git diff --exit-code` (a RED guard is fixed in the composer, never by relaxing a
gate).
**Source:** 02-04-PLAN, `test_compose.py:215-257, 288-306, 534-554`

### A test fixture can drift from the code it exercises without turning red
`test_compose.py`'s `_build_load` models a point-in-time KPI as a one-element endpoint list and
comments it "point-in-time, no delta" — but after `efb635a` the live loader emits point-in-time as
ZERO endpoints, and a one-element list now fires a "declared movement" note. The suite still passes
because no test asserts the note's absence, so the drift went unnoticed until this review.

**Context:** The compose-level zero-endpoint arm — the exact behavior `efb635a` established — is
consequently unguarded (see 02-VALIDATION). A fixture whose *intent comment* no longer matches the
code's behavior is a silent validation gap; the lesson is to pin the semantically-load-bearing arm
directly, not assume a passing suite means the intended path is covered.
**Source:** this-round live drive, `test_compose.py:123-142`, commit `efb635a`

---

## Patterns

### Adversarial planted-cheat test (plant the violation, assert it's caught)
A guard test's positive half (every real output satisfies the predicate) is paired with an adversarial
half (a hand-built bad object is rejected/routed by the SAME predicate), so the positive pass is
provably non-vacuous. Used for Hole B (planted zero-trace + un-addressed claims), Hole A (poisoned
ProseBlock), and no-auto-publish (direct PUBLISHED review raises).
**When to use:** Any invariant whose whole value is that it catches violations.
**Source:** `test_compose.py`, mirrors Phase-1's "prove-it-fires" halves

### Kind-agnostic composition seam (proven by a second-kind test)
The composer consumes `SectionBinding[]` with no knowledge that "lanes" exist; a `SectionBinding`
representing a different conceptual kind (a risk register) composes with zero composer change. The
seam is proven by composing that second kind, not merely asserted.
**When to use:** Any transform that should generalize over a family of structurally-identical inputs.
**Source:** compose.py:340-366, `test_kind_agnostic_seam_second_kind`

### Reference-not-re-mint parallel-array pairing
An additive `list[list[Claim]]` field appended in lockstep with an existing list, holding the SAME
Claim objects already minted elsewhere (object identity, `is`), so it adds a pairing without adding a
mint — the coverage identity stays intact and is re-proven by an object-identity test.
**When to use:** Exposing a relationship over already-minted atoms without disturbing a coverage
invariant.
**Source:** swimlane.py:373-405, `test_endpoints_are_references_not_re_mints`

---

## Surprises

### The gate holes existed in shipped code long before this phase
Holes A (un-gated non-`ClaimsBlock` numerals) and B (un-addressed-trace free pass) were research
findings about the *existing* pipeline, not new risks this phase introduced. Phase 2 closes them **at
the composer** with new adversarial guards while leaving `faithfulness.py`/`coverage.py` untouched —
the holes were latent in the spine since v1.0's distill phases, surfaced by the research pass.

**Impact:** Framed the whole phase as "add guards that make the existing cheat RED," not "fix a bug I
just wrote" — and explains why the forbidden list is so strict (the temptation was to weaken an
existing gate to go green).
**Source:** 02-CONTEXT.md §"Trust guards", 02-PATTERNS.md "No Analog Found", RESEARCH Holes A/B

### The Δ contract was rewritten twice AFTER the trust-guard suite already passed
The 13-test suite (02-04) landed green at 605 tests — and then two fixes (`4031af1`, `efb635a`)
changed the disclosure semantics without touching a single test. The suite was robust enough to
absorb a semantic change silently, which is both reassuring (the guards weren't over-fit to one
disclosure form) and a warning (the change slipped past the suite because the specific arm wasn't
pinned — see the fixture-drift lesson).

**Impact:** Confirmed the guards test *invariants* not *exact strings*, but also exposed the one
unpinned branch. The drift (silent → over-disclosing → movement-form-only) is the phase's real story.
**Source:** git order `6aae29f` (tests) → `4031af1`/`efb635a` (fixes), 02-04-SUMMARY (605 green)

### GSD state tooling couldn't parse this milestone's phase-numbering format
During the loop, the SDK/verb layer that reads phase state had trouble with this milestone's
`0N-name` phase directory format versus the older numbering the tooling expected — a machinery
friction, not a product defect, surfaced while assembling the retroactive artifacts.

**Impact:** Reinforces the loop's design principle that the round artifacts + STATE file (not the
tooling's live parse) are the durable memory; the human-readable compass survives a tooling parse
gap. Logged for RETRO.
**Source:** deep-review loop PLAN.md §"Amendments", this-round assembly friction

---
*Learnings extracted: 2026-07-02 (retroactive, deep-review loop Round 2)*
*Extractor: Claude (Bureau Chief)*
