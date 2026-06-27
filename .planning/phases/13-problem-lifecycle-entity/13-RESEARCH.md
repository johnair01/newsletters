# Phase 13: Problem Lifecycle Entity (A2) - Research

**Researched:** 2026-06-19
**Domain:** Typed Pydantic entity design above the `semantic.py` spine; state-machine enum + human-gated transition log; import-boundary / "no-write-back" proof by test; terminology-axis distinctness
**Confidence:** HIGH

> This is a design-VALIDATION research pass against the LIVE codebase. The decisions are locked in
> `13-CONTEXT.md`; every finding below confirms or refines them against actual code, with file:line
> citations. No production code was written. No new dependency, no external call, no AI.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. **A new typed module `src/newsletters/problem.py`** — Pydantic, AI-free, imports `semantic.Source`/
   `Trace` only (leaf/acyclic boundary; NOT in `semantic.py`); NEVER imports distill-AI/network.
   `Problem` is a first-class entity ABOVE `Source`.
2. **`ProblemState` enum** = IDENTIFIED → OWNED → IN_PROGRESS → RESOLVED → VERIFIED — a DISTINCT type
   from `ReviewState`. A test proves the two enums share no member values and are different types.
3. **`Problem` aggregates ≥1 traced `Source`** — carries references/Traces to constituent Sources so
   every Problem stays traceable to evidence. Zero sources is invalid (≥1 required).
4. **Human-gated `transition(to, by, note=...)`** — records each transition (from→to, actor,
   timestamp/note); refuses an invalid ladder jump or a transition with no actor; NEVER auto-mutates.
   The transition log is the legible record. Distinct from the review gate's publish/review API.
5. **NO write-back / spine boundary (PROB-03, hard constraint):** `problem.py` has ZERO
   external-system/network imports; NO method writes to Jira/ADO or mutates external state. Solving is
   external. PROVEN BY TEST: (a) no network/external import reachable from `problem.py`; (b) Problem API
   exposes no write-back/export-to-tracker path; (c) `semantic.py` spine is unchanged.
6. **Scope:** the typed Problem entity + ProblemState ladder + human-gated transition + boundary +
   terminology-distinctness + no-write-back tests + a small dogfood Problem. **PROB-02 (queryable
   portfolio) + PROB-04 (board surface) are Phase 14 — do NOT build rendering/aggregation here.**
   No AI; no new dependency.

### Claude's Discretion
- The exact ladder rule (strictly sequential vs. allow re-open) — recommended below (Question B).
- The exact field shape for referencing constituent Sources (Trace list vs. source-id list) —
  recommended below (Question A).
- Test file naming/placement and the exact assertions — recommended below (Questions C/D).
- The specific real Source the dogfood Problem aggregates — recommended below (Question E).

### Deferred Ideas (OUT OF SCOPE)
- **PROB-02** — queryable/aggregatable portfolio (group/count/age by node/area; recurrence). Phase 14.
- **PROB-04** — problem-board surface rendering alongside the gate-state board. Phase 14.
- Any rendering, `render.py`/`site.py`/`templates.py` touch, HTML output, or cross-problem query API.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROB-01 | A first-class `Problem` above `Source`, aggregating ≥1 traced `Source`, carrying its own lifecycle ladder (`Identified→Owned→In Progress→Resolved→Verified`), kept rigorously distinct from the review gate and the fan-out chain | Question A (shape), Question B (ladder), Question D (distinctness test). Mirrors `semantic.Source`/`Trace` (semantic.py:49-184) and the leaf-module pattern (locators.py:1-19). |
| PROB-03 | *(hard constraint)* Legibility layer, not an execution tracker — no write-back to Jira/ADO; solving stays external/operator-owned (preserves the `semantic.py` boundary at semantic.py:22-24); transitions human-gated, never auto-mutated | Question C (boundary proof by test, three sub-proofs), Question B (actor-required transition). Mirrors the AI-isolation guard idiom (test_ai_optional.py:117-158, .importlinter:23-36). |

> PROB-02 and PROB-04 are **Phase 14** (REQUIREMENTS.md:139-142, ROADMAP.md:364-376) — confirmed out
> of scope for Phase 13. See Question F.
</phase_requirements>

---

## Summary

Phase 13 adds one new leaf module — `src/newsletters/problem.py` — carrying a `Problem` Pydantic
entity, a `ProblemState` `StrEnum` ladder, and a single human-gated `transition()` method that appends
to an immutable `TransitionEvent` log. It sits **above** `Source` and imports only stdlib + Pydantic +
`semantic` (`Source`/`Trace`), exactly mirroring how `promote.py` imports from `semantic` (promote.py:18-24)
and how `locators.py` stays a stdlib+Pydantic leaf (locators.py:1-19, 21-25). The spine (`semantic.py`)
is untouched: `Problem` references Sources, never mutates them.

The codebase already contains every pattern this phase needs, so confidence is HIGH and risk is LOW.
The review gate (`ReviewState` + `Review._published_requires_satisfied_policy`, semantic.py:250-287)
is the template for "human-gated, validator-enforced, no-auto path." The AI-isolation guard
(`.importlinter` + `test_ai_optional.py`) is the template for "prove a forbidden import never reaches a
module." The `promote.py` human-gated transforms (promote.py:28-94) are the template for "actor-required,
refuse-on-invalid." Nothing new needs inventing — Phase 13 is composition of existing idioms.

**Primary recommendation:** Build `problem.py` as a leaf module with `Problem`, `ProblemState`,
`TransitionEvent`; reference constituent Sources by a **list of `semantic.Trace`** (reusing the existing
evidence-pointer type) validated to length ≥1; make the ladder **sequential with explicit re-open**
(Resolved/Verified → In Progress allowed, every other backward/skip move refused); name the verb
`transition`; and add `tests/test_problem.py` with the three PROB-03 boundary proofs + the PROB-01/guard
distinctness proof + a dogfood Problem aggregating the real `session-rev1` Source. Build NO rendering.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `Problem` entity + `ProblemState` ladder | Core / Backend (`src/newsletters/problem.py`) | — | Pure typed domain model; belongs beside `semantic.py`/`promote.py` in the AI-free core. |
| Aggregating ≥1 traced `Source` | Core (`Problem` references `semantic.Trace`) | — | Evidence-pointer reuse; `Source` lives in `semantic.py`, `Problem` references it without mutation. |
| Human-gated `transition()` | Core (`Problem.transition`) | — | A pure in-memory state transition + append to a log; mirrors `Surface.approve/publish` (semantic.py:566-588). |
| No-write-back / spine-boundary proof | Test tier (`tests/test_problem.py`) + lint (`.importlinter`) | — | Static + runtime guard, mirroring `test_ai_optional.py` (no AI edge → no external-system edge). |
| Cross-problem query / portfolio | **Phase 14 (DEFERRED)** | — | A1 cannot aggregate; PROB-02 builds it. NOT this phase. |
| Board rendering | **Phase 14 (DEFERRED)** | — | PROB-04 renders alongside the gate-state board. NOT this phase. |

---

## Per-Question Findings

### A. Placement + shape — CONFIRMED, with field recommendations

**Placement: a NEW `src/newsletters/problem.py` leaf module.** [VERIFIED: codebase grep]

The repo's import discipline is explicit and load-bearing. `locators.py:1-19` documents the leaf rule:
"this module imports ONLY stdlib + pydantic. It must NEVER import from `.semantic`, the `.distill`
package, or `.capture`." `problem.py` is the *next tier up*: it may import `semantic` (the spine) but
nothing AI/network. The precedent is `promote.py`, which imports `Claim, ClaimsBlock, ProseBlock, Review,
Surface` from `.semantic` (promote.py:18-24) and `Kpi, KpiStatus` from `.models` — a clean acyclic edge
`promote → semantic → {locators, templates}`. `problem.py` adds the parallel edge `problem → semantic`.
This is acyclic (semantic.py imports only `.locators` + `.templates`, semantic.py:36-37 — never `.promote`,
never a hypothetical `.problem`), so no circular-import risk.

**Why not in `semantic.py`:** the spine docstring (semantic.py:1-25) is scoped to "capture, trust,
publish" — the Source→Claim→Distillation→Surface model + the review gate. A Problem is a NEW axis *above*
that; keeping it in its own module keeps the spine focused (CONTEXT.md decision 1) and keeps the
distinctness obvious.

**Recommended `Problem` shape** (mirrors the `BaseModel` style of `Source`, semantic.py:49-83, and
`Review`, semantic.py:256-287):

```python
# Source: pattern mirrors semantic.Source (semantic.py:49-83) + semantic.Review (semantic.py:256-287)
class Problem(BaseModel):
    id: str
    title: str
    state: ProblemState = ProblemState.IDENTIFIED          # the CURRENT rung (starts at the bottom)
    evidence: list[Trace] = Field(default_factory=list)    # ≥1 traced Source — the constituent record
    log: list[TransitionEvent] = Field(default_factory=list)  # the immutable from→to/actor/when record
    opened: datetime = Field(default_factory=_utcnow)

    @field_validator("evidence")
    @classmethod
    def _at_least_one_source(cls, v: list[Trace]) -> list[Trace]:
        if not v:
            raise ValueError(
                "A Problem must aggregate >=1 traced Source — every problem traces to evidence. "
                "A Problem with zero sources is not legible; add a Trace to a constituent Source."
            )
        return v
```

**Field recommendation — reference Sources by `list[semantic.Trace]`, NOT a bare `list[str]` of ids.**
[VERIFIED: codebase grep] Rationale:
- `Trace` is the *existing* evidence-pointer type (semantic.py:86-184): `source_id` + `locator` + `span`
  + content-address fields. Reusing it means a Problem points at its constituent ticket/passdown/RCA the
  SAME way a `Claim` points at its evidence (`Claim.evidence: list[Trace]`, semantic.py:191). One
  evidence grammar across the codebase, not two.
- It carries `content_hash`/offsets, so a Problem's evidence is content-addressed and drift-aware *for
  free* (`Trace.is_stale_against`, semantic.py:177-184) — the same property the dogfood corpus relies on
  (dogfood.py:118-152). PROB-04's "links back to constituent Source records/claims" (REQUIREMENTS.md:74)
  is then *prepared* here with zero extra work; rendering it is Phase 14.
- A bare `list[str]` would re-invent a weaker pointer and break the `is_traced`/staleness story.

Add a convenience property mirroring `Claim.is_traced` (semantic.py:195-197) and
`Surface._published_claims` (semantic.py:545-550):

```python
@property
def source_ids(self) -> list[str]:
    """The distinct Source ids this Problem aggregates (for the Phase-14 board's back-links)."""
    return list(dict.fromkeys(t.source_id for t in self.evidence))
```

**Confidence: HIGH** — every element has a live precedent in `semantic.py`.

---

### B. The `ProblemState` ladder + human-gated `transition` — CONFIRMED, with ladder rule

**The enum** (a `StrEnum`, exactly like `ReviewState`, semantic.py:250-254; `StrEnum` is stdlib ≥3.11
and already used, semantic.py:31 — the `.venv` is Python 3.12.3 [VERIFIED: `.venv/bin/python --version`]):

```python
# Source: pattern mirrors semantic.ReviewState (semantic.py:250-254) — DISTINCT member VALUES (see Q.D)
class ProblemState(StrEnum):
    IDENTIFIED = "identified"
    OWNED = "owned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    VERIFIED = "verified"
```

> **Terminology-distinctness note:** `ReviewState` uses `"draft"/"in_review"/"published"`
> (semantic.py:251-253). `ProblemState`'s values `"identified"/"owned"/"in_progress"/"resolved"/"verified"`
> share **no** member value with it. Enforced by the Question-D test. Note `IN_PROGRESS = "in_progress"`
> vs `IN_REVIEW = "in_review"` — distinct strings; the test must assert value-set disjointness, not just
> name difference.

**The `transition` API** (the reserved axis-3 verb per the guard, promotion-terminology-guard.md:30 and
CONTEXT.md:22-23 — NOT promote/publish/advance/fan-out/derive):

```python
# Source: pattern mirrors Surface.approve/publish human-gated transforms (semantic.py:566-588)
def transition(self, to: ProblemState, by: str, note: str = "") -> "Problem":
    """Record a human-gated lifecycle transition. Never auto-advances.

    Refuses (raises ValueError) on: an empty actor (`by`), or an illegal ladder move
    (see _LADDER). On success, appends a TransitionEvent(from, to, by, note, at) to `log`
    and sets `state = to`. The log is the legible record of the lifecycle.
    """
    if not by:
        raise ValueError(
            "transition() requires an explicit human actor (`by`). A Problem's state never "
            "auto-advances — like the publish gate, every move is human-gated."
        )
    if to not in _LADDER[self.state]:
        raise ValueError(
            f"Illegal lifecycle move {self.state.value!r} -> {to.value!r}. "
            f"Allowed from {self.state.value!r}: "
            f"{sorted(s.value for s in _LADDER[self.state])}."
        )
    self.log.append(TransitionEvent(from_state=self.state, to_state=to, by=by, note=note))
    self.state = to
    return self
```

with a supporting immutable event:

```python
class TransitionEvent(BaseModel):
    from_state: ProblemState
    to_state: ProblemState
    by: str
    note: str = ""
    at: datetime = Field(default_factory=_utcnow)
```

The `not by` guard mirrors `Surface.approve`'s `if not reviewer: raise ValueError("approve() requires a
reviewer.")` (semantic.py:568-569) — the same "no actor → refuse" idiom. Note: a `_utcnow()` helper
identical to semantic.py:40-41 should be defined locally in `problem.py` (don't import a private from
semantic; keep the leaf clean — it's two lines).

**Ladder rule recommendation: SEQUENTIAL forward, with EXPLICIT re-open.** [CITED:
a2-problem-lifecycle-decision.md:42-55] The A2 note frames the entity as the legible *record* of a
real-world lifecycle, not an idealized one. Real bottlenecks reopen: a "Resolved" problem fails
verification, a "Verified" fix regresses. A strictly one-way ladder would force operators to fabricate a
new Problem id (losing the history that makes it legible) — the opposite of the legibility goal. So:

```python
# Forward one rung at a time; re-open is the ONLY backward move, and only from the "done" rungs.
_LADDER: dict[ProblemState, set[ProblemState]] = {
    ProblemState.IDENTIFIED:  {ProblemState.OWNED},
    ProblemState.OWNED:       {ProblemState.IN_PROGRESS},
    ProblemState.IN_PROGRESS: {ProblemState.RESOLVED},
    ProblemState.RESOLVED:    {ProblemState.VERIFIED, ProblemState.IN_PROGRESS},  # re-open
    ProblemState.VERIFIED:    {ProblemState.IN_PROGRESS},                          # regression re-open
}
```

This refuses skips (Identified → Resolved), refuses arbitrary jumps backward (Verified → Identified), but
allows the two real re-open paths. The re-open is still a *recorded* human transition (it lands in the
log with an actor + note), so the legibility property holds: the lifecycle's bumps are visible, not erased.

If the planner/discuss prefers a stricter MVP, a strictly-forward ladder (drop the two re-open edges) is a
one-line change and still satisfies all three success criteria; the recommendation above is the more
honest model and is what the A2 "legible record of the real lifecycle" framing argues for. **[ASSUMED]**
that operators want re-open — flag for confirmation (Assumptions Log A1).

**Confidence: HIGH** on the API shape (direct `Surface.approve/publish` analog); **MEDIUM** on the
re-open rule (a defensible design call, flagged for confirmation).

---

### C. The no-write-back / spine-boundary PROOF (PROB-03 hard constraint) — three test designs

The codebase already proves a structurally identical property — "no AI import is reachable from core" —
via two complementary guards (test_ai_optional.py:1-17 explains why neither alone suffices). Phase 13
reuses that exact playbook for "no external-system/network import is reachable from `problem.py`." Three
sub-proofs, mirroring the three clauses of CONTEXT.md decision 5:

**(a) No network/external-system import reachable from `problem.py`.** [VERIFIED: codebase pattern at
test_ai_optional.py:143-158, .importlinter:23-36]

Two layers, like the AI guard:
- *Static layer* — extend `.importlinter` with a SECOND `forbidden` contract,
  `forbid-external-write-in-problem`, whose `source_modules = newsletters.problem` and
  `forbidden_modules` lists the network/external-system stdlib + would-be-tracker packages, e.g.
  `socket`, `http`, `http.client`, `urllib`, `urllib.request`, `ftplib`, `smtplib`, `subprocess`,
  `requests` (and any Jira/ADO SDK names). `include_external_packages = True` is already set
  (.importlinter:21). The existing `test_import_linter_contract_holds` (test_ai_optional.py:117-137)
  runs `lint-imports` and asserts exit 0 — it will cover the new contract automatically. *(Caveat: a
  `forbidden` contract on `socket` etc. catches a DIRECT or transitive import edge; because `problem`
  imports only `semantic` → `{locators, templates}` and Pydantic, the transitive set is small and known
  AI/network-free — verify by running `lint-imports` once the module exists.)*
- *Runtime layer* — a subprocess test mirroring `test_core_import_loads_no_ai_module`
  (test_ai_optional.py:143-158): `import newsletters.problem`, then assert none of a
  `FORBIDDEN_MODULES` set (`socket`, `http`, `urllib`, `ftplib`, `smtplib`, `requests`, `subprocess`) is
  in `sys.modules`. Run with `PYDANTIC_DISABLE_PLUGINS=true` and `cwd=REPO_ROOT` exactly as the AI test
  does (test_ai_optional.py:154-158), so we measure OUR import graph, not the ambient `.venv`.

**(b) The Problem API exposes NO write-back/export-to-tracker/mutate-external method.** [VERIFIED:
codebase pattern]

This is a positive-space assertion: enumerate `Problem`'s public callable surface and assert it contains
ONLY the sanctioned methods. Mirrors the spirit of `test_pyproject_dependency_boundary`
(test_ai_optional.py:76-111), which asserts an allowed-set rather than just a forbidden-set.

```python
def test_problem_api_has_no_write_back_method() -> None:
    public = {n for n in dir(Problem) if not n.startswith("_")}
    # the ONLY mutating/behavioral method is transition(); everything else is data/derived.
    forbidden_substrings = ("export", "push", "sync", "write", "send", "post", "upload",
                            "jira", "ado", "devops", "remote", "publish")
    offenders = {n for n in public if any(s in n.lower() for s in forbidden_substrings)}
    assert not offenders, f"Problem exposes a write-back/export path: {offenders}"
    assert "transition" in public  # the one sanctioned mutator
```

This is a *standing guard*: if a future phase adds `export_to_jira`, the test fails loudly — encoding the
PROB-03 hard constraint as a durable rule, not a vibe (per CLAUDE.md's "encode durable fixes as guards").

**(c) The `semantic.py` spine is UNCHANGED (Problem sits above; it does not mutate
Source/Distillation/Surface or the review gate).** [VERIFIED: codebase pattern]

Two assertions:
- *No mutation by construction* — a test that builds a `Problem` from a real `Source`, takes
  `source.content_hash()` before, runs a full `transition()` sequence, and asserts the Source's hash +
  fields are byte-identical after. Because `Problem.evidence` holds `Trace`s (which carry `source_id`,
  not the `Source` object) and `transition` only appends to `log` + sets `self.state`, there is no path
  to the Source — the test makes that explicit.
- *Spine import-direction unchanged* — assert `semantic.py` does NOT import `problem` (keeps the
  dependency one-way: `problem → semantic`, never the reverse). A simple source-text assertion (mirroring
  `test_openpyxl_loader_has_no_toplevel_openpyxl_import`, test_ai_optional.py:284-304): read
  `semantic.py` and assert no `import` line references `problem`. This guarantees the spine is oblivious
  to the new layer.

**The "human-gated, never auto-mutated" test** (the CONTEXT-required proof that no code path advances
state without an explicit actor): assert `Problem(...).transition(to=OWNED, by="")` raises ValueError
(empty actor refused), and assert the only way `state` changes is through `transition` (there is no
setter, no auto-advance method) — the API-surface test (b) already proves `transition` is the sole
mutator, and this test proves `transition` itself refuses an actor-less call. Together they close the
"never auto-mutated" guarantee — the direct analog of `test_published_without_approval_is_rejected`
(test_semantic.py:67-69).

**Confidence: HIGH** — all three sub-proofs are line-for-line adaptations of shipped, green tests.

---

### D. Terminology-distinctness test (PROB-01 / the guard) — design

The guard (promotion-terminology-guard.md:31-34) requires a test asserting the lifecycle ladder type is
distinct from the surface-gate type, with no shared member and no shared verb. [VERIFIED: codebase]

```python
# Source: enums at semantic.py:250-254 (ReviewState) and problem.py (ProblemState, new)
def test_problemstate_distinct_from_reviewstate() -> None:
    assert ProblemState is not ReviewState                       # different TYPES
    assert not issubclass(ProblemState, ReviewState)             # not a subtype either way
    prob_values = {m.value for m in ProblemState}
    review_values = {m.value for m in ReviewState}
    assert prob_values.isdisjoint(review_values), (
        f"axis collision: shared state value(s) {prob_values & review_values}"
    )
    prob_names = {m.name for m in ProblemState}
    review_names = {m.name for m in ReviewState}
    assert prob_names.isdisjoint(review_names), (
        f"axis collision: shared member name(s) {prob_names & review_names}"
    )

def test_lifecycle_verb_collides_with_no_axis_verb() -> None:
    # axis-3 verb is `transition`; it must not appear as a review-gate or fan-out/promote verb.
    from newsletters import semantic, promote
    reserved_elsewhere = {"publish", "approve", "open_pull_request",   # review gate (semantic.py)
                          "promote_claim_to_kpi", "promote_report_to_article",  # promote.py
                          "fan_out", "derive"}                          # fan-out chain
    assert "transition" not in reserved_elsewhere
    # and the Surface gate does NOT grow a `transition` verb, nor Problem a gate verb:
    assert not hasattr(semantic.Surface, "transition")
    assert "transition" in {n for n in dir(Problem) if not n.startswith("_")}
    for gate_verb in ("publish", "approve", "open_pull_request"):
        assert not hasattr(Problem, gate_verb), f"Problem must not reuse the gate verb {gate_verb!r}"
```

Note the value check matters precisely because `ProblemState.IN_PROGRESS = "in_progress"` is *adjacent*
to `ReviewState.IN_REVIEW = "in_review"` — close but disjoint; the test makes the disjointness explicit
rather than relying on eyeballing. This directly enforces success-criterion 2 (ROADMAP.md:359).

**Confidence: HIGH.**

---

### E. Dogfood example — CONFIRMED (entity-only; NO rendering)

The repo's dogfood module already builds real `Source`s with verbatim transcripts and content-addressed
traces (dogfood.py:214-417). The cleanest real Problem to model is a genuine build problem from THIS
project's own history, aggregating an existing dogfood Source. Recommended: a small standalone example
function (place it in `tests/test_problem.py` as the end-to-end test, OR a tiny `_dogfood_problem()` in
`problem.py` guarded as example-only — recommend the **test**, to avoid widening `problem.py`'s surface
and to keep the module a pure type module):

```python
# Source: reuses the real session-rev1 Source shape (dogfood.py:361-368) + Trace.from_source (semantic.py:126-170)
def test_dogfood_problem_end_to_end() -> None:
    # A real problem from the build: "the Locator union risked a circular import" (locators.py:5-16).
    src = Source(
        id="session-rev1",
        context="claude-code",
        transcript="Rev1 end-to-end: the Locator union risked a circular import "
                   "semantic->distill->semantic; resolved by making locators a leaf module.",
    )
    span = "the Locator union risked a circular import"
    start = src.transcript.find(span)
    evidence = [Trace.from_source(src, start, start + len(span))]

    prob = Problem(id="prob-circular-import",
                   title="Locator union risked a circular import",
                   evidence=evidence)                       # >=1 source enforced
    assert prob.state is ProblemState.IDENTIFIED
    prob.transition(ProblemState.OWNED, by="Claude", note="picked up during Rev1")
    prob.transition(ProblemState.IN_PROGRESS, by="Claude")
    prob.transition(ProblemState.RESOLVED, by="Claude", note="moved Locator to a leaf module")
    prob.transition(ProblemState.VERIFIED, by="JJ Airuoyo", note="import graph acyclic; tests green")

    assert prob.state is ProblemState.VERIFIED
    assert [e.to_state for e in prob.log] == [
        ProblemState.OWNED, ProblemState.IN_PROGRESS, ProblemState.RESOLVED, ProblemState.VERIFIED]
    assert prob.source_ids == ["session-rev1"]              # traceable to evidence (PROB-04 prep)
    # the evidence stays content-addressed + non-stale against the live source (drift-aware, free):
    assert evidence[0].is_addressed and not evidence[0].is_stale_against(src)
```

This proves the entity end-to-end (aggregation + ≥1 enforcement + ladder + human-gated log + traceability)
with **zero rendering** — exactly the Phase-13 boundary. The actor on the VERIFIED step is a *peer*
(`"JJ Airuoyo"`, dogfood.py:48), echoing the review gate's peer-review ethos without reusing its API.

**Confidence: HIGH.** **[ASSUMED]** the specific problem chosen is illustrative — any real Source works;
the planner may pick another (Assumptions Log A2).

---

### F. Scope confirmation — PROB-02 / PROB-04 are Phase 14 (CONFIRMED)

[VERIFIED: REQUIREMENTS.md:139-142, ROADMAP.md:349-376]

- REQUIREMENTS.md:139-142 maps PROB-01 + PROB-03 → Phase 13; PROB-02 + PROB-04 → Phase 14.
- ROADMAP.md:354 lists Phase 13 requirements as exactly `PROB-01, PROB-03`.
- ROADMAP.md:364-376 (Phase 14) owns the queryable portfolio (group/count/age, recurrence) and the
  problem-board surface, and lists `Depends on: Phase 9 (site IA / board rendering), Phase 13 (Problem
  entity)`. The dependency arrow is one-way: Phase 14 needs the Phase-13 entity; Phase 13 needs nothing
  from Phase 14.

**Phase-14 work that must NOT leak into Phase 13 (risk flags):**
1. **Any aggregation/query API on a *collection* of Problems** (e.g. `group_by_node`, `count_by_state`,
   `age`, recurrence detection). The `source_ids` property on a *single* Problem is fine (it's
   single-entity traceability for PROB-01); a cross-Problem query function is PROB-02.
2. **Any touch of `render.py` / `site.py` / `templates.py` / `site.from_surfaces`** — that is the board
   surface (PROB-04). Phase 13 produces no HTML and registers no template.
3. **A "ProblemBoard"/"portfolio" container type** — defer. Phase 13 ships individual `Problem` objects
   (and the dogfood proves one); the board/portfolio is Phase 14.
4. **`node`/`area` taxonomy fields** added *for grouping* — the grouping is PROB-02. (A `Problem` may
   carry a `title`; do not add fields whose only purpose is cross-record grouping.)

**Confidence: HIGH** — the split is documented in three places and consistent.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pydantic` | already a core dep (pyproject.toml; test_ai_optional.py:89) | `BaseModel`, `Field`, `field_validator` for `Problem`/`TransitionEvent` | The entire spine is Pydantic (semantic.py:34); this is the house type system. |
| stdlib `enum.StrEnum` | Python ≥3.11 (`.venv` is 3.12.3) | `ProblemState` ladder | Exactly how `ReviewState` is built (semantic.py:31, 250-254). |
| stdlib `datetime` | — | `TransitionEvent.at` / `Problem.opened` timestamps | `_utcnow()` idiom (semantic.py:40-41). |
| `newsletters.semantic` | in-repo | `Source`, `Trace` references | The spine `Problem` sits above. |

**ZERO new dependencies.** [VERIFIED: codebase] Everything needed (Pydantic, `StrEnum`, `datetime`,
`semantic`) is already present and AI-free. Confirmed against the AI-optional contract (.importlinter:23-36)
and the dependency-boundary test (test_ai_optional.py:76-111).

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `list[Trace]` for evidence | `list[str]` source ids | Loses content-addressing + the unified evidence grammar (`Claim.evidence` is `list[Trace]`, semantic.py:191). Rejected. |
| Sequential+re-open ladder | strictly-forward ladder | Stricter MVP, one-line change; but can't model real re-opens, forcing duplicate Problem ids. Recommended against; flagged for confirmation. |
| Dict-based `_LADDER` allow-table | a `transitions`-library state machine | Would add a NEW dependency — forbidden this phase. The dict is stdlib and trivially testable. Rejected. |
| Dogfood example in `problem.py` | example lives in `tests/test_problem.py` | Keeping it in the test keeps `problem.py` a pure type module (no example surface). Recommended: test. |

**Installation:** none — no new packages.

## Package Legitimacy Audit

> Not applicable — Phase 13 installs **zero** external packages. All dependencies (`pydantic`, stdlib
> `enum`/`datetime`, in-repo `semantic`) are already present and verified by the standing AI-optional
> tests (test_ai_optional.py:76-111). No registry lookup required.

**Packages removed due to [SLOP] verdict:** none.
**Packages flagged as suspicious [SUS]:** none.

## Architecture Patterns

### System Architecture Diagram

```
  scattered external record                 Newsletters core (AI-free leaf tier)
  (Jira ticket / passdown / RCA)
            │  captured as
            ▼
   semantic.Source  ──referenced by──►  semantic.Trace ──aggregated (>=1)──►  problem.Problem
   (semantic.py:49)   (NOT mutated)      (semantic.py:86)                      (problem.py, NEW)
            ▲                                                                       │
            │ content_hash() drift-check (read-only)                               │ human actor calls
            └───────────────────── NO write-back ◄─────────────────────────────── │ transition(to, by)
                                                                                    ▼
   external solving stays operator-owned                                  ProblemState ladder
   (semantic.py:22-24 boundary holds)                                     IDENTIFIED→…→VERIFIED
                                                                          + immutable TransitionEvent log
                                                                                    │
                                                                                    │ (Phase 14 ONLY)
                                                                                    ▼
                                                                   [ portfolio query + board surface ]
                                                                   [ DEFERRED — PROB-02 / PROB-04 ]
```

Data flows ONE way: external record → Source → Trace → Problem. The Problem reads the Source (for
drift-checking) but never writes to it or to any external system. State advances only via a
human-actor `transition`. The dashed Phase-14 box is out of scope.

### Recommended Project Structure
```
src/newsletters/
├── semantic.py      # UNCHANGED — the spine (Source/Trace/Review/Surface)
├── promote.py       # the existing human-gated transforms (the import-pattern precedent)
├── locators.py      # the leaf-module precedent (stdlib+pydantic only)
└── problem.py       # NEW — Problem / ProblemState / TransitionEvent / transition()

tests/
└── test_problem.py  # NEW — entity tests + the three PROB-03 boundary proofs + distinctness + dogfood

.importlinter        # ADD a second `forbidden` contract: forbid-external-write-in-problem
```

### Pattern 1: Human-gated, validator-enforced state transform
**What:** State changes go through a method that refuses on a missing actor or an illegal move; there is
no setter and no auto-advance.
**When to use:** Any axis where "a human decided this" must be provable.
**Example:**
```python
# Source: semantic.py:566-588 (Surface.approve/publish) — the exact idiom Problem.transition mirrors
def approve(self, reviewer: str) -> "Surface":
    if not reviewer:
        raise ValueError("approve() requires a reviewer.")
    ...
```

### Pattern 2: Forbidden-import contract as a standing guard
**What:** A `forbidden` import-linter contract + a runtime `sys.modules` subprocess check prove a module
can never reach a forbidden dependency class.
**When to use:** Encoding a hard boundary (no AI; now: no external-system write) as a durable rule.
**Example:**
```ini
# Source: .importlinter:23-36 — copy this contract shape for problem.py's external-write boundary
[importlinter:contract:forbid-external-write-in-problem]
name = problem.py must not import any network/external-system package
type = forbidden
source_modules = newsletters.problem
forbidden_modules = socket
    http
    urllib
    ftplib
    smtplib
    subprocess
    requests
```

### Anti-Patterns to Avoid
- **Putting `Problem` in `semantic.py`:** dilutes the spine; makes the new axis less obviously distinct.
  Use a leaf module.
- **Referencing Sources by bare id strings:** re-invents a weaker pointer; breaks the unified evidence
  grammar and content-addressing. Use `list[Trace]`.
- **A public state setter / an `advance()` with a default actor:** breaks the human-gated guarantee.
  Only `transition(to, by)` with a required `by`.
- **Reusing any axis-1/axis-2 verb** (`publish`, `promote`, `fan_out`, `derive`, `advance`): collides
  with the terminology guard. The verb is `transition`.
- **Pulling Phase-14 work in** (collection queries, board rendering, portfolio container, grouping
  taxonomy): out of scope (Question F).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Evidence pointer to a Source | a new `{source_id, ...}` model | `semantic.Trace` (semantic.py:86-184) | Already content-addressed + drift-aware; one evidence grammar. |
| Timestamping | manual `datetime.now()` calls scattered | a local `_utcnow()` (copy semantic.py:40-41) | Matches the spine's tz-aware UTC idiom. |
| "No forbidden import" proof | a bespoke AST scanner | the import-linter `forbidden` contract + `sys.modules` subprocess test (test_ai_optional.py:117-158) | Shipped, green, two-layer (static + runtime). |
| Enum | a class of string constants | `enum.StrEnum` (semantic.py:31) | Exactly how `ReviewState` is done; gives `.value` + iteration for the distinctness test. |

**Key insight:** Phase 13 needs zero invention — every piece is a documented, tested idiom already in
`semantic.py` / `promote.py` / `test_ai_optional.py`. The work is composition + the boundary proof.

## Common Pitfalls

### Pitfall 1: `IN_PROGRESS` vs `IN_REVIEW` near-collision
**What goes wrong:** A reviewer eyeballs the two enums, sees both have an "in_…" member, and assumes a
shared value or a near-miss bug.
**Why it happens:** `ProblemState.IN_PROGRESS = "in_progress"` and `ReviewState.IN_REVIEW = "in_review"`
are textually adjacent.
**How to avoid:** The Question-D test asserts `prob_values.isdisjoint(review_values)` — proving the
strings differ, not just the member names. Keep that assertion explicit.
**Warning signs:** Any temptation to name a member `IN_REVIEW` on `ProblemState`.

### Pitfall 2: A transitive import sneaking a forbidden module in
**What goes wrong:** `problem.py` looks clean, but something it imports pulls `urllib`/`socket` in,
failing the runtime guard.
**Why it happens:** `forbidden` contracts and `sys.modules` checks catch transitive edges, not just
direct ones.
**How to avoid:** `problem` imports only `semantic` + Pydantic + stdlib `enum`/`datetime`. Verify by
running `lint-imports` once and the runtime subprocess test (mirroring test_ai_optional.py:143-158).
**Warning signs:** Importing `capture`, `render`, `site`, or any adapter from `problem.py`.

### Pitfall 3: Scope creep into Phase 14
**What goes wrong:** Adding "just a small" `group_by` or a board render "while we're here."
**Why it happens:** PROB-02/04 feel adjacent.
**How to avoid:** No collection-level query, no `render.py` touch, no portfolio container (Question F).
**Warning signs:** Any function taking `list[Problem]` and returning aggregates; any HTML string.

## Code Examples

### Full `problem.py` skeleton (verified against the spine idioms)
```python
# Source: composes semantic.py:31,40-41,49-83,250-287,566-588 + locators.py:1-19 leaf rule
from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from pydantic import BaseModel, Field, field_validator
from .semantic import Source, Trace   # the ONLY non-stdlib/pydantic import — acyclic, AI-free

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class ProblemState(StrEnum):
    IDENTIFIED = "identified"; OWNED = "owned"; IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"; VERIFIED = "verified"

_LADDER: dict[ProblemState, set[ProblemState]] = {
    ProblemState.IDENTIFIED:  {ProblemState.OWNED},
    ProblemState.OWNED:       {ProblemState.IN_PROGRESS},
    ProblemState.IN_PROGRESS: {ProblemState.RESOLVED},
    ProblemState.RESOLVED:    {ProblemState.VERIFIED, ProblemState.IN_PROGRESS},
    ProblemState.VERIFIED:    {ProblemState.IN_PROGRESS},
}

class TransitionEvent(BaseModel):
    from_state: ProblemState; to_state: ProblemState; by: str
    note: str = ""; at: datetime = Field(default_factory=_utcnow)

class Problem(BaseModel):
    id: str; title: str
    state: ProblemState = ProblemState.IDENTIFIED
    evidence: list[Trace] = Field(default_factory=list)
    log: list[TransitionEvent] = Field(default_factory=list)
    opened: datetime = Field(default_factory=_utcnow)

    @field_validator("evidence")
    @classmethod
    def _at_least_one_source(cls, v: list[Trace]) -> list[Trace]:
        if not v:
            raise ValueError("A Problem must aggregate >=1 traced Source.")
        return v

    @property
    def source_ids(self) -> list[str]:
        return list(dict.fromkeys(t.source_id for t in self.evidence))

    def transition(self, to: ProblemState, by: str, note: str = "") -> "Problem":
        if not by:
            raise ValueError("transition() requires an explicit human actor (`by`).")
        if to not in _LADDER[self.state]:
            raise ValueError(f"Illegal move {self.state.value!r} -> {to.value!r}.")
        self.log.append(TransitionEvent(from_state=self.state, to_state=to, by=by, note=note))
        self.state = to
        return self
```

> Note: this is a research SKETCH for the planner, not committed production code. `model_config =
> ConfigDict(validate_assignment=True)` is optional — `Surface` uses it (semantic.py:501); for `Problem`
> the `transition` method is the only mutation path so it is not required, but it would also re-run the
> evidence validator on assignment if desired.

## Runtime State Inventory

> Not applicable — Phase 13 is a greenfield additive module (a NEW `problem.py` + a NEW
> `tests/test_problem.py` + one added `.importlinter` contract). No rename/refactor/migration; no stored
> data, live service config, OS-registered state, secrets, or build artifacts are affected.
> - Stored data: **None** — no datastore; Problems are in-memory typed objects this phase.
> - Live service config: **None.**
> - OS-registered state: **None.**
> - Secrets/env vars: **None.**
> - Build artifacts: **None** — additive module; no packaging change (no new dependency).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Lifecycle state lives only in Jira/ADO/heads (A1) | A first-class `Problem` consolidates the *record* (A2, legibility-only) | A2 decision 2026-06-17 | Signals can later aggregate across problems (Phase 14); Phase 13 builds the entity. |

**Deprecated/outdated:** none relevant. The "promotion" term for the fan-out axis was already renamed to
"fan-out" (SITE-05; promotion-terminology-guard.md:30) — the Problem ladder must avoid "promote" too.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Operators want **re-open** transitions (Resolved/Verified → In Progress), not a strictly-forward ladder | Q.B | If wrong: drop the two re-open edges from `_LADDER` (one-line change). Low risk; the stricter ladder still passes all criteria. |
| A2 | The specific dogfood problem ("Locator circular import") is illustrative; any real Source works | Q.E | None structural — planner may pick a different real Source. |
| A3 | The `forbidden_modules` list (`socket`/`http`/`urllib`/`ftplib`/`smtplib`/`subprocess`/`requests`) is the right network/external-system set to bar from `problem.py` | Q.C(a) | If a relevant SDK is missed, the static contract under-covers; the runtime + API-surface tests still backstop. Confirm the list during planning. |

## Open Questions

1. **Strictly-forward vs. re-open ladder (A1).**
   - What we know: the A2 note frames `Problem` as the legible record of the *real* lifecycle, which reopens.
   - What's unclear: whether the MVP wants the simpler strictly-forward ladder.
   - Recommendation: ship sequential+re-open (recommended); confirm with the user in discuss/plan.

2. **Should `Problem` be exported from `newsletters/__init__.py`?**
   - What we know: the spine types are all re-exported there (`__init__.py:59-78`).
   - What's unclear: whether Phase 13 should add `Problem`/`ProblemState`/`transition` to `__all__` now,
     or wait for Phase 14 (the consumer).
   - Recommendation: export `Problem`, `ProblemState`, `TransitionEvent` now (low cost, makes the entity
     a first-class part of the package API per PROB-01's "first-class entity"). The planner should add a
     one-line `__all__` extension + import, mirroring the existing block.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python ≥3.11 (`StrEnum`) | `ProblemState` | ✓ | 3.12.3 (`.venv`) | — |
| `pydantic` | `Problem`/`TransitionEvent` | ✓ | core dep (test_ai_optional.py:89) | — |
| `pytest` | test suite | ✓ | 9.1.0 | — |
| `import-linter` (`lint-imports`) | the static boundary contract | ✓ | in `[dev]` (test_ai_optional.py:108-111) | runtime subprocess test still proves the boundary if absent (test_ai_optional.py:122-128) |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none material — `import-linter` is present in dev/CI; the runtime
guard backstops it on bare envs.

## Validation Architecture

> `workflow.nyquist_validation` is `true` in `.planning/config.json` [VERIFIED] — section included.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.0 [VERIFIED: `.venv/bin/pytest --version`] |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `pythonpath = ["src"]`, pyproject.toml:66) |
| Quick run command | `.venv/bin/pytest tests/test_problem.py -x` |
| Full suite command | `.venv/bin/pytest` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROB-01 | `Problem` aggregates ≥1 traced Source; <1 rejected | unit | `.venv/bin/pytest tests/test_problem.py::test_problem_requires_at_least_one_source -x` | ❌ Wave 0 |
| PROB-01 | Ladder enum typed; valid sequence advances | unit | `.venv/bin/pytest tests/test_problem.py::test_ladder_forward_and_reopen -x` | ❌ Wave 0 |
| PROB-01 | `ProblemState` distinct from `ReviewState` (no shared value/name/verb) | unit | `.venv/bin/pytest tests/test_problem.py::test_problemstate_distinct_from_reviewstate -x` | ❌ Wave 0 |
| PROB-03 | `transition` refuses no-actor + illegal move; never auto-advances | unit | `.venv/bin/pytest tests/test_problem.py::test_transition_human_gated -x` | ❌ Wave 0 |
| PROB-03 | No network/external import reachable from `problem.py` (static + runtime) | unit/integration | `.venv/bin/pytest tests/test_problem.py::test_problem_loads_no_external_module -x` + `lint-imports` | ❌ Wave 0 |
| PROB-03 | Problem API exposes no write-back/export path | unit | `.venv/bin/pytest tests/test_problem.py::test_problem_api_has_no_write_back_method -x` | ❌ Wave 0 |
| PROB-03 | `semantic.py` spine unchanged (Source not mutated; no reverse import) | unit | `.venv/bin/pytest tests/test_problem.py::test_spine_unchanged_by_problem -x` | ❌ Wave 0 |
| PROB-01/03 | Dogfood Problem end-to-end (no rendering) | integration | `.venv/bin/pytest tests/test_problem.py::test_dogfood_problem_end_to_end -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `.venv/bin/pytest tests/test_problem.py -x`
- **Per wave merge:** `.venv/bin/pytest` (full suite) + `lint-imports`
- **Phase gate:** full suite green + `lint-imports` exit 0 before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_problem.py` — covers PROB-01 + PROB-03 (all rows above)
- [ ] `.importlinter` — add the `forbid-external-write-in-problem` contract (covered by the existing
      `test_import_linter_contract_holds`, test_ai_optional.py:117-137)
- [ ] Framework install: none — pytest + import-linter already present.

## Security Domain

> `security_enforcement` is `true` in `.planning/config.json` [VERIFIED] — section included.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | No auth surface; `Problem` is an in-memory typed object this phase. |
| V3 Session Management | no | No sessions. |
| V4 Access Control | partial | The "human-gated transition" IS an access-control-adjacent invariant: state changes require a recorded actor (`by`). Enforced by `transition`'s `not by` guard + the human-gated test (Q.C). |
| V5 Input Validation | yes | Pydantic typing + the `evidence ≥1` validator + the `_LADDER` legal-move check refuse malformed input. |
| V6 Cryptography | no (reuse only) | No new crypto. `Trace.content_hash` (SHA-256, semantic.py:71-83) is reused read-only; never hand-rolled. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Silent/auto state advance (no human) | Tampering / Repudiation | `transition` requires `by`; no setter/auto-advance; proven by `test_transition_human_gated`. |
| Write-back to an external system (becomes a second tracker) | Tampering (out-of-boundary write) | `.importlinter` forbidden contract + runtime `sys.modules` guard + API-surface allow-list (Q.C). |
| Repudiated lifecycle change ("who moved this?") | Repudiation | Immutable `TransitionEvent` log records `by` + `at` + `note` on every move. |
| Axis-collision corrupting the trust gate ("promote to Published") | Tampering | Terminology-distinctness test (Q.D): no shared enum value/name/verb across the three axes. |

## Sources

### Primary (HIGH confidence)
- `src/newsletters/semantic.py:31,40-41,49-184,250-287,545-588` — Source/Trace, `_utcnow`, `ReviewState`,
  `Review` validator, `Surface.approve/publish` (the human-gated idiom).
- `src/newsletters/locators.py:1-19,21-25` — the leaf-module rule (stdlib+pydantic only; acyclic).
- `src/newsletters/promote.py:18-94` — the `problem→semantic` import precedent + human-gated transforms.
- `tests/test_ai_optional.py:76-158,284-304` — the forbidden-import contract + runtime `sys.modules`
  guard + allow-list test (the PROB-03 proof template).
- `.importlinter:17-36` — the `forbidden` contract shape to copy.
- `.planning/REQUIREMENTS.md:71-74,139-142` — PROB-01..04 text + phase mapping.
- `.planning/ROADMAP.md:349-376` — Phase 13/14 goals, criteria, dependency direction.
- `.planning/notes/a2-problem-lifecycle-decision.md:42-87` — the legibility-layer scoping + boundary.
- `.planning/seeds/promotion-terminology-guard.md:12-34` — the three-axes guard + reserved verb.
- `src/newsletters/dogfood.py:214-417` — real Source shapes + content-addressed traces (dogfood basis).
- `.planning/config.json` — `nyquist_validation: true`, `security_enforcement: true`.

### Secondary (MEDIUM confidence)
- none — all findings are codebase-grounded.

### Tertiary (LOW confidence)
- none.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — zero new deps; every type/idiom exists in-repo and is tested.
- Architecture: HIGH — `problem.py` is a direct parallel of `promote.py`'s import edge + `locators.py`'s
  leaf rule; acyclicity verified from `semantic.py`'s imports (semantic.py:36-37).
- Boundary proof (PROB-03): HIGH — line-for-line adaptation of shipped, green AI-isolation tests.
- Ladder re-open rule: MEDIUM — a defensible design call (flagged A1 for user confirmation).

**Research date:** 2026-06-19
**Valid until:** 2026-07-19 (stable; pure in-repo composition, no fast-moving external deps).
