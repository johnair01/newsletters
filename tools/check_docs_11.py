#!/usr/bin/env python
"""Phase-11 doc gate: the install/work-surface flow + self-host-fonts note are documented.

Specs are the source of truth (CLAUDE.md). This gate proves Plan 11-05 Task 3 actually landed
the documentation (no silent code/spec drift): the work-surface install/dogfood flow in
architecture/product-spec, and the executed self-host-fonts mandate in design-system.

stdlib only; no AI; safe on the bare install. Exit 0 if documented, exit 1 (naming the gap) if not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def _read(p: str) -> str:
    fp = Path(p)
    return fp.read_text(encoding="utf-8") if fp.exists() else ""


def main() -> int:
    flow = (_read("docs/architecture.md") + "\n" + _read("docs/product-spec.md")).lower()
    design = _read("docs/design-system.md").lower()

    failures: list[str] = []

    # The install/work-surface flow: at least one concrete marker of the new path.
    flow_markers = (r"capture_files", r"--corpus", r"work corpus", r"work[- ]surface")
    if not any(re.search(m, flow) for m in flow_markers):
        failures.append(
            "docs/architecture.md or docs/product-spec.md must document the work-surface install "
            "flow (capture_files / --corpus / work corpus / work-surface)."
        )

    # The self-host-fonts note: the mandate is recorded as executed.
    if not any(m in design for m in ("font-face", "self-host", "self host")):
        failures.append(
            "docs/design-system.md must record the self-hosted @font-face / DM-first fallback "
            "(the no-external-font-call mandate, executed)."
        )

    if failures:
        for f in failures:
            print(f"DOC GAP: {f}")
        return 1
    print("docs ok: install/work-surface flow + self-host-fonts note are documented.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
