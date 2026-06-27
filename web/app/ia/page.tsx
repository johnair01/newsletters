import Link from 'next/link';
import { sitemap, surfaceList } from '@/lib/data';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

const h2 = { fontFamily: mono, fontSize: 12, letterSpacing: '.16em', textTransform: 'uppercase' as const, color: 'var(--text)' };
const section = { borderTop: '2px solid var(--text)', paddingTop: 14 };

export default function IAPage() {
  return (
    <div style={{ padding: '40px 28px 70px', maxWidth: 980, margin: '0 auto' }}>
      <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.2em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 14px' }}>Design round · Information Architecture</p>
      <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(34px,5vw,52px)', lineHeight: 1.04, margin: '0 0 18px', maxWidth: '16ch' }}>Make the fan-out visible.</h1>
      <p style={{ fontSize: 17, lineHeight: 1.6, color: 'var(--text-dim)', maxWidth: '62ch', margin: '0 0 42px' }}>
        One reviewed record fans out into five reader surfaces. The surfaces are well-built in isolation — this round redesigns how they <em style={{ color: 'var(--text)', fontStyle: 'italic' }}>connect</em>: a persistent spine, a lateral fan-out switcher, a first-class claim→evidence trail, and a library you can actually browse.
      </p>

      {/* 01 sitemap */}
      <div style={{ ...section, marginBottom: 48 }}>
        <h2 style={{ ...h2, margin: '0 0 18px' }}>01 · Sitemap</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(200px,1fr))', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
          {sitemap.map((m) => (
            <Link key={m.label} href={m.href} data-nav style={{ textAlign: 'left', background: 'var(--card)', borderLeft: `3px solid ${m.color}`, padding: '15px 16px', color: 'var(--text)' }}>
              <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', display: 'block', marginBottom: 6 }}>{m.kicker}</span>
              <span style={{ fontFamily: serif, fontSize: 19, display: 'block', lineHeight: 1.1 }}>{m.label}</span>
              <span style={{ fontSize: 12.5, color: 'var(--text-dim)', display: 'block', marginTop: 5, lineHeight: 1.4 }}>{m.note}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* 02 cross-link graph */}
      <div style={{ ...section, marginBottom: 10 }}>
        <h2 style={{ ...h2, margin: '0 0 6px' }}>02 · The cross-link graph</h2>
        <p style={{ fontSize: 14.5, lineHeight: 1.55, color: 'var(--text-dim)', maxWidth: '60ch', margin: '0 0 26px' }}>
          One <strong style={{ color: 'var(--text)' }}>record</strong> → many <strong style={{ color: 'var(--text)' }}>surfaces</strong>. Every surface is built of <strong style={{ color: 'var(--text)' }}>claims</strong>; every claim links to its <strong style={{ color: 'var(--text)' }}>evidence</strong>. The onboarding path is an ordered thread across them.
        </p>
        <div style={{ border: '1px solid var(--line)', background: 'var(--card)', padding: '26px 22px' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 8 }}>
            <div style={{ background: 'var(--text)', color: 'var(--bg)', padding: '13px 22px', textAlign: 'center' }}>
              <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.14em', textTransform: 'uppercase', opacity: 0.7, display: 'block', marginBottom: 3 }}>Record · source of truth</span>
              <span style={{ fontFamily: serif, fontSize: 20 }}>The Semantic Spine</span>
            </div>
          </div>
          <div style={{ height: 24, width: 2, background: 'var(--line)', margin: '0 auto' }} />
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center', background: 'var(--line)', border: '1px solid var(--line)' }}>
            {surfaceList.map((s) => (
              <Link key={s.type} href={s.href} data-nav style={{ flex: '1 1 130px', minWidth: 120, background: 'var(--card)', borderTop: `4px solid ${s.color}`, padding: '14px 12px', textAlign: 'center', color: 'var(--text)' }}>
                <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: s.textColor, display: 'block', marginBottom: 5 }}>Surface</span>
                <span style={{ fontFamily: serif, fontSize: 18, display: 'block' }}>{s.label}</span>
                <span style={{ fontSize: 11, color: 'var(--text-dim)', display: 'block', marginTop: 4 }}>{s.claims} claims</span>
              </Link>
            ))}
          </div>
          <p style={{ fontFamily: mono, fontSize: 10.5, letterSpacing: '.06em', color: 'var(--text-dim)', textAlign: 'center', margin: '18px 0 0' }}>
            ↓ each claim ↘ evidence span ↘ back · ⟶ onboarding threads Show → Report → Article → Learning
          </p>
        </div>
      </div>

      {/* 03 global navigation */}
      <div style={{ ...section, margin: '48px 0' }}>
        <h2 style={{ ...h2, margin: '0 0 6px' }}>03 · Global navigation</h2>
        <p style={{ fontSize: 14.5, lineHeight: 1.55, color: 'var(--text-dim)', maxWidth: '60ch', margin: '0 0 22px' }}>
          A persistent near-black spine on every page. Six primary destinations, a jump-to search, breadcrumbs, and a mobile drawer. The spine is always reachable — surfaces are never dead-ends.
        </p>
        <div style={{ border: '1px solid var(--line)', background: 'var(--chrome-bg)', color: 'var(--chrome-fg)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '0 18px', height: 56, flexWrap: 'wrap' }}>
            <span style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
              <span style={{ width: 11, height: 11, background: 'var(--color-brand-primary)', display: 'inline-block' }} />
              <span style={{ fontFamily: serif, fontSize: 19 }}>Signals</span>
            </span>
            <span style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--chrome-fg)', borderBottom: '2px solid var(--color-brand-primary)', paddingBottom: 3 }}>Start here</span>
            {['Library', 'Newsletters', 'Articles', 'The Show', 'Learning'].map((l) => (
              <span key={l} style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--chrome-dim)' }}>{l}</span>
            ))}
            <span style={{ marginLeft: 'auto', fontFamily: mono, fontSize: 10.5, color: 'var(--chrome-dim)', border: '1px solid rgba(255,255,255,.14)', padding: '6px 10px' }}>Jump to… ⌘K</span>
          </div>
        </div>
      </div>

      {/* 04 fan-out switcher treatments */}
      <div style={{ ...section, margin: '48px 0' }}>
        <h2 style={{ ...h2, margin: '0 0 6px' }}>04 · The fan-out switcher <span style={{ color: 'var(--text-dim)' }}>— three treatments</span></h2>
        <p style={{ fontSize: 14.5, lineHeight: 1.55, color: 'var(--text-dim)', maxWidth: '60ch', margin: '0 0 24px' }}>
          The signature control: jump laterally between the surfaces of the <em style={{ color: 'var(--text)', fontStyle: 'italic' }}>same record</em>. Live screens use option A.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
          {/* A: segmented control */}
          <div style={{ background: 'var(--card)', padding: '20px 18px' }}>
            <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 14px' }}>A · Segmented control</p>
            <div style={{ border: '1px solid var(--line)', display: 'flex', flexWrap: 'wrap' }}>
              <span style={{ flex: 1, textAlign: 'center', fontFamily: mono, fontSize: 11, letterSpacing: '.06em', textTransform: 'uppercase', padding: '9px 6px', background: 'var(--text)', color: 'var(--bg)', borderBottom: '3px solid var(--color-brand-primary)' }}>Report</span>
              {['Article', 'News', 'Show', 'Learn'].map((l) => (
                <span key={l} style={{ flex: 1, textAlign: 'center', fontFamily: mono, fontSize: 11, letterSpacing: '.06em', textTransform: 'uppercase', padding: '9px 6px', color: 'var(--text-dim)', borderBottom: '3px solid transparent', borderLeft: '1px solid var(--line)' }}>{l}</span>
              ))}
            </div>
            <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text-dim)', margin: '13px 0 0' }}>Compact, horizontal, reads as one object. Color underline encodes the active surface type.</p>
          </div>
          {/* B: see-this-as strip */}
          <div style={{ background: 'var(--card)', padding: '20px 18px' }}>
            <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 14px' }}>B · “See this as” strip</p>
            <div style={{ borderLeft: '3px solid var(--color-brand-primary)', padding: '4px 0 4px 12px' }}>
              <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', display: 'block', marginBottom: 7 }}>See this record as</span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7 }}>
                <span style={{ fontFamily: mono, fontSize: 11, textTransform: 'uppercase', letterSpacing: '.04em', background: 'var(--text)', color: 'var(--bg)', padding: '4px 9px' }}>Report ✓</span>
                {['Article', 'Newsletter', 'Show', 'Learning'].map((l) => (
                  <span key={l} style={{ fontFamily: mono, fontSize: 11, textTransform: 'uppercase', letterSpacing: '.04em', border: '1px solid var(--line)', color: 'var(--text)', padding: '4px 9px' }}>{l}</span>
                ))}
              </div>
            </div>
            <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text-dim)', margin: '13px 0 0' }}>Editorial, sits under the title. The label spells out the mental model explicitly.</p>
          </div>
          {/* C: sibling rail */}
          <div style={{ background: 'var(--card)', padding: '20px 18px' }}>
            <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 14px' }}>C · Sibling rail</p>
            <div style={{ display: 'flex', flexDirection: 'column', border: '1px solid var(--line)' }}>
              <span style={{ fontFamily: mono, fontSize: 11, textTransform: 'uppercase', letterSpacing: '.05em', padding: '8px 10px', borderLeft: '3px solid var(--color-brand-primary)', background: 'var(--color-surface-low)', color: 'var(--text)' }}>Report</span>
              {[['Article', 'var(--text)'], ['Newsletter', 'var(--color-amber)'], ['Show', 'var(--color-accent)'], ['Learning', 'var(--color-green)']].map(([l, c]) => (
                <span key={l} style={{ fontFamily: mono, fontSize: 11, textTransform: 'uppercase', letterSpacing: '.05em', padding: '8px 10px', borderLeft: `3px solid ${c}`, color: 'var(--text-dim)', borderTop: '1px solid var(--line)' }}>{l}</span>
              ))}
            </div>
            <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text-dim)', margin: '13px 0 0' }}>Vertical, parks in the margin on wide screens. Best when surfaces are long-scroll.</p>
          </div>
        </div>
      </div>

      {/* 05 provenance treatments */}
      <div style={{ ...section, margin: '48px 0 0' }}>
        <h2 style={{ ...h2, margin: '0 0 6px' }}>05 · The provenance pattern <span style={{ color: 'var(--text-dim)' }}>— two treatments</span></h2>
        <p style={{ fontSize: 14.5, lineHeight: 1.55, color: 'var(--text-dim)', maxWidth: '60ch', margin: '0 0 24px' }}>
          Claim → evidence → back, as one repeatable affordance. Live Report uses option A (slide-in panel).
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
          {/* A: slide-in panel */}
          <div style={{ background: 'var(--card)', padding: '20px 18px' }}>
            <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 14px' }}>A · Slide-in evidence panel</p>
            <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text)', margin: '0 0 14px' }}>
              Every published claim links to its source evidence<sup style={{ fontFamily: mono, fontSize: 10, color: 'var(--bg)', background: 'var(--color-brand-primary)', padding: '1px 5px', marginLeft: 3 }}>EV</sup>.
            </p>
            <div style={{ borderLeft: '3px solid var(--color-brand-primary)', background: 'var(--color-surface-low)', padding: '11px 13px' }}>
              <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', display: 'block', marginBottom: 6 }}>Evidence · The Show 00:21:08 →</span>
              <span style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text-dim)', fontStyle: 'italic' }}>“…nothing ships unless the claim points back at a span…”</span>
              <span style={{ fontFamily: mono, fontSize: 10, color: 'var(--color-brand-primary)', display: 'block', marginTop: 9 }}>← Back to claim</span>
            </div>
            <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text-dim)', margin: '13px 0 0' }}>Reader stays in place; evidence opens beside the claim, with a clear return.</p>
          </div>
          {/* B: jump + breadcrumb return */}
          <div style={{ background: 'var(--card)', padding: '20px 18px' }}>
            <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 14px' }}>B · Jump to highlighted span</p>
            <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text)', margin: '0 0 14px' }}>
              The claim is a <span style={{ color: 'var(--color-brand-primary)', borderBottom: '2px solid var(--color-brand-primary)' }}>link</span> that jumps to its source, highlighted in context.
            </p>
            <div style={{ border: '1px solid var(--line)', padding: '11px 13px' }}>
              <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text-dim)', display: 'block', marginBottom: 7 }}>Report · §3.2</span>
              <span style={{ fontSize: 12.5, lineHeight: 1.55, color: 'var(--text-dim)' }}>…the gate is <mark style={{ background: 'var(--color-amber)', color: 'var(--text)', padding: '0 2px' }}>Draft → In Review → Published</mark>, and a human signs…</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginTop: 11, fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
              <span style={{ color: 'var(--color-brand-primary)' }}>← Back to Article</span><span style={{ opacity: 0.5 }}>where you came from</span>
            </div>
            <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--text-dim)', margin: '13px 0 0' }}>Full context of the source; a breadcrumb returns you to the citing surface.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
