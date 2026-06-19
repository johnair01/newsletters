// signals/hub.jsx — The Hub (converged) · Editorial type + OS sidebar +
// a Signals-native "Key Moments" pattern for The Show.
// Full-page scrollable publication. Owns light/dark state.

function Hub() {
  const [theme, setTheme] = React.useState('light');
  const [activeNav, setActiveNav] = React.useState('the-show');
  const dark = theme === 'dark';

  const scrollTo = (id, nav) => {
    if (nav) setActiveNav(nav);
    const el = document.getElementById(id);
    if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 78, behavior: 'smooth' });
  };

  const navGroups = [
    { h: 'Surfaces', items: [['The Show', 'the-show', 'key-moments'], ['The Newsletter', 'the-newsletter', 'surfaces'], ['The Articles', 'the-articles', 'surfaces']] },
    { h: 'Cases', items: [['Downtime RCA', 'downtime', 'key-moments'], ['Defect detection', 'defect-det', 'field'], ['Defect tooling', 'defect-tool', 'field'], ['Technician scaling', 'tech-scaling', 'field']] },
    { h: 'Library', items: [['The Practice Library', 'library', 'surfaces'], ['Templates & prompts', 'templates', 'template']] },
  ];

  const moments = [
    { n: '01', ts: '02:10', spine: 'What was the problem', title: '47 minutes, four systems, no agreement', body: 'The line stopped and each data source told a different story. JJ frames the real burden — not the stop itself, but the hours of cross-referencing it took just to explain it.', img: 'control room — line 4 stop' },
    { n: '02', ts: '06:40', spine: 'What was hard', title: 'The evidence was scattered across four systems that never line up', body: 'Timestamps disagreed and nobody owned the join. The hard part was reconciliation, not detection — pulling {{MA_SYSTEM}}, {{SPC_SYSTEM}}, {{DEFECT_SYSTEM}} and {{WORK_ORDER_SYSTEM}} into one truth.', img: 'four-source timeline, misaligned' },
    { n: '03', ts: '11:25', spine: 'What actually worked', title: 'Align the timelines — then let the disagreements point at the cause', body: 'Instead of a smarter alarm, the team built one reconciled timeline. The contradictions between systems stopped being noise and became the signal.', img: 'reconciled timeline view' },
    { n: '04', ts: '18:30', spine: 'How rigor was held', title: 'Every claim traced to a source, human-validated before publish', body: 'Practitioner plus domain review. Nothing shipped without a line back to the evidence — rigor as the way the work earns trust, not as ceremony.', img: 'review trail — claims to evidence' },
    { n: '05', ts: '24:05', spine: 'What others should copy', title: 'The reusable record, not the heroics', body: 'The output isn\u2019t a war story — it\u2019s a template the next shift inherits. Same shape, new event. One conversation becomes a record, an article, and a prompt.', img: 'reusable record template' },
    { n: '06', ts: '31:50', spine: 'What changed in the workflow', title: 'Time-to-cause fell from ~2 shifts to 2.5 hours', body: 'Work content down, energy up. The night shift now opens a record instead of a blank page — and the method ports to the next case without starting over.', img: 'before / after — time to cause' },
  ];

  return (
    <div className="signals" data-theme={theme} style={{ minHeight: '100vh', fontFamily: 'var(--font-body)' }}>

      {/* NAV */}
      <SiteNav active="The Show" theme={theme} onToggle={() => setTheme(dark ? 'light' : 'dark')} />

      {/* HERO */}
      <section style={{ padding: '64px 48px 52px', borderBottom: '1px solid var(--line)', maxWidth: 1240, margin: '0 auto' }}>
        <Eyebrow withRule>Engineering Coherence &amp; AI Practice — Issue No. 014</Eyebrow>
        <h1 className="sg-display" style={{ fontSize: 62, maxWidth: 940, marginTop: 24 }}>
          Engineering knowledge that stays <em>coherent</em>, credible, and worth reusing.
        </h1>
        <p style={{ fontSize: 17, lineHeight: 1.6, color: 'var(--text-dim)', maxWidth: 580, marginTop: 24 }}>
          A practitioner-led publication from the plant floor — the recorded conversations, the weekly signal, and the peer-reviewed write-ups that turn one good fix into something the whole organization can run.
        </p>
        <div style={{ display: 'flex', gap: 14, marginTop: 32 }}>
          <a href={SITE.show} className="sg-btn" style={{ textDecoration: 'none' }}>Open the latest episode <IconArrow /></a>
          <Button ghost>How this works</Button>
        </div>
      </section>

      {/* BODY — sidebar + main */}
      <div className="hub-body" style={{ maxWidth: 1240, margin: '0 auto', padding: '0 48px 8px' }}>

        {/* SIDEBAR */}
        <aside className="hub-aside" style={{ top: 88, paddingTop: 44 }}>
          {navGroups.map((g) => (
            <div key={g.h} style={{ marginBottom: 24 }}>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 12 }}>{g.h}</div>
              <ul style={{ display: 'grid', gap: 2 }}>
                {g.items.map(([label, id, target]) => {
                  const active = activeNav === id;
                  return (
                    <li key={id}>
                      <a onClick={() => { setActiveNav(id); scrollTo(target); }} style={{ display: 'block', fontSize: 13.5, padding: '6px 10px', marginLeft: -10, color: active ? 'var(--color-brand-primary)' : 'var(--text)', borderLeft: active ? '2px solid var(--color-brand-primary)' : '2px solid transparent', background: active ? 'var(--color-brand-light)' : 'transparent', cursor: 'pointer', fontWeight: active ? 600 : 400 }}>{label}</a>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}

          {/* This episode */}
          <div style={{ borderTop: '1px solid var(--line)', paddingTop: 20, marginTop: 4 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 14 }}>This Episode</div>
            <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', rowGap: 9, columnGap: 12, margin: 0 }}>
              {[['Host', 'JJ'], ['Format', 'The Show · Ep. 014'], ['Runtime', '38:00'], ['Moments', '6 captured']].map(([k, v]) => (
                <React.Fragment key={k}>
                  <dt className="sg-mono" style={{ color: 'var(--text-dim)' }}>{k}</dt>
                  <dd style={{ margin: 0, fontSize: 13, color: 'var(--text)', fontWeight: 500 }}>{v}</dd>
                </React.Fragment>
              ))}
            </dl>
            <div style={{ marginTop: 16 }}><GateBadge current="Published" /></div>
            <a href={SITE.show} style={{ display: 'inline-flex', alignItems: 'center', gap: 7, marginTop: 18, fontFamily: 'var(--font-mono)', fontSize: 10.5, letterSpacing: '0.1em', textTransform: 'uppercase', textDecoration: 'none', color: 'var(--color-brand-primary)', cursor: 'pointer' }}>Watch the recording ↗</a>
          </div>

          {/* Subscribe */}
          <div style={{ marginTop: 24, border: '1px solid var(--line)', borderLeft: '3px solid var(--color-accent)', padding: '18px 20px' }}>
            <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 17, lineHeight: 1.35 }}>The weekly signal, in your inbox.</p>
            <p style={{ fontSize: 12.5, color: 'var(--text-dim)', marginTop: 8, lineHeight: 1.5 }}>Level-headed. No hype. Mondays.</p>
            <button className="sg-btn" style={{ marginTop: 14, width: '100%', justifyContent: 'center', padding: '10px' }}>Join the list</button>
          </div>
        </aside>

        {/* MAIN */}
        <main className="hub-main" style={{ paddingTop: 44, minWidth: 0 }}>

          {/* Lead signal intro */}
          <section id="downtime">
            <SectionDivider label="Lead Signal · The Show, Ep. 014" />
            <h2 className="sg-display" style={{ fontSize: 40, lineHeight: 1.1, marginTop: 28, maxWidth: 720 }}>
              The downtime nobody could explain — <em>and the trail that finally did.</em>
            </h2>
            <p style={{ fontSize: 16, lineHeight: 1.65, color: 'var(--text-dim)', marginTop: 20, maxWidth: 620 }}>
              A line goes down for 47 minutes. Four systems each hold a piece of the story and none of them agree. Here is how the team reconstructed what actually happened — told in the practitioner&rsquo;s own voice, then turned into a record the next shift can reuse without starting over.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 22, marginTop: 24, flexWrap: 'wrap' }}>
              <ProfileChip initials="JJ" name="JJ" role="Practitioner-in-residence" />
              <span className="sg-mono">14 min read</span>
              <Tag kind="peer">Peer Reviewed</Tag>
            </div>
            <div style={{ display: 'flex', gap: 18, marginTop: 22, flexWrap: 'wrap' }}>
              <a href={SITE.report} className="sg-btn" style={{ textDecoration: 'none' }}>Open the RCA record <IconArrow /></a>
              <a href={SITE.article} className="sg-btn ghost" style={{ textDecoration: 'none' }}>Read the write-up</a>
            </div>
          </section>

          {/* KEY MOMENTS */}
          <section id="key-moments" style={{ marginTop: 52 }}>
            <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 24, flexWrap: 'wrap' }}>
              <SectionDivider label="Key Moments · the format spine, timestamped" variant="accent" style={{ flex: 1, minWidth: 320 }} />
              <span className="sg-mono" style={{ whiteSpace: 'nowrap' }}>6 moments · 38:00</span>
            </div>

            <div style={{ marginTop: 28, display: 'grid', gap: 0, borderTop: '1px solid var(--line)' }}>
              {moments.map((m, i) => (
                <KeyMoment key={m.n} m={m} dark={dark} last={i === moments.length - 1} />
              ))}
            </div>
          </section>

          {/* PULL QUOTE */}
          <section style={{ marginTop: 44 }}>
            <div className="sg-quote">
              <span className="sg-quote-mark">&ldquo;</span>
              <p className="sg-quote-text" style={{ maxWidth: 640 }}>We didn&rsquo;t need a smarter alarm. We needed the four systems to tell one story.</p>
              <p className="sg-quote-attr">JJ — in conversation, Ep. 014 · 11:25</p>
            </div>
          </section>

          {/* REUSABLE TEMPLATE */}
          <section id="template" style={{ marginTop: 44 }}>
            <SectionDivider label="The Reusable Record · regenerated per event" />
            <PromptBlock label="Template · RCA synthesis" style={{ marginTop: 22 }}>
              <span className="d">{'// one conversation \u2192 record, article, wiki entry, prompt'}</span>{'\n'}
              <span className="k">synthesize</span>(<span className="a">event</span>) {'{'}
              {'\n  '}join  → [{'{{MA_SYSTEM}}'}, {'{{SPC_SYSTEM}}'}, {'{{DEFECT_SYSTEM}}'}, {'{{WORK_ORDER_SYSTEM}}'}]
              {'\n  '}align → one reconciled timeline
              {'\n  '}emit  → hypothesis · narrative · action items · <span className="k">reusable_record</span>
              {'\n'}{'}'}
            </PromptBlock>
          </section>

          {/* THREE SURFACES */}
          <section id="surfaces" style={{ marginTop: 52 }}>
            <SectionDivider label="One conversation, many surfaces" />
            <div style={{ marginTop: 28, borderTop: '1px solid var(--line)' }}>
              {[
                { n: '01', name: 'The Show', tail: 'recorded conversations', body: 'Practitioner-led recordings of real use cases — engineers walking through work they actually did, and the reasoning behind it.', meta: 'New episode every other Thursday', href: SITE.show },
                { n: '02', name: 'The Newsletter', tail: 'weekly signal', body: 'A level-headed digest carrying organizational memory and proof of usefulness. Lead signal · from the field · state of the art · risks & realities · the queue.', meta: 'Sent Mondays · 6-minute read', href: SITE.newsletter },
                { n: '03', name: 'The Articles', tail: 'peer-reviewed write-ups', body: 'Practitioner write-ups generated from conversations and system outputs — traceable claims, evidence-backed, human-validated.', meta: 'Published to the Practice Library', href: SITE.article },
              ].map((s) => (
                <div key={s.n} className="hub-surface" style={{ padding: '26px 0', borderBottom: '1px solid var(--line)' }}>
                  <span className="sg-display" style={{ fontSize: 36, color: 'var(--line)' }}>{s.n}</span>
                  <div>
                    <h3 className="sg-display" style={{ fontSize: 25 }}>{s.name} <em style={{ color: 'var(--text-dim)', fontSize: 19 }}>— {s.tail}</em></h3>
                    <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-dim)', marginTop: 10, maxWidth: 520 }}>{s.body}</p>
                  </div>
                  <div className="hub-surface-meta" style={{ textAlign: 'right' }}>
                    <div className="sg-mono" style={{ marginBottom: 14 }}>{s.meta}</div>
                    <a href={s.href} style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', textDecoration: 'none', color: 'var(--color-brand-primary)', display: 'inline-flex', alignItems: 'center', gap: 7, cursor: 'pointer' }}>Enter <IconArrow /></a>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* FROM THE FIELD + QUEUE */}
          <section id="field" style={{ marginTop: 52, paddingBottom: 8 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48 }}>
              <div>
                <SectionDivider label="From the Field" />
                <div style={{ marginTop: 22 }}>
                  {[
                    { t: 'Three fragmented signals, one defect — characterized in an afternoon', tag: 'Defect detection', status: 'Published' },
                    { t: 'Reducing the work content of a frontline inspection by half', tag: 'Technician scaling', status: 'In Review' },
                    { t: 'Writing a downtime so the next shift inherits it', tag: 'Workflow design', status: 'Published' },
                  ].map((a, i) => (
                    <div key={i} style={{ padding: '16px 0', borderTop: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', gap: 20, alignItems: 'flex-start' }}>
                      <div>
                        <p style={{ fontSize: 14.5, lineHeight: 1.4, color: 'var(--text)', maxWidth: 340 }}>{a.t}</p>
                        <span className="sg-mono" style={{ marginTop: 7, display: 'inline-block' }}>{a.tag}</span>
                      </div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', color: a.status === 'Published' ? 'var(--color-brand-primary)' : 'var(--color-amber)', whiteSpace: 'nowrap', paddingTop: 2 }}>{a.status}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <SectionDivider label="The Queue" />
                <div style={{ marginTop: 22, background: 'var(--color-surface-low)', borderLeft: '3px solid var(--color-ink)', padding: '22px 26px' }}>
                  <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 18, lineHeight: 1.4, color: 'var(--text)' }}>What&rsquo;s in design, parked, or up next.</p>
                  <ul style={{ marginTop: 18, display: 'grid', gap: 13 }}>
                    {[['Next', 'Defect tooling — the practitioner-facing instrument layer'], ['Parked', 'A general assurance / verification layer — needs confirmation'], ['Drafting', 'Work-content reduction, as the umbrella frame']].map(([k, v]) => (
                      <li key={v} style={{ display: 'grid', gridTemplateColumns: '70px 1fr', gap: 12, alignItems: 'baseline' }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>{k}</span>
                        <span style={{ fontSize: 13.5, lineHeight: 1.45, color: 'var(--text)' }}>{v}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      {/* FOOTER */}
      <footer style={{ background: 'var(--chrome-bg)', borderTop: '3px solid var(--color-brand-primary)', padding: '46px 48px 34px', marginTop: 56 }}>
        <div style={{ maxWidth: 1240, margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr', gap: 40 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10 }}>
                <span style={{ fontFamily: 'var(--font-display)', fontSize: 22, color: 'var(--chrome-fg)' }}>Signals</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.4)' }}>from the underground</span>
              </div>
              <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 18, color: 'rgba(255,255,255,0.7)', marginTop: 16, maxWidth: 360, lineHeight: 1.4 }}>Engineers learning from engineers. Coherence over hype.</p>
            </div>
            {[['Surfaces', ['The Show', 'The Newsletter', 'The Articles', 'Archive']], ['Practice', ['How review works', 'Submit a use case', 'The Practice Library', 'Onboarding']]].map(([h, items]) => (
              <div key={h}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'rgba(255,255,255,0.4)', marginBottom: 16 }}>{h}</div>
                <ul style={{ display: 'grid', gap: 11 }}>
                  {items.map((it) => <li key={it} style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'rgba(255,255,255,0.7)', cursor: 'pointer' }}>{it}</li>)}
                </ul>
              </div>
            ))}
          </div>
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.12)', marginTop: 34, paddingTop: 18, display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.35)' }}>{'{{CONFIDENTIAL_LABEL}}'} · Internal · {'{{ORG}}'}</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em', color: 'rgba(255,255,255,0.35)' }}>Renders without JavaScript · WCAG AA</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

// ---- Key Moment row — thumbnail + timestamped, spine-tagged ----
function KeyMoment({ m, dark, last }) {
  const [hover, setHover] = React.useState(false);
  return (
    <article
      onMouseEnter={() => setHover(true)} onMouseLeave={() => setHover(false)}
      className="hub-moment"
      style={{ padding: '26px 0', borderBottom: last ? 0 : '1px solid var(--line)', alignItems: 'start', transition: 'background var(--dur-base) var(--ease-out)', background: hover ? 'var(--color-surface-low)' : 'transparent', marginInline: hover ? -16 : 0, paddingInline: hover ? 16 : 0 }}>
      <span className="km-num sg-display" style={{ fontSize: 30, color: hover ? 'var(--color-accent)' : 'var(--line)', transition: 'color var(--dur-base)' }}>{m.n}</span>

      <a className="km-thumb" style={{ position: 'relative', display: 'block', cursor: 'pointer' }}>
        <ImgPlaceholder label={m.img} height={172} dark={dark} />
        <span style={{ position: 'absolute', top: 10, left: 10, display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: 'var(--font-mono)', fontSize: 11, fontWeight: 500, letterSpacing: '0.04em', color: '#fff', background: 'rgba(10,10,15,0.82)', padding: '5px 9px' }}>
          {m.ts} <span style={{ opacity: 0.8 }}>↗</span>
        </span>
      </a>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
          <span className="sg-tag cat">{m.spine}</span>
        </div>
        <h3 className="sg-display" style={{ fontSize: 23, lineHeight: 1.18 }}>{m.title}</h3>
        <p style={{ fontSize: 14.5, lineHeight: 1.62, color: 'var(--text-dim)', marginTop: 12, maxWidth: 560 }}>{m.body}</p>
      </div>
    </article>
  );
}

window.Hub = Hub;
