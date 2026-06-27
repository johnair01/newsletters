import type { Metadata } from 'next';
import './globals.css';
import { SignalsProvider } from '@/components/SignalsProvider';
import { Nav } from '@/components/Nav';
import { Breadcrumb } from '@/components/Breadcrumb';
import { Footer } from '@/components/Footer';
import { EvidencePanel } from '@/components/EvidencePanel';
import { CommandPalette } from '@/components/CommandPalette';

export const metadata: Metadata = {
  title: 'Signals — one reviewed record, told for every reader',
  description:
    'Signals turns one reviewed record into five reader surfaces — Report, Article, Newsletter, The Show and Learning — with every claim traced to its source.',
};

// Pre-paint: apply the saved/system theme to <html> before first paint so there
// is no light→dark flash on load. Kept tiny and dependency-free on purpose.
const themeScript = `(function(){try{var t=localStorage.getItem('signals-theme');if(t!=='light'&&t!=='dark'){t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){document.documentElement.setAttribute('data-theme','light');}})();`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <SignalsProvider>
          <div className="viewport">
            <Nav />
            <Breadcrumb />
            <main style={{ minHeight: '60vh' }}>{children}</main>
            <Footer />
          </div>
          {/* Root-mounted overlays */}
          <EvidencePanel />
          <CommandPalette />
        </SignalsProvider>
      </body>
    </html>
  );
}
