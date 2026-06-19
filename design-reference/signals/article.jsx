// signals/article.jsx — The Articles surface · peer-reviewed practitioner write-up.
// One component, parametrized sidebar: nav="toc" (scroll-tracking on-page
// contents) | nav="sections" (hub-style wayfinding). frozen=true freezes the
// TOC active state (for the static side-by-side canvas) and skips the scroll
// listener. Owns light/dark state.

function Article({ nav = 'toc', frozen = false, frozenActive = 'method' }) {
  const [theme, setTheme] = React.useState('light');
  const [active, setActive] = React.useState(frozen ? frozenActive : 'problem');
  const [progress, setProgress] = React.useState(frozen ? 0.42 : 0);
  const dark = theme === 'dark';

  const sections = [
    { id: 'problem', toc: 'The problem' },
    { id: 'current', toc: 'Current state' },
    { id: 'method', toc: 'What we did' },
    { id: 'rigor', toc: 'How rigor was held' },
    { id: 'record', toc: 'The reusable record' },
    { id: 'results', toc: 'What changed' },
    { id: 'reasoning', toc: 'In JJ\u2019s words' },
  ];

  React.useEffect(() => {
    if (frozen || nav !== 'toc') return;
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
  }, [nav, frozen]);

  const goto = (id) => {
    const el = document.getElementById(id);
    if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 78, behavior: 'smooth' });
  };

  return (
    <div className="signals article-root" data-theme={theme} style={{ minHeight: '100vh', fontFamily: 'var(--font-body)' }}>

      {/* NAV */}
      <SiteNav active="Articles" theme={theme} onToggle={() => setTheme(dark ? 'light' : 'dark')} />

      {/* ARTICLE HEADER */}
      <header style={{ maxWidth: 1180, margin: '0 auto', padding: '56px 48px 40px', borderBottom: '1px solid var(--line)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
          <Eyebrow variant="brand">Article · Downtime Root-Cause Analysis</Eyebrow>
          <a href={SITE.report} style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', textDecoration: 'none', color: 'var(--text-dim)', display: 'inline-flex', alignItems: 'center', gap: 6 }}>From record RCA-4471 <IconArrow size={11} /></a>
        </div>
        <h1 className="sg-display" style={{ fontSize: 54, lineHeight: 1.08, maxWidth: 900, marginTop: 20 }}>
          Four systems, four stories — <em>and the reconciled timeline that found the cause.</em>
        </h1>
        <p style={{ fontSize: 18, lineHeight: 1.6, color: 'var(--text-dim)', maxWidth: 700, marginTop: 22 }}>
          A 47-minute line stop, reconstructed from fragmented evidence into a single hypothesis, a narrative, and a record the next shift can reuse. The pattern travels; the data stays in config.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', gap: 24, marginTop: 30, flexWrap: 'wrap' }}>
          <ProfileChip initials="JJ" name="JJ" role="Practitioner-in-residence · author" size={38} />
          <div style={{ width: 1, height: 30, background: 'var(--line)' }} />
          <div>
            <div className="sg-mono" style={{ color: 'var(--text-dim)' }}>Reviewed by</div>
            <div style={{ fontSize: 13, fontWeight: 500, marginTop: 3 }}>Reliability Eng. + Process domain</div>
          </div>
          <div style={{ flex: 1 }} />
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <Tag kind="peer">Peer Reviewed</Tag>
            <Tag kind="published">Published</Tag>
            <span className="sg-mono">14 min</span>
            <span className="sg-mono">Jun 09 · 2026</span>
          </div>
        </div>
      </header>

      {/* BODY */}
      <div className="article-body" style={{ maxWidth: 1180, margin: '0 auto', padding: '0 48px' }}>

        {/* SIDEBAR */}
        <aside className="article-aside" style={{ top: 88, paddingTop: 40 }}>
          {nav === 'toc' ? (
            <TocSidebar sections={sections} active={active} progress={progress} onGoto={goto} />
          ) : (
            <SectionsSidebar active="downtime" />
          )}

          {/* shared: review meta */}
          <div style={{ marginTop: 26, border: '1px solid var(--line)', borderLeft: '3px solid var(--color-ink)', padding: '18px 20px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 12 }}>Peer Review</div>
            <ul style={{ display: 'grid', gap: 11 }}>
              {[['Practitioner', 'JJ', true], ['Domain review', 'Process Eng.', true], ['Claims traced', '6 / 6', true], ['Human-validated', 'Yes', true]].map(([k, v]) => (
                <li key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
                  <span className="sg-mono" style={{ color: 'var(--text-dim)' }}>{k}</span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 12.5, fontWeight: 500, color: 'var(--color-green)' }}><IconCheck size={11} />{v}</span>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* PROSE */}
        <main className="article-main" style={{ paddingTop: 44, minWidth: 0 }}>
          <article style={{ maxWidth: 720 }}>

            <Sec id="problem" eyebrow="01 · The problem">
              <P>The cost of a line stop is rarely the stop itself. It is the hours afterward — engineers and technicians cross-referencing four systems that each describe the same 47 minutes differently, trying to assemble a story credible enough to act on. That reconciliation <em>is</em> the work content. It is slow, it is repeated every event, and almost none of it is captured for the next person.</P>
              <P>This write-up follows one event end to end and extracts the pattern: how fragmented evidence becomes a single, reusable record — and why the method matters more than any one fix.</P>
            </Sec>

            <Divider />

            <Sec id="current" eyebrow="02 · Current state">
              <P>The evidence lived in four places, owned by no one in combination:</P>
              <ul className="article-list">
                {[['{{MA_SYSTEM}}', 'availability and uptime — when the line was down, by the minute'], ['{{SPC_SYSTEM}}', 'process control — the signals drifting before the stop'], ['{{DEFECT_SYSTEM}}', 'inspection and defect data — what the parts looked like'], ['{{WORK_ORDER_SYSTEM}}', 'the event and work-order log — what people did, and when']].map(([k, v]) => (
                  <li key={k}><span className="sg-mono" style={{ color: 'var(--color-brand-primary)' }}>{k}</span> — {v}</li>
                ))}
              </ul>
              <P>Each was accurate on its own. The problem was the seams: timestamps that didn&rsquo;t align, no shared key, and no owner of the join. The hard part was never detection. It was reconciliation.</P>
            </Sec>

            <Divider />

            <Sec id="method" eyebrow="03 · What we did">
              <P>We did not reach for a smarter alarm. We built one reconciled timeline — inputs aligned to a common clock, then read for the places they <em>disagreed</em>. The contradictions, it turned out, were the signal.</P>

              <figure style={{ margin: '28px 0' }}>
                <ImgPlaceholder label="figure 1 — four sources aligned to one reconciled timeline" height={240} dark={dark} />
                <figcaption className="sg-mono" style={{ marginTop: 10, color: 'var(--text-dim)' }}>Fig. 1 — Evidence from four systems, aligned. The gap at 02:47 is where they stop agreeing.</figcaption>
              </figure>

              <P>The shape of the method is portable: <strong>inputs → reasoning → outputs → reusable record.</strong> Only the inputs are configured per environment; the reasoning and the record travel unchanged.</P>

              <KpiBlock style={{ margin: '24px 0' }} items={[
                { label: 'Downtime', value: '47m', delta: 'vs 90m median', dir: 'up' },
                { label: 'Time to cause', value: '2.5h', delta: 'was ~2 shifts', dir: 'up' },
                { label: 'Availability', value: '96.4%', delta: '+1.2 pt', dir: 'up' },
              ]} />
            </Sec>

            <Divider />

            <Sec id="rigor" eyebrow="04 · How rigor was held">
              <P>Rigor here is not ceremony — it is the adoption strategy. A claim that cannot be traced does not ship. Every assertion in this article links back to a source line in one of the four systems, and the synthesis was validated by a human before publish.</P>
              <div style={{ border: '1px solid var(--line)', borderLeft: '3px solid var(--color-brand-primary)', background: 'var(--color-brand-light)', padding: '20px 24px', margin: '22px 0' }}>
                <div className="sg-mono" style={{ color: 'var(--color-brand-primary)', marginBottom: 10 }}>Claim → evidence</div>
                <p style={{ fontSize: 14.5, lineHeight: 1.6 }}>&ldquo;The stop began with a guard interlock, not a mechanical fault&rdquo; — traced to {'{{WORK_ORDER_SYSTEM}}'} event 4471 + a {'{{SPC_SYSTEM}}'} drift 90s prior. <span style={{ color: 'var(--color-brand-primary)' }}>[see refs 1, 3]</span></p>
              </div>
            </Sec>

            <Divider />

            <Sec id="record" eyebrow="05 · The reusable record">
              <P>The output is not a war story. It is a template the next event drops into — the same synthesis, regenerated against new inputs, feeding the recording, the digest, the wiki entry, and this article.</P>
              <PromptBlock label="Template · RCA synthesis" style={{ margin: '22px 0' }}>
                <span className="k">synthesize</span>(<span className="a">event</span>) {'{'}
                {'\n  '}join  → [{'{{MA_SYSTEM}}'}, {'{{SPC_SYSTEM}}'}, {'{{DEFECT_SYSTEM}}'}, {'{{WORK_ORDER_SYSTEM}}'}]
                {'\n  '}align → one reconciled timeline
                {'\n  '}read  → where the sources disagree
                {'\n  '}emit  → hypothesis · narrative · action items · <span className="k">reusable_record</span>
                {'\n'}{'}'}
              </PromptBlock>
            </Sec>

            <Divider />

            <Sec id="results" eyebrow="06 · What changed">
              <P>Time-to-cause dropped from roughly two shifts to two and a half hours. But the number that matters is the one that doesn&rsquo;t show on a dashboard: the night shift now opens a record instead of a blank page. The work content fell, and the energy of the work rose.</P>
            </Sec>

            <Divider />

            <Sec id="reasoning" eyebrow="07 · In JJ&rsquo;s words">
              <div className="sg-quote" style={{ borderLeftColor: 'var(--color-accent)', background: dark ? 'var(--color-surface-low)' : '#faf0e9' }}>
                <span className="sg-quote-mark" style={{ color: 'var(--color-accent)' }}>&ldquo;</span>
                <p className="sg-quote-text" style={{ maxWidth: 600 }}>I keep coming back to one thing: we weren&rsquo;t missing data, we were missing a story. Make the four systems agree on a timeline and the cause stops hiding. Then write it down so the next person inherits the thinking, not just the answer.</p>
                <p className="sg-quote-attr">JJ — author&rsquo;s note</p>
              </div>
            </Sec>

            {/* ACTION ITEMS */}
            <div style={{ marginTop: 44 }}>
              <SectionDivider label="Action Items" centered />
              <div style={{ marginTop: 22, border: '1px solid var(--line)' }}>
                {[['Add guard-interlock check to startup sequence', 'M. Okafor', 'Fri', 'Open'], ['Backfill the sensor gap on conveyor 4B', 'Reliability', 'Next wk', 'Open'], ['Template this RCA for the night shift', 'JJ', 'Done', 'Closed']].map((r, i) => (
                  <div key={i} className="article-action" style={{ padding: '13px 20px', borderTop: i ? '1px solid var(--line)' : 0, background: i % 2 ? 'var(--color-surface-low)' : 'transparent' }}>
                    <span style={{ fontSize: 14, color: 'var(--text)' }}>{r[0]}</span>
                    <span className="sg-mono">{r[1]}</span>
                    <span className="sg-mono">{r[2]}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase', color: r[3] === 'Closed' ? 'var(--color-green)' : 'var(--color-amber)' }}>{r[3]}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* REFERENCES */}
            <div style={{ marginTop: 40 }}>
              <SectionDivider label="Traceable Claims · references" />
              <ol style={{ marginTop: 18, display: 'grid', gap: 10, counterReset: 'ref' }}>
                {[
                  ['Event 4471 — line-4 stop record', '{{WORK_ORDER_SYSTEM}}'],
                  ['Availability log, 02:30–03:30', '{{MA_SYSTEM}}'],
                  ['Process drift, sensor 4B', '{{SPC_SYSTEM}}'],
                  ['Inspection pass, lot 22-118', '{{DEFECT_SYSTEM}}'],
                ].map((r, i) => (
                  <li key={i} style={{ display: 'grid', gridTemplateColumns: '28px 1fr auto', gap: 12, alignItems: 'baseline', paddingBottom: 10, borderBottom: '1px solid var(--line)' }}>
                    <span className="sg-display" style={{ fontSize: 18, color: 'var(--color-brand-primary)' }}>{i + 1}</span>
                    <span style={{ fontSize: 13.5 }}>{r[0]}</span>
                    <span className="sg-mono" style={{ color: 'var(--text-dim)' }}>{r[1]}</span>
                  </li>
                ))}
              </ol>
            </div>

            {/* FORWARD PREVIEW */}
            <div style={{ marginTop: 40, border: '1px solid var(--line)', borderLeft: '3px solid var(--color-accent)', padding: '24px 28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>
              <div>
                <div className="sg-mono" style={{ color: 'var(--text-dim)', marginBottom: 8 }}>Next in the queue</div>
                <p className="sg-display" style={{ fontSize: 22, fontStyle: 'italic' }}>Defect tooling — the instrument layer</p>
              </div>
              <a href={SITE.report} className="sg-btn ghost" style={{ textDecoration: 'none' }}>Read next <IconArrow /></a>
            </div>

          </article>
        </main>
      </div>

      {/* FOOTER */}
      <footer style={{ background: 'var(--chrome-bg)', borderTop: '3px solid var(--color-brand-primary)', padding: '32px 48px', marginTop: 56 }}>
        <div style={{ maxWidth: 1180, margin: '0 auto', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>{'{{CONFIDENTIAL_LABEL}}'} · Internal · {'{{ORG}}'} · Published to {'{{LEARNING_PLATFORM}}'}</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.4)' }}>Renders without JavaScript · Print-ready · WCAG AA</span>
        </div>
      </footer>
    </div>
  );
}

// ---- prose helpers ----
function Sec({ id, eyebrow, children }) {
  return (
    <section id={id} style={{ scrollMarginTop: 80 }}>
      <div style={{ marginBottom: 16 }}><Eyebrow variant="accent">{eyebrow}</Eyebrow></div>
      {children}
    </section>
  );
}
function P({ children }) {
  return <p style={{ fontSize: 16.5, lineHeight: 1.72, color: 'var(--text)', margin: '0 0 18px', maxWidth: 680 }}>{children}</p>;
}
function Divider() {
  return <div style={{ margin: '36px 0' }}><SectionDivider label="§" centered /></div>;
}

// ---- TOC sidebar (scroll-tracking) ----
function TocSidebar({ sections, active, progress, onGoto }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>On this page</span>
        <span className="sg-mono" style={{ color: 'var(--color-brand-primary)', fontVariantNumeric: 'tabular-nums' }}>{Math.round(progress * 100)}%</span>
      </div>
      <div style={{ height: 2, background: 'var(--line)', marginBottom: 16, position: 'relative' }}>
        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${progress * 100}%`, background: 'var(--color-brand-primary)', transition: 'width 120ms linear' }} />
      </div>
      <ul style={{ display: 'grid', gap: 1 }}>
        {sections.map((s) => {
          const on = active === s.id;
          return (
            <li key={s.id}>
              <a onClick={() => onGoto(s.id)} style={{ display: 'block', fontSize: 13, lineHeight: 1.35, padding: '7px 12px', marginLeft: -12, cursor: 'pointer', color: on ? 'var(--color-brand-primary)' : 'var(--text-dim)', borderLeft: on ? '2px solid var(--color-brand-primary)' : '2px solid var(--line)', background: on ? 'var(--color-brand-light)' : 'transparent', fontWeight: on ? 600 : 400, transition: 'color 150ms, background 150ms' }}>{s.toc}</a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

// ---- Sections sidebar (hub-style wayfinding) ----
function SectionsSidebar({ active }) {
  const groups = [
    { h: 'Surfaces', items: [['The Show', 'show'], ['The Newsletter', 'news'], ['The Articles', 'articles']] },
    { h: 'Cases', items: [['Downtime RCA', 'downtime'], ['Defect detection', 'dd'], ['Defect tooling', 'dt'], ['Technician scaling', 'ts']] },
    { h: 'Library', items: [['The Practice Library', 'lib'], ['Templates & prompts', 'tpl']] },
  ];
  return (
    <div>
      {groups.map((g) => (
        <div key={g.h} style={{ marginBottom: 22 }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 12 }}>{g.h}</div>
          <ul style={{ display: 'grid', gap: 2 }}>
            {g.items.map(([label, id]) => {
              const on = active === id || (active === 'downtime' && id === 'articles');
              return (
                <li key={id}>
                  <a style={{ display: 'block', fontSize: 13.5, padding: '6px 10px', marginLeft: -10, cursor: 'pointer', color: on ? 'var(--color-brand-primary)' : 'var(--text)', borderLeft: on ? '2px solid var(--color-brand-primary)' : '2px solid transparent', background: on ? 'var(--color-brand-light)' : 'transparent', fontWeight: on ? 600 : 400 }}>{label}</a>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </div>
  );
}

window.Article = Article;
