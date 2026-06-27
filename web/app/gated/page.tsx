import Link from 'next/link';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function GatedPage() {
  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: '0 28px' }}>
      <div style={{ padding: '34px 0 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-paper)', background: 'var(--color-brand-primary)', padding: '4px 10px' }}>Report</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)', border: '1px solid var(--text-dim)', padding: '3px 9px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--text-dim)', borderRadius: '50%', display: 'inline-block' }} />Draft
          </span>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Record · Review Round 1</span>
        </div>
        <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(30px,4.4vw,46px)', lineHeight: 1.05, margin: '0 0 22px', maxWidth: '20ch' }}>
          First evidence audit — open threads before publish.
        </h1>
      </div>

      {/* review gate notice */}
      <div style={{ border: '1px solid var(--line)', borderLeft: '4px solid var(--color-amber)', background: 'var(--card)', padding: '26px 24px', marginBottom: 24 }}>
        <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-amber-ink)', margin: '0 0 14px' }}>Held at the review gate</p>
        <p style={{ fontSize: 17, lineHeight: 1.65, color: 'var(--text)', margin: '0 0 18px', maxWidth: '52ch' }}>
          This surface is still a <strong>Draft</strong>. Nothing publishes without human review, so its claims aren&apos;t readable yet — and they can&apos;t be cited from other surfaces until they clear the gate.
        </p>
        {/* gate progress */}
        <div style={{ display: 'flex', alignItems: 'stretch', border: '1px solid var(--line)', marginBottom: 6 }}>
          <div style={{ flex: 1, padding: '11px 12px', background: 'var(--color-surface-low)', borderRight: '1px solid var(--line)', textAlign: 'center' }}>
            <span style={{ fontFamily: mono, fontSize: 9, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text)', display: 'block' }}>● Draft</span>
            <span style={{ fontFamily: mono, fontSize: 9, color: 'var(--text-dim)' }}>you are here</span>
          </div>
          <div style={{ flex: 1, padding: '11px 12px', borderRight: '1px solid var(--line)', textAlign: 'center' }}>
            <span style={{ fontFamily: mono, fontSize: 9, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text-dim)', display: 'block' }}>○ In Review</span>
            <span style={{ fontFamily: mono, fontSize: 9, color: 'var(--text-dim)' }}>next</span>
          </div>
          <div style={{ flex: 1, padding: '11px 12px', textAlign: 'center' }}>
            <span style={{ fontFamily: mono, fontSize: 9, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text-dim)', display: 'block' }}>○ Published</span>
            <span style={{ fontFamily: mono, fontSize: 9, color: 'var(--text-dim)' }}>readable</span>
          </div>
        </div>
      </div>

      {/* what you can still do */}
      <div style={{ paddingBottom: 70 }}>
        <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 14px' }}>While it&apos;s in draft, you can still</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
          <Link href="/report" data-nav style={{ textAlign: 'left', background: 'var(--card)', borderLeft: '3px solid var(--color-brand-primary)', padding: '15px 16px', color: 'var(--text)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
            <span>
              <span style={{ fontFamily: serif, fontSize: 18, display: 'block' }}>Read the published record it audits</span>
              <span style={{ fontSize: 13, color: 'var(--text-dim)' }}>The Semantic Spine · Report</span>
            </span>
            <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--text-dim)' }}>→</span>
          </Link>
          <Link href="/library" data-nav style={{ textAlign: 'left', background: 'var(--card)', borderLeft: '3px solid var(--text)', padding: '15px 16px', color: 'var(--text)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
            <span>
              <span style={{ fontFamily: serif, fontSize: 18, display: 'block' }}>Back to the library</span>
              <span style={{ fontSize: 13, color: 'var(--text-dim)' }}>Browse published records by topic</span>
            </span>
            <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--text-dim)' }}>→</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
