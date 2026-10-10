"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  History,
  Clock,
  ArrowRight,
  RefreshCw,
  AlertCircle,
  FileText,
  ChevronLeft,
  Server,
} from "lucide-react";
import { opsApi } from "@/lib/api";
import { SavedIncidentSummary, IncidentAnalysisResponse } from "@/lib/types";
import { SeverityBadge } from "@/components/ui/Badge";
import { AnalysisResultsView } from "@/components/results/AnalysisResultsView";

function IncidentHistoryContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const requestedId = searchParams.get("id");

  const [incidents, setIncidents] = useState<SavedIncidentSummary[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<IncidentAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingReport, setLoadingReport] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await opsApi.getIncidents();
      setIncidents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load incidents.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  // If ?id= is present in URL, fetch that incident
  useEffect(() => {
    if (requestedId) {
      setLoadingReport(true);
      opsApi
        .getIncidentById(requestedId)
        .then((data) => {
          setSelectedIncident(data);
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Incident not found");
        })
        .finally(() => {
          setLoadingReport(false);
        });
    } else {
      setSelectedIncident(null);
    }
  }, [requestedId]);

  const handleOpenIncident = (id: string) => {
    router.push(`/history?id=${id}`);
  };

  const handleBackToList = () => {
    router.push("/history");
    setSelectedIncident(null);
  };

  if (loadingReport) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16 text-center">
        <RefreshCw className="h-6 w-6 animate-spin text-emerald-600 mx-auto mb-2" />
        <p className="text-xs text-slate-500 font-mono">Loading saved incident report...</p>
      </div>
    );
  }

  if (selectedIncident) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8 space-y-4">
        <button
          onClick={handleBackToList}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to Incident History
        </button>
        <AnalysisResultsView data={selectedIncident} onReset={handleBackToList} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <History className="h-5 w-5 text-emerald-600" />
            <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
              Incident Investigation History
            </h1>
          </div>
          <p className="text-sm text-slate-600">
            Audit trail of analyzed infrastructure incidents, root cause records, and recommendations.
          </p>
        </div>

        <button
          onClick={fetchIncidents}
          disabled={loading}
          className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="mb-6 flex items-start gap-2 rounded-md border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
          <div>
            <p className="font-semibold">Unable to fetch history</p>
            <p>{error}</p>
          </div>
        </div>
      )}

      {loading && incidents.length === 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-xs text-slate-500">
          <RefreshCw className="h-6 w-6 animate-spin text-slate-400 mx-auto mb-2" />
          Loading saved incident records...
        </div>
      ) : incidents.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 bg-white p-12 text-center space-y-3">
          <FileText className="h-8 w-8 text-slate-400 mx-auto" />
          <h2 className="text-sm font-semibold text-slate-800">No Incidents Analyzed Yet</h2>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Analyze your first error log or test a demo failure scenario from the Incident Analyzer to view persistent reports here.
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white shadow-xs divide-y divide-slate-100 overflow-hidden">
          {incidents.map((incident) => (
            <div
              key={incident.id}
              onClick={() => handleOpenIncident(incident.id)}
              className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/70 transition-colors cursor-pointer group"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityBadge severity={incident.severity} />
                  <span className="font-bold text-sm text-slate-900 group-hover:text-emerald-700 transition-colors">
                    {incident.title}
                  </span>
                </div>
                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                  {incident.summary}
                </p>
                <div className="flex items-center gap-4 text-[11px] text-slate-400 font-mono pt-1">
                  <span className="flex items-center gap-1">
                    <Server className="h-3 w-3" />
                    {incident.service_name} ({incident.environment})
                  </span>
                  {incident.created_at && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(incident.created_at).toLocaleString()}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 sm:shrink-0">
                <span>View Full Report</span>
                <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function HistoryPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs text-slate-500">Loading history...</div>}>
      <IncidentHistoryContent />
    </Suspense>
  );
}
