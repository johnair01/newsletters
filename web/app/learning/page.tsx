import Link from 'next/link';
import { FanoutSwitcher } from '@/components/FanoutSwitcher';
import { EvButton } from '@/components/EvButton';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function LearningPage() {
  return (
    <div style={{ maxWidth: 1040, margin: '0 auto', padding: '0 28px' }}>
      <div style={{ padding: '34px 0 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-paper)', background: 'var(--color-green)', padding: '4px 10px' }}>Learning</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-green)', border: '1px solid var(--color-green)', padding: '3px 9px' }}>
            <span style={{ width: 7, height: 7, background: 'var(--color-green)', borderRadius: '50%', display: 'inline-block' }} />Published · newcomer re-cut
          </span>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>Record · The Semantic Spine</span>
        </div>
        <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(32px,4.6vw,48px)', lineHeight: 1.04, margin: '0 0 6px', maxWidth: '18ch' }}>
          Start here: what “the spine” actually means.
        </h1>
        <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.06em', color: 'var(--text-dim)', margin: '0 0 22px' }}>Learning · re-cut of the Report · ~6 min read</p>
      </div>

      <FanoutSwitcher />

      <div className="rail-grid" style={{ padding: '24px 0 70px' }}>
        <div style={{ maxWidth: '62ch' }}>
          <p style={{ fontSize: 18, lineHeight: 1.75, color: 'var(--text)', margin: '0 0 22px' }}>
            New to all this? Read it plainly. A <strong style={{ borderBottom: '2px dotted var(--color-green)' }}>record</strong> is the single, checked version of what happened. Everything you read on Signals is just that record, re-told for a different reader.
          </p>
          <div style={{ borderLeft: '3px solid var(--color-green)', background: 'var(--color-surface-low)', padding: '16px 18px', margin: '0 0 24px' }}>
            <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--color-green)', margin: '0 0 8px' }}>In one sentence</p>
            <p style={{ fontSize: 17, lineHeight: 1.55, color: 'var(--text)', margin: 0 }}>One checked record → five ways to read it → every sentence shows its source.</p>
          </div>
          <p style={{ fontSize: 17, lineHeight: 1.75, color: 'var(--text)', margin: '0 0 20px' }}>
            When you see an <EvButton id="e1" bg="var(--color-green)" label="EV" superscript={false} /> marker, tap it — it shows you exactly where that fact came from, then brings you right back.
          </p>
        </div>

        <aside className="rail-aside" style={{ flexDirection: 'column', gap: 16, position: 'sticky', top: 132 }}>
          <div style={{ border: '1px solid var(--line)', background: 'var(--card)', padding: '14px 15px' }}>
            <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--color-green)', margin: '0 0 11px' }}>Glossary</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 11 }}>
              <div>
                <p style={{ fontFamily: serif, fontSize: 16, margin: 0 }}>Record</p>
                <p style={{ fontSize: 12.5, lineHeight: 1.45, color: 'var(--text-dim)', margin: '2px 0 0' }}>The checked source of truth.</p>
              </div>
              <div>
                <p style={{ fontFamily: serif, fontSize: 16, margin: 0 }}>Surface</p>
                <p style={{ fontSize: 12.5, lineHeight: 1.45, color: 'var(--text-dim)', margin: '2px 0 0' }}>One way of reading the record.</p>
              </div>
              <div>
                <p style={{ fontFamily: serif, fontSize: 16, margin: 0 }}>Evidence</p>
                <p style={{ fontSize: 12.5, lineHeight: 1.45, color: 'var(--text-dim)', margin: '2px 0 0' }}>Where a claim came from.</p>
              </div>
            </div>
          </div>
          <Link href="/onboarding" data-nav style={{ textAlign: 'left', background: 'var(--color-green)', color: 'var(--color-paper)', padding: '14px 15px' }}>
            <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.08em', textTransform: 'uppercase', display: 'block', marginBottom: 4, opacity: 0.85 }}>Guided</span>
            <span style={{ fontFamily: serif, fontSize: 18 }}>Take the path →</span>
          </Link>
        </aside>
      </div>
    </div>
  );
}
