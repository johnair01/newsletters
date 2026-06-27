// Shared, typed data for the Signals navigation/IA layer.
// Pure data + types — safe to import from server or client components.
// Prose here is representative (per the handoff); the navigation, switching,
// provenance, library and onboarding mechanics are the real deliverable.

export type SurfaceType = 'report' | 'article' | 'newsletter' | 'show' | 'learning';
export type ReviewState = 'Draft' | 'In Review' | 'Published';

export interface SurfaceMeta {
  type: SurfaceType;
  label: string;
  /** Identity accent color (CSS custom property reference). */
  color: string;
  /** AA-safe text variant of the accent for use on light backgrounds. */
  textColor: string;
  href: string;
  claims: number;
}

/** Canonical left-to-right order of the five reader surfaces. */
export const SURFACE_ORDER: SurfaceType[] = ['report', 'article', 'newsletter', 'show', 'learning'];

export const SURFACES: Record<SurfaceType, SurfaceMeta> = {
  report: { type: 'report', label: 'Report', color: 'var(--color-brand-primary)', textColor: 'var(--color-brand-primary)', href: '/report', claims: 9 },
  article: { type: 'article', label: 'Article', color: 'var(--text)', textColor: 'var(--text)', href: '/article', claims: 6 },
  newsletter: { type: 'newsletter', label: 'Newsletter', color: 'var(--color-amber)', textColor: 'var(--color-amber-ink)', href: '/newsletter', claims: 4 },
  show: { type: 'show', label: 'Show', color: 'var(--color-accent)', textColor: 'var(--color-accent-ink)', href: '/show', claims: 7 },
  learning: { type: 'learning', label: 'Learning', color: 'var(--color-green)', textColor: 'var(--color-green)', href: '/learning', claims: 5 },
};

export const surfaceList: SurfaceMeta[] = SURFACE_ORDER.map((t) => SURFACES[t]);

/** The persistent global nav spine — six primary destinations. */
export const navSpine: { label: string; href: string }[] = [
  { label: 'Start here', href: '/onboarding' },
  { label: 'Library', href: '/library' },
  { label: 'Newsletters', href: '/newsletter' },
  { label: 'Articles', href: '/article' },
  { label: 'The Show', href: '/show' },
  { label: 'Learning', href: '/learning' },
];

/** Breadcrumb label per route. */
export const crumbMap: Record<string, string> = {
  '/': 'Home',
  '/ia': 'IA & Patterns',
  '/library': 'Library',
  '/report': 'Report · Data Model',
  '/article': 'Article · The Semantic Spine',
  '/newsletter': 'Newsletter',
  '/show': 'The Show · Ep.01',
  '/learning': 'Learning · Data Model',
  '/onboarding': 'Start here',
  '/gated': 'Library · Review Round 1',
};

export interface SitemapEntry {
  kicker: string;
  label: string;
  note: string;
  color: string;
  href: string;
}

export const sitemap: SitemapEntry[] = [
  { kicker: 'Front door', label: 'Home', note: 'Start-here reading journey', color: 'var(--color-brand-primary)', href: '/' },
  { kicker: 'Index', label: 'Library', note: 'Browse by record & topic', color: 'var(--text)', href: '/library' },
  { kicker: 'Surface', label: 'Report', note: 'Dense reviewed record', color: 'var(--color-brand-primary)', href: '/report' },
  { kicker: 'Surface', label: 'Article', note: 'Peer-reviewed write-up', color: 'var(--text)', href: '/article' },
  { kicker: 'Surface', label: 'Newsletter', note: 'Per-reader digest', color: 'var(--color-amber)', href: '/newsletter' },
  { kicker: 'Surface', label: 'The Show', note: 'Source conversation', color: 'var(--color-accent)', href: '/show' },
  { kicker: 'Surface', label: 'Learning', note: 'Newcomer re-cut', color: 'var(--color-green)', href: '/learning' },
  { kicker: 'Path', label: 'Onboarding', note: 'Ordered 1→2→3 track', color: 'var(--color-green)', href: '/onboarding' },
];

export interface FooterCol {
  head: string;
  links: { label: string; href: string }[];
}

export const footerCols: FooterCol[] = [
  {
    head: 'Surfaces',
    links: [
      { label: 'Reports', href: '/report' },
      { label: 'Articles', href: '/article' },
      { label: 'Newsletters', href: '/newsletter' },
      { label: 'The Show', href: '/show' },
      { label: 'Learning', href: '/learning' },
    ],
  },
  {
    head: 'Navigate',
    links: [
      { label: 'Start here', href: '/onboarding' },
      { label: 'Library', href: '/library' },
      { label: 'IA & patterns', href: '/ia' },
    ],
  },
];

export interface LibraryRecord {
  id: string;
  title: string;
  topic: string;
  state: ReviewState;
  stateColor: string;
  summary: string;
  /** Surfaces this record is published as. */
  chips: SurfaceType[];
  count: number;
  /** Where "Open →" leads. */
  href: string;
}

export const records: LibraryRecord[] = [
  {
    id: 'datamodel',
    title: 'The Semantic Spine',
    topic: 'Architecture',
    state: 'Published',
    stateColor: 'var(--color-green)',
    summary: 'How the shared record is structured so every surface stays traceable.',
    chips: ['report', 'article', 'newsletter', 'show', 'learning'],
    count: 5,
    href: '/report',
  },
  {
    id: 'kickoff',
    title: 'Project Kickoff',
    topic: 'Process',
    state: 'Published',
    stateColor: 'var(--color-green)',
    summary: 'Scope, readers, and the fan-out thesis agreed at the start.',
    chips: ['report', 'show'],
    count: 2,
    href: '/report',
  },
  {
    id: 'plan',
    title: 'The Build Plan',
    topic: 'Process',
    state: 'In Review',
    stateColor: 'var(--color-amber-ink)',
    summary: 'Sequenced milestones and the review gate definition.',
    chips: ['report', 'newsletter'],
    count: 2,
    href: '/report',
  },
  {
    id: 'rev1',
    title: 'Review Round 1',
    topic: 'Quality',
    state: 'Draft',
    stateColor: 'var(--text-dim)',
    summary: 'First evidence audit — open threads before publish.',
    chips: ['report'],
    count: 1,
    href: '/gated',
  },
];

export const topicNames = ['Architecture', 'Process', 'Quality'] as const;

export interface StateFilterMeta {
  key: 'all' | ReviewState;
  label: string;
  dot: string;
}

export const stateFilterMeta: StateFilterMeta[] = [
  { key: 'all', label: 'All', dot: 'var(--text)' },
  { key: 'Published', label: 'Published', dot: 'var(--color-green)' },
  { key: 'In Review', label: 'In review', dot: 'var(--color-amber)' },
  { key: 'Draft', label: 'Draft', dot: 'var(--text-dim)' },
];

export interface Evidence {
  id: string;
  claim: string;
  span: string;
  source: string;
  /** Route of the surface this evidence lives on. */
  sourceHref: string;
  ts: string;
}

export const evidenceMap: Record<string, Evidence> = {
  e1: {
    id: 'e1',
    claim: '“One record fans out into five reader surfaces.”',
    span: '…we keep ONE reviewed record and re-cut it per audience rather than rewriting facts five times…',
    source: 'The Show — Ep.01',
    sourceHref: '/show',
    ts: '00:14:22',
  },
  e2: {
    id: 'e2',
    claim: '“Every published claim links to its source evidence.”',
    span: '…nothing ships unless the claim points back at a span in the record or transcript…',
    source: 'The Show — Ep.01',
    sourceHref: '/show',
    ts: '00:21:08',
  },
  e3: {
    id: 'e3',
    claim: '“Nothing publishes without human review.”',
    span: '…the gate is Draft → In Review → Published, and a human signs the review…',
    source: 'Report — Build Plan',
    sourceHref: '/report',
    ts: '§3.2',
  },
};

export interface OnboardingStep {
  kicker: string;
  title: string;
  surface: SurfaceType;
  color: string;
  href: string;
  blurb: string;
}

export const onboardingSteps: OnboardingStep[] = [
  {
    kicker: 'Step 1 · Listen',
    title: 'The source conversation',
    surface: 'show',
    color: 'var(--color-accent)',
    href: '/show',
    blurb: 'Everything starts as a real conversation. Hear the raw thinking before it was written up.',
  },
  {
    kicker: 'Step 2 · Read the record',
    title: 'The reviewed Report',
    surface: 'report',
    color: 'var(--color-brand-primary)',
    href: '/report',
    blurb: 'The conversation becomes a dense, reviewed record — the single source of truth other surfaces cite.',
  },
  {
    kicker: 'Step 3 · Go deeper',
    title: 'The peer-reviewed Article',
    surface: 'article',
    color: 'var(--text)',
    href: '/article',
    blurb: 'The argued, citable write-up of the same record for a technical reader.',
  },
  {
    kicker: 'Step 4 · Or start gentle',
    title: 'The Learning re-cut',
    surface: 'learning',
    color: 'var(--color-green)',
    href: '/learning',
    blurb: 'The same record re-cut for a newcomer, plain-language, with a glossary.',
  },
];

export interface JumpItem {
  label: string;
  kind: string;
  color: string;
  href: string;
  /** Search keywords. */
  kw: string;
}

export interface JumpGroup {
  head: string;
  items: JumpItem[];
}

export const jumpGroups: JumpGroup[] = [
  {
    head: 'Surfaces',
    items: [
      { label: 'Report', kind: 'Surface', color: 'var(--color-brand-primary)', href: '/report', kw: 'report record datamodel spine dense' },
      { label: 'Article', kind: 'Surface', color: 'var(--text)', href: '/article', kw: 'article peer review semantic spine' },
      { label: 'Newsletter', kind: 'Surface', color: 'var(--color-amber)', href: '/newsletter', kw: 'newsletter digest reader edition' },
      { label: 'The Show', kind: 'Surface', color: 'var(--color-accent)', href: '/show', kw: 'show episode conversation transcript source' },
      { label: 'Learning', kind: 'Surface', color: 'var(--color-green)', href: '/learning', kw: 'learning newcomer recut glossary start' },
    ],
  },
  {
    head: 'Pages',
    items: [
      { label: 'Home', kind: 'Page', color: 'var(--color-brand-primary)', href: '/', kw: 'home front door' },
      { label: 'Library', kind: 'Index', color: 'var(--text)', href: '/library', kw: 'library index archive browse topic record' },
      { label: 'Start here', kind: 'Path', color: 'var(--color-green)', href: '/onboarding', kw: 'onboarding path guided start here journey' },
      { label: 'IA & Patterns', kind: 'Reference', color: 'var(--color-brand-primary)', href: '/ia', kw: 'ia map sitemap patterns fan-out provenance' },
    ],
  },
  {
    head: 'Records',
    items: [
      { label: 'The Semantic Spine', kind: 'Record', color: 'var(--color-brand-primary)', href: '/report', kw: 'semantic spine datamodel architecture' },
      { label: 'Project Kickoff', kind: 'Record', color: 'var(--color-brand-primary)', href: '/report', kw: 'kickoff process scope' },
      { label: 'The Build Plan', kind: 'Record', color: 'var(--color-amber)', href: '/report', kw: 'build plan milestones review gate' },
    ],
  },
];
