import Link from 'next/link';
import { footerCols } from '@/lib/data';

const mono = "'DM Mono', monospace";

export function Footer() {
  return (
    <footer style={{ background: 'var(--chrome)', color: 'var(--chrome-text)', padding: '40px 22px 34px' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '34px 60px' }}>
        <div style={{ flex: '1 1 220px' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 12 }}>
            <span style={{ width: 11, height: 11, background: 'var(--blue)', display: 'inline-block' }} />
            <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: 20 }}>Signals</span>
          </div>
          <p style={{ fontSize: 13.5, lineHeight: 1.55, color: 'var(--chrome-muted)', maxWidth: '34ch', margin: 0 }}>
            One reviewed record, told for every reader. Every claim traces to its source.
          </p>
        </div>

        {footerCols.map((col) => (
          <div key={col.head} style={{ flex: '0 1 auto' }}>
            <p style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--chrome-muted)', margin: '0 0 13px' }}>
              {col.head}
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 9 }}>
              {col.links.map((l) => (
                <Link
                  key={l.label}
                  href={l.href}
                  data-nav
                  style={{ textAlign: 'left', color: 'var(--chrome-text)', fontFamily: "'Instrument Sans', sans-serif", fontSize: 13.5, opacity: 0.85 }}
                >
                  {l.label}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          borderTop: '1px solid rgba(255,255,255,.12)',
          marginTop: 30,
          paddingTop: 16,
          display: 'flex',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 10,
          fontFamily: mono,
          fontSize: 10,
          letterSpacing: '.08em',
          textTransform: 'uppercase',
          color: 'var(--chrome-muted)',
        }}
      >
        <span>© Signals — reviewed record system</span>
        <span>Draft · In Review · Published — review gate on every surface</span>
      </div>
    </footer>
  );
}
