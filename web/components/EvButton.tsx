'use client';

import { useSignals } from './SignalsProvider';

const mono = "'DM Mono', monospace";

interface EvButtonProps {
  id: string;
  /** Pill background — the citing surface's accent. */
  bg?: string;
  /** Pill text color. */
  fg?: string;
  label?: string;
  /** Render inline as superscript (in running prose) vs. baseline. */
  superscript?: boolean;
}

/** Inline claim → evidence trigger. Opens the slide-in evidence panel. */
export function EvButton({ id, bg = 'var(--color-brand-primary)', fg = 'var(--color-paper)', label = 'EV ↗', superscript = true }: EvButtonProps) {
  const { openEvidence } = useSignals();
  return (
    <button
      type="button"
      data-nav
      onClick={() => openEvidence(id)}
      aria-label="Show the source evidence for this claim"
      style={{
        verticalAlign: superscript ? 'super' : 'baseline',
        fontFamily: mono,
        fontSize: 9.5,
        letterSpacing: '.04em',
        color: fg,
        background: bg,
        border: 0,
        padding: '1px 6px',
        marginLeft: 3,
      }}
    >
      {label}
    </button>
  );
}
