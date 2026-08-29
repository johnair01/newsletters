# RETRO — friction log & hardened rules

> Log friction honestly — name mistakes, don't paper over them. Each durable fix becomes a rule
> (in `CLAUDE.md`) or a guard, not a vibe. A recurring friction you haven't hardened is a bug.
> Newest on top.

## 2026-08-29 (latest) — W27: the milestone's frictions, and what each one hardened into

**Friction observed (v1.3 plan 04-03 — the operator recipe, the spec deltas, and the phase sweep).**
This is the milestone's closing entry, so it names the frictions that recurred across the whole of
v1.3 rather than only the ones this plan met.

1. **"A test suite and the job that runs it are two different artifacts" cost us THREE times.** W21
   (`[pptx]` installed by no job), W25 (nine modules named by no job at all), and the shape survives
   into this phase's design: `tests/test_weeklysite.py` is stdlib-only *by construction* precisely
   so it can live in `site-integrity`, a job with **no** `0 skipped` assertion, without becoming a
   green that means "not run". The recurrence is the honest finding: W21's rule was written down
   and then applied to the extra that tripped it instead of to the class.
2. **A document that describes the system goes stale the moment the system grows, and nothing
   notices.** The `--corpus` section of `docs/architecture.md` was stale at **two** corpora — it had
   survived the module corpus entirely — and `content/README.md` had said "Empty until then" since
   v1.1. Four documents were wrong and every gate was green, because no gate reads prose.
3. **A recipe whose commands were never run is a promise.** Two of the six documented commands
   needed a decision that only *running* them surfaces: `build --corpus weekly` renders the corpus
   at `content/weekly/` and takes no `--spec` (so an operator's HTML route is "put your spec in the
   corpus dir", which the doc now says out loud), and there is **no `--workbook` flag** — the export
   path is a Python-API seam this milestone. Both would have shipped as implied-by-omission lies in
   a recipe written from the plan rather than from the CLI.
4. **The `_EMAIL_RE` collision, and why the allowance is narrow and documented.** The committed
   `.eml` corpus trips the synthetic-content scanner by design: the scanner treats an address SHAPE
   as its proxy for a real person, and every header of a synthetic message is a shape. The
   allowance is exactly one reserved domain (RFC 6761 `@example.invalid`), it is documented in the
   test's own docstring rather than buried in a regex, and it carries a **second planted arm** — a
   non-reserved address that must still trip *through* the allowance. Without that arm, "ignore the
   reserved domain" is one refactor away from "ignore every address" and nobody would notice.
5. **The GSD state tooling mutated `STATE.md` on error and reported values it had not written.**
   Recorded across W24, W25 and W26; three occurrences is a tool bug, not bad luck. **Fourth
   occurrence, this plan:** W26's routing rule was followed — `STATE.md` was hand-edited and never
   handed to `state.*` — and the two verbs that *were* run behaved exactly as W26 predicted.
   `roadmap.update-plan-progress` was clean and correct (checkbox + progress row).
   `requirements.mark-complete` flipped the checkbox correctly, updated the traceability table
   this time, **and injected a stray blank line into the Future Requirements list**, splitting two
   bullets into two lists. Caught by diffing against a scratchpad copy taken before the call, and
   repaired by hand. The rule is holding; the tool is not fixed.
6. **DEF-15 taxed every plan in this milestone that added an import.** `isort` has no
   `profile = "black"`, so the two tools disagree on every parenthesized multi-line import, and each
   plan paid the same "is this failure mine?" tax and worked around it the same way (module-level
   access, single-line imports). Four plans have now paid a toll on a fix that is one config line
   plus one reformat.

**Rules hardened**

- *A gate's location is part of the gate.* When adding a test module, name the CI job it runs in and
  the extras that job installs, in the module's own docstring — and put any extra-gated test only in
  a job that **fails on skip**. (The durable form of W21/W25, now applied to the class rather than
  to the instance that tripped it.)
- *A doc that names a command is held to the command by a test.* `docs/weekly.md` is parsed by
  `tests/test_weeklysite.py::test_recipe_commands_match_the_shipped_cli`, which drives its expected
  set from the **live Typer app** and asserts a floor on how many command lines it found. A
  doc-contract test that silently matches nothing passes forever and protects nothing.
- *A doc that describes the system's shape is held to it by a test too.*
  `test_docs_describe_four_corpora` asserts, for four documents, that the weekly is named and that
  the specific stale wording is gone — so the **next** corpus turns them red instead of leaving them
  quietly wrong. It reads the prose with code fences and HTML comments stripped and whitespace
  collapsed, because the phrase it forbids spans a line break in `architecture.md`: a raw `in` check
  would have passed on the stale document, which is a guard that only *looks* like one.
- *Write the recipe from the CLI, then run it.* Every fenced command is executed against the
  committed corpus in document order before the recipe is believed, and any command that needed
  editing is fixed **in the doc** and re-run from the top — never corrected in a summary.
- *Keep an allowance narrow, documented, and armed against its own widening.* State the allowance in
  a docstring, scope it to the narrowest token that makes it true, and plant an arm that must still
  trip through it.
- Unchanged and still in force: **hand-edit `.planning/STATE.md`; run the other GSD state verbs but
  diff every one of them before committing** (W26).

**Still open**

- **DEF-15 is now four plans old and maintainer-gated.** Recommendation for the PR: pay it in one
  reviewed commit (`profile = "black"` + one repo-wide reformat), because the alternative is that
  every future plan re-derives the same workaround.
- Unchanged from Phases 2 and 3, and still PR-review items: nobody has watched the `pptx` or
  `weekly` CI jobs go green (no `gh` here), and nobody has opened a deck in real PowerPoint. The
  `weekly` job's exact command was re-run locally in this plan at **189 passed / 0 skipped**.
- The compass entry flagged as missing in W26 is now written: `WHERE-WE-ARE.md` carries one entry
  covering **all three** Phase 4 plans, with the decisions-and-why log and both known limitations.

## 2026-08-29 (earlier) — W26: the seventeenth integration site, and the state tool's third strike

**Friction observed (v1.3 plan 04-02 — wiring the fourth corpus in, and proving the deck)**

1. **The state tool corrupted `STATE.md` for the THIRD time, and a second verb turned out to share
   the bug.** `state.advance-plan` produced the identical failure W24 and W25 recorded — same
   `{"error": "Cannot parse Current Plan or Total Plans in Phase"}`, same six-insertion mutation
   written *anyway*, truncating `stopped_at` mid-sentence and injecting blank lines **into** a
   markdown paragraph (which silently splits prose into fragments a later reader will not know were
   one sentence). New this time: `requirements.mark-complete` shares the blank-line-injection bug —
   it flipped the checkbox correctly, added a stray blank line to the Deferred list, and did **not**
   update the traceability table its own contract says it updates.
   `roadmap.update-plan-progress` was clean and correct.
   Three occurrences is a tool bug, not bad luck. The rule stops being "diff after every call" and
   becomes a routing rule.
2. **The plan enumerated sixteen integration sites and there were seventeen.** The missing one was
   `test_render.py`'s dead-link guard, which pins cross-corpus hrefs to an allow-list —
   `href.startswith(("work/", "module/", "../"))` — a three-corpus tuple that a fourth corpus
   necessarily fails. Worth logging as a **success**, not just a miss: it failed loud, immediately,
   in the same command as the change, because a previous session had written the guard as an
   explicit allow-list rather than a permissive skip. An allow-list that must be widened is a guard
   that tells you it exists; a `continue` would have published a dead link.
3. **A plan's own MEASURED number had gone stale between planning and execution.** The plan states
   `grep -rl '<section class="nl-records"' content/` returns 4 — measured before plan 04-01
   committed the weekly's own Library, which also carries the strip. It returns 5. The regen scope
   (four files change) was still right, so nothing broke; but "MEASURED, not estimated" has a
   shelf life, and the thing that expires it is *our own previous plan*.

**Rules hardened**

- *Hand-edit `.planning/STATE.md`; never delegate it to `state.*` verbs.* Run the other GSD state
  verbs, but **diff every one of them before committing** — including the ones that report success.
  (Supersedes W24/W25's "diff after any call" with a concrete routing rule, now that we know which
  file is the casualty and that success envelopes do not mean clean writes.)
- *Write cross-cutting guards as explicit allow-lists, not permissive skips.* When a guard cannot
  verify something locally, make it assert the known-good SHAPE and fail on anything else. The cost
  is one line per legitimate extension; the payoff is that adding an integration point announces
  every place that needs to know about it.
- *A measured number in a plan carries the date and the tree it was measured on.* Re-measure before
  relying on one written in an earlier plan of the same phase — our own commits are the most likely
  thing to have invalidated it.

**Still open**

- The compass narrative for Phase 4 is deliberately **not** written yet: this phase's convention
  (set by 04-01, matching Phase 3's) puts the `WHERE-WE-ARE.md` entry at the phase's last plan, so
  **04-03 must carry entries for 04-01, 04-02 and 04-03 together**. Flagged here so it cannot be
  forgotten — an unwritten compass entry is the stale-compass bug on a delay.
- Unchanged from Phases 2 and 3, and still PR-review items: nobody has watched the `pptx` or
  `weekly` CI jobs go green (no `gh` here), and nobody has opened a deck in real PowerPoint. The
  `weekly` job's exact command was run locally at 189 passed / 0 skipped — the strongest local
  evidence available, and still not the same thing as a run.

## 2026-08-29 (earlier) — W25: the nine test modules nobody was running, and the vacuous-diff family closed

**Friction observed (v1.3 plan 03-04 — the weekly deck, values-via-export, and the CI job)**

1. **"A test suite and the job that runs it are two different artifacts" cost us twice in one
   milestone.** W21 was `[pptx]`: no CI job installed the extra, so every pptx module skipped
   itself on every run. This plan found the same shape one layer out and *larger*: nine modules —
   `test_weeklyspec.py` (88 tests, the entire authoring/placement/compose/deck path),
   `test_weekly_blocks.py`, `test_weekly_values.py`, `test_semantic_gate_frozen.py`,
   `test_casespec.py`, `test_compose.py`, `test_swimlane.py`, `test_abstraction_guard.py`,
   `test_excel_adapter.py` — were named by **no** CI job at all. Not skipped. Simply never
   collected. Every green any of them produced during three plans of this phase was a local green.
   The honest reading is that W21's rule was written down and then applied only to the extra that
   happened to trip it, instead of to the class.
2. **64 skips were reported for three plans and nobody read the number.** The baseline line
   `699 passed, 64 skipped` was recorded in three consecutive summaries as though the second number
   were furniture. It was the entire `[excel]` surface excusing itself. One `pip install -e '.[excel]'`
   turned it into `812 passed, 0 skipped` — and the delta is bigger than 64, because a module-level
   `importorskip` reports the whole module as **one** skip entry however many tests it holds. A skip
   count is not a count of skipped tests, which makes it even easier to under-read.
3. **A plan's stated behaviour did not match the live adapter.** The plan said the excel adapter's
   claims carry "the canonical `Sheet!A1<SEP>value` lines". They do not: the claim's text is the
   **cell value**, and the `Sheet!A1<SEP>` prefix is what separates adjacent values in the
   transcript so duplicate values still get distinct, ordered spans. Found by probing the live
   adapter before writing the assertion — which is the only reason the test asserts something true.
   A test written to the plan's wording would have been green-by-adjustment or red-for-nothing.
4. **A grep-shaped acceptance criterion was case-sensitive and the prose was not.** The criterion
   `grep -c 'text-only\|text only' docs/weekly-spec.md` printed `0` against a paragraph whose
   heading said **TEXT-ONLY** in the house's emphatic caps. The criterion was right and the prose
   was fine; only the pair was wrong. Same family as W24's "a criterion binds the file's prose too".
5. **The state tool's *return value* disagreed with what it wrote to disk.** W24 recorded a handler
   that errored *and* mutated; this session hit that again (`state.advance-plan` returned
   `{"error": "Cannot parse Current Plan or Total Plans in Phase"}` having already written six
   lines) — and then hit something sharper. `state.update-progress` returned
   `{"updated": true, "percent": 100, "completed": 10, "total": 10}` and **wrote `percent: 75`**
   into `STATE.md`. A *successful* call whose reported number contradicts the file is worse than a
   failing one, because there is nothing in the outcome to make you look. Caught only because W24's
   rule says to diff the file after **any** state call. Both were reverted from a scratchpad backup
   and `STATE.md` was hand-edited. `roadmap.update-plan-progress` was closer but still needed
   repair: it flipped the phase row to Complete without checking the two remaining plan boxes, and
   inserted blank lines between the plan bullets.

**Rules hardened**

- *A new test module is not done until a CI job names it.* Adding a module without adding it to a
  job is the W21/W25 failure, now observed twice. The `weekly` job exists (`.github/workflows/ci.yml`)
  and asserts **`0 skipped`** with a failure message that names this lesson — so the guard is a job
  step, not a note in a retro.
- *Read the skip count, out loud, in the summary — and treat a non-zero one as an open question,
  never as furniture.* Both the before (`64 skipped`) and after (`0 skipped`) counts are recorded in
  `03-04-SUMMARY.md`. A green whose skip count you did not read is not evidence.
- *Probe the live object before asserting its shape, even when a plan states it.* The plan is an
  intention; the adapter is the fact. (This is CLAUDE.md's "diagnose the live object" applied to a
  planning artifact rather than to a failure.)
- *Write a token-grep criterion and the prose it will read in the same breath* — case included.
- *A tool's return envelope is not evidence of what it wrote.* Extends W24's "diff the file after
  any state call, success **or** failure" with its sharper case: diff it even when the call
  succeeded **and** reported the number you wanted. Where the tool and the file disagree, revert
  from the backup and hand-edit — never reconcile by trusting the envelope.

**Closed by this plan:** the vacuous-diff family (W22's `git diff HEAD` gate) is now fully retired —
every diff-shape guard in the repo resolves the branch point through the one `milestone_base_ref`
fixture, and the CI job that runs them sets `fetch-depth: 0` so they can execute instead of failing
on infrastructure. **Carried unchanged:** DEF-15 (isort/black profile) charged its tax again.

## 2026-08-29 (earlier) — W24: the tool that half-wrote the state file, and the guard that accused the author

**Friction observed (v1.3 plan 03-03 — asset placement + the weekly composer)**

1. **A state-handler failed AND mutated.** `gsd-tools query state.advance-plan` exited with
   `{"error": "Cannot parse Current Plan or Total Plans in Phase from STATE.md"}` — and had already
   written to `STATE.md` before erroring: it *regressed* `stopped_at` to the previous plan's value,
   set `percent: 50` (the true value is 90), and bumped `completed_plans`. An error message that
   reads like "I did nothing" while the file on disk has changed is the worst shape a failure can
   take. Caught only because `git diff` was run on the file afterwards rather than trusting the
   exit. This is W23's rule ("verify a mutation actually applied") pointed the other way: **verify
   that a *failed* mutation did not apply either.**
2. **A guard that was obviously right accused the author.** The editorialization guard — "every
   string on the page is either something the author wrote or a declared connective constant" —
   was first implemented as a plain substring test against the file text. It failed on
   `weekly-full.yml`'s own **block scalar**: YAML folds a multi-line value, so the author's text is
   not a literal substring of the author's file. The tempting fix (allowlist the line) would have
   punched a hole in the guard. The honest fix was to compare through the *faithfulness gate's own*
   normal form, which forgives whitespace and nothing else. Found by running it, not by reasoning
   about it.
3. **A plan-acceptance grep can be satisfied by a docstring.** `grep -c 'PIL\|Pillow\|imghdr'` must
   print 0 — and it went red on a *comment* explaining that the module never uses them. The
   criterion was right (a grep cannot read intent) and the prose had to be rewritten to describe
   the rule without naming the tokens. Worth remembering when writing "no X appears in this file"
   criteria: the file cannot then discuss X.
4. **A mutation's own safety assertion fired on a false positive.** The `_addressed` → `addressed`
   rename script asserted `"_addressed" not in new` — which is true only if you forget that
   `Trace.is_addressed` legitimately contains that substring. The script stopped the write, which
   is the right failure, but the assertion needed to be a word-boundary regex with the known-good
   name excluded.

**Rules hardened**

- *After any GSD state-handler call — success **or** failure — `git diff` the file it owns before
  trusting the outcome.* A non-zero exit is not evidence that nothing was written. (Extends W23's
  "verify a mutation applied" to its mirror image.)
- *A "this token appears nowhere in the file" criterion binds the file's prose too.* Explain the
  rule without naming the token, or the guard fails on its own documentation.
- *A guard's first RED is data about the guard, not only about the code.* When a new guard fires on
  known-good input, fix the comparator to the one the codebase already trusts (here: the
  faithfulness gate's `_normalize`) rather than allowlisting the input.

**Carried unchanged:** DEF-15 (isort/black profile) charged its tax again. W23's backup-copy revert
discipline was followed for both mutations in this plan and cost nothing.

## 2026-08-29 (earlier) — W23: the mutation that mutated nothing, and the revert that ate my work

**Friction observed (v1.3 plan 03-02 — the Weekly Spec load half)**

1. **A mutation observation that was a silent no-op reported a green that meant nothing.** The plan
   requires proving each new guard can fail. The first attempt mutated a test file with a
   `str.replace` whose target string omitted a trailing comma — so nothing changed, the suite passed,
   and the output *looked* exactly like "the guard is vacuous". Taken at face value it would have
   sent us to debug a guard that was fine. This is W21/W22's family again at one more remove: not a
   check that never ran, but a **falsification attempt that never happened**, reported as a result.
2. **`git checkout --` destroyed uncommitted work while reverting a mutation.** Reverting the
   (no-op) mutation with `git checkout -- tests/test_abstraction_guard.py` discarded the *entire*
   uncommitted edit — the denylist additions and the new test — because `checkout` restores the last
   commit, not the pre-mutation state. Ten minutes of re-typing, and the near-miss is worse than the
   cost: had it happened on a larger uncommitted file the loss would have been silent and hard to
   notice.
3. **A guard that is obviously correct can still be the wrong guard.** Two tests were written for
   file-order minting: a whole-document "spans ascend strictly" sweep, and a "the duplicated person
   traces to its own line" assertion. The sweep is the more general-looking one. Under the actual
   mutation it stayed **GREEN** — the stolen span still ascends; the robbed section merely became
   disclosures instead of claims. Only the line-number assertion caught it. Generality is not
   sensitivity, and we would have shipped the weaker one alone if we had not broken it on purpose.
4. **Two plan-acceptance greps could be satisfied while the design got worse.** The plan left
   `_GATE`'s disposition open ("import the promoted one"). The literal reading is a private
   cross-module import, a pattern that exists nowhere in `src/` — and it would have passed every
   stated criterion. Promoting the name honestly cost one extra changed line and is visible in the
   diff, which is the point.
5. **DEF-15 charged its tax again** — unchanged, still maintainer-gated, still costs "is this
   failure mine?" on every plan that touches these files.

**Rules hardened**

- *A mutation script must assert that it mutated something.* Every planted-failure edit now checks
  `new != original` (or a match count) and raises before writing. A falsification attempt that
  silently failed to apply is indistinguishable from a vacuous guard, and the two demand opposite
  responses.
- *Never revert a mutation with `git checkout --` on a file carrying uncommitted work.* Copy the
  file to the scratchpad first (`cp f $SP/f.bak`), mutate, then restore from the backup. `checkout`
  restores the last **commit**, not the last **state**.
- *When two guards look redundant, mutate before deleting one.* Keep both unless a real mutation
  shows they catch the same thing. Here the more general guard was the weaker one.

## 2026-08-29 — W22: the *other* gate that was green because it never ran

**Friction observed (v1.3 plan 03-01 — the weekly block kinds)**

1. **W21's shape repeated, in the most load-bearing file we have.** One plan after learning that a
   test and the job that runs it are different artifacts, we found a guard protecting
   `src/newsletters/semantic.py` — the review gate, the "no auto-publish, ever" hard rule — that
   shelled `git diff HEAD`. That compares the *working tree* to the last commit. It went red on an
   uncommitted edit and green the instant that edit was committed, so in CI's clean checkout it had
   never been able to fail, on any run, since it was written. Two milestones of "the gate is
   byte-frozen" rested on it. The failure mode is identical to W21 and the surface is different: a
   green that means "not run" versus a green that means "nothing to look at". Both are a check
   whose *precondition* silently made it a no-op, and neither was visible from the colour.
2. **We only caught it because the phase was forced to edit the file the guard protected.** If this
   phase had not legitimately needed to extend `semantic.py`, nobody would have looked at that
   assertion at all. That is uncomfortable: the vacuity was found by accident, not by audit.
3. **A guard is not evidence until you have watched it fail.** The replacement was written, went
   green immediately, and *felt* done. It wasn't — a fingerprint function that returned a constant
   would also have been green. Deliberately breaking it (a blank line inside `Surface.publish`)
   turned it red and turned the green into evidence. Notable: the mutation was caught by only one of
   the two halves — inserting a line deletes nothing, so the "nothing was removed" half stayed green
   throughout. Two halves, two failure modes, and neither alone was the protection we thought we had.
4. **Two acceptance criteria in the plan were mutually unsatisfiable as literally written** (a file
   had to contain `merge-base` and must not contain the literal `"HEAD"` — impossible when
   `merge-base HEAD origin/main` is the command). Resolving it by moving the base ref into one
   shared fixture produced a better design than either criterion described. But it cost a real
   detour, and the near-miss is worth naming: the cheap way out is to satisfy the grep and leave the
   duplication.
5. **DEF-15 charged its tax again.** `black --check` fails on both production files this plan
   touched — and failed on them *before* the plan touched them, which took a scratch checkout of the
   base revision to establish. Every plan touching these files pays "is this failure mine?" until
   the repo-wide reformat happens.

**Rules hardened**

- *A guard whose precondition can silently make it a no-op is not a guard.* Before trusting one, ask
  what state it is comparing against and whether that state can ever differ in the environment that
  runs it. `git diff HEAD` in CI is the canonical example: there is never anything uncommitted.
- *Never `HEAD` as a diff base for a freeze — always the milestone base* (`git merge-base HEAD
  origin/main`), resolved in **one** place (`tests/conftest.py::milestone_base_ref`). Two copies of
  a base ref drift exactly as two copies of a normalizer do (Phase 2's "ONE normalizer" rule,
  generalised).
- *A gate that cannot resolve its precondition FAILS — it never skips* — and its message names the
  fix (here: `fetch-depth: 0`). A skip is how W21 happened; a skip is a no-op wearing green.
- *Ship a guard with the mutation that proves it can fail, and record the observed red and green.*
  An unproven guard is a vibe. Where a guard has independent halves, note which half caught the
  mutation — if it is always the same one, the other half is unproven.
- *A refusal test is only as good as its constructing arm.* Assert that the invalid case fails
  **and** that the valid case still builds; otherwise a model that rejects everything is "correct".

## 2026-08-29 — W21: the gate that was green because it never ran

**Friction observed (v1.3 plan 02-03 — the proof in CI)**

1. **Four test modules had been silently skipping in CI for the whole milestone, and the CI was
   green the entire time.** No job installed the `[pptx]` extra, so every pptx module hit its
   `pytest.importorskip` and skipped itself on every push. The signal was there in plain sight — an
   `s` in the log where a `.` belonged — and nobody was reading for it, because *the check was
   green*. Two plans' worth of renderer work was defended by a gate that had never executed a single
   line of it. This is the phase's most RETRO-worthy friction by a distance: it is not a bug in a
   test, it is a bug in what we accepted as evidence.
2. **The negative control was one convenience away from being deleted.** With the writer now
   existing, "two renders are byte-identical" *looks* like proof on its own. It is not: two writes
   inside one wall-clock second are already byte-identical (DOS timestamps have 2-second
   granularity), so without the control the assertion is green whenever the machine is fast. The
   control now carries that sentence inside its own failure message, addressed to whoever next
   thinks it is redundant.
3. **Getting the un-normalized pair honestly took more thought than the assertion did.** The obvious
   route — rebuild an "identical" presentation in the fixture — would have been a second
   implementation of the writer, and the control would have been measuring *it*, not the writer.
   Intercepting the bytes on their way into the normalizer keeps the measurement on the real code
   path; the fixture now raises if it ever captures the wrong number of payloads, so the day the
   writer stops routing through it we get a red instead of a silently hollow control.

**Rules hardened**

- *A test suite and the job that runs it are two different artifacts, and only the second one is
  evidence.* Adding a test behind an optional extra without adding (or extending) the CI job that
  installs it produces a green that means "not run". When a test module can skip itself, the plan
  that adds it owes an assertion that its command runs with **0 skipped** in the environment that
  matters.
- *Read the shape of a green, not just its colour.* `s` where a `.` was expected is a failure
  report. Where a suite is allowed to skip, the count of skips is part of the result.
- *When you need a "before" measurement of your own code, intercept it — never re-implement it.* A
  reconstructed input measures the reconstruction. And make the interception fail loud if it stops
  intercepting, or the control quietly becomes decoration.

## 2026-08-29 (earlier) — Writing the writer: the near-misses were all *one-directional* proofs

**Friction observed (v1.3 plan 02-02 — the writer)**

1. **Two assertions would have been green while proving nothing, for the same reason.** The
   Published-case test asks "no slide carries `NL_DRAFT_WATERMARK`" — written with a top-level scan
   it would have been blind to a watermark nested in a group, i.e. the *exact* W17 hole the whole
   phase exists to close, reintroduced inside the test meant to prove its absence. And SC-3's Draft
   half would pass an unconditional watermark that branded approved work as unreviewed forever.
   Both fixed by writing the inversion and by searching recursively.
2. **I introduced a real isort failure and nearly logged it as pre-existing debt.** The lazy
   `MSO_SHAPE_TYPE` import carried two trailing pragmas, overflowing isort's width. The 02-01 rule
   below saved it: checking `git show b1369e0:src/newsletters/pptx_writer.py` showed the module was
   isort-**clean** before this plan, so this one was mine — while `tests/test_pptx_writer.py`'s
   failure genuinely was DEF-15. Same symptom, opposite verdicts, and only the check tells them
   apart.
3. **The GSD state handlers mangled the records for the third consecutive plan.**
   `state.advance-plan` errored identically ("Cannot parse Current Plan or Total Plans"),
   `state.update-progress` printed 83% while writing `percent: 25` and silently rewrote
   `stopped_at` to an older wording, `state.record-metric` and `state.add-decision` both rejected
   their documented arguments, and `roadmap.update-plan-progress` produced `In Progress|  |` again.
   All repaired by hand.

**Rules hardened**

- *Assert the inversion, or you have not asserted the condition.* Any test of the form "X happens
  when C" needs its sibling "X does **not** happen when not-C". A conditional behaviour proved in
  one direction is indistinguishable from an unconditional one — and for gate-derived behaviour
  (watermarks, publication status) the unconditional version is a product bug, not a test bug.
- *A negative assertion must use the same search the positive one does.* "No watermark anywhere"
  written with a shallower walk than the binder uses is a green that means "I did not look".
- *The pre-existing-failure check cuts both ways.* Run it to avoid paying for inherited debt AND to
  catch debt you just created. Assuming the answer either way is the mistake.

## 2026-08-29 (later) — Promoting a spike: the frictions were a self-contradicting gate, a
## formatter civil war, and the state handlers mangling records again

**Friction observed (v1.3 plan 02-01 — the renderer foundation)**

1. **A plan acceptance criterion contradicted itself.** Task 1 required
   `git diff --exit-code -- tests/fixtures/pptx/` to exit 0 *and* required a docstring edit to a
   file in that directory. Both cannot hold. The intent was obvious from the criterion two lines
   later ("`git diff -- …_author_fixtures.py` touches **only** lines inside the module docstring"),
   so it was resolved in favour of the load-bearing half — *no committed binary changed* — and
   verified with the narrower gate `git diff --exit-code -- 'tests/fixtures/pptx/*.pptx'`. Recorded
   rather than silently "passed": a gate you reinterpret without saying so is a gate you have
   disabled.
2. **`isort` and `black` disagree repo-wide and always have.** The repo declares `isort` in `[dev]`
   but sets no `profile = "black"`, so isort wants grid-wrapped imports and black wants
   vertical-hanging-indent: *any* parenthesized multi-line import fails one of them. Adding one
   import to `test_pptx_determinism.py` therefore produced an "isort failure" that had nothing to do
   with the change — `HEAD` already failed on that file, and on `test_ai_optional.py`,
   `_record_determinism_evidence.py` and (for black) `_author_fixtures.py`. Ten minutes went into
   proving the failure was pre-existing instead of into the work.
3. **The GSD state handlers mangled the records again — the same defect class as 01-02.**
   `state.advance-plan` errored outright ("Cannot parse Current Plan or Total Plans"),
   `state.update-progress` wrote plan counts (3→6, 3→4) while leaving `percent: 25` untouched even
   though it *printed* 67%, `state.record-metric` rejected its documented positional arguments, and
   `roadmap.update-plan-progress` again produced a malformed table row (`In Progress|  |`). All
   repaired by hand.
4. **The plan's frontmatter would have over-claimed a requirement.** `requirements: [WKLY-01]` on a
   plan that renders nothing — following the state step literally would have ticked WKLY-01
   complete two plans early.

**Rules hardened**

- *When two acceptance criteria of the same task contradict each other, satisfy the one that
  protects committed evidence, verify it with a narrower command, and say in the summary that you
  reinterpreted a gate.* Silent reinterpretation is how a gate becomes decorative.
- *Formatter noise is only news if `HEAD` was clean.* Before "fixing" a lint failure on a file you
  touched, run the same check against `git show HEAD:<file>`. If it already failed, log it as
  pre-existing debt and match the house style (**black**, which the repo's own files follow) rather
  than starting a repo-wide reformat inside an unrelated plan. The durable fix — adding
  `[tool.isort] profile = "black"` and reformatting once — is now a named deferred item, not a
  recurring tax.
- *Never let a plan's `requirements:` frontmatter tick a requirement the plan did not deliver.*
  A requirement is complete when its behaviour is provable, not when the last plan mentioning it
  runs. WKLY-01 stays "in progress" in `REQUIREMENTS.md` until 02-03 renders a deck in CI.
- *Treat every GSD state/roadmap handler as needing a diff review.* This is the second consecutive
  phase where they corrupted the files they were asked to maintain. The standing practice is now:
  run the handler, `git diff` the result, repair by hand, and log it — and, when it errors, update
  the file directly rather than leaving the machine-state stale.
- *A promotion out of `tests/` into `src/` is a verbatim move or it is a rewrite.* Promote first,
  diff to prove nothing was tidied (git's rename detection makes this one command), and only then
  add new material — in this case a WHY-first preamble and the shared constants, appended around the
  untouched original. The security review of a zip handler is only cheap while that is true.

## 2026-08-29 — A spike is only evidence if the environment can run it and the clock can move

**Friction observed**

Four things went wrong in v1.3 Phase 1, all of them worth naming rather than smoothing over.

1. **The environment shipped no `.venv` and no `python-pptx`.** The phase's whole premise — "run a
   real double write and commit the measurement" — fails at first contact on a fresh container.
   The plan had predicted it and carried `python -m venv .venv` + `pip install -e
   '.[dev,test,pptx,config]'` as an explicit first task, which is the only reason the spike ran at
   all. (The 2026-07-09 debian-PyYAML friction below did *not* recur: a fresh venv without
   `--system-site-packages` avoids it.)
2. **A same-second double write would have "proved" a byte-stability that does not exist.** DOS
   timestamps in a ZIP have 2-second granularity, so two renders in a tight loop are byte-identical
   *for the wrong reason*. This is not hypothetical: `tests/fixtures/pptx/_author_fixtures.py` has
   asserted since the ADAPT-06 work that "python-pptx does NOT stamp the save-time wall-clock." The
   measurement says it does. The repo had been carrying a false claim, almost certainly produced by
   exactly that probe.
3. **A plan's own acceptance gate counted substrings, not headings.** Plan 01-02's check asserted
   `t.count('## Decision') == 1` over the whole file — but `### Decision…` and `## Decisions Made`
   both contain `## Decision`, so a perfectly good document could have failed the gate (or a bad
   one passed it) on a formatting accident.
4. **The GSD state handlers mangled the records they were asked to update.** In 01-02,
   `roadmap.update-plan-progress` rewrote the phase row with a malformed empty cell and dropped its
   wave detail, appended a per-plan metric row into the middle of a *bullet list* in `STATE.md`
   instead of the metrics table, and replaced a prose `Last session:` paragraph with a bare
   timestamp — orphaning the two lines after it. Each was repaired by hand.

**Rules hardened**

- *A phase whose research finds a missing dependency carries the install as an explicit first
  task* — not as an assumed precondition. "Run the spike" is not an instruction an empty container
  can follow, and an executor that discovers this mid-plan burns a context on setup.
- *A determinism spike must cross a time boundary and ship a negative control, or its green means
  nothing.* `tests/test_pptx_determinism.py` sleeps 3 seconds between writes (crossing the 2-second
  DOS boundary) and asserts **C**: the *un-normalized* pair is NOT byte-equal. Without C, the
  passing assertion B is indistinguishable from two writes landing in the same second. The sleep is
  load-bearing, not incidental.
- *When the measurement contradicts a claim already in the repo, correct the claim in the same
  change* — in place, keeping the original reasoning and stating what changed and why (per
  `CLAUDE.md` §Conventions). Leaving the repo holding two answers is worse than either answer.
- *A gate that means "this heading appears once" must anchor to the line start* (`grep -c '^## …'`),
  never a bare substring count. Plan 01-03's gates were written that way after 01-02 surfaced it.
- *Never trust the GSD state/roadmap handlers' output: after running them, read the modified
  sections and repair the formatting by hand.* The verify-the-subagent rule in `CLAUDE.md` applies
  to the tooling, not just to the agents.

## 2026-07-09 — `pip install -e ".[test,config]"` fails cold on a debian-managed PyYAML

**Friction observed**

On a fresh session container, the documented install failed outright: the environment ships
a debian-packaged PyYAML 6.0.1 with no pip RECORD file, so pip's attempt to upgrade it to
the `[config]` extra's `PyYAML>=6.0.3` aborts the WHOLE install ("Cannot uninstall PyYAML
6.0.1, RECORD file not found") — the package itself never installs, and the baseline test
run is blocked before any work starts.

**Rule hardened**

- *Known-good workaround, recorded here rather than rediscovered per session:*
  `pip install -e ".[test,config]" --ignore-installed PyYAML` installs cleanly (verified:
  `yaml.__version__` → 6.0.3, suite green). If this recurs across sessions, the durable fix
  is a SessionStart hook or a documented bootstrap line in CONTRIBUTING.md — a friction met
  twice without hardening is a bug.

## 2026-07-03 — The published site rotted because publishing had three channels and zero tests

**Friction observed**

Live forensics (v1.2 research doc) found the "deployed" site was a 2-week-stale *hand-pushed*
`gh-pages` snapshot; the automated workflow built a DIFFERENT site (the placeholder `web/` app)
and had failed 4/4 runs — **including run #3 from `main`**, which invalidates the "merging to
main will deploy" assumption the two-gates entry below left standing; and no test anywhere saw
the *assembled* tree, so `/module/…` 404'd live and every work/module page's "Start here"/Home/
fan-out link pointed at a nonexistent corpus-local `index.html`. Each corpus was individually
green; the composition was broken. The repo's own record believed the site was fine.

**Rules hardened**

- *One publish channel, and it republishes only what a human already merged.* The deploy
  workflow re-runs the merge-block gate and the byte-drift checks over the **committed**
  corpora, assembles via the same tested function everything else uses (`publish.assemble_site`
  — never ad-hoc `cp` in YAML), and pushes through the channel with the fewest invisible gates
  (single-commit force-push to `gh-pages`: one visible `contents: write` permission, no
  environment allowlist). Manual `gh-pages` pushes are retired.
- *Test the composition, not just the parts.* The published tree is a first-class test subject
  (`tests/test_publish.py`, PR-blocking): assembled-tree link resolution, committed==fresh for
  ALL corpora, fonts-present, generated-marker. The assembled-tree link test caught the live
  dead-nav bug on its first run — a per-corpus test structurally never could.
- *A "next step: publish" left manual will silently rot.* The 6/19 UAT snapshot was correct the
  day it was pushed and wrong within two weeks. If publishing is a standing intention, it must
  be a workflow, not a memory.

## 2026-07-02 (late) — Pages deploy: a workflow change cannot see a repo-settings gate

**Friction observed**

PR #8 extended the Pages workflow to publish the report corpora and to deploy from the
integration branch — the build succeeded, but the DEPLOY job was rejected: the
`github-pages` environment's protection rule (Settings → Environments, a repo setting,
invisible to the workflow file and to CI) only allows deployments from approved branches.
The /reports/ URLs 404'd while every gate we could see was green; found only when the
Editor-in-Chief asked for the preview.

**Rule hardened**

- *An outward-facing deploy has TWO gates: the workflow (in-repo, we can change it) and
  the environment protection rule (repo settings, maintainer-only).* When shipping a
  deploy-from-a-new-branch change, verify the environment allowlist covers that branch —
  or state plainly in the PR that the maintainer must allow it / merge to an allowed
  branch before the deploy can land. "The workflow is correct" ≠ "the deploy will run."

## 2026-07-02 — Session: v1.1 overnight run (Phases 1–3 shipped; one stall JJ caught live)

**Friction observed**

1. **A background CI-wait stalled the run — three compounding mistakes in one decision.** After
   shipping PR #6's body I gated the merge on a *backgrounded* poll loop: (a) the container
   restarted and killed it — the EXACT failure class already hardened in the 2026-06-18 entry
   ("a completion notification is not liveness"), violated again; (b) the loop used
   unauthenticated `curl` to api.github.com, which returns empty in this environment, so it
   could never succeed; (c) the head commit was docs-only and never triggered CI at all —
   zero check runs would ever appear. JJ caught the silence and flagged it. The gates had
   already been independently re-run locally; only the merge click was pending.
2. **Recurring smaller class, positive note:** the abstraction guard (LANE-03) fired three times
   tonight on genuine leaks (a planned default path, a CLI docstring, a planted self-test) — a
   rule encoded as a test did its job repeatedly where a convention would have silently rotted.

**Friction observed (morning review, from JJ directly)**

3. **The PRs fixed hype but not audience.** The Signals dispatch removed boilerplate and tied
   claims to evidence — and was still unreadable to the person it was for: "I don't understand
   what the shit is going on." The bodies assumed a co-engineer; the reviewer is a CLIENT being
   taught. And the deliverable (the rendered report) wasn't one click away — the Pages deploy
   only published the web app, never the report corpora, so "review" meant reading diffs.

**Rules hardened**

- *The reviewer is a client being taught.* Every PR body now MUST open with a plain-terms
  "Start here" section — what we built / why it matters to you / how to review with clickable
  links, the rendered artifact first. Encoded in ship.md's generate_pr_body + enforced by
  `tests/test_signals_voice.py` (a reverted contract is a RED suite, not a vibe).
- *If the deliverable is visual, deploy it.* The Pages workflow now publishes the rendered
  corpora at `/reports/{rev1,work,module}/` alongside the web app — a review link, not a diff.
- *Never gate forward progress on a background wait.* At a decision point, check external state
  SYNCHRONOUSLY through the authenticated channel (GitHub MCP tools here — plain curl to
  api.github.com is dead in this environment), act on what you find, and move on. Background
  monitors are for *notification*, never for *sequencing*.
- *Before waiting on CI, confirm CI was actually triggered for that SHA* (docs-only commits may
  not trigger it). Waiting on a run that doesn't exist looks identical to a slow run.
- *When local enforced gates are green and CI's jobs are a strict subset of what was re-run
  locally, a docs-only head commit does not block the merge* — verify the post-merge run on the
  integration branch instead.

**Friction observed (deep-review loop, rounds 1–8)**

4. **The milestone shipped functionally but was never formally closed per GSD.** All 4 phases were
   built, verified, and merged (PRs #4–#8) — but there were **no per-phase VERIFICATION/VALIDATION/
   LEARNINGS**, no `MILESTONES.md`, no retrospective, no archive, no tag, and STATE/ROADMAP/PROJECT
   carried internal contradictions (STATE frozen mid-Phase-2 with a "3 plans" metrics table; ROADMAP
   Phase-3 checkboxes unticked and Phase-4 "Plans: TBD"; the ROADMAP five-section criterion vs the
   shipped six-section dispatch). "Green tests + merged PRs" felt like "done", so the GSD close ritual
   — the part that produces the *learning* artifacts — was silently skipped. Shipped ≠ closed.
5. **A self-verifying builder cannot see its own self-consistent blind spots.** The overnight run
   verified every phase against its own plan and passed — yet the drift above (and the R5 "weakest
   link", the R7 unguarded arms, the R8 ontology drift) was invisible to that inline verification
   *because it was self-consistent with the builder's own frame*. It took a **fresh-context, adversarial
   deep-review loop** — reading the live repo with standing lenses (delta-to-reality / drift / total-
   history honesty) rather than re-checking intent — to surface what the builder could not see about
   itself. The code enforces its ontology in tests, but the tests prove enums/verbs disjoint, not the
   *prose*; only an outside read caught the compass still saying "promotion chain".

**Rules hardened**

- *A milestone is not done when the code is green — it is done when it is CLOSED per GSD.* Before
  declaring a milestone complete: per-phase VERIFICATION/VALIDATION/LEARNINGS exist, the compass
  (STATE/ROADMAP/PROJECT/WHERE-WE-ARE) is internally consistent with the live repo, and the
  `audit-milestone → complete-milestone` ritual (archive + RETROSPECTIVE + tag) has run. "Merged PRs"
  is a build signal, not a close signal. (This loop is the retroactive execution of that rule.)
- *Independent, fresh-context review catches what inline verification structurally cannot.* Self-
  verification checks the work against the builder's own frame, so self-consistent blind spots survive
  it. For anything load-bearing (trust invariants, ontology, the promise ledger), run a fresh-context
  review that reads the LIVE object with adversarial lenses — the value it buys is *independence, not
  correctness*. (Generalises "the agent says green ≠ green" from executors to the builder's own
  verification pass.)

## 2026-06-19 — Session: autonomous Phases 8–13 (the cut to UAT)

**Friction observed**

1. **A "sole-mutator" claim that a mutable model didn't enforce.** Phase-13's `Problem` documented
   "transition is the only way state changes" + a human-gated guarantee — but it was a default-mutable
   pydantic model, so `p.state = VERIFIED` bypassed the actor check, the ladder, AND the log. The
   verifier's adversarial probe caught it. Same CLASS as the Phase-7 silent-drop: **a comment/claim
   that the code doesn't actually enforce.** (Also recurred smaller: Phase-9 stale-green — gates run
   before content regen; Phase-12 a publish() attempt the merge-gate correctly blocked.)
2. **A planner subagent died mid-write, leaving truncated + uncommitted plans** (Phase 12). Caught only
   because I audited the plans against the locked decisions and found render+dogfood uncovered + a
   truncated 12-03. The "agent says green ≠ green" rule applied to a *planner*, not just executors.

**Rules hardened**

- *Enforce invariants in CODE, prove by TEST — never in a comment.* A trust guarantee (human-gated, no
  silent drops, faithful, no auto-publish) is real only if a bypass attempt RAISES and a test proves it.
  `Problem.state`/`log` are now `__setattr__`-guarded; the adversarial "try to bypass it" probe is now
  part of verification, not optional. Generalises the Phase-7 lesson to ALL claimed invariants.
- *Audit a returned plan against the locked decisions before executing* — a plan set can be thin or
  truncated (dead subagent). Re-plan/extend to full coverage; don't execute an under-scoped plan.
- *A completion notification is not liveness; gates run AFTER content regen; push every task* — carried
  forward from the 16h stall and reconfirmed across these phases.

## 2026-06-18 — Session: autonomous Phases 5–7 (+ a 16h stall + a silent-drop bug)

**Friction observed**

1. **Background agents stalled silently for ~16h (container idle-reclaim).** Two parallel Phase-7
   Wave-1 executors were dispatched; the remote container was idle-reclaimed while they were
   mid-flight, killing them AND the completion notifications I was waiting on. 07-02 had committed its
   RED test but not `_pbir.py`, so the suite was broken at collection. I sat waiting on notifications
   that would never arrive until the user flagged "16 hours." **Root cause:** trusting the completion-
   notification channel as liveness; it's only live while the container is.
2. **A real silent-drop bug, authored INTO the proof corpus.** The Phase-7 verifier caught that
   `_tmdl.py` didn't know the `model` object type (nor `ref table` lines), so `model.tmdl`'s header +
   `culture`/`defaultPowerBIDataSourceVersion` + table refs were READ then dropped with no unit and no
   `unextracted[]` disclosure — violating the #1 invariant. Worse, the golden test's identity
   (`claims + misses == units`) structurally *couldn't* see it (the dropped lines never became units),
   and `_author_fixtures.py` literally documented "ref lines, which the parser skips" — the corpus was
   authored to match the bug.

**Rules hardened**

- *A completion notification is not a liveness check.* When a background agent has been quiet far
  longer than its peers took, STOP waiting and diagnose the LIVE repo (git log timestamps, run the
  suite) — don't trust silence. Commit+push after EVERY task so a reclaim can never lose work (now in
  every executor brief). Recovered 07-02 inline from its committed RED test rather than re-dispatching.
- *No-silent-drops must be anchored to LINES READ, not units emitted.* A coverage identity over
  emitted units cannot catch a line that's read and dropped before becoming a unit. Parsers now
  DISCLOSE any orphan/unrecognized line (`unparsed:` signal → `_R_TMDL_UNPARSED`), and golden suites
  assert zero `unparsed:` over the corpus + positively anchor previously-leaked content
  (`test_no_line_is_read_but_undisclosed`). Generalises the Phase-4 "verify the persisted object"
  rule to "verify against the SOURCE lines, not just the parser's output."
- *A proof corpus authored around a bug proves nothing.* Treat "the parser skips X" notes in fixtures
  as a red flag, not a given.

## 2026-06-17 — Session: autonomous Phases 2–4

**Friction observed**

1. **Adapter coverage drops are not reconstructable from the `Source` — a silent-drop-on-round-trip.**
   Phase 4's `EmailAdapter` holds its U1–U7 `unextracted[]` entries in an in-memory dict keyed by
   `source.id`. The Phase-4 verifier proved live that persisting a `Source` (JSON round-trip) and then
   calling `distill()` on a *fresh* adapter instance **silently loses the forwarded-rfc822 (U1) drop
   and reports `complete=True`** — a direct violation of the "no silent drops" invariant, just outside
   the same-instance `parse()→distill()` flow the golden test exercises. Body claims still mint
   faithfully, so it didn't block Phase 4 — but **Phases 5/6/7 will copy this adapter pattern**, so the
   flaw would replicate ×3 if not hardened at this fork.

**Rules hardened**

- *Adapter coverage must be reconstructable from the `Source`, not adapter memory.* Before replicating
  the adapter pattern (Phase 5 Excel), the coverage/`unextracted[]` for a `Source` must travel with the
  `Source` (or be recomputable from it), so re-distilling a persisted `Source` cannot silently report
  `complete=True`. **Folded into Phase 5 as task zero** + a round-trip coverage-parity test added to the
  conformance/golden pattern (fresh-adapter `distill()` of a persisted `Source` must equal the original
  coverage). Tracked in `WHERE-WE-ARE.md` (Phase-4 close note).
- *Verify the persisted/round-trip path, not just the same-instance happy path.* Golden/conformance
  suites for any extractor must exercise `model_dump_json → reload → re-derive` and assert coverage
  parity — the same-instance test hid this. (Generalises "the agent says green ≠ green" to "the
  in-memory object ≠ the persisted object.")

## 2026-06-14 — Session: plan Phase 1 + cross-AI review

**Friction observed**

1. **The in-flow plan-checker passed plans that contained a real circular import.** The GSD
   plan-checker and source-grounding passes both green-lit Phase 1's plans, which wired
   `semantic.py` to `import from .distill.locators` while `distill/__init__` eager-imports `ports`,
   which imports back from `semantic` — a `semantic → distill/__init__ → ports → semantic(partial)`
   cycle that breaks `import newsletters` and the Rev1 test tripwire. The plan even *asserted* the
   arrangement was "acyclic." Only an **independent cross-AI review** (`/gsd-review`, fresh-context
   opus) caught it — by *reproducing* the cycle with a minimal package mirror, not by reasoning.
2. **The replan's own consistency sweep left one stray.** After the leaf-module fix, `01-PATTERNS.md`
   still had one executor-facing line saying `import ... from .distill.locators` — the exact
   cycle-causing path. Caught by an independent grep for the old path after the planner reported done
   ("the agent says green" applied to the *replan*, not just the original).

**Rules hardened**

- *Peer-review foundational/typed-contract phases before executing* — the in-flow checker reasons
  about plans; it does not run them. For phases that define import structure, an independent reviewer
  that **reproduces** the failure is worth the extra cycle. (Confirmed: review paid for itself here.)
- *Bake a fresh-interpreter import-order check into acceptance criteria* whenever a phase adds a
  module that a core module must import across a package boundary:
  `python -c "import pkg; import pkg.core; import pkg.subpkg"` (both orders) must exit 0. Now in the
  Phase 1 plans; reusable guard for any package with an eager-`__init__` barrel.
- *After a replan, re-grep for the thing you fixed* — a planner's self-reported consistency sweep is a
  claim; verify the old pattern is gone from **all** artifacts (plans, PATTERNS, SKELETON, RESEARCH).

## 2026-06-14 — Session: publish Rev1 → plan Rev2 with GSD

**Friction observed**

1. **Outward/irreversible actions got blocked by the auto-mode classifier** — publishing a public
   GitHub Pages site, pushing branches, writing permission rules, running an agent-chosen installer.
   Each block was *correct*: the trigger was acting on links/scripts without explicit user intent, or
   self-authorizing external code.
2. **Doc/agent claims didn't match the live repo** — the brief (and a research subagent) described the
   Rev1 spine as present "in `src/newsletters/`", but on this branch `models.py` was still the OKR
   stub; the real spine was on another branch. Caught only by checking the live branch.
3. **Ephemeral container kept threatening to eat work** — repeated Stop-hook nudges to commit/push;
   GSD install + planning would vanish on recycle if not pushed.
4. **`AskUserQuestion` rejected a call** — omitted the required `question` field on each item.

**Rules hardened (now in `CLAUDE.md`)**

- *Interactive until trusted* — never auto-approve outward/irreversible or self-permission actions;
  surface to the human, don't fight the classifier.
- *"The agent says green" ≠ green* — verify subagent/doc claims against the **live repo** before
  building on them (rule born directly from friction #2).
- *Commit + push every stage* — the container is ephemeral; unpushed work is lost work.

**Still open**

- Work-surface interview not done → Phase 11 is a shell.
- `DistillPort` exact contract shape is `[OPEN]` → needs a planning-research cycle before Phase 1 code.
- Home 8-section spec needs confirming in writing before Phase 9.
