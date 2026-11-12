# Lane B spec: operator view v0

**Done tonight:** a static page, rendered by the engine, showing JJ's client list (one
fixture row standing in for Client 1) and, per client, the Library board, the editions list,
and an interactions pane split into received / sent / pending. Typed loader, read-only.
Tests prove: loader reads the fixture without writing, the page shows all three panes and
the FIXTURE label, the committed preview is byte-identical to a fresh render, and the
operator module imports no AI code.

**Exit files:** `src/newsletters/operator.py`, `render_operator_view` in
`src/newsletters/render.py`, `tests/fixtures/operator/fixture-client/client.json`,
`tests/test_operator.py`, preview at `docs/runs/2026-11-07/lanes/B-operator-view/preview/operator.html`,
and the lane docs in this folder.

**Out of scope:** real client data, any write or send action from the view, auth or
hosting, deploy, the Next.js `web/` app, merging to main, the public Library.
