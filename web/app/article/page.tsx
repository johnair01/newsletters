import Link from 'next/link';
import { FanoutSwitcher } from '@/components/FanoutSwitcher';
import { EvButton } from '@/components/EvButton';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function ArticlePage() {
  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '0 28px' }}>
      <div style={{ padding: '34px 0 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-paper)', background: 'var(--text)', padding: '4px 10px' }}>Article</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-green)', border: '1px solid var(--color-green)', padding: '3px 9px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--color-green)', borderRadius: '50%', display: 'inline-block' }} />Published · peer-reviewed
          </span>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Record · The Semantic Spine</span>
        </div>
        <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(32px,4.6vw,48px)', lineHeight: 1.04, margin: '0 0 6px', maxWidth: '20ch' }}>
          The Semantic Spine: a traceable record for many readers.
        </h1>
        <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.06em', color: 'var(--text-dim)', margin: '0 0 22px' }}>Article · 6 claims · 9 citations</p>
      </div>

      <FanoutSwitcher />

      <div style={{ maxWidth: '62ch', padding: '24px 0 70px' }}>
        <p style={{ fontFamily: serif, fontStyle: 'italic', fontSize: 21, lineHeight: 1.5, color: 'var(--text)', margin: '0 0 24px' }}>
          Abstract — A single reviewed record can serve five distinct audiences without duplicating or drifting from its evidence.
        </p>
        <p style={{ fontSize: 17, lineHeight: 1.75, color: 'var(--text)', margin: '0 0 20px' }}>
          We argue that audience-tuning belongs at the surface layer, not the fact layer. Each claim in this article cites the same spine the Report is built from
          <EvButton id="e1" bg="var(--text)" />, which is what keeps the Newsletter, Show, and Learning re-cuts mutually consistent.
        </p>
        <p style={{ fontSize: 17, lineHeight: 1.75, color: 'var(--text)', margin: '0 0 20px' }}>
          Provenance is not a footnote convenience; it is the contract. A claim with no traceable span cannot publish
          <EvButton id="e2" bg="var(--text)" />.
        </p>
        <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--text-dim)', margin: '26px 0 0', borderTop: '1px solid var(--line)', paddingTop: 20 }}>
          Prefer it lighter? Read the same record as the{' '}
          <Link href="/learning" data-nav style={{ borderBottom: '2px solid var(--color-green)', color: 'var(--color-green)' }}>Learning re-cut →</Link>
        </p>
      </div>
    </div>
  );
}
