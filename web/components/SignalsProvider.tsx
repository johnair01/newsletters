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
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [evidenceId, setEvidenceId] = useState<string | null>(null);

  // Resolve initial theme from storage / system preference, then keep <html> in sync.
  useEffect(() => {
    const stored = window.localStorage.getItem('signals-theme') as Theme | null;
    const initial: Theme = stored ?? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    setTheme(initial);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    window.localStorage.setItem('signals-theme', theme);
  }, [theme]);

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
