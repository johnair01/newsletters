'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { navSpine } from '@/lib/data';
import { useSignals } from './SignalsProvider';

const mono = "'DM Mono', monospace";

export function Nav() {
  const pathname = usePathname();
  const { drawerOpen, setDrawerOpen, openPalette } = useSignals();

  return (
    <header style={{ background: 'var(--chrome-bg)', color: 'var(--chrome-fg)', position: 'sticky', top: 0, zIndex: 40 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 20, padding: '0 22px', height: 62 }}>
        <Link
          href="/"
          data-nav
          aria-label="Signals — home"
          style={{ display: 'flex', alignItems: 'baseline', gap: 9, color: 'var(--chrome-fg)' }}
        >
          <span style={{ width: 13, height: 13, background: 'var(--color-brand-primary)', display: 'inline-block' }} />
          <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, lineHeight: 1 }}>Signals</span>
        </Link>

        <nav className="nav-desktop" style={{ alignItems: 'center', gap: 3, marginLeft: 14 }}>
          {navSpine.map((n) => {
            const active = pathname === n.href;
            return (
              <Link
                key={n.href}
                href={n.href}
                data-nav
                aria-current={active ? 'page' : undefined}
                style={{
                  fontFamily: mono,
                  fontSize: 11.5,
                  letterSpacing: '.1em',
                  textTransform: 'uppercase',
                  borderBottom: `2px solid ${active ? 'var(--color-brand-primary)' : 'transparent'}`,
                  color: active ? 'var(--chrome-fg)' : 'var(--chrome-dim)',
                  padding: '7px 11px',
                }}
              >
                {n.label}
              </Link>
            );
          })}
        </nav>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            type="button"
            data-nav
            onClick={openPalette}
            aria-label="Open jump-to command palette"
            className="nav-desktop"
            style={{
              alignItems: 'center',
              gap: 8,
              background: 'rgba(255,255,255,.06)',
              border: '1px solid rgba(255,255,255,.14)',
              color: 'var(--chrome-dim)',
              fontFamily: mono,
              fontSize: 11,
              letterSpacing: '.06em',
              padding: '7px 12px',
            }}
          >
            Jump to… <span style={{ opacity: 0.6 }}>⌘K</span>
          </button>

          <button
            type="button"
            data-nav
            onClick={() => setDrawerOpen(!drawerOpen)}
            aria-label="Toggle navigation menu"
            aria-expanded={drawerOpen}
            className="nav-burger"
            style={{ flexDirection: 'column', gap: 4, background: 'none', border: 0, padding: 6 }}
          >
            <span style={{ width: 20, height: 2, background: 'var(--chrome-fg)', display: 'block' }} />
            <span style={{ width: 20, height: 2, background: 'var(--chrome-fg)', display: 'block' }} />
            <span style={{ width: 20, height: 2, background: 'var(--chrome-fg)', display: 'block' }} />
          </button>
        </div>
      </div>

      {drawerOpen && (
        <div
          className="nav-burger"
          style={{ borderTop: '1px solid rgba(255,255,255,.1)', padding: '8px 22px 16px', flexDirection: 'column' }}
        >
          {navSpine.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              data-nav
              onClick={() => setDrawerOpen(false)}
              style={{
                textAlign: 'left',
                fontFamily: mono,
                fontSize: 13,
                letterSpacing: '.08em',
                textTransform: 'uppercase',
                borderBottom: '1px solid rgba(255,255,255,.08)',
                color: 'var(--chrome-fg)',
                padding: '13px 2px',
              }}
            >
              {n.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
