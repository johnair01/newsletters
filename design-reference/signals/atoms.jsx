// signals/atoms.jsx — shared Signals primitives (exported to window)
// Generic, token-driven building blocks composed differently per direction.

const { useState } = React;

// ---- icons (simple glyphs only) ----
function IconArrow({ size = 13 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 7h8M7.5 3.5L11 7l-3.5 3.5" />
    </svg>
  );
}
function IconCheck({ size = 12 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 6.5L5 9.5L10 3" />
    </svg>
  );
}
function IconPlay({ size = 12 }) {
  return <svg width={size} height={size} viewBox="0 0 12 12" fill="currentColor"><path d="M2.5 1.5v9l8-4.5z" /></svg>;
}
function IconSun({ size = 15 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <circle cx="9" cy="9" r="3.4" />
      <path d="M9 1.5v2M9 14.5v2M1.5 9h2M14.5 9h2M3.7 3.7l1.4 1.4M12.9 12.9l1.4 1.4M14.3 3.7l-1.4 1.4M5.1 12.9l-1.4 1.4" />
    </svg>
  );
}
function IconMoon({ size = 15 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 18 18" fill="currentColor">
      <path d="M14.5 11.2A6 6 0 0 1 6.8 3.5a.6.6 0 0 0-.8-.8 6.6 6.6 0 1 0 9.3 9.3.6.6 0 0 0-.8-.8z" />
    </svg>
  );
}

// ---- eyebrow ----
function Eyebrow({ children, variant = '', withRule = false, style }) {
  return (
    <div className={`sg-eyebrow ${variant}`} style={style}>
      <span>{children}</span>
      {withRule && <span className="sg-rule" style={{ maxWidth: 60 }} />}
    </div>
  );
}

// ---- section divider ----
function SectionDivider({ label, variant = 'brand', centered = false, style }) {
  if (centered) {
    return (
      <div className="sg-divider" style={style}>
        <span className="sg-rule" />
        <span className={`sg-eyebrow ${variant}`}>{label}</span>
        <span className="sg-rule" />
      </div>
    );
  }
  return (
    <div className="sg-divider" style={style}>
      <span className={`sg-eyebrow ${variant}`} style={{ flex: '0 0 auto' }}>{label}</span>
      <span className="sg-rule" />
    </div>
  );
}

// ---- tag ----
function Tag({ kind = 'cat', children, live = false }) {
  return (
    <span className={`sg-tag ${kind}`}>
      {(kind === 'live' || live) && <span className="sg-dot" />}
      {kind === 'peer' && <IconCheck size={10} />}
      {children}
    </span>
  );
}

// ---- governance gate ----
function GateBadge({ current = 'In Review', compact = false }) {
  const steps = ['Draft', 'In Review', 'Published'];
  const ci = steps.indexOf(current);
  return (
    <div className="sg-gate" role="status" aria-label={`Status: ${current}`}>
      {steps.map((s, i) => (
        <React.Fragment key={s}>
          {i > 0 && <span className="sg-gate-sep">›</span>}
          <span className={`sg-gate-step ${i < ci ? 'done' : ''} ${i === ci ? 'current' : ''}`}
            style={i === ci ? { color: s === 'In Review' ? 'var(--color-amber)' : s === 'Published' ? 'var(--color-brand-primary)' : 'var(--text)' } : null}>
            {i === ci && <span className="sg-dot" style={{ marginRight: 6, width: 5, height: 5 }} />}
            {s}
          </span>
        </React.Fragment>
      ))}
    </div>
  );
}

// ---- profile chip ----
function ProfileChip({ initials, name, role, size = 32, photo }) {
  return (
    <div className="sg-chip">
      <div className="sg-avatar" style={{ width: size, height: size, fontSize: size * 0.44, background: photo }}>
        {!photo && initials}
      </div>
      <div>
        <div className="sg-chip-name">{name}</div>
        {role && <div className="sg-chip-role">{role}</div>}
      </div>
    </div>
  );
}

// ---- KPI block ----
function KpiBlock({ items, style }) {
  return (
    <div className="sg-kpi" style={{ gridTemplateColumns: `repeat(${items.length}, 1fr)`, ...style }}>
      {items.map((it, i) => (
        <div className="sg-kpi-cell" key={i}>
          <div className="sg-kpi-label">{it.label}</div>
          <div className="sg-kpi-value">{it.value}</div>
          {it.delta && <div className={`sg-kpi-delta ${it.dir || ''}`}>{it.delta}</div>}
        </div>
      ))}
    </div>
  );
}

// ---- prompt block ----
function PromptBlock({ label = 'Prompt', children, style }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="sg-prompt" style={style}>
      <div className="sg-prompt-head">
        <span className="sg-prompt-label">{label}</span>
        <button className="sg-prompt-copy" onClick={() => { setCopied(true); setTimeout(() => setCopied(false), 1600); }}>
          {copied ? 'Copied ✓' : 'Copy'}
        </button>
      </div>
      <div className="sg-prompt-body">{children}</div>
    </div>
  );
}

// ---- theme toggle ----
function ThemeToggle({ theme, onToggle, onDark = false }) {
  const dark = theme === 'dark';
  return (
    <button
      onClick={onToggle}
      aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={dark ? 'Light mode' : 'Dark mode'}
      style={{
        width: 34, height: 34, display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'transparent', cursor: 'pointer',
        border: `1px solid ${onDark ? 'rgba(255,255,255,0.22)' : 'var(--line)'}`,
        color: onDark ? 'rgba(255,255,255,0.85)' : 'var(--text-dim)',
        transition: 'all 200ms cubic-bezier(0,0,0.2,1)',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.color = onDark ? '#fff' : 'var(--text)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.color = onDark ? 'rgba(255,255,255,0.85)' : 'var(--text-dim)'; }}
    >
      {dark ? <IconMoon /> : <IconSun />}
    </button>
  );
}

// ---- button ----
function Button({ children, ghost = false, withArrow = false, onClick, style }) {
  return (
    <button className={`sg-btn ${ghost ? 'ghost' : ''}`} onClick={onClick} style={style}>
      {children}
      {withArrow && <IconArrow />}
    </button>
  );
}

// ---- striped image placeholder ----
function ImgPlaceholder({ label = 'image', ratio, height, style, dark = false }) {
  const stripe = dark ? 'rgba(255,255,255,0.05)' : 'rgba(10,10,15,0.05)';
  const base = dark ? 'rgba(255,255,255,0.03)' : 'rgba(10,10,15,0.025)';
  return (
    <div style={{
      position: 'relative', width: '100%', aspectRatio: ratio, height,
      background: `repeating-linear-gradient(135deg, ${base} 0 11px, ${stripe} 11px 22px)`,
      border: '1px solid var(--line)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', ...style,
    }}>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--text-dim)', background: 'var(--bg)', padding: '4px 8px' }}>{label}</span>
    </div>
  );
}

// ---- site nav (shared, cross-linked) ----
const SITE = {
  hub: 'Signals%20Hub.html',
  article: 'Signals%20Article.html',
  newsletter: 'Signals%20Newsletter.html',
  report: 'Signals%20Report.html',
  show: 'Signals%20Show.html',
  proposal: 'Signals%20Proposal.html',
};
function SiteNav({ active, theme, onToggle, accent = 'var(--color-brand-primary)', tagline = 'from the underground', action }) {
  const links = [
    ['Start here', SITE.proposal],
    ['The Show', SITE.show],
    ['Newsletter', SITE.newsletter],
    ['Articles', SITE.article],
    ['Archive', SITE.hub],
  ];
  return (
    <header className="site-nav" style={{ position: 'sticky', top: 0, zIndex: 50, background: 'var(--chrome-bg)', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 48px' }}>
      <a href={SITE.hub} style={{ display: 'flex', alignItems: 'baseline', gap: 12, textDecoration: 'none' }}>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: 23, color: 'var(--chrome-fg)', letterSpacing: '-0.01em' }}>Signals</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.45)' }}>{tagline}</span>
      </a>
      <nav style={{ display: 'flex', gap: 30 }}>
        {links.map(([label, href]) => {
          const on = active === label;
          return (
            <a key={label} href={href} style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', textDecoration: 'none', color: on ? '#fff' : 'rgba(255,255,255,0.6)', borderBottom: on ? `2px solid ${accent}` : '2px solid transparent', paddingBottom: 4, cursor: 'pointer' }}>{label}</a>
          );
        })}
      </nav>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <ThemeToggle theme={theme} onToggle={onToggle} onDark />
        {action || <a href={SITE.newsletter} className="sg-btn" style={{ padding: '9px 16px', textDecoration: 'none', background: accent, borderColor: accent }}>Subscribe</a>}
      </div>
    </header>
  );
}

Object.assign(window, {
  IconArrow, IconCheck, IconPlay, IconSun, IconMoon,
  Eyebrow, SectionDivider, Tag, GateBadge, ProfileChip,
  KpiBlock, PromptBlock, ThemeToggle, Button, ImgPlaceholder,
  SiteNav, SITE,
});
