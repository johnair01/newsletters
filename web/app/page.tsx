import Link from 'next/link';
import { surfaceList } from '@/lib/data';

const mono = "'DM Mono', monospace";
const serif = "'DM Serif Display', serif";

export default function HomePage() {
  return (
    <div>
      {/* hero */}
      <div style={{ padding: '64px 28px 54px', maxWidth: 900, margin: '0 auto', borderBottom: '1px solid var(--line)' }}>
        <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.2em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 18px' }}>
          One record · five surfaces · every claim traced
        </p>
        <h1 style={{ fontFamily: serif, fontWeight: 400, fontSize: 'clamp(38px,6vw,68px)', lineHeight: 1.02, margin: '0 0 22px', maxWidth: '14ch' }}>
          The record, told for every reader.
        </h1>
        <p style={{ fontSize: 18, lineHeight: 1.6, color: 'var(--text-dim)', maxWidth: '54ch', margin: '0 0 30px' }}>
          Signals turns the messy record of how work gets done into trustworthy, audience-tuned stories. Read it as a Report, an Article, a Newsletter, a Show, or a Learning re-cut — same evidence underneath.
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
          <Link href="/onboarding" data-nav style={{ fontFamily: mono, fontSize: 12, letterSpacing: '.1em', textTransform: 'uppercase', background: 'var(--text)', color: 'var(--color-paper)', padding: '14px 22px' }}>
            Start here →
          </Link>
          <Link href="/library" data-nav style={{ fontFamily: mono, fontSize: 12, letterSpacing: '.1em', textTransform: 'uppercase', background: 'transparent', color: 'var(--text)', border: '1px solid var(--text)', padding: '14px 22px' }}>
            Browse the library
          </Link>
        </div>
      </div>

      {/* the fan-out, explained */}
      <div style={{ padding: '48px 28px', maxWidth: 980, margin: '0 auto' }}>
        <p style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 6px' }}>How it works</p>
        <h2 style={{ fontFamily: serif, fontWeight: 400, fontSize: 30, margin: '0 0 26px' }}>One reviewed record fans out.</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(168px,1fr))', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
          {surfaceList.map((s) => (
            <Link
              key={s.type}
              href={s.href}
              data-nav
              style={{ textAlign: 'left', background: 'var(--card)', borderTop: `4px solid ${s.color}`, padding: '20px 16px', color: 'var(--text)', minHeight: 148, display: 'flex', flexDirection: 'column' }}
            >
              <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: s.textColor, marginBottom: 9 }}>Surface</span>
              <span style={{ fontFamily: serif, fontSize: 23, lineHeight: 1.05, marginBottom: 6 }}>{s.label}</span>
              <span style={{ fontSize: 12.5, lineHeight: 1.45, color: 'var(--text-dim)', marginTop: 'auto' }}>{s.claims} claims · enter →</span>
            </Link>
          ))}
        </div>
      </div>

      {/* start-here journey + principles */}
      <div style={{ padding: '8px 28px 60px', maxWidth: 980, margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: 30 }}>
        <div style={{ borderLeft: '3px solid var(--color-green)', padding: '6px 0 6px 18px' }}>
          <p style={{ fontFamily: mono, fontSize: 10.5, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-green)', margin: '0 0 12px' }}>New here? Read in order</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--line)', border: '1px solid var(--line)' }}>
            <Link href="/show" data-nav style={{ textAlign: 'left', background: 'var(--card)', padding: '13px 15px', display: 'flex', gap: 13, alignItems: 'baseline', color: 'var(--text)' }}>
              <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--text-dim)' }}>01</span><span style={{ fontSize: 14.5 }}>Listen to the source conversation</span>
            </Link>
            <Link href="/report" data-nav style={{ textAlign: 'left', background: 'var(--card)', padding: '13px 15px', display: 'flex', gap: 13, alignItems: 'baseline', color: 'var(--text)' }}>
              <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--text-dim)' }}>02</span><span style={{ fontSize: 14.5 }}>Read the reviewed Report</span>
            </Link>
            <Link href="/learning" data-nav style={{ textAlign: 'left', background: 'var(--card)', padding: '13px 15px', display: 'flex', gap: 13, alignItems: 'baseline', color: 'var(--text)' }}>
              <span style={{ fontFamily: mono, fontSize: 11, color: 'var(--text-dim)' }}>03</span><span style={{ fontSize: 14.5 }}>Or start with the gentle re-cut</span>
            </Link>
          </div>
          <Link href="/onboarding" data-nav style={{ display: 'inline-block', marginTop: 14, fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--color-green)' }}>
            Open the guided path →
          </Link>
        </div>
        <div style={{ borderLeft: '3px solid var(--color-brand-primary)', padding: '6px 0 6px 18px' }}>
          <p style={{ fontFamily: mono, fontSize: 10.5, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 12px' }}>The promise</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <p style={{ fontFamily: serif, fontSize: 18, margin: '0 0 4px' }}>Every claim is traced.</p>
              <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--text-dim)', margin: 0 }}>Click any claim to see the exact source span it came from, then click back.</p>
            </div>
            <div>
              <p style={{ fontFamily: serif, fontSize: 18, margin: '0 0 4px' }}>Nothing ships unreviewed.</p>
              <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--text-dim)', margin: 0 }}>A visible Draft → In Review → Published gate sits on every surface.</p>
            </div>
            <div>
              <p style={{ fontFamily: serif, fontSize: 18, margin: '0 0 4px' }}>Move sideways, freely.</p>
              <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--text-dim)', margin: 0 }}>The fan-out switcher jumps you between surfaces of the same record.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
