// signals/report.jsx — Flagship Report view · the RCA output surface.
// Header + status gate (human-in-the-loop, advanceable) → KPI strip →
// narrative (centered dividers, narrow prose) → collapsible evidence table →
// action items → forward preview. Print-optimized. Owns light/dark.

function Report() {
  const [theme, setTheme] = React.useState('light');
  const dark = theme === 'dark';
  const stages = ['Draft', 'In Review', 'Published'];
  const [stage, setStage] = React.useState('In Review');
  const [open, setOpen] = React.useState({ wo: true, ma: false, spc: true, def: false });
  const toggle = (k) => setOpen((o) => ({ ...o, [k]: !o[k] }));

  const evidence = [
    { k: 'wo', sys: '{{WORK_ORDER_SYSTEM}}', name: 'Event log', summary: 'Stop raised 02:30, restart 03:17', rows: [
      ['02:30:04', 'Stop event', 'E-4471', 'Operator-acknowledged, guard zone 4'],
      ['03:17:22', 'Restart', 'OK', 'Manual restart after interlock reset'],
    ] },
    { k: 'ma', sys: '{{MA_SYSTEM}}', name: 'Availability', summary: '47 min unplanned, line 4', rows: [
      ['02:30–03:17', 'Downtime', '47 min', 'Classified unplanned'],
      ['Shift', 'Availability', '96.4%', '+1.2 pt vs prior shift'],
    ] },
    { k: 'spc', sys: '{{SPC_SYSTEM}}', name: 'Process drift', summary: 'Sensor 4B drift starting 02:28:34', rows: [
      ['02:28:34', 'Drift onset', '+2.1\u03c3', 'Conveyor tension, sensor 4B'],
      ['02:29:50', 'Threshold', 'Breach', '90s before the stop'],
    ] },
    { k: 'def', sys: '{{DEFECT_SYSTEM}}', name: 'Inspection', summary: 'No defects attributable to event', rows: [
      ['Lot 22-118', 'Inspection', 'Pass', 'No correlation to the stop'],
    ] },
  ];

  return (
    <div className="signals article-root" data-theme={theme} style={{ minHeight: '100vh', fontFamily: 'var(--font-body)' }}>

      {/* NAV */}
      <SiteNav theme={theme} onToggle={() => setTheme(dark ? 'light' : 'dark')} tagline="· report"
        action={<button className="sg-btn ghost" style={{ padding: '9px 16px', color: '#fff', borderColor: 'rgba(255,255,255,0.3)' }} onClick={() => window.print()}>Print / Export</button>} />

      {/* REPORT HEADER */}
      <header style={{ maxWidth: 1180, margin: '0 auto', padding: '48px 48px 32px', borderBottom: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 20, flexWrap: 'wrap' }}>
          <Eyebrow variant="brand">Root-Cause Analysis · Report</Eyebrow>
          <Tag kind="live">Live record</Tag>
        </div>
        <h1 className="sg-display" style={{ fontSize: 46, lineHeight: 1.08, maxWidth: 860, marginTop: 16 }}>
          Event #4471 — Line 4, a <em>47-minute</em> stop, reconstructed.
        </h1>
        <p style={{ fontSize: 16.5, lineHeight: 1.6, color: 'var(--text-dim)', maxWidth: 680, marginTop: 16 }}>
          Evidence from four systems, reconciled to one timeline. A guard interlock — not a mechanical fault — began the stop. This record is the reusable output: the next event drops into the same shape.
        </p>
      </header>

      {/* BODY: meta rail + document */}
      <div className="article-body" style={{ maxWidth: 1180, margin: '0 auto', padding: '0 48px' }}>

        {/* META RAIL */}
        <aside className="article-aside" style={{ top: 88, paddingTop: 36 }}>
          {/* status gate — human-in-the-loop */}
          <div style={{ border: '1px solid var(--line)', borderLeft: '3px solid var(--color-amber)', padding: '18px 20px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 14 }}>Publish gate</div>
            <div style={{ display: 'grid', gap: 8 }}>
              {stages.map((s, i) => {
                const ci = stages.indexOf(stage);
                const done = i < ci, cur = i === ci;
                const tone = s === 'Published' ? 'var(--color-brand-primary)' : s === 'In Review' ? 'var(--color-amber)' : 'var(--text-dim)';
                return (
                  <div key={s} style={{ display: 'flex', alignItems: 'center', gap: 10, opacity: done || cur ? 1 : 0.4 }}>
                    <span style={{ width: 14, height: 14, borderRadius: '50%', border: `2px solid ${done || cur ? tone : 'var(--line)'}`, background: done ? tone : 'transparent', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto' }}>
                      {done && <IconCheck size={8} />}
                    </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.08em', textTransform: 'uppercase', color: cur ? tone : 'var(--text)', fontWeight: cur ? 600 : 400 }}>{s}</span>
                    {cur && s !== 'Published' && <span className="sg-dot" style={{ marginLeft: 'auto', background: tone }} />}
                  </div>
                );
              })}
            </div>
            {stage !== 'Published' ? (
              <button className="sg-btn" style={{ marginTop: 16, width: '100%', justifyContent: 'center', padding: '9px' }}
                onClick={() => setStage(stages[stages.indexOf(stage) + 1])}>
                {stage === 'Draft' ? 'Send to review' : 'Approve & publish'}
              </button>
            ) : (
              <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 8, fontFamily: 'var(--font-mono)', fontSize: 10.5, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--color-green)' }}>
                <IconCheck size={11} /> Published to {'{{LEARNING_PLATFORM}}'}
              </div>
            )}
          </div>

          {/* meta */}
          <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', rowGap: 11, columnGap: 14, margin: '22px 0 0' }}>
            {[['Report', 'RCA-4471'], ['Window', '02:30–03:17'], ['Owner', 'Reliability Eng.'], ['Confidence', 'High'], ['Generated', 'Jun 09 · 03:48']].map(([k, v]) => (
              <React.Fragment key={k}>
                <dt className="sg-mono" style={{ color: 'var(--text-dim)' }}>{k}</dt>
                <dd style={{ margin: 0, fontSize: 13, color: 'var(--text)', fontWeight: 500 }}>{v}</dd>
              </React.Fragment>
            ))}
          </dl>

          {/* sources */}
          <div style={{ borderTop: '1px solid var(--line)', marginTop: 20, paddingTop: 16 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 12 }}>Sources joined · 4</div>
            <ul style={{ display: 'grid', gap: 8 }}>
              {['{{MA_SYSTEM}}', '{{SPC_SYSTEM}}', '{{DEFECT_SYSTEM}}', '{{WORK_ORDER_SYSTEM}}'].map((s) => (
                <li key={s} className="sg-mono" style={{ color: 'var(--color-brand-primary)', paddingLeft: 12, borderLeft: '2px solid var(--line)' }}>{s}</li>
              ))}
            </ul>
          </div>
        </aside>

        {/* DOCUMENT */}
        <main className="article-main" style={{ paddingTop: 40, minWidth: 0 }}>

          {/* KPI strip */}
          <KpiBlock items={[
            { label: 'Downtime', value: '47m', delta: 'vs 90m median', dir: 'up' },
            { label: 'Time to cause', value: '2.5h', delta: 'was ~2 shifts', dir: 'up' },
            { label: 'Availability', value: '96.4%', delta: '+1.2 pt', dir: 'up' },
            { label: 'Sources', value: '4', delta: 'one timeline', dir: '' },
          ]} />

          <article style={{ maxWidth: 720, marginTop: 8 }}>
            {/* narrative */}
            <div style={{ marginTop: 36 }}><SectionDivider label="Summary" centered /></div>
            <RP>At 02:30, line 4 stopped for 47 minutes. The four systems that recorded the event each described it differently. Reconciled to a single timeline, the sequence is unambiguous: a process drift on sensor 4B breached threshold at 02:29:50, and a guard interlock tripped 14 seconds later. The stop was procedural, not mechanical.</RP>

            <div style={{ marginTop: 32 }}><SectionDivider label="Root cause" centered /></div>
            <RP><strong>A guard interlock in zone 4 tripped on a conveyor-tension drift, not a mechanical fault.</strong> The drift was visible in {'{{SPC_SYSTEM}}'} 90 seconds before the stop; no defect was attributable to the event. The 47 minutes were spent diagnosing in the dark — exactly the work content this record removes for the next shift.</RP>

            <div style={{ marginTop: 32 }}><SectionDivider label="Reconciled evidence" centered /></div>
            <p className="sg-mono" style={{ color: 'var(--text-dim)', margin: '14px 0 16px' }}>Click a source to expand its rows. Every claim above traces here.</p>

            {/* COLLAPSIBLE EVIDENCE TABLE */}
            <div style={{ border: '1px solid var(--line)' }}>
              {evidence.map((g, gi) => (
                <div key={g.k} style={{ borderTop: gi ? '1px solid var(--line)' : 0 }}>
                  <button onClick={() => toggle(g.k)} className="report-row"
                    style={{ width: '100%', textAlign: 'left', background: 'transparent', cursor: 'pointer', border: 0, padding: '14px 18px', borderLeft: '3px solid var(--color-brand-primary)', display: 'grid', gridTemplateColumns: '18px 1fr auto', gap: 14, alignItems: 'center' }}>
                    <span style={{ transition: 'transform 180ms', transform: open[g.k] ? 'rotate(90deg)' : 'none', color: 'var(--text-dim)', display: 'inline-flex' }}>
                      <svg width="9" height="11" viewBox="0 0 9 11" fill="currentColor"><path d="M0 0l9 5.5L0 11z" /></svg>
                    </span>
                    <span style={{ minWidth: 0 }}>
                      <span className="sg-mono" style={{ color: 'var(--color-brand-primary)' }}>{g.sys}</span>
                      <span style={{ display: 'block', fontSize: 13.5, color: 'var(--text-dim)', marginTop: 3 }}>{g.summary}</span>
                    </span>
                    <span className="sg-mono" style={{ color: 'var(--text-dim)', whiteSpace: 'nowrap' }}>{g.name} · {g.rows.length}</span>
                  </button>
                  {open[g.k] && (
                    <div style={{ background: 'var(--color-surface-low)', padding: '4px 18px 12px' }}>
                      {g.rows.map((r, ri) => (
                        <div key={ri} className="report-detail" style={{ display: 'grid', gridTemplateColumns: '120px 110px 90px 1fr', gap: 14, padding: '9px 0', borderTop: ri ? '1px solid var(--line)' : 0, alignItems: 'baseline' }}>
                          <span className="sg-mono" style={{ color: 'var(--text)' }}>{r[0]}</span>
                          <span style={{ fontSize: 13, fontWeight: 500 }}>{r[1]}</span>
                          <span className="sg-mono" style={{ color: 'var(--color-brand-primary)' }}>{r[2]}</span>
                          <span style={{ fontSize: 13, color: 'var(--text-dim)', lineHeight: 1.45 }}>{r[3]}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* action items */}
            <div style={{ marginTop: 40 }}>
              <SectionDivider label="Action Items" />
              <div style={{ marginTop: 18, border: '1px solid var(--line)' }}>
                {[['Add guard-interlock check to startup sequence', 'M. Okafor', 'Fri', 'Open'], ['Backfill the sensor gap on conveyor 4B', 'Reliability', 'Next wk', 'Open'], ['Template this RCA for the night shift', 'JJ', 'Done', 'Closed']].map((r, i) => (
                  <div key={i} className="article-action" style={{ padding: '13px 18px', borderTop: i ? '1px solid var(--line)' : 0, background: i % 2 ? 'var(--color-surface-low)' : 'transparent' }}>
                    <span style={{ fontSize: 14, color: 'var(--text)' }}>{r[0]}</span>
                    <span className="sg-mono">{r[1]}</span>
                    <span className="sg-mono">{r[2]}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase', color: r[3] === 'Closed' ? 'var(--color-green)' : 'var(--color-amber)' }}>{r[3]}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* forward preview */}
            <div style={{ marginTop: 36, border: '1px solid var(--line)', borderLeft: '3px solid var(--color-accent)', padding: '22px 26px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 20, flexWrap: 'wrap' }}>
              <div>
                <div className="sg-mono" style={{ color: 'var(--text-dim)', marginBottom: 8 }}>This record feeds</div>
                <p className="sg-display" style={{ fontSize: 21, fontStyle: 'italic' }}>The published write-up &amp; the weekly signal</p>
              </div>
              <a href={SITE.article} className="sg-btn ghost" style={{ textDecoration: 'none' }}>Open the article <IconArrow /></a>
            </div>
          </article>
        </main>
      </div>

      {/* FOOTER */}
      <footer style={{ background: 'var(--chrome-bg)', borderTop: '3px solid var(--color-brand-primary)', padding: '32px 48px', marginTop: 56 }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>{'{{CONFIDENTIAL_LABEL}}'} · Internal · {'{{ORG}}'} · RCA-4471</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>Human-validated · Print-ready · WCAG AA</span>
        </div>
      </footer>
    </div>
  );
}

// report prose — slightly larger, document-grade
function RP({ children }) {
  return <p style={{ fontSize: 16.5, lineHeight: 1.72, color: 'var(--text)', margin: '14px 0 0', maxWidth: 700 }}>{children}</p>;
}

window.Report = Report;
