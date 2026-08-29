# Phase 1 — VERIFICATION (2026-07-03)

**Verdict: PASSED 5/5** — gates re-run independently in the working tree (not trusted from
any executor's report).

| # | Success criterion (ROADMAP) | Evidence |
|---|---|---|
| 1 | `records` param renders strip from existing tokens; omitted/empty → no markup (SC1 as amended, 01-CONTEXT d5) | `test_records_strip_empty_renders_nothing` green; `.nl-records` CSS uses only existing custom properties (`--text-dim`/`--text`/`--line`/`--signal`, DM Mono sizes); no new color/radius |
| 2 | Strip on chrome pages ONLY | `test_records_strip_on_chrome_pages_only` green (rev1 index+library carry it with both neighbor hrefs; every per-surface page asserted free of it); work/module library strips verified in regenerated committed HTML |
| 3 | `render_404` base-path-absolute + marker | `test_render_404_is_base_path_absolute_and_marked` green (every href absolute-or-external, `url('/newsletters/fonts/`, marker present, no-trailing-slash normalization) |
| 4 | Corpora regenerated same-commit; byte gates green; ledgers unchanged | commit `1102ba1`: only `content/*/site/*.html` changed; `git diff content/*/ids.json` empty; `test_committed_equals_fresh_build` + double-render green post-regen |
| 5 | Cross-corpus hrefs explicitly pinned, not skipped | `test_no_dead_link_every_internal_href_resolves` now asserts path-hrefs match `work/|module/|../` shapes with the resolver-of-record note in-code |

## Gate set (re-run 2026-07-03, this tree)

```
python -m pytest -q                      629 passed
lint-imports                             Contracts: 2 kept, 0 broken.
newsletters check --corpus rev1          All published surfaces clean — no blockers.
newsletters check --corpus work          All published surfaces clean — no blockers.
newsletters check --corpus module        All published surfaces clean — no blockers.
git diff content/*/ids.json              (empty — append-only held)
```

## Notes

- 626 → **629** tests (3 new guards). No existing test weakened; the dead-link test got
  *stricter* (path-hrefs must match known shapes rather than being unreachable).
- The strip's links are provably resolvable only in the assembled tree — deliberately deferred
  to Phase 2's `tests/test_publish.py` (recorded in-code and in `docs/surfaces.md`).
