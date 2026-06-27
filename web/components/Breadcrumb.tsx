'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { crumbMap } from '@/lib/data';

const mono = "'DM Mono', monospace";

export function Breadcrumb() {
  const pathname = usePathname();
  const crumb = crumbMap[pathname] ?? '';

  return (
    <nav
      aria-label="Breadcrumb"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 9,
        padding: '11px 22px',
        borderBottom: '1px solid var(--hairline)',
        background: 'var(--low)',
        fontFamily: mono,
        fontSize: 10.5,
        letterSpacing: '.1em',
        textTransform: 'uppercase',
        color: 'var(--muted)',
        overflow: 'hidden',
        whiteSpace: 'nowrap',
      }}
    >
      <Link href="/" data-nav style={{ color: 'var(--muted)', letterSpacing: 'inherit', textTransform: 'inherit' }}>
        Home
      </Link>
      <span style={{ opacity: 0.5 }}>/</span>
      <span style={{ color: 'var(--ink)' }}>{crumb}</span>
    </nav>
  );
}
