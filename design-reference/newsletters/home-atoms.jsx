// newsletters/home-atoms.jsx — shared chrome for the open-source "Newsletters"
// home directions. Re-uses the Signals design language (tokens.css + atoms.jsx)
// but rebrands the product as "Newsletters" and adopts the new nav spine:
//   Start here · Newsletters · Articles · Show
// De-Intel'd: all worked-example content is a neutral software team.

// ---- GitHub glyph ----
function IconGit({ size = 14 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
    </svg>
  );
}

// ---- Newsletters nav — dark chrome bar, new spine ----
const NL_LINKS = [
  ['Start here', '#start'],
  ['Newsletters', '#newsletters'],
  ['Articles', '#articles'],
  ['The Show', '#show'],
];

function NLNav({ active, theme, onToggle, accent = 'var(--color-brand-primary)', tagline = 'working in the open', links = NL_LINKS }) {
  return (
    <header className="site-nav" style={{ position: 'sticky', top: 0, zIndex: 50, background: 'var(--chrome-bg)', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 44px', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
      <a href="#start" style={{ display: 'flex', alignItems: 'baseline', gap: 12, textDecoration: 'none' }}>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--chrome-fg)', letterSpacing: '-0.01em' }}>Newsletters</span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'rgba(245,243,238,0.45)' }}>{tagline}</span>
      </a>
      <nav style={{ display: 'flex', gap: 28 }}>
        {links.map(([label, href]) => {
          const on = active === label;
          return (
            <a key={label} href={href} style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.12em', textTransform: 'uppercase', textDecoration: 'none', whiteSpace: 'nowrap', color: on ? '#fff' : 'rgba(245,243,238,0.6)', borderBottom: on ? `2px solid ${accent}` : '2px solid transparent', paddingBottom: 4, cursor: 'pointer', transition: 'color 160ms' }}>{label}</a>
          );
        })}
      </nav>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <ThemeToggle theme={theme} onToggle={onToggle} onDark />
        <a href="#" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontFamily: 'var(--font-mono)', fontSize: 10.5, letterSpacing: '0.1em', textTransform: 'uppercase', textDecoration: 'none', color: 'rgba(245,243,238,0.85)', border: '1px solid rgba(255,255,255,0.22)', padding: '8px 14px', cursor: 'pointer' }}>
          <IconGit size={13} /> GitHub
        </a>
      </div>
    </header>
  );
}

// ---- shared footer ----
function NLFooter({ maxWidth = 1180 }) {
  return (
    <footer style={{ background: 'var(--chrome-bg)', borderTop: '3px solid var(--color-brand-primary)', padding: '46px 44px 32px', marginTop: 64 }}>
      <div style={{ maxWidth, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr', gap: 40 }} className="nl-foot-grid">
          <div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
              <span style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--chrome-fg)' }}>Newsletters</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'rgba(245,243,238,0.4)' }}>working in the open</span>
            </div>
            <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 18, color: 'rgba(245,243,238,0.7)', marginTop: 16, maxWidth: 360, lineHeight: 1.4 }}>Turn information into conversation. Conversation into action.</p>
          </div>
          {[['Surfaces', ['Start here', 'Newsletters', 'Articles', 'The Show']], ['Project', ['README & spec', 'Architecture', 'How review works', 'Contributing']]].map(([h, items]) => (
            <div key={h}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'rgba(245,243,238,0.4)', marginBottom: 16 }}>{h}</div>
              <ul style={{ display: 'grid', gap: 11 }}>
                {items.map((it) => <li key={it} style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'rgba(245,243,238,0.7)', cursor: 'pointer' }}>{it}</li>)}
              </ul>
            </div>
          ))}
        </div>
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.12)', marginTop: 34, paddingTop: 18, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(245,243,238,0.35)' }}>Open source · MIT · self-hostable</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(245,243,238,0.35)' }}>Renders without JavaScript · WCAG AA</span>
        </div>
      </div>
    </footer>
  );
}

// ---- the four surfaces (generic, software-team framing) ----
const NL_SURFACES = [
  { n: '01', name: 'The Show', tail: 'recorded conversations', body: 'Practitioners walking through real work they did — and the reasoning behind it. The raw material everything else is distilled from.', meta: 'New episode every other week', nav: 'show' },
  { n: '02', name: 'Newsletters', tail: 'the weekly signal, per reader', body: 'A level-headed digest of what changed and why it matters — automatically re-cut for each reader from their own corpus. One shared edition, many personal ones.', meta: 'Sent weekly · ~6-min read', nav: 'newsletters' },
  { n: '03', name: 'The Articles', tail: 'peer-reviewed write-ups', body: 'Durable write-ups generated from conversations and system outputs — every claim traced to a source, human-validated before publish.', meta: 'Published to the Library', nav: 'articles' },
  { n: '04', name: 'The Report', tail: 'the reusable record', body: 'The structured record a surface is built on — regenerated per event so the next person inherits the shape instead of a blank page.', meta: 'One record per event', nav: 'report' },
];

// ---- the publish loop (agentic journalist → PR → human review → publish) ----
const NL_PIPELINE = [
  { k: 'Ingest', t: 'A conversation or event', d: 'A recorded walk-through, an incident, a merged change — structured into a record.' },
  { k: 'Distill', t: 'An agent drafts', d: 'The agentic journalist synthesizes the record into surfaces, tuned to each audience corpus.' },
  { k: 'Review', t: 'Opened as a pull request', d: 'A human reviews the draft in a PR — edits, questions, approves. Rigor as the way it earns trust.' },
  { k: 'Publish', t: 'Merged & relayed', d: 'On merge it ships to the Show, the Letters, the Articles — and the Library remembers it.' },
];

// ---- five practices of working in the open ----
const NL_PRACTICES = [
  ['Public storytelling', 'Set context in the open — what we are doing and why, as we do it.'],
  ['Community contribution', 'Make it easy for anyone to pick up, fork, and add to the work.'],
  ['Prototyping in the wild', 'Ship rough, learn fast, in view of the people it is for.'],
  ['Reflection & documentation', 'Talk openly about mistakes, changes, and what we learned.'],
  ['Remixable products', 'Leave behind records others can reuse — not heroics they can only admire.'],
];

// ---- personas for the personalization demo ----
const NL_PERSONAS = [
  { id: 'maintainer', initials: 'MK', name: 'A maintainer', role: 'Owns the service', accent: 'var(--color-brand-primary)' },
  { id: 'contributor', initials: 'NC', name: 'A new contributor', role: 'First month', accent: 'var(--color-green)' },
  { id: 'lead', initials: 'EL', name: 'An eng lead', role: 'Sponsors the team', accent: 'var(--color-accent)' },
];

Object.assign(window, { IconGit, NLNav, NLFooter, NL_SURFACES, NL_PIPELINE, NL_PRACTICES, NL_PERSONAS });
