"""The ``adapters`` package — format-specific extraction feeding the ONE shared faithful gate.

Each adapter is a registered ``DistillPort`` backend that does format-specific raw extraction
into intermediate "units," then calls the shared :func:`normalize` to mint typed
``Claim(+Trace)``. The faithful-extraction rule lives ONLY in ``normalize`` (ADAPT-01, CONTEXT
decision 1) — adapters never hand-mint hashes and never decide faithfulness themselves.

This package is stdlib/Pydantic-only and AI-free (the import-linter ``forbid-ai-in-core``
contract, ``source_modules = newsletters``, already covers it — no ``.importlinter`` edit needed).
The Email adapter (Plan 02) and future adapters (Excel, PPTX) slot in alongside ``normalize``.
"""

from __future__ import annotations

from .normalize import normalize

__all__ = ["normalize"]
