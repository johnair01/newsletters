'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { jumpGroups, type JumpGroup } from '@/lib/data';
import { useSignals } from './SignalsProvider';

const mono = "'DM Mono', monospace";

/** "Jump to…" command palette (⌘K). Searchable jump across surfaces, pages, records. */
export function CommandPalette() {
  const { paletteOpen, closePalette } = useSignals();
  const router = useRouter();
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const triggerRef = useRef<Element | null>(null);

  // Reset query + capture/focus on open; restore focus to the trigger on close.
  useEffect(() => {
    if (paletteOpen) {
      triggerRef.current = document.activeElement;
      setQuery('');
      // focus after paint
      const id = requestAnimationFrame(() => inputRef.current?.focus());
      return () => cancelAnimationFrame(id);
    }
    if (triggerRef.current instanceof HTMLElement) triggerRef.current.focus();
  }, [paletteOpen]);

  const groups: JumpGroup[] = useMemo(() => {
    const q = query.trim().toLowerCase();
    return jumpGroups
      .map((g) => ({
        head: g.head,
        items: g.items.filter((it) => !q || `${it.label} ${it.kw}`.toLowerCase().includes(q)),
      }))
      .filter((g) => g.items.length > 0);
  }, [query]);

  const flat = useMemo(() => groups.flatMap((g) => g.items), [groups]);

  if (!paletteOpen) return null;

  const navigate = (href: string) => {
    closePalette();
    router.push(href);
  };

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 90 }} role="dialog" aria-modal="true" aria-label="Jump to">
      <div onClick={closePalette} style={{ position: 'absolute', inset: 0, background: 'rgba(10,10,15,.5)' }} />
      <div
        style={{
          position: 'absolute',
          top: 64,
          left: '50%',
          transform: 'translateX(-50%)',
          width: 'min(560px, 90%)',
          background: 'var(--card)',
          border: '1px solid var(--line)',
          boxShadow: '0 24px 60px rgba(10,10,15,.3)',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '78%',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '16px 18px', borderBottom: '1px solid var(--line)' }}>
          <span style={{ fontFamily: mono, fontSize: 13, color: 'var(--text-dim)' }}>⌘K</span>
          <input
            ref={inputRef}
            data-nav
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && flat[0]) navigate(flat[0].href);
            }}
            placeholder="Jump to a surface, record, or page…"
            aria-label="Jump to a surface, record, or page"
            style={{ flex: 1, border: 0, background: 'none', outline: 'none', fontFamily: "'Instrument Sans', sans-serif", fontSize: 16, color: 'var(--text)' }}
          />
          <button type="button" data-nav onClick={closePalette} style={{ background: 'none', border: '1px solid var(--line)', fontFamily: mono, fontSize: 10, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--text-dim)', padding: '4px 8px' }}>
            Esc
          </button>
        </div>

        <div style={{ overflow: 'auto', flex: 1 }}>
          {groups.map((g) => (
            <div key={g.head}>
              <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: 0, padding: '12px 18px 6px' }}>{g.head}</p>
              {g.items.map((it) => (
                <button
                  key={`${g.head}-${it.label}`}
                  type="button"
                  data-nav
                  onClick={() => navigate(it.href)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    background: 'var(--card)',
                    border: 0,
                    borderLeft: `3px solid ${it.color}`,
                    borderTop: '1px solid var(--line)',
                    padding: '11px 18px',
                    color: 'var(--text)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                  }}
                >
                  <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, flex: 1 }}>{it.label}</span>
                  <span style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.08em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>{it.kind}</span>
                  <span style={{ fontFamily: mono, fontSize: 12, color: 'var(--text-dim)' }}>↵</span>
                </button>
              ))}
            </div>
          ))}
          {groups.length === 0 && (
            <div style={{ padding: '40px 18px', textAlign: 'center' }}>
              <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, margin: '0 0 6px', color: 'var(--text)' }}>No matches</p>
              <p style={{ fontSize: 13.5, color: 'var(--text-dim)', margin: 0 }}>Try “report”, “show”, or a record name like “spine”.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
