'use client';

import { createContext, useCallback, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

interface SignalsContextValue {
  theme: Theme;
  toggleTheme: () => void;
  drawerOpen: boolean;
  setDrawerOpen: (v: boolean) => void;
  paletteOpen: boolean;
  openPalette: () => void;
  closePalette: () => void;
  evidenceId: string | null;
  openEvidence: (id: string) => void;
  closeEvidence: () => void;
}

const SignalsContext = createContext<SignalsContextValue | null>(null);

export function useSignals(): SignalsContextValue {
  const ctx = useContext(SignalsContext);
  if (!ctx) throw new Error('useSignals must be used within <SignalsProvider>');
  return ctx;
}

export function SignalsProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');
  const [ready, setReady] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [evidenceId, setEvidenceId] = useState<string | null>(null);

  // Sync state to whatever the pre-paint inline script already applied to <html>
  // (storage → system preference). Reading it here means no hydration flash.
  useEffect(() => {
    const applied = document.documentElement.getAttribute('data-theme') as Theme | null;
    const initial: Theme = applied ?? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    setTheme(initial);
    setReady(true);
  }, []);

  // Only write the attribute/storage on subsequent changes (a user toggle),
  // never on the first resolve — the inline script owns the initial paint.
  useEffect(() => {
    if (!ready) return;
    document.documentElement.setAttribute('data-theme', theme);
    window.localStorage.setItem('signals-theme', theme);
  }, [theme, ready]);

  const toggleTheme = useCallback(() => setTheme((t) => (t === 'dark' ? 'light' : 'dark')), []);
  const openPalette = useCallback(() => setPaletteOpen(true), []);
  const closePalette = useCallback(() => setPaletteOpen(false), []);
  const openEvidence = useCallback((id: string) => setEvidenceId(id), []);
  const closeEvidence = useCallback(() => setEvidenceId(null), []);

  // Global keyboard: ⌘K / Ctrl+K toggles the palette; Esc closes overlays.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        setPaletteOpen((p) => !p);
      }
      if (e.key === 'Escape') {
        setPaletteOpen(false);
        setEvidenceId(null);
        setDrawerOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <SignalsContext.Provider
      value={{
        theme,
        toggleTheme,
        drawerOpen,
        setDrawerOpen,
        paletteOpen,
        openPalette,
        closePalette,
        evidenceId,
        openEvidence,
        closeEvidence,
      }}
    >
      {children}
    </SignalsContext.Provider>
  );
}
