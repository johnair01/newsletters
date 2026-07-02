# Phase 2: Module-scope Report composer - Pattern Map

**Mapped:** 2026-07-02
**Files analyzed:** 3 (1 new module, 1 possible additive extension, 1 new test file)
**Analogs found:** 3 / 3 (all strong; every new file has a live precedent in-repo)

## Headline finding (read this first — it changes the plan)

**The additive `swimlane.py` extension IS needed.** The as-built `SectionBinding`/`KpiItem` does
NOT expose a per-KPI endpoint pairing, so Phase 2 cannot reliably compute `compute_delta(start,
close)` from *what it already emits*. Details in the "Endpoint-pairing finding" section below. The
extension must land on `swimlane.SectionBinding` (a new optional field), **never** on
`semantic.KpiItem` — `semantic.py` is on the forbidden list.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/newsletters/compose.py` (NEW) | service / composer | transform (bindings → Surface) | `src/newsletters/worksurface.py` `build_work_report` | role-match (composed-surface precedent; different input) |
| `src/newsletters/compose.py` — ledger helper | utility | file-I/O (append-only ledger) | `src/newsletters/site.py` `Ledger` + `worksurface.build_work_site` | exact (reuse, do not fork) |
| `src/newsletters/compose.py` — `compute_delta` | utility | transform (pure derivation) | `src/newsletters/adapters/_timestamps.py` `deterministic_timestamp` (pure-fn shape) | partial (no delta precedent exists; mirror pure-fn discipline) |
| `src/newsletters/swimlane.py` (ADDITIVE extension) | model | transform | existing `SectionBinding` / `_bind_kpis` in same file | exact (extend in place, additively) |
| `tests/test_compose.py` (NEW) | test | request-response | `tests/test_worksurface.py` + `tests/test_swimlane.py` + `tests/test_semantic.py` | exact (three complementary test shapes) |
| `tests/fixtures/...` (possible) | test fixture | file-I/O | `tests/fixtures/swimlane/module-x.yml` (Phase-1) | exact |

---

## Endpoint-pairing finding (explicit answer to the CONTEXT question)

**Question:** Does the live `SectionBinding`/`SwimlaneLoad` API expose enough for Phase 2 to pair
each KPI with its two traced period endpoints, or is the additive extension needed?

**What `SectionBinding` exposes today** (`swimlane.py:120-136`):
```python
class SectionBinding(BaseModel):
    heading: str
    kpi_items: list[KpiItem] = Field(default_factory=list)   # semantic.KpiItem: label, value, delta=None, dir=None
    claims: list[Claim] = Field(default_factory=list)        # FLAT list — heading claim + label claims + endpoint claims + all other lane scalars, in file order
    missing: list[str] = Field(default_factory=list)
    unextracted: list[Unextracted] = Field(default_factory=list)
```

**How KPI endpoints are minted today** (`swimlane.py:337-362`, `_bind_kpis`):
```python
elif key == _VALUES_KEY and isinstance(val, list):
    # Period endpoints: each its OWN traced value; display the last (close) endpoint.
    for endpoint in val:
        token, ok = _mint_scalar(endpoint, minter, claims, unextracted)
        if ok:
            value_display, value_present = token, True
...
# delta/dir left None — Phase 2 computes Δ from the two traced endpoints (non-goal here).
kpi_items.append(KpiItem(label=label, value=value_display))
```

**Finding — extension IS needed.** Three concrete reasons derivation from the current output is
unsafe:
1. **No back-reference.** Each period endpoint is minted into the *flat* `binding.claims` list.
   `KpiItem` records only the **close** endpoint's display string in `.value`; the **start**
   endpoint's traced `Claim` is buried among heading/label/other-scalar claims with **no link back
   to its KpiItem**. Nothing pairs a KpiItem to its two endpoint Claims.
2. **Text-matching is ambiguous.** The trap fixture deliberately repeats "a value across two KPIs"
   (`test_swimlane.py` docstring), and endpoint Claims have `text == raw token`. Matching endpoints
   to a KpiItem by claim text is therefore non-unique.
3. **Endpoint count isn't recorded.** A `value:` KPI mints one endpoint; a `values:` KPI mints N.
   Positional slicing of `claims` requires knowing each KPI's endpoint count, which the binding does
   not carry. So positional derivation is fragile and would silently mis-pair.

The locked Δ contract requires **both** endpoints be independently content-addressed Claims *before*
any delta is computed (CONTEXT "The Δ contract"; SUMMARY reconciliation #2). That demands an explicit
pairing.

**Where the extension goes:** a NEW optional field on `swimlane.SectionBinding` carrying each KPI's
ordered traced endpoint Claims, parallel to `kpi_items` (e.g. `kpi_endpoints: list[list[Claim]]` or a
small typed carrier). It MUST NOT touch `semantic.KpiItem` (forbidden — `semantic.py`/`models.py`
frozen). Hard conditions from CONTEXT: **every existing Phase-1 test stays byte-untouched AND green**
(the new field is `default_factory`, so `test_swimlane.py` counts/dumps are unaffected only if the
field defaults empty AND is populated without changing the existing `claims`/`kpi_items` outputs —
verify the read-anchored coverage identity `len(all_claims)+len(all_unextracted)==scalars_walked`
still holds: endpoint Claims must be the SAME objects already in `claims`, referenced — not
re-minted, or the identity at `swimlane.py:494-500` breaks) AND **`test_abstraction_guard.py` stays
green** (no config-specific literal in the new field/keys).

---

## Pattern Assignments

### `src/newsletters/compose.py` (service / composer, transform)

**Analog:** `src/newsletters/worksurface.py` (`build_work_report`, lines 137-227) — the closest
composed-`Surface` precedent. Note the input differs (Phase 2 consumes `SectionBinding[]`, not
`Decision[]`), so mine the *discipline* (traced-or-missing routing, lineage/traces population,
Draft-only), not the exact control flow.

**Module docstring + import discipline** (mirror `swimlane.py:1-63` and `worksurface.py:37-63`):
AI-free, stdlib + pydantic + core modules only. Per CONTEXT: **no `yaml` import** (compose is
loader-agnostic), no `distill`, no `render`, no `models`. Consume `swimlane.SectionBinding` /
`SwimlaneLoad`; use `semantic` block types + `site.Ledger`; `adapters._timestamps.EPOCH_ZERO`.
```python
from __future__ import annotations
from .adapters._timestamps import EPOCH_ZERO
from .semantic import (
    ClaimsBlock, KpiStripBlock, KpiItem, QuoteBlock, FanoutBlock, FanoutLink,
    ProseBlock, Claim, Source, Surface, Review,
)
from .site import Ledger
from .swimlane import SwimlaneLoad, SectionBinding
from .templates import REPORT
```

**Traced-or-missing routing pattern** (copy the *policy* from `worksurface.py:196-227`): every claim
kept on a `ClaimsBlock` must be content-addressed; anything unprovable is routed to `Surface.missing`
and dropped from the block — never fabricated. Phase 1 already did the minting, so compose SELECTS
traced Claims and appends compose-found gaps to `missing[]`:
```python
# worksurface.py:198-221 — the routing shape to mirror (adapted: compose selects, never re-mints)
for claim in block.claims:
    if not claim.evidence:
        report.missing.append(claim.text)   # honest gap, never fabricated
        continue
    ...
    kept.append(claim)
block.claims = kept
```

**Surface construction + `traces` population** (mirror `capture.build_report:101-113` and
`worksurface`'s `traces=distillation.traces`): carry the loader's `Source`(s) onto `Surface.traces`
so claim-beside-trace rendering works in Phase 3.
```python
# capture.py:101-113 — the Surface(...) shape to copy (template=REPORT, Draft review, traces set)
return Surface(
    id=surface_id,
    template=REPORT,                      # templates.REPORT: slots hero/kpi/prose/claims/quote/fanout
    title=title,
    eyebrow=eyebrow or "Report · ...",
    blocks=blocks,
    traces=distillation.traces,           # <-- carry loader Source(s); Phase-3 needs this
    byline=[author],
    review=Review(policy=REPORT.review_policy, author=author),  # Draft by default
)
```

**DETERMINISM TRAP — `Surface.created`** (`semantic.py:526`):
```python
created: datetime = Field(default_factory=_utcnow)   # <-- DEFAULTS TO now(); NONDETERMINISTIC
```
`capture.build_report` / `worksurface.build_work_report` do **not** pass `created`, so they inherit
`now()` — they are NOT byte-stable across composes and are therefore NOT the precedent to copy here.
The deterministic precedent is `Source.timestamp=EPOCH_ZERO` (`worksurface.py:114`,
`swimlane.py:460`). CONTEXT locks it: **pass `created` explicitly** (`EPOCH_ZERO` or the Source's
timestamp) so `model_dump_json` is byte-identical across two composes. This is a genuine deviation
from the composed-surface analog — the analog has the bug this phase must not inherit.

**Block assembly per lane** (config/file order, `swimlane.py:471-477` preserves lane order): per
`SectionBinding` → `KpiStripBlock(heading=lane heading, items=...)` then `ClaimsBlock(claims=lane
claims)`. Block types at `semantic.py:364-403`:
```python
class KpiStripBlock: kind="kpi"; heading: Optional[str]; items: list[KpiItem]
class ClaimsBlock:   kind="claims"; heading="Findings — every claim traced"; claims: list[Claim]
class QuoteBlock:    kind="quote"; text: str; attr: Optional[str]         # sourced-or-omit
class FanoutBlock:   kind="fanout"; heading="What this produced"; links: list[FanoutLink]
class ProseBlock:    kind="prose"; heading: Optional[str]; text=""        # connective tissue ONLY — no numerals
class FanoutLink:    kind: str; title: str; href: Optional[str] = None    # href=None for the stub
```

**`compute_delta(start, close)` — pure-function discipline** (no in-repo delta precedent; mirror the
pure, stateless, argument-only shape of `adapters/_timestamps.deterministic_timestamp:45-61`):
```python
# _timestamps.py:45-61 — the pure-fn contract to mirror (no clock, no state, reproducible)
def deterministic_timestamp(intrinsic: datetime | None) -> datetime:
    if intrinsic is None:
        return EPOCH_ZERO
    ...
```
Apply the locked Δ contract: derive from two traced endpoint values; either endpoint absent →
`(delta=None, dir=None)` + a `missing[]` note (never a fabricated 0); `Δ==0` is honest "no change"
(`dir=None`, delta rendered as computed zero form). Δ lives ONLY in `KpiItem.delta`/`.dir`; it is
never a Claim, never traced, never rendered as a claim.

**Ledger wiring for `R-NNN`** (reuse `site.Ledger`, DO NOT fork — CONTEXT + SUMMARY #3):
```python
# worksurface.build_work_site:417-419 / dogfood.build_site:759-761 — the load→use→save beat
ledger = Ledger.load("content/module/ids.json")   # NEW own ledger; first entry R-001
# ref = ledger.ref_for(slug, "report")            # site.py:111-148 — append-only; R-{:03d}
# ledger.save()                                    # site.py:161-167 — byte-stable JSON
```
`Ledger.ref_for(slug, "report")` → `R-001` on first sight (`_REF_FORMAT` `site.py:69-74`;
`_next_ordinal` = `max(existing)+1`, `site.py:150-159`). Existing ledgers each start their own
`R-001` (`content/rev1/ids.json` and `content/work/ids.json` both have an `R-001` today) — the own
`content/module/ids.json` is consistent with that. **Discretion (CONTEXT):** whether compose calls
`ledger.save()` (writes disk) or only assigns in-memory refs may defer to Phase 3 — note that
`Site.from_surfaces` reads/extends the in-memory ledger but the CALLER owns `save()`
(`site.py:229-235`), so compose can assign refs deterministically without persisting.

---

### `src/newsletters/swimlane.py` (additive extension, model)

**Analog:** the existing `SectionBinding` (lines 120-136) and `_bind_kpis` (lines 291-362) — extend
in place. Add ONE optional `default_factory` field carrying per-KPI ordered endpoint Claims (parallel
to `kpi_items`), populated in `_bind_kpis` by *referencing the Claims already appended to* `claims`
(not re-minting — the read-anchored coverage identity at `swimlane.py:494-500` counts every minted
Claim exactly once). Keep the field name a GENERIC structural term (abstraction guard).

**Hard conditions (verify, do not assume):**
- Re-run `tests/test_swimlane.py` (24-claim / 0-unextracted counts, ordered `_R_*` reasons, byte
  determinism) — must stay green with the file byte-untouched.
- Re-run `tests/test_abstraction_guard.py` — the new field/keys must carry no config-specific value.
- Re-assert the coverage identity after populating the new field.

---

### `tests/test_compose.py` (test) + fixtures

**Analogs (three complementary shapes):**

1. **No-auto-publish / gate proof** — `tests/test_semantic.py:59-101` + `tests/test_worksurface.py:333-364`.
   Prove ON THE COMPOSED SURFACE: composed review state is `Draft`
   (`test_worksurface.py:350-351`, `assert report.gate.value == "draft"`); `publish()` without a
   satisfied policy raises (`test_semantic.py:67-69`); untraced claim blocks
   `open_pull_request()` (`test_semantic.py:88-93`). Adversarial: direct `Review(state=PUBLISHED,
   ...)` raises via the model validator (`semantic.py:279-287`) — prove the publish path the model
   actually enforces raises.
   ```python
   # test_semantic.py:88-93 — untraced-claim block, the shape to reuse on the composed surface
   with pytest.raises(ValueError):
       s.open_pull_request()
   ```

2. **Determinism / byte-equality** — `tests/test_worksurface.py:111-118` (two calls → identical
   `model_dump_json`) and `:319-330` (byte-stable across renders). Apply to compose: same input →
   byte-identical `model_dump_json` across two composes (this is where the `created`=`EPOCH_ZERO`
   fix is proven). Recompute every rendered delta from its two endpoints and assert byte-equality
   (the delta-reproducibility guard standing in for a trace).
   ```python
   # test_worksurface.py:116-118 — the byte-equality assertion shape
   dump = [s.model_dump_json() for s in first]
   assert dump == [s.model_dump_json() for s in second]
   ```

3. **Trust guards / invariant assertions** — `tests/test_worksurface.py:128-200` (every ClaimsBlock
   claim `is_traced` + `trace.is_addressed`; ≥1 routed to `missing[]`) and `tests/test_swimlane.py`
   header invariants. The three new guards this phase lands:
   - **Zero-trace-claim:** any emitted claim with zero traces → fail (mirror
     `test_worksurface.py:172-175`).
   - **All-content-addressed:** any emitted trace `is_addressed == False` → fail (mirror
     `test_worksurface.py:176-179`).
   - **Numeral-free-prose:** any non-`ClaimsBlock` text block (prose/rationale) carrying a digit run
     not verbatim from a traced claim → fail (NEW; no exact analog — scan `ProseBlock.text` for
     un-sourced digit runs, allow-listing config-derived structural labels).
   ```python
   # test_worksurface.py:172-179 — the per-claim traced+addressed assertion pair to reuse
   assert claim.is_traced, f"... untraced — should have been routed to missing[]"
   trace = claim.evidence[0]
   assert trace.is_addressed, f"... trace is not content-addressed"
   ```

4. **Kind-agnostic seam test** (CONTEXT decision): compose a second, non-lane `SectionBinding` kind
   with ZERO composer change — prove the composer consumes `SectionBinding[]` without knowing lanes
   exist. Mirror the "structure/invariant, never a magic value" discipline of
   `test_swimlane.py` (assert from the same parsed fixture the loader read, never a frozen string;
   Pitfall 8). Fixtures follow `tests/fixtures/swimlane/module-x.yml` style if any config is needed
   — but per CONTEXT, compose is testable with **hand-built `SectionBinding`s, no YAML** (SUMMARY
   line 149), so prefer in-memory bindings over a fixture.

**Test import shape** (mirror `test_swimlane.py:36-56`): import the loader's OWN constants/models
rather than inline-duplicating literals (no drift).

---

## Shared Patterns

### Determinism (byte-stable output)
**Source:** `src/newsletters/adapters/_timestamps.py` (`EPOCH_ZERO`, line 42) — reused by
`worksurface.py:114` and `swimlane.py:460`.
**Apply to:** `compose.py` — pass `Surface.created=EPOCH_ZERO` explicitly (the `created` default is
`now()`, `semantic.py:526`); preserve file/config order for lanes+KPIs (no `set()`, no non-total
sort — `swimlane.py:471-477`); make `compute_delta` a pure function of its two arguments.
```python
EPOCH_ZERO = datetime(1970, 1, 1, tzinfo=timezone.utc)   # _timestamps.py:42
```

### Append-only ledger (R-NNN identity)
**Source:** `src/newsletters/site.py` `Ledger` (lines 82-167); wiring beat at
`worksurface.build_work_site:417-419` / `dogfood.build_site:759-761`.
**Apply to:** `compose.py` — `Ledger.load("content/module/ids.json")` → `ref_for(slug, "report")` →
optional `save()`. Reuse, never fork; never hardcode a `"R-NNN"` string.
```python
def ref_for(self, slug, kind, *, issue=None, date=None) -> str:
    if slug in self._data:
        return self._data[slug]["ref"]          # EXISTING — immutable
    n = self._next_ordinal(kind)                # max(existing per-type)+1
    ref = _REF_FORMAT.get(kind).format(n)       # "R-{:03d}" -> R-001 first
    ...
```

### Traced-or-missing honesty routing
**Source:** `src/newsletters/worksurface.py` (`build_work_report`, lines 196-227) — the
content-address-or-`missing[]` policy; `Surface.missing` carrier (`semantic.py:516-520`, str-only).
**Apply to:** every `ClaimsBlock` compose emits, the quote slot (sourced-or-omit + `missing[]` note),
and compose-found gaps (union of lane `missing[]` + compose gaps). Never fabricate.

### No-auto-publish gate (the hard rule)
**Source:** `src/newsletters/semantic.py` — `Review._published_requires_satisfied_policy` (279-287),
`Surface.open_pull_request` untraced-claim refusal (552-564), `Surface.publish` (575-588).
**Apply to:** the composed surface is `Draft`; DO NOT touch the gate — prove it holds via new tests
(the forbidden list bans editing `semantic.py`).

---

## No Analog Found

| File / concern | Role | Data Flow | Reason |
|----------------|------|-----------|--------|
| `compute_delta(start, close)` | utility | transform | No delta-derivation exists anywhere in the codebase — this is a genuinely new trace pattern (SUMMARY "Research Flags", Phase 2). Mirror the *pure-function discipline* of `_timestamps.deterministic_timestamp`, but the logic (two-traced-endpoints → derived Δ, undefined-as-first-class) is new. |
| Numeral-free-prose guard | test | transform | No existing test scans non-`ClaimsBlock` block text for un-sourced digit runs (Hole A). New guard; closest shape is `test_ai_optional.py`'s "read module text, assert forbidden pattern absent" (referenced by `test_abstraction_guard.py:11`). |
| Deterministic `Surface.created` | (composer field) | — | No composed-surface precedent passes `created` — `capture.build_report`/`worksurface.build_work_report` both inherit the `now()` default. This phase is the FIRST to make a composed surface byte-stable; treat as new discipline, not a copy target. |

---

## Metadata

**Analog search scope:** `src/newsletters/` (swimlane, worksurface, capture, site, semantic,
templates, dogfood, adapters/_timestamps), `tests/` (test_worksurface, test_semantic,
test_swimlane, test_abstraction_guard), `content/{rev1,work}/ids.json`.
**Files scanned:** ~14 source/test files read in full or targeted.
**Forbidden-to-edit (CONTEXT/PITFALLS #11, verified):** `semantic.py`, `templates.py`, `models.py`,
`render`, `site.py` (READ-ONLY reuse — do not fork the Ledger), `faithfulness.py`, `coverage.py`,
`conftest.py`, existing tests, `.importlinter`, `ci.yml`. The ONLY writable source targets this phase
are the NEW `compose.py`, the ADDITIVE `swimlane.py` field, and NEW `tests/test_compose.py` (+ any
new fixture).
**Pattern extraction date:** 2026-07-02
</content>
</invoke>
