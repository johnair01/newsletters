# 07-02 SUMMARY — stdlib PBIR reader (ADAPT-05, L3)

> NOTE: the executor committed its RED suite (`567cd64`) then the remote container was idle-reclaimed
> before it wrote `_pbir.py` — breaking suite collection. The orchestrator recovered the GREEN
> implementation inline (`323977d`) against the committed contract. Status: COMPLETE (15 tests passed).

## Public API (for 07-03)
```python
from newsletters.adapters._pbir import Detection, extract_report, detect_row_caps

@dataclass
class Detection:  # typed row-cap/aggregation finding (structure only; 07-03 maps to _R_* reasons)
    kind: str          # "topn" | "filter" | "aggregated" | "measure_value" | "directquery" | "rowlimit"
    path: str          # the object path passed in
    params: dict[str, str]

extract_report(obj: dict, object_path: str) -> list[tuple[str, str]]
#   ordered (object_path, verbatim_value) text units: page displayName (path .../Page[<name>]),
#   visual title (.title), text-box runs (.textbox), field refs "Entity.Property" (.field),
#   and filter LITERAL values (.filter — the disclosure caveat: 'Contoso' surfaced as config text).

detect_row_caps(obj: dict, object_path: str) -> list[Detection]
#   topn (filterType==TopN; params operator,itemCount) · filter (restricting; params level,target,literals;
#   unknown filter shapes degrade to generic "filter" — research A1) · aggregated (params ref,fn; Function
#   0==Sum via _AGG_FN) · measure_value (params name) · directquery (obj {"mode":"directQuery"}) ·
#   rowlimit (objects.*.properties.maxRows; params limit). A plain Column projection is NOT a detection.
```
- Pure, deterministic, stdlib-only. Key-lenient (missing keys degrade, never crash/silently miss).
- Reason strings are OWNED BY 07-03 (this module returns structure). Detections force the adapter's
  `Coverage.complete=False` (fail loud); plus a categorical whole-source `_R_NO_DATA_ROWS` (07-03)
  because PBIP text has no data rows.

## Gates (live, recovery)
- `pytest tests/test_pbir_reader.py` → 15 passed. Full suite recovered → 414 passed, 1 xfailed.
  mypy clean (19 files). lint-imports 1 kept/0 broken. Bare import ok. No new dependency.

## For 07-03
Walk the PBIP folder; call `extract_report` per report json + `parse_tmdl` per `.tmdl`; feed all units
to the shared `normalize()`; convert `Detection`s + TMDL `directQuery` signal to `_R_*` `unextracted[]`
entries; add `_R_NO_DATA_ROWS`. Register backend "powerbi"; join parity + determinism matrices.
