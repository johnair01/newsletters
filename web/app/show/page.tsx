import Link from 'next/link';
import { FanoutSwitcher } from '@/components/FanoutSwitcher';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function ShowPage() {
  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '0 28px' }}>
      <div style={{ padding: '34px 0 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-paper)', background: 'var(--color-accent-ink)', padding: '4px 10px' }}>The Show</span>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Ep.01 · the source conversation</span>
        </div>
        <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(30px,4.4vw,46px)', lineHeight: 1.05, margin: '0 0 6px', maxWidth: '20ch' }}>
          Where the record actually started.
        </h1>
        <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.06em', color: 'var(--text-dim)', margin: '0 0 22px' }}>
          Episode 01 · 38 min · transcript below feeds the record
        </p>
      </div>

      <FanoutSwitcher />

      {/* player (decorative — no audio) */}
      <div style={{ background: 'var(--text)', color: 'var(--color-paper)', padding: 22, margin: '18px 0 26px', display: 'flex', alignItems: 'center', gap: 18, flexWrap: 'wrap' }}>
        <button type="button" aria-label="Play episode" style={{ width: 52, height: 52, borderRadius: '50%', background: 'var(--color-accent)', border: 0, color: 'var(--color-paper)', fontSize: 18, flex: 'none' }}>▶</button>
        <div style={{ flex: 1, minWidth: 160 }}>
          <div style={{ height: 4, background: 'rgba(255,255,255,.2)', position: 'relative' }}>
            <span style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '36%', background: 'var(--color-accent)' }} />
          </div>
          <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.06em', color: 'rgba(255,255,255,.6)', margin: '8px 0 0' }}>00:14:22 / 00:38:40</p>
        </div>
      </div>

      {/* transcript with cited span */}
      <div style={{ maxWidth: '64ch', paddingBottom: 70 }}>
        <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 14px' }}>Transcript</p>
        <div style={{ display: 'flex', gap: 14, marginBottom: 16 }}>
          <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--color-accent-ink)', flex: 'none', width: 62 }}>00:14:22</span>
          <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--text)', margin: 0 }}>
            <mark style={{ background: 'var(--color-amber)', color: 'var(--text)', padding: '0 3px' }}>…we keep one reviewed record and re-cut it per audience rather than rewriting facts five times…</mark> That&apos;s the whole bet.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 14, marginBottom: 16 }}>
          <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--color-accent-ink)', flex: 'none', width: 62 }}>00:21:08</span>
          <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--text-dim)', margin: 0 }}>…nothing ships unless the claim points back at a span in the record or transcript…</p>
        </div>
        <p style={{ fontSize: 15, lineHeight: 1.65, color: 'var(--text-dim)', borderTop: '1px solid var(--line)', paddingTop: 18, marginTop: 8 }}>
          This transcript is the evidence behind the{' '}
          <Link href="/report" data-nav style={{ borderBottom: '2px solid var(--color-brand-primary)', color: 'var(--color-brand-primary)' }}>Report&apos;s</Link> claims. That&apos;s why claim links land here.
        </p>
      </div>
    </div>
  );
}
