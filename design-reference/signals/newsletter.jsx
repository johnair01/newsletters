// signals/newsletter.jsx — The Newsletter surface · weekly curated digest.
// Level-headed, no hype. Recurring spine: lead signal · from the field ·
// state of the art · risks & realities · the queue. Amber = digest signal.
// Contextual "In this issue" sidebar (scroll-tracking), not hub wayfinding.

function Newsletter() {
  const [theme, setTheme] = React.useState('light');
  const [active, setActive] = React.useState('lead');
  const [progress, setProgress] = React.useState(0);
  const dark = theme === 'dark';
  const AMBER = 'var(--color-amber)';

  const sections = [
    { id: 'lead', label: 'Lead Signal' },
    { id: 'field', label: 'From the Field' },
    { id: 'art', label: 'State of the Art' },
    { id: 'risks', label: 'Risks & Realities' },
    { id: 'queue', label: 'The Queue' },
  ];

  React.useEffect(() => {
    const ids = sections.map((s) => s.id);
    const onScroll = () => {
      let cur = ids[0];
      for (const id of ids) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top <= 130) cur = id;
      }
      setActive(cur);
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  const goto = (id) => { const el = document.getElementById(id); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 78, behavior: 'smooth' }); };

  return (
    <div className="signals article-root" data-theme={theme} style={{ minHeight: '100vh', fontFamily: 'var(--font-body)' }}>

      {/* NAV */}
      <SiteNav active="Newsletter" theme={theme} onToggle={() => setTheme(dark ? 'light' : 'dark')} accent="var(--color-amber)" />

      {/* ISSUE MASTHEAD */}
      <header style={{ maxWidth: 1180, margin: '0 auto', padding: '54px 48px 38px', borderBottom: '1px solid var(--line)' }}>
        <div className="sg-eyebrow" style={{ color: AMBER }}><span>The Newsletter — Weekly Digest</span><span className="sg-rule" style={{ maxWidth: 60, background: AMBER, opacity: 0.5 }} /></div>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 28, marginTop: 18, flexWrap: 'wrap' }}>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 88, lineHeight: 0.9, color: AMBER }}>014</div>
          <div style={{ paddingBottom: 8 }}>
            <h1 className="sg-display" style={{ fontSize: 40, lineHeight: 1.08 }}>The signal, <em>weekly.</em></h1>
            <div className="sg-mono" style={{ marginTop: 10 }}>Monday · Jun 09 · 2026 · 6-minute read</div>
          </div>
        </div>
        <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 21, lineHeight: 1.45, color: 'var(--text)', maxWidth: 760, marginTop: 26 }}>
          This week: a 47-minute stop that four systems couldn&rsquo;t agree on, two field dispatches worth copying, and one honest caveat about where this doesn&rsquo;t work yet.
        </p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 18 }}>
          <ProfileChip initials="JJ" name="JJ" role="Editor" />
          <div style={{ flex: 1 }} />
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {sections.map((s) => <span key={s.id} className="sg-tag cat" style={{ cursor: 'pointer' }} onClick={() => goto(s.id)}>{s.label}</span>)}
          </div>
        </div>
      </header>

      {/* BODY */}
      <div className="article-body" style={{ maxWidth: 1180, margin: '0 auto', padding: '0 48px' }}>

        {/* SIDEBAR — In this issue */}
        <aside className="article-aside" style={{ top: 88, paddingTop: 40 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>In this issue</span>
            <span className="sg-mono" style={{ color: AMBER, fontVariantNumeric: 'tabular-nums' }}>{Math.round(progress * 100)}%</span>
          </div>
          <div style={{ height: 2, background: 'var(--line)', marginBottom: 16, position: 'relative' }}>
            <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${progress * 100}%`, background: AMBER, transition: 'width 120ms linear' }} />
          </div>
          <ul style={{ display: 'grid', gap: 1 }}>
            {sections.map((s, i) => {
              const on = active === s.id;
              return (
                <li key={s.id}>
                  <a onClick={() => goto(s.id)} style={{ display: 'flex', gap: 10, alignItems: 'baseline', fontSize: 13, lineHeight: 1.35, padding: '7px 12px', marginLeft: -12, cursor: 'pointer', color: on ? AMBER : 'var(--text-dim)', borderLeft: on ? `2px solid ${AMBER}` : '2px solid var(--line)', background: on ? 'color-mix(in oklab, var(--color-amber) 12%, transparent)' : 'transparent', fontWeight: on ? 600 : 400, transition: 'color 150ms, background 150ms' }}>
                    <span className="sg-mono" style={{ color: on ? AMBER : 'var(--line)' }}>{String(i + 1).padStart(2, '0')}</span>{s.label}
                  </a>
                </li>
              );
            })}
          </ul>

          {/* Recent issues */}
          <div style={{ borderTop: '1px solid var(--line)', marginTop: 22, paddingTop: 18 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 12 }}>Recent issues</div>
            <ul style={{ display: 'grid', gap: 12 }}>
              {[['013', 'Templating the win'], ['012', 'When to say \u201cparked\u201d'], ['011', 'The four-source join']].map(([n, t]) => (
                <li key={n} style={{ display: 'flex', gap: 12, alignItems: 'baseline', cursor: 'pointer' }}>
                  <span className="sg-display" style={{ fontSize: 17, color: 'var(--line)' }}>{n}</span>
                  <span style={{ fontSize: 13, color: 'var(--text)' }}>{t}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Subscribe */}
          <div style={{ marginTop: 22, border: '1px solid var(--line)', borderLeft: `3px solid ${AMBER}`, padding: '18px 20px' }}>
            <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 17, lineHeight: 1.35 }}>Get it Monday morning.</p>
            <button className="sg-btn" style={{ marginTop: 14, width: '100%', justifyContent: 'center', padding: '10px', background: AMBER, borderColor: AMBER }}>Join the list</button>
          </div>
        </aside>

        {/* MAIN — single readable column */}
        <main className="article-main" style={{ paddingTop: 44, minWidth: 0 }}>
          <div style={{ maxWidth: 680 }}>

            {/* LEAD SIGNAL */}
            <section id="lead" style={{ scrollMarginTop: 80 }}>
              <NlHead n="01" label="Lead Signal" amber={AMBER} />
              <div style={{ border: '1px solid var(--line)', borderLeft: `3px solid ${AMBER}`, background: 'var(--card)', padding: '24px 26px', marginTop: 18 }}>
                <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap' }}>
                  <Tag kind="peer">Peer Reviewed</Tag>
                  <span className="sg-tag cat">Downtime RCA</span>
                  <span className="sg-tag cat">The Show · Ep. 014</span>
                </div>
                <h3 className="sg-display" style={{ fontSize: 28, lineHeight: 1.14 }}>The downtime nobody could explain — and the trail that finally did.</h3>
                <p style={{ fontSize: 15.5, lineHeight: 1.65, color: 'var(--text-dim)', marginTop: 14 }}>
                  A line went down for 47 minutes and four systems each told a different story. The team didn&rsquo;t reach for a smarter alarm — they reconciled the timelines and let the disagreements point at the cause. Time-to-cause fell from ~2 shifts to 2.5 hours, and the night shift now opens a record instead of a blank page.
                </p>
                <div style={{ display: 'flex', gap: 18, marginTop: 20, flexWrap: 'wrap' }}>
                  <a href={SITE.article} style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', textDecoration: 'none', color: AMBER, display: 'inline-flex', alignItems: 'center', gap: 7, cursor: 'pointer' }}>Read the write-up <IconArrow /></a>
                  <a href={SITE.show} style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', textDecoration: 'none', color: 'var(--text-dim)', display: 'inline-flex', alignItems: 'center', gap: 7, cursor: 'pointer' }}>Listen <IconPlay /></a>
                </div>
              </div>
            </section>

            <NlRule />

            {/* FROM THE FIELD */}
            <section id="field" style={{ scrollMarginTop: 80 }}>
              <NlHead n="02" label="From the Field" amber={AMBER} />
              <div style={{ marginTop: 8 }}>
                {[
                  { t: 'Three fragmented signals, one defect — characterized in an afternoon', b: 'A pattern that used to take a week of back-and-forth, closed in a sitting by joining inspection, process and event data into one view.', tag: 'Defect detection', status: 'Published' },
                  { t: 'Half the work content out of a frontline inspection', b: 'Not by replacing the technician — by handing them the boring 50% so judgment goes where it counts.', tag: 'Technician scaling', status: 'In Review' },
                ].map((a, i) => (
                  <div key={i} style={{ padding: '18px 0', borderTop: '1px solid var(--line)' }}>
                    <h4 className="sg-display" style={{ fontSize: 20, lineHeight: 1.2 }}>{a.t}</h4>
                    <p style={{ fontSize: 14.5, lineHeight: 1.6, color: 'var(--text-dim)', marginTop: 9 }}>{a.b}</p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 12 }}>
                      <span className="sg-mono">{a.tag}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', color: a.status === 'Published' ? 'var(--color-brand-primary)' : 'var(--color-amber)' }}>{a.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <NlRule />

            {/* STATE OF THE ART */}
            <section id="art" style={{ scrollMarginTop: 80 }}>
              <NlHead n="03" label="State of the Art" amber={AMBER} />
              <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--text)', marginTop: 14 }}>
                The week&rsquo;s through-line: <strong>reconciled timelines beat smarter alarms.</strong> Across two cases, the leverage came from making sources agree on a clock — not from a new model. It&rsquo;s a quieter idea than most AI headlines, and it keeps working.
              </p>
              <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--text)', marginTop: 14 }}>
                Also worth your time: a clean argument for the <em>one-to-many</em> content engine — one conversation generating the recording, the digest, the article, the wiki entry, and a reusable prompt. Design every surface to feed the next.
              </p>
            </section>

            <NlRule />

            {/* RISKS & REALITIES */}
            <section id="risks" style={{ scrollMarginTop: 80 }}>
              <NlHead n="04" label="Risks & Realities" amber={AMBER} />
              <div style={{ border: '1px solid var(--line)', borderLeft: '3px solid var(--color-accent)', background: dark ? 'var(--color-surface-low)' : '#faf0e9', padding: '20px 24px', marginTop: 16 }}>
                <ul style={{ display: 'grid', gap: 14 }}>
                  {[
                    ['Where it doesn\u2019t work yet', 'Events with no shared key across systems still need a human to seed the join. The method assumes you can align — when you can\u2019t, it stalls.'],
                    ['Rigor isn\u2019t free', 'Tracing every claim costs time up front. We think it\u2019s the cheapest part of adoption — but it is not zero, and pretending otherwise erodes trust.'],
                  ].map(([h, b]) => (
                    <li key={h}>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10.5, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--color-accent)', marginBottom: 5 }}>{h}</div>
                      <p style={{ fontSize: 14.5, lineHeight: 1.6, color: 'var(--text)' }}>{b}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            <NlRule />

            {/* THE QUEUE */}
            <section id="queue" style={{ scrollMarginTop: 80 }}>
              <NlHead n="05" label="The Queue" amber={AMBER} />
              <ul style={{ marginTop: 14, display: 'grid', gap: 14 }}>
                {[['Next', 'Defect tooling — the practitioner-facing instrument layer'], ['Parked', 'A general assurance / verification layer — needs confirmation'], ['Drafting', 'Work-content reduction, as the umbrella frame']].map(([k, v]) => (
                  <li key={v} style={{ display: 'grid', gridTemplateColumns: '78px 1fr', gap: 14, alignItems: 'baseline', paddingBottom: 14, borderBottom: '1px solid var(--line)' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>{k}</span>
                    <span style={{ fontSize: 15, lineHeight: 1.5, color: 'var(--text)' }}>{v}</span>
                  </li>
                ))}
              </ul>
              <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 18, color: 'var(--text-dim)', marginTop: 24 }}>That&rsquo;s the week. Reply if something here is useful — or if it isn&rsquo;t. — JJ</p>
            </section>

          </div>
        </main>
      </div>

      {/* FOOTER */}
      <footer style={{ background: 'var(--chrome-bg)', borderTop: `3px solid ${AMBER}`, padding: '32px 48px', marginTop: 56 }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>{'{{CONFIDENTIAL_LABEL}}'} · Internal · {'{{ORG}}'} · Issue No. 014</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>Unsubscribe · Manage preferences · WCAG AA</span>
        </div>
      </footer>
    </div>
  );
}

function NlHead({ n, label, amber }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
      <span className="sg-display" style={{ fontSize: 24, color: amber }}>{n}</span>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--text)' }}>{label}</span>
      <span className="sg-rule" />
    </div>
  );
}
function NlRule() { return <div style={{ height: 40 }} />; }

window.Newsletter = Newsletter;
