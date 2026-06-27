'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { surfaceList } from '@/lib/data';

const mono = "'DM Mono', monospace";

/**
 * The signature fan-out control (shipped treatment A: segmented control).
 * Jump laterally between the five surfaces of the *same record* without
 * losing context. The active segment carries the surface's accent underline.
 * Sticky just beneath the global header.
 */
export function FanoutSwitcher() {
  const pathname = usePathname();

  return (
    <div
      style={{
        position: 'sticky',
        top: 62,
        zIndex: 20,
        background: 'var(--bg)',
        padding: '10px 0 12px',
        borderBottom: '1px solid var(--line)',
        marginBottom: 8,
      }}
    >
      <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--text-dim)', display: 'block', marginBottom: 8 }}>
        See this record as
      </span>
      <div style={{ display: 'flex', border: '1px solid var(--text)', flexWrap: 'wrap' }}>
        {surfaceList.map((s, i) => {
          const active = pathname === s.href;
          return (
            <Link
              key={s.type}
              href={s.href}
              data-nav
              aria-current={active ? 'page' : undefined}
              style={{
                flex: '1 1 0',
                minWidth: 84,
                textAlign: 'center',
                fontFamily: mono,
                fontSize: 11,
                letterSpacing: '.05em',
                textTransform: 'uppercase',
                borderLeft: i === 0 ? '0' : '1px solid var(--text)',
                padding: '10px 8px',
                background: active ? 'var(--text)' : 'transparent',
                color: active ? 'var(--color-paper)' : 'var(--text-dim)',
                borderBottom: `3px solid ${active ? s.color : 'transparent'}`,
              }}
            >
              {s.label}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
