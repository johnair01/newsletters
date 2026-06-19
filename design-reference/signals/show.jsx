// signals/show.jsx — The Show surface · a practitioner-led recorded episode.
// Structured guest onboarding (invite → prep → record → publish), the format
// spine as timestamped chapters, and the one-to-many fan-out. Accent =
// the "recording / live" signal. Owns light/dark.

function Show() {
  const [theme, setTheme] = React.useState('light');
  const [active, setActive] = React.useState('synopsis');
  const dark = theme === 'dark';
  const ACCENT = 'var(--color-accent)';

  const sections = [
    { id: 'synopsis', label: 'Synopsis' },
    { id: 'chapters', label: 'Chapters' },
    { id: 'takeaways', label: 'What to copy' },
    { id: 'fanout', label: 'What it became' },
  ];

  React.useEffect(() => {
    const ids = sections.map((s) => s.id);
    const onScroll = () => {
      let cur = ids[0];
      for (const id of ids) { const el = document.getElementById(id); if (el && el.getBoundingClientRect().top <= 130) cur = id; }
      setActive(cur);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  const goto = (id) => { const el = document.getElementById(id); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 78, behavior: 'smooth' }); };

  const chapters = [
    { ts: '02:10', spine: 'What was the problem', title: '47 minutes, four systems, no agreement' },
    { ts: '06:40', spine: 'What was hard', title: 'The evidence never lined up' },
    { ts: '11:25', spine: 'What actually worked', title: 'Align the timelines, read the disagreements' },
    { ts: '18:30', spine: 'How rigor was held', title: 'Every claim traced to a source' },
    { ts: '24:05', spine: 'What others should copy', title: 'The reusable record, not the heroics' },
    { ts: '31:50', spine: 'What changed', title: 'Two shifts down to two and a half hours' },
  ];

  const onboarding = ['Invite', 'Prep', 'Record', 'Publish'];
  const obStage = 3; // Published

  return (
    <div className="signals article-root" data-theme={theme} style={{ minHeight: '100vh', fontFamily: 'var(--font-body)' }}>

      <SiteNav active="The Show" theme={theme} onToggle={() => setTheme(dark ? 'light' : 'dark')} accent={ACCENT} tagline="from the underground" />

      {/* EPISODE HERO */}
      <header style={{ maxWidth: 1180, margin: '0 auto', padding: '48px 48px 36px', borderBottom: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <div className="sg-eyebrow" style={{ color: ACCENT }}><span>The Show · Episode 014</span><span className="sg-rule" style={{ maxWidth: 50, background: ACCENT, opacity: 0.5 }} /></div>
        </div>
        <h1 className="sg-display" style={{ fontSize: 50, lineHeight: 1.08, maxWidth: 880, marginTop: 16 }}>
          The downtime nobody could explain — <em>a conversation on the floor.</em>
        </h1>

        <div style={{ display: 'flex', alignItems: 'center', gap: 22, marginTop: 22, flexWrap: 'wrap' }}>
          <ProfileChip initials="MO" name="M. Okafor" role="Guest · Reliability Engineer" size={38} />
          <div style={{ width: 1, height: 30, background: 'var(--line)' }} />
          <ProfileChip initials="JJ" name="JJ" role="Host · Practitioner-in-residence" size={38} />
          <div style={{ flex: 1 }} />
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <Tag kind="published">Published</Tag>
            <Tag kind="peer">Peer Reviewed</Tag>
            <span className="sg-mono">38:00</span>
          </div>
        </div>

        {/* recording placeholder */}
        <div style={{ marginTop: 26, position: 'relative' }}>
          <ImgPlaceholder label="recording — line 4 walkthrough, night shift" ratio="16 / 7" dark={dark} />
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <button aria-label="Play episode" style={{ width: 64, height: 64, borderRadius: '50%', border: 'none', background: ACCENT, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', boxShadow: '0 6px 24px rgba(0,0,0,0.25)' }}>
              <span style={{ marginLeft: 4 }}><IconPlay size={22} /></span>
            </button>
          </div>
          {/* faux scrubber */}
          <div style={{ position: 'absolute', left: 16, right: 16, bottom: 14, display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#fff' }}>00:00</span>
            <div style={{ flex: 1, height: 3, background: 'rgba(255,255,255,0.35)', position: 'relative' }}>
              <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '14%', background: ACCENT }} />
              <div style={{ position: 'absolute', left: '14%', top: '50%', width: 10, height: 10, borderRadius: '50%', background: '#fff', transform: 'translate(-50%,-50%)' }} />
            </div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: '#fff' }}>38:00</span>
          </div>
        </div>
      </header>

      {/* BODY */}
      <div className="article-body" style={{ maxWidth: 1180, margin: '0 auto', padding: '0 48px' }}>

        {/* SIDEBAR */}
        <aside className="article-aside" style={{ top: 88, paddingTop: 38 }}>
          {/* onboarding stepper */}
          <div style={{ border: '1px solid var(--line)', borderLeft: `3px solid ${ACCENT}`, padding: '18px 20px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 14 }}>How this episode was made</div>
            <ol style={{ display: 'grid', gap: 0 }}>
              {onboarding.map((s, i) => {
                const done = i <= obStage;
                return (
                  <li key={s} style={{ display: 'grid', gridTemplateColumns: '18px 1fr', gap: 12, alignItems: 'start' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                      <span style={{ width: 16, height: 16, borderRadius: '50%', border: `2px solid ${done ? ACCENT : 'var(--line)'}`, background: done ? ACCENT : 'transparent', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto' }}>{done && <IconCheck size={8} />}</span>
                      {i < onboarding.length - 1 && <span style={{ width: 2, flex: 1, minHeight: 18, background: i < obStage ? ACCENT : 'var(--line)' }} />}
                    </div>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', color: done ? 'var(--text)' : 'var(--text-dim)', fontWeight: i === obStage ? 600 : 400, paddingBottom: 14 }}>{s}{i === obStage && ' ✓'}</span>
                  </li>
                );
              })}
            </ol>
          </div>

          {/* In this episode */}
          <div style={{ marginTop: 24 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 12 }}>In this episode</div>
            <ul style={{ display: 'grid', gap: 1 }}>
              {sections.map((s) => {
                const on = active === s.id;
                return (
                  <li key={s.id}>
                    <a onClick={() => goto(s.id)} style={{ display: 'block', fontSize: 13, padding: '7px 12px', marginLeft: -12, cursor: 'pointer', color: on ? ACCENT : 'var(--text-dim)', borderLeft: on ? `2px solid ${ACCENT}` : '2px solid var(--line)', background: on ? 'color-mix(in oklab, var(--color-accent) 12%, transparent)' : 'transparent', fontWeight: on ? 600 : 400, transition: 'color 150ms, background 150ms' }}>{s.label}</a>
                  </li>
                );
              })}
            </ul>
          </div>

          {/* meta */}
          <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', rowGap: 10, columnGap: 14, margin: '22px 0 0', borderTop: '1px solid var(--line)', paddingTop: 18 }}>
            {[['Recorded', 'Jun 06 · 2026'], ['Chapters', '6'], ['Case', 'Downtime RCA']].map(([k, v]) => (
              <React.Fragment key={k}>
                <dt className="sg-mono" style={{ color: 'var(--text-dim)' }}>{k}</dt>
                <dd style={{ margin: 0, fontSize: 13, color: 'var(--text)', fontWeight: 500 }}>{v}</dd>
              </React.Fragment>
            ))}
          </dl>
        </aside>

        {/* MAIN */}
        <main className="article-main" style={{ paddingTop: 40, minWidth: 0 }}>
          <div style={{ maxWidth: 720 }}>

            {/* SYNOPSIS */}
            <section id="synopsis" style={{ scrollMarginTop: 80 }}>
              <SectionDivider label="Synopsis" variant="accent" />
              <p style={{ fontSize: 17, lineHeight: 1.7, color: 'var(--text)', marginTop: 18 }}>
                A line went down for 47 minutes and four systems each told a different story. In this episode, M. Okafor walks JJ through the night — not a polished post-mortem, but the actual reasoning: what they tried, what failed, and the moment the four systems finally agreed on a timeline. No celebrity takes. A practitioner, doing real work, explaining it the way you&rsquo;d explain it to a peer.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 22 }}>
                {chapters.map((c) => <span key={c.spine} className="sg-tag cat">{c.spine}</span>)}
              </div>
            </section>

            {/* CHAPTERS */}
            <section id="chapters" style={{ scrollMarginTop: 80, marginTop: 44 }}>
              <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 20, flexWrap: 'wrap' }}>
                <SectionDivider label="Chapters · the format spine, timestamped" variant="accent" style={{ flex: 1, minWidth: 300 }} />
                <span className="sg-mono" style={{ whiteSpace: 'nowrap' }}>6 · 38:00</span>
              </div>
              <div style={{ marginTop: 22, borderTop: '1px solid var(--line)' }}>
                {chapters.map((c, i) => <Chapter key={i} c={c} accent={ACCENT} n={i + 1} />)}
              </div>
            </section>

            {/* PULL QUOTE */}
            <section style={{ marginTop: 40 }}>
              <div className="sg-quote" style={{ borderLeftColor: ACCENT, background: dark ? 'var(--color-surface-low)' : '#faf0e9' }}>
                <span className="sg-quote-mark" style={{ color: ACCENT }}>&ldquo;</span>
                <p className="sg-quote-text" style={{ maxWidth: 600 }}>We didn&rsquo;t need a smarter alarm. We needed the four systems to tell one story.</p>
                <p className="sg-quote-attr">M. Okafor — Ep. 014 · 11:25</p>
              </div>
            </section>

            {/* WHAT TO COPY */}
            <section id="takeaways" style={{ scrollMarginTop: 80, marginTop: 44 }}>
              <SectionDivider label="What to copy" variant="accent" />
              <ul style={{ marginTop: 18, display: 'grid', gap: 14 }}>
                {[
                  'Reconcile timelines before you reach for a better model — alignment is the leverage.',
                  'Treat the places your systems disagree as the signal, not the noise.',
                  'Write the record so the next shift inherits the thinking, not just the answer.',
                ].map((t, i) => (
                  <li key={i} style={{ display: 'grid', gridTemplateColumns: '28px 1fr', gap: 12, alignItems: 'baseline' }}>
                    <span className="sg-display" style={{ fontSize: 22, color: ACCENT }}>{String(i + 1).padStart(2, '0')}</span>
                    <span style={{ fontSize: 16, lineHeight: 1.6, color: 'var(--text)' }}>{t}</span>
                  </li>
                ))}
              </ul>
            </section>

            {/* WHAT IT BECAME — one-to-many */}
            <section id="fanout" style={{ scrollMarginTop: 80, marginTop: 44 }}>
              <SectionDivider label="What this conversation became" />
              <p className="sg-mono" style={{ color: 'var(--text-dim)', margin: '14px 0 18px' }}>One conversation, many surfaces — each feeds the next.</p>
              <div style={{ display: 'grid', gap: 12 }}>
                {[
                  { t: 'The RCA record', d: 'Event #4471 — the reconciled timeline & evidence', href: SITE.report, tag: 'Report' },
                  { t: 'The peer-reviewed write-up', d: 'Four systems, four stories — the published article', href: SITE.article, tag: 'Article' },
                  { t: 'The weekly signal', d: 'Issue 014 — lead signal of the week', href: SITE.newsletter, tag: 'Newsletter' },
                ].map((x) => (
                  <a key={x.t} href={x.href} className="sg-card hoverable accent" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
                    <div>
                      <div className="sg-mono" style={{ color: ACCENT, marginBottom: 6 }}>{x.tag}</div>
                      <div className="sg-display" style={{ fontSize: 20 }}>{x.t}</div>
                      <p style={{ fontSize: 13.5, color: 'var(--text-dim)', marginTop: 4 }}>{x.d}</p>
                    </div>
                    <IconArrow />
                  </a>
                ))}
                <div className="sg-card" style={{ borderLeftColor: 'var(--line)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, opacity: 0.7 }}>
                  <div>
                    <div className="sg-mono" style={{ color: 'var(--text-dim)', marginBottom: 6 }}>Also generated</div>
                    <div className="sg-display" style={{ fontSize: 20 }}>The wiki entry &amp; a reusable prompt</div>
                    <p style={{ fontSize: 13.5, color: 'var(--text-dim)', marginTop: 4 }}>Published to {'{{WIKI}}'} — searchable by the next team</p>
                  </div>
                </div>
              </div>
            </section>

          </div>
        </main>
      </div>

      {/* FOOTER */}
      <footer style={{ background: 'var(--chrome-bg)', borderTop: `3px solid ${ACCENT}`, padding: '32px 48px', marginTop: 56 }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>{'{{CONFIDENTIAL_LABEL}}'} · Internal · {'{{ORG}}'} · The Show · Ep. 014</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>Propose an episode · WCAG AA</span>
        </div>
      </footer>
    </div>
  );
}

// ---- chapter row (timestamped) ----
function Chapter({ c, accent, n }) {
  const [hover, setHover] = React.useState(false);
  return (
    <a onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      style={{ display: 'grid', gridTemplateColumns: '40px 86px 1fr', gap: 18, alignItems: 'center', padding: '16px 0', borderBottom: '1px solid var(--line)', cursor: 'pointer', textDecoration: 'none', background: hover ? 'var(--color-surface-low)' : 'transparent', marginInline: hover ? -14 : 0, paddingInline: hover ? 14 : 0, transition: 'background var(--dur-base) var(--ease-out)' }}>
      <span className="sg-display" style={{ fontSize: 22, color: hover ? accent : 'var(--line)', transition: 'color var(--dur-base)' }}>{String(n).padStart(2, '0')}</span>
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: 'var(--font-mono)', fontSize: 12, color: accent, justifySelf: 'start', border: `1px solid ${hover ? accent : 'var(--line)'}`, padding: '4px 8px', transition: 'border-color var(--dur-base)' }}>{c.ts} <span style={{ opacity: 0.7 }}>↗</span></span>
      <span>
        <span className="sg-mono" style={{ color: 'var(--text-dim)', display: 'block', marginBottom: 3 }}>{c.spine}</span>
        <span className="sg-display" style={{ fontSize: 20, color: 'var(--text)' }}>{c.title}</span>
      </span>
    </a>
  );
}

window.Show = Show;
