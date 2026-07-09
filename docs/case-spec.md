# Case Spec — hand-authored YAML into the reviewed record

How an engineer puts a **case** — a work-content burden and the design that answers it —
into the record by hand, in a PR, with zero AI. The spec file is the source; the package
lifts it through the existing spine (`Source → Claim(+Trace) → Distillation → Surface`)
into a **Draft Report** that moves through the same review gate as everything else.

This schema is revived deliberately from the design-era Operating Agreement: the point is
the *pattern* (inputs → reasoning → outputs → reusable record) and the *author's own
voice*, kept portable across orgs by pushing every org specific into `config`.

---

## Writing one

Author a YAML file (data, not code — parsed with `safe_load` only) and open a PR:

```yaml
case: <name/title of the case>
problem: <the work-content burden, stated as a human problem>
current_state: <how it is done today>
imagined_state: <what better looks like>
design:                # the pattern — four slots, all optional, nothing else
  inputs: <what goes in>
  reasoning: <why the design is shaped this way>
  outputs: <what comes out>
  reusable_record: <what record the work leaves behind>
reasoning: |
  Your intent and thinking, in your own voice. This is first-class content:
  it survives VERBATIM into the rendered surface — never summarized, never
  dropped. Write it like you would explain it to a colleague.
portable:              # what travels to another org: method, schema, reasoning
  - <thing that travels>
config:                # org-specific slots: system names, metrics, registries.
  some_system: <name>  # NEVER rendered into claims — specifics stay config.
```

Rules the loader enforces (teaching errors, never silent drops):

- The document must be a mapping of exactly these eight fields; an unknown field (a typo)
  fails loudly rather than dropping what you wrote.
- Narrative fields are strings — quote values YAML would type-coerce (`42`, `yes`).
- `design` accepts only the four canonical slots; `portable` is a string or list of strings.
- Every field is optional. An absent or empty field is **disclosed** in
  `Distillation.missing[]` (and the surface's honesty panel) — never fabricated.

## What happens to it

`newsletters.casespec.load_case_spec(path)` reads the file **verbatim** into a
content-addressed `Source` (the transcript IS your file text) and mints one traced `Claim`
per authored value via `Trace.from_source` — real character spans of your file, so the
span-containment faithfulness gate passes strictly, not by fallback. A multi-line
`reasoning` block is traced to its raw block region in the file. `config:` values are
carried on `CaseSpec.config` for downstream binding but are **never** minted into a claim
or rendered into a block — a test (`tests/test_casespec.py::test_config_never_in_claims`)
polices this.

`newsletters.casespec.build_case_report(load, author=...)` produces the surface:

- a `Surface(REPORT)` in **Draft** — no auto-publish; the `Draft › In Review › Published`
  gate with a recorded approval is the only path out,
- a `ClaimsBlock` of your traced claims (problem, states, design slots, portable items),
- your `reasoning` as a `QuoteBlock`, byte-verbatim, attributed to you,
- everything you left blank listed in `Surface.missing[]`, shown to the reviewer.

Loads and builds are deterministic (`EPOCH_ZERO` timestamps, file-order iteration): the
same file always produces the byte-identical record. PyYAML lives behind the `[config]`
extra (`pip install '.[config]'`); the rest of the spine runs without it.
