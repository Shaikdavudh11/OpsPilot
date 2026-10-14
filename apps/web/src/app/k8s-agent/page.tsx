"use client";

import { useEffect, useState } from "react";
import {
  Boxes,
  Terminal,
  FolderGit2,
  FolderOpen,
  ArrowRight,
  Sparkles,
  Check,
  Copy,
  Download,
  AlertTriangle,
  ShieldCheck,
  Activity,
  Layers,
  Cpu,
  Server,
  Code2,
  RefreshCw,
  Zap,
  Wrench,
  CheckCircle2,
  FileCode2,
  ExternalLink,
} from "lucide-react";
import { opsApi, ApiError } from "@/lib/api";
import {
  K8sAnalysisResponse,
  PodTroubleshootResponse,
  SampleRepo,
  HealthResponse,
} from "@/lib/types";

export default function K8sAgentPage() {
  const [activeTab, setActiveTab] = useState<"analyze" | "troubleshoot">("analyze");
  const [samples, setSamples] = useState<SampleRepo[]>([]);
  const [loadingSamples, setLoadingSamples] = useState(false);
  const [k8sHealth, setK8sHealth] = useState<HealthResponse | null>(null);

  // Analysis state
  const [repoSource, setRepoSource] = useState<"github" | "local">("local");
  const [repoUrl, setRepoUrl] = useState("");
  const [localPath, setLocalPath] = useState("");
  const [appName, setAppName] = useState("");
  const [namespace, setNamespace] = useState("production");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<K8sAnalysisResponse | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [activeManifestTab, setActiveManifestTab] = useState<string>("deployment_yaml");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // Troubleshooter state
  const [podName, setPodName] = useState("payment-api-7b89d6b47c-2x9wl");
  const [troubleshootNs, setTroubleshootNs] = useState("production");
  const [describeLogs, setDescribeLogs] = useState("");
  const [troubleshooting, setTroubleshooting] = useState(false);
  const [troubleshootResult, setTroubleshootResult] = useState<PodTroubleshootResponse | null>(null);
  const [troubleshootError, setTroubleshootError] = useState<string | null>(null);

  const checkK8sHealth = async () => {
    try {
      const h = await opsApi.getK8sHealth();
      setK8sHealth(h);
    } catch {
      setK8sHealth(null);
    }
  };

  useEffect(() => {
    checkK8sHealth();
    const interval = setInterval(checkK8sHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    async function loadSamples() {
      try {
        setLoadingSamples(true);
        const data = await opsApi.getK8sSampleRepos();
        setSamples(data);
        const localSample = data.find((s) => s.repo_source === "local");
        if (localSample?.local_path) {
          setLocalPath(localSample.local_path);
          setAppName("opspilot");
        }
      } catch (err) {
        console.error("Failed to load sample repos:", err);
      } finally {
        setLoadingSamples(false);
      }
    }
    loadSamples();
  }, []);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleDownloadYaml = (filename: string, content: string) => {
    const blob = new Blob([content], { type: "text/yaml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setAnalyzing(true);
    setAnalysisError(null);
    try {
      const res = await opsApi.analyzeRepo({
        repo_source: repoSource,
        repo_url: repoSource === "github" ? repoUrl : undefined,
        local_path: repoSource === "local" ? localPath : undefined,
        app_name: appName.trim() || undefined,
        namespace: namespace.trim() || "default",
      });
      setAnalysisResult(res);
      setActiveManifestTab("deployment_yaml");
    } catch (err) {
      setAnalysisError(
        err instanceof ApiError ? err.message : "Failed to analyze repository."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelectSample = (sample: SampleRepo) => {
    if (sample.repo_source === "github") {
      setRepoSource("github");
      setRepoUrl(sample.repo_url || "");
      setAppName(sample.id);
    } else {
      setRepoSource("local");
      setLocalPath(sample.local_path || "");
      setAppName(sample.id);
    }
  };

  const handleTroubleshoot = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setTroubleshooting(true);
    setTroubleshootError(null);
    try {
      const res = await opsApi.troubleshootPod({
        pod_name: podName.trim(),
        namespace: troubleshootNs.trim(),
        describe_output: describeLogs,
        pod_logs: describeLogs,
      });
      setTroubleshootResult(res);
    } catch (err) {
      setTroubleshootError(
        err instanceof ApiError ? err.message : "Pod troubleshooting failed."
      );
    } finally {
      setTroubleshooting(false);
    }
  };

  const handleLoadTroubleshootScenario = (
    title: string,
    describe: string,
    logs: string
  ) => {
    setDescribeLogs(`${describe}\n\n--- Container Logs ---\n${logs}`);
    setPodName(`app-${title.toLowerCase().replace(/[^a-z0-9]/g, "-").slice(0, 16)}`);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
      {/* Header Banner */}
      <div className="rounded-2xl border border-slate-200 bg-linear-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 sm:p-8 text-white shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300">
                <Boxes className="h-3.5 w-3.5" />
                Autonomous Kubernetes DevOps Copilot
              </div>
              <div className="inline-flex items-center gap-1.5 rounded-full border border-slate-700 bg-slate-800/80 px-2.5 py-1 text-[11px] font-mono text-slate-300">
                {k8sHealth?.status === "healthy" ? (
                  <>
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-emerald-300 font-medium">Backend Online (Port 8002)</span>
                  </>
                ) : (
                  <>
                    <span className="h-2 w-2 rounded-full bg-amber-400" />
                    <span className="text-amber-300 font-medium">Backend Standby (Port 8002)</span>
                  </>
                )}
              </div>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Inspect Any Codebase & Deploy Production Kubernetes
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Feed any public/private GitHub repository or local codebase. OpsPilot automatically detects the technology stack, ports, environment requirements, and generates hardened multi-stage Dockerfiles, production Kubernetes manifests, and step-by-step rollout runbooks.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 rounded-xl bg-slate-800/80 p-1.5 border border-slate-700/60 self-start md:self-auto">
            <button
              onClick={() => setActiveTab("analyze")}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition-all ${
                activeTab === "analyze"
                  ? "bg-emerald-500 text-white shadow-md"
                  : "text-slate-300 hover:text-white hover:bg-slate-700/50"
              }`}
            >
              <FolderGit2 className="h-4 w-4" />
              Repo to K8s Plan
            </button>
            <button
              onClick={() => setActiveTab("troubleshoot")}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold transition-all ${
                activeTab === "troubleshoot"
                  ? "bg-indigo-500 text-white shadow-md"
                  : "text-slate-300 hover:text-white hover:bg-slate-700/50"
              }`}
            >
              <Wrench className="h-4 w-4" />
              Pod Troubleshooter & Remediation
            </button>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: REPO TO KUBERNETES PLAN */}
      {/* ========================================================================= */}
      {activeTab === "analyze" && (
        <div className="space-y-8">
          {/* Quick-Preset Selectors */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Quick-Start Application Presets
              </span>
              <span className="text-xs text-slate-400">Click to auto-populate</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {samples.map((s) => (
                <button
                  key={s.id}
                  onClick={() => handleSelectSample(s)}
                  className="flex flex-col text-left p-3.5 rounded-xl border border-slate-200 bg-white hover:border-emerald-500 hover:shadow-xs transition-all group"
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <span className="font-semibold text-xs text-slate-900 group-hover:text-emerald-700">
                      {s.name}
                    </span>
                    <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-mono text-slate-600">
                      {s.language}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                    {s.description}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Repository Input Form */}
          <form
            onSubmit={handleAnalyze}
            className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-6"
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div className="flex items-center gap-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                  <Terminal className="h-4 w-4" />
                </span>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">
                    Repository Configuration
                  </h3>
                  <p className="text-xs text-slate-500">
                    Choose between a remote Git repository or a local workspace folder
                  </p>
                </div>
              </div>

              {/* Source Switcher */}
              <div className="inline-flex rounded-lg bg-slate-100 p-1">
                <button
                  type="button"
                  onClick={() => setRepoSource("local")}
                  className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-medium transition-all ${
                    repoSource === "local"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <FolderOpen className="h-3.5 w-3.5" />
                  Local Workspace
                </button>
                <button
                  type="button"
                  onClick={() => setRepoSource("github")}
                  className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-medium transition-all ${
                    repoSource === "github"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <FolderGit2 className="h-3.5 w-3.5" />
                  GitHub URL
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
              {repoSource === "local" ? (
                <div className="md:col-span-6 space-y-1">
                  <label className="text-xs font-semibold text-slate-700">
                    Local Directory Path
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="/Users/username/projects/my-app"
                    value={localPath}
                    onChange={(e) => setLocalPath(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-mono text-slate-900 focus:border-emerald-500 focus:outline-hidden"
                  />
                  <p className="text-[11px] text-slate-400">
                    Absolute or relative path to the project on this machine
                  </p>
                </div>
              ) : (
                <div className="md:col-span-6 space-y-1">
                  <label className="text-xs font-semibold text-slate-700">
                    GitHub Repository URL
                  </label>
                  <input
                    type="url"
                    required
                    placeholder="https://github.com/organization/repository"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    className="w-full rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-mono text-slate-900 focus:border-emerald-500 focus:outline-hidden"
                  />
                  <p className="text-[11px] text-slate-400">
                    Shallow-cloned securely into an ephemeral sandbox for inspection
                  </p>
                </div>
              )}

              <div className="md:col-span-3 space-y-1">
                <label className="text-xs font-semibold text-slate-700">
                  Application Name (K8s)
                </label>
                <input
                  type="text"
                  placeholder="e.g. order-api"
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-mono text-slate-900 focus:border-emerald-500 focus:outline-hidden"
                />
                <p className="text-[11px] text-slate-400">
                  Used as the Kubernetes resource identifier prefix
                </p>
              </div>

              <div className="md:col-span-3 space-y-1">
                <label className="text-xs font-semibold text-slate-700">
                  Target Namespace
                </label>
                <input
                  type="text"
                  placeholder="default"
                  value={namespace}
                  onChange={(e) => setNamespace(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-mono text-slate-900 focus:border-emerald-500 focus:outline-hidden"
                />
                <p className="text-[11px] text-slate-400">
                  Kubernetes cluster target namespace
                </p>
              </div>
            </div>

            {analysisError && (
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-start gap-3">
                <AlertTriangle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
                <div>
                  <span className="font-bold">Inspection Error:</span> {analysisError}
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={analyzing}
                className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-6 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 transition-colors"
              >
                {analyzing ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin text-emerald-400" />
                    Scanning Repository & Synthesizing K8s Plan...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 text-emerald-400" />
                    Analyze Codebase & Generate Production Kubernetes Plan
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Analysis Results View */}
          {analysisResult && (
            <div className="space-y-8 animate-in fade-in duration-300">
              {/* Stack Architecture Highlights */}
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Primary Stack
                  </span>
                  <div className="mt-1 flex items-center gap-1.5">
                    <Code2 className="h-4 w-4 text-indigo-500" />
                    <span className="text-sm font-bold text-slate-900">
                      {analysisResult.detected_stack.framework}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {analysisResult.detected_stack.primary_language}
                  </span>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Container Port
                  </span>
                  <div className="mt-1 flex items-center gap-1.5">
                    <Cpu className="h-4 w-4 text-emerald-500" />
                    <span className="text-sm font-bold text-slate-900 font-mono">
                      TCP {analysisResult.detected_stack.recommended_port}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500">
                    {analysisResult.detected_stack.detected_ports.length > 0
                      ? `Detected from source`
                      : `Framework default`}
                  </span>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Health Probe Route
                  </span>
                  <div className="mt-1 flex items-center gap-1.5">
                    <Activity className="h-4 w-4 text-cyan-500" />
                    <span className="text-sm font-bold text-slate-900 font-mono">
                      {analysisResult.detected_stack.health_endpoint}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500">Startup & Ready</span>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Backing Services
                  </span>
                  <div className="mt-1 flex items-center gap-1.5">
                    <Server className="h-4 w-4 text-amber-500" />
                    <span className="text-sm font-bold text-slate-900">
                      {analysisResult.detected_stack.backing_services.length > 0
                        ? analysisResult.detected_stack.backing_services.join(", ")
                        : "Stateless"}
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500">Dependencies</span>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Discovered Env Vars
                  </span>
                  <div className="mt-1 flex items-center gap-1.5">
                    <Zap className="h-4 w-4 text-purple-500" />
                    <span className="text-sm font-bold text-slate-900 font-mono">
                      {analysisResult.detected_stack.detected_env_vars.length} Keys
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500">ConfigMap / Secret</span>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-2xs">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Scanned Files
                  </span>
                  <div className="mt-1 flex items-center gap-1.5">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                    <span className="text-sm font-bold text-slate-900 font-mono">
                      {analysisResult.detected_stack.total_files_scanned} files
                    </span>
                  </div>
                  <span className="text-[11px] text-slate-500">Deep inspection</span>
                </div>
              </div>

              {/* Manifest Workbench */}
              <div className="rounded-2xl border border-slate-200 bg-white shadow-xs overflow-hidden">
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between border-b border-slate-200 bg-slate-50/80 px-4 py-3 gap-3">
                  <div className="flex items-center gap-2 overflow-x-auto">
                    {[
                      { key: "deployment_yaml", label: "deployment.yaml", icon: Layers },
                      { key: "dockerfile", label: "Dockerfile", icon: FileCode2 },
                      { key: "service_yaml", label: "service.yaml", icon: Server },
                      { key: "configmap_yaml", label: "configmap.yaml", icon: Zap },
                      { key: "secret_yaml", label: "secret.yaml", icon: ShieldCheck },
                      { key: "ingress_yaml", label: "ingress.yaml", icon: ExternalLink },
                      { key: "hpa_yaml", label: "hpa.yaml", icon: Cpu },
                      { key: "all_in_one_yaml", label: "k8s-all-in-one.yaml", icon: Boxes },
                    ].map((tab) => {
                      const Icon = tab.icon;
                      const isActive = activeManifestTab === tab.key;
                      return (
                        <button
                          key={tab.key}
                          onClick={() => setActiveManifestTab(tab.key)}
                          className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-mono font-medium transition-all shrink-0 ${
                            isActive
                              ? "bg-slate-900 text-white shadow-xs"
                              : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/60"
                          }`}
                        >
                          <Icon className="h-3.5 w-3.5" />
                          {tab.label}
                        </button>
                      );
                    })}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() =>
                        handleCopy(
                          (analysisResult.manifests as unknown as Record<string, string>)[activeManifestTab] || "",
                          activeManifestTab
                        )
                      }
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 transition-colors"
                    >
                      {copiedKey === activeManifestTab ? (
                        <>
                          <Check className="h-3.5 w-3.5 text-emerald-600" />
                          <span className="text-emerald-700">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-3.5 w-3.5 text-slate-500" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={() =>
                        handleDownloadYaml(
                          `${analysisResult.app_name}-k8s-bundle.yaml`,
                          analysisResult.manifests.all_in_one_yaml
                        )
                      }
                      className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors shadow-xs"
                    >
                      <Download className="h-3.5 w-3.5" />
                      Download YAML Bundle
                    </button>
                  </div>
                </div>

                {/* Code Body */}
                <div className="relative bg-slate-950 p-4 overflow-x-auto text-slate-100 font-mono text-xs leading-relaxed max-h-[500px]">
                  <pre>
                    {(analysisResult.manifests as unknown as Record<string, string>)[activeManifestTab]}
                  </pre>
                </div>
              </div>

              {/* Step-by-Step Production Deployment Runbook */}
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-emerald-600" />
                  <h3 className="text-base font-bold text-slate-900">
                    Production Rollout Execution Runbook
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysisResult.deployment_steps.map((step) => (
                    <div
                      key={step.step_number}
                      className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-3"
                    >
                      <div className="flex items-center gap-3">
                        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-emerald-400">
                          {step.step_number}
                        </span>
                        <h4 className="text-xs font-bold text-slate-900">
                          {step.title}
                        </h4>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {step.description}
                      </p>

                      <div className="space-y-1.5">
                        {step.commands.map((cmd, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between rounded-lg bg-slate-900 px-3 py-2 text-xs font-mono text-slate-200"
                          >
                            <span className="truncate pr-2">{cmd}</span>
                            <button
                              onClick={() => handleCopy(cmd, `cmd-${step.step_number}-${idx}`)}
                              className="text-slate-400 hover:text-white shrink-0"
                              title="Copy command"
                            >
                              {copiedKey === `cmd-${step.step_number}-${idx}` ? (
                                <Check className="h-3.5 w-3.5 text-emerald-400" />
                              ) : (
                                <Copy className="h-3.5 w-3.5" />
                              )}
                            </button>
                          </div>
                        ))}
                      </div>

                      {step.verification && (
                        <div className="rounded-md bg-emerald-50/70 border border-emerald-100 p-2.5 text-[11px] text-emerald-800 flex items-start gap-2">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0 mt-0.5" />
                          <span>
                            <strong className="font-semibold">Verify:</strong> {step.verification}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Production Hardening & Recommendations */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-3">
                  <div className="flex items-center gap-2 text-emerald-700">
                    <ShieldCheck className="h-4 w-4" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                      Security & Non-Root Hardening
                    </h4>
                  </div>
                  <ul className="space-y-2">
                    {analysisResult.security_hardening.map((item, idx) => (
                      <li
                        key={idx}
                        className="text-xs text-slate-600 flex items-start gap-2"
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-3">
                  <div className="flex items-center gap-2 text-indigo-700">
                    <Cpu className="h-4 w-4" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">
                      High Availability & Scale Recommendations
                    </h4>
                  </div>
                  <ul className="space-y-2">
                    {analysisResult.production_recommendations.map((item, idx) => (
                      <li
                        key={idx}
                        className="text-xs text-slate-600 flex items-start gap-2"
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: POD TROUBLESHOOTER & AUTO-REMEDIATION */}
      {/* ========================================================================= */}
      {activeTab === "troubleshoot" && (
        <div className="space-y-8">
          {/* Preset Failure Scenario Buttons */}
          <div className="space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Simulate Real Production Pod Outages
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() =>
                  handleLoadTroubleshootScenario(
                    "db-conn-refused",
                    "State: Waiting (CrashLoopBackOff)\nLast State: Terminated (Exit Code 1)\nEvents: Back-off restarting failed container in pod auth-service-7b89d6b47c-2x9wl",
                    "psycopg.OperationalError: connection to server at '127.0.0.1', port 5432 failed: Connection refused\nIs the server running on host '127.0.0.1' and accepting TCP/IP connections?"
                  )
                }
                className="flex flex-col text-left p-3.5 rounded-xl border border-slate-200 bg-white hover:border-indigo-500 hover:shadow-xs transition-all"
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="font-semibold text-xs text-slate-900">
                    CrashLoopBackOff
                  </span>
                  <span className="rounded bg-rose-50 px-1.5 py-0.5 text-[10px] font-mono text-rose-700">
                    Exit 1
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Container boots before PostgreSQL TCP socket is ready or uses localhost.
                </p>
              </button>

              <button
                type="button"
                onClick={() =>
                  handleLoadTroubleshootScenario(
                    "oom-killed",
                    "State: Terminated\nReason: OOMKilled\nExit Code: 137\nLast State: Terminated (Exit Code: 137)",
                    "FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory"
                  )
                }
                className="flex flex-col text-left p-3.5 rounded-xl border border-slate-200 bg-white hover:border-indigo-500 hover:shadow-xs transition-all"
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="font-semibold text-xs text-slate-900">
                    OOMKilled
                  </span>
                  <span className="rounded bg-rose-50 px-1.5 py-0.5 text-[10px] font-mono text-rose-700">
                    Exit 137
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Pod memory exceeded cgroup memory limit under spike load.
                </p>
              </button>

              <button
                type="button"
                onClick={() =>
                  handleLoadTroubleshootScenario(
                    "image-pull-auth",
                    "Events: Failed to pull image \"myregistry.azurecr.io/billing-api:v2.1.0\": rpc error: code = Unknown desc = unexpected status code 401 Unauthorized\nState: Waiting (ImagePullBackOff)",
                    ""
                  )
                }
                className="flex flex-col text-left p-3.5 rounded-xl border border-slate-200 bg-white hover:border-indigo-500 hover:shadow-xs transition-all"
              >
                <div className="flex items-center justify-between w-full mb-1">
                  <span className="font-semibold text-xs text-slate-900">
                    ImagePullBackOff
                  </span>
                  <span className="rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-mono text-amber-700">
                    Auth 401
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Private registry auth token missing in pod imagePullSecrets.
                </p>
              </button>
            </div>
          </div>

          {/* Troubleshooter Form */}
          <form
            onSubmit={handleTroubleshoot}
            className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-5"
          >
            <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                <Wrench className="h-4 w-4" />
              </span>
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Live Pod Diagnostic Studio
                </h3>
                <p className="text-xs text-slate-500">
                  Paste output from `kubectl describe pod` or `kubectl logs` for instant root cause diagnosis and YAML patch generation
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-700">
                  Pod Identifier
                </label>
                <input
                  type="text"
                  required
                  value={podName}
                  onChange={(e) => setPodName(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-mono text-slate-900 focus:border-indigo-500 focus:outline-hidden"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-700">
                  Namespace
                </label>
                <input
                  type="text"
                  required
                  value={troubleshootNs}
                  onChange={(e) => setTroubleshootNs(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 px-3.5 py-2 text-xs font-mono text-slate-900 focus:border-indigo-500 focus:outline-hidden"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-700">
                Pod Logs / Events / Stacktrace
              </label>
              <textarea
                rows={6}
                required
                placeholder="Paste `kubectl describe pod <name>` or container stderr logs here..."
                value={describeLogs}
                onChange={(e) => setDescribeLogs(e.target.value)}
                className="w-full rounded-lg border border-slate-200 p-3 text-xs font-mono text-slate-900 focus:border-indigo-500 focus:outline-hidden leading-relaxed"
              />
            </div>

            {troubleshootError && (
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
                {troubleshootError}
              </div>
            )}

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={troubleshooting}
                className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-6 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {troubleshooting ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin text-indigo-200" />
                    Diagnosing Pod Lifecycle & Synthesizing Fix...
                  </>
                ) : (
                  <>
                    <Wrench className="h-4 w-4" />
                    Troubleshoot Pod & Generate Remediation Patch
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Troubleshooter Results */}
          {troubleshootResult && (
            <div className="space-y-6 animate-in fade-in duration-300">
              {/* Diagnosis Summary Banner */}
              <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Detected Pod Issue
                    </span>
                    <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-rose-600" />
                      {troubleshootResult.detected_issue}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-mono font-medium text-slate-700">
                      Pod: {troubleshootResult.pod_name}
                    </span>
                    <span className="rounded-full bg-emerald-50 border border-emerald-200 px-2.5 py-1 text-xs font-semibold text-emerald-800">
                      Confidence: {troubleshootResult.confidence.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-900">
                    Root Cause Analysis:
                  </h4>
                  <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                    {troubleshootResult.root_cause}
                  </p>
                </div>

                {/* Extracted Evidence */}
                {troubleshootResult.evidence.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-slate-900">
                      Extracted Log Evidence:
                    </h4>
                    <div className="space-y-1">
                      {troubleshootResult.evidence.map((ev, idx) => (
                        <div
                          key={idx}
                          className="rounded bg-slate-900 px-3 py-1.5 font-mono text-[11px] text-amber-300"
                        >
                          {ev}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Remediation YAML Patch & Commands */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                {troubleshootResult.yaml_patch && (
                  <div className="md:col-span-7 rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                        <FileCode2 className="h-4 w-4 text-emerald-600" />
                        Kubernetes Manifest Remediation Patch
                      </h4>
                      <button
                        onClick={() =>
                          handleCopy(troubleshootResult.yaml_patch || "", "yaml-patch")
                        }
                        className="inline-flex items-center gap-1 rounded border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] font-medium text-slate-700 hover:bg-slate-100"
                      >
                        {copiedKey === "yaml-patch" ? (
                          <>
                            <Check className="h-3 w-3 text-emerald-600" />
                            <span>Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3" />
                            <span>Copy Patch</span>
                          </>
                        )}
                      </button>
                    </div>

                    <pre className="rounded-lg bg-slate-950 p-3.5 text-[11px] font-mono text-emerald-400 overflow-x-auto leading-relaxed">
                      {troubleshootResult.yaml_patch}
                    </pre>
                  </div>
                )}

                <div
                  className={`${
                    troubleshootResult.yaml_patch ? "md:col-span-5" : "md:col-span-12"
                  } rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-4`}
                >
                  <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    <Terminal className="h-4 w-4 text-indigo-600" />
                    Operator CLI Remediation Commands
                  </h4>

                  <div className="space-y-2">
                    {troubleshootResult.recommended_commands.map((cmd, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between rounded-lg bg-slate-900 px-3 py-2 text-xs font-mono text-slate-200"
                      >
                        <span className="truncate pr-2">{cmd}</span>
                        <button
                          onClick={() => handleCopy(cmd, `fix-cmd-${idx}`)}
                          className="text-slate-400 hover:text-white shrink-0"
                          title="Copy command"
                        >
                          {copiedKey === `fix-cmd-${idx}` ? (
                            <Check className="h-3.5 w-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="h-3.5 w-3.5" />
                          )}
                        </button>
                      </div>
                    ))}
                  </div>

                  {troubleshootResult.preventative_guidance.length > 0 && (
                    <div className="space-y-1.5 pt-2 border-t border-slate-100">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Preventative Guardrails
                      </span>
                      <ul className="space-y-1">
                        {troubleshootResult.preventative_guidance.map((g, idx) => (
                          <li
                            key={idx}
                            className="text-xs text-slate-600 flex items-start gap-1.5"
                          >
                            <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 mt-1.5 shrink-0" />
                            <span>{g}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
