"""Tests for the Email ``.eml`` adapter (ADAPT-02) — parse, charset ladder, U1-U8 routing.

The adapter is the first stdlib-only ``DistillPort`` backend and proves the shared
``normalize()`` (Plan 01) end-to-end against a deceptively-deep real format. These tests
exercise:

* Task 1 — ``faithful_decode`` charset ladder, ``strip_html`` determinism, canonical
  transcript layout, verbatim paragraph segmentation.
* Task 2 — ``EmailAdapter.distill`` U1-U8 routing, the zero-silent-drop accounting identity,
  faithful content-addressed spans, registration + conformance.

Fixtures are tiny hand-written ``.eml`` byte literals (the big committed golden corpus is
Plan 03). CRLF (``\r\n``) line endings are used deliberately where the parse path matters.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from newsletters.adapters._html_text import strip_html
from newsletters.adapters.email_adapter import EmailAdapter, faithful_decode
from newsletters.distill import (
    Coverage,
    DistillationResult,
    Unextracted,
    assert_conforms,
    available,
    resolve,
)


# --------------------------------------------------------------------------- #
# Task 1 — charset ladder
# --------------------------------------------------------------------------- #


def test_faithful_decode_clean_utf8_no_fallback() -> None:
    text, enc, fell_back = faithful_decode("café".encode("utf-8"), "utf-8")
    assert text == "café"
    assert enc == "utf-8"
    assert fell_back is False


def test_faithful_decode_mislabeled_utf8_falls_back_to_latin1() -> None:
    # 0xe9 is 'é' in latin-1 but an invalid lone continuation byte in utf-8.
    text, enc, fell_back = faithful_decode(b"caf\xe9", "utf-8")
    assert enc == "latin-1"
    assert fell_back is True
    assert text == "café"


def test_faithful_decode_unknown_charset_catches_lookuperror() -> None:
    # An unregistered codec raises LookupError (NOT UnicodeDecodeError); the ladder must
    # catch it and fall through (declared skipped) to a successful decode.
    text, enc, fell_back = faithful_decode(b"hi", "x-unknown-cs")
    assert text == "hi"
    assert fell_back is True
    assert enc in {"utf-8", "latin-1"}


def test_faithful_decode_no_declared_charset_uses_utf8_no_fallback() -> None:
    text, enc, fell_back = faithful_decode(b"hello", None)
    assert text == "hello"
    assert enc == "utf-8"
    assert fell_back is False


# --------------------------------------------------------------------------- #
# Task 1 — deterministic HTML strip
# --------------------------------------------------------------------------- #


def test_strip_html_is_lossy_and_drops_script() -> None:
    text, lossy = strip_html("<p>A</p><script>zzz</script><p>B</p>")
    assert lossy is True
    assert "zzz" not in text
    assert "A" in text and "B" in text


def test_strip_html_is_deterministic() -> None:
    assert strip_html("<p>A</p><p>B</p>") == strip_html("<p>A</p><p>B</p>")


def test_strip_html_skips_style_and_head() -> None:
    text, _ = strip_html("<head><style>x{}</style></head><body><p>Body</p></body>")
    assert "Body" in text
    assert "x{}" not in text


# --------------------------------------------------------------------------- #
# Task 1 — canonical transcript layout + verbatim segmentation
# --------------------------------------------------------------------------- #


def _plain_mail(body: str = "Hello team.\r\n\r\nRevenue is up 12% this quarter.") -> bytes:
    return (
        b"From: Jose Garcia <jose@example.com>\r\n"
        b"To: Team <team@example.com>\r\n"
        b"Subject: Quarterly results\r\n"
        b"Date: Wed, 17 Jun 2026 09:00:00 +0000\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"\r\n" + body.encode("ascii")
    )


def test_transcript_layout_is_header_block_blank_line_body() -> None:
    source, _claims_units, _unx = EmailAdapter().parse(_plain_mail(), "msg.eml")
    expected = (
        "From: Jose Garcia <jose@example.com>\n"
        "To: Team <team@example.com>\n"
        "Subject: Quarterly results\n"
        "Date: Wed, 17 Jun 2026 09:00:00 +0000\n"
        "\n"
        "Hello team.\n"
        "\n"
        "Revenue is up 12% this quarter."
    )
    assert source.transcript == expected


def test_missing_header_emits_no_line() -> None:
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: No To header\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"\r\nBody."
    )
    source, _u, _x = EmailAdapter().parse(raw, "no_to.eml")
    # No "To:" line at all — a missing header must NOT emit a blank line (offset stability).
    assert "\nTo:" not in source.transcript
    assert source.transcript.startswith("From: a@example.com\nSubject: No To header\n\nBody.")


def test_rfc2047_subject_decoded_and_verbatim_in_transcript() -> None:
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: =?utf-8?q?Caf=C3=A9_results?=\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"\r\nBody."
    )
    source, _u, _x = EmailAdapter().parse(raw, "rfc2047.eml")
    assert "Café results" in source.transcript


def test_body_paragraphs_are_exact_substrings_of_transcript() -> None:
    source, units, _x = EmailAdapter().parse(_plain_mail(), "msg.eml")
    body_units = [u for u in units if u not in (
        "Jose Garcia <jose@example.com>",
        "Team <team@example.com>",
        "Quarterly results",
        "Wed, 17 Jun 2026 09:00:00 +0000",
    )]
    assert body_units == ["Hello team.", "Revenue is up 12% this quarter."]
    for u in units:
        assert u in source.transcript


def test_timestamp_from_date_header_and_path_in_context() -> None:
    source, _u, _x = EmailAdapter().parse(_plain_mail(), "/inbox/msg.eml")
    assert source.context == "/inbox/msg.eml"
    assert isinstance(source.timestamp, datetime)
    assert source.timestamp.year == 2026 and source.timestamp.month == 6 and source.timestamp.day == 17


# --------------------------------------------------------------------------- #
# Task 2 — distill() happy path + U1-U8 routing
# --------------------------------------------------------------------------- #


def _distill(raw: bytes, path: str = "msg.eml") -> DistillationResult:
    adapter = EmailAdapter()
    source, _u, _x = adapter.parse(raw, path)
    return adapter.distill([source])


def test_distill_happy_plain_mail() -> None:
    result = _distill(_plain_mail())
    assert isinstance(result, DistillationResult)
    assert result.backend == "email"
    # 4 header claims + 2 body claims
    assert len(result.distillation.claims) == 6
    assert result.coverage.complete is True
    assert result.coverage.unextracted == []


def test_every_claim_is_faithful_and_content_addressed() -> None:
    result = _distill(_plain_mail())
    for claim in result.distillation.claims:
        assert claim.is_traced
        trace = claim.evidence[0]
        assert trace.is_addressed is True
        assert trace.span == claim.text


def test_u1_forwarded_rfc822_routed() -> None:
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: Fwd\r\n"
        b'Content-Type: multipart/mixed; boundary="B"\r\n'
        b"\r\n"
        b"--B\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"\r\nSee forwarded message.\r\n"
        b"--B\r\n"
        b"Content-Type: message/rfc822\r\n"
        b"Content-Disposition: inline\r\n"
        b"\r\n"
        b"From: orig@example.com\r\n"
        b"Subject: Original\r\n"
        b"\r\nNested body.\r\n"
        b"--B--\r\n"
    )
    result = _distill(raw)
    reasons = [u.reason for u in result.coverage.unextracted]
    assert any("message/rfc822" in r for r in reasons)
    assert result.coverage.complete is False
    # nested mail NOT extracted as claims
    assert all("Nested body" not in c.text for c in result.distillation.claims)


def test_u2_non_text_attachment_routed() -> None:
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: With PDF\r\n"
        b'Content-Type: multipart/mixed; boundary="B"\r\n'
        b"\r\n"
        b"--B\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"\r\nReport attached.\r\n"
        b"--B\r\n"
        b"Content-Type: application/pdf\r\n"
        b'Content-Disposition: attachment; filename="r.pdf"\r\n'
        b"Content-Transfer-Encoding: base64\r\n"
        b"\r\nJVBERi0=\r\n"
        b"--B--\r\n"
    )
    result = _distill(raw)
    reasons = [u.reason for u in result.coverage.unextracted]
    assert any("application/pdf" in r for r in reasons)
    assert result.coverage.complete is False


def test_u3_charset_fallback_routed() -> None:
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: Mislabeled\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"Content-Transfer-Encoding: 8bit\r\n"
        b"\r\ncaf\xe9 time\r\n"  # 0xe9 invalid utf-8, latin-1 'é'
    )
    result = _distill(raw)
    reasons = [u.reason for u in result.coverage.unextracted]
    assert any("charset fallback" in r for r in reasons)
    assert result.coverage.complete is False


def test_u4_residual_ufffd_routed() -> None:
    # Declares latin-1 but the byte sequence is a lone utf-8-style replacement injected;
    # we craft a body that decodes cleanly under the declared charset yet contains U+FFFD.
    body = "data � here".encode("utf-8")
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: Replacement\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"Content-Transfer-Encoding: 8bit\r\n"
        b"\r\n" + body + b"\r\n"
    )
    result = _distill(raw)
    reasons = [u.reason for u in result.coverage.unextracted]
    assert any("U+FFFD" in r or "replac" in r.lower() for r in reasons)
    assert result.coverage.complete is False


def test_u5_html_only_emit_both() -> None:
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: HTML only\r\n"
        b"Content-Type: text/html; charset=us-ascii\r\n"
        b"\r\n<html><body><p>First para.</p><p>Second para.</p></body></html>\r\n"
    )
    result = _distill(raw)
    reasons = [u.reason for u in result.coverage.unextracted]
    assert any("html-only" in r.lower() for r in reasons)
    # emit-both: best-effort paragraph claims AND the U5 entry
    body_claims = [c for c in result.distillation.claims if "para" in c.text.lower()]
    assert len(body_claims) >= 1
    assert result.coverage.complete is False


def test_u6_no_readable_body_routed() -> None:
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: Image only\r\n"
        b'Content-Type: multipart/mixed; boundary="B"\r\n'
        b"\r\n"
        b"--B\r\n"
        b"Content-Type: image/png\r\n"
        b'Content-Disposition: attachment; filename="x.png"\r\n'
        b"Content-Transfer-Encoding: base64\r\n"
        b"\r\niVBORw0=\r\n"
        b"--B--\r\n"
    )
    result = _distill(raw)
    reasons = [u.reason for u in result.coverage.unextracted]
    assert any("no text/plain or text/html body" in r for r in reasons)
    assert result.coverage.complete is False


def test_u7_malformed_mime_defect_routed() -> None:
    # multipart with NO closing boundary -> CloseBoundaryNotFoundDefect.
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: Broken\r\n"
        b'Content-Type: multipart/mixed; boundary="B"\r\n'
        b"\r\n"
        b"--B\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"\r\nSome content.\r\n"
        # no --B-- close
    )
    result = _distill(raw)
    reasons = [u.reason for u in result.coverage.unextracted]
    assert any("MIME defect" in r for r in reasons)
    assert result.coverage.complete is False


def test_inline_rfc822_yielded_even_though_not_attachment() -> None:
    # Pitfall 3: inline message/rfc822 has is_attachment()==False but iter_attachments yields it.
    raw = (
        b"From: a@example.com\r\n"
        b"Subject: Fwd inline\r\n"
        b'Content-Type: multipart/mixed; boundary="B"\r\n'
        b"\r\n"
        b"--B\r\n"
        b"Content-Type: text/plain; charset=us-ascii\r\n"
        b"\r\nBody.\r\n"
        b"--B\r\n"
        b"Content-Type: message/rfc822\r\n"
        b"Content-Disposition: inline\r\n"
        b"\r\n"
        b"From: o@example.com\r\n"
        b"\r\nNested.\r\n"
        b"--B--\r\n"
    )
    result = _distill(raw)
    assert any("message/rfc822" in u.reason for u in result.coverage.unextracted)


# --------------------------------------------------------------------------- #
# Task 2/3 — accounting identity, coverage honesty
# --------------------------------------------------------------------------- #


def test_accounting_identity_plain_mail() -> None:
    result = _distill(_plain_mail())
    # 6 claims + 0 unextracted == 6 units walked (4 headers + 2 body paragraphs)
    assert len(result.distillation.claims) + len(result.coverage.unextracted) == 6


def test_coverage_complete_false_whenever_dropped() -> None:
    result = _distill(
        b"From: a@example.com\r\n"
        b"Subject: HTML only\r\n"
        b"Content-Type: text/html; charset=us-ascii\r\n"
        b"\r\n<p>Hi.</p>\r\n"
    )
    if result.coverage.unextracted:
        assert result.coverage.complete is False


# --------------------------------------------------------------------------- #
# Task 3 — registry + conformance
# --------------------------------------------------------------------------- #


def test_registered_under_email() -> None:
    import newsletters.adapters  # noqa: F401  (import triggers registration)

    assert "email" in available()


def test_resolve_returns_backend() -> None:
    import newsletters.adapters  # noqa: F401

    backend = resolve("email")
    assert backend.name == "email"


def test_conforms() -> None:
    adapter = EmailAdapter()
    source, _u, _x = adapter.parse(_plain_mail(), "msg.eml")
    result = assert_conforms(adapter, [source])
    assert isinstance(result, DistillationResult)


def test_determinism_same_eml_identical_result() -> None:
    raw = _plain_mail()
    a = _distill(raw)
    b = _distill(raw)
    assert a.model_dump_json() == b.model_dump_json()


def test_unextracted_entries_use_free_locator_content_anchor() -> None:
    result = _distill(
        b"From: a@example.com\r\n"
        b"Subject: HTML only\r\n"
        b"Content-Type: text/html; charset=us-ascii\r\n"
        b"\r\n<p>Hi.</p>\r\n"
    )
    for u in result.coverage.unextracted:
        assert isinstance(u, Unextracted)
        # locator carries content/reason text, never an ordinal index
        assert u.reason != ""
