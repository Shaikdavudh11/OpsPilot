"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Terminal,
  Play,
  RotateCcw,
  AlertCircle,
  Sparkles,
  Lock,
} from "lucide-react";
import { opsApi } from "@/lib/api";
import { DemoScenario, IncidentAnalysisResponse } from "@/lib/types";
import { AnalysisResultsView } from "@/components/results/AnalysisResultsView";

function AnalyzerForm() {
  const searchParams = useSearchParams();
  const scenarioParam = searchParams.get("scenario");

  const [title, setTitle] = useState("");
  const [environment, setEnvironment] = useState("production");
  const [serviceName, setServiceName] = useState("");
  const [rawLogs, setRawLogs] = useState("");
  const [loading, setLoading] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IncidentAnalysisResponse | null>(null);

  // Demo scenarios
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>("");

  useEffect(() => {
    // Load scenarios on mount
    opsApi
      .getDemoScenarios()
      .then((data) => {
        setScenarios(data);
        if (scenarioParam) {
          const matched = data.find((s) => s.id === scenarioParam);
          if (matched) {
            setSelectedScenarioId(matched.id);
            setTitle(matched.title);
            setEnvironment(matched.environment);
            setServiceName(matched.service_name);
            setRawLogs(matched.raw_logs);
          }
        }
      })
      .catch(() => {});
  }, [scenarioParam]);

  // Timer while analyzing
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (loading) {
      setElapsedSeconds(0);
      timer = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [loading]);

  const handleSelectScenario = (scenarioId: string) => {
    setSelectedScenarioId(scenarioId);
    const found = scenarios.find((s) => s.id === scenarioId);
    if (found) {
      setTitle(found.title);
      setEnvironment(found.environment);
      setServiceName(found.service_name);
      setRawLogs(found.raw_logs);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawLogs.trim() || rawLogs.trim().length < 10) {
      setError("Please paste a meaningful error log snippet (at least 10 characters).");
      return;
    }

    if (rawLogs.length > 65536) {
      setError("Log input exceeds maximum limit of 65,536 characters.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await opsApi.analyzeIncident({
        title: title.trim() || "Uncategorized Incident",
        environment,
        service_name: serviceName.trim() || "unknown-service",
        raw_logs: rawLogs,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze incident.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  if (result) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <AnalysisResultsView data={result} onReset={handleReset} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1.5">
          <Terminal className="h-5 w-5 text-emerald-600" />
          <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
            Incident Investigation Assistant
          </h1>
        </div>
        <p className="text-sm text-slate-600">
          Paste error logs, stack traces, or container crash outputs to generate grounded root cause assessments, evidence extraction, and safe diagnostic suggestions.
        </p>
      </div>

      {/* Main Analysis Form */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
        {/* Sample Scenario Selector */}
        {scenarios.length > 0 && (
          <div className="mb-6 rounded-lg border border-slate-200 bg-slate-50/70 p-4">
            <div className="flex items-center justify-between mb-2">
              <label
                htmlFor="scenario-select"
                className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5"
              >
                <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
                Quick-Load Realistic SRE Scenario
              </label>
              <span className="text-[11px] text-slate-400">
                {scenarios.length} scenarios available
              </span>
            </div>
            <select
              id="scenario-select"
              value={selectedScenarioId}
              onChange={(e) => handleSelectScenario(e.target.value)}
              className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-800 shadow-2xs focus:border-emerald-500 focus:outline-hidden focus:ring-1 focus:ring-emerald-500"
            >
              <option value="">-- Choose a failure scenario to populate form --</option>
              {scenarios.map((s) => (
                <option key={s.id} value={s.id}>
                  [{s.category.toUpperCase()}] {s.title} — {s.description}
                </option>
              ))}
            </select>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Metadata Row */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label
                htmlFor="incident-title"
                className="block text-xs font-semibold text-slate-700 mb-1"
              >
                Incident Title (Optional)
              </label>
              <input
                id="incident-title"
                type="text"
                placeholder="e.g., Database connection pool timeout"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-hidden focus:ring-1 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label
                htmlFor="service-name"
                className="block text-xs font-semibold text-slate-700 mb-1"
              >
                Service / Workload
              </label>
              <input
                id="service-name"
                type="text"
                placeholder="e.g., payment-service"
                value={serviceName}
                onChange={(e) => setServiceName(e.target.value)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:border-emerald-500 focus:outline-hidden focus:ring-1 focus:ring-emerald-500"
              />
            </div>

            <div>
              <label
                htmlFor="environment"
                className="block text-xs font-semibold text-slate-700 mb-1"
              >
                Environment
              </label>
              <select
                id="environment"
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-xs text-slate-900 focus:border-emerald-500 focus:outline-hidden focus:ring-1 focus:ring-emerald-500"
              >
                <option value="production">Production</option>
                <option value="staging">Staging</option>
                <option value="dev">Development</option>
                <option value="ci">CI / Test Pipeline</option>
              </select>
            </div>
          </div>

          {/* Log Input Area */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label
                htmlFor="raw-logs"
                className="block text-xs font-semibold text-slate-700"
              >
                Error Log Output / Stack Trace <span className="text-rose-500">*</span>
              </label>
              <div className="flex items-center gap-3 text-[11px] text-slate-500">
                <span className="flex items-center gap-1 text-slate-500">
                  <Lock className="h-3 w-3 text-emerald-600" />
                  Auto-redacts API keys & tokens
                </span>
                <span className="font-mono">
                  {rawLogs.length.toLocaleString()} / 65,536 chars
                </span>
              </div>
            </div>

            <textarea
              id="raw-logs"
              rows={12}
              required
              value={rawLogs}
              onChange={(e) => setRawLogs(e.target.value)}
              placeholder="Paste raw application stdout/stderr logs, Kubernetes describe pod events, Docker exit logs, or CI/CD test failure output here..."
              className="w-full rounded-md border border-slate-300 bg-slate-950 p-3 font-mono text-xs text-emerald-300 placeholder:text-slate-600 focus:border-emerald-500 focus:outline-hidden focus:ring-1 focus:ring-emerald-500 selection:bg-emerald-900 selection:text-white"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-start gap-2 rounded-md border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold">Analysis Failed</p>
                <p>{error}</p>
              </div>
            </div>
          )}

          {/* Submit & Reset Buttons */}
          <div className="flex items-center justify-between pt-2">
            <button
              type="button"
              onClick={() => {
                setRawLogs("");
                setTitle("");
                setServiceName("");
                setSelectedScenarioId("");
                setError(null);
              }}
              className="flex items-center gap-1.5 rounded-md border border-slate-200 px-3.5 py-2 text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Clear Form
            </button>

            <button
              type="submit"
              disabled={loading || !rawLogs.trim()}
              className="flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <>
                  <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  <span>Analyzing Logs ({elapsedSeconds}s)...</span>
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-white" />
                  <span>Run Incident Investigation</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function AnalyzerPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading analyzer...</div>}>
      <AnalyzerForm />
    </Suspense>
  );
}
