"""Author the 8 golden `.eml` fixtures as EXACT bytes (run once; committed output is the corpus).

These fixtures stand in for untrusted real-world mail. Each is hand-authored, tiny, and uses
EXPLICIT ``Content-Transfer-Encoding`` / ``charset`` so the adapter's decode + routing path is
exercised, not incidental. Written as raw bytes (CRLF headers, a deliberate latin-1 byte) because
an editor cannot be trusted to preserve them. The committed `.eml` files are the corpus; this
script documents exactly how they were produced and lets anyone regenerate them byte-for-byte.

Run:  .venv/bin/python tests/fixtures/eml/_author_fixtures.py
"""

from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).parent

# RFC 5322 wire format uses CRLF line endings; build each fixture as exact bytes.
CRLF = b"\r\n"


def _eml(headers: list[bytes], body: bytes) -> bytes:
    """Assemble a raw message: CRLF-joined headers, a blank line, then the verbatim body."""
    return CRLF.join(headers) + CRLF + CRLF + body


FIXTURES: dict[str, bytes] = {}

# 1) plain_simple.eml — text/plain ASCII, 2 paragraphs. The clean, complete case.
#    Expect: 4 header claims + 2 body claims, complete=True, unextracted == [].
FIXTURES["plain_simple.eml"] = _eml(
    [
        b"From: Ada Lovelace <ada@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: Weekly update",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b"Content-Type: text/plain; charset=us-ascii",
        b"Content-Transfer-Encoding: 7bit",
    ],
    b"We shipped the analytics engine on Tuesday." + CRLF + CRLF
    + b"Revenue is up twelve percent this quarter.",
)

# 2) rfc2047_subject.eml — RFC2047-encoded Subject (=?utf-8?q?...?=) with an em-dash + accent.
#    Expect: Subject claim text is the DECODED unicode, verbatim in the transcript.
#    "Quarterly — café results" encoded as utf-8 quoted-printable.
FIXTURES["rfc2047_subject.eml"] = _eml(
    [
        b"From: Jose Garcia <jose@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: =?utf-8?q?Quarterly_=E2=80=94_caf=C3=A9_results?=",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b"Content-Type: text/plain; charset=utf-8",
        b"Content-Transfer-Encoding: 7bit",
    ],
    b"The numbers held steady.",
)

# 3) multipart_alternative.eml — text/plain + text/html alternatives.
#    Expect: body claims come from the PLAIN part; the html alternative is the SAME content,
#    so it is neither double-counted nor recorded in unextracted[]. complete=True.
_ALT_BOUNDARY = b"ALTBOUND"
FIXTURES["multipart_alternative.eml"] = _eml(
    [
        b"From: Ada Lovelace <ada@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: Alternative parts",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b'Content-Type: multipart/alternative; boundary="' + _ALT_BOUNDARY + b'"',
    ],
    b"--" + _ALT_BOUNDARY + CRLF
    + b"Content-Type: text/plain; charset=us-ascii" + CRLF
    + b"Content-Transfer-Encoding: 7bit" + CRLF + CRLF
    + b"Plain wins over html." + CRLF
    + b"--" + _ALT_BOUNDARY + CRLF
    + b"Content-Type: text/html; charset=us-ascii" + CRLF
    + b"Content-Transfer-Encoding: 7bit" + CRLF + CRLF
    + b"<html><body><p>Plain wins over html.</p></body></html>" + CRLF
    + b"--" + _ALT_BOUNDARY + b"--" + CRLF,
)

# 4) html_only.eml — text/html, NO plain alternative.
#    Expect: best-effort stripped paragraph claims + a U5 (lossy strip) entry. complete=False.
FIXTURES["html_only.eml"] = _eml(
    [
        b"From: Ada Lovelace <ada@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: HTML only",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b"Content-Type: text/html; charset=us-ascii",
        b"Content-Transfer-Encoding: 7bit",
    ],
    b"<html><body><p>First paragraph here.</p>"
    + b"<p>Second paragraph here.</p></body></html>",
)

# 5) mixed_with_pdf.eml — multipart/mixed, text body + a tiny application/pdf attachment.
#    Expect: body claims + a U2 (non-text attachment) entry. complete=False.
#    The attachment payload is a couple of bytes — the adapter NEVER decodes it (DoS mitigation),
#    only records type/filename.
_MIX_BOUNDARY = b"MIXBOUND"
FIXTURES["mixed_with_pdf.eml"] = _eml(
    [
        b"From: Ada Lovelace <ada@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: With attachment",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b'Content-Type: multipart/mixed; boundary="' + _MIX_BOUNDARY + b'"',
    ],
    b"--" + _MIX_BOUNDARY + CRLF
    + b"Content-Type: text/plain; charset=us-ascii" + CRLF
    + b"Content-Transfer-Encoding: 7bit" + CRLF + CRLF
    + b"See the attached report." + CRLF
    + b"--" + _MIX_BOUNDARY + CRLF
    + b"Content-Type: application/pdf; name=\"report.pdf\"" + CRLF
    + b"Content-Transfer-Encoding: base64" + CRLF
    + b'Content-Disposition: attachment; filename="report.pdf"' + CRLF + CRLF
    + b"JVBERi0x" + CRLF  # a couple of bytes; never decoded
    + b"--" + _MIX_BOUNDARY + b"--" + CRLF,
)

# 6) forwarded_rfc822.eml — a nested message/rfc822 part (a forwarded message).
#    Expect: top body claims + a U1 (forwarded mail) entry. complete=False.
_FWD_BOUNDARY = b"FWDBOUND"
_NESTED = (
    b"From: Old Sender <old@example.com>" + CRLF
    + b"To: Old Recipient <orig@example.com>" + CRLF
    + b"Subject: The original message" + CRLF
    + b"Date: Tue, 16 Jun 2026 08:00:00 +0000" + CRLF
    + b"Content-Type: text/plain; charset=us-ascii" + CRLF + CRLF
    + b"This is the forwarded body."
)
FIXTURES["forwarded_rfc822.eml"] = _eml(
    [
        b"From: Ada Lovelace <ada@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: Fwd: the original",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b'Content-Type: multipart/mixed; boundary="' + _FWD_BOUNDARY + b'"',
    ],
    b"--" + _FWD_BOUNDARY + CRLF
    + b"Content-Type: text/plain; charset=us-ascii" + CRLF
    + b"Content-Transfer-Encoding: 7bit" + CRLF + CRLF
    + b"Please see the forwarded note below." + CRLF
    + b"--" + _FWD_BOUNDARY + CRLF
    + b"Content-Type: message/rfc822" + CRLF
    + b"Content-Disposition: attachment" + CRLF + CRLF
    + _NESTED + CRLF
    + b"--" + _FWD_BOUNDARY + b"--" + CRLF,
)

# 7) mislabeled_charset.eml — declares charset=utf-8 but the body contains a raw latin-1 byte
#    (0xe9, "é" in latin-1) that is INVALID standalone utf-8. The strict ladder falls back to
#    latin-1. Expect: a U3 (charset fallback) entry. complete=False.
#    (0xe9 alone is not valid utf-8, so utf-8 strict raises and the ladder falls to latin-1 ->
#     a faithful "é" with no residual U+FFFD, so U3 fires and U4 does not.)
FIXTURES["mislabeled_charset.eml"] = _eml(
    [
        b"From: Jose Garcia <jose@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: Mislabeled body",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b"Content-Type: text/plain; charset=utf-8",
        b"Content-Transfer-Encoding: 8bit",
    ],
    b"Caf\xe9 numbers held steady.",  # 0xe9 is latin-1 'e-acute', invalid as lone utf-8
)

# 8) malformed_boundary.eml — a multipart whose CLOSE boundary is missing.
#    Expect: a U7 (MIME defect, e.g. CloseBoundaryNotFoundDefect) entry; the readable body is
#    still extracted. complete=False.
_BAD_BOUNDARY = b"BADBOUND"
FIXTURES["malformed_boundary.eml"] = _eml(
    [
        b"From: Ada Lovelace <ada@example.com>",
        b"To: Team <team@example.com>",
        b"Subject: Broken boundary",
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000",
        b'Content-Type: multipart/mixed; boundary="' + _BAD_BOUNDARY + b'"',
    ],
    b"--" + _BAD_BOUNDARY + CRLF
    + b"Content-Type: text/plain; charset=us-ascii" + CRLF
    + b"Content-Transfer-Encoding: 7bit" + CRLF + CRLF
    + b"The body is still readable." + CRLF
    # NOTE: no closing "--BADBOUND--" line -> CloseBoundaryNotFoundDefect
)


def main() -> None:
    for name, data in FIXTURES.items():
        (HERE / name).write_bytes(data)
        print(f"wrote {name} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
