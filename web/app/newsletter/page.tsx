import Link from 'next/link';
import { FanoutSwitcher } from '@/components/FanoutSwitcher';
import { EvButton } from '@/components/EvButton';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function NewsletterPage() {
  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: '0 28px' }}>
      <div style={{ padding: '34px 0 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--text)', background: 'var(--color-amber)', padding: '4px 10px' }}>Newsletter</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-green)', border: '1px solid var(--color-green)', padding: '3px 9px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--color-green)', borderRadius: '50%', display: 'inline-block' }} />Published
          </span>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>For · the newcomer</span>
        </div>
        <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(30px,4.4vw,44px)', lineHeight: 1.06, margin: '0 0 6px' }}>
          What the spine means for you this week.
        </h1>
        <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.06em', color: 'var(--text-dim)', margin: '0 0 22px' }}>Newsletter · per-reader digest · 4 claims</p>
      </div>

      <FanoutSwitcher />

      {/* per-reader picker */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', padding: '18px 0 8px' }}>
        <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--text-dim)', alignSelf: 'center' }}>Edition</span>
        <span style={{ fontFamily: mono, fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.04em', background: 'var(--text)', color: 'var(--color-paper)', padding: '4px 10px' }}>Newcomer ✓</span>
        <span style={{ fontFamily: mono, fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.04em', border: '1px solid var(--line)', color: 'var(--text)', padding: '4px 10px' }}>For JJ</span>
        <span style={{ fontFamily: mono, fontSize: 10.5, textTransform: 'uppercase', letterSpacing: '.04em', border: '1px solid var(--line)', color: 'var(--text)', padding: '4px 10px' }}>For Nate</span>
      </div>

      <div style={{ padding: '14px 0 70px' }}>
        <div style={{ borderLeft: '3px solid var(--color-amber)', padding: '2px 0 2px 18px', margin: '0 0 22px' }}>
          <p style={{ fontSize: 17, lineHeight: 1.65, color: 'var(--text)', margin: 0 }}>
            The headline this week: one record now powers all five surfaces, and you can move between them freely.
            <EvButton id="e1" bg="var(--color-amber)" fg="var(--text)" />
          </p>
        </div>
        <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--text-dim)', margin: 0 }}>
          Want the full argument? Read the{' '}
          <Link href="/article" data-nav style={{ borderBottom: '2px solid var(--text)', color: 'var(--text)' }}>Article →</Link>
        </p>
      </div>
    </div>
  );
}
