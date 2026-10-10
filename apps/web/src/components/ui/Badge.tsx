import React from "react";
import { Severity, RiskLevel, Confidence } from "@/lib/types";

interface SeverityBadgeProps {
  severity: Severity;
  className?: string;
}

export function SeverityBadge({ severity, className = "" }: SeverityBadgeProps) {
  const styles: Record<Severity, string> = {
    low: "bg-slate-100 text-slate-700 border-slate-200",
    medium: "bg-amber-50 text-amber-800 border-amber-200",
    high: "bg-orange-50 text-orange-800 border-orange-200",
    critical: "bg-rose-50 text-rose-800 border-rose-200 font-bold animate-pulse",
  };

  const labels: Record<Severity, string> = {
    low: "LOW SEVERITY",
    medium: "MEDIUM SEVERITY",
    high: "HIGH SEVERITY",
    critical: "CRITICAL SEVERITY",
  };

  return (
    <span
      className={`inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold tracking-wide uppercase ${styles[severity]} ${className}`}
    >
      {labels[severity]}
    </span>
  );
}

interface ConfidenceBadgeProps {
  confidence: Confidence;
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const styles: Record<Confidence, string> = {
    low: "bg-amber-50 text-amber-700 border-amber-200",
    medium: "bg-blue-50 text-blue-700 border-blue-200",
    high: "bg-emerald-50 text-emerald-800 border-emerald-200",
  };

  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wider ${styles[confidence]}`}
    >
      {confidence} Confidence
    </span>
  );
}

interface RiskBadgeProps {
  risk: RiskLevel;
}

export function RiskBadge({ risk }: RiskBadgeProps) {
  const styles: Record<RiskLevel, string> = {
    low: "bg-emerald-50 text-emerald-700 border-emerald-200",
    medium: "bg-amber-50 text-amber-700 border-amber-200",
    high: "bg-rose-50 text-rose-700 border-rose-200",
  };

  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider ${styles[risk]}`}
    >
      Risk: {risk}
    </span>
  );
}
