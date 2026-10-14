"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Activity,
  ShieldCheck,
  Terminal,
  History,
  LayoutDashboard,
  Cpu,
  AlertCircle,
  RefreshCw,
  Boxes,
} from "lucide-react";
import { opsApi } from "@/lib/api";
import { HealthResponse } from "@/lib/types";

export function Navbar() {
  const pathname = usePathname();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await opsApi.getHealth();
      setHealth(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Offline");
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/k8s-agent", label: "K8s Copilot", icon: Boxes },
    { href: "/analyzer", label: "Incident Analyzer", icon: Terminal },
    { href: "/history", label: "Incident History", icon: History },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 text-emerald-400 shadow-sm transition-transform group-hover:scale-105">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 text-lg tracking-tight">
                  OpsPilot
                </span>
                <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700 border border-emerald-200">
                  SRE AI
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">
                Incident Investigation Engine
              </p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname?.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-slate-100 text-slate-900 font-semibold"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                >
                  <Icon className="h-4 w-4 text-slate-500" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Backend Connectivity Status Badge */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50/80 px-3 py-1.5 text-xs text-slate-700 shadow-xs">
            {loading && !health ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin text-slate-400" />
            ) : health?.status === "healthy" ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
                </span>
                <span className="font-medium text-slate-800">API Connected</span>
                <span className="hidden sm:inline-block text-slate-300">|</span>
                <span className="hidden sm:inline-flex items-center gap-1 font-mono text-[11px] text-slate-600">
                  <Cpu className="h-3 w-3 text-slate-400" />
                  {health.ai_provider.toUpperCase()}
                </span>
              </>
            ) : (
              <>
                <span className="h-2 w-2 rounded-full bg-amber-500" />
                <span className="text-amber-800 font-medium flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  API Disconnected
                </span>
                <button
                  onClick={checkHealth}
                  title="Retry connection"
                  className="ml-1 text-slate-500 hover:text-slate-800"
                >
                  <RefreshCw className="h-3 w-3" />
                </button>
              </>
            )}
          </div>

          <Link
            href="/analyzer"
            className="hidden sm:inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-emerald-700 transition-colors"
          >
            <Activity className="h-3.5 w-3.5" />
            New Investigation
          </Link>
        </div>
      </div>
    </header>
  );
}
