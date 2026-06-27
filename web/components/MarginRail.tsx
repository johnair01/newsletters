'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { surfaceList } from '@/lib/data';

const mono = "'DM Mono', monospace";

/** Sibling-surfaces rail + provenance legend (parks in the margin on wide screens). */
export function MarginRail() {
  const pathname = usePathname();

  return (
    <aside className="rail-aside" style={{ flexDirection: 'column', gap: 20, position: 'sticky', top: 132 }}>
      <div style={{ border: '1px solid var(--hairline)', background: 'var(--card)' }}>
        <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--muted)', margin: 0, padding: '12px 14px 10px', borderBottom: '1px solid var(--hairline)' }}>
          Sibling surfaces
        </p>
        {surfaceList.map((s) => {
          const active = pathname === s.href;
          return (
            <Link
              key={s.type}
              href={s.href}
              data-nav
              aria-current={active ? 'page' : undefined}
              style={{
                width: '100%',
                textAlign: 'left',
                background: active ? 'var(--low)' : 'var(--card)',
                borderLeft: `3px solid ${s.color}`,
                borderTop: '1px solid var(--hairline)',
                padding: '10px 13px',
                color: 'var(--ink)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span style={{ fontFamily: mono, fontSize: 11, textTransform: 'uppercase', letterSpacing: '.04em' }}>{s.label}</span>
              <span style={{ fontFamily: mono, fontSize: 10, color: 'var(--muted)' }}>{active ? '● here' : '→'}</span>
            </Link>
          );
        })}
      </div>
      <div style={{ borderLeft: '3px solid var(--blue)', padding: '4px 0 4px 13px' }}>
        <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.1em', textTransform: 'uppercase', color: 'var(--blue)', margin: '0 0 6px' }}>Provenance</p>
        <p style={{ fontSize: 12.5, lineHeight: 1.5, color: 'var(--muted)', margin: 0 }}>
          Tap any <span style={{ fontFamily: mono, fontSize: 9.5, color: 'var(--paper)', background: 'var(--blue)', padding: '1px 5px' }}>EV</span> to open the source span. Close to return.
        </p>
      </div>
    </aside>
  );
}
