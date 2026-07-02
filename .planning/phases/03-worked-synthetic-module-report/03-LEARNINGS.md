---
phase: 3
phase_name: "Worked synthetic Module Report"
project: "Newsletters"
generated: "2026-07-02"
counts:
  decisions: 4
  lessons: 3
  patterns: 2
  surprises: 3
missing_artifacts:
  - "03-PATTERNS.md (pattern_mapper skipped this phase — inline decision; accepted gap, see 03-VERIFICATION)"
  - "Phase-3 UI-SPEC.md (ui_phase toggle unexercised despite ROADMAP 'UI hint: yes' — accepted gap: zero new UI, reuses render.py)"
  - "03-UAT.md (no conversational UAT was run this phase)"
---

# Phase 3 Learnings: Worked synthetic Module Report

> Retroactively extracted (2026-07-02) from the phase paper trail (03-CONTEXT, three PLANs/SUMMARYs),
> the live code (`modulesite.py`, the `--corpus module` parts of `cli.py`, `content/module/`,
> `test_modulesite.py`, `test_module_cli.py`), and git history (`81f8c13`…`bac34ca`; the two
> abstraction-guard fixes `851ccf5`/`e566bfb`; squash-merged as `65bbea8` PR #6). Builds on Rounds
> 1–2 (`01-LEARNINGS`, `02-LEARNINGS`); does not repeat them.

## Decisions

### Generic config discovery — never hardcode the fixture filename
`modulesite.py` DISCOVERS its config via a sorted glob of the single `*.yml` under `content/module/`
(`_discover_config`), rather than the plan's suggested literal `content/module/module-a.yml` default.
The surface slug/title are derived by the composer from the config's own identity at runtime.

**Rationale:** The Phase-1 abstraction guard (LANE-03) denylists every config-specific value — and its
`_SEED_SCHEME` set already contained `module-a` before Phase 3 was written. Any `module-a` literal in
`src/` fails the suite. Discovery keeps the concrete name in config + rendered content ONLY, while a
SORTED glob (first entry) stays deterministic and byte-stable. Behavior is unchanged: no-arg
`build_module_surfaces()`/`build_module_site()` still build the corpus.
**Source:** 03-01-SUMMARY §Decisions, commit `851ccf5`, modulesite.py:67-82

### Own corpus + own ledger, kept separate from rev1/work
The module corpus is self-contained: its own `content/module/` config, its own append-only
`content/module/ids.json` (first ref R-001, keyed by slug `report-module-a`), its own
`content/module/site/`. `build_module_site` is the SOLE ledger writer (compose only reads/assigns —
the 02-03 caller-owns-save decision); `cli.py` routes the module BUILDER through the SAME unforked
`review_blockers` gate — the selector never forks the gate (T-11-13).

**Rationale:** Corpus isolation at the ledger layer preserves the corpus boundary and mirrors
`content/work/` exactly; routing the builder (not the gate) means an unsafe corpus can never bypass
the trust boundary. `cli.py` is extended ADDITIVELY only — rev1/work paths byte-untouched,
`review.py` untouched.
**Source:** 03-CONTEXT §Site build/§CLI, 03-02-SUMMARY, modulesite.py:180-182, cli.py:86-89,140-143

### The planted blocker is a monkeypatched in-memory fixture, never a committed dirty corpus
`test_check_module_blocks_on_planted_blocker` constructs ONE in-memory PUBLISHED surface with an
addressed-but-unentailed trace and monkeypatches `modulesite.build_module_surfaces` to return it —
proving the gate fires nonzero WITHOUT ever committing a dirty corpus (T-03-07).

**Rationale:** A gate that only ever sees clean input proves nothing (the Phase-10/11 norm), so the
blocking direction is mandatory — but the committed `content/module/` must stay clean + Draft. A
monkeypatched fixture gives the blocking proof while keeping the working tree clean (verified: git
status clean after the suite).
**Source:** 03-02-PLAN Task 2, 03-CONTEXT §CLI+gate, test_module_cli.py:35-59,74-96

### Committed == fresh-build (byte-stable committed artifacts)
The rendered `content/module/site/` (12 files) and `content/module/ids.json` are committed built
output, verified byte-identical to a fresh `build_module_site()` before commit and pinned by
`test_committed_equals_fresh_build`.

**Rationale:** The committed==fresh-build norm (Phase 11/12) makes the committed output an auditable,
reproducible artifact — anyone can regenerate it and diff to zero. Requires EPOCH_ZERO everywhere,
sorted inputs, and byte-stable ledger save; the phase inherits all three from the Phase-1/2 spine.
**Source:** 03-CONTEXT §Site build, 03-01-SUMMARY, test_modulesite.py:248-278

---

## Lessons

### A rule from a PRIOR phase out-enforced this phase's OWN plan — rules-as-tests beat planning
The Phase-1 abstraction guard's `_SEED_SCHEME` denylist pre-registered the entire `module-a` scheme
(`module-a`, `area-bem`, `owner-*`, `\beng-\d{2,}\b`, `\btoolset-\d+\b`) BEFORE Phase 3 existed. So
when Phase 3's own plans suggested `config_path="content/module/module-a.yml"` (03-01) and a docstring
naming "the swim-lane module-a config" (03-02), the guard fired on BOTH the plan's suggested defaults —
forcing `851ccf5` (generic discovery) and `e566bfb` (docstring scrub).

**Context:** This is the phase's ontological story: a principle encoded as an executable test in an
earlier phase caught a violation the *planner itself proposed*. The plan was fallible; the rule was
not. A hardened rule-as-test out-enforces planning — it holds against every future edit, including the
plan's own. The right response was to make the source MORE abstract (discover, derive at runtime), never
to relax the guard. (Twin of Round 1's swimlane docstring drift and Round 2's stale-docstring finding —
but here the guard *caught* the drift at build time instead of it slipping through.)
**Source:** commits `851ccf5` + `e566bfb`, tests/test_abstraction_guard.py:114-140, 03-01/03-02 SUMMARY §Deviations

### Confidentiality is a TEST, proven non-vacuous by a planted leak
`test_committed_content_is_synthetic` scans every committed `content/module/` file against a denylist
of real-name SHAPES (representative real-looking tokens + an email-address regex) — and proves the
scanner actually fires by planting `Jean-Luc Picard` / `ops@starfleet.int` and asserting it is caught.
The scan is scoped to authored content (`.yml` + `site/*.html` + `ids.json`), deliberately EXCLUDING
the vendored OFL font-license text (third-party copy would false-positive on foundry names).

**Context:** "Strip the proprietary, preserve the personal" only holds if it is enforced, not trusted.
A denylist that never fires could be silently empty; the planted-leak self-check (Phase-7 "prove it
blocks" norm) makes the clean pass provably meaningful. Scoping matters: scanning vendored license
text would make the guard flaky and erode trust in it.
**Source:** 03-03-SUMMARY §Decisions, test_modulesite.py:307-379

### Shared-ledger-path safety rests entirely on save-idempotence — name it, don't assume it
`build_module_site(out_dir)` saves its ledger to the FIXED `content/module/ids.json`, NOT under
`out_dir`. So every test build re-saves a tracked file. It is safe ONLY because R-001 is already
recorded and `Ledger.save()` is byte-stable (sort_keys + trailing newline), making the re-save
idempotent — a fact 03-03 made load-bearing (snapshots the ledger bytes, asserts unchanged) rather
than assumed.

**Context:** A side effect on a committed path is a hermeticity smell; the honest move was to document
it in the suite docstring + every affected test, turn it into POSITIVE evidence of append-only
stability, and flag the true fix (thread the path through `out_dir`) as out-of-scope future hardening —
not to hide it. Re-verified this round: `git status` clean after tmp builds.
**Source:** 03-03-SUMMARY §Concerns, test_modulesite.py:23-30,248-278

---

## Patterns

### Corpus-mirroring worksurface (the singular-analog build seam)
A new corpus is added by MIRRORING `worksurface.build_work_site` exactly — `Ledger.load` →
`Site.from_surfaces` → `ledger.save()` → `render_surface` per page → `render_library` →
`_emit_fonts` — as a NEW sibling module (`modulesite.py`), never by editing the renderer/composer and
never by putting the build seam in the `compose.py` leaf (which must not import render/site). Reuse is
proven by `git diff --exit-code` on the existing modules.
**When to use:** Adding another corpus/output that wires the same loader→composer→renderer spine over
a different committed input; the analog is singular and explicit, so no PATTERNS.md pass was needed.
**Source:** modulesite.py (whole module), 03-CONTEXT §Site build, 03-01-SUMMARY

### Gate-fires-both-ways (clean-exempt + planted-blocker)
A corpus gate is validated in BOTH directions: the clean corpus exits 0 (often Draft-vacuously) AND a
planted PUBLISHED blocker forces nonzero through the SAME unforked gate. The clean pass alone is
vacuous; the blocking direction is the real proof, and it is built in-memory (monkeypatch) so the
committed corpus stays clean.
**When to use:** Any selector/router that must not let a new input bypass a trust gate.
**Source:** test_module_cli.py:62-96, mirrors test_worksurface's corpus-level pattern (T-11-13)

---

## Surprises

### The abstraction guard denylist was clairvoyant — it named `module-a` a whole milestone early
The `_SEED_SCHEME` frozenset in `test_abstraction_guard.py` (authored in Phase 1) explicitly lists
`module-a`, `area-bem`, and the owner scheme, with a comment: "the `module-a` example itself is
Phase 3 — none of it may appear in Phase-1 source ... so a future paste of the worked config into
source is caught here, not in review." Phase 3 then tried exactly that paste (via the plan's default),
and the Phase-1 guard caught it — as its own comment predicted.

**Impact:** Reframed the whole phase's src/ discipline from "remember to abstract" to "the guard will
tell you the instant you don't." It is the strongest evidence in the repo that the ABSTRACT-EVERYTHING
principle is a live enforced invariant, not an aspiration — a rule written to catch a violation that
did not yet exist, catching it on schedule.
**Source:** test_abstraction_guard.py:114-140, commits `851ccf5`/`e566bfb`

### Two of the three ROADMAP-implied artifacts were consciously skipped — and that was correct
ROADMAP marks Phase 3 "UI hint: yes", yet no UI-SPEC was produced; and no 03-PATTERNS was mapped.
Both are ACCEPTED gaps, not omissions: the phase adds a new *corpus* through the already-specified
Phase-9/10 `render.py` (zero new UI), and its build analog was a single explicit module
(`worksurface.py`, no pattern-mapping needed). The workflow's default artifact set over-fit a
UI/greenfield phase shape this phase didn't have.

**Impact:** A reminder that GSD's artifact checklist is a prompt, not a mandate — the honest move is to
RECORD the skip and why (as an accepted gap), never to retro-fabricate a UI-SPEC for a reuse-only
phase. (This retroactive record IS that honesty.)
**Source:** ROADMAP.md Phase 3 "UI hint: yes"; absent 03-PATTERNS.md / Phase-3 UI-SPEC.md; 03-VERIFICATION §Accepted-Gap Records

### The clean gate proves nothing, and that's the honest headline
Every clean-corpus `check --corpus module` exit-0 in this phase is DRAFT-VACUOUS — the only committed
surface is Draft, so `review_blockers` returns `[]` without inspecting anything. This is not a defect
(the report ships Draft by the no-auto-publish rule) but it means the phase's committed corpus never
positively exercises the gate; all the gate's teeth come from one monkeypatched blocker.

**Impact:** Consistent with Phase 11's caveat and honestly flagged in all three SUMMARYs and the test
docstrings — the discipline of naming a passing-but-vacuous check as vacuous (rather than counting it
as coverage) is itself the lesson, and is why the blocking-direction test is mandatory.
**Source:** 03-02-SUMMARY §Concerns, 03-03-SUMMARY §Concerns, test_module_cli.py:62-72

---
*Learnings extracted: 2026-07-02 (retroactive, deep-review loop Round 3)*
*Extractor: Claude (Bureau Chief)*
