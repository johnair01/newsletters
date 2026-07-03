# Feature Research

**Domain:** Config-driven, module-scope **swim-lane Report composer** — a function that assembles ONE owned module's `Surface(REPORT)` cut across its swim lanes (per-lane KPI strip with start→close Δ, traced findings, owner attribution, fanout stub, honesty panel) from *already-existing traced claims*. The composer **selects / orders / links**; it never authors factual prose.
**Researched:** 2026-07-02
**Confidence:** HIGH on the composer's edge-case contract and the faithful-not-suggestive boundary (grounded in the live spine — `semantic.py`, `templates.py`, `surfaces.md`); MEDIUM on external practitioner norms for workstream status reports (cross-checked against project-management + metric-reporting sources, which are consistent but generic).

> **Scope note.** This studies ONLY the NEW v1.1 capability. The typed spine already ships and is
> **out of scope to re-research**: `Source → Claim(+Trace) → Distillation → Surface`; the
> `Draft → InReview → Published` gate with no auto-publish; the `REPORT` preset with slots
> `[hero, kpi, prose, claims, quote, fanout]`; `KpiItem{label, value, delta, dir}`; `KpiStripBlock`
> and `ClaimsBlock`; the `R-NNN` ledger; and the renderer's claim-beside-trace view + honesty panel.
> Those are the **substrate** the composer stands on and are marked **[substrate]** where relevant.
>
> **Load-bearing constraint (CLAUDE.md — faithful, not suggestive).** The composer is a
> *re-arrangement* of the reviewed record. It may SELECT which claims/KPIs appear, ORDER them, GROUP
> them by lane, and LINK them to evidence. It may NOT write factual prose, editorialise, invent KPI
> values, or synthesise a lane's story. Every anti-feature below flows from this line. The learning
> surface (`surfaces.md`) already set this precedent — the swim-lane composer inherits the same crux.

## Practitioner expectations for a swim-lane / workstream status report

A workstream ("swim lane") status report is a standard project-management artifact. Practitioners
expect, **per lane**: (1) clear **ownership** — one accountable name per lane (RACI); (2) a small set
of **KPIs with movement** — where the metric started the period and where it closed, plus the
direction/size of change; (3) **findings / accomplishments** for the period; and increasingly (4)
**risks / gaps** made explicit rather than hidden. The near-universal delta convention is
**Δ = close_value − start_value**, shown as an absolute (and sometimes relative) change with an
up/down direction. The report is read lane-by-lane, then rolled up across lanes into a weekly (the
`PROJECT.md` "weeklies per swim lane" usage). This maps cleanly onto the existing model: a lane
becomes a `ClaimsBlock` + a `KpiStripBlock` section; `KpiItem.delta`/`dir` carry the movement;
`byline` carries the owner; `missing[]` + honesty panel carry the gaps.

## Feature Landscape

### Table Stakes (Users Expect These)

Missing any of these makes the composed report feel like it isn't actually a swim-lane report.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Per-lane section grouping** — one `KpiStripBlock` + one `ClaimsBlock` per configured lane, in config order | A swim-lane report *is* the per-lane cut; without it you just have a flat report | MEDIUM | The core "section abstraction." Keep it generic: a lane is one instance of a `ReportSection` so project/interview kinds slot in later (`PROJECT.md` unit-of-work model). |
| **Start→close Δ computed at compose time into `KpiItem.delta`/`dir`** | The whole point of a status report is *movement*, not a snapshot | MEDIUM | Δ = close − start, derived by the composer. **No `start`/baseline field is added to `Kpi`** (Key Decision, 2026-07-02) — the composer holds the start value from config/period and computes; the model stays untouched. Direction from the sign; format faithfully (units, +/−). |
| **Traced findings per lane (reuse `ClaimsBlock`)** | Every finding must show its evidence; that's the product's core value | LOW | Pure reuse of `ClaimsBlock` + the renderer's claim-beside-trace. Composer only *selects & orders* existing `Claim`s into the lane's block. |
| **Owner attribution per lane** | RACI: a status report with no accountable owner is noise | LOW | Owner comes from YAML config → surface/section attribution (e.g. lane `byline`/quote `attr`). Never hardcoded. |
| **Config-driven lanes/modules/owners (YAML)** | JJ's fundamental principle — different orgs organise differently; hardcoded lanes = a fixed tool | MEDIUM | The whole milestone's premise. Loader binds lane → `FunctionalGroup` + `Kpi`s/`Objective`s; every loaded value becomes a traced `Claim`/`KpiItem`. Abstraction guard test: no fixture names in `src/`. |
| **`missing[]` routing + honesty panel** | Unsubstantiated material must be shown, never dropped silently (hard rule) | LOW | [substrate] Composer routes any lane finding/KPI it cannot back with a `Trace` into `Surface.missing[]`; the panel already renders it. |
| **Stable `R-NNN` id from the ledger; `Draft` state only** | Identity must be durable; nothing auto-publishes | LOW | [substrate] Composer requests the next `R-NNN` from the append-only ledger and emits a `Draft` `Surface`. It never touches the gate. |
| **Owner quote slot per lane (`QuoteBlock`)** | Status reports carry a named human voice ("owner's read") | LOW | The `attr` is the owner; the quote **text must be a verbatim, sourced quote** (a `Claim`/`Trace`), not composer-authored commentary — see anti-features. |
| **Fanout stub** | The report is the root of the promotion chain (Report → Article → Newsletter) | LOW | [substrate] `FanoutBlock` with links (may be a stub this milestone). |
| **Deterministic, byte-stable output** | Re-composing the same config must produce the same report (like the learning surface's SITE-06 double-render rule) | MEDIUM | Total, stable ordering (config order for lanes; a defined sort key within a lane). No wall-clock, no set-iteration nondeterminism. |

### Differentiators (Competitive Advantage)

Where this composer beats a PowerPoint/Confluence workstream template. Align with Core Value.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Every KPI Δ and every finding traces to its YAML/source** | No status-report tool shows *where the number came from*; this one does, per lane | MEDIUM | The loader makes each loaded value a `Claim`/`KpiItem` traced to its YAML source (or a declared slot). This is the honesty story applied to numbers, not just prose. |
| **Undefined-Δ is a first-class, honest state (not a fake 0)** | Practitioners hate reports that invent a baseline; showing "new this period / no prior value" is *more* trustworthy | LOW | See edge-case contract below. `delta=None, dir=None` renders as "—"/"new", not "0". This is a differentiator *because* competitors silently coerce. |
| **Generic section abstraction (lane / project / interview)** | One composer shape serves three report kinds; orgs aren't boxed into one cut | MEDIUM | Build the `ReportSection` seam now even though only the swim-lane kind ships; project/interview kinds are deferred but must "slot in later" (`PROJECT.md`). |
| **Config-only re-shaping for any org** | Point it at a new team's YAML and get their swim-lane report — no code change | MEDIUM | Enforced by the abstraction-guard test. This is the "not a fixed tool" promise made testable. |
| **Composer is pure select/order/link (audit-clean by construction)** | The composition itself can be trusted because it *cannot* introduce unsourced facts | MEDIUM | The API only accepts already-traced `Claim`s/`KpiItem`s and arranges them. Makes the report as auditable as its inputs. |

### Anti-Features (Commonly Requested, Often Problematic)

Every one of these violates *faithful, not suggestive* or the no-auto-publish / traced-claim hard rules.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Composer writes a lane summary / "executive narrative"** | "Just summarise how the lane did" | Authors factual prose → editorialising; unauditable; breaks the core invariant | Select + order existing traced claims; if a summary is wanted it must itself be a reviewed `Claim`. Leave `prose`/narrative to the human. |
| **Auto-fill a start value / baseline when config lacks one** | "So every KPI shows a Δ" | Invents a fact; makes movement look real when it isn't | Emit `delta=None` (undefined), route a note to `missing[]`, render "new/—". Never fabricate. |
| **Composer flags a lane "at risk" / colours it red by inference** | "Highlight the lanes that need attention" | That's *emphasis/judgement* — the human's job (faithful-not-suggestive) | Show the Δ and direction faithfully; let the reviewer read the status. Status labels must be sourced claims, not composer verdicts. |
| **Add a `start`/`baseline` field to the `Kpi` model** | "Cleaner than computing at compose time" | Deliberately deferred model change (Key Decision); widens the model before we've closed one loop | Composer holds the period-start value and computes Δ; model stays untouched this milestone. |
| **Skip / hide empty or unowned lanes** | "A blank lane looks bad" | Silent omission — the reader can't tell "nothing happened" from "not reported"; hides gaps | Render the lane with an explicit empty/unowned state and route to `missing[]`/honesty panel. Absence must be visible. |
| **Composer promotes/publishes the report when it looks complete** | "It's done, ship it" | Violates no-auto-publish, the single most important invariant | Always emit `Draft`; a human moves the gate. Composer never calls promote/publish. |
| **AI backfills missing findings for a thin lane** | "Fill the gaps so the report is complete" | Fabrication behind a trust surface; AI-optional core forbids AI authority | Thin lane stays thin; gaps go to the honesty panel. AI (if any) may only help *select*, never *author*. |
| **Hardcode a starter set of lanes/modules "for convenience"** | "Ship a working example fast" | Fixture names leak into `src/`; breaks the abstraction guard | Ship the worked example (`module-a`) as **config** in a fixture dir, loaded by the generic composer. |

## The composition-API edge-case contract (the heart of this milestone)

A good composer is defined by how it behaves at the boundaries. These are behaviour requirements, not
nice-to-haves — each has a single, honest, deterministic answer. (Confidence: HIGH — derived from the
live model + hard rules.)

| Input condition | Required composer behaviour | Rationale |
|-----------------|-----------------------------|-----------|
| **Lane with zero KPIs** | Emit the lane section with an **empty `KpiStripBlock`** (or omit the strip but keep the lane heading + claims); do **not** invent KPIs. Note the absence in the panel if a KPI was expected. | A lane can legitimately be findings-only. Absence is data. |
| **KPI with no period-start value (Δ undefined)** | `KpiItem.value` = close value; **`delta=None`, `dir=None`**; render "new" / "—". Route a `missing[]` note ("no start-of-period value for X"). | Δ = close − start is undefined without a start. Never coerce to 0 or fabricate a baseline. |
| **KPI with a start but no close value** | Show the start as context or route to `missing[]` ("no close value for X"); `delta=None`. Do not compute a Δ against a guessed close. | Symmetric to the above; the movement is genuinely unknown. |
| **Unowned lane** | Render the lane with an explicit **"owner: unassigned"** marker; omit/blank the owner quote slot (do not fabricate a quote); optionally route to `missing[]`. | RACI gap must be visible, not hidden. A missing owner is a finding. |
| **Empty lane set (module has no lanes configured)** | Emit a valid `Draft` `Surface` with the hero + an **empty-state** body and an honesty panel stating no lanes were configured. Do **not** error out silently or emit nothing. | A composer that returns nothing is indistinguishable from a crash; the empty state is honest and testable. |
| **Lane finding with no `Trace`** | Do **not** place it in the `ClaimsBlock`; route the text to `Surface.missing[]`. | [substrate hard rule] Every published claim ≥1 Trace; unsubstantiated → `missing[]`. |
| **Duplicate lane ids / duplicate KPI labels in config** | Fail loudly at load time (validation error) rather than silently merging or last-wins. | Ambiguous config is an authoring bug; determinism requires it be caught. |
| **Δ present but direction ambiguous (Δ = 0)** | `delta` shows "0"/"no change", `dir=None` (neither up nor down). | Zero movement is a real, distinct state from "up a tiny bit" or "undefined." |

## Feature Dependencies

```
[Swim-lane binding + traced YAML loader]
    └──requires──> [KpiItem / Claim / Trace types]            (substrate ✓)
    └──requires──> [FunctionalGroup / Kpi / Objective models] (substrate ✓, models.py)

[Module-scope Report composer]
    └──requires──> [Swim-lane binding + traced YAML loader]   (its input)
    └──requires──> [Start→close Δ compute]                    (into KpiItem.delta)
    └──requires──> [Per-lane section grouping / ReportSection abstraction]
    └──requires──> [R-NNN ledger + Draft Surface + REPORT preset] (substrate ✓)
    └──requires──> [missing[] routing + honesty panel]        (substrate ✓)

[Worked synthetic Module Report (module-a)]
    └──requires──> [Module-scope Report composer]
    └──requires──> [Library / renderer]                       (substrate ✓)

[Abstraction guard test] ──enforces──> [Config-driven lanes/owners]
[Δ compute at compose time] ──conflicts──> [start/baseline field on Kpi]  (deliberately excluded)
[Composer authoring prose] ──conflicts──> [faithful-not-suggestive]        (forbidden)
```

### Dependency Notes

- **Composer requires the traced loader:** the composer only *arranges* traced inputs; the loader is
  what turns YAML values into `Claim`/`KpiItem` carrying `Trace`s. Build the loader first.
- **Δ-compute conflicts with a `Kpi.start` field:** by decision, the composer holds the start value and
  computes; adding a model field is the excluded alternative, not a parallel option.
- **Section abstraction enables later kinds:** build `ReportSection` generic now so project/interview
  report kinds slot in without reworking the composer (`PROJECT.md` unit-of-work model).
- **Abstraction guard gates everything config:** the no-fixture-names-in-`src/` test is the executable
  form of "abstract everything"; it must pass before the milestone is done.

## MVP Definition

### Launch With (v1.1)

- [ ] **Traced YAML loader** — lane → `FunctionalGroup`+`Kpi`s/`Objective`s; every value a traced `Claim`/`KpiItem` — the composer's only trustworthy input source.
- [ ] **Module-scope Report composer** — per-lane `KpiStripBlock` (Δ at compose time) + `ClaimsBlock`, owner attribution + quote slot, fanout stub; emits `Draft` `Surface(REPORT)` with `R-NNN`. The milestone.
- [ ] **Full edge-case contract** — zero KPIs, undefined Δ, unowned lane, empty lane set, untraced finding all handled per the table — this is what makes the API *good*, not just present.
- [ ] **Worked synthetic Module Report (`module-a`)** — config in a fixture dir, rendered into `content/`, Library- and gate-visible with claim-beside-trace + honesty panel — proves the whole path.
- [ ] **Abstraction guard test** — no fixture/org names in `src/`; config-driven lane set proven.

### Add After Validation (v1.x)

- [ ] **Signals-voice PR/summary bodies** — `ship` workflow PRs read as dispatches from diff + verbatim gate output (in-milestone stretch; must not weaken any gate).
- [ ] **Relative Δ (%) alongside absolute** — trigger: reviewers ask for percentage movement; keep faithful (only when both start & close exist).
- [ ] **Per-lane risk/dependency section** — trigger: teams want RACI-style risk lanes; must be sourced claims, not composer verdicts.

### Future Consideration (v2+)

- [ ] **Project-kind and interview-kind reports** — deferred by decision; the section abstraction must already accommodate them.
- [ ] **Cross-lane rollup → weekly Newsletter** — the `PROJECT.md` "weekly cut across all swim lanes"; depends on multiple lane reports existing first.
- [ ] **`Kpi.start`/baseline as a real model field** — only if compose-time derivation proves insufficient across many report kinds.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Traced YAML loader | HIGH | MEDIUM | P1 |
| Module-scope Report composer | HIGH | MEDIUM | P1 |
| Start→close Δ at compose time | HIGH | MEDIUM | P1 |
| Edge-case contract (undefined Δ, empty/unowned lanes, empty set) | HIGH | MEDIUM | P1 |
| `missing[]` routing per lane | HIGH | LOW | P1 |
| Generic `ReportSection` abstraction | MEDIUM | MEDIUM | P1 |
| Worked `module-a` report in Library | HIGH | LOW | P1 |
| Abstraction guard test | HIGH | LOW | P1 |
| Owner quote slot (sourced) | MEDIUM | LOW | P2 |
| Fanout stub | LOW | LOW | P2 |
| Signals-voice PR bodies | MEDIUM | MEDIUM | P2 |
| Relative Δ (%) | MEDIUM | LOW | P3 |
| Project/interview report kinds | MEDIUM | HIGH | P3 |

**Priority key:** P1 = must have for the milestone · P2 = should have · P3 = future.

## Competitor Feature Analysis

| Feature | PowerPoint/SlideTeam workstream template | Confluence/Jira status report | Our Approach |
|---------|------------------------------------------|-------------------------------|--------------|
| Per-lane KPI + owner | Manual, hand-typed each period | Semi-automated from Jira fields | Config-driven; loaded values are traced claims |
| Metric Δ | Hand-computed, easily stale/wrong | Auto from tracked fields, no provenance shown | Computed at compose time, **traced to source** |
| Missing/undefined data | Silently blank or faked | Blank or "N/A" | First-class `missing[]` + honesty panel; undefined Δ shown honestly |
| Prose/narrative | Human writes freely | Human writes freely | Composer never authors; select/order/link only |
| Publishing | Email/attach, no gate | Page publish, no evidence gate | `Draft` only; human gate; no auto-publish |
| Reusability across orgs | Copy-paste template | Per-instance config | YAML config, abstraction-guard enforced |

## Sources

- [SlideTeam — Workstream Status Report templates](https://www.slideteam.net/blog/top-10-workstream-status-report-template-with-samples-and-examples) — confirms per-lane KPIs, accomplishments, risks, dependencies, ownership as the expected content set (MEDIUM).
- [Atlassian — Swimlane diagrams: ownership & accountability](https://www.atlassian.com/work-management/project-management/project-planning/swimlane-diagram) — lanes encode clear per-lane ownership (RACI) (MEDIUM).
- [ProjectManager — Swimlane diagram template](https://www.projectmanager.com/templates/swimlane-diagram-template) — swim lane = responsibility grouping (MEDIUM).
- [Ahrefs — dashboard metrics: delta over a period](https://help.ahrefs.com/en/articles/5373022-understanding-the-metrics-in-the-dashboard-overview) — Δ = end-of-period − start-of-period convention (MEDIUM).
- [Datadog — metric change / delta checks](https://www.datadoghq.com/blog/alerting-101-metric-checks/) — delta and no-stable-baseline handling as a recognised concern (MEDIUM).
- Live repo (HIGH): `src/newsletters/semantic.py` (`KpiItem`, `KpiStripBlock`, `ClaimsBlock`, `Surface.missing[]`), `src/newsletters/templates.py` (`REPORT` slots), `docs/surfaces.md` (Report + faithful-not-suggestive precedent), `.planning/PROJECT.md` (milestone scope, Key Decisions).

---
*Feature research for: config-driven swim-lane module Report composer (v1.1)*
*Researched: 2026-07-02*
