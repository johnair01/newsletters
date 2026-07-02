# Round 5 — The trust chain as ONE system: every invariant, mapped

> Deep-review loop, Round 5. Subject: the whole trust chain on the merged HEAD
> (`b64faaf`, branch `loop-r5/trust-invariants`), reviewed cross-phase as a single
> system across its total history. Standing lenses: delta-to-reality · drift ·
> total-history honesty.
>
> Method note (per CLAUDE.md): every enforcement point below was read on the LIVE
> file at this SHA, not taken from a phase claim; every adversarial proof is named by
> its test function; vacuous/structural-only proofs are flagged as such.
>
> **This document reviews; it does not refactor.** Real drift found is recorded, not
> fixed (fixes are separate gated changes). No code was written this round.

**Invariant count: 12** (the 11 requested + one that fell out of the reading —
loader→composer read-anchored coverage identity, #12, the upstream feeder the
composer's Hole-B guard trusts).

---

## Fresh evidence (this SHA, run once)

**Invariant-relevant suite** — `.venv/bin/pytest tests/test_semantic.py tests/test_faithfulness_gate.py tests/test_review.py tests/test_problem_boundary.py tests/test_compose.py -q`:

```
.....................................................................    [100%]
69 passed in 1.47s
```

**Full suite** — `.venv/bin/pytest -q` (tail):

```
........................................................................ [ 57%]
........................................................................ [ 69%]
........................................................................ [ 80%]
........................................................................ [ 92%]
...............................................                          [100%]
623 passed in 11.72s
```

**Static AI-optional + no-write-back boundary** — `.venv/bin/lint-imports` (tail):

```
Core (newsletters) must not import any AI/LLM package KEPT
problem.py must not import any network/external-system package KEPT

Contracts: 2 kept, 0 broken.
```

The trust chain is GREEN on the merged HEAD: 623 tests, 2 import contracts, no drift
between what the code claims and what it does at this SHA.

---

## The invariants

### 1 — No auto-publish

**Statement.** A `Surface` reaches `Published` only through a `Review` whose recorded
approval set satisfies the template's `ReviewPolicy`; there is no code path that
publishes without a satisfied gate.

**Enforcement point(s).**
- `src/newsletters/semantic.py:279-287` — `Review._published_requires_satisfied_policy`,
  a `@model_validator(mode="after")` that raises `ValueError` if `state is PUBLISHED and
  not self.satisfied()`. This is the true chokepoint: it fires on *construction and on
  every assignment* (the model has no `validate_assignment` on `Review` itself, but
  `Surface.publish` rebuilds the `Review` via `model_copy(update=…)`, re-running the
  validator).
- `semantic.py:271-277` — `Review.satisfied()`: `len(approvals) >= policy.min_approvals`
  AND, if `require_peer`, at least one approver `!= author`.
- `semantic.py:575-588` — `Surface.publish()` builds a candidate Review and assigns it;
  "validator raises if policy unsatisfied" is the entire mechanism (no bypass branch).
- Socket mirror: `distill/conformance.py:73-77` — a backend's `distill()` MUST return a
  `DistillationResult`, never a `Surface`/`Review`, so the distill socket "cannot hand
  back a published anything."

**Adversarial proof.**
- `tests/test_semantic.py::test_published_without_approval_is_rejected` — direct
  `Review(state=PUBLISHED, …)` with no approvals raises. Structural, non-vacuous.
- `tests/test_semantic.py::test_article_requires_a_peer_not_the_author` — peer policy
  rejects an author self-approval.
- `tests/test_compose.py::test_no_auto_publish_on_the_composed_surface` — the composed
  surface is `Draft`; `publish()` with no reviewer raises AND leaves gate `Draft`; a
  direct `Review(state=PUBLISHED,…)` raises.
- `tests/test_distill_socket.py::test_socket_never_auto_publishes` — the socket return
  type cannot be a published anything.

**Known ceilings.** The gate enforces *policy satisfaction*, not *reviewer identity
authenticity* — `approve("anyone")` records a string; nothing verifies the approver is a
real, authorized human (that trust is external, at the PR layer). `require_peer` only
checks `approver != author` by string inequality, so two colluding names still pass. The
gate governs the `Review` object; it does not stop someone editing `content/**/site/*.html`
by hand outside the model (that is `review.py`'s merge-gate job, invariant #9).

**History.** The oldest invariant — present since the Rev1 spine (`5aca6f2`, "Rev1:
parameterized surface templates…"). The validator's wording and the `satisfied()`
peer-check are the canonical enforcement CLAUDE.md points every other guard back at
("mirrors the no-auto-publish gate in semantic.py"). No bypass was ever found in it; it
is the *reference implementation* that later guards (Coverage, Problem) were built to
imitate.

---

### 2 — Every published claim traces to evidence

**Statement.** Every `Claim` rendered into a *published* surface has ≥1 `Trace`;
unsubstantiated material goes to `missing[]`, is shown to the reviewer, and is never
published silently.

**Enforcement point(s).**
- `semantic.py:552-564` — `Surface.open_pull_request()` refuses to move Draft→In-Review
  if any claim in a `ClaimsBlock` is untraced ("move them to `missing`"). This is the
  *entry* to the gate, so an untraced claim can never even reach review.
- `semantic.py:196-197` — `Claim.is_traced` (`len(evidence) > 0`), the reused predicate.
- Distill boundary: `distill/ports.py:95-131` — `_enforce()`, the SINGLE site where
  faithfulness is checked; raises on the first claim a backend emits that isn't entailed.
- Reviewer-facing relocation: `distill/faithfulness.py:77-107` —
  `route_unfaithful_to_missing()` moves every unfaithful claim's text VERBATIM into
  `missing[]`.
- Merge gate: `review.py:112-119` — an `OPEN_MISSING` blocker for a published surface
  carrying non-empty `missing[]`.

**Adversarial proof.**
- `tests/test_semantic.py::test_untraced_claim_blocks_review` /
  `test_traced_claim_passes_review` — the `open_pull_request` gate, both directions.
- `tests/test_compose.py::test_untraced_and_unaddressed_claims_are_routed_to_missing` —
  planted zero-trace + un-addressed claims land in `missing[]`, not in a `ClaimsBlock`.
- `tests/test_distill_socket.py::test_faithfulness_seam_rejects_untraced`.

**Known ceilings.** `open_pull_request` only inspects `ClaimsBlock` claims
(`_published_claims`, `semantic.py:545-550`). A numeral or fact authored into a
`ProseBlock`/`KpiStripBlock` is NOT a `Claim` and is invisible to this gate — that gap is
covered separately and only at the composer (invariant #5, Hole A), never at the semantic
gate. Also: the gate is *published-only* by design; a Draft can hold untraced claims
freely (they must be resolved before review, not before draft).

**History.** Rev1 spine invariant (`5aca6f2`). The faithfulness *seam* that hardened
"traced" into "entailed" arrived with the distill socket (Phase-1 v1.1) and self-
strengthened to span-containment in Phase 3 (see #4).

---

### 3 — Content-addressed STALE detection

**Statement.** A `Trace` pins the SHA-256 of its Source's full content at capture time;
STALE is *computed* by comparing that pin to the live source hash — never a stored flag —
and an un-addressed trace is never stale.

**Enforcement point(s).**
- `semantic.py:71-83` — `Source.content_hash()`: `sha256(transcript)`, stdlib only,
  deliberately EXCLUDING the `extraction` coverage carrier (folding it in would re-key
  every existing Trace and falsely mark it stale).
- `semantic.py:126-170` — `Trace.from_source()`, the SOLE content-addressed constructor;
  validates `0 <= start <= end <= len` BEFORE slicing (raises, never clips).
- `semantic.py:177-184` — `Trace.is_stale_against()`: `is_addressed and live != pinned`.
- `semantic.py:199-211` — `Claim.is_stale()`; `semantic.py:310-319` —
  `Distillation.stale_claims()`.
- Merge gate: `review.py:92-101` — STALE blocker, checked FIRST (elif-guards UNENTAILED).

**Adversarial proof.**
- `tests/test_review.py::test_blocks_stale_published_claim` — a drifted source produces a
  STALE blocker on a published surface. Structural.
- `tests/test_swimlane.py::test_every_emitted_trace_is_addressed` — proves every loader
  trace *is* addressed (the precondition for STALE to ever apply), with an adversarial
  half rejecting a `content_hash=None` trace.

**Known ceilings.** STALE only has teeth where a trace is content-addressed. An
un-addressed trace (`content_hash is None`) is *never* stale — a deliberate no-false-
positive choice (Option A, #4). A trace whose `source_id` is absent from the lookup is
*skipped*, not flagged (`Claim.is_stale`, `semantic.py:207-211`) — we cannot judge drift
without the live source, so a missing source silently yields "not stale," not an error.
Hash is over `transcript` only, so metadata drift (context, timestamp) is invisible by
design.

**History.** The content-address fields are OPTIONAL/backward-compat (D-1/D-4) so every
Rev1 trace stays valid. The work-corpus ledger seed (`8229db1`, Phase-11) is where
`content_hash` first appears in committed data. STALE-as-computed (D-2) is the design
decision the faithfulness Option-A rule was later built to mirror.

---

### 4 — Faithfulness: span-containment + Option-A structural fallback

**Statement.** A claim is faithful iff it has ≥1 trace AND either (a) a trace is
un-addressed (structural fallback — span-containment N/A), or (b) an addressed trace's
normalized span contains the normalized claim text. Untraced ⇒ unfaithful.

**Enforcement point(s).**
- `distill/faithfulness.py:62-74` — `SpanContainmentFaithfulness.entails()`. Line 68-69
  is Option-A (a): un-addressed trace → structural pass. Line 71-72 is (b): strict
  normalized containment.
- `distill/faithfulness.py:42-50` — `_normalize()` (casefold + whitespace-collapse) on
  TRANSIENT copies only; never mutates stored text.
- `distill/ports.py:83-87` — `StructuralFaithfulness` (the Phase-1 default, traced-only).
- `distill/ports.py:119-122` — `_enforce()` lazily binds `SpanContainmentFaithfulness`
  as the default now (was structural in Phase 1).

**Adversarial proof.**
- `tests/test_faithfulness_gate.py::test_entails_false_when_addressed_span_does_not_contain_claim`
  — teeth on addressed evidence.
- `::test_unaddressed_trace_is_structural_fallback_entailed` — Option-A (a) proven.
- `::test_entails_false_for_untraced_claim`, `::test_entails_never_mutates_claim_or_traces`,
  `::test_enforce_default_now_rejects_addressed_unentailed_claim`.
- AI-free proof: `::test_faithfulness_module_imports_no_ai`.

**Known ceilings — this is the chain's most important honest limit.** Option-A (a) means
**an un-addressed trace passes structurally with NO content check**. Any claim whose
evidence is all un-addressed (the entire live `capture.py` path, which mints empty-span
traces) gets the traced-only guarantee — span-containment does not apply. So a caller who
hand-builds an un-addressed trace with a fabricated span passes the gate. This is a
*deliberate* no-false-positive choice (a strict rule would reject every Rev1 claim), and
the gate **self-strengthens** as sources migrate to `Trace.from_source`. Second ceiling:
containment is substring, not semantics — "revenue fell" is entailed by a span containing
those words regardless of surrounding negation.

**History.** Hardened in Phase 3 (WHERE-WE-ARE decisions log, 2026-06-17): an executor
caught that live capture mints empty-span traces, so strict containment would falsely
reject every Rev1 claim — violating *faithful-not-suggestive*. Resolution mirrors the
STALE rule: "absence of content-addressing means *not applicable*, never a false verdict."
Rejected Option B (harden `capture.py` now) as scope creep. This is the single most-cited
scope boundary in the repo.

---

### 5 — Hole A: numeral-free non-claims content (composer-level)

**Statement.** No composer-authored, non-`ClaimsBlock` text carries an un-sourced digit
run; the only out-of-claim numerals are `KpiItem` value/delta, each traceable to a
content-addressed endpoint.

**Enforcement point(s).**
- `compose.py:329-338` — the connective `ProseBlock` carries transitions only, NO
  numerals/facts.
- `compose.py:240-244` — `_FANOUT_STUB`: structural, numeral-free descriptive labels only.
- `compose.py:196-226` — `_compose_kpi_item`: the only place a delta numeral is produced,
  and only from two content-addressed numeric endpoints (`_addressed`, `compose.py:191-193`);
  otherwise `delta=None` + a `missing[]` note, NEVER a fabricated 0.
- Δ derivation: `compute_delta` (`compose.py:108-146`) is pure — never itself a `Claim`,
  never traced, never rendered as a claim.

**Adversarial proof.**
- `tests/test_compose.py::test_authored_prose_is_numeral_free` — planted
  `ProseBlock("we shipped 42 features")` is CAUGHT by the same scan that passes for real
  output. Non-vacuous, structural.
- `::test_kpi_numbers_are_sourced_to_endpoints` — every KPI value numeral equals its
  traced close endpoint; a delta numeral requires ≥2 endpoints.
- `::test_every_rendered_delta_recomputes_byte_equal` — the reproducibility test that
  stands in for a trace on the derived Δ.

**Known ceilings — the sharpest scoping limit.** Hole A is closed **only at the composer,
not at the semantic gate.** The scan is a test-side regex over composer output
(`_authored_digit_runs` in the test file), not an in-model invariant. Any *other* producer
of a `Surface` (the AI backend of the future, invariant #DEF-11 seam; `capture.build_report`;
a hand-built surface) can author a numeral into a `ProseBlock` and NOTHING stops it — the
semantic layer has no numeral guard. This is the widest "invariant genuinely stops here"
boundary in the whole chain.

**History.** Holes A and B were RESEARCH findings about the *existing* v1.0 pipeline, not
risks Phase 2 introduced (`02-LEARNINGS` §Surprises: "the gate holes existed in shipped
code long before this phase"). Phase 2 (`22396ce`, PR #5) closed them *at the composer*
with adversarial planted-cheat guards while leaving `faithfulness.py`/`coverage.py`
untouched — deliberately, to avoid weakening an existing gate to go green.

---

### 6 — Hole B: all-addressed traces (loader + composer-level)

**Statement.** No un-addressed free-pass trace ever leaves the loader; the composer
selects only claims where *every* trace is content-addressed, routing the rest to
`missing[]`.

**Enforcement point(s).**
- Loader (upstream close): `swimlane.py:227-229` — `Trace.from_source` is the SOLE
  minting path; a non-locatable scalar is routed to `unextracted[]` with a reason code
  (`swimlane.py:219-222`), never a hand-minted hash or guessed claim. Every emitted trace
  `is_addressed`.
- Composer (downstream select): `compose.py:191-193` — `_addressed(claim)` = traced AND
  all traces addressed; `compose.py:356-363` — unaddressed claims routed to `missing[]`.

**Adversarial proof.**
- `tests/test_swimlane.py::test_every_emitted_trace_is_addressed` — positive half over
  both fixtures + adversarial half: a hand-built `Trace(content_hash=None)` is rejected by
  the SAME predicate that passes for every loader claim. Non-vacuous, structural.
- `tests/test_compose.py::test_untraced_and_unaddressed_claims_are_routed_to_missing`.

**Known ceilings.** The loader closes Hole B *by construction* for its own output; the
composer closes it *by selection* for what it composes. But the semantic `Claim` type
still permits an un-addressed trace (it must, for Rev1 back-compat) — so Hole B is closed
at these two producers, NOT in the type system. The same limitation as #5: a different
producer can emit un-addressed traces, and only the *faithfulness gate's* structural
fallback (which passes them, #4) sees them downstream.

**History.** Loader close landed Phase 1 (`01-LEARNINGS`: "closes Hole B upstream — no
un-addressed free-pass trace ever leaves this loader"). Composer close landed Phase 2 as
the `_addressed` select. Both are the "prove-it-fires" guard-halves pattern minted in
Phase 1.

---

### 7 — Byte-stable determinism

**Statement.** The same input always produces a byte-identical `model_dump_json` — no
clock, no `set()`, no non-total sort anywhere in the loader→composer→committed-output
path.

**Enforcement point(s).**
- Loader: `swimlane.py:509-514` — `Source.timestamp = EPOCH_ZERO` (never `now()`); lanes
  iterated in FILE ORDER (`swimlane.py:526-530`); a single forward-only cursor
  (`_Minter`, `swimlane.py:192-229`) gives duplicate scalars distinct offsets.
- Composer: `compose.py:384-395` — `Surface(created=EPOCH_ZERO)` passed EXPLICITLY (never
  the `now()` default — the confirmed determinism trap); FILE-ORDER iteration
  (`compose.py:340-342`); `_dedup_in_order` (`compose.py:182-188`, no `set()`).
- Δ: `compute_delta` is a pure function of two argument strings (`compose.py:108`).
- Ledger: compose is read/assign-only, never `save()` (`compose.py:322-325`); persistence
  is the caller's, keeping compose disk-write-free.

**Adversarial proof.**
- `tests/test_swimlane.py::test_load_is_byte_stable`.
- `tests/test_compose.py::test_two_composes_are_byte_identical`,
  `::test_determinism_with_repeated_value_across_lanes`.
- Corpus level: `tests/test_modulesite.py::test_committed_equals_fresh_build` (committed
  output byte-identical to a fresh build).

**Known ceilings — a live latent trap.** Determinism is enforced *per caller*, not in the
type. `semantic.py`'s `Surface.created: datetime = Field(default_factory=_utcnow)` and
`Source.timestamp` default to `now()`. Two existing builders — `capture.build_report` and
`worksurface.build_work_report` — inherit this default and are therefore NOT byte-stable
(`02-LEARNINGS` lesson: "a live trap every composer inherits"). Any future composer that
forgets `created=EPOCH_ZERO` silently loses determinism. The proper fix (make `created`
required, or default to a sentinel) is deferred — `semantic.py` is on the frozen list.

**History.** `EPOCH_ZERO` discipline is inherited from the Rev1 adapters. Phase 2 made
the composer the *first byte-stable composed surface*, treating the `capture.build_report`
analog as a determinism trap not a copy target.

---

### 8 — AI-optional core

**Statement.** `import newsletters` and the deterministic spine run with only stdlib +
Pydantic; every AI/LLM package lives behind an `[ai]` extra, lazy-imported inside the AI
backend only; CI fails if any AI import is statically reachable from core.

**Enforcement point(s).**
- `.importlinter:23-35` — `forbid-ai-in-core` forbidden contract: `newsletters` must not
  import `pydantic_ai / langchain / langgraph / langsmith / logfire / openai / anthropic`.
  `include_external_packages = True`.
- `pyproject.toml:23-46` — `ai = ["pydantic-ai"]` behind `[project.optional-dependencies]`;
  the same discipline for `[excel]/[pptx]/[config]` (PyYAML behind `[config]`, lazy-imported
  in `_yaml_loader`).
- Every trust module re-asserts it in its own docstring (faithfulness.py:30-33,
  conformance.py:20-22, review.py:19-23, problem.py:8-17).

**Adversarial proof.**
- `.venv/bin/lint-imports` → "Core (newsletters) must not import any AI/LLM package KEPT"
  (verbatim above). Static.
- Runtime complements (necessary-but-not-sufficient, per `.importlinter:8-15`):
  `tests/test_faithfulness_gate.py::test_faithfulness_module_imports_no_ai`,
  `tests/test_review.py::test_review_module_imports_no_ai`,
  `tests/test_distill_socket.py::test_distill_package_imports_no_ai`,
  `tests/test_ai_optional.py::test_no_ai_pydantic_plugin_active` (the pydantic-plugin
  auto-activation blind spot), plus the bare no-extras install CI job (PKG-03).

**Known ceilings — explicitly documented, not hidden.** The import-linter contract catches
static import EDGES only. It CANNOT catch pydantic-plugin auto-activation (pydantic
auto-loads every installed `pydantic`-group plugin, e.g. logfire's, with no import edge for
a static checker to see — see `.planning/notes/ai-optional-pydantic-plugin-leak.md`). The
contract is *necessary-but-not-sufficient*; the runtime entry-point guard + the bare-install
CI job close the blind spot. This is a genuinely two-layer invariant.

**History.** Core discipline since Rev1. `[config]` (PyYAML) was added Phase 1 behind an
extra rather than as a core dep, overriding a RESEARCH line that suggested a project
dependency — the minimal-core invariant won (`01-LEARNINGS` §Decisions).

---

### 9 — No-write-back problem boundary

**Statement.** The `Problem` lifecycle entity is a legibility layer, not a tracker:
`problem.py` never writes back to any external system, and `Problem`'s public API exposes
no export/push/sync path — state changes ONLY through the human-gated `transition`.

**Enforcement point(s).**
- `.importlinter:50-63` — `forbid-external-write-in-problem` forbidden contract:
  `newsletters.problem` must not import `socket / http / urllib / ftplib / smtplib /
  subprocess / requests`.
- `problem.py:43` — the ONLY non-stdlib/pydantic import is `.semantic` (leaf, acyclic).
- `problem.py:136-149` — `__setattr__` guard: direct assignment to `state`/`log` outside
  `transition` raises (the human-gate cannot be sidestepped).
- `problem.py:172-206` — `transition()` is the SOLE mutator: refuses an empty actor and an
  illegal ladder move; opens the private `_via_transition` gate for exactly the two guarded
  writes.

**Adversarial proof.**
- `tests/test_problem_boundary.py::test_problem_loads_no_external_module` — a `sys.modules`
  subprocess guard proving none of the forbidden modules is reachable on a real import.
- `::test_problem_api_has_no_write_back_method` — a standing allow-list guard: any future
  `export_to_jira`/`push_to_ado`/`sync_remote` fails loudly; `transition` must remain;
  `set_state`/`advance`/`auto_advance`/`publish`/`approve` must be absent.
- `::test_transition_human_gated_empty_actor_raises`,
  `::test_spine_unchanged_by_problem` (full ladder leaves the Source byte-identical; the
  edge stays one-way problem→semantic).
- `.venv/bin/lint-imports` → "problem.py must not import any network/external-system
  package KEPT".

**Known ceilings.** The API allow-list is a substring scan over `dir(Problem)` minus the
pydantic surface — a write-back method named without any of the `WRITE_BACK_SUBSTRINGS`
fragments would evade it. The import contract is static-only (same class of limit as #8);
its runtime `sys.modules` complement is what actually proves reachability. `transition`
being the sole mutator holds only because BOTH the `__setattr__` guard AND the
`_via_transition` gate are present — remove either and a bare `p.state = VERIFIED` bypasses
the ladder, the actor check, and the log.

**History.** The `__setattr__` loophole was a *real* bypass, found and closed this
milestone: `89e0947` "fix(13): close the human-gate loophole — transition is now the SOLE
state mutator." Before it, construction-time field-setting worked but a post-construction
`p.state = …` sidestepped the whole gate — the human-gate was a lie. The Phase-13 verifier
caught it; the fix makes "transition is the sole mutator" literal.

---

### 10 — The three state axes (terminology separation)

**Statement.** Three lifecycle axes never collide in type, value, name, or verb:
(1) the Surface review gate `Draft→In Review→Published`; (2) the Surface fan-out chain
(report/article/newsletter/show/learning); (3) the Problem lifecycle ladder
`Identified→Owned→In Progress→Resolved→Verified`.

**Enforcement point(s).**
- `problem.py:65-79` — `ProblemState`, a `StrEnum` *distinct* from `ReviewState` with
  member values sharing nothing with the gate's; `IN_PROGRESS = "in_progress"` deliberately
  disjoint from `IN_REVIEW = "in_review"`.
- `problem.py:172` — the axis-3 verb is `transition` (never promote/publish/advance/
  fan-out/derive — the reserved verbs of axes 1 and 2), documented `problem.py:33-34`.
- Semantic axis-1 verbs: `publish`/`approve`/`open_pull_request` (`semantic.py:552-588`).

**Adversarial proof.**
- `tests/test_problem_boundary.py::test_problemstate_distinct_from_reviewstate` —
  distinct type, disjoint member VALUES and NAMES, explicit adjacency assertion
  (`in_progress != in_review`). Structural.
- `::test_lifecycle_verb_collides_with_no_axis_verb` — `transition` collides with no
  gate/fan-out/promote verb; `Surface` has no `transition`; `Problem` has no gate verb.

**Known ceilings.** The guard proves disjointness of the *typed enums and verbs*, not of
free-text UI copy or docstrings — a doc could still say "promote a problem" and no test
fails. It checks the two axes that share an enum shape (Problem vs Review); the fan-out
axis (#2) is enforced by naming convention ("fan-out" not "promotion") not by a type, so
its separation rests partly on discipline. Note the compass itself still carries a legacy
"one promotion chain" phrasing (WHERE-WE-ARE decisions log) — a *known ontological drift*
flagged for the Round-8 sweep, not a code defect.

**History.** Planted as a seed (`promotion-terminology-guard.md`, 2026-06-17) BEFORE any
Phase-13 code, precisely because "promotion" was ambiguous across axes 2 and 3 and risked
bleeding into axis 1 ("promote to Published"). Resolved first, then the `Problem` entity
typed — the guard is the seed made executable.

---

### 11 — Invariant-3: the private corpus is never serialized

**Statement.** The private `Corpus` (`weights`/`read`/`owned`) is never embedded in a
`Surface` or `Source`; personalization reads it at render time and the output carries
*emphasis*, not the corpus.

**Enforcement point(s).**
- `semantic.py:219-242` — `Corpus` is a standalone model, passed to `claims_for()`/
  `emphasis()`, never stored on a Surface.
- `semantic.py:493-521` — `Surface` holds NO `Corpus` and NO `Distillation` object — only
  an `audience_label` string, the rendered blocks, and a `missing: list[str]` carrier
  documented "str entries only … so invariant 3 is preserved."
- `semantic.py:303-304` — `Distillation.audience_name` is a name string only; the corpus
  is passed to `render()` and never stored.

**Adversarial proof.**
- `tests/test_semantic.py::test_private_corpus_not_serialized_into_surface` — asserts
  `weights`/`read`/`owned`/`core` do NOT appear in `model_dump()` or `model_dump_json()`.
- `::test_corpus_emphasis_orders_without_leaking` — emphasis reorders claims without the
  corpus leaving.
- `::test_render_does_not_leak_private_corpus` (render layer).

**Known ceilings.** The serialization guard checks specific field-name strings
(`weights`/`read`/`owned`/`core`) are absent from a dumped Surface — it proves *this*
Surface built *this* way doesn't leak; it is not a type-level proof that no code path could
ever place a Corpus on a Surface (the `Surface` type has no Corpus field, so this holds
structurally, but the test is a value-scan not a schema assertion). Emphasis values derived
from weights *do* influence claim ORDER in the output — the corpus's *effect* is visible
even though its data is not (this is intended: "same facts, new emphasis").

**History.** Rev1 spine invariant (one of the three enforced-in-code invariants named in
the `semantic.py` module docstring, `semantic.py:19-21`). Unchanged across the milestone.

---

### 12 — Read-anchored coverage identity (loader) — the upstream feeder *(added this round)*

**Statement.** Every non-null scalar the loader READS is either minted into a
content-addressed claim or disclosed in `unextracted[]`:
`len(all_claims) + len(all_unextracted) == scalars_walked`. Zero silent drops, enforced by
construction. (Included because the composer's Hole-B select and `missing[]` honesty *trust*
this feeder — it is the first link of the chain.)

**Enforcement point(s).**
- `swimlane.py:545-553` — the identity is checked in `load_swimlanes`; a mismatch raises
  `RuntimeError` ("a scalar was read but neither claimed nor disclosed — silent drop,
  forbidden").
- `swimlane.py:209-229` — `_Minter.mint` increments `walked` for every scalar READ; a
  `None` leaf is absent, not read (`swimlane.py:274-275`).
- Coverage honesty mirror: `distill/coverage.py:54-67` — `Coverage` cannot be
  `complete=True` with a non-empty `unextracted[]` (the dishonest state is unrepresentable,
  mirroring the no-auto-publish gate).

**Adversarial proof.**
- `tests/test_swimlane.py::test_no_yaml_scalar_is_read_but_undisclosed` — the identity,
  cross-checked against an INDEPENDENT scalar-leaf count (`_count_scalar_leaves`), so a
  self-consistent-but-wrong internal tally cannot pass. Structural, non-vacuous.
- `tests/test_distill_socket.py::test_coverage_lying_completeness_rejected`.

**Known ceilings.** The identity is anchored to what the *loader's own walk* considers a
scalar leaf — a value the parser drops before the walk (a genuine YAML-parse loss) is
invisible to it; the independent yardstick walks the SAME parsed doc, so both share the
parser's view. A type-coerced scalar (`yes`→`True`) counts as *read* and is honestly routed
to `unextracted[]` — coverage is preserved, but its content-address is not (it displays a
value with no backing claim; `01-LEARNINGS` surprise).

---

## System-level: where the invariants COMPOSE

The chain is a pipeline of producers and gates, each trusting the honesty of the one
upstream:

```
 YAML config
   │  (#12 read-anchored coverage: every scalar → addressed claim OR disclosed gap)
   ▼
 swimlane loader ──emits──► SectionBinding[]  (#6 loader: every trace is_addressed;
   │                                            #7 EPOCH_ZERO + file-order determinism)
   ▼
 compose_module_report
   │  (#6 composer: _addressed SELECT, rest → missing[];
   │   #5 Hole A: authored prose numeral-free, Δ only from addressed endpoints;
   │   #1 ships Draft, never publishes; #7 created=EPOCH_ZERO)
   ▼
 Surface (Draft)  ── review gate ──►  (#1 no-auto-publish validator;
   │                                    #2 open_pull_request refuses untraced claims)
   ▼
 render → honesty panel (surface.missing[] shown to reviewer)
   │
   ▼
 review.review_blockers (#3 STALE / #4 UNENTAILED / #2 OPEN_MISSING)
   │  published-only; the CI merge gate (`newsletters check`)
   ▼
 merge to main
```

The composition is real and load-bearing: **#12 feeds #6 feeds #5 feeds #1 feeds the
honesty panel feeds the #3/#4 check gate.** Each gate REUSES the upstream predicate rather
than re-deriving trust (`review.py` reuses `Claim.is_stale` and
`SpanContainmentFaithfulness.entails`; the composer reuses `Trace.from_source`;
`_enforce` is the single faithfulness site the socket, conformance, and route-to-missing
all call). "One trust rule, one place" holds across the chain — there is exactly one
definition of "faithful," one of "stale," one of "addressed."

The determinism invariant (#7) and AI-optional (#8) are *ambient* — they hold at every
node, not at one gate — and are the reason the committed output is an auditable artifact
(`committed == fresh-build`) and the spine runs with zero AI.

## The seam for an untrusted producer (DistillPort AI backend, DEF-11)

The distill socket (`ports.py` `DistillPort`) is the designed plug for a future AI "robot
journalist." The question Round 5 must answer honestly: **if we plug an untrusted producer
into that socket, does the existing chain contain it?**

What the socket DOES contain, at the boundary, via `conformance.assert_conforms`
(`conformance.py:38-94`):
- return type is `DistillationResult`, never a published Surface/Review (#1 mirror);
- coverage is present and internally honest — no "complete with dropped content" (#12
  mirror);
- **every emitted claim passes `_enforce` faithfulness** (#2/#4);
- the result round-trips losslessly through JSON.

What the socket does NOT contain — the seams a hostile producer slips through:
1. **The faithfulness gate's Option-A structural fallback (#4 ceiling) is the widest
   hole.** A backend that emits claims with *un-addressed* traces (empty `content_hash`)
   and fabricated spans PASSES `_enforce` — span-containment never runs on un-addressed
   evidence. An untrusted producer that simply never content-addresses its traces gets the
   traced-only guarantee and can attach any span text it likes. The gate only bites a
   producer honest enough to content-address.
2. **Hole A (#5) is composer-only.** The AI backend produces a `Distillation`/`Surface`
   directly, bypassing `compose_module_report`. Nothing scans an AI-authored `ProseBlock`
   for un-sourced numerals — the numeral-free guarantee simply does not exist off the
   composer path.
3. **Determinism (#7) is per-caller.** An AI backend inherits the `now()` default unless
   it explicitly passes `EPOCH_ZERO`; committed-output reproducibility is not enforced on
   it by the type.

The final human gate (#1) still holds absolutely — an AI-produced Surface CANNOT reach
Published without a recorded human approval, and `review_blockers` (#3/#4) runs at merge on
whatever is published. So the *catastrophic* failure (silent auto-publish of fabricated
content) is closed. But the *insidious* failure — an AI producer emitting plausibly-spanned,
un-addressed, numeral-laden claims that pass every automated gate and land in front of a
human who trusts the "every claim traced" badge — is NOT closed by the automated chain. It
rests entirely on the human reviewer, which is exactly the "interactive until trusted" rule.

### Weakest-link verdict

**The weakest link is the faithfulness gate's Option-A structural fallback (#4): an
un-addressed trace passes with no content check.** Today this is correct and necessary —
the live `capture.py` path mints empty-span traces, and a strict rule would produce false
positives that violate *faithful-not-suggestive*. But it means the gate's teeth are
*opt-in by the producer*: only a backend that content-addresses its evidence is actually
checked. **The chain is ready for a *trusted* AI producer (one that mints via
`Trace.from_source`), but it is NOT ready for an *untrusted* one** — an untrusted producer
that declines to content-address bypasses span-containment (#4), and Hole A (#5) doesn't
exist off the composer path at all. The DEF-11 robot journalist must therefore be required,
at the socket, to emit only content-addressed traces (turning Option-A (a) from a fallback
into a rejected case for that backend), and to route through a numeral-guard equivalent —
otherwise the automated chain reduces to "no auto-publish + a human reads it," which is the
floor, not the guarantee the "every claim traced" badge implies.

The honest one-line framing: **the chain's automated teeth are conditional on producer
honesty; its unconditional guarantee is the human gate.** That is the right design for the
milestone we're in (manual + deterministic producers), and the exact thing to harden before
an untrusted backend is admitted.

---

## Deepest-learning summary (3 sentences)

The trust chain is genuinely a single composed system — one definition each of faithful,
stale, and addressed, reused by every gate, with the human no-auto-publish validator
(#1) as the unconditional backstop that no producer can route around. But its *automated*
teeth are conditional on producer honesty: the faithfulness gate's Option-A fallback (#4)
passes un-addressed traces without a content check, and the numeral-free guarantee (#5,
Hole A) exists only at the composer — so a trusted, content-addressing producer is fully
gated while an untrusted one that declines to content-address slips past everything except
the human. The milestone's real hardening pattern — a real bypass found and closed
(`89e0947`, the Problem `__setattr__` loophole), holes closed at the producer with
adversarial "prove-it-fires" guards, and honest scope boundaries recorded rather than
papered over — is exactly what must be applied to the DistillPort seam before the DEF-11
robot journalist is admitted: require content-addressed traces at the socket, or the badge
"every claim traced" overstates what the automation actually proves.
