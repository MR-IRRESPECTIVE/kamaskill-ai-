import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'KarmaSkill AI - Competency Platform',
  description: 'AI-powered competency intelligence and personalized learning platform.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-sans bg-slate-50">
        {children}
      </body>
    </html>
  );
}
