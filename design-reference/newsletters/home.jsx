// newsletters/home.jsx — THE fused open-source home (one front door).
// Leads with the WHY (the idea), proves it with the WOW (the interactive
// personalization demo), then hands off to the HOW (the engine + the code).
// Owns light/dark + the "viewing as…" persona state for the whole page.

function Home() {
  const [theme, setTheme] = React.useState('light');
  const [who, setWho] = React.useState('maintainer');
  const dark = theme === 'dark';
  const MW = 1180;

  // One reviewed source — "the latency regression four dashboards disagreed
  // about" — re-cut per audience corpus.
  const LETTERS = {
    maintainer: {
      kicker: 'Your weekly · checkout-svc',
      lead: { tag: 'Root cause', title: 'Connection-pool saturation under the new retry policy', body: 'The p99 climb traced to retries exhausting the pool during a downstream blip — invisible on the APM average, obvious once the four sources were on one timeline.' },
      items: [
        ['The fix that shipped', 'Bounded retries + a pool-pressure guardrail. Diff and the reusable record are linked.'],
        ['Watch this week', 'Pool-wait p99 and retry-rate on the dashboard you own.'],
      ],
      why: 'You own checkout-svc — surfaced because the regression hit your service during your on-call window.',
    },
    contributor: {
      kicker: 'Your weekly · onboarding edition',
      lead: { tag: 'Start here', title: 'How we debug latency here, walked through end to end', body: 'A real regression, narrated: how four observability sources get reconciled into one story. The clearest map of our tooling you\u2019ll find in week one.' },
      items: [
        ['The reusable record', 'Open the RCA template — the shape you\u2019ll inherit next time, not a blank page.'],
        ['Glossary', 'APM, traces, RUM, p99 — the terms in this letter, defined.'],
      ],
      why: 'You\u2019re in your first month — your corpus weights orientation and context over deep internals.',
    },
    lead: {
      kicker: 'Your weekly · the signal',
      lead: { tag: 'Impact', title: 'Time-to-cause fell from ~2 shifts to 2.5 hours', body: 'One reconciled timeline replaced two days of cross-referencing. Work content down, energy up — and the method ports to the next incident without starting over.' },
      items: [
        ['What it unblocks', 'On-call hours returned to feature work; the pattern is now a template.'],
        ['Across the quarter', 'Third regression resolved with the reusable record. The trend is the story.'],
      ],
      why: 'You sponsor the team — your corpus leads with outcomes, cost, and cross-case patterns.',
    },
  };
  const L = LETTERS[who];
  const persona = NL_PERSONAS.find((p) => p.id === who);

  const navLinks = [['Start here', '#start'], ['Newsletters', '#newsletters'], ['Articles', '#surfaces'], ['The Show', '#surfaces']];

  return (
    <div className="signals" data-theme={theme} style={{ minHeight: '100vh', fontFamily: 'var(--font-body)' }}>
      <NLNav active="Start here" theme={theme} onToggle={() => setTheme(dark ? 'light' : 'dark')} links={navLinks} />

      {/* ───────────── WHY · hero ───────────── */}
      <section id="start" style={{ maxWidth: MW, margin: '0 auto', padding: '78px 44px 56px', borderBottom: '1px solid var(--line)', scrollMarginTop: 80 }}>
        <Eyebrow withRule>An open framework for working in the open</Eyebrow>
        <h1 className="sg-display" style={{ fontSize: 72, lineHeight: 1.03, maxWidth: 960, marginTop: 26 }}>
          Turn information into <em>conversation.</em><br />Conversation into <em>action.</em>
        </h1>
        <p style={{ fontSize: 18.5, lineHeight: 1.6, color: 'var(--text-dim)', maxWidth: 620, marginTop: 28 }}>
          Newsletters distills structured knowledge into audience-tuned reports, articles, and letters — drafted by agents, approved by humans, published in the open. A learning surface for teams that want to learn everywhere, all the time.
        </p>
        <div style={{ display: 'flex', gap: 14, marginTop: 34, flexWrap: 'wrap' }}>
          <a href="#newsletters" className="sg-btn" style={{ textDecoration: 'none' }}>See it in action <IconArrow /></a>
          <a href="#developers" className="sg-btn ghost" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8 }}><IconGit size={13} /> View on GitHub</a>
        </div>
        <p className="sg-mono" style={{ color: 'var(--text-dim)', marginTop: 26 }}>Open source · MIT · self-hostable · human-in-the-loop by design</p>
      </section>

      {/* ───────────── WHY · the problem ───────────── */}
      <section style={{ maxWidth: MW, margin: '0 auto', padding: '56px 44px 0' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 56, alignItems: 'start' }} className="nl-2col">
          <div>
            <SectionDivider label="Why this exists" />
            <p style={{ fontFamily: 'var(--font-display)', fontSize: 30, lineHeight: 1.28, marginTop: 22, maxWidth: 460 }}>
              In a world flooded with information, <em>relevance wins.</em>
            </p>
          </div>
          <div style={{ paddingTop: 6 }}>
            <p style={{ fontSize: 16.5, lineHeight: 1.72, color: 'var(--text)' }}>
              Most of what a team learns evaporates. It lives in a thread, a call nobody recorded, a dashboard only one person reads. The knowledge is there — it just never gets distilled, attributed, or relayed to the people it would help.
            </p>
            <p style={{ fontSize: 16.5, lineHeight: 1.72, color: 'var(--text-dim)', marginTop: 16 }}>
              Newsletters is the semantic bridge between structured data and human understanding: a publishing layer that captures the work as it happens and hands each person exactly what matters to them.
            </p>
          </div>
        </div>
      </section>

      {/* ───────────── WOW · the personalization demo ───────────── */}
      <section id="newsletters" style={{ maxWidth: MW, margin: '0 auto', padding: '72px 44px 0', scrollMarginTop: 80 }}>
        <SectionDivider label="See it in action · audience-aware by design" variant="accent" />
        <h2 className="sg-display" style={{ fontSize: 44, lineHeight: 1.08, marginTop: 22, maxWidth: 760 }}>
          Everyone gets the newsletter that&rsquo;s <em>about them.</em>
        </h2>
        <p style={{ fontSize: 16.5, lineHeight: 1.62, color: 'var(--text-dim)', maxWidth: 620, marginTop: 16 }}>
          One source event. One review. Then the agent re-cuts the weekly letter from each reader&rsquo;s own corpus. Same facts — different emphasis. Switch readers and watch it change:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 36, alignItems: 'start', marginTop: 32 }} className="nl-demo-grid">
          {/* picker */}
          <div style={{ position: 'sticky', top: 88 }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--text-dim)', marginBottom: 14 }}>Viewing as</div>
            <div style={{ display: 'grid', gap: 8 }}>
              {NL_PERSONAS.map((p) => {
                const on = who === p.id;
                return (
                  <button key={p.id} onClick={() => setWho(p.id)} style={{
                    textAlign: 'left', cursor: 'pointer', padding: '14px 16px', background: on ? 'var(--card)' : 'transparent',
                    border: '1px solid var(--line)', borderLeft: `3px solid ${on ? p.accent : 'var(--line)'}`,
                    display: 'flex', alignItems: 'center', gap: 12, transition: 'all 180ms var(--ease-out)', boxShadow: on ? '0 4px 18px rgba(0,0,0,0.07)' : 'none',
                  }}>
                    <span className="sg-avatar" style={{ width: 34, height: 34, fontSize: 14, background: on ? p.accent : 'var(--color-surface-mid)', color: on ? '#fff' : 'var(--text-dim)' }}>{p.initials}</span>
                    <span>
                      <span style={{ display: 'block', fontSize: 14, fontWeight: 600, color: on ? 'var(--text)' : 'var(--text-dim)' }}>{p.name}</span>
                      <span style={{ display: 'block', fontFamily: 'var(--font-mono)', fontSize: 10.5, color: 'var(--text-dim)', marginTop: 2 }}>{p.role}</span>
                    </span>
                  </button>
                );
              })}
            </div>
            <div style={{ marginTop: 18, border: '1px solid var(--line)', borderLeft: '3px solid var(--color-ink)', padding: '14px 16px', background: 'var(--color-surface-low)' }}>
              <div className="sg-mono" style={{ color: 'var(--text-dim)', marginBottom: 7 }}>Same source</div>
              <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text)' }}>All three letters are cut from one reviewed record — the latency-regression RCA.</p>
            </div>
          </div>

          {/* the generated letter */}
          <div key={who} className="sg-fade" style={{ background: 'var(--card)', border: '1px solid var(--line)', borderTop: `3px solid ${persona.accent}` }}>
            <div style={{ padding: '22px 30px', borderBottom: '1px solid var(--line)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
              <div>
                <div className="sg-mono" style={{ color: persona.accent, letterSpacing: '0.1em', textTransform: 'uppercase' }}>{L.kicker}</div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: 22, marginTop: 4 }}>The weekly signal</div>
              </div>
              <ProfileChip initials={persona.initials} name={persona.name} role={persona.role} />
            </div>
            <div style={{ padding: '28px 30px 0' }}>
              <Tag kind="cat">{L.lead.tag}</Tag>
              <h3 className="sg-display" style={{ fontSize: 30, lineHeight: 1.16, marginTop: 14, maxWidth: 560 }}>{L.lead.title}</h3>
              <p style={{ fontSize: 15.5, lineHeight: 1.65, color: 'var(--text-dim)', marginTop: 14, maxWidth: 560 }}>{L.lead.body}</p>
            </div>
            <div style={{ padding: '24px 30px 0' }}>
              {L.items.map(([t, d]) => (
                <div key={t} style={{ padding: '16px 0', borderTop: '1px solid var(--line)' }}>
                  <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text)' }}>{t}</div>
                  <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--text-dim)', marginTop: 4 }}>{d}</p>
                </div>
              ))}
            </div>
            <div style={{ margin: '8px 30px 30px', background: 'var(--color-brand-light)', borderLeft: `3px solid ${persona.accent}`, padding: '14px 18px' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9.5, letterSpacing: '0.14em', textTransform: 'uppercase', color: persona.accent }}>Why you&rsquo;re seeing this</span>
              <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--text)', marginTop: 6 }}>{L.why}</p>
            </div>
          </div>
        </div>

        {/* how personalization works */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 30 }} className="nl-how-grid">
          {[
            ['Codify once', 'The event is reviewed and recorded a single time, every claim traced to its source.'],
            ['Tune to a corpus', 'Each reader carries a private corpus — role, owned services, what they\u2019ve read. It stays local.'],
            ['Re-cut on send', 'The agent reorders, reframes, and trims the same record against that corpus. No new facts — new emphasis.'],
          ].map(([t, d], i) => (
            <div key={t} className="sg-card" style={{ borderLeftColor: NL_PERSONAS[i].accent }}>
              <span className="sg-display" style={{ fontSize: 28, color: 'var(--line)' }}>{String(i + 1).padStart(2, '0')}</span>
              <div className="sg-display" style={{ fontSize: 20, marginTop: 6 }}>{t}</div>
              <p style={{ fontSize: 13.5, lineHeight: 1.6, color: 'var(--text-dim)', marginTop: 10 }}>{d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ───────────── HOW · the publishing engine ───────────── */}
      <section id="engine" style={{ maxWidth: MW, margin: '0 auto', padding: '72px 44px 0', scrollMarginTop: 80 }}>
        <SectionDivider label="How it publishes · human in the loop" />
        <p style={{ fontSize: 15.5, lineHeight: 1.6, color: 'var(--text-dim)', margin: '16px 0 30px', maxWidth: 640 }}>
          Agents do the drafting. People do the deciding. Nothing publishes without passing through review — the same gate that makes the output worth trusting.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', border: '1px solid var(--line)' }} className="nl-pipe">
          {NL_PIPELINE.map((p, i) => (
            <div key={p.k} style={{ padding: '24px 24px 28px', borderRight: i < 3 ? '1px solid var(--line)' : 0, borderLeft: i === 0 ? '3px solid var(--color-brand-primary)' : 0, position: 'relative' }}>
              <div className="sg-mono" style={{ color: 'var(--color-accent)', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 12 }}>{String(i + 1).padStart(2, '0')} · {p.k}</div>
              <h4 className="sg-display" style={{ fontSize: 19, lineHeight: 1.15 }}>{p.t}</h4>
              <p style={{ fontSize: 13, lineHeight: 1.55, color: 'var(--text-dim)', marginTop: 10 }}>{p.d}</p>
              {i < 3 && <span style={{ position: 'absolute', right: -8, top: '50%', transform: 'translateY(-50%)', zIndex: 2, color: 'var(--color-brand-primary)', background: 'var(--bg)' }}><IconArrow /></span>}
            </div>
          ))}
        </div>
        <div style={{ marginTop: 18, display: 'flex', alignItems: 'center', gap: 18, flexWrap: 'wrap' }}>
          <span className="sg-mono" style={{ color: 'var(--text-dim)' }}>The review gate, on every artifact:</span>
          <GateBadge current="In Review" />
        </div>
      </section>

      {/* ───────────── HOW · the four surfaces ───────────── */}
      <section id="surfaces" style={{ maxWidth: MW, margin: '0 auto', padding: '64px 44px 0', scrollMarginTop: 80 }}>
        <SectionDivider label="One conversation, many surfaces" variant="accent" />
        <p style={{ fontSize: 15.5, lineHeight: 1.6, color: 'var(--text-dim)', margin: '16px 0 28px', maxWidth: 600 }}>
          A single record fans out into everything a reader might need — each surface a different distance from the raw work.
        </p>
        <div style={{ borderTop: '1px solid var(--line)' }}>
          {NL_SURFACES.map((s) => (
            <div key={s.n} style={{ display: 'grid', gridTemplateColumns: '76px 1fr 240px', gap: 28, alignItems: 'baseline', padding: '26px 0', borderBottom: '1px solid var(--line)' }} className="nl-surface-row">
              <span className="sg-display" style={{ fontSize: 36, color: 'var(--line)' }}>{s.n}</span>
              <div>
                <h3 className="sg-display" style={{ fontSize: 26 }}>{s.name} <em style={{ color: 'var(--text-dim)', fontSize: 19 }}>— {s.tail}</em></h3>
                <p style={{ fontSize: 14.5, lineHeight: 1.6, color: 'var(--text-dim)', marginTop: 10, maxWidth: 540 }}>{s.body}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="sg-mono" style={{ marginBottom: 14 }}>{s.meta}</div>
                <a href="#" style={{ fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', textDecoration: 'none', color: 'var(--color-brand-primary)', display: 'inline-flex', alignItems: 'center', gap: 7, cursor: 'pointer' }}>Enter <IconArrow /></a>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ───────────── WHY · the thesis (anchor) ───────────── */}
      <section style={{ maxWidth: MW, margin: '0 auto', padding: '64px 44px 0' }}>
        <SectionDivider label="The thesis · five practices of working in the open" />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 0, marginTop: 26, borderTop: '1px solid var(--line)', borderLeft: '1px solid var(--line)' }} className="nl-practice-grid">
          {NL_PRACTICES.map(([t, d], i) => (
            <div key={t} style={{ padding: '20px 18px 22px', borderRight: '1px solid var(--line)', borderBottom: '1px solid var(--line)' }}>
              <span className="sg-display" style={{ fontSize: 22, color: 'var(--line)' }}>{String(i + 1).padStart(2, '0')}</span>
              <div className="sg-display" style={{ fontSize: 17, lineHeight: 1.14, marginTop: 8 }}>{t}</div>
              <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text-dim)', marginTop: 8 }}>{d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ───────────── HOW · for developers ───────────── */}
      <section id="developers" style={{ maxWidth: MW, margin: '0 auto', padding: '72px 44px 0', scrollMarginTop: 80 }}>
        <SectionDivider label="For developers · clone it, point it at your work" variant="accent" />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.05fr', gap: 40, marginTop: 26, alignItems: 'start' }} className="nl-2col">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', fontSize: 13 }}>
              <IconGit size={15} /> <span style={{ color: 'var(--text)' }}>nneibaue</span> / <span style={{ color: 'var(--color-brand-primary)', fontWeight: 500 }}>newsletters</span>
              <span style={{ marginLeft: 6, padding: '2px 8px', border: '1px solid var(--line)', fontSize: 10, letterSpacing: '0.08em', textTransform: 'uppercase' }}>public</span>
            </div>
            <p style={{ fontSize: 16, lineHeight: 1.68, color: 'var(--text)', marginTop: 18, maxWidth: 460 }}>
              Everything is a typed, type-safe model so outputs stay consistent and auditable. Three core objects carry the whole system: a <strong>Source</strong> (what happened), a <strong>Distillation</strong> (the agent&rsquo;s synthesis, every claim traced), and a <strong>Surface</strong> (the published artifact + its review gate).
            </p>
            <p style={{ fontSize: 14.5, lineHeight: 1.65, color: 'var(--text-dim)', marginTop: 14, maxWidth: 460 }}>
              Deploy modular MCP servers so private corpora stay local and encrypted. Every surface is a slot-marked template — fork it, repopulate with your specifics, ship.
            </p>
            <div style={{ marginTop: 22, display: 'flex', gap: 14, flexWrap: 'wrap' }}>
              <a href="#" className="sg-btn" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8 }}><IconGit size={13} /> Clone the repo</a>
              <a href="#" className="sg-btn ghost" style={{ textDecoration: 'none' }}>Read the spec</a>
            </div>
          </div>
          <div style={{ display: 'grid', gap: 14 }}>
            <PromptBlock label="install">
              <span className="d">{'# from PyPI'}</span>{'\n'}
              <span className="k">pip</span> install newsletters
            </PromptBlock>
            <PromptBlock label="synthesize.py">
              <span className="d">{'# one conversation → record, article, letter, episode'}</span>{'\n'}
              <span className="k">from</span> newsletters <span className="k">import</span> synthesize, Corpus{'\n'}{'\n'}
              out = <span className="k">synthesize</span>({'\n'}
              {'  '}event=<span className="a">"latency-regression-2026-06-12"</span>,{'\n'}
              {'  '}sources=[<span className="a">"apm"</span>, <span className="a">"traces"</span>, <span className="a">"logs"</span>, <span className="a">"rum"</span>],{'\n'}
              {'  '}audience=Corpus.<span className="k">load</span>(<span className="a">"maintainers"</span>),{'\n'}
              ){'\n'}
              out.<span className="k">open_pull_request</span>()  <span className="d">{'# human reviews before publish'}</span>
            </PromptBlock>
          </div>
        </div>
      </section>

      {/* ───────────── invitation ───────────── */}
      <section style={{ maxWidth: MW, margin: '0 auto', padding: '64px 44px 8px' }}>
        <div style={{ background: 'var(--color-surface-low)', borderLeft: '3px solid var(--color-accent)', padding: '40px 44px' }}>
          <p style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: 27, lineHeight: 1.32, maxWidth: 640 }}>
            Clone it, point it at your own work, and start publishing what you learn — for your team, your org, or the world.
          </p>
          <div style={{ display: 'flex', gap: 14, marginTop: 26, flexWrap: 'wrap' }}>
            <a href="#" className="sg-btn" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8 }}><IconGit size={13} /> Get started on GitHub</a>
            <a href="#newsletters" className="sg-btn ghost" style={{ textDecoration: 'none' }}>Replay the demo</a>
          </div>
        </div>
      </section>

      <NLFooter maxWidth={MW} />
    </div>
  );
}

window.Home = Home;
