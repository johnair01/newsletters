# Phase 4: Shared Adapter Normalizer & Email Adapter - Research

**Researched:** 2026-06-17
**Domain:** Deterministic, AI-free MIME/.eml extraction (Python stdlib `email` + `html.parser`), feeding a shared faithful `normalize()` that mints content-addressed `Claim(+Trace)`.
**Confidence:** HIGH (all core API behaviors verified empirically against a live CPython interpreter; cited against docs.python.org 3.12)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
1. **Architecture — shared normalize() at the socket (ADAPT-01).** New `src/newsletters/adapters/`
   package. Each adapter is a registered `DistillPort` backend that (a) does format-specific raw
   extraction into intermediate "raw units," then (b) calls ONE shared `normalize()` that mints typed
   `Claim(+Trace)`. **The faithful-extraction rule lives only in `normalize()`:** every Claim's text
   must be a verbatim, content-addressed span of its Source (via `Trace.from_source`); anything not
   verbatim-locatable is routed to `unextracted[]`, never fabricated. Adapters never hand-mint hashes.

2. **Email → Source model (decoded-text transcript).** One `.eml` → one `Source`. `Source.transcript`
   is a **canonical DECODED text** rendering (a headers block + the decoded body) so spans are verbatim
   and content-addressable; Trace offsets index into that transcript. The raw file path/identifier
   lives in `Source.context`. (Not the raw RFC822 bytes — that leaks encodings and yields ugly offsets.)

3. **Granularity — headers + paragraphs.** Key headers (From / To / Subject / Date) each become a
   Claim with a Trace into the transcript's header block; the decoded body is segmented into paragraphs,
   each its own Claim(+Trace). Auditable atoms, real per-claim provenance.

4. **`unextracted[]` — broad, no silent drops (success criterion).** Route to `unextracted[]`:
   forwarded/nested `message/rfc822`, non-text attachments, charset/decoding fallbacks, HTML-only
   bodies where deterministic tag-stripping is lossy, and anything `normalize()` cannot verbatim-locate.
   The golden-file test asserts **zero silent drops** (every input part is either a Claim or an
   `unextracted[]` entry).

5. **Scope / stdlib.** Python stdlib only — `email` (RFC822/MIME parsing), `email.policy.default`,
   `html.parser` for deterministic HTML→text. **No new dependency**, no Package-Legitimacy gate. Keep
   the AI-optional contract (`lint-imports`) and bare-install gate green. `.msg` (GPL `extract-msg`) is
   explicitly OUT (REQUIREMENTS Out-of-Scope).

### Claude's Discretion
- The exact intermediate "raw unit" dataclass shape (it is internal to the adapter and never serialized
  out — only `Claim(+Trace)` and `Coverage` cross the socket).
- The precise transcript layout (this research RECOMMENDS one; see Q5).
- The HTMLParser tag-stripping rule set (this research RECOMMENDS a minimal block-aware stripper; see Q4).
- The fixed charset-fallback ladder (this research RECOMMENDS `declared → utf-8 → latin-1`; see Q2).

### Deferred Ideas (OUT OF SCOPE)
- `.msg` (Outlook) ingestion — GPL `extract-msg`, explicitly out (REQUIREMENTS Out-of-Scope).
- Any third-party charset detection (`chardet`/`charset-normalizer`) — a dependency AND non-deterministic.
- Any third-party HTML→text (`html2text`, `BeautifulSoup`/`lxml`) — dependency and/or non-deterministic output.
- Rich HTML structure preservation (tables, links-with-hrefs) — out; HTML-only bodies route to unextracted[] when stripping is lossy.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ADAPT-01 | Shared `normalize()` — the faithful-extraction rule in exactly one place | Q5 (transcript + offset-location algorithm), Q1 (what feeds normalize), the `Trace.from_source` contract (verified: `semantic.py:109-153`); span-containment gate (`faithfulness.py:62-74`) is what normalize's output must survive |
| ADAPT-02 | Email `.eml` adapter, stdlib-only, registered `DistillPort` backend | Q1 (modern `email` parse), Q2 (charset fallback), Q3 (multipart), Q4 (HTML→text), Q7 (paragraph segmentation), the "no new dependency" confirmation |
| ADAPT-06 | Golden-file tests | Q6 (fixture set + zero-silent-drops assertion + JSON round-trip via `assert_conforms`) |
</phase_requirements>

## Summary

The Python stdlib already contains everything this phase needs; **no new dependency is warranted or
permitted**. Parse each `.eml` with `email.message_from_bytes(raw, policy=email.policy.default)`, which
returns a modern `EmailMessage` whose accessors (`str(msg['Subject'])`, `get_body(...)`,
`iter_attachments()`, `get_content()`) decode RFC2047 header words, Content-Transfer-Encoding, and
charset for you. The adapter's job is to (a) extract decoded raw units, (b) build a canonical **decoded
text transcript** (headers block + decoded body), (c) hand verbatim spans to the shared `normalize()`,
which mints `Claim(+Trace)` via `Trace.from_source`, and (d) honestly account for everything it could
*not* faithfully extract in `Coverage.unextracted[]`.

The single most important correctness insight, verified empirically: **`get_content()` does NOT raise on
a mislabeled charset** — it silently substitutes U+FFFD (`�`) replacement characters (`errors='replace'`
is the default for text parts). That is a faithfulness violation hiding in plain sight. The adapter must
therefore decode the body itself with a fixed, deterministic ladder (`declared → utf-8 → latin-1`, all
`errors='strict'`) and route any part that required a non-declared fallback — or that still contains
U+FFFD — to `unextracted[]`. An **unknown/unregistered charset raises `LookupError`** (not
`UnicodeDecodeError`); both must be caught. `latin-1` strict is a *total* function over bytes (it maps
all 256 values and never raises), which makes the fallback ladder deterministic and guaranteed to
terminate — but reaching it is itself the signal to record an `unextracted[]` entry.

**Primary recommendation:** Parse with `policy=email.policy.default`; build a decoded-text transcript;
locate every claim span by `str.find(unit, cursor)` advancing a running cursor (this disambiguates
duplicate paragraphs); mint traces only via `Trace.from_source`; and treat the `Coverage` honesty
validator + the Phase-3 `SpanContainmentFaithfulness` gate as the two automatic invariants the adapter
must satisfy rather than reimplement.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `.eml` byte parsing / MIME walk | Adapter (`adapters/email_adapter.py`) | — | Format-specific; the only place that touches `email` |
| Charset decode + fallback ladder | Adapter | — | Format-specific; decisions about declared charset live with the parser |
| Deterministic HTML→text | Adapter (helper) | — | Only invoked for HTML-only bodies; lossy → reported, not the body of record |
| Canonical transcript assembly | Adapter | — | The transcript IS `Source.transcript`; built before normalize runs |
| Verbatim span → `Claim(+Trace)` minting | **Shared `normalize()`** (`adapters/normalize.py`) | — | The faithful-extraction rule lives in ONE place (D-1, CONTEXT decision 1) |
| Content-address hashing | `Trace.from_source` (core `semantic.py`) | — | Adapters NEVER hand-mint hashes (CONTEXT decision 1) |
| Faithfulness enforcement (span-containment) | Phase-3 gate (`distill/faithfulness.py`) | conformance suite | Already built; normalize's output must survive it — do not reimplement |
| Coverage honesty ("no complete-with-drops") | `Coverage` validator (`distill/coverage.py`) | — | Already enforced in code; adapter only populates it correctly |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `email` (stdlib) | Python 3.12 stdlib | RFC 5322 / MIME parse via `message_from_bytes` + `EmailMessage` | The canonical, dependency-free MIME parser; the modern (`policy.default`) API decodes headers/CTE/charset for you |
| `email.policy` (stdlib) | Python 3.12 stdlib | `policy.default` → returns `EmailMessage` with modern accessors | Without it you get the legacy `Message` (no `get_body`/`iter_attachments`/`get_content`) |
| `html.parser` (stdlib) | Python 3.12 stdlib | Deterministic HTML→text tag-stripping (HTML-only bodies) | Event-driven, no dependency, fully deterministic output |
| `hashlib` (stdlib, indirect) | Python 3.12 stdlib | SHA-256 content-address — **used only by `Source.content_hash()` / `Trace.from_source`** | Adapter does NOT call it directly (CONTEXT decision 1) |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `email.headerregistry` (stdlib) | 3.12 | Structured header objects (`Date` → `.datetime`, address headers → `.addresses`) | Optional convenience; the transcript uses the decoded *string* form `str(msg[h])` for verbatim spans |
| `email.errors` (stdlib) | 3.12 | `msg.defects` / `part.defects` enumerate malformed-MIME defects | Detect structural corruption to record as an `unextracted[]` reason |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib charset ladder | `chardet` / `charset-normalizer` | **REJECTED** — adds a dependency AND is statistical/non-deterministic (CONTEXT decision 5; violates "faithful, not suggestive" — guessing). |
| `html.parser` stripper | `html2text` / `BeautifulSoup` + `lxml` | **REJECTED** — dependency, `lxml` is a C extension (breaks bare-install), `html2text` output is opinionated/non-deterministic. |
| stdlib `email` | `mailparser`, `flanker` | **REJECTED** — wrap the same stdlib but add deps; no benefit for this scope. |

**Installation:**
```bash
# NONE. Python stdlib only. No `pip install`, no new entry in pyproject [ai] or base deps.
```

**Version verification:** N/A — no external packages. All modules (`email`, `email.policy`,
`email.headerregistry`, `email.errors`, `html.parser`, `hashlib`) ship with CPython. The modern
`EmailMessage` API (`policy.default`, `get_body`, `iter_attachments`, `get_content`) has been stable
since Python 3.6 and is current in 3.12. [VERIFIED: live interpreter, behaviors reproduced on CPython 3.11.15; API identical in 3.12 per docs] [CITED: docs.python.org/3.12/library/email.message.html]

## Package Legitimacy Audit

**N/A — this phase installs no external packages** (CONTEXT decision 5: "Python stdlib only … No new
dependency, no Package-Legitimacy gate"). All imports resolve to the CPython standard library. There is
no registry lookup to perform, no slopsquatting surface, and no `postinstall` script risk.

**Packages removed due to [SLOP] verdict:** none (none proposed).
**Packages flagged as suspicious [SUS]:** none.

> Planner note: any plan task that proposes adding a dependency here CONTRADICTS a locked decision and
> must be rejected — escalate to the reviewer rather than installing.

## Architecture Patterns

### System Architecture Diagram

```
  .eml bytes (read from path; path -> Source.context)
        │
        ▼
  email.message_from_bytes(raw, policy=email.policy.default)  ──► EmailMessage (msg)
        │
        ├─► HEADER EXTRACTION ──────────────────────────────────────────────┐
        │     str(msg['From'/'To'/'Subject'/'Date'])  (RFC2047 auto-decoded) │
        │                                                                    │
        ├─► BODY SELECTION                                                    │
        │     body = msg.get_body(preferencelist=('plain','html'))           │
        │       ├─ body is text/plain ──► get_content() (decode CTE+charset)  │
        │       │                          + adapter charset re-check ────────┤
        │       ├─ body is text/html  ──► html.parser strip ──► LOSSY ────────┼──► unextracted[]
        │       └─ body is None        ──► no readable body ─────────────────►┼──► unextracted[]
        │                                                                    │
        ├─► NON-BODY PARTS  (msg.iter_attachments())                          │
        │     ├─ non-text attachment (application/*, image/*) ───────────────┼──► unextracted[]
        │     └─ message/rfc822 (forwarded; maintype=='message') ────────────┼──► unextracted[]
        │                                                                    │
        ├─► msg.defects / part.defects (malformed MIME) ─────────────────────┼──► unextracted[]
        │                                                                    │
        ▼                                                                    ▼
  BUILD CANONICAL TRANSCRIPT  (headers block + "\n\n" + decoded body)   Coverage.unextracted[]
        │                                                              (complete=False if non-empty)
        ▼
  shared normalize(transcript, raw_units, source) ───► for each unit:
        cursor-advancing str.find ─► (start,end) ─► Trace.from_source(source,start,end)
        │                                            │
        │                                            ├─ locatable  ──► Claim(text=span, evidence=[Trace])
        │                                            └─ not locatable ──► unextracted[]  (never fabricate)
        ▼
  Distillation(claims=[...], missing=[...])  +  Coverage(complete=?, unextracted=[...])
        │
        ▼
  DistillationResult(distillation=, coverage=, backend="email")
        │
        ▼
  [Phase-3] SpanContainmentFaithfulness.entails(claim)  +  Coverage honesty validator
        (both automatic — assert_conforms drives them in the golden test)
```

### Recommended Project Structure
```
src/newsletters/adapters/
├── __init__.py          # exports normalize, EmailAdapter; registers EmailAdapter in the distill registry
├── normalize.py         # the SHARED faithful normalize() — minting Claim(+Trace); the ONE rule site
├── email_adapter.py     # the .eml DistillPort backend: parse -> raw units + transcript -> normalize()
└── _html_text.py        # deterministic html.parser tag-stripper helper (lossy; reports lossiness)
```

### Component Responsibilities
| File | Owns | Must NOT do |
|------|------|-------------|
| `normalize.py` | Cursor-advancing offset location; `Trace.from_source` minting; routing non-locatable units to a returned `unextracted[]` list | Touch the `email` module; fabricate text; hand-mint hashes |
| `email_adapter.py` | `email` parse, MIME walk, charset ladder, transcript assembly, building raw units + a partial `unextracted[]` (attachments/rfc822/defects); calling `normalize()`; assembling `DistillationResult` | Reimplement faithfulness/coverage validators; call `Surface.publish` or construct a published `Review` (HARD RULE — `manual.py:13-17`) |
| `_html_text.py` | Deterministic block-aware tag-stripping; returning `(text, lossy: bool)` | Use any third-party parser; emit non-deterministic output |

### Pattern 1: Modern parse — always pass `policy.default`
**What:** The single line that unlocks the entire modern API.
**When to use:** Every parse. The default (no policy) returns a legacy `Message` that LACKS `get_body`, `iter_attachments`, and `get_content`.
**Example:**
```python
# Source: https://docs.python.org/3.12/library/email.parser.html (BytesParser / message_from_bytes)
#         https://docs.python.org/3.12/library/email.policy.html (policy.default => EmailMessage)
import email
import email.policy

with open(path, "rb") as fh:           # ALWAYS bytes (message_from_bytes), never text
    raw = fh.read()
msg = email.message_from_bytes(raw, policy=email.policy.default)
# msg is an email.message.EmailMessage  [VERIFIED: live interpreter]
```
**Note:** read `rb` and use `message_from_bytes` (not `message_from_string`) — the file is bytes with
its own internal charsets; decoding to text first would corrupt non-ASCII before parsing.

### Pattern 2: Header extraction — `str(msg[h])` decodes RFC2047 words
**What:** `str()` on a header value renders the *decoded* unicode (encoded-words like
`=?utf-8?q?Jos=C3=A9?=` become `José`).
**Example:**
```python
# Source: https://docs.python.org/3.12/library/email.headerregistry.html
subject = str(msg["Subject"])   # 'Quarterly — results'  (RFC2047 auto-decoded)  [VERIFIED]
from_   = str(msg["From"])      # 'José García <jose@example.com>'                [VERIFIED]
date    = str(msg["Date"])      # 'Wed, 17 Jun 2026 09:00:00 +0000' (verbatim string form)
# A missing header -> msg[h] is None; guard before str().
```
**Faithfulness note:** use the **decoded string form** (`str(msg[h])`) in the transcript so the span is
human-readable verbatim text. `msg['Date'].datetime` gives a parsed `datetime` for `Source.timestamp`,
but the transcript span should be the *string* the header rendered to.

### Pattern 3: Body selection — `get_body(preferencelist=('plain','html'))`
**What:** Picks the best body part by preference; returns `None` if none match.
**Example:**
```python
# Source: https://docs.python.org/3.12/library/email.message.html#email.message.EmailMessage.get_body
body = msg.get_body(preferencelist=("plain", "html"))
if body is None:
    ...  # no readable body -> unextracted[]  [VERIFIED: returns None]
elif body.get_content_type() == "text/plain":
    text = body.get_content()           # decodes CTE + charset
elif body.get_content_type() == "text/html":
    text, lossy = strip_html(body.get_content())   # lossy -> unextracted[]
```

### Pattern 4: Attachments & forwarded mail — `iter_attachments()` + maintype check
**What:** `iter_attachments()` yields every non-body part (real attachments AND inline non-body parts
like `message/rfc822`). A forwarded message has `get_content_maintype() == "message"`.
**Example:**
```python
# Source: https://docs.python.org/3.12/library/email.message.html#email.message.EmailMessage.iter_attachments
for part in msg.iter_attachments():
    ct = part.get_content_type()
    if part.get_content_maintype() == "message":   # message/rfc822 forwarded mail  [VERIFIED]
        route_to_unextracted(part, reason="forwarded message/rfc822 — nested mail not extracted (scope)")
    else:                                            # application/pdf, image/png, ...
        route_to_unextracted(part, reason=f"non-text attachment ({ct}) — not extracted")
```
**Gotcha [VERIFIED]:** an *inline* `message/rfc822` has `is_attachment() == False` but `iter_attachments()`
**still yields it** (it is a non-body part). Do NOT filter on `is_attachment()`; iterate everything
`iter_attachments()` yields. Also `get_payload(decode=True)` returns `None` on a `message/rfc822`
container part (it is multipart, not a leaf with CTE) — never call `len()` on it blindly.

### Anti-Patterns to Avoid
- **Parsing without `policy.default`:** silently yields the legacy API and breaks every accessor below. Always pass the policy.
- **Trusting `get_content()` to be faithful:** it substitutes U+FFFD on a charset mismatch and never tells you. Re-decode the body yourself with the strict ladder (Q2) and check for U+FFFD.
- **`chardet`/guessing the charset:** non-deterministic + a dependency. Forbidden.
- **Locator from list position:** `locators.py:17-19` forbids ordinal anchors; use the content span + offsets only.
- **Hand-minting `content_hash`:** adapters must call `Trace.from_source` (CONTEXT decision 1); never compute SHA-256 in the adapter.
- **`get_payload()` without `decode=True`** when you want bytes: prefer the modern `get_content()` for text; only fall to `get_payload(decode=True)` for raw bytes of a *leaf* part you cannot decode.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RFC2047 header word decoding | A `=?charset?enc?...?=` decoder | `str(msg[h])` under `policy.default` | Auto-decoded; edge cases (folding, mixed charsets) handled |
| Content-Transfer-Encoding decode (base64/quoted-printable) | A b64/QP decoder | `get_content()` / `get_payload(decode=True)` | Handles CTE + line-ending quirks |
| MIME boundary parsing / multipart walk | A boundary splitter | `msg.walk()` / `iter_parts()` / `iter_attachments()` / `get_body()` | Nested multiparts, defects, preamble/epilogue all handled |
| Charset → unicode decode | A charset alias table | `bytes.decode(name)` (stdlib codec registry) | Stdlib already aliases hundreds of charset names |
| SHA-256 content-addressing | Any hashing in the adapter | `Trace.from_source(source,start,end)` | Single-place pinning (`semantic.py:109-153`); validates offsets, slices verbatim span |
| Faithfulness / span-containment | A containment check in the adapter | The Phase-3 `SpanContainmentFaithfulness` gate (auto via `assert_conforms`) | Already built (`faithfulness.py`); "one trust rule, one place" |
| "no silent drop" enforcement | A manual coverage tally | `Coverage` model validator (`coverage.py:54-67`) | `complete=True` with non-empty `unextracted[]` is *unrepresentable* |

**Key insight:** Email is a deceptively deep format (RFC 5322 + the MIME RFCs + decades of
non-conforming real-world mail). The stdlib `email` package encodes that accumulated knowledge; every
line you hand-roll is a faithfulness bug waiting to happen. The adapter's value is *decision-making*
(what to extract vs. route to `unextracted[]`), not *parsing*.

## Runtime State Inventory

> Not a rename/refactor/migration phase — this is a greenfield adapter. Section included only to record
> the explicit "nothing to migrate" finding so the planner isn't left guessing.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no datastore keys/collections reference this phase. Adapter is pure function of input bytes. | none |
| Live service config | None — no external service config. | none |
| OS-registered state | None. | none |
| Secrets/env vars | None — the adapter reads `.eml` files, no credentials. | none |
| Build artifacts | New package `src/newsletters/adapters/` — must be importable; the `lint-imports` (import-linter) contract and bare-install gate must stay green after adding it. | Confirm `adapters/` adds no AI import reachable from `core`; re-run `lint-imports`. |

**Nothing found in categories 1-4:** verified — the adapter has no runtime state beyond its input file
and the in-memory `Source`/`Distillation`/`Coverage` objects it returns.

## Common Pitfalls

### Pitfall 1: `get_content()` silently substitutes U+FFFD on a charset mismatch
**What goes wrong:** A part declares `charset="utf-8"` but contains a latin-1 byte (`0xe9`).
`get_content()` returns `'caf� ...'` — a `�` replacement char — and **does not raise**. [VERIFIED: live interpreter]
**Why it happens:** the stdlib text-content handler decodes with `errors='replace'` by default.
**How to avoid:** decode the body yourself with the strict ladder (Q2); if the declared charset fails or
the result contains U+FFFD, route that part to `unextracted[]` with the reason recorded. Never let a
`�`-laced paragraph become a Claim.
**Warning signs:** `'�' in decoded_text` is True; or the strict-declared decode raised.

### Pitfall 2: Unknown charset raises `LookupError`, not `UnicodeDecodeError`
**What goes wrong:** `b"hi".decode("x-unknown-cs")` → `LookupError: unknown encoding`. A `try/except
UnicodeDecodeError` misses it and crashes the adapter. [VERIFIED: live interpreter]
**Why it happens:** the codec name isn't in the registry — a *lookup* failure, not a *decode* failure.
**How to avoid:** catch `(UnicodeDecodeError, LookupError)` together in the ladder; on exhaustion fall to
`latin-1` (which is total) and record an `unextracted[]` entry.
**Warning signs:** an uncaught `LookupError` traceback in tests.

### Pitfall 3: Forwarded `message/rfc822` looks like a body, not an attachment
**What goes wrong:** an inline forwarded message has `is_attachment() == False`, so a naive
"attachments only" filter drops it silently — a faithfulness failure (it carries content).
**Why it happens:** `Content-Disposition: inline` ⇒ `is_attachment()` False, but it is still a non-body part.
**How to avoid:** iterate everything `iter_attachments()` yields and branch on
`get_content_maintype() == "message"`; route to `unextracted[]`. Per CONTEXT decision 4, nested mail is
out of scope for extraction in this phase — but it must be *accounted for*, never silently dropped. [VERIFIED]

### Pitfall 4: CRLF line endings shift every offset
**What goes wrong:** raw `.eml` uses CRLF (`\r\n`). If the transcript keeps `\r\n` but paragraph
splitting normalizes to `\n` (or vice-versa), the unit text is no longer a substring of the transcript
and `str.find` returns -1 → the claim "can't be located" and (correctly, but wastefully) routes to
`unextracted[]`.
**Why it happens:** `get_content()` may normalize line endings; the transcript and the located units
must use *identical* newline conventions.
**How to avoid:** normalize the decoded body to `\n` **once**, BEFORE building the transcript, and derive
paragraph units from that same normalized string. The transcript is the single source of truth; units
are slices of it. Then `str.find` always succeeds for a faithful unit.

### Pitfall 5: Duplicate paragraphs collide on offset if you always `find` from 0
**What goes wrong:** two identical paragraphs both resolve to the first occurrence's offset → wrong
provenance, and the second claim's trace points at the first paragraph.
**How to avoid:** advance a running cursor: `idx = transcript.find(unit, cursor); cursor = idx + len(unit)`.
[VERIFIED: two identical "repeat" paragraphs resolved to distinct offsets 28 and 36.]

### Pitfall 6: `get_payload(decode=True)` returns `None` on container parts
**What goes wrong:** calling it on a `multipart/*` or `message/rfc822` part returns `None`;
`len(None)` raises `TypeError`. [VERIFIED]
**How to avoid:** only call `get_payload(decode=True)` on leaf parts (`is_multipart() is False`); for
non-text leaves you only need the fact that it exists + its content-type to record an `unextracted[]` entry.

## Code Examples

### Deterministic charset-fallback ladder (Q2)
```python
# Faithful, deterministic, no chardet. declared -> utf-8 -> latin-1, all strict.
# latin-1 strict decodes ALL 256 byte values and NEVER raises -> the ladder is total. [VERIFIED]
def faithful_decode(raw_bytes: bytes, declared: str | None) -> tuple[str, str, bool]:
    """Return (text, encoding_used, fell_back). fell_back=True => record unextracted[]."""
    tried = []
    candidates = ([declared] if declared else []) + ["utf-8", "latin-1"]
    for enc in candidates:
        try:
            text = raw_bytes.decode(enc, errors="strict")
            fell_back = (declared is not None and enc != declared) or (declared is None and enc != "utf-8")
            return text, enc, fell_back
        except (UnicodeDecodeError, LookupError):
            tried.append(enc)
            continue
    # Unreachable: latin-1 strict cannot fail. Kept for total-function clarity.
    return raw_bytes.decode("latin-1", errors="replace"), "latin-1", True
```

### Deterministic HTML→text stripper (Q4)
```python
# Source: https://docs.python.org/3.12/library/html.parser.html
from html.parser import HTMLParser

class _TextExtractor(HTMLParser):
    _BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "section"}
    _SKIP = {"script", "style", "head"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)  # &amp; -> & deterministically  [VERIFIED]
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._skip_depth += 1
        if tag in self._BLOCK:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self._SKIP and self._skip_depth:
            self._skip_depth -= 1
        if tag in self._BLOCK:
            self._parts.append("\n")

    def handle_data(self, data):
        if not self._skip_depth:
            self._parts.append(data)

def strip_html(html: str) -> tuple[str, bool]:
    """Return (text, lossy). lossy is ALWAYS True: tag-stripping discards structure/links/styling,
    so an HTML-only body's text is reported in unextracted[] AND offered as best-effort paragraphs.
    Per CONTEXT decision 4: HTML-only bodies where stripping is lossy route to unextracted[]."""
    p = _TextExtractor()
    p.feed(html)
    p.close()
    return "".join(p._parts), True
```
**Determinism note [VERIFIED]:** identical input → byte-identical output across runs; `convert_charrefs=True`
resolves entities deterministically. The output is *lossy* by construction (no hrefs, no tables, no
emphasis), which is exactly why CONTEXT decision 4 routes HTML-only bodies to `unextracted[]`.

### Cursor-advancing offset location (Q5) — the heart of `normalize()`
```python
# normalize() locates each verbatim unit by scanning forward from a running cursor, so
# duplicate paragraphs get DISTINCT offsets. Then it mints the trace via Trace.from_source.
from newsletters.semantic import Claim, Source, Trace
from newsletters.distill.coverage import Unextracted
from newsletters.locators import FreeLocator

def normalize(source: Source, units: list[str]) -> tuple[list[Claim], list[Unextracted]]:
    claims: list[Claim] = []
    unextracted: list[Unextracted] = []
    cursor = 0
    transcript = source.transcript
    for unit in units:
        idx = transcript.find(unit, cursor)
        if idx == -1:
            # Not verbatim-locatable -> NEVER fabricate. Account for it honestly.
            unextracted.append(Unextracted(
                locator=FreeLocator(text=unit[:60]),
                reason="unit not verbatim-locatable in transcript (faithful, not suggestive)",
            ))
            continue
        end = idx + len(unit)
        trace = Trace.from_source(source, idx, end)   # pins hash + span verbatim  [semantic.py:109-153]
        claims.append(Claim(text=unit, evidence=[trace]))
        cursor = end
    return claims, unextracted
```
**Why this survives the gate:** `Claim.text == unit == transcript[idx:end] == trace.span`, so the
Phase-3 `SpanContainmentFaithfulness._normalize(claim.text) in _normalize(trace.span)` is trivially True
(`faithfulness.py:62-74`), and `Coverage.complete` is set False whenever `unextracted` is non-empty.

## What Routes to `unextracted[]` — the explicit enumeration

Per CONTEXT decision 4 ("broad, no silent drops"). Every item below is a `Coverage.Unextracted(locator,
reason)`; emitting ANY of them forces `Coverage.complete = False` (the validator makes the alternative
unrepresentable — `coverage.py:54-67`).

| # | Condition | How detected (EmailMessage API) | Reason string (suggested) |
|---|-----------|----------------------------------|---------------------------|
| U1 | Forwarded / nested mail | `part.get_content_maintype() == "message"` (e.g. `message/rfc822`); `get_content()` returns a nested `EmailMessage` [VERIFIED] | `"forwarded message/rfc822 — nested mail not extracted (scope)"` |
| U2 | Non-text attachment | `iter_attachments()` yields it AND `get_content_maintype() not in {"text","message"}` (application/*, image/*, …) | `"non-text attachment (<ctype>, filename=<name>) — not extracted"` |
| U3 | Charset fallback / decode concession | `faithful_decode` returned `fell_back=True`, OR declared charset raised `LookupError`/`UnicodeDecodeError` | `"charset fallback: declared <x> failed, decoded as <enc> — interpretation may be unfaithful"` |
| U4 | Replacement chars present | `'�' in decoded_text` after `get_content()` (the silent-replace trap) [VERIFIED] | `"undecodable bytes replaced with U+FFFD — text not faithful"` |
| U5 | HTML-only body, lossy strip | `get_body(...)` is `text/html` AND no `text/plain` alternative; `strip_html` returns `lossy=True` (always) | `"html-only body — deterministic tag-strip is lossy (structure/links dropped)"` |
| U6 | No readable body | `get_body(preferencelist=("plain","html")) is None` [VERIFIED] | `"no text/plain or text/html body part found"` |
| U7 | Malformed MIME | `msg.defects` or any `part.defects` non-empty (e.g. `CloseBoundaryNotFoundDefect`) [VERIFIED] | `"MIME defect(s): <defect class names>"` |
| U8 | Unit not verbatim-locatable | `transcript.find(unit, cursor) == -1` inside `normalize()` | `"unit not verbatim-locatable in transcript (faithful, not suggestive)"` |

**Zero-silent-drop accounting identity** (the golden-test assertion):
```
(# Claims minted) + (# unextracted[] entries) == (# extractable input units the walk encountered)
```
where "input units" = the chosen body's paragraphs + each non-body MIME part + each defect class.
Nothing the MIME walk touches may be absent from BOTH sides.

## Recommended Transcript Layout (Q5)

`Source.transcript` is the canonical DECODED text. Recommended fixed layout (the planner may tune labels,
but the *structure* — header block, blank-line separator, decoded body — is the contract):

```
From: José García <jose@example.com>
To: Team <team@example.com>
Subject: Quarterly — results
Date: Wed, 17 Jun 2026 09:00:00 +0000

Hello team.

Revenue is up 12% this quarter.
```

Rules that keep spans verbatim and offsets stable:
1. **Header block first**, one decoded header per line as `"<Name>: <str(msg[name])>"`, in the fixed
   order From, To, Subject, Date. Skip a header that is `None` (do not emit an empty line — that would
   shift offsets non-deterministically). Each header *value* (the text after `": "`) is the verbatim
   span a header-Claim locates.
2. **Exactly one blank line** (`"\n\n"`) separates the header block from the body.
3. **Decoded body** appended verbatim, after line-ending normalization to `\n` (Pitfall 4).
4. The transcript is built **once**; every Claim unit (header value or body paragraph) is a *slice* of
   it located by the cursor-advancing `str.find`. Adapters never construct claim text independently of
   the transcript — that is what guarantees `claim.text == trace.span`.
5. `Source.id` = a stable id (e.g. the file path or a derived id); `Source.context` = the raw file path
   (CONTEXT decision 2); `Source.timestamp` may use `msg['Date'].datetime` when present.

**Offset-location algorithm:** see the `normalize()` example above — single forward pass, running
cursor, `str.find(unit, cursor)`, `Trace.from_source(source, idx, idx+len(unit))`. O(n·k) and fully
deterministic.

## Paragraph Segmentation (Q7)

- **Split the normalized body on blank lines** (one or more `\n\n`). Recommended: split on runs of
  `\n\s*\n`-equivalent using a deterministic stdlib approach — e.g. iterate, accumulating lines, and
  flush a paragraph on an empty line. Keep it regex-free where practical (parity with the AI-optional,
  minimal-dependency ethos; the faithfulness gate itself avoids regex — `faithfulness.py:30-31`).
- **Preserve verbatim text.** A paragraph unit must be an exact substring of the transcript. Do NOT
  `.strip()` the paragraph and then store the stripped form as the claim while the transcript holds the
  unstripped form — `str.find` would fail and route a faithful paragraph to `unextracted[]`. Either (a)
  store the unstripped slice, or (b) strip the transcript body identically before locating. Pick ONE and
  apply it to both transcript and units (recommended: normalize trailing whitespace in the transcript
  body once, then segment that exact string).
- **Pitfalls:** CRLF vs LF (normalize to `\n` once — Pitfall 4); trailing whitespace on lines (decide a
  single rule and apply to the transcript itself); a body that is all-whitespace ⇒ zero paragraph
  claims (legitimate; not an `unextracted[]` unless a body part existed but yielded no text).

## Golden-File Test Plan (Q6, ADAPT-06)

**Pattern:** small committed `.eml` fixtures → run `EmailAdapter.distill([source])` → assert the
resulting `DistillationResult` matches an expected typed JSON (claims + traces + coverage). Drive the
contract via the existing `assert_conforms` (`conformance.py`) which already checks shape, return-type,
coverage honesty, span-containment faithfulness, AND the lossless JSON round-trip (D-04).

**Fixture set (each a tiny hand-written `.eml`):**
| Fixture | Exercises | Expected outcome |
|---------|-----------|------------------|
| `plain_simple.eml` | text/plain, ASCII, 2 paragraphs | 4 header Claims + 2 body Claims; `coverage.complete == True`; `unextracted == []` |
| `rfc2047_subject.eml` | `=?utf-8?q?...?=` Subject with `—`/accented chars | Subject Claim text is the *decoded* unicode; span verbatim in transcript |
| `multipart_alternative.eml` | plain + html alternatives | body Claims come from the **plain** part; html alternative NOT double-counted, NOT in unextracted[] (it's the same content) |
| `html_only.eml` | text/html, no plain alternative | best-effort paragraph Claims (optional) + **U5** unextracted[] entry; `complete == False` |
| `mixed_with_pdf.eml` | multipart/mixed, text body + application/pdf attachment | body Claims + **U2** unextracted[] entry for the PDF; `complete == False` |
| `forwarded_rfc822.eml` | nested message/rfc822 | top body Claims + **U1** unextracted[] entry; nested mail NOT extracted; `complete == False` |
| `mislabeled_charset.eml` | declares utf-8, contains latin-1 byte | body decoded via fallback ladder; **U3** (and/or **U4** if U+FFFD) unextracted[] entry; `complete == False` |
| `malformed_boundary.eml` | missing close boundary | **U7** unextracted[] entry from `defects`; still extracts what it can |

**Core assertions (every fixture):**
1. **Zero silent drops:** `len(claims) + len(coverage.unextracted) == expected_total_units` (the
   accounting identity above). This is the success criterion from CONTEXT decision 4.
2. **Faithful spans:** for every Claim, `claim.text == claim.evidence[0].span` and
   `source.transcript[trace.start:trace.end] == claim.text` (re-slice check).
3. **Content-addressed:** every Claim's trace `is_addressed is True` (came through `Trace.from_source`).
4. **Coverage honesty:** `coverage.complete == (len(coverage.unextracted) == 0)` — already guaranteed by
   the validator; assert it to document intent.
5. **Conformance + round-trip:** `assert_conforms(EmailAdapter(...), [source])` passes (drives
   span-containment + lossless JSON round-trip, `conformance.py:38-94`).
6. **Determinism:** parsing the same fixture twice yields equal `DistillationResult` (no time/random in
   claim text; `Source.timestamp` from the Date header, not `now()`).

**Fixture authoring tips:** store fixtures as raw bytes (`.eml`) committed under
`tests/fixtures/eml/`; keep them minimal (a handful of lines); use explicit `Content-Transfer-Encoding`
and `charset` so the decode path is exercised, not incidental. Store expected JSON alongside as
`<fixture>.expected.json` and compare via `model_dump()` (drop volatile fields if any).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Legacy `email.message.Message` + `get_payload()` manual decode | `EmailMessage` via `policy=email.policy.default` + `get_content()`/`get_body()`/`iter_attachments()` | Python 3.6 (policy framework); default-recommended since 3.6, current in 3.12 | Auto RFC2047 + CTE + charset decode; far less hand-rolling |
| `email.message_from_string` | `email.message_from_bytes` (parse bytes, not pre-decoded text) | long-standing best practice | Avoids corrupting non-ASCII before MIME charset handling |

**Deprecated/outdated:**
- Calling the legacy API without a policy: still works but yields `Message` (no modern accessors) — avoid.
- `email.Utils` / `email.Header.decode_header` manual RFC2047 decoding: unnecessary under `policy.default`.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Target runtime is Python 3.12 (pyproject sets `python_version="3.12"`); behaviors were reproduced on the local 3.11.15 interpreter. The `EmailMessage` API is identical across 3.6–3.12. | Standard Stack | LOW — API stable since 3.6; if a 3.12-only nuance exists it would only *add* capability, not break these calls. |
| A2 | The HTML→text strip tag set (`_BLOCK`/`_SKIP`) is a *recommendation*; exact tags are Claude's discretion (CONTEXT). | Code Examples | LOW — output is always flagged lossy → unextracted[], so an imperfect tag set never produces an unfaithful Claim. |
| A3 | Paragraph segmentation = blank-line split with verbatim preservation; the precise whitespace rule is discretion. | Q7 | LOW — any rule is safe as long as transcript and units share it (else faithful text routes to unextracted[], which is honest, not wrong). |

**Note:** No `[ASSUMED]` claims about external packages exist (there are none). All API behaviors are
`[VERIFIED: live interpreter]` and `[CITED: docs.python.org/3.12]`. The three assumptions above are
design-recommendation assumptions, all LOW risk.

## Open Questions

1. **Should HTML-only bodies ALSO emit best-effort paragraph Claims, or ONLY an `unextracted[]` entry?**
   - What we know: CONTEXT decision 4 says HTML-only bodies "where deterministic tag-stripping is lossy"
     route to `unextracted[]`. Stripping is *always* lossy.
   - What's unclear: whether the stripped text should additionally be offered as (clearly-flagged) Claims
     for partial value, or withheld entirely.
   - Recommendation: **emit the stripped paragraphs as Claims AND record a U5 `unextracted[]` entry**
     (the body is still verbatim-locatable in a transcript built from the stripped text, so it passes the
     gate; the U5 entry preserves honesty about lost structure). If the reviewer prefers strict purity,
     withhold Claims and emit only U5 — the planner should surface this as a one-line decision.

2. **`Source.id` derivation.** Path-based id is simplest; a content-derived id is more stable across
   moves. Recommendation: use the file path (matches CONTEXT decision 2 putting the path in `context`);
   defer content-id to a later phase if needed.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python `email` stdlib | `.eml` parse | ✓ | stdlib (3.12 target; 3.11.15 local) | — |
| Python `email.policy` | modern `EmailMessage` | ✓ | stdlib | — |
| Python `html.parser` | HTML→text | ✓ | stdlib | — |
| Python `email.errors` / `email.headerregistry` | defects / header objects | ✓ | stdlib | — |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** none. Everything is stdlib; no `pip install`, no external service.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (declared in `pyproject.toml` `[dev]`) |
| Config file | `pyproject.toml` (`pythonpath = ["src"]`) |
| Quick run command | `pytest tests/test_email_adapter.py -x -q` |
| Full suite command | `pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ADAPT-01 | `normalize()` mints verbatim, content-addressed Claims; non-locatable → unextracted[] | unit | `pytest tests/test_normalize.py -x` | ❌ Wave 0 |
| ADAPT-02 | `.eml` → Source(transcript) → DistillationResult; all U1–U8 routing | unit/integration | `pytest tests/test_email_adapter.py -x` | ❌ Wave 0 |
| ADAPT-02 | adapter registered + conforms to socket | integration | `pytest tests/test_email_adapter.py::test_conforms -x` | ❌ Wave 0 |
| ADAPT-06 | golden fixtures: zero silent drops + JSON round-trip | golden | `pytest tests/test_email_golden.py -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_email_adapter.py tests/test_normalize.py -x -q`
- **Per wave merge:** `pytest -q`
- **Phase gate:** Full suite green + `lint-imports` (import-linter) green + bare-install gate green, before `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `tests/test_normalize.py` — covers ADAPT-01 (offset location, duplicate-paragraph disambiguation, non-locatable routing)
- [ ] `tests/test_email_adapter.py` — covers ADAPT-02 (parse, charset ladder, U1–U8 routing, registry+conformance)
- [ ] `tests/test_email_golden.py` — covers ADAPT-06 (8 fixtures + accounting identity + round-trip)
- [ ] `tests/fixtures/eml/*.eml` + `*.expected.json` — the golden corpus (8 fixtures listed above)
- [ ] No framework install needed — pytest already in `[dev]`.

## Security Domain

> `security_enforcement: true` in `.planning/config.json`. This is an untrusted-input parser (`.eml`
> files may be arbitrary/hostile), so input-validation and resource-exhaustion controls apply.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | adapter has no auth surface |
| V3 Session Management | no | stateless pure function |
| V4 Access Control | no | reads a file path passed in; no privilege boundary crossed here |
| V5 Input Validation | **yes** | stdlib `email` parser (battle-tested); decode failures routed to `unextracted[]`, never crash; catch `(UnicodeDecodeError, LookupError)`; check `msg.defects` |
| V6 Cryptography | no (indirect) | SHA-256 content-address is via `hashlib` in core `Trace.from_source` — never hand-rolled in the adapter |
| V12 Files & Resources | **yes** | `.eml` is untrusted; bound work (see threats below) |

### Known Threat Patterns for stdlib email parsing
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Decompression/parse bomb — deeply nested multipart or huge base64 attachment | Denial of Service | The adapter never *decodes* non-text attachment bytes (records type only, U2); cap nesting depth and/or input file size; rely on `iter_attachments`/`walk` not recursing unboundedly into pathological structures |
| Malformed MIME (missing boundary, bad headers) | Tampering | Parser does not crash — surfaces `msg.defects`; route to U7 rather than raising [VERIFIED: `CloseBoundaryNotFoundDefect`] |
| Mislabeled/hostile charset (`x-unknown-cs`, mislabeled bytes) | Tampering | Strict fallback ladder; `LookupError`/`UnicodeDecodeError` caught; U+FFFD detected (U3/U4); never `errors='replace'` silently |
| HTML body with `<script>`/active content | (Injection — downstream) | `html.parser` extracts TEXT only and skips `script`/`style`; no HTML is rendered or executed by the adapter; output is plain text |
| Header injection via CRLF in extracted values | Tampering | Header values are extracted as text into a transcript, never re-emitted into a network protocol here; downstream surfaces are typed + reviewed |

**Note:** This adapter produces *truth only* and never publishes (HARD RULE, mirrors `manual.py:13-17`).
The no-auto-publish and faithfulness gates are upstream invariants it inherits, not security controls it implements.

## Sources

### Primary (HIGH confidence)
- Live CPython interpreter (3.11.15) — reproduced every API behavior cited (`policy.default` → `EmailMessage`; RFC2047 auto-decode; `get_body`/`get_content`/`iter_attachments`; U+FFFD silent replace; `LookupError` on unknown charset; `message/rfc822` detection; `get_payload(decode=True)` None on containers; `defects`; HTMLParser determinism; cursor `str.find` disambiguation; latin-1 totality).
- docs.python.org/3.12/library/email.message.html — `EmailMessage.get_body`, `iter_attachments`, `get_content`, `get_content_type`, `get_content_maintype`, `is_attachment`, `walk`.
- docs.python.org/3.12/library/email.policy.html — `policy.default` returns `EmailMessage`.
- docs.python.org/3.12/library/email.parser.html — `message_from_bytes` / `BytesParser`.
- docs.python.org/3.12/library/email.headerregistry.html — structured headers, RFC2047 decoded string form, `Date.datetime`.
- docs.python.org/3.12/library/html.parser.html — `HTMLParser`, `convert_charrefs`, `handle_data`/`handle_starttag`.
- Repo contracts (read this session): `semantic.py` (`Source`/`Trace.from_source`/`Claim`), `distill/ports.py`, `distill/registry.py`, `distill/coverage.py`, `distill/conformance.py`, `distill/faithfulness.py`, `distill/manual.py`, `locators.py`.

### Secondary (MEDIUM confidence)
- None required — primary sources covered every claim.

### Tertiary (LOW confidence)
- None. (All search providers are disabled in `.planning/config.json`; research relied on official docs + live verification, which is the stronger path here.)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib only; every module verified present and behaving as cited.
- Architecture: HIGH — derived directly from the live repo contracts (ports/coverage/faithfulness/Trace.from_source) the adapter must satisfy.
- Pitfalls: HIGH — each pitfall was reproduced on the live interpreter (U+FFFD silent replace, LookupError, inline rfc822, payload-None, defects, cursor disambiguation).

**Research date:** 2026-06-17
**Valid until:** 2026-12-17 (stdlib `email`/`html.parser` are stable, slow-moving APIs — 6-month validity).
