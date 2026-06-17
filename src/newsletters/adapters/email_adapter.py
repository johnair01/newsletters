"""The Email ``.eml`` adapter (ADAPT-02) — the first stdlib-only ``DistillPort`` backend.

One ``.eml`` -> one ``Source`` whose ``transcript`` is a canonical DECODED text (a header block
plus the decoded body). The adapter slices verbatim units (the four key header VALUES, then the
body paragraphs) out of that transcript and hands them — IN TRANSCRIPT ORDER — to the shared
``normalize()`` (Plan 01), which mints content-addressed ``Claim(+Trace)``. The adapter
hand-mints NO hashes; the faithful-extraction rule lives only in ``normalize()`` (CONTEXT
decision 1).

Email is a deceptively-deep format; the value here is *decision-making* — extract vs. route to
``unextracted[]`` — not parsing. The stdlib ``email`` package owns parsing. Everything the walk
touches that the adapter cannot faithfully extract is accounted for in ``Coverage.unextracted[]``
(U1-U7 here; U8 — non-locatable units — is delegated to ``normalize()``). ZERO silent drops.

The charset ladder (CONTEXT decision 7) is the research top-risk: ``get_content()`` silently
substitutes U+FFFD on a mislabeled charset and never raises, so the adapter re-decodes the body
itself with a fixed ``declared -> utf-8 -> latin-1`` ladder (all ``errors='strict'``; latin-1 is
total) and routes any non-declared fallback / residual U+FFFD / ``LookupError`` /
``UnicodeDecodeError`` to ``unextracted[]``.

HARD RULE (mirrors ``manual.py:13-17``): this returns truth only. It NEVER calls
``Surface.publish``, sets ``ReviewState.PUBLISHED``, or builds a published ``Review``.

This is the ONLY module that imports ``email``. It imports no AI library and never computes a
SHA-256 (``grep`` the verification block in the plan).
"""

from __future__ import annotations

import email
import email.policy
from email.message import EmailMessage, Message

from ..distill.coverage import Coverage, Unextracted
from ..distill.ports import DistillationResult
from ..locators import FreeLocator
from ..semantic import Distillation, Source
from ._html_text import strip_html
from .normalize import normalize

# The fixed, deterministic charset-fallback ladder (after the declared charset): never guess
# (no chardet — CONTEXT decision 5). latin-1 strict decodes all 256 byte values and NEVER raises,
# so the ladder is a total function and always terminates.
_FALLBACK_LADDER = ("utf-8", "latin-1")

# The four key headers that become claims, in the fixed transcript order (CONTEXT decision 3).
_HEADER_ORDER = ("From", "To", "Subject", "Date")

# The U+FFFD replacement char — its presence after decode means bytes were unfaithfully replaced.
_REPLACEMENT = "�"

# ---- reason strings (the U1-U8 contract; Plan 03's golden corpus pins these) ----------------
_R_RFC822 = "forwarded message/rfc822 — nested mail not extracted (scope)"
_R_ATTACH = "non-text attachment ({ctype}, filename={name}) — not extracted"
_R_CHARSET = "charset fallback: declared {declared} failed, decoded as {enc} — interpretation may be unfaithful"
_R_UFFFD = "undecodable bytes replaced with U+FFFD — text not faithful"
_R_HTML = "html-only body — deterministic tag-strip is lossy (structure/links dropped)"
_R_NOBODY = "no text/plain or text/html body part found"
_R_DEFECT = "MIME defect(s): {defects}"


def faithful_decode(raw_bytes: bytes, declared: str | None) -> tuple[str, str, bool]:
    """Decode ``raw_bytes`` via the fixed ladder ``declared -> utf-8 -> latin-1`` (all strict).

    Returns ``(text, encoding_used, fell_back)``. ``fell_back=True`` is the signal the caller
    records a ``U3`` ``unextracted[]`` entry: the bytes did not decode under the encoding the
    sender DECLARED, so our interpretation may be unfaithful.

    Catches BOTH ``UnicodeDecodeError`` (bytes invalid for a known codec) AND ``LookupError`` (an
    unknown/unregistered charset name — RESEARCH Pitfall 2). latin-1 strict cannot raise, so the
    ladder is total.
    """
    candidates: list[str] = ([declared] if declared else []) + list(_FALLBACK_LADDER)
    for enc in candidates:
        try:
            text = raw_bytes.decode(enc, errors="strict")
        except (UnicodeDecodeError, LookupError):
            continue
        if declared is not None:
            fell_back = enc != declared
        else:
            fell_back = enc != "utf-8"
        return text, enc, fell_back
    # Unreachable: latin-1 strict is total. Kept for a defined return on every path.
    return raw_bytes.decode("latin-1", errors="strict"), "latin-1", True


def _segment_paragraphs(body: str) -> list[str]:
    """Split a decoded body into verbatim paragraphs on blank-line runs.

    ONE whitespace rule, applied so transcript and units share it (RESEARCH Q7, Pitfall 4): each
    paragraph is the ``strip()``-ed run of non-blank lines. The CALLER rebuilds the transcript
    body as ``"\\n\\n".join(paragraphs)`` from these exact strings, so every unit is by
    construction an exact substring — a faithful paragraph never routes to ``unextracted[]`` for
    a whitespace mismatch.
    """
    paragraphs: list[str] = []
    current: list[str] = []
    for line in body.split("\n"):
        if line.strip() == "":
            if current:
                paragraphs.append("\n".join(current).strip())
                current = []
        else:
            current.append(line)
    if current:
        paragraphs.append("\n".join(current).strip())
    return [p for p in paragraphs if p]


def _defect_names(msg: Message) -> list[str]:
    """The class names of any structural MIME defects on ``msg`` (empty if well-formed)."""
    return [type(d).__name__ for d in getattr(msg, "defects", [])]


class EmailAdapter:
    """Parse ``.eml`` bytes into a ``Source`` + verbatim units, then ``normalize()`` -> result.

    Registered under the name ``"email"`` (see ``adapters/__init__.py``). ``distill(sources)`` is
    signature-exact with ``DistillPort``; ``parse(raw, path)`` is the public entrypoint that turns
    raw ``.eml`` bytes into the ``Source`` this backend distills (mirrors how ``manual.py``
    constructor-injects its ``WorkSession`` — here the raw-bytes parse builds the ``Source``).
    """

    name = "email"

    def __init__(self) -> None:
        # parse() records each Source's adapter-side unextracted[] (U1-U7) here, keyed by
        # source.id, so the contract-exact distill(sources) can recover the drops that are NOT
        # reconstructable from the decoded transcript alone (a forwarded part, an attachment, a
        # charset fallback). This mirrors manual.py constructor-injecting its WorkSession: the
        # adapter carries the format-specific state distill() needs, while distill(sources) stays
        # signature-exact with DistillPort.
        self._adapter_unextracted: dict[str, list[Unextracted]] = {}

    # ------------------------------------------------------------------ #
    # Parse: raw .eml bytes -> (Source, body-claim units, partial unextracted[])
    # ------------------------------------------------------------------ #
    def parse(
        self, raw: bytes, path: str
    ) -> tuple[Source, list[str], list[Unextracted]]:
        """Parse ``raw`` ``.eml`` bytes into a ``Source`` + transcript-order units + partial drops.

        ``path`` is the raw file path/identifier; it becomes ``Source.id`` and ``Source.context``
        (CONTEXT decision 2). ``Source.timestamp`` comes from the ``Date`` header when present.
        Returns the verbatim body+header units to hand to ``normalize()`` and the adapter's OWN
        ``unextracted[]`` entries (U1-U7); ``distill()`` merges them with ``normalize()``'s U8.

        ALWAYS parses bytes with ``policy=email.policy.default`` so we get the modern
        ``EmailMessage`` API (``get_body``/``iter_attachments``/``get_content``). Robust to hostile
        input: malformed MIME surfaces as ``defects`` (U7), never an exception that aborts.
        """
        msg = email.message_from_bytes(raw, policy=email.policy.default)
        assert isinstance(msg, EmailMessage)

        unextracted: list[Unextracted] = []

        # ---- headers (decoded string form; missing -> no line, no offset shift) -------------
        header_lines: list[str] = []
        header_units: list[str] = []
        for name in _HEADER_ORDER:
            value = msg[name]
            if value is None:
                continue
            decoded = str(value)
            header_lines.append(f"{name}: {decoded}")
            header_units.append(decoded)

        # ---- timestamp from Date header (not now()) -----------------------------------------
        timestamp = None
        date_hdr = msg["Date"]
        if date_hdr is not None:
            dt = getattr(date_hdr, "datetime", None)
            if dt is not None:
                timestamp = dt

        # ---- body selection + faithful decode -----------------------------------------------
        body_text, body_unx = self._decode_body(msg)
        unextracted.extend(body_unx)

        # ---- non-body parts: forwarded mail (U1), non-text attachments (U2) -----------------
        unextracted.extend(self._walk_attachments(msg))

        # ---- structural defects (U7) — top-level + every part -------------------------------
        unextracted.extend(self._collect_defects(msg))

        # ---- segment body into verbatim paragraphs, rebuild canonical transcript ------------
        paragraphs = _segment_paragraphs(body_text) if body_text else []
        body_block = "\n\n".join(paragraphs)
        if header_lines and body_block:
            transcript = "\n".join(header_lines) + "\n\n" + body_block
        else:
            transcript = "\n".join(header_lines) + body_block

        source = Source(
            id=path,
            context=path,
            transcript=transcript,
            **({"timestamp": timestamp} if timestamp is not None else {}),
        )
        units = header_units + paragraphs
        # Record adapter-side drops so the contract-exact distill(sources) can recover them.
        self._adapter_unextracted[source.id] = unextracted
        return source, units, unextracted

    # ------------------------------------------------------------------ #
    # Body selection + the charset ladder (CONTEXT decision 7)
    # ------------------------------------------------------------------ #
    def _decode_body(self, msg: EmailMessage) -> tuple[str, list[Unextracted]]:
        """Pick + faithfully decode the body. Returns ``(decoded_text, partial_unextracted)``."""
        unextracted: list[Unextracted] = []
        body = msg.get_body(preferencelist=("plain", "html"))
        if body is None:
            unextracted.append(
                Unextracted(locator=FreeLocator(text="(no body)"), reason=_R_NOBODY)
            )
            return "", unextracted

        ctype = body.get_content_type()
        raw_bytes = body.get_payload(decode=True)
        # A leaf text part always decodes to bytes; guard the (unexpected) None to stay robust.
        if not isinstance(raw_bytes, (bytes, bytearray)):
            unextracted.append(
                Unextracted(locator=FreeLocator(text="(no body)"), reason=_R_NOBODY)
            )
            return "", unextracted

        declared = body.get_content_charset()
        text, enc, fell_back = faithful_decode(bytes(raw_bytes), declared)
        # Normalize line endings to \n ONCE, before anything slices it (Pitfall 4).
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        if ctype == "text/html":
            # CONTEXT decision 6 — emit both: strip to text (the transcript body) AND disclose U5.
            text, _lossy = strip_html(text)
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            unextracted.append(
                Unextracted(locator=FreeLocator(text=text[:60]), reason=_R_HTML)
            )

        # U3: any non-declared fallback (or a declared charset that raised) is a faithfulness risk.
        if fell_back:
            unextracted.append(
                Unextracted(
                    locator=FreeLocator(text=text[:60]),
                    reason=_R_CHARSET.format(declared=declared, enc=enc),
                )
            )
        # U4: residual U+FFFD means bytes were unfaithfully replaced somewhere upstream.
        if _REPLACEMENT in text:
            unextracted.append(
                Unextracted(locator=FreeLocator(text=text[:60]), reason=_R_UFFFD)
            )

        return text, unextracted

    # ------------------------------------------------------------------ #
    # Non-body parts: U1 forwarded message/rfc822, U2 non-text attachments
    # ------------------------------------------------------------------ #
    def _walk_attachments(self, msg: EmailMessage) -> list[Unextracted]:
        """Account for every non-body part. Iterate ALL of ``iter_attachments()``.

        Do NOT filter on ``is_attachment()``: an inline ``message/rfc822`` has
        ``is_attachment()==False`` but IS yielded here (RESEARCH Pitfall 3). Never
        ``get_payload(decode=True)`` a container (returns None — Pitfall 6); we only need the
        content-type to account for it, never the bytes (DoS mitigation T-04-05).
        """
        out: list[Unextracted] = []
        for part in msg.iter_attachments():
            maintype = part.get_content_maintype()
            ctype = part.get_content_type()
            if maintype == "message":
                out.append(
                    Unextracted(locator=FreeLocator(text=ctype), reason=_R_RFC822)
                )
            elif maintype != "text":
                name = part.get_filename() or "(unnamed)"
                out.append(
                    Unextracted(
                        locator=FreeLocator(text=ctype),
                        reason=_R_ATTACH.format(ctype=ctype, name=name),
                    )
                )
            # A text/* attachment (rare) is neither body nor a drop here; not silently lost —
            # it is simply not a non-text/forwarded part. (No text attachment in the fixtures.)
        return out

    # ------------------------------------------------------------------ #
    # U7: structural MIME defects on the message or any part
    # ------------------------------------------------------------------ #
    def _collect_defects(self, msg: EmailMessage) -> list[Unextracted]:
        """One U7 entry per part (incl. root) that carries non-empty ``defects``."""
        out: list[Unextracted] = []
        for part in msg.walk():
            names = _defect_names(part)
            if names:
                out.append(
                    Unextracted(
                        locator=FreeLocator(text=part.get_content_type()),
                        reason=_R_DEFECT.format(defects=", ".join(names)),
                    )
                )
        return out

    # ------------------------------------------------------------------ #
    # The DistillPort entrypoint
    # ------------------------------------------------------------------ #
    def distill(self, sources: list[Source]) -> DistillationResult:
        """Mint claims via ``normalize()`` and merge adapter-drops with normalize-drops.

        Each ``Source`` here was produced by ``parse()`` (transcript + units). We re-derive the
        units from the transcript the same deterministic way ``parse`` did, so a ``Source`` that
        round-tripped through JSON still distills identically. Returns truth only — never
        publishes (HARD RULE, ``manual.py:13-17``).
        """
        all_claims = []
        merged_unextracted: list[Unextracted] = []
        traces: list[Source] = []

        for source in sources:
            units, adapter_unx = self._units_for(source)
            claims, norm_unx = normalize(source, units)
            all_claims.extend(claims)
            merged_unextracted.extend(adapter_unx)
            merged_unextracted.extend(norm_unx)
            traces.append(source)

        coverage = Coverage(
            complete=(len(merged_unextracted) == 0),
            unextracted=merged_unextracted,
            cost_hint="free",
            effort_hint="deterministic",
        )
        return DistillationResult(
            distillation=Distillation(claims=all_claims, traces=traces),
            coverage=coverage,
            backend=self.name,
        )

    def _units_for(self, source: Source) -> tuple[list[str], list[Unextracted]]:
        """Derive header + paragraph units from an already-built transcript ``Source``.

        ``parse()`` put the canonical transcript on the ``Source``; here we recover the verbatim
        units (header values + body paragraphs) by re-splitting that same transcript with the SAME
        whitespace rule (header/body split = the first blank line), so ``claim.text`` is always an
        exact substring of ``source.transcript`` and ``normalize()`` locates every one.

        The adapter-side ``unextracted[]`` (U1-U7) is NOT reconstructable from the decoded
        transcript alone (a stripped attachment leaves no trace there), so it is recovered from
        the per-source record ``parse()`` stored. A ``Source`` not produced by this adapter's
        ``parse`` simply has no recorded drops — its claims are still minted faithfully.
        """
        transcript = source.transcript
        if "\n\n" in transcript:
            header_block, body_block = transcript.split("\n\n", 1)
        else:
            header_block, body_block = transcript, ""
        header_units = [
            line.split(": ", 1)[1]
            for line in header_block.split("\n")
            if ": " in line
        ]
        paragraphs = _segment_paragraphs(body_block) if body_block else []
        adapter_unx = self._adapter_unextracted.get(source.id, [])
        return header_units + paragraphs, adapter_unx
