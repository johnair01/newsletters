'use client';

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { evidenceMap } from '@/lib/data';
import { useSignals } from './SignalsProvider';

const mono = "'DM Mono', monospace";

/** Provenance, shipped treatment A: a slide-in evidence panel beside the claim. */
export function EvidencePanel() {
  const { evidenceId, closeEvidence } = useSignals();
  const router = useRouter();
  const panelRef = useRef<HTMLDivElement>(null);

  const ev = evidenceId ? evidenceMap[evidenceId] : null;

  // Move focus into the panel when it opens (keyboard operability).
  useEffect(() => {
    if (ev && panelRef.current) panelRef.current.focus();
  }, [ev]);

  if (!ev) return null;

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 80 }} role="dialog" aria-modal="true" aria-label="Evidence">
      <div onClick={closeEvidence} style={{ position: 'absolute', inset: 0, background: 'rgba(10,10,15,.42)' }} />
      <div
        ref={panelRef}
        tabIndex={-1}
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          bottom: 0,
          width: 'min(420px, 86%)',
          background: 'var(--ev-bg)',
          borderLeft: '3px solid var(--color-brand-primary)',
          boxShadow: '-16px 0 40px rgba(10,10,15,.18)',
          animation: 'evIn .26s cubic-bezier(.2,.7,.3,1)',
          display: 'flex',
          flexDirection: 'column',
          outline: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 20px 14px', borderBottom: '1px solid var(--line)' }}>
          <span style={{ fontFamily: mono, fontSize: 10, letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--color-brand-primary)' }}>Evidence</span>
          <button type="button" data-nav onClick={closeEvidence} style={{ background: 'none', border: 0, fontFamily: mono, fontSize: 11, letterSpacing: '.06em', textTransform: 'uppercase', color: 'var(--text-dim)', padding: 4 }}>
            ✕ Back to claim
          </button>
        </div>
        <div style={{ padding: '22px 20px', overflow: 'auto', flex: 1 }}>
          <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--text-dim)', margin: '0 0 9px' }}>The claim</p>
          <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 20, lineHeight: 1.3, margin: '0 0 24px', color: 'var(--text)' }}>{ev.claim}</p>
          <p style={{ fontFamily: mono, fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: 'var(--color-brand-primary)', margin: '0 0 9px' }}>
            Traces to · {ev.source} · {ev.ts}
          </p>
          <div style={{ borderLeft: '3px solid var(--color-brand-primary)', background: 'var(--color-surface-low)', padding: '14px 16px' }}>
            <p style={{ fontSize: 15, lineHeight: 1.65, fontStyle: 'italic', color: 'var(--text)', margin: 0 }}>{ev.span}</p>
          </div>
        </div>
        <div style={{ padding: '16px 20px', borderTop: '1px solid var(--line)', display: 'flex', gap: 10 }}>
          <button
            type="button"
            data-nav
            onClick={() => { closeEvidence(); router.push(ev.sourceHref); }}
            style={{ flex: 1, fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', background: 'var(--text)', color: 'var(--color-paper)', border: 0, padding: 12 }}
          >
            Open source surface →
          </button>
          <button type="button" data-nav onClick={closeEvidence} style={{ fontFamily: mono, fontSize: 11, letterSpacing: '.08em', textTransform: 'uppercase', background: 'transparent', color: 'var(--text)', border: '1px solid var(--text)', padding: '12px 16px' }}>
            ← Back
          </button>
        </div>
      </div>
    </div>
  );
}
