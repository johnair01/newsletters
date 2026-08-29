# Weekly Spec — the authored weekly, hand-written into the reviewed record

How a module lead puts a **weekly** — the recurring "here is what happened, in my own words"
deck — into the record by hand, in a PR, with zero AI. The spec file is the source; the package
lifts it through the existing spine (`Source → Claim(+Trace) → Distillation → Surface`) into a
**Draft Report** that moves through the same review gate as everything else, and the `.pptx` deck
is one *rendering* of that record. The weekly reuses `Surface(REPORT)`: the deck is an output
**format**, not a new semantic kind, so `src/newsletters/semantic.py`'s `kind` enum is untouched
by this work (decision **D-01**).

The Weekly Spec is a **sibling** of the [Case Spec](case-spec.md) — not an extension of its
schema. The *mechanism* is reused verbatim (`safe_load` only, newline-normalized file text as the
evidence, `Trace.from_source` spans, root containment, `config:` bound but never claimed); the
*key set* is separate, and lives in its own loader (`newsletters.weeklyspec`). Widening the Case
Spec's exactly-eight-key validator to accept weekly fields would make a Case Spec silently accept
weekly keys **and** a Weekly Spec silently accept case keys — destroying, in both directions, the
strict-schema guarantee that is the whole point of a teaching error.

---

## Writing one

Author a YAML file (data, not code — parsed with `safe_load` only) and open a PR. Every key below
is optional; every absence is disclosed, never fabricated. The comments *are* the schema:

```yaml
week: "2026-W35"                    # the period label. Quote it — YAML types 2026-W35 as a string
                                    # anyway, but 42 or yes would silently stop being your text.
module: "Delivery Platform"         # the module/team this weekly is for. A narrative string.
highlights:                         # NarrativeBlock(tone="highlight") — your words, byte-verbatim.
  - "Cut the release checklist from nine manual steps to two."
  - "Second reviewer joined the rota; no single point of approval left."
lowlights:                          # NarrativeBlock(tone="lowlight") — state them honestly.
  - "The migration slipped a week; the dependency was mine to spot and I did not."
recognitions:                       # RecognitionsBlock — one entry per person.
  - person: "Devi R."               # who.
    reason: "Found the ordering bug the tests were blind to."   # what they did, in your words.
    source: "mail:20260824-rota"    # OPTIONAL. A Source id / message id that evidences it.
                                    # Absent is fine: your word IS the evidence, traced to this
                                    # file — and the missing evidence is disclosed.
team:                               # TeamBlock — who this module is, this week.
  - name: "Devi R."
    role: "Reliability"             # optional; "" when unstated.
    lines:                          # short authored lines. Carried verbatim, never rewritten.
      - "Owns the rota; on call through Friday."
    photo: "headshot-devi"          # OPTIONAL. An `assets:` KEY below — never a file path.
assets:                             # AssetBlock inputs. Field-by-field rules: see "Assets" below.
  lane-throughput:                  # the asset key — how `photo:` and prose refer to it.
    file: "assets/weekly/2026-W35/lane-throughput.png"   # repo-relative, must stay under the root
    sha256: "3b1f0c9a2d5e47b8c0f1a6d3e9b2748c5a0d1f63e874b295c3a7d0e16f28b4c9"
    folder: "Weekly review pack"    # provenance minimum 1/3
    date: "2026-08-24"              # provenance minimum 2/3 — ISO YYYY-MM-DD, quoted
    event: "Friday module review"   # provenance minimum 3/3 — the event label
    link: "https://example.invalid/reports/lane-throughput"  # REQUIRED iff stands_in_for: values
    stands_in_for: "values"         # omit, or "values" for a screenshot standing in for numbers.
                                    # Author-declared. Never inferred from the file or its name.
    caption: "Throughput by lane, week 35."   # optional
    alt: "Bar chart, four lanes, week 35."    # optional
config:                             # org-specific slots: system names, metrics, registries.
  tracker_name: "the tracker"       # NEVER rendered into claims — specifics stay config.
```

## Rules the loader enforces (teaching errors, never silent drops)

1. **Exactly these top-level keys.** The document is a mapping of `week`, `module`, `highlights`,
   `lowlights`, `recognitions`, `team`, `assets`, `config` — and nothing else. An unknown key (a
   typo: `highlight:`, `recognition:`) **fails loudly** rather than dropping what you wrote. A
   spec that quietly ignores a mistyped key is a spec that loses a lowlight.
2. **Narrative fields are strings.** Quote anything YAML would type-coerce — `42`, `yes`, `no`,
   `2026-W35`, `2026-08-24`. A bare `yes` becomes the boolean `True` and stops being your text.
3. **`highlights` / `lowlights` items are carried byte-verbatim.** The composer never summarises
   them, never reorders them by importance, never adds connective prose, never merges two lines
   into one. Faithful, not suggestive: emphasis is the author's job. (Phase 3 ships a planted-
   editorialization guard so this is enforced, not merely promised.)
4. **Every absent or empty field is disclosed** in `Surface.missing[]` and shown to the reviewer —
   including *"no lowlights were authored"*, which is precisely the absence a weekly is tempted to
   hide. Nothing is filled in on your behalf.
5. **`config:` values are bound, never claimed.** They are carried on the typed spec for
   downstream binding and are **never** minted into a `Claim` or rendered into a block, so a
   weekly stays portable across orgs (a test polices this for the Case Spec today; the Weekly
   Spec inherits the same guard).
6. **A recognition with no `source` is still carried** — the author's word is the evidence, traced
   to a real span of this file — **and** its missing evidence is disclosed. Both halves matter:
   dropping the recognition would erase credit; publishing it as if sourced would be a lie.
7. **The spec file is read read-only, and every path it names must resolve under the project
   root.** A path that escapes the root **raises**. This is not a `missing[]` case; it is a
   refusal. `missing[]` is for content that is absent — not for a request the loader will not
   serve.

## What happens to it

`newsletters.weeklyspec.load_weekly_spec(path)` reads the file as **newline-normalized text**
(CRLF folds to LF; otherwise unaltered) into a content-addressed `Source`
(`id` = the repo-relative path, `context="weekly-spec:{rel}"`, `transcript` = that normalized
text, `timestamp=EPOCH_ZERO`). The transcript is the file, so every span, offset and hash
addresses the same normalized text. Each authored value is then minted as one traced `Claim` via
**`Trace.from_source`** — real character spans of *your* file, so the span-containment
faithfulness gate passes on its strict branch, not by structural fallback. YAML is parsed with
**`safe_load`** only, through the existing lazy `[config]` boundary: config is data, not code.

`newsletters.weeklyspec.build_weekly_report(load, author=...)` produces the surface:

- a **`Surface(REPORT)` in Draft** — no auto-publish; the `Draft › In Review › Published` gate
  with a recorded approval is the only path out, exactly as for every other surface,
- the per-lane KPI strip and the traced claims the adapters contribute (a `KpiStripBlock` and a
  `ClaimsBlock`) — the evidence half of the weekly,
- a **`NarrativeBlock` per tone** — one for `highlights`, one for `lowlights` — carrying your
  lines byte-verbatim,
- a **`RecognitionsBlock`**, a **`TeamBlock`**, and one **`AssetBlock` per placed asset**,
- everything you left blank, every recognition without a source, and every asset whose provenance
  was incomplete, listed in **`Surface.missing[]`** and shown to the reviewer.

## The four block kinds

The weekly adds four kinds to the discriminated `Block` union in `src/newsletters/semantic.py`.
Each follows the union's live idiom exactly: a `kind: Literal["<name>"] = "<name>"` discriminator,
an optional `heading`, and `Field(default_factory=list)` for every collection.

## Assets — the evidence record

An asset reaches a slide only because its provenance record was complete. This section is the
record shape and the exact routing for every way it can be incomplete.

## Determinism, and the extras it needs

Loads and builds are deterministic (`EPOCH_ZERO` timestamps, file-order iteration): the same file
always produces the byte-identical record. PyYAML lives behind the `[config]` extra
(`pip install '.[config]'`) and python-pptx behind `[pptx]`; the rest of the spine runs without
either. The deck the weekly renders to is **byte-stable** under the recorded decision in
[`.planning/notes/2026-08-29-pptx-determinism-decision.md`](../.planning/notes/2026-08-29-pptx-determinism-decision.md)
— a declared post-save OPC-zip normalization, scoped in writing to a fixed (python-pptx, zlib)
pair, with the part-content digest as the cross-environment assertion. Two renders of one
reviewed record are the same deck.
