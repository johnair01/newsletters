# The weekly, end to end — the operator's recipe (WKLY-06)

How **you** — not the person who wrote this package — take a real week's material (a template
deck, maybe a workbook export, maybe a mail drop, maybe a folder of photos) and end up with a
reviewed weekly record: an HTML page with an honesty panel, and a `.pptx` deck you could send.

The shape of this document follows the WORK-01 flow in
[`docs/architecture.md`](architecture.md) §8: **numbered steps, each naming the exact command or
function it runs, each stating the trust property that step preserves.** The authoring contract —
the eight keys, the seven loader rules, the four block kinds — is **not** repeated here. It has
one home, [`docs/weekly-spec.md`](weekly-spec.md), and two copies of a schema drift exactly as two
normalizers do.

**Read this before anything else.** Everything below runs **on your machine, read-only**. The
package reads the files you point it at (`Path.read_text` / `Path.read_bytes` and nothing else),
**makes no network call**, and **commits nothing** — the only writes are the files you name with
`--out` and the corpus ledger. Your material stays where it is; nothing is transmitted anywhere.
And nothing here publishes: `Draft › In Review › Published`, with a recorded human reviewer, is
the only way out, and no command in this document can take that step.

---

## 1. What you need

| Input | Required? | What it is |
|---|---|---|
| A **template deck** | yes, for the deck | A `.pptx` *you* designed, whose Selection-Pane shape names start with `NL_` |
| A **Weekly Spec** | yes | One YAML file — your week, in your words ([`docs/weekly-spec.md`](weekly-spec.md)) |
| A **lane config** | yes, for the KPI strip | The module config whose values the weekly binds |
| A **workbook export** | optional | Your BI view exported to `.xlsx` |
| An **`.eml` drop** | optional | Saved mail that evidences a recognition |
| A **photo folder** | optional | Images you want placed, each with its provenance |

All of it is **local, read-only input**. The package never writes to the material you point it at,
never opens a socket, and never adds any of it to git. What you commit is your decision, made in a
pull request, like every other change to the record.

## 2. Install

```
pip install '.[config,pptx]'
```

Add `[excel]` only if you are bringing a workbook:

```
pip install '.[config,excel,pptx]'
```

Then check the install answered:

```
newsletters version
```

**Trust property: the bare install is AI-free, and none of these extras changes that.** `config`
is PyYAML, `pptx` is python-pptx, `excel` is openpyxl — three non-AI, MIT, pure-input libraries,
each lazy-imported inside the one module that needs it. Every AI dependency lives behind a
separate `[ai]` extra that nothing in this recipe touches, and a CI job (`bare-install`) fails if
an AI import ever becomes reachable from the core.

## 3. Prepare the template

The writer **fills your existing slides**. It never adds a slide, never invents a layout, never
moves a box. You lay the deck out; the package puts the record's words in the boxes you named.

1. Open your deck, open the **Selection Pane**, and rename every shape you want filled so its name
   **starts with `NL_`** (for example `NL_HIGHLIGHTS`, `NL_LOWLIGHTS`, `NL_TEAM`, `NL_ASSETS`).
2. Anything *not* named `NL_…` is left exactly as you drew it — your footer, your logo, your
   page furniture.
3. Both directions fail loud, naming the offender: an `NL_` shape the record has no content for
   **refuses to render**, and a slot the record wants that your deck does not declare **refuses to
   render**. A silently half-filled deck is a deck somebody sends.

Two costs, learned by measurement, that will bite you if nobody says them out loud:

- **Set `word_wrap=True` and `auto_size=NONE` on your text boxes.** PowerPoint's default autofit
  is computed by PowerPoint, not by the file, so a long line **overflows the slide silently** —
  the file is valid, the text is there, and it runs off the edge when somebody opens it. (P-07.)
- **Slots are looked up on your DOCUMENT slides only.** Placeholders that live on a *layout* or on
  the *master* are not walked. Put the `NL_` shape on the slide itself. (IN-07.)

**Trust property: the deck is yours; the record only supplies words.** And it supplies only words
the record can stand behind — the writer has no image-placement path at all this milestone, so the
deck is text-only by construction, not by omission.

## 4. Author the Weekly Spec

The full contract is [`docs/weekly-spec.md`](weekly-spec.md) — read it there, once. The eight
top-level keys, by name only: `week`, `module`, `highlights`, `lowlights`, `recognitions`, `team`,
`assets`, `config`.

The two rules an operator most needs before writing the first one:

- **Rule 4 — every absence is disclosed, never fabricated.** A field you leave blank is listed in
  the record's `missing[]` and shown to your reviewer, including *"no lowlights were authored"* —
  precisely the absence a weekly is tempted to hide. Nothing is filled in on your behalf, and the
  composer never summarises, reorders or merges the lines you wrote.
- **Rule 7 — a path that escapes the project root RAISES.** It is a refusal, not an absence: it
  never lands in `missing[]`. `missing[]` is for content that is genuinely absent, never for a
  request the loader will not serve. If the two were collapsed, a path traversal could be
  "disclosed" and look honest.

Your byline lives in `config: author:` — or pass `--author "Your Name"`. If you give neither, the
build **refuses** with an error naming both. A name on a record is a claim about who stands behind
it, so it is the one thing this system will not default.

## 5. Point the read-only adapters at your data

**Mail (`.eml`).** Drop saved messages into the corpus's `inbox/` and give a recognition a
`source:` naming the message's repo-relative path. `EmailAdapter().parse(raw, path)` (stdlib
`email` only — **no extra, no network**) turns those bytes into a content-addressed `Source`, so a
recognition's credit is evidenced rather than asserted. A `source:` that resolves to nothing is
disclosed by name; the recognition is still carried, because dropping it would erase credit.

**Numbers (workbook).** Export the BI view to `.xlsx` and read it with the adapter this repo
**already** has — `newsletters.adapters.resolve("excel")` (ADAPT-03). Every cell becomes a claim
pinned to its own address in *your* export, and the weekly's KPI strip derives its ↑/↓ from two
independently traced endpoint cells, never from a number somebody typed.

State plainly, because the gap matters when you plan your week:

- **There is no CSV reader.** The live adapter is `.xlsx`-only; a CSV path would be exactly the new
  adapter WKLY-04 forbids.
- **There is no Power BI value reader.** Nothing connects to a BI tool. You export; the package
  reads the export. (Reading the tool directly is ADAPT-05, deferred and written down.)
- **There is no `--workbook` flag yet.** The shipped `newsletters weekly` command binds values from
  the lane config it is given with `--lanes`. Carrying an export's claims into a weekly is a
  Python-API seam today (`resolve("excel")` → `SectionBinding` → `build_weekly_report(...,
  bindings=[...])`), proved end to end in `tests/test_weekly_values.py`. Said out loud rather than
  implied by a flag that does not exist.

**Photos.** Each image is an `assets:` record carrying **folder + date + event** — the provenance
minimum — and a `link:` is **required** when a screenshot stands in for values (`stands_in_for:
values`). Provenance is checked *before* the file is read, so an under-documented image is never
placed and needs no file on disk at all; the reviewer is told which field was missing.

**Trust property, again, because this is the step that touches your real material: read-only, no
network, nothing committed.** The loader hashes an image's bytes and never opens it as an image —
no imaging library is reachable from this code path.

## 6. Compose and render

Four commands. They are run verbatim against the committed sample corpus every time this phase is
verified, and a test parses every one of them against the live CLI — so a renamed flag turns the
suite red instead of rotting this page.

See the options the shipped command actually exposes:

```
newsletters weekly --help
```

Render the weekly record to HTML (swap `--out` for a directory of yours):

```
newsletters build --corpus weekly --out build/weekly-preview
```

Render the deck. Swap the four input paths for yours; **`--out` is yours** and is never derived
from the record's content:

```
newsletters weekly --spec content/weekly/weekly-2374-w41.yml \
                   --lanes content/module/module-a.yml \
                   --template content/weekly/template.pptx \
                   --author "Tora Ziyal" \
                   --out content/weekly/deck/weekly-2374-w41.pptx
```

It writes two files: the deck, and a `.digest` sidecar beside it. The sidecar is the deck's
`part_digest` — a sorted, length-prefixed hash of each part inside the `.pptx` — so you can check
later that the deck you are about to send is the deck that was rendered, **on a bare install with
no optional extra**. Render the same record twice and both decks carry the same digest.

Run the merge-block gate, and assemble the site if you publish one:

```
newsletters check --corpus weekly
```

```
newsletters assemble --out dist/site
```

`newsletters build --corpus weekly` renders **the corpus at `content/weekly/`** — it discovers the
single `*.yml` there rather than taking a `--spec`. To render your own week to HTML, put your spec
in that corpus directory (or copy the corpus and point the builder at your copy). The deck command
is the one that takes explicit paths. That asymmetry is the shipped surface today, stated rather
than papered over.

## 7. Review

1. **Open the HTML** (`library.html`, then the record's page).
2. **Read the honesty panel.** This is the part worth reading: what the record does *not* know.
   Every absent field, every recognition without a source, every image whose provenance was
   incomplete is named there, in the loader's own words.
3. **Check the deck.** Every slide carries the **DRAFT** watermark, and the file's core properties
   say `contentStatus = draft`. If it is not approved, it looks unapproved wherever it lands.
4. **Then a human decides.** `Draft › In Review › Published`, with a recorded reviewer, is the only
   way out of Draft. **No command in this document publishes anything**, and nothing in the weekly
   code path can call `publish()` — that is asserted by a test that reads the source, not promised
   in prose.

One honest note about the gate command: `newsletters check --corpus weekly` is **Draft-vacuous by
design**. `review_blockers` exempts every surface that is not Published, because publication *is*
the trust boundary — so a Draft weekly exits 0 no matter what it contains. The exit code proves the
wiring; **the honesty panel is what an operator reads.** The gate's teeth are for the day somebody
publishes: it has been proven to fire on a planted published blocker
(`tests/test_weeklysite.py::test_check_weekly_blocks_on_planted_blocker`).

## 8. What the sample looks like

`content/weekly/` is the worked example, committed and rendered, and you can read every part of it:
the spec (`weekly-2374-w41.yml`), the mail drop (`inbox/`), the image (`assets/`), the template
copy, the corpus's own append-only ledger (`ids.json`), the rendered page (`site/`) and the deck
(`deck/`).

It plants **three absences on purpose**, because a sample that hides what it does not know teaches
the wrong lesson to whoever copies it:

1. a lane that **declares no KPIs** — so the strip is omitted and the omission is disclosed;
2. a recognition with **no `source:`** — credit is still given, the missing evidence is named;
3. an asset missing its **`folder:`** — provenance is checked before the file is read, so the image
   is never placed.

Each appears in the record's `missing[]` **and** in the rendered honesty panel; a test locates them
by the composer's own format strings, so no disclosure sentence is typed twice.

**The deck is a corpus artifact, not a download.** It lives at `content/weekly/deck/`, which is
*outside* `content/weekly/site/`, and `publish.assemble_site` copies `content/*/site` only — so no
deck can reach the published tree. That is a structural property of the layout, not a discipline
somebody has to remember. Linking a deck from a published page would be a deliberate, reviewed
change (one task, recorded, not built).
