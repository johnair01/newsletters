# Lane B decisions (all candidate until JJ checks them)

## D1. What a tester sees stays identical to what ships

- **Decision:** Confirm the working answer, with one addition. One engine function
  (`newsletters.render.render_operator_view`) renders the view; there is no separate
  mock-up. The thing a tester opens is that function's output for a given client
  directory, written to a file on the branch. It goes to main as is. The addition: a test
  regenerates the committed preview and fails if a single byte differs, so "identical" is
  checked by CI, not promised. The only thing allowed to differ between test and ship is
  the input data (fixture today, the real client directory later), never the renderer.
- **Options considered:** (a) a hand-built HTML or design-reference mock-up, then rebuild
  in the engine; (b) one renderer, preview is its output (chosen); (c) a live server that
  renders on request, so there is no committed file at all.
- **Why:** (a) is exactly the drift we have hit before (DEF-13: placeholder data wearing
  the product's URL; design-reference is a contract, not shipped code). (b) reuses the
  existing byte-stable regen pattern the Library already uses (SITE-06 generated marker).
  (c) adds infra we do not need for a private, single-operator view.
- **What would change it:** the view needing live state (actions like "approve" or
  "send" from the page, or data that changes faster than a commit). Then the preview
  becomes a snapshot of a running app, and "identical" has to be checked by rendering the
  same data through the same app, not by comparing committed bytes.
- **Status:** candidate.

## D2. No real client instance in this repo, so v0 uses fixture data

- **Decision:** a search of the repo for the client's name finds nothing, and there is no client
  concept in the engine yet. v0 uses one fixture client, id `fixture-client`, named
  "Client 1 (fixture)", with invented, obviously-fake content.
  Every rendered page carries a visible FIXTURE banner. No client data was copied from
  anywhere.
- **Options considered:** fixture (chosen); pull the real client config from the Pulse IQ repo (not
  allowed: "do not copy client data from anywhere", and that repo is out of this lane's
  scope); ask JJ (JJ is busy, and the kickoff already answers it).
- **Why:** the kickoff says so, and it keeps real client data out of a public MIT repo.
- **What would change it:** JJ pointing at where the real client instance lives. Then the view
  reads that directory read-only through the same loader; no renderer change.
- **Status:** candidate.

## D3. A client is a directory with a `client.json`, read-only, stdlib + Pydantic only

- **Decision:** New core module `newsletters.operator` defines `Client`, `Edition`,
  `Interaction` and `OperatorView`, and `load_client(dir)` reads `<dir>/client.json`. It
  never writes. JSON, not YAML, so the loader stays stdlib + Pydantic (the AI-optional,
  dependency-light core rule; PyYAML is behind the `[config]` extra).
- **Options considered:** YAML (nicer to hand-edit, but needs the extra); reuse the
  Case Spec format (wrong shape: one case, not a client relationship); a database (no).
- **Why:** smallest typed format the core can read with no new dependency. The Library
  part reuses `Site.from_surfaces` with an in-memory ledger, so no new identity scheme.
- **What would change it:** the real client instance already having a format. Then the
  loader adapts to it, and `client.json` becomes the fixture's shape only.
- **Status:** candidate.

## D4. Library, editions and interactions: what each one means in v0

- **Decision:** *Library* = the client's surfaces on the existing Draft / In Review /
  Published board (same `_board` the public Library uses). *Editions* = the dated issues
  delivered to that client, newest first, each pointing at a Library surface by id.
  *Interactions* = a typed log with direction `received`, `sent` or `pending`, shown as
  three columns. Pending is derived only from the log, never inferred.
- **Options considered:** editions as just the newsletter-kind surfaces (loses date and
  issue number, which the ledger does not carry for cadenced surfaces); interactions
  inferred from surface gate state (would invent facts the record does not hold).
- **Why:** faithful, not suggestive: the view shows what the record says and nothing it
  has to guess.
- **What would change it:** JJ saying an edition is something else (for example a bundle
  of several surfaces), or wanting pending items computed from gate state.
- **Status:** candidate.

## D5. The operator view is private and not part of the published site

- **Decision:** It is not added to `publish._CORPUS_LAYOUT`, not deployed, and its
  preview lives under this lane folder. The page carries a "private operator view, not
  published" line.
- **Why:** kickoff says do not deploy; the client list is not something the public site
  should show.
- **What would change it:** a hosting decision for private views (auth), which is a
  maintainer call.
- **Status:** candidate.

## D6. No client or person names on this branch (public repo)

- **Decision:** After an Orchestrator message (7:06 PM PT), the client's real name was
  replaced with "Client 1" in every current file on this branch, and the fixture is named
  "Client 1 (fixture)". This was done with a new commit; history was NOT rewritten, so the
  name still exists in the file contents of earlier commits on `operator-view-v0` (no
  commit message holds it). "JJ" is kept: it is the maintainer's handle and already
  appears throughout `CLAUDE.md` on main.
- **Options considered:** new commit (chosen, as instructed); rewrite history to purge
  the name (would remove it fully but breaks the no-rewrite rule); delete and recreate
  the branch (same effect as a rewrite).
- **Why:** the Orchestrator asked for a forward fix; JJ decides the real labelling.
- **What would change it:** JJ deciding the name must be purged from history too. Then
  the branch needs a rewrite or deletion, which is JJ's call as maintainer.
- **Status:** candidate.

## D7. The interactions pane never renders an email address

- **Decision:** Every interaction string (channel and summary) passes through a broad
  email filter before rendering and shows "[email hidden]". Test:
  `test_no_email_address_renders_in_interactions`. Built tonight, because real render
  logs carry client addresses and the filter is cheap to have in place before real data.
- **Options considered:** filter at render (chosen); filter at load (would hide the
  address from code that may legitimately need it later, such as a send action); reject
  logs that contain addresses (too strict for real logs).
- **Why:** the page is where exposure happens, so the guard sits at the page.
- **What would change it:** a need to show who sent something. Then show a name or a
  role label from config, never the raw address.
- **Status:** candidate.

## D8. Any real Library export needs a client-name filter (not built tonight)

- **Decision:** Recorded only. Real issues name the client throughout, so before any real
  Library is rendered on this public branch, a client-name filter (names from config,
  replaced by the client's label) and a test that no configured name renders must exist.
  No real data is imported tonight, so nothing would exercise it yet.
- **Options considered:** build now against fake names (possible, but it would be tested
  only on invented input); defer until the real loader exists (chosen).
- **Why:** a filter is only as good as the real names it is tested against, and those
  cannot live in this repo.
- **What would change it:** the decision to render real client data from a public repo at
  all. Keeping real client directories outside this repo may make the filter a second
  line of defence rather than the first.
- **Status:** candidate.
