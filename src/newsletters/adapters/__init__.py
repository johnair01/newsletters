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

from ..distill import register
from .email_adapter import EmailAdapter
from .normalize import normalize

# Register the Email adapter under the name "email" on package import, so an operator can select
# it via ``newsletters.distill.resolve("email")``. The shape guard in ``register`` confirms it
# satisfies the @runtime_checkable ``DistillPort`` (a ``name`` attribute + a ``distill`` method).
# This import side-effect is acyclic (``distill`` does not import ``adapters``) and AI-free.
register(EmailAdapter())

__all__ = ["normalize", "EmailAdapter"]
