"""Surface templates — the parameterized shape behind every surface.

The four reader-facing surfaces are **not four classes**; they are four
parameterizations of one ``SurfaceTemplate`` (Decision 1). Structure, cadence, audience
scope, and review policy are **typed config** (Decision 2 — only the prose is templated).

An operator (PulseIQ, a factory line, any org) registers its own templates without
touching the core: it contributes by *using*, and owns nothing of the commons.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Cadence(StrEnum):
    """How often a surface is produced. Data, never a hardcoded type."""

    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    PER_EVENT = "per_event"
    ON_DEMAND = "on_demand"

    @property
    def label(self) -> str:
        return {
            Cadence.WEEKLY: "Weekly",
            Cadence.BIWEEKLY: "Every other week",
            Cadence.PER_EVENT: "Per event",
            Cadence.ON_DEMAND: "On demand",
        }[self]


class SignalColor(StrEnum):
    """The accent each surface carries (maps to a design token)."""

    BRAND = "brand"     # Report — brand blue / live
    ACCENT = "accent"   # The Show — terracotta
    AMBER = "amber"     # Newsletter
    INK = "ink"         # Article
    GREEN = "green"

    @property
    def css_var(self) -> str:
        return {
            SignalColor.BRAND: "var(--color-brand-primary)",
            SignalColor.ACCENT: "var(--color-accent)",
            SignalColor.AMBER: "var(--color-amber)",
            SignalColor.INK: "var(--color-ink)",
            SignalColor.GREEN: "var(--color-green)",
        }[self]


class AudienceScope(StrEnum):
    """Who a surface is addressed to — individual reader up to the open commons."""

    INDIVIDUAL = "individual"
    GROUP = "group"
    ORG = "org"
    PROJECT = "project"
    COMMONS = "commons"


class ReviewPolicy(BaseModel):
    """The gate's strictness — carried per template (Report = light, Article = peer)."""

    min_approvals: int = 1
    require_peer: bool = Field(
        default=False, description="Approver must differ from the author"
    )

    @classmethod
    def light(cls) -> "ReviewPolicy":
        """A simple PR: the author approves and you're good (the Report)."""
        return cls(min_approvals=1, require_peer=False)

    @classmethod
    def peer(cls) -> "ReviewPolicy":
        """Peer review required: someone other than the author must approve (the Article)."""
        return cls(min_approvals=1, require_peer=True)

    def describe(self) -> str:
        base = f"{self.min_approvals} approval(s)"
        return base + (", peer-reviewed (not the author)" if self.require_peer else "")


class SurfaceTemplate(BaseModel):
    """The base/preset for a surface — the 'Jinja template' shape, as typed config."""

    name: str
    display_name: str
    tagline: str = ""
    cadence: Cadence
    personalized: bool = False
    signal_color: SignalColor = SignalColor.BRAND
    scope: AudienceScope = AudienceScope.GROUP
    review_policy: ReviewPolicy = Field(default_factory=ReviewPolicy.light)
    slots: list[str] = Field(default_factory=list)
    distance: int = Field(0, description="0 = closest to raw work; higher = more distilled")


# --------------------------------------------------------------------------- #
# The four canonical presets — increasing distillation, increasing audience
# --------------------------------------------------------------------------- #

SHOW = SurfaceTemplate(
    name="show",
    display_name="The Show",
    tagline="the recorded session everything is distilled from",
    cadence=Cadence.BIWEEKLY,
    personalized=False,
    signal_color=SignalColor.ACCENT,
    scope=AudienceScope.COMMONS,
    review_policy=ReviewPolicy.light(),
    slots=["hero", "chapters", "fanout"],
    distance=0,
)

REPORT = SurfaceTemplate(
    name="report",
    display_name="The Report",
    tagline="how we solved it — the investigation you approve",
    cadence=Cadence.PER_EVENT,
    personalized=False,
    signal_color=SignalColor.BRAND,
    scope=AudienceScope.GROUP,
    review_policy=ReviewPolicy.light(),
    slots=["hero", "kpi", "prose", "claims", "quote", "fanout"],
    distance=1,
)

ARTICLE = SurfaceTemplate(
    name="article",
    display_name="The Article",
    tagline="the durable, peer-reviewed lesson",
    cadence=Cadence.ON_DEMAND,
    personalized=False,
    signal_color=SignalColor.INK,
    scope=AudienceScope.COMMONS,
    review_policy=ReviewPolicy.peer(),
    slots=["hero", "prose", "claims", "prompt"],
    distance=2,
)

NEWSLETTER = SurfaceTemplate(
    name="newsletter",
    display_name="Newsletters",
    tagline="what matters to you this week",
    cadence=Cadence.WEEKLY,
    personalized=True,
    signal_color=SignalColor.AMBER,
    scope=AudienceScope.INDIVIDUAL,
    review_policy=ReviewPolicy.light(),
    slots=["masthead", "lead", "items", "kpi", "quote", "rationale"],
    distance=3,
)


# --------------------------------------------------------------------------- #
# Registry — built-in presets plus operator-registered templates
# --------------------------------------------------------------------------- #

_REGISTRY: dict[str, SurfaceTemplate] = {t.name: t for t in (SHOW, REPORT, ARTICLE, NEWSLETTER)}


def register(template: SurfaceTemplate) -> SurfaceTemplate:
    """Register an operator-defined template (forkability — no core change needed)."""
    _REGISTRY[template.name] = template
    return template


def get_template(name: str) -> SurfaceTemplate:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"No surface template named {name!r}. Known: {sorted(_REGISTRY)}"
        ) from None


def all_templates() -> list[SurfaceTemplate]:
    return sorted(_REGISTRY.values(), key=lambda t: t.distance)
