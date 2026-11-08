# library-fixture

This is a FIXTURE Library for the Lane D connector tests.

The content is invented for testing. It is not Pulse IQ data and it is not client data. Every page carries a `[FIXTURE]` marker in its title. Do not copy any of this text into a real Library.

Contents:

- `ids.json` lists the editions, in the same shape as a real Library's `ids.json`.
- `site/` holds one HTML page per edition, plus `library.html`, a non-edition index page.
- `report-fixture-missing-html` is listed in `ids.json` but has no page on purpose, so the tests can cover a missing file.
