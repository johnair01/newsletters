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

### `NarrativeBlock` — the author's voice

```python
class NarrativeItem(BaseModel):
    text: str                                    # the authored line, byte-verbatim
    claim: Optional[Claim] = None                # the traced claim carrying that text

class NarrativeBlock(BaseModel):
    """Authored highlights / lowlights — the author's voice, never summarized."""
    kind: Literal["narrative"] = "narrative"
    heading: Optional[str] = None                # e.g. "Highlights" / "Lowlights"
    tone: Literal["highlight", "lowlight"] = "highlight"
    items: list[NarrativeItem] = Field(default_factory=list)
```

One block per tone. `NarrativeItem.text` is what the author typed; `claim` is the same text as a
traced `Claim`, so the rendered line and its evidence never diverge.

### `RecognitionsBlock` — credit, with or without a source

```python
class Recognition(BaseModel):
    person: str
    reason: str                                  # what they did, in the author's words
    evidence: list[Trace] = Field(default_factory=list)   # empty ⇒ disclosed in missing[]

class RecognitionsBlock(BaseModel):
    kind: Literal["recognitions"] = "recognitions"
    heading: Optional[str] = "Recognitions"
    recognitions: list[Recognition] = Field(default_factory=list)
```

`evidence` may legitimately be empty — rule 6. The recognition is still carried and the absent
evidence is disclosed; neither half is optional.

### `TeamBlock` — who the module is, this week

```python
class TeamMember(BaseModel):
    name: str
    role: str = ""
    lines: list[str] = Field(default_factory=list)        # short authored lines
    photo: Optional[str] = None                           # an `assets:` KEY, never a path

class TeamBlock(BaseModel):
    kind: Literal["team"] = "team"
    heading: Optional[str] = "The team"
    members: list[TeamMember] = Field(default_factory=list)
```

`photo` holds an asset **key**, not a path, so a team photo goes through the same provenance
routing as every other placed image instead of around it.

### `AssetBlock` — one placed asset

```python
class AssetBlock(BaseModel):
    """One placed asset. It is here ONLY because its provenance record was complete."""
    kind: Literal["asset"] = "asset"
    heading: Optional[str] = None
    asset: AssetRecord                                     # REQUIRED — see the invariant below
    caption: Optional[str] = None
    evidence: list[Trace] = Field(min_length=1)            # ≥1 enforced by the TYPE, not convention
```

**The invariant: `asset` is required, not optional.** There is no `AssetBlock` without an
`AssetRecord`, and no `AssetRecord` without its provenance minimums — so "an asset without
provenance reached a `Surface`" is **unrepresentable** rather than merely policed by a check
somebody can forget to call. This is the same move `GlossaryTerm.definition: Claim` already makes
in this codebase (faithfulness enforced *by the type*, not by a reviewer's diligence), and it is
the type-level half of decision **D-02**.

**The same move covers `evidence`.** `Field(min_length=1)` makes an `AssetBlock` with zero traces
fail Pydantic validation at construction — an asset the record does not vouch for is
*unrepresentable*, not merely unconventional. The loader satisfies the minimum by minting the ≥1
`Trace` into the asset record at placement time (last routing row below); a code path that tries
to place an asset without doing so gets a teaching `ValidationError` naming the empty field, never
a traceless block on a surface. Note the contrast with `Recognition.evidence`, which **may** be
empty by design (rule 6): a recognition without a source is still credit owed and is carried with
its absence disclosed, while an asset without a trace is a picture nobody vouched for and must not
exist at all.

### Their place in the union

The four join `Block = Annotated[Union[...], Field(discriminator="kind")]` in `semantic.py`,
which now carries **fifteen** members — the count pinned by
`tests/test_weekly_blocks.py::test_block_union_has_fifteen_members`, so the number in this
sentence is a test, not a claim. The discriminator values are `"narrative"`,
`"recognitions"`, `"team"` and `"asset"` — each declared as the member's `kind` `Literal`, so
round-tripping a `Surface` through JSON resolves the right model without guessing.

### The dispatch contract: every kind renders, or the dispatch fails loud

`render.py`'s `_block_html` is an `isinstance` chain that used to end in a bare `return ""`.
Before this phase every one of the union's members had a branch, so that fall-through was
**unreachable** — it was not a live defect. Adding four kinds without four branches is exactly
what would have made it reachable, and
it would fail in the worst available way: a block that was authored, traced and reviewed would
render as the empty string, with no error anywhere. A surface silently missing its lowlights is
the precise failure this product exists to prevent.

So the contract, written down before the code existed and now shipped: **Phase 3 added four
branches AND converted the fall-through into a teaching `raise` that names the unhandled
`block.kind`.** A new kind renders under `docs/design-system.md` tokens, or the dispatch fails
loud. Both halves are asserted in `tests/test_weekly_blocks.py`: the coverage test drives its
cases from `typing.get_args(Block)`, so a member added without a branch fails there, and the
refusal is exercised by calling `_block_html` directly with a non-member (the only way to reach a
fall-through that stays unreachable by construction).

The classes each new block reuses — named here so Phase 3 had **no visual discretion**
(`--radius: 0`, existing tokens, no new CSS):

| Block | HTML |
|-------|------|
| `NarrativeBlock` | `div.block` + `h3.block-h` + one `div.item` per line: the tone label in `span.sg-tag.cat`, the verbatim text in `div.bo` |
| `RecognitionsBlock` | `div.block` + `h3.block-h` + one `div.item` per recognition: `div.ti` the person, `div.bo` the reason |
| `TeamBlock` | `div.block` + `h3.block-h` + one `div.chapter` per member: `div.t` the role, `div.ti` the name, `div.bo` the short lines |
| `AssetBlock` | `div.block` + `figure.diagram` with `div.dh` the heading and `<figcaption>` the caption |

## Assets — the evidence record

An asset reaches a slide only because its provenance record was complete. This section is the
record shape and the exact routing for every way it can be incomplete.

```python
class AssetRecord(BaseModel):
    """A content-addressed file plus its provenance. A missing minimum ⇒ missing[], not a slide."""
    key: str                        # the spec-local handle (the `assets:` mapping key)
    file: str                       # repo-relative path, root-contained
    sha256: str                     # content address of the FILE BYTES (hashlib.sha256)
    folder: str                     # provenance minimum 1/3
    date: str                       # provenance minimum 2/3 — ISO-8601 YYYY-MM-DD
    event: str                      # provenance minimum 3/3 — the event label
    link: Optional[str] = None      # REQUIRED iff stands_in_for == "values"
    stands_in_for: Optional[Literal["values"]] = None
    caption: Optional[str] = None
    alt: Optional[str] = None
```

**Why the record is the evidence, and not the image.** `Source.transcript` is a `str`, and
`Source.content_hash()` hashes that string — so **an image can never be a `Source`**. Any design
that tries to make the binary the evidence fights the spine. Instead the *asset record text* is
the `Source`, and the image's identity lives inside it as the `sha256` hex string. That hash is a
literal substring of the record, so it traces verbatim like any other field via
`Trace.from_source`, and the span-containment gate keeps its teeth over the provenance claims.

**Why `stands_in_for` is author-declared and never inferred.** Deciding "is this a BI screenshot
standing in for values?" from a filename, a folder or the image itself would be the composer
forming an opinion about content — the exact instinct faithful-not-suggestive forbids. The author
declares it; the loader enforces the consequence (a deep link, or the asset is not placed).

### The routing — no discretion left to the implementer

| Condition | Outcome | Disclosure |
|-----------|---------|------------|
| any of `folder` / `date` / `event` absent or empty | not placed; no `AssetBlock` minted | `asset {key!r}: provenance field {field!r} is absent — the minimum is folder + date + event label; disclosed, never placed` |
| `stands_in_for == "values"` and `link` absent or empty | not placed | `asset {key!r}: a screenshot standing in for values requires a deep link to the report; disclosed, never placed` |
| `file` missing on disk, or its `sha256` ≠ the recorded value | not placed | `asset {key!r}: file {file!r} does not match its recorded content address — refusing to place a file that is not the one the record describes` |
| `file` path escapes the project root | **`ValueError`** — fail loud, **not** `missing[]` | mirrors `casespec.load_case_spec`'s root containment: a refusal, not an absence |
| all three minimums present, the link present when required, and the hash matches | an `AssetBlock` is minted, with ≥1 `Trace` into the record | — |
| `team[].photo` names no `assets:` entry, or names an asset that was **not placed** | the member is carried; no photo is rendered | `team member {name!r}: photo key {key!r} names no placed asset — the member is carried, the photo is not` |
| a recognition `source:` that resolves to no known `Source` | the recognition is carried with `evidence=[]`, exactly as if `source:` were absent (rule 6) — **never** a fabricated `Trace` | `recognition for {person!r}: source {source!r} does not resolve to a known Source — carried, with the unresolvable id disclosed` |

The third row is the substitution case: a record that describes image A while image B sits on
disk. Placing it would publish a picture the record does not vouch for, so the content address is
checked at placement time, not trusted from authoring time.

The last two rows route the *references* into and out of this record, so no authored-input failure
mode is left to implementer discretion. A dangling `photo:` key is a `missing[]` disclosure, not a
teaching error: unlike a mistyped top-level key (which risks dropping authored content), the
member and their lines are fully carried — only the photo, which the provenance routing above may
legitimately withhold anyway, is absent, and inventing or guessing an image would be worse than
disclosing its absence. An unresolvable recognition `source:` gets the *absent-source* treatment
rather than a minted empty `Trace` or a silent field drop: a `source:` that resolves to nothing is
not evidence, and pretending otherwise — in either direction — would fabricate or erase exactly
what `missing[]` exists to surface. The one difference from a truly absent `source:` is the
disclosure text, which names the unresolvable id so the author can fix the typo.

**Determinism of placed images** (measured in `01-RESEARCH`): media parts are numbered in add
order, so iterating `assets:` in **spec file order** keeps `ppt/media/image1..N` stable across
renders; and two byte-identical images produce **one** media part, because python-pptx
content-deduplicates.

**The deck this milestone ships is text-only — a decision, not an oversight (v1.3 Phase 3).** The
measurement above is *recorded but not yet consumed*: the writer (`src/newsletters/pptx_writer.py`)
has **no `add_picture` path at all**, and `bind_slots` refuses any shape without a text frame — a
picture placeholder reports `has_text_frame == False` and is rejected with a teaching error rather
than filled. No Phase 3 success criterion budgets image placement, so none was built. What this
means concretely: an `AssetBlock` reaches the **HTML** surface (as `figure.diagram` + caption — see
"the four block kinds"), and its authored `caption:` can contribute to a text slot; **the image
itself does not reach the deck.** Placing images — the media-part numbering the paragraph above
measures, plus the relative-path resolution the HTML renderer also defers — is a **round-two item**,
carried openly rather than left implicit.

**The slot derivation, and why an empty section still gets a line.** `weeklyspec.weekly_slots(load,
surface)` is the `Surface → NL_` mapping the writer requires (it takes `slots` as a required keyword
precisely because only the composer knows which authored block belongs in which Selection-Pane
name). It always emits **all four** slot keys the template declares, in a fixed order, and for a
section the author left empty the single line on that slide **is that section's own `missing[]`
disclosure** — the string the loader wrote, asserted to be present in `surface.missing` before it is
emitted, so a slide line can never drift into invented prose. Omitting the key was the obvious
alternative and is wrong twice over: `bind_slots` refuses an `NL_`-prefixed shape with no content,
so a weekly with no lowlights would fail to render at all — and rule 4's absence is exactly what the
reviewer's slide should carry.

## Determinism, and the extras it needs

Loads and builds are deterministic (`EPOCH_ZERO` timestamps, file-order iteration): the same file
always produces the byte-identical record. PyYAML lives behind the `[config]` extra
(`pip install '.[config]'`) and python-pptx behind `[pptx]`; the rest of the spine runs without
either. The deck the weekly renders to is **byte-stable** under the recorded decision in
[`.planning/notes/2026-08-29-pptx-determinism-decision.md`](../.planning/notes/2026-08-29-pptx-determinism-decision.md)
— a declared post-save OPC-zip normalization, scoped in writing to a fixed (python-pptx, zlib)
pair, with the part-content digest as the cross-environment assertion. Two renders of one
reviewed record are the same deck.
