import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "OpsPilot — AI-Powered DevOps & SRE Incident Assistant",
  description:
    "Grounded AI incident analysis assistant for logs, deployment failures, container crashes, and cloud infrastructure diagnostics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-slate-50 font-sans text-slate-900 antialiased selection:bg-emerald-100 selection:text-emerald-900">
        <div className="flex min-h-screen flex-col">
          <Navbar />
          <main className="flex-1">{children}</main>
          <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
            <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-slate-700">OpsPilot</span>
                <span>— Grounded SRE Diagnostic Assistant</span>
              </div>
              <p className="text-slate-400">
                Diagnostic commands are suggestions only and are never executed directly.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
