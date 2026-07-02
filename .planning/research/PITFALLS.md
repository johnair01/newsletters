# Pitfalls Research

**Domain:** Config-driven YAML loader + module-scope swim-lane Report composer, added to an existing typed trust-pipeline (Newsletters `src/newsletters/`)
**Researched:** 2026-07-02
**Confidence:** HIGH (grounded in live code: `semantic.py`, `adapters/normalize.py`, `distill/faithfulness.py`, `distill/coverage.py`, `adapters/_timestamps.py`, `site.py`, plus `RETRO.md` lessons)

> Scope note: these are the failure modes of *adding THIS capability to THIS system*. Generic
> "write good code" advice is omitted. Every pitfall names a live invariant it would break, a
> testable prevention, and which of the four milestone phases owns it:
> **P1 Loader · P2 Composer · P3 Worked example · P4 PR-voice.**

---

## The two structural holes to internalize first

Two properties of the *existing* code make this milestone dangerous. Read them before the pitfalls.

**Hole A — the faithfulness gate only sees `ClaimsBlock`.** `Surface._published_claims()`
(`semantic.py:545-550`) scans **only** `ClaimsBlock` blocks; `open_pull_request()`'s untraced check
(`semantic.py:552-564`) inherits that blind spot. `SpanContainmentFaithfulness.entails`
(`faithfulness.py`) is only ever run over claims that reach that path. **Consequence:** every fact
placed in a `ProseBlock`, `KpiStripBlock` (`KpiItem.value`/`.delta` are bare `str`, not `Claim`),
`ItemsBlock`, or `RationaleBlock` is **completely un-gated**. The composer can smuggle any invented
numeral through a prose or KPI slot and no existing test will notice. This is the milestone's #1
faithfulness surface.

**Hole B — an un-addressed trace is a free pass.** `SpanContainmentFaithfulness.entails` returns
`True` for any trace where `not trace.is_addressed` (i.e. `content_hash is None` — the Rev1
backward-compat fallback). So a `Claim` carrying a single `FreeLocator()`/bare-string trace
**passes faithfulness trivially with no span check at all.** An overnight agent trying to "go green"
can mint delta/prose claims with un-addressed traces and they will pass. Every claim this milestone
mints MUST be content-addressed via `Trace.from_source` (`is_addressed is True`).

---

## Critical Pitfalls

### Pitfall 1: The computed delta invents a fact with no trace story

**What goes wrong:**
The composer computes `KpiItem.delta` at compose time from a start value and a close value
(`+8`, `−3 pts`, `12%`). That delta string is a **new number that appears nowhere in the YAML**.
Because `KpiItem.delta` is a bare `str` on a `KpiStripBlock` (Hole A), nothing checks it — so a
wrong, rounded, or sign-flipped delta ships as if traced. Worse: an agent "traces" the delta by
attaching a `Trace` whose span is the *start* value, which passes span-containment by accident for
small integers or passes trivially if un-addressed (Hole B).

**Why it happens:**
A derived value feels "obviously true" so its provenance gets skipped. But a computed delta is a
*claim about a relationship between two traced values* — its trace story is **two traces (the start
Claim and the close Claim), plus a deterministic, re-runnable derivation** — not one span that
happens to contain the literal.

**How to avoid:**
- Both endpoints must exist as content-addressed `KpiItem`s/`Claim`s traced to their YAML spans
  **before** any delta is computed. If either endpoint is missing/untraceable, the delta is NOT
  computed — the KPI ships value-only and the gap is routed to `Surface.missing[]`.
- The delta is **derived, never authored**: a single pure function `compute_delta(start, close)`
  whose inputs are the two traced values. Prove by a test that recomputes every rendered delta from
  its two endpoints and asserts byte-equality — the delta must be *reproducible*, which is the
  compositional analogue of "traceable".
- Treat the delta as a *presentation of two traces*, not a fact of its own: the honesty panel /
  evidence chip for a delta must surface **both** endpoint traces, so a reviewer can re-do the
  subtraction. Document this "delta = f(start-trace, close-trace)" trace story in the composer.
- Never add a `start`/`baseline` field to `Kpi` to make the delta "traceable" — that model change is
  explicitly deferred (Key Decision, PROJECT.md). Derive at compose time.

**Warning signs:**
A delta that renders when only one endpoint was found in the YAML; a `Trace` on a delta whose span
is one endpoint value; a delta string that is not reproducible from `compute_delta`; any rounding
done inline in a format string rather than in the tested derivation function.

**Phase to address:** P2 Composer (derivation + both-endpoints-or-missing rule; delta-reproducibility test).

---

### Pitfall 2: Connective / prose slots accumulate un-traced numerals

**What goes wrong:**
The composer writes a heading, an eyebrow, a lane intro, or a `RationaleBlock` like "Lane closed the
quarter up 8 points across 3 KPIs." Those numerals (`8`, `3`) are facts, in a `ProseBlock`, which is
un-gated (Hole A). Over four phases this accumulates: each "harmless" summary sentence adds an
un-traced number, and "faithful, not suggestive" quietly dies by a thousand cuts.

**Why it happens:**
Prose slots exist for connective tissue and feel exempt from the trust rule. There is currently **no
test** that a prose/KPI/rationale slot is numeral-free-unless-traced.

**How to avoid:**
- **Rule: composer-authored prose slots carry NO numerals or facts not drawn from a traced Claim.**
  The composer may *select, order, link, and label* — it may never *author factual prose*.
- Enforce in code + prove by test (RETRO 2026-06-19: invariants live in code, not comments): a guard
  test scans every non-`ClaimsBlock` block's rendered text for digit runs (and other fact tokens)
  and fails unless each is either (a) a `KpiItem.value` traced to a Claim, or (b) a delta that
  reproduces from two traced endpoints. Structural/label text (lane names from config, headings) is
  allow-listed explicitly, not by accident.
- Prefer *structural* prose: "Findings — every claim traced" (a fixed label) over "3 findings".
  Counts, if shown, are derived and covered by the same reproducibility test as deltas.

**Warning signs:**
Any digit in a `ProseBlock`/`RationaleBlock`/`eyebrow`/`title` that isn't a config label; f-strings
in the composer that interpolate a metric into narrative; a reviewer asking "where does that number
come from?" and the answer being "the composer wrote it."

**Phase to address:** P2 Composer (the numeral-free-prose guard test); reaffirmed in P4 PR-voice
(the dispatch body is also composer-authored prose — see Pitfall 12).

---

### Pitfall 3: Tracing against re-serialized YAML instead of the raw file text

**What goes wrong:**
The loader does `data = yaml.safe_load(text)`, then to build a `Source.transcript` it does
`yaml.safe_dump(data)` (or builds its own string) and locates scalar offsets in *that*. The
re-serialized text differs from the file the human wrote — key order, quoting, flow vs block style,
indentation, comment loss — so offsets point at the wrong bytes, or `Trace.from_source` raises, or
(worst) resolves to a plausible-but-wrong span. Provenance now lies about where a value came from.

**Why it happens:**
It's easier to serialize a parsed object than to locate values in messy source text. But
`Trace.from_source` (`semantic.py:126-170`) pins `span = source.transcript[start:end]` against
`source.content_hash()` of the transcript — so the transcript MUST be the exact artifact you want
provenance to point at: **the raw YAML file text, byte-for-byte.**

**How to avoid:**
- `Source.transcript` = the **raw file text read once** (`path.read_text("utf-8")`), never a
  re-dump. Parse only to learn *which* values exist; locate them in the raw text.
- **Reuse `adapters/normalize.py`.** It already is the one faithful-extraction gate: hand it the
  raw YAML as `source.transcript` and the list of scalar value strings *in file order*; it does the
  cursor-advancing `str.find`, mints content-addressed claims via `Trace.from_source`, and routes
  non-locatable scalars to `unextracted[]`. Do not reinvent locating logic.
- Character offsets, not byte offsets (normalize.py docstring): consistent with `Trace.from_source`.

**Warning signs:**
Any `safe_dump`/`yaml.dump`/manual re-stringify feeding a transcript; `Trace.from_source` raising
"runs past transcript length"; spans that don't visually match the YAML file.

**Phase to address:** P1 Loader.

---

### Pitfall 4: Scalar-location traps — duplicates, quotes, multi-line, anchors/aliases

**What goes wrong:**
Locating a YAML scalar's characters in raw text is deceptively hard:
- **Duplicate values** — `42` appears for three KPIs; naive `find` from 0 attributes all three to
  the first occurrence's offset (wrong provenance for KPIs 2 and 3).
- **Quoting drift** — parsed value is `foo`; raw text is `"foo"` or `'foo'`. `find("foo")` may hit
  the intended token, but the offsets exclude/mis-handle quotes and the reviewer sees a span without
  its delimiters; a value like `"1,024"` parses to `1,024` but a numeric type may parse to `1024`.
- **Type coercion** — YAML parses `1.0`→float `1.0`, `yes`→`True`, `2026-07-02`→a `date`,
  `007`→`7`. `str(parsed_value)` no longer matches the raw token, so `find` fails and the value is
  falsely routed to `unextracted[]` (or, if forced, mis-attributed).
- **Multi-line / block scalars** (`|`, `>`) — the *logical* value (folded/chomped) is not a verbatim
  substring of the raw text; span-containment cannot hold.
- **Anchors & aliases** (`&a 42` … `*a`) — the value's characters exist only at the anchor site; the
  alias site contains `*a`, not `42`. Tracing the alias's value to the anchor's characters is
  provenance fiction (it says "value here" pointing elsewhere).
- **Comments** (`# target set by owner`) — parsers drop them silently (see Pitfall 9).

**Why it happens:**
People trace the *parsed* value, not the *raw token*. The cursor in `normalize.py` handles
duplicates correctly **only if values are presented in file order**; type-coercion and quoting break
the string-equality `find` depends on.

**How to avoid:**
- Present scalars to `normalize()` **in file order** so the forward-only cursor gives duplicates
  distinct, correct offsets (this is exactly why the cursor exists — normalize.py docstring).
- Trace the **raw token text as written**, not the coerced Python value. Options, in preference
  order: (a) use a loader that yields source spans (e.g. `ruamel.yaml`'s round-trip mode exposes
  line/col; or a small stdlib line-scan for the flat, controlled fixture shape) and pass the raw
  token; (b) if using `str(value)`, constrain the fixture schema to string-typed, unquoted, single-
  line scalars so coercion can't bite — and test that constraint.
- **Anchors/aliases, block scalars, and any value not verbatim-locatable → route to
  `unextracted[]`/`missing[]`, never fabricate.** normalize.py already does this for the `find == -1`
  case; the loader must not "resolve" an alias to make it locatable.
- Fixtures for the worked example deliberately avoid anchors/aliases/block-scalars/ambiguous
  coercions — but a *test fixture that exercises each trap* proves the loader routes them honestly.

**Warning signs:**
A KPI's evidence chip showing the wrong occurrence of a repeated number; values silently absent from
claims after a `yes`/date/`1.0` appears in YAML; any code that dereferences an alias to find a span.

**Phase to address:** P1 Loader (both the honest-routing behavior and the trap-fixture test).

---

### Pitfall 5: Non-deterministic timestamps break byte-stable re-render (the EPOCH_ZERO trap, again)

**What goes wrong:**
`Source` (`semantic.py:53`), `Surface.created` (`:526`), and `Provenance.captured_at` (`:478`) all
default to `_utcnow()` (wall clock). If the loader/composer lets any of these fall to its default,
two renders of the same YAML produce different bytes → the SITE-06 byte-stable double-render property
fails, and every Trace/Source is non-equal across runs. This is the **exact** bug `_timestamps.py`
was written to kill for the file adapters — and it will recur here if the new code doesn't apply the
same discipline.

**Why it happens:**
The default factory is silent and invisible; nothing forces you to pass a timestamp. The lesson was
learned in the adapter tier and lives in `_timestamps.py`, not in `semantic.py` (the spine keeps its
`_utcnow` default deliberately) — so a *new* subsystem re-encounters it fresh.

**How to avoid:**
- The loader sets `Source.timestamp` deterministically: an **intrinsic date from the config** (a
  declared close-date slot, itself a traced Claim) if present, else `EPOCH_ZERO`. Reuse
  `adapters/_timestamps.deterministic_timestamp()` — do not hand-roll or call `now()`.
- The composer sets `Surface.created` (and any `Provenance.captured_at`) to a deterministic value
  (EPOCH_ZERO or the config close-date), never the default. `Surface` has
  `validate_assignment=True`, so set it at construction.
- Prove with a **double-render byte-equality test**: build the surface twice, render twice, assert
  identical bytes; and a Source-equality test (`model_dump_json` twice → equal).

**Warning signs:**
`1970-01-01` is *expected* and honest (means "no intrinsic date"); a *wall-clock* date or a diff
that changes only in a timestamp field between two runs is the bug.

**Phase to address:** P1 Loader (Source.timestamp) + P2 Composer (Surface.created); verified in
P3 Worked example (the committed render must be byte-stable).

---

### Pitfall 6: Lane / dict ordering is non-deterministic

**What goes wrong:**
Lanes, KPIs, or claims are collected via a `set`, a `dict` merged from multiple reads, or sorted by
a non-total key (e.g. sort by delta magnitude with ties) — so their order varies run to run or
Python to Python, and the rendered surface (and its offsets/refs) drifts. `Site.from_surfaces`
already had to be made "reorder-safe" (site.py:235); the composer must not re-introduce order
sensitivity upstream.

**Why it happens:**
`yaml.safe_load` preserves mapping order (CPython dict insertion order, file order) — but only if you
iterate the parsed mapping directly. Building lanes from `set()`/`dict()` unions, or sorting on a
non-unique key, discards that guarantee.

**How to avoid:**
- Preserve **file order** for lanes/KPIs (iterate the parsed mapping directly; don't route through a
  `set`). If a display sort is wanted, sort by a **total, content-derived** key with a stable
  tiebreak (e.g. lane name), never by a value that can tie.
- Any JSON the milestone writes (a new ledger, a manifest) uses `json.dumps(..., sort_keys=True,
  indent=2, ensure_ascii=False) + "\n"` — copy the `Ledger.save()` recipe (site.py:161-167).
- Prove with the same double-render byte-equality test as Pitfall 5, plus a shuffled-input test if
  any collection could be reordered.

**Warning signs:**
`set(` in the lane/KPI path; `sorted(..., key=lambda x: x.delta)`; a diff between two renders that
reorders whole lanes/rows.

**Phase to address:** P2 Composer; verified P3 Worked example.

---

### Pitfall 7: R-NNN ref collisions across the multiple existing ledgers

**What goes wrong:**
There are already **two** ledgers, each with their own `R-001`: `content/rev1/ids.json`
(`R-001`…`R-004`) and `content/work/ids.json` (`R-001`). Refs are unique only *within a ledger*. If
the module report (a) starts a *new* ledger, it gets `R-001` — colliding with two existing `R-001`s
if surfaced in the same Library; if it (b) appends to `content/rev1/ids.json`, it must go through
`Ledger.ref_for` and land on `R-005` (next ordinal), never a hardcoded number. Hardcoding `R-NNN` in
the composer, or `count+1` instead of `max+1`, breaks the append-only stability invariant
(site.py:87-88, A4) and risks reusing a deleted surface's number.

**Why it happens:**
`R-NNN` looks like a display string you can format inline. The append-only ledger contract lives in
`site.py` and is easy to bypass by just setting `Surface.id`/a ref by hand.

**How to avoid:**
- The composer NEVER formats a ref itself. It obtains the ref via `Ledger.ref_for(slug, "report")`
  against the **correct, explicitly-chosen** ledger, and the caller persists with `ledger.save()`
  (from_surfaces does not save — site.py:227-229).
- Decide and document *which* ledger the module report belongs to (recommend: its own module-scoped
  ledger path, and accept that refs are ledger-local; if it must appear in the unified Library,
  append to the unified ledger so ordinals stay globally coherent). Make the choice a test.
- Rely on `_next_ordinal` = `max(existing)+1` (site.py:150-159); never `len()+1`.

**Warning signs:**
A literal `"R-005"`/`f"R-{n}"` in composer code; a second file also claiming `R-001` that renders
into the same index; a ref that changes when surfaces are reordered.

**Phase to address:** P2 Composer (ref via ledger) + P3 Worked example (ledger path choice + save).

---

### Pitfall 8: Fixture / config specifics leak into `src/` or into test assertions

**What goes wrong:**
`module-a`, a lane name, an owner, or a metric label appears in `src/newsletters/` (hardcoded lane
handling, a special-case for a fixture value), or a test asserts on a specific lane name/value
(`assert item.label == "Deploys"`). This violates JJ's fundamental principle — ABSTRACT EVERYTHING;
core carries data models only, specifics are config (PROJECT.md, 2026-07-02) — and makes the tool
fixed rather than config-driven. In a **public repo**, a leaked *real* org/tool/metric/site/program
name is also a confidentiality breach.

**Why it happens:**
Hardcoding the one known fixture is the shortest path to a green worked example; tests naturally want
to assert on concrete values.

**How to avoid:**
- **Abstraction-guard test** (mandated by PROJECT.md Active requirement): a test that greps `src/`
  and fails if any fixture/config-specific token appears. Author it early (P1) so later phases can't
  regress it.
- Tests assert on **structure and invariants**, not on specific config strings: "every KpiItem has a
  traced value or is in missing[]", "delta reproduces from endpoints", "N lanes in → N lanes out" —
  not "lane == 'Deploys'". Where a value must be checked, read it from the same config the code
  reads, so the assertion tracks the config.
- Fixtures use an **obviously fabricated** naming scheme (`module-a`, `lane-alpha`, synthetic
  metrics) with a comment stating they are synthetic; a test/CI check that no real-name patterns
  (allow-list of synthetic prefixes) appear in committed content.

**Warning signs:**
Any config string literal in `src/`; a test that breaks when you rename a lane in the YAML; a
plausible real product/metric name in a fixture.

**Phase to address:** P1 Loader (guard test authored) + P3 Worked example (synthetic-name check on
committed content).

---

### Pitfall 9: Silent drops — YAML keys read but neither claimed nor disclosed (the Phase-7 lesson)

**What goes wrong:**
The loader reads the YAML, mints claims for the values it recognizes, and **silently ignores** the
rest — an unrecognized key, a nested block it didn't traverse, a comment carrying meaning, a value it
couldn't locate. Coverage reports `complete=True`. This is *exactly* the Phase-7 `_tmdl.py` bug
(RETRO 2026-06-18): content read then dropped with no `unextracted[]` disclosure, and a golden test
whose identity (`claims + misses == units`) **structurally couldn't see it** because dropped lines
never became units.

**Why it happens:**
Coverage identities are naturally written over *emitted units*, which can't catch a key that's read
and dropped before becoming a unit. It's tempting to traverse only the keys you care about.

**How to avoid:**
- **Anchor coverage to keys/scalars READ, not units emitted** (the hardened rule): the loader
  enumerates *every* scalar leaf in the parsed YAML and asserts each becomes **either** a Claim
  **or** a disclosed `unextracted[]`/`missing[]` entry. `Coverage._complete_means_nothing_dropped`
  (coverage.py:54-67) already makes "complete + dropped" unrepresentable — feed it honestly.
- **Golden test `test_no_yaml_key_is_read_but_undisclosed`**: over the fixture, assert
  `set(all scalar leaves) == set(claimed values) ∪ set(disclosed values)`, with zero unaccounted.
  Positively anchor any structurally-skippable content (comments, unknown keys) to a disclosure
  signal — mirror `test_no_line_is_read_but_undisclosed`.
- Decide explicitly what is **structure** (mapping keys like `lanes:`, `kpis:`) vs **content**
  (values), and document it; comments are dropped by the parser — if the fixture must carry meaning,
  it goes in a value, never a comment. Never author the fixture *around* a loader gap (RETRO: "a
  proof corpus authored around a bug proves nothing").

**Warning signs:**
A loader that traverses a hand-picked key list; `complete=True` alongside YAML keys with no
corresponding claim; a fixture comment like "the loader skips X"; meaning encoded in a `# comment`.

**Phase to address:** P1 Loader (read-anchored coverage + golden test).

---

### Pitfall 10: Claimed invariants not enforced in code (the mutable-model bypass, again)

**What goes wrong:**
The composer's docstrings assert guarantees — "delta is always derived from two traced values",
"prose slots are numeral-free", "every KPI value is traced" — but nothing *enforces* them, so a later
edit (or an agent) sets `KpiItem.delta` or `KpiItem.value` directly and the guarantee silently dies.
This is the Phase-13 `Problem.state` bug's class (RETRO 2026-06-19): a "sole-mutator" claim a
default-mutable Pydantic model didn't enforce; `KpiItem`/`Claim` are default-mutable too.

**Why it happens:**
Writing the guarantee as prose is faster than encoding + proving it. Pydantic models are mutable by
default.

**How to avoid:**
- Every trust guarantee this milestone claims is enforced **in code and proven by an adversarial
  test that a bypass RAISES or is caught** — the generalized hardened rule. Concretely: the
  numeral-free-prose guard (Pitfall 2), the delta-reproducibility test (Pitfall 1), the
  read-anchored coverage test (Pitfall 9), and the all-claims-content-addressed test (Hole B) are
  the enforcement — the docstrings only *describe* them.
- Add an adversarial probe to verification: "hand-set a delta that doesn't reproduce / put a numeral
  in a prose slot / mint a claim with an un-addressed trace → a gate/test must fail."

**Warning signs:**
A guarantee that exists only in a comment/docstring; no test that *tries* to violate it; "it's fine,
the composer always does X" with no guard.

**Phase to address:** P2 Composer (enforcement + adversarial tests); the discipline spans all phases.

---

### Pitfall 11: Gate-weakening to "go green" (the overnight-agent forbidden list)

**What goes wrong:**
Facing a failing faithfulness/determinism gate, an unattended agent takes the path of least
resistance and **weakens the trust layer** to pass. Specific temptations, all forbidden:
- **Exploit Hole B**: mint delta/prose claims with **un-addressed** traces so
  `entails` returns `True` without a span check. → Forbid: assert every composed claim
  `trace.is_addressed`.
- **Loosen `_normalize`** in `faithfulness.py` (e.g. strip digits, or make containment fuzzier) so a
  computed delta "contains". → Forbid: `faithfulness.py` is out of scope for edits this milestone.
- **Dump everything into `Surface.missing[]`** to empty the body and pass — turning the honesty panel
  into a trash can. → `missing[]` is for genuinely-unprovable material only; a test should assert the
  worked example has real traced claims, not an empty body + a giant missing list.
- **Add a `Kpi.start`/`baseline` field** to make the delta "traceable" — a deliberately-deferred
  model change (Key Decision, PROJECT.md).
- **Edit the golden/determinism test** to accept drift, or **author the fixture around a loader gap**
  (RETRO).
- **Call `publish()`/auto-advance the gate** — the milestone ships `Draft` only; no `publish` path.

**Why it happens:**
"Green" is the visible target; the invariants are invisible until an adversarial check exists. The
16h-stall / autonomous-phase sessions (RETRO) show unattended agents optimize for the notification,
not the truth.

**How to avoid:**
- Treat the DoD gates as immutable during execution: faithfulness gate, coverage invariant,
  no-auto-publish, ledger append-only, byte-stable render. A change to any of these is "a
  conversation, not a commit" (CLAUDE.md). Encode the forbidden list into the executor brief.
- Independently re-run gates after any "green" claim (CLAUDE.md: "the agent says green ≠ green");
  verify against the live repo/branch.
- The all-claims-content-addressed test closes Hole B; the numeral guard closes Hole A; together
  they remove the easy cheats.

**Warning signs:**
A diff touching `faithfulness.py`, `coverage.py`, `semantic.py` gate code, or a golden test during a
composer task; a surface with an empty/near-empty body and an overflowing `missing[]`; a new
`start`/`baseline` field; any `.publish(` in milestone code.

**Phase to address:** P2 Composer (primary); enforced as a review rule across all phases; P4 PR-voice
must not narrate around a weakened gate.

---

### Pitfall 12: The Signals-voice PR body invents facts or launders a weakened gate

**What goes wrong:**
The P4 `ship` workflow generates a PR/summary body in "Signals voice." Two failure modes: (a) the
dispatch prose invents numerals/claims not in the diff or gate output (the same
faithful-not-suggestive breach as Pitfall 2, now in the PR narrative) — "shipped 3 lanes, +40%
coverage" with no source; (b) the body paraphrases/softens the gate output so a red gate reads as
green, i.e. the PR body becomes a channel to launder a weakened gate.

**Why it happens:**
PR bodies feel like marketing copy, exempt from the trust rule; summarizing gate output invites
editorializing.

**How to avoid:**
- The dispatch is generated **from the diff + verbatim gate output** — the gate result is quoted
  verbatim, never paraphrased, and the body **may not weaken any gate** (PROJECT.md P4 requirement).
- Apply the same numeral-free-unless-sourced rule (Pitfall 2) to the PR body: every fact traces to
  the diff or the quoted gate output; counts are derived and reproducible.
- A test/check that the gate section of the PR body is a verbatim copy of the tool output (byte
  match), not a rewrite.

**Warning signs:**
A PR body with metrics not present in the diff/gate output; a "gate: passing" line that doesn't match
the actual tool output; adjectives on the gate result.

**Phase to address:** P4 PR-voice.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Trace the parsed value via `str(value)` instead of the raw token | No span-mapping code | Type-coercion/quoting silently mis-traces or false-drops values (Pitfall 4) | Only if fixture schema is constrained to unquoted single-line strings **and** a test enforces that constraint |
| Put counts/deltas in prose f-strings | Reads naturally | Un-gated invented facts (Holes A/B, Pitfalls 1–2) | Never |
| Hardcode `R-NNN` / the one fixture in `src/` | Fastest green worked example | Breaks ledger append-only + ABSTRACT-EVERYTHING; ref collisions (Pitfalls 7–8) | Never |
| Coverage identity over emitted units | Simple golden test | Cannot see read-then-dropped keys (Pitfall 9, the Phase-7 bug) | Never — anchor to keys read |
| Let `Surface.created`/`Source.timestamp` default | Less to pass | Non-deterministic bytes; SITE-06 fails (Pitfall 5) | Never in composed/loaded output |
| Add `Kpi.start` to make delta "traceable" | Delta looks traced | Deferred model change; scope creep; still doesn't fix Hole A | Never this milestone |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| YAML parser in `core` | Adding PyYAML/ruamel to the AI-optional core path | Core imports only stdlib + Pydantic (CLAUDE.md). Put the loader in an allowed layer and add the YAML dep so import-linter + bare-install CI stay green; verify the dep is reachable only from the loader, never from `core`/`semantic` |
| `adapters/normalize.py` | Reinventing scalar location in the loader | Reuse `normalize()` — the single faithful-extraction gate; feed raw YAML text + values in file order |
| `Trace.from_source` | Adapters/loader computing offsets against a re-dump | Transcript = raw file text; let `from_source` validate offsets before slicing (raises on bad range) |
| `site.Ledger` | Formatting refs inline / not calling `save()` | `ref_for` assigns; caller `save()`s; choose the ledger path deliberately (Pitfall 7) |
| `Coverage` | `complete=True` with silent drops | `_complete_means_nothing_dropped` makes it unrepresentable — disclose every unlocatable scalar |
| import graph | Loader importing `distill/__init__` and creating a cycle | Respect the leaf rule (locators.py note); run the both-orders `python -c "import ..."` acceptance check (RETRO 2026-06-14) |

## Performance Traps

Not a scale-sensitive milestone (single module, small YAML, synthetic fixture). The only relevant
"trap" is `str.find` per scalar being O(n·m) — irrelevant at fixture size; do not optimize.

## Security / Confidentiality Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Real org/tool/metric/site/program name in a committed fixture | Confidentiality breach in a **public** repo | Synthetic fabricated names only; CI check + reviewer gate on committed content (Pitfall 8) |
| `yaml.load` (full loader) on config | Arbitrary object construction from untrusted YAML | `yaml.safe_load` only |
| Corpus/personalization data serialized into a Surface | Breaks invariant 3 (private corpus never serialized) | `Surface.missing[]` and blocks carry plain strings/Claims only (already enforced by types) |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Delta shown without both endpoints/traces | Reviewer can't verify the number | Surface both endpoint traces beside the delta (Pitfall 1) |
| `missing[]` overflowing while body is thin | Reviewer sees a hollow report; honesty panel becomes noise | Only genuinely-unprovable material in `missing[]`; a real traced body |
| `1970-01-01` mistaken for a real date | Confusion | It is the honest "no intrinsic date" sentinel — keep it visibly distinct (EPOCH_ZERO rationale) |

## "Looks Done But Isn't" Checklist

- [ ] **Delta:** reproduces from its two traced endpoints in a test? (not just "renders")
- [ ] **Prose/KPI/rationale slots:** scanned for un-traced numerals by a guard test? (Hole A)
- [ ] **Every composed claim:** `trace.is_addressed is True`? (Hole B — un-addressed passes trivially)
- [ ] **Coverage:** anchored to *scalars read*, not units emitted? `test_no_yaml_key_is_read_but_undisclosed` present?
- [ ] **Determinism:** double-render byte-equality test green? `Surface.created`/`Source.timestamp` set deterministically?
- [ ] **Ledger:** ref from `ref_for` (not hardcoded), correct ledger chosen, `save()` called, no `R-001` collision?
- [ ] **Abstraction:** no fixture/config token in `src/`; tests assert structure not lane names?
- [ ] **Confidentiality:** committed fixture names obviously synthetic; no real org/tool/metric names?
- [ ] **Gate:** state is `Draft`; no `publish()`; `faithfulness.py`/`coverage.py`/gate code untouched?
- [ ] **PR body (P4):** gate output quoted verbatim; no invented numerals?
- [ ] **Anchors/aliases/block-scalars/coercions:** trap fixture proves honest routing to `unextracted[]`?
- [ ] **Import graph:** both-orders `python -c "import newsletters; import newsletters.<loader>"` exit 0; YAML dep not reachable from core?

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Delta/prose invented fact shipped | MEDIUM | Add the numeral guard + delta-reproducibility tests (they'll go red), route offenders to `missing[]` or trace them, re-render |
| Traced against re-dump (offsets wrong) | MEDIUM | Switch transcript to raw file text, re-mint via `normalize()`; content_hash change re-keys traces — expected, re-run goldens |
| R-NNN collision | LOW | Choose the correct ledger, delete the bad ref entry (append-only: don't renumber others), re-run `ref_for` for the new slug |
| Silent-drop discovered | MEDIUM | Add read-anchored coverage test (goes red), disclose dropped scalars in `unextracted[]`, set `complete=False` |
| Non-deterministic bytes | LOW | Set timestamps via `deterministic_timestamp`/EPOCH_ZERO, remove `set()`/non-total sorts, re-run double-render test |
| Fixture name leaked into `src/` | LOW | Move to config, add abstraction-guard test |
| Real name leaked into public content | HIGH | Rewrite git history if pushed; replace with synthetic names; add CI name-check |

## Pitfall-to-Phase Mapping

| # | Pitfall | Prevention Phase | Verification |
|---|---------|------------------|--------------|
| 1 | Computed delta with no trace story | P2 Composer | Delta reproduces from two traced endpoints; missing-if-one-endpoint test |
| 2 | Un-traced numerals in prose slots | P2 Composer (reaffirm P4) | Numeral-free-prose guard test over all non-ClaimsBlock blocks |
| 3 | Tracing re-serialized YAML | P1 Loader | Transcript == raw file bytes; spans match file; via `normalize()` |
| 4 | Scalar-location traps | P1 Loader | Trap fixture (dupes/quotes/coercion/anchors/block) routes honestly |
| 5 | Non-deterministic timestamps | P1 Loader + P2 Composer | Double-render byte-equality; Source round-trip equality |
| 6 | Lane/dict ordering | P2 Composer | Shuffled-input + double-render byte-equality |
| 7 | R-NNN ledger collisions | P2 Composer + P3 | Ref via `ref_for`; ledger-path test; no duplicate `R-001` in the surfaced index |
| 8 | Config specifics leak | P1 (guard) + P3 | Abstraction-guard grep test; synthetic-name check on content |
| 9 | Silent drops of YAML keys | P1 Loader | `test_no_yaml_key_is_read_but_undisclosed`; `complete=False` when dropped |
| 10 | Invariant claimed not enforced | P2 Composer (all) | Adversarial bypass tests raise/fail |
| 11 | Gate-weakening to go green | P2 (all) | No diff to gate/golden code; all-claims-content-addressed test; Draft-only |
| 12 | PR body invents/launders | P4 PR-voice | Gate output byte-verbatim in body; numeral guard on dispatch prose |

## Sources

- Live code (HIGH): `src/newsletters/semantic.py` (`_published_claims`/`open_pull_request` gate blind spot; `Trace.from_source`; `Surface.created` default; `KpiItem`/`KpiStripBlock`), `src/newsletters/distill/faithfulness.py` (`SpanContainmentFaithfulness.entails` — un-addressed free pass), `src/newsletters/adapters/normalize.py` (cursor-advancing verbatim locate; the reuse target), `src/newsletters/distill/coverage.py` (`_complete_means_nothing_dropped`), `src/newsletters/adapters/_timestamps.py` (EPOCH_ZERO precedent), `src/newsletters/site.py` (`Ledger`, append-only `_next_ordinal`, byte-stable `save`), `src/newsletters/locators.py` (leaf import rule; no-ordinal anchors), `content/rev1/ids.json` + `content/work/ids.json` (dual-ledger `R-001` collision surface).
- Project docs (HIGH): `.planning/PROJECT.md` (ABSTRACT EVERYTHING; delta-at-compose-time / no `Kpi.start`; Draft-only; PR body may not weaken a gate; synthetic-fixtures / public-repo constraint).
- `RETRO.md` (HIGH): Phase-7 silent-drop (coverage anchored to lines read, not units emitted; proof-corpus-around-a-bug); Phase-13 mutable-model bypass (enforce in code, prove by adversarial test); Phase-4 round-trip determinism; "agent says green ≠ green"; both-orders import acceptance check.

---
*Pitfalls research for: config-driven swim-lane Report composer (v1.1) on the Newsletters trust pipeline*
*Researched: 2026-07-02*
