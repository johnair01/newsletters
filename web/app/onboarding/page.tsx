'use client';

import { useState } from 'react';
import Link from 'next/link';
import { onboardingSteps } from '@/lib/data';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function OnboardingPage() {
  const [step, setStep] = useState(0);
  const total = onboardingSteps.length;
  const cur = onboardingSteps[step];
  const atStart = step === 0;
  const atEnd = step === total - 1;

  return (
    <div style={{ maxWidth: 880, margin: '0 auto', padding: '34px 28px 70px' }}>
      <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.2em', textTransform: 'uppercase', color: 'var(--color-green)', margin: '0 0 12px' }}>Guided reading path</p>
      <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(32px,4.6vw,46px)', lineHeight: 1.04, margin: '0 0 24px' }}>Start here.</h1>

      {/* progress */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
        {onboardingSteps.map((s, i) => (
          <div key={s.surface} style={{ flex: 1, height: 5, background: i <= step ? 'var(--color-green)' : 'var(--line)' }} />
        ))}
      </div>
      <p style={{ fontFamily: mono, fontSize: 10.5, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 28px' }}>
        Step {step + 1} of {total}
      </p>

      {/* current step card */}
      <div style={{ border: '1px solid var(--line)', borderLeft: `4px solid ${cur.color}`, background: 'var(--card)', padding: '30px 28px', marginBottom: 24 }}>
        <p style={{ fontFamily: mono, fontSize: 10.5, letterSpacing: '.14em', textTransform: 'uppercase', color: cur.color, margin: '0 0 14px' }}>{cur.kicker}</p>
        <h2 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(26px,3.4vw,36px)', lineHeight: 1.08, margin: '0 0 14px' }}>{cur.title}</h2>
        <p style={{ fontSize: 17, lineHeight: 1.65, color: 'var(--text-dim)', margin: '0 0 24px', maxWidth: '54ch' }}>{cur.blurb}</p>
        <Link href={cur.href} data-nav style={{ display: 'inline-block', fontFamily: mono, fontSize: 11, letterSpacing: '.1em', textTransform: 'uppercase', background: 'var(--text)', color: 'var(--color-paper)', padding: '13px 20px' }}>
          Open this surface →
        </Link>
      </div>

      {/* prev / next */}
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, borderTop: '1px solid var(--line)', paddingTop: 18 }}>
        <button
          type="button"
          data-nav
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={atStart}
          style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', background: 'transparent', border: '1px solid var(--text)', color: 'var(--text)', padding: '12px 18px', opacity: atStart ? 0.4 : 1 }}
        >
          ← Previous
        </button>
        <button
          type="button"
          data-nav
          onClick={() => setStep((s) => Math.min(total - 1, s + 1))}
          disabled={atEnd}
          style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', background: 'var(--color-green)', border: 0, color: 'var(--color-paper)', padding: '12px 18px', opacity: atEnd ? 0.4 : 1 }}
        >
          Next step →
        </button>
      </div>

      {/* step list */}
      <div style={{ marginTop: 34, display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
        {onboardingSteps.map((s, i) => (
          <button
            key={s.surface}
            type="button"
            data-nav
            onClick={() => setStep(i)}
            style={{ textAlign: 'left', background: i === step ? 'var(--color-surface-low)' : 'var(--card)', border: 0, borderLeft: `3px solid ${s.color}`, padding: '13px 16px', display: 'flex', gap: 14, alignItems: 'center', color: 'var(--text)' }}
          >
            <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--text-dim)' }}>{String(i + 1).padStart(2, '0')}</span>
            <span style={{ fontFamily: serif, fontSize: 17, flex: 1 }}>{s.title}</span>
            <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
              {i === step ? '● now' : i < step ? 'done' : '→'}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
