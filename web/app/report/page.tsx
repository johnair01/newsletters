import Link from 'next/link';
import { FanoutSwitcher } from '@/components/FanoutSwitcher';
import { MarginRail } from '@/components/MarginRail';
import { EvButton } from '@/components/EvButton';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function ReportPage() {
  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '0 28px' }}>
      {/* surface header */}
      <div style={{ padding: '34px 0 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-paper)', background: 'var(--color-brand-primary)', padding: '4px 10px' }}>Report</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-green)', border: '1px solid var(--color-green)', padding: '3px 9px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--color-green)', borderRadius: '50%', display: 'inline-block' }} />Published
          </span>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Record · The Semantic Spine</span>
        </div>
        <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(32px,4.6vw,48px)', lineHeight: 1.04, margin: '0 0 6px', maxWidth: '20ch' }}>
          The data model that keeps every surface honest.
        </h1>
        <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.06em', color: 'var(--text-dim)', margin: '0 0 22px' }}>
          Reviewed record · 9 claims · last signed off 3 days ago
        </p>
      </div>

      <FanoutSwitcher />

      {/* body: claims + margin rail */}
      <div className="rail-grid" style={{ padding: '24px 0 70px' }}>
        <div style={{ maxWidth: '66ch' }}>
          <p style={{ fontSize: 17, lineHeight: 1.7, color: 'var(--text)', margin: '0 0 22px' }}>
            A surface is only as trustworthy as the record beneath it. This report defines that record — the semantic spine every Article, Newsletter, Show, and Learning re-cut is generated from.
          </p>

          <div style={{ borderLeft: '3px solid var(--line)', padding: '2px 0 2px 18px', margin: '0 0 22px' }}>
            <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 7px' }}>Claim 01</p>
            <p style={{ fontSize: 17, lineHeight: 1.65, color: 'var(--text)', margin: 0 }}>
              One record fans out into five reader surfaces, rather than five facts written five times.
              <EvButton id="e1" />
            </p>
          </div>

          <div style={{ borderLeft: '3px solid var(--line)', padding: '2px 0 2px 18px', margin: '0 0 22px' }}>
            <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 7px' }}>Claim 02</p>
            <p style={{ fontSize: 17, lineHeight: 1.65, color: 'var(--text)', margin: 0 }}>
              Every published claim links to its source evidence — a span in the record or transcript.
              <EvButton id="e2" />
            </p>
          </div>

          <div style={{ borderLeft: '3px solid var(--line)', padding: '2px 0 2px 18px', margin: '0 0 22px' }}>
            <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 7px' }}>Claim 03</p>
            <p style={{ fontSize: 17, lineHeight: 1.65, color: 'var(--text)', margin: 0 }}>
              Nothing publishes without human review; the gate is Draft → In Review → Published.
              <EvButton id="e3" />
            </p>
          </div>

          <p style={{ fontSize: 16, lineHeight: 1.7, color: 'var(--text-dim)', margin: '26px 0 0', borderTop: '1px solid var(--line)', paddingTop: 20 }}>
            Continue laterally: read the same record as the peer-reviewed{' '}
            <Link href="/article" data-nav style={{ borderBottom: '2px solid var(--text)', color: 'var(--text)' }}>Article</Link>, or the newcomer{' '}
            <Link href="/learning" data-nav style={{ borderBottom: '2px solid var(--color-green)', color: 'var(--color-green)' }}>Learning re-cut</Link>.
          </p>
        </div>

        <MarginRail />
      </div>
    </div>
  );
}
