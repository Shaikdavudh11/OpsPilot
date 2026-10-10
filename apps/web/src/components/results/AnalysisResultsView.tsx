"use client";

import React from "react";
import {
  ShieldAlert,
  Search,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Lock,
  ArrowRight,
  Info,
  Clock,
  Server,
} from "lucide-react";
import { IncidentAnalysisResponse } from "@/lib/types";
import { SeverityBadge, ConfidenceBadge, RiskBadge } from "@/components/ui/Badge";
import { CommandBox } from "@/components/ui/CommandBox";

interface AnalysisResultsViewProps {
  data: IncidentAnalysisResponse;
  onReset?: () => void;
}

export function AnalysisResultsView({ data, onReset }: AnalysisResultsViewProps) {
  return (
    <div className="space-y-6">
      {/* Safety Notice Banner */}
      <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50/70 p-4 text-xs text-amber-900">
        <ShieldAlert className="h-5 w-5 shrink-0 text-amber-600 mt-0.5" />
        <div className="space-y-1">
          <p className="font-semibold text-amber-900">
            Automated SRE Safety Notice
          </p>
          <p className="text-amber-800 leading-relaxed">
            All root cause assessments and diagnostic commands provided below are advisory suggestions grounded in the provided logs. OpsPilot does not execute commands, modify infrastructure, or access external systems. Always review commands carefully in your runbooks prior to execution.
          </p>
        </div>
      </div>

      {/* Header Overview Card */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2.5">
              <SeverityBadge severity={data.severity} />
              {data.redacted_secrets_count && data.redacted_secrets_count > 0 ? (
                <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700 border border-slate-200">
                  <Lock className="h-3 w-3 text-slate-500" />
                  {data.redacted_secrets_count} Secret{data.redacted_secrets_count > 1 ? "s" : ""} Redacted
                </span>
              ) : null}
            </div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              {data.title}
            </h1>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-500 shrink-0">
            {data.analyzed_at && (
              <div className="flex items-center gap-1.5 font-mono">
                <Clock className="h-3.5 w-3.5 text-slate-400" />
                <span>{new Date(data.analyzed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
              </div>
            )}
            {onReset && (
              <button
                onClick={onReset}
                className="rounded-md border border-slate-200 px-3 py-1.5 font-medium text-slate-700 hover:bg-slate-50 transition-colors"
              >
                New Analysis
              </button>
            )}
          </div>
        </div>

        {/* Executive Summary */}
        <div className="pt-4">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
            Incident Summary
          </h2>
          <p className="text-sm text-slate-800 leading-relaxed font-normal">
            {data.summary}
          </p>
        </div>
      </div>

      {/* Primary Root Cause Assessment */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Search className="h-5 w-5 text-emerald-600" />
            <h2 className="text-base font-bold text-slate-900">
              Likely Root Cause
            </h2>
          </div>
          <ConfidenceBadge confidence={data.likely_root_cause.confidence} />
        </div>

        <div className="rounded-lg bg-slate-50 border border-slate-200 p-4 mb-4">
          <p className="text-sm font-semibold text-slate-900">
            {data.likely_root_cause.description}
          </p>
        </div>

        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
            Technical Reasoning
          </h3>
          <p className="text-sm text-slate-700 leading-relaxed">
            {data.likely_root_cause.reasoning}
          </p>
        </div>
      </div>

      {/* Evidence Extracted from Logs */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle2 className="h-5 w-5 text-emerald-600" />
          <h2 className="text-base font-bold text-slate-900">
            Supporting Evidence Extracted from Logs
          </h2>
        </div>

        {data.evidence && data.evidence.length > 0 ? (
          <div className="space-y-3">
            {data.evidence.map((item, index) => (
              <div
                key={index}
                className="rounded-lg border border-slate-200 bg-slate-50/60 p-3.5"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    {item.source}
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Evidence #{index + 1}
                  </span>
                </div>
                <div className="font-mono text-xs text-slate-800 bg-white p-2.5 rounded border border-slate-200 overflow-x-auto whitespace-pre-wrap">
                  {item.finding}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500 italic">
            No explicit line-level evidence extracted.
          </p>
        )}
      </div>

      {/* Step-by-Step Diagnostic Recommendations */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex items-center gap-2 mb-4">
          <Server className="h-5 w-5 text-emerald-600" />
          <h2 className="text-base font-bold text-slate-900">
            Recommended Diagnostic & Remediation Steps
          </h2>
        </div>

        <div className="space-y-4">
          {data.recommendations.map((step, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-slate-200 bg-white p-4 shadow-2xs"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-2">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-900 text-[11px] font-bold text-white">
                    {idx + 1}
                  </span>
                  <h3 className="text-sm font-semibold text-slate-900">
                    {step.action}
                  </h3>
                </div>
                <RiskBadge risk={step.risk_level} />
              </div>

              <p className="text-xs text-slate-600 ml-7 leading-relaxed">
                <strong className="text-slate-700">Rationale: </strong>
                {step.reason}
              </p>

              {step.suggested_command && (
                <div className="ml-7 mt-2">
                  <CommandBox command={step.suggested_command} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Prevention & Systemic Hardening */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="h-5 w-5 text-emerald-600" />
          <h2 className="text-base font-bold text-slate-900">
            Long-term Prevention & Reliability Engineering
          </h2>
        </div>

        <div className="grid gap-3 md:grid-cols-2">
          {data.prevention.map((prev, idx) => (
            <div
              key={idx}
              className="rounded-lg border border-slate-200 bg-slate-50/50 p-4"
            >
              <h3 className="text-xs font-bold text-slate-900 mb-1 flex items-center gap-1.5">
                <ArrowRight className="h-3 w-3 text-emerald-600" />
                {prev.strategy}
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                {prev.details}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Limitations & Missing Telemetry */}
      {data.limitations && data.limitations.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-2 mb-3">
            <Info className="h-5 w-5 text-slate-500" />
            <h2 className="text-base font-bold text-slate-900">
              Confidence Estimate & Limitations
            </h2>
          </div>
          <p className="text-xs text-slate-500 mb-3">
            The following boundaries define what could not be independently verified from the provided input:
          </p>
          <ul className="space-y-1.5 text-xs text-slate-600 list-disc list-inside">
            {data.limitations.map((limit, idx) => (
              <li key={idx} className="leading-relaxed">
                {limit}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
