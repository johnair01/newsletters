// signals/proposal.jsx — "Start here" · the proposal / charter surface.
// The operating model the user confirmed, built as a SLOT-MARKED TEMPLATE:
// org/area/system/metric/meeting/person specifics live in {{SLOTS}} so it can
// be repopulated with real internal data. Owns light/dark.

function Proposal() {
  const [theme, setTheme] = React.useState('light');
  const [active, setActive] = React.useState('vision');
  const dark = theme === 'dark';

  const sections = [
    { id: 'vision', label: 'What this is' },
    { id: 'rhythm', label: 'The operating rhythm' },
    { id: 'workstreams', label: 'The workstreams' },
    { id: 'partnership', label: 'Ownership & partnership' },
    { id: 'engine', label: 'How it publishes' },
    { id: 'ask', label: 'The invitation' },
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

  // operating rhythm — daily → Wednesday → weekly → bi-weekly
  const rhythm = [
    { cad: 'Daily', name: '{{DAILY_WG}}', what: 'Defects & tool faults working group with the {{INTERNS}}.', out: 'Generates a record every day' },
    { cad: 'Wednesday', name: '{{TASK_FORCE}}', what: 'Tool faults / E3s, fed by the daily records.', out: 'Carries the area story up' },
    { cad: 'Weekly', name: '{{TEAM_WEEKLY}}', what: 'Review of the two key issues + my swim-lane updates.', out: 'The weekly signal' },
    { cad: 'Bi-weekly', name: '{{INTERN_REVIEW}}', what: 'Intern swim-lane review — surfacing problems across the board.', out: 'New cases enter the queue' },
  ];

  return (
    <div className="signals article-root" data-theme={theme} style={{ minHeight: '100vh', fontFamily: 'var(--font-body)' }}>

      <SiteNav active="Start here" theme={theme} onToggle={() => setTheme(dark ? 'light' : 'dark')} />

      {/* HERO */}
      <header style={{ maxWidth: 1180, margin: '0 auto', padding: '60px 48px 44px', borderBottom: '1px solid var(--line)' }}>
        <Eyebrow withRule>Engineering Coherence &amp; AI Practice — {'{{AREA}}'}</Eyebrow>
        <h1 className="sg-display" style={{ fontSize: 60, lineHeight: 1.08, maxWidth: 940, marginTop: 22 }}>
          A working surface for how we <em>find, solve, and share</em> — coherently.
        </h1>
        <p style={{ fontSize: 17.5, lineHeight: 1.6, color: 'var(--text-dim)', maxWidth: 640, marginTop: 22 }}>
          We run our defect and tool-fault work in the open, publish what we learn as we learn it, and let the tooling we build mature into the enterprise system. This is the infrastructure that makes that legible — to our team, to leadership, and to the partners we build with.
        </p>
        <div style={{ display: 'flex', gap: 14, marginTop: 32, flexWrap: 'wrap' }}>
          <a href={SITE.report} className="sg-btn" style={{ textDecoration: 'none' }}>See a live record <IconArrow /></a>
          <a href="#ask" className="sg-btn ghost" style={{ textDecoration: 'none' }}>How to take part</a>
        </div>
        <p className="sg-mono" style={{ color: 'var(--text-dim)', marginTop: 24 }}>Template · {'{{ORG}}'} · {'{{AREA}}'} — repopulate the {'{{SLOTS}}'} with your specifics</p>
      </header>

      {/* BODY */}
      <div className="article-body" style={{ maxWidth: 1180, margin: '0 auto', padding: '0 48px' }}>

        {/* SIDEBAR */}
        <aside className="article-aside" style={{ top: 88, paddingTop: 40 }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 14 }}>On this page</div>
          <ul style={{ display: 'grid', gap: 1 }}>
            {sections.map((s) => {
              const on = active === s.id;
              return (
                <li key={s.id}>
                  <a onClick={() => goto(s.id)} style={{ display: 'block', fontSize: 13, padding: '7px 12px', marginLeft: -12, cursor: 'pointer', color: on ? 'var(--color-brand-primary)' : 'var(--text-dim)', borderLeft: on ? '2px solid var(--color-brand-primary)' : '2px solid var(--line)', background: on ? 'var(--color-brand-light)' : 'transparent', fontWeight: on ? 600 : 400, transition: 'color 150ms, background 150ms' }}>{s.label}</a>
                </li>
              );
            })}
          </ul>
          <div style={{ marginTop: 24, border: '1px solid var(--line)', borderLeft: '3px solid var(--color-brand-primary)', padding: '18px 20px' }}>
            <div className="sg-mono" style={{ color: 'var(--text-dim)', marginBottom: 10 }}>The surfaces</div>
            <ul style={{ display: 'grid', gap: 9 }}>
              {[['The Show', SITE.show], ['The Newsletter', SITE.newsletter], ['The Articles', SITE.article], ['The Report', SITE.report]].map(([t, h]) => (
                <li key={t}><a href={h} style={{ fontSize: 13, color: 'var(--text)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 7 }}>{t} <IconArrow size={11} /></a></li>
              ))}
            </ul>
          </div>
        </aside>

        {/* MAIN */}
        <main className="article-main" style={{ paddingTop: 44, minWidth: 0 }}>
          <div style={{ maxWidth: 740 }}>

            {/* VISION */}
            <section id="vision" style={{ scrollMarginTop: 80 }}>
              <SectionDivider label="What this is" />
              <p style={{ fontSize: 17, lineHeight: 1.72, color: 'var(--text)', marginTop: 18 }}>
                <strong>Signals</strong> is the publishing and cultural layer for how engineering work gets done in {'{{AREA}}'}. The north star is plain: make it easier to find problems, reason through them, and solve them — collaboratively, quickly, and in the most energizing way. The tools are the instrument; better operation is the outcome.
              </p>
              <p style={{ fontSize: 17, lineHeight: 1.72, color: 'var(--text)', marginTop: 16 }}>
                It is one system of surfaces — a daily working group that generates records, a weekly signal, peer-reviewed write-ups, and recorded conversations — all tracing back to the real cases we&rsquo;re working: <strong>defect detection</strong> and <strong>tool-fault reduction</strong>.
              </p>
            </section>

            <SecRule />

            {/* RHYTHM */}
            <section id="rhythm" style={{ scrollMarginTop: 80 }}>
              <SectionDivider label="The operating rhythm" variant="accent" />
              <p style={{ fontSize: 15.5, lineHeight: 1.6, color: 'var(--text-dim)', margin: '14px 0 22px', maxWidth: 640 }}>
                A cadence that feeds itself: the daily record rolls up into Wednesday&rsquo;s task force and the weekly signal, while the bi-weekly intern review keeps new problems entering the queue.
              </p>
              <div style={{ borderTop: '1px solid var(--line)' }}>
                {rhythm.map((r, i) => (
                  <div key={i} style={{ display: 'grid', gridTemplateColumns: '120px 1fr 200px', gap: 20, alignItems: 'baseline', padding: '20px 0', borderBottom: '1px solid var(--line)' }} className="prop-rhythm">
                    <div>
                      <div className="sg-mono" style={{ color: 'var(--color-accent)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>{r.cad}</div>
                    </div>
                    <div>
                      <div className="sg-display" style={{ fontSize: 21 }}>{r.name}</div>
                      <p style={{ fontSize: 14, lineHeight: 1.55, color: 'var(--text-dim)', marginTop: 6 }}>{r.what}</p>
                    </div>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ color: 'var(--color-brand-primary)' }}><IconArrow /></span>
                      <span style={{ fontSize: 13, color: 'var(--text)', fontWeight: 500 }}>{r.out}</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <SecRule />

            {/* WORKSTREAMS */}
            <section id="workstreams" style={{ scrollMarginTop: 80 }}>
              <SectionDivider label="The workstreams" />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 20 }} className="prop-2col">
                {[
                  { t: 'Defect detection', d: 'Surfacing and characterizing defects faster across fragmented signals — {{DEFECT_SYSTEM}}, {{SPC_SYSTEM}} and the floor.', tag: 'Daily · with {{INTERNS}}' },
                  { t: 'Tool-fault reduction', d: 'Driving down tool faults / E3s — the instrument layer around detection and disposition, feeding {{TASK_FORCE}}.', tag: 'Daily → Wednesday' },
                ].map((w) => (
                  <div key={w.t} className="sg-card" style={{ borderLeftColor: 'var(--color-brand-primary)' }}>
                    <div className="sg-display" style={{ fontSize: 23 }}>{w.t}</div>
                    <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-dim)', marginTop: 10 }}>{w.d}</p>
                    <div className="sg-mono" style={{ color: 'var(--color-brand-primary)', marginTop: 14 }}>{w.tag}</div>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 16, border: '1px solid var(--line)', borderLeft: '3px solid var(--color-ink)', padding: '18px 22px', background: 'var(--color-surface-low)' }}>
                <span className="sg-mono" style={{ color: 'var(--text-dim)' }}>The area story</span>
                <p style={{ fontSize: 15, lineHeight: 1.6, color: 'var(--text)', marginTop: 8 }}>Above the two streams, the weekly builds the <strong>{'{{MA_SYSTEM}}'} / overall-manufacturing story for {'{{AREA}}'}</strong> — telling what&rsquo;s going on and where the constraint is.</p>
              </div>
            </section>

            <SecRule />

            {/* PARTNERSHIP */}
            <section id="partnership" style={{ scrollMarginTop: 80 }}>
              <SectionDivider label="Ownership & partnership" variant="accent" />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 20 }} className="prop-2col">
                <div className="sg-card" style={{ borderLeftColor: 'var(--color-accent)' }}>
                  <div className="sg-display" style={{ fontSize: 21, fontStyle: 'italic' }}>We own our area</div>
                  <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-dim)', marginTop: 10 }}>We discover the tooling and the ways of working that solve <em>our</em> problems, in a form we can see and use day to day.</p>
                </div>
                <div className="sg-card" style={{ borderLeftColor: 'var(--color-brand-primary)' }}>
                  <div className="sg-display" style={{ fontSize: 21, fontStyle: 'italic' }}>We partner with enterprise</div>
                  <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-dim)', marginTop: 10 }}>We build alongside {'{{ENTERPRISE_TEAM}}'} and the {'{{ENTERPRISE_AI_SUITE}}'} — not in a silo, not waiting on a roadmap.</p>
                </div>
              </div>
              {/* promotion path */}
              <div style={{ marginTop: 20, border: '1px solid var(--line)', padding: '24px 26px' }}>
                <div className="sg-mono" style={{ color: 'var(--text-dim)', marginBottom: 18 }}>The promotion path</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 28px 1fr 28px 1fr', gap: 10, alignItems: 'center' }} className="prop-promote">
                  {[['Discover locally', 'A fix that works on our floor, in our records.'], ['Proven', 'It holds across cases and shifts — evidence-backed.'], ['Promoted to {{ENTERPRISE_AI_SUITE}}', 'What matters broadly graduates to the enterprise system.']].map((p, i) => (
                    <React.Fragment key={i}>
                      {i > 0 && <span style={{ textAlign: 'center', color: 'var(--color-brand-primary)' }}><IconArrow /></span>}
                      <div style={{ borderLeft: `3px solid ${i === 2 ? 'var(--color-brand-primary)' : 'var(--color-rule)'}`, paddingLeft: 14 }}>
                        <div className="sg-display" style={{ fontSize: 17, lineHeight: 1.15 }}>{p[0]}</div>
                        <p style={{ fontSize: 12.5, lineHeight: 1.45, color: 'var(--text-dim)', marginTop: 6 }}>{p[1]}</p>
                      </div>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            </section>

            <SecRule />

            {/* ENGINE */}
            <section id="engine" style={{ scrollMarginTop: 80 }}>
              <SectionDivider label="How it publishes" />
              <p style={{ fontSize: 15.5, lineHeight: 1.6, color: 'var(--text-dim)', margin: '14px 0 18px', maxWidth: 640 }}>
                One conversation or workflow, many surfaces — each feeds the next. The daily working group&rsquo;s records become the Report, the Article, the weekly Newsletter, and an episode of The Show.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                {[['Daily record', SITE.report], ['→', null], ['Article', SITE.article], ['→', null], ['Weekly signal', SITE.newsletter], ['→', null], ['The Show', SITE.show]].map(([t, h], i) => (
                  t === '→'
                    ? <span key={i} className="sg-mono" style={{ color: 'var(--text-dim)' }}>→</span>
                    : <a key={i} href={h} className="sg-tag cat" style={{ textDecoration: 'none', padding: '8px 12px', fontSize: 11 }}>{t}</a>
                ))}
              </div>
            </section>

            <SecRule />

            {/* ASK */}
            <section id="ask" style={{ scrollMarginTop: 80 }}>
              <SectionDivider label="The invitation" variant="accent" />
              <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 22, lineHeight: 1.4, color: 'var(--text)', margin: '16px 0 24px', maxWidth: 660 }}>
                This works by invitation, not mandate. Here&rsquo;s what we&rsquo;re asking of each of you.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }} className="prop-3col">
                {[
                  { who: 'Leadership', ask: 'Sponsor the cadence', d: 'Back the daily working group and the weekly as the way {{AREA}} tells its story.' },
                  { who: '{{ENTERPRISE_TEAM}}', ask: 'Partner with us', d: 'Build alongside us; take what matures into {{ENTERPRISE_AI_SUITE}}.' },
                  { who: 'Peers in other areas', ask: 'Adopt the template', d: 'Run the same Case Spec on your floor — the method travels.' },
                ].map((a) => (
                  <div key={a.who} className="sg-card hoverable" style={{ borderLeftColor: 'var(--color-accent)', display: 'flex', flexDirection: 'column' }}>
                    <div className="sg-mono" style={{ color: 'var(--text-dim)', marginBottom: 10 }}>{a.who}</div>
                    <div className="sg-display" style={{ fontSize: 21 }}>{a.ask}</div>
                    <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--text-dim)', marginTop: 10, flex: 1 }}>{a.d}</p>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 24, display: 'flex', gap: 14, flexWrap: 'wrap' }}>
                <a href={SITE.hub} className="sg-btn" style={{ textDecoration: 'none' }}>Explore the system <IconArrow /></a>
                <a href={SITE.report} className="sg-btn ghost" style={{ textDecoration: 'none' }}>See a live record</a>
              </div>
            </section>

          </div>
        </main>
      </div>

      {/* FOOTER */}
      <footer style={{ background: 'var(--chrome-bg)', borderTop: '3px solid var(--color-brand-primary)', padding: '32px 48px', marginTop: 56 }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>{'{{CONFIDENTIAL_LABEL}}'} · Internal · {'{{ORG}}'} · {'{{AREA}}'}</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>Proposal template · repopulate per handoff/REPOPULATE.md</span>
        </div>
      </footer>
    </div>
  );
}

function SecRule() { return <div style={{ margin: '40px 0' }}><SectionDivider label="§" centered /></div>; }

window.Proposal = Proposal;
