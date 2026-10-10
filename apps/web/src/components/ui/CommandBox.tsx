"use client";

import React, { useState } from "react";
import { Copy, Check, Terminal, ShieldAlert } from "lucide-react";

interface CommandBoxProps {
  command: string;
}

export function CommandBox({ command }: CommandBoxProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      setCopied(false);
    }
  };

  return (
    <div className="mt-2.5 overflow-hidden rounded-lg border border-slate-700 bg-slate-900 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/60 px-3 py-1.5 text-[11px] text-slate-400">
        <div className="flex items-center gap-1.5 font-mono">
          <Terminal className="h-3.5 w-3.5 text-emerald-400" />
          <span>Diagnostic Command Suggestion</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-[10px] text-amber-400/90 font-sans">
            <ShieldAlert className="h-3 w-3" />
            Not auto-executed
          </span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-300 hover:bg-slate-700 hover:text-white transition-colors"
            title="Copy command to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 text-emerald-400" />
                <span className="text-emerald-400 font-medium">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>
      <div className="p-3 font-mono text-xs text-emerald-300 overflow-x-auto whitespace-pre selection:bg-emerald-950 selection:text-white">
        <code>{command}</code>
      </div>
    </div>
  );
}
