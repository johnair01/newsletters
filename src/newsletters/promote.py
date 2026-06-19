"""Promotions — the system's grammar: working artifacts become durable ones, by review.

Two promotions, both **human-gated**:

* ``Claim → KPI`` — a finding becomes a *tracked measure* when it is worth measuring.
* ``Report → Article`` — a record of solving becomes a *durable, peer-reviewed lesson*
  when it is worth teaching.

Both are reviewed steps, not automatic. "You can't fix what you can't measure"; you can't
teach what you haven't reviewed.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .models import Kpi, KpiStatus
from .semantic import (
    Claim,
    ClaimsBlock,
    ProseBlock,
    Review,
    Surface,
)
from .templates import ARTICLE


def promote_claim_to_kpi(
    claim: Claim,
    *,
    title: str,
    owner: str,
    data_link: str,
    status: KpiStatus = KpiStatus.IN_PROGRESS,
) -> Kpi:
    """Promote a traced ``Claim`` into a tracked ``Kpi`` (the measurement bridge).

    Refuses untraced claims: a measure must rest on evidence, like any published claim.
    """
    if not claim.is_traced:
        raise ValueError(
            "Cannot promote an untraced claim to a KPI — a measure must rest on evidence."
        )
    return Kpi(
        title=title,
        status=status,
        owner=owner,
        last_updated=datetime.now(timezone.utc),
        data_link=data_link,
    )


def promote_report_to_article(
    report: Surface,
    *,
    surface_id: str,
    title: str,
    eyebrow: str = "Article · peer-reviewed",
    lead: str = "",
    author: str,
) -> Surface:
    """Promote a Report into a Draft→InReview ``Article`` awaiting **peer** approval.

    Carries the report's traced claims forward, records lineage both ways, and adopts the
    Article template's peer-review policy — so the author cannot self-approve it.
    """
    if report.kind != "report":
        raise ValueError(f"promote_report_to_article expects a report, got {report.kind!r}.")

    claims: list[Claim] = []
    for b in report.blocks:
        if isinstance(b, ClaimsBlock):
            claims.extend(b.claims)

    blocks: list = []
    if lead:
        blocks.append(ProseBlock(text=lead))
    blocks.append(ClaimsBlock(heading="The lesson — traced to the record", claims=claims))

    article = Surface(
        id=surface_id,
        template=ARTICLE,
        title=title,
        eyebrow=eyebrow,
        blocks=blocks,
        traces=list(report.traces),
        byline=[author],
        review=Review(policy=ARTICLE.review_policy, author=author),
    )
    article.lineage.derived_from.append(report.id)
    report.lineage.produced.append(article.id)
    # Open it for review immediately — it now waits on a peer (not the author).
    article.open_pull_request()
    return article
