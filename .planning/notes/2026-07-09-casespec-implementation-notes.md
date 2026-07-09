# Implementation notes — Case Spec authoring path (claude/case-spec-authoring)

## Integration path chosen: direct builder (swimlane/compose precedent), NOT capture.build_report

`capture.build_report` was the other candidate, but `capture_session` mints bare-locator,
**un-addressed** traces (no span, no content hash, no offsets). A Case Spec claim carried
that way would pass the faithfulness gate only via the structural un-addressed fallback
(OPTION A(a) in `distill/faithfulness.py`) — the spec for this work package demands claims
"traced to REAL spans of the file text (span-containment faithfulness must pass)", i.e.
the strict branch. So `casespec.py` follows the `swimlane.py → compose.py` precedent
instead: raw file text becomes the `Source.transcript` verbatim, every value is minted via
`Trace.from_source` (the sole pinning constructor), and the Draft `Surface(REPORT)` is
built directly with `created=EPOCH_ZERO` for byte-determinism.

## The one genuinely new mechanism: the block-region fallback

A block scalar's (`|`/`>`) logical value is not a verbatim substring of the raw text —
`swimlane.py` discloses those to `unextracted[]`. That is the right call for config
scalars, but a Case Spec's `reasoning` is usually a block scalar and is the *point* of the
format. The fallback traces such a value to the field's **raw block region** (from after
`key:` through the deeper-indented lines, located by a forward-only line scan) and keeps
the claim **only if** the live `SpanContainmentFaithfulness` gate entails it against that
region (normalization collapses the indentation/newline differences). One definition of
"faithful", reused — never reimplemented. A value neither strategy can pin is routed
verbatim to `missing[]`.

## Other decisions

- `config:` is carried on `CaseSpec.config` (typed, for downstream binding) and never
  walked into claims; `test_config_never_in_claims` polices claim text AND every rendered
  block string.
- `reasoning` lives in BOTH layers: a traced claim in the `Distillation` (truth), and a
  byte-verbatim `QuoteBlock` in the surface (presentation). It is excluded from the
  surface's `ClaimsBlock` so it renders once, in the author's voice slot.
- Strict schema (unknown field / unknown design slot / coerced scalar → teaching
  `ValueError`): this is an authoring format written by hand in PRs, so a typo must fail
  loudly, not silently drop authored content. Absence, by contrast, is honest and goes to
  `missing[]`.
- Not exported from `newsletters/__init__.py` — mirrors `swimlane`/`compose`, keeps the
  diff small.
- PyYAML stays behind `[config]` via `_yaml_loader` (verified: `import newsletters.casespec`
  succeeds with `yaml` import-blocked); import-linter contracts re-run KEPT.
