# OpsPilot — Frontend Web Application Documentation

The **Frontend Web Application** (`apps/web`) is a modern Next.js 16 application engineered for Site Reliability Engineers (SREs), DevOps architects, and cloud operators. It provides an executive investigation dashboard, a live log analyzer, incident history audits, and the autonomous Kubernetes Copilot studio.

---

## 1. Technology Stack

- **Framework:** Next.js 16 (App Router, Turbopack, React 19)
- **Language:** TypeScript 5.x (strict mode enabled)
- **Styling:** Tailwind CSS 4.x (with modern SRE slate, emerald, cyan, and indigo accents)
- **Icons:** Lucide React (modern, lightweight SVG icons)
- **Deployment Targets:** Vercel (Edge-optimized), Docker container, or self-hosted Node.js runtime

---

## 2. Monorepo Directory Layout (`apps/web/`)

```
apps/web/
├── src/
│   ├── app/                           # Next.js App Router Pages
│   │   ├── page.tsx                   # Executive SRE Dashboard (/)
│   │   ├── layout.tsx                 # Root Layout with Navbar & Footer
│   │   ├── globals.css                # Global CSS resets & Tailwind styling
│   │   ├── k8s-agent/
│   │   │   └── page.tsx               # Kubernetes Copilot & Diagnostic Studio (/k8s-agent)
│   │   ├── analyzer/
│   │   │   └── page.tsx               # Incident Log Ingestion & Analysis (/analyzer)
│   │   └── history/
│   │       └── page.tsx               # Incident History & Audit Reports (/history)
│   │
│   ├── components/                    # Modular Reusable UI Components
│   │   ├── layout/
│   │   │   ├── Navbar.tsx             # Sticky header with multi-service connectivity status
│   │   │   └── Footer.tsx             # Standard footer with version and documentation links
│   │   ├── results/
│   │   │   ├── ResultsView.tsx        # Comprehensive diagnostic report viewer
│   │   │   ├── EvidenceCard.tsx       # Quoted verbatim findings with line badges
│   │   │   ├── CommandBox.tsx         # Copyable diagnostic CLI commands with safety tags
│   │   │   └── MitigationSteps.tsx    # Prioritized remediation actions
│   │   └── ui/
│   │       ├── Badge.tsx              # Severity & risk level indicators (critical, high, medium, low)
│   │       └── Modal.tsx              # Reusable modal overlays
│   │
│   └── lib/
│       ├── api.ts                     # Typed multi-backend API client
│       └── types.ts                   # TypeScript interfaces matching backend contracts
│
├── .env.local                         # Local environment configuration
├── Dockerfile                         # Containerized Next.js standalone build
├── package.json                       # Scripts and dependencies
└── tsconfig.json                      # Strict TypeScript compiler options
```

---

## 3. Application Pages & Features

### 1. Executive SRE Dashboard (`/`)
- High-level metrics: Total incidents analyzed, critical/high severity distribution, backend connectivity indicators.
- Quick-launch cards: Direct buttons to investigate logs or launch the Kubernetes Copilot.
- Failure scenario presets: One-click launching of 6 pre-baked real-world outages.

### 2. Autonomous Kubernetes Copilot (`/k8s-agent`)
- **Tab 1: Repository to Kubernetes Plan**:
  - Ingests public/private GitHub repository URLs or local machine folders.
  - Interactive status indicator: Scanning repo -> Detecting stack -> Generating Dockerfile & manifests.
  - Stack Architecture summary cards: Primary language, framework, exposed TCP port, health check probe path, backing services, discovered environment variable count.
  - Manifest Workbench: Tabbed syntax-highlighted code explorer for `deployment.yaml`, `Dockerfile`, `service.yaml`, `configmap.yaml`, `secret.yaml`, `ingress.yaml`, `hpa.yaml`, and `k8s-all-in-one.yaml`.
  - Copy and 1-click **Download All-in-One YAML Bundle**.
  - Step-by-step production rollout runbook with copyable terminal commands.
- **Tab 2: Pod Troubleshooter & Diagnostic Studio**:
  - Ingests pod exit logs or `kubectl describe pod` output.
  - Instant root cause diagnosis, extracted verbatim evidence, drop-in YAML patch diff, and operator fix commands.
  - Quick-preset simulators: CrashLoopBackOff (Database connection refused), OOMKilled (Exit Code 137), ImagePullBackOff (Auth missing), and Probe Timeout.
- **Live Health Indicator:** Real-time badge tracking connectivity to the dedicated Kubernetes Agent backend on Port 8002.

### 3. Incident Analyzer (`/analyzer`)
- Paste raw multi-line stack traces, Kubernetes pod events, container crash logs, or CI/CD logs.
- Interactive Secret Redaction Preview: Displays scrubbed sensitive tokens (AWS keys, passwords, JWTs) prior to analysis.
- AI Provider status indicator: Displays active engine (Mock, Gemini, or OpenAI).
- Formatted investigation results with root cause reasoning, verbatim evidence quotes, and actionable recommendations.

### 4. Incident History & Audit Trail (`/history`)
- Persistent SQLite / PostgreSQL audit logs of all past incident investigations.
- Real-time search by service name, environment, or keyword.
- Filter by severity (Critical, High, Medium, Low).
- Detailed report modal for reviewing past investigations.

---

## 4. Multi-Backend API Client Architecture

The frontend communicates with **two independent backend services**:

```
                       ┌───────────────────────────────┐
                       │     Next.js Frontend (:3000)   │
                       └───────────────┬───────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                │                                             │
      opsApi.analyzeIncident()                       opsApi.analyzeRepo()
      opsApi.getIncidents()                          opsApi.troubleshootPod()
                │                                             │
                ▼                                             ▼
┌───────────────────────────────┐             ┌───────────────────────────────┐
│     apps/api (Port 8001)      │             │    apps/k8s-agent (Port 8002) │
│    NEXT_PUBLIC_API_URL        │             │  NEXT_PUBLIC_K8S_API_URL      │
└───────────────────────────────┘             └───────────────────────────────┘
```

### Environment Configuration (`apps/web/.env.local`)
```env
# Incident Investigation Backend
NEXT_PUBLIC_API_URL=http://localhost:8001

# Autonomous Kubernetes Agent Backend
NEXT_PUBLIC_K8S_API_URL=http://localhost:8002
```

### Centralized Client (`apps/web/src/lib/api.ts`)
The `request<T>()` helper function handles:
- Dynamic base URL routing (`API_BASE_URL` vs. `K8S_API_BASE_URL`)
- Consistent JSON headers and error serialization
- Detailed `ApiError` class with HTTP status codes and backend validation details
- `cache: "no-store"` for real-time dynamic data fetching

---

## 5. Local Development & Build

### Install Dependencies:
```bash
cd apps/web
npm install
```

### Run Development Server (with Turbopack):
```bash
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

### Typecheck & Production Build:
```bash
npm run build
```
Generates an optimized standalone build ready for zero-cost deployment on Vercel or in a Docker container.
