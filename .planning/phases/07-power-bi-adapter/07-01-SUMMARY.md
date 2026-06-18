# 07-01 SUMMARY — stdlib TMDL parser (ADAPT-05, L2)

> NOTE: the executor completed the code (RED `e9667bc` + GREEN `27f75aa`) but the remote container was
> idle-reclaimed before it wrote this SUMMARY. Reconstructed by the orchestrator from the live module
> + passing tests (16 passed). Status: COMPLETE.

## Public API (for 07-03)
```python
from newsletters.adapters._tmdl import parse_tmdl
parse_tmdl(text: str) -> tuple[list[tuple[str, str]], list[str]]
#   returns (units, signals)
#   units   = ordered [(object_path_prefix, verbatim_value)] in declaration order
#             e.g. ("Model/Table[Sales]/Measure[Total]", "<DAX text>"), column dataTypes,
#             /// descriptions (one unit per line), table/column/measure/relationship/hierarchy names.
#   signals = non-extractable findings; currently ["directQuery"] when a partition uses DirectQuery mode.
```
- Pure, deterministic, stdlib-only (`re`). **Never evaluates DAX** — a measure's `expression` is
  emitted as verbatim text, never a value (faithful-not-suggestive, the Excel formula-cache crux).
- Grammar: single-tab-indent object headers `type name`, `property: value`, `=`-introduced default
  expressions (single-line / indent-deeper multi-line / ```` ``` ````-fenced), `///` descriptions.

## Gates (live re-run by orchestrator during recovery)
- `pytest tests/test_tmdl_parser.py` → 16 passed. mypy clean. lint-imports 1 kept/0 broken. Stdlib only.

## For 07-03
Feed `units` verbatim to the shared `normalize()` (transcript-prefix pattern); map each `signal`
(`directQuery`) to its `_R_*` `unextracted[]` reason. No new dependency.
