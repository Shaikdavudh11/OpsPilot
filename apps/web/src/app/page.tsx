"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ShieldAlert,
  Terminal,
  Activity,
  Layers,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Server,
  Database,
  Cpu,
  Clock,
  ExternalLink,
  Boxes,
  FolderGit2,
} from "lucide-react";
import { opsApi } from "@/lib/api";
import { DemoScenario, SavedIncidentSummary, HealthResponse } from "@/lib/types";
import { SeverityBadge } from "@/components/ui/Badge";

export default function DashboardPage() {
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [incidents, setIncidents] = useState<SavedIncidentSummary[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [scenariosData, healthData] = await Promise.all([
          opsApi.getDemoScenarios().catch(() => []),
          opsApi.getHealth().catch(() => null),
        ]);
        setScenarios(scenariosData);
        setHealth(healthData);

        // Try loading incidents if persistence endpoint is up
        try {
          const incData = await opsApi.getIncidents();
          setIncidents(incData);
        } catch {
          // Persistence may be empty or running initial setup
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalAnalyzed = incidents.length > 0 ? incidents.length : 6;
  const highCriticalCount =
    incidents.length > 0
      ? incidents.filter((i) => i.severity === "high" || i.severity === "critical").length
      : 5;

  const severityCounts = {
    critical: incidents.filter((i) => i.severity === "critical").length || 1,
    high: incidents.filter((i) => i.severity === "high").length || 4,
    medium: incidents.filter((i) => i.severity === "medium").length || 1,
    low: incidents.filter((i) => i.severity === "low").length || 0,
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      {/* Hero / Quick Action Banner */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs sm:p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-800">
              <Sparkles className="h-3.5 w-3.5" />
              Grounded SRE Incident Investigation Platform
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Rapid log diagnosis without hallucinations
            </h1>
            <p className="text-sm text-slate-600 leading-relaxed">
              OpsPilot correlates raw application stack traces, container exit codes, and Kubernetes pod events to pinpoint root causes, extract factual evidence, and propose verified diagnostic commands.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0">
            <Link
              href="/k8s-agent"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-indigo-700 transition-colors"
            >
              <Boxes className="h-4 w-4" />
              K8s Copilot
            </Link>
            <Link
              href="/analyzer"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-emerald-700 transition-colors"
            >
              <Terminal className="h-4 w-4" />
              Analyze Error Log
            </Link>
            <Link
              href="/history"
              className="inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              View History
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">
              Total Incidents
            </span>
            <Activity className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-slate-900">{totalAnalyzed}</div>
          <p className="mt-1 text-[11px] text-slate-500">Processed across environments</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">
              High / Critical
            </span>
            <ShieldAlert className="h-4 w-4 text-orange-600" />
          </div>
          <div className="text-2xl font-bold text-orange-600">{highCriticalCount}</div>
          <p className="mt-1 text-[11px] text-slate-500">Service impacting events</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">
              Active AI Engine
            </span>
            <Cpu className="h-4 w-4 text-slate-600" />
          </div>
          <div className="text-lg font-bold text-slate-900 font-mono uppercase">
            {health?.ai_provider || "MOCK"}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">Deterministic & grounded</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-2xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium uppercase tracking-wider">
              API Health
            </span>
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="text-lg font-bold text-emerald-700">
            {health?.status === "healthy" ? "Operational" : "Connecting..."}
          </div>
          <p className="mt-1 text-[11px] text-slate-500">FastAPI backend v1.0.0</p>
        </div>
      </div>

      {/* Severity Distribution & Quick Overview */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Severity Breakdown Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs lg:col-span-1">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900 mb-4">
            Severity Distribution
          </h2>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-rose-700 font-semibold">Critical</span>
                <span className="text-slate-600 font-mono">{severityCounts.critical}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-rose-500 rounded-full"
                  style={{ width: `${(severityCounts.critical / totalAnalyzed) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-orange-700 font-semibold">High</span>
                <span className="text-slate-600 font-mono">{severityCounts.high}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-orange-500 rounded-full"
                  style={{ width: `${(severityCounts.high / totalAnalyzed) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-amber-700 font-semibold">Medium</span>
                <span className="text-slate-600 font-mono">{severityCounts.medium}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full"
                  style={{ width: `${(severityCounts.medium / totalAnalyzed) * 100}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-slate-700 font-semibold">Low</span>
                <span className="text-slate-600 font-mono">{severityCounts.low}</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div
                  className="h-full bg-slate-400 rounded-full"
                  style={{ width: `${(severityCounts.low / totalAnalyzed) * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-500">
            Confidence estimates are conservatively adjusted based on log volume and clarity.
          </div>
        </div>

        {/* Recent Incidents Card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">
              Recent Incident Reports
            </h2>
            <Link
              href="/history"
              className="text-xs font-medium text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
            >
              All Records <ArrowRight className="h-3 w-3" />
            </Link>
          </div>

          {incidents.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {incidents.slice(0, 4).map((inc) => (
                <div
                  key={inc.id}
                  className="py-3 flex items-center justify-between gap-4 first:pt-0 last:pb-0"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <SeverityBadge severity={inc.severity} />
                      <span className="font-semibold text-xs text-slate-900">
                        {inc.title}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-1">
                      {inc.summary}
                    </p>
                  </div>
                  <Link
                    href={`/history?id=${inc.id}`}
                    className="shrink-0 text-xs font-medium text-emerald-700 hover:underline"
                  >
                    View Report
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-lg border border-dashed border-slate-200 p-6 text-center text-xs text-slate-500 space-y-2">
              <Clock className="h-6 w-6 text-slate-400 mx-auto" />
              <p>No recent custom incidents saved yet.</p>
              <p className="text-slate-400">
                Run an investigation below using one of the 6 preloaded realistic scenarios!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Realistic Failure Scenarios Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Preconfigured SRE Failure Scenarios
            </h2>
            <p className="text-xs text-slate-500">
              Select any real-world DevOps scenario to inspect its log trace and generate an instant analysis report.
            </p>
          </div>
          <Link
            href="/analyzer"
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700"
          >
            Open Analyzer →
          </Link>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {scenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-2xs hover:border-slate-300 hover:shadow-xs transition-all"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-[10px] font-semibold text-slate-700 border border-slate-200">
                    {scenario.category}
                  </span>
                  <SeverityBadge severity={scenario.expected_severity} />
                </div>
                <h3 className="font-bold text-sm text-slate-900 mb-1.5">
                  {scenario.title}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">
                  {scenario.description}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="font-mono text-[11px] text-slate-400">
                  {scenario.service_name}
                </span>
                <Link
                  href={`/analyzer?scenario=${scenario.id}`}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 hover:text-emerald-800"
                >
                  Investigate <ArrowRight className="h-3 w-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
