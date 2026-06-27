"""The coverage / ``unextracted[]`` honesty contract (SOCK-04, D-05, D-03).

Two distinct kinds of honesty, both surfaced, never silent (D-05):

* **unreadable** — raw content a backend could not extract. Lives HERE, in
  ``Coverage.unextracted[]`` (a ``list[Unextracted]``).
* **unprovable** — a claim with no entailed evidence. Lives in the existing
  ``Distillation.missing[]`` (a ``list[str]``).

These are DISTINCT — different models, different meaning. Do NOT merge them.

The D-05 honesty invariant — a backend may not claim full coverage while admitting it
dropped content — is enforced *in code* by a ``model_validator`` (mirroring the
no-auto-publish gate in ``semantic.py:142-150``): "complete with dropped content" is
unrepresentable, not merely discouraged.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from ..locators import Locator


# --------------------------------------------------------------------------- #
# Unextracted — one piece of raw content a backend could not read
# --------------------------------------------------------------------------- #


class Unextracted(BaseModel):
    """Raw content a backend could NOT extract (the *unreadable* gap, D-05)."""

    locator: Locator
    reason: str = ""


# --------------------------------------------------------------------------- #
# Coverage — the per-result manifest
# --------------------------------------------------------------------------- #


class Coverage(BaseModel):
    """A backend's coverage manifest: did it read everything, and what did it drop?

    ``cost_hint`` / ``effort_hint`` carry the D-03 low-token preference signal so an
    operator can prefer the cheap, deterministic path.
    """

    complete: bool = True
    unextracted: list[Unextracted] = Field(default_factory=list)
    cost_hint: str = "free"
    effort_hint: str = "deterministic"

    @model_validator(mode="after")
    def _complete_means_nothing_dropped(self) -> "Coverage":
        """D-05 honesty invariant: you cannot be ``complete`` and still have dropped content.

        Mirrors the no-auto-publish gate (semantic.py:142-150): the dishonest state is
        made unrepresentable, not merely warned about.
        """
        if self.complete and self.unextracted:
            raise ValueError(
                "Coverage cannot be complete=True with a non-empty unextracted[]: "
                f"{len(self.unextracted)} item(s) were dropped. Set complete=False, or "
                "extract the content. No silent dropping (D-05)."
            )
        return self

    @classmethod
    def fully_covered(cls) -> "Coverage":
        """The hand-authored / nothing-dropped case: complete, with empty ``unextracted[]``."""
        return cls(complete=True, unextracted=[])
