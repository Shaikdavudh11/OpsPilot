# OpsPilot — AI-Powered DevOps & SRE Incident Assistant

OpsPilot is an AI-powered incident investigation assistant engineered for Site Reliability Engineers (SREs), DevOps engineers, and cloud architects. It ingests application error logs, container crashes, Kubernetes pod events, and deployment pipeline failures to produce grounded, hallucination-free diagnostic reports with actionable recommendations.

> [!NOTE]
> ### 📚 Comprehensive Documentation Library:
> - **[Autonomous Kubernetes Agent Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/k8s-agent/README.md):** Full architecture, detection heuristics, manifest synthesis, pod troubleshooter & Kind cluster guide.
> - **[Frontend Web Application Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/frontend/README.md):** Next.js 16 App Router, UI components, workbench tabs, and multi-backend routing.
> - **[Incident API Service Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/api/README.md):** SRE log analysis, secret redaction, prompt injection defense, and AI providers.
> - **[Unified Deployment Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/deployment/README.md):** Local development, Docker Compose, free cloud tiers, and Kubernetes cluster setup.

---

## Key Capabilities

- **Autonomous Kubernetes Copilot:** Inspects any public/private GitHub repository or local codebase, detects language, framework, ports, and environment variables, and generates hardened multi-stage Dockerfiles, production Kubernetes manifests (Deployment, Service, ConfigMap, Secret, Ingress, HPA), and step-by-step rollout runbooks.
- **Live Pod Diagnostic Studio & Auto-Remediation:** Diagnoses real pod outages (CrashLoopBackOff, OOMKilled 137, ImagePullBackOff, probe failures), extracts root causes, generates YAML patch diffs, and provides operator CLI fix commands.
- **Factual Evidence Extraction:** Quotes verbatim findings directly from logs. Never hallucinates non-existent lines or unvisited clusters.
- **Automated Secret Redaction:** Scrubs AWS access keys, GitHub tokens, database passwords in connection strings, Bearer tokens, JWTs, and private keys before passing text to AI models.
- **Prompt Injection Defense:** Strict separation between system directives and untrusted evidentiary log payloads.
- **Deterministic Mock Provider:** Works 100% out of the box with zero external API keys or paid credits required.
- **Pluggable Real AI Engines:** Configurable integration with Google Gemini or OpenAI-compatible endpoints via server-side environment variables.
- **Suggested Commands with Safety Guards:** Diagnostic CLI commands are clearly flagged as operator suggestions and are never auto-executed by the system.
- **Incident History & Audit Trail:** Persistent report storage with local zero-config SQLite or production PostgreSQL via SQLAlchemy.

---

## Monorepo Architecture

```
OpsPilot/
├── apps/
│   ├── api/                           # Incident Investigation API (FastAPI, Port 8001)
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/      # /health, /api/incidents, /api/demo-scenarios
│   │   │   ├── core/                  # security.py (redactor), prompt_templates.py
│   │   │   ├── db/                    # models.py, session.py (SQLAlchemy)
│   │   │   └── services/              # analyzer.py, providers/ (Mock, Gemini, OpenAI)
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── k8s-agent/                     # Autonomous Kubernetes Copilot (FastAPI, Port 8002)
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/      # /health, /api/k8s/analyze-repo, /troubleshoot-pod
│   │   │   ├── schemas/               # k8s.py (Pydantic v2 validation contracts)
│   │   │   └── services/              # inspector.py, generator.py, troubleshooter.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── web/                           # Next.js 16 Web Application (Port 3000)
│       ├── src/
│       │   ├── app/                   # / (Dashboard), /k8s-agent, /analyzer, /history
│       │   ├── components/            # UI badges, CommandBox, ResultsView, Navbar
│       │   └── lib/                   # api.ts (Multi-backend router), types.ts
│       └── Dockerfile
├── docs/
│   ├── README.md                      # Documentation index and overview
│   ├── k8s-agent/                     # Complete Kubernetes Agent documentation (README.md)
│   ├── frontend/                      # Next.js 16 frontend documentation (README.md)
│   ├── api/                           # Incident analysis API documentation (README.md)
│   ├── deployment/                    # Local, Docker Compose, Cloud & K8s deployment guides
│   ├── architecture.md                # System topology specification
│   └── api.md                         # OpenAPI specifications
├── examples/
│   └── failure-scenarios/             # 6 standalone realistic failure scenario JSONs
├── tests/
│   └── api/                           # Incident API pytest test suite
├── docker-compose.yml                 # Multi-container orchestration (db, api, k8s-agent, web)
├── .env.example
└── .gitignore
```

---

## Prerequisites

- **macOS or Linux**
- **Python 3.12+** (with `venv` or `uv`)
- **Node.js 20+** and `npm`
- **Docker & Docker Compose** (optional for containerized deployment)

---

> [!TIP]
> For the comprehensive step-by-step local runbook, see the **[Local Setup & Run Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/deployment/local_setup.md)**.

### 1. Configure Environments

```bash
# Configure API
cp apps/api/.env.example apps/api/.env

# Configure Kubernetes Agent
cp apps/k8s-agent/.env.example apps/k8s-agent/.env

# Configure Frontend
cat <<EOF > apps/web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_K8S_API_URL=http://localhost:8002
EOF
```

### 2. Start the Incident Backend API (Terminal 1)

```bash
cd apps/api
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
API Documentation: [http://localhost:8001/docs](http://localhost:8001/docs)

### 3. Start the Kubernetes Agent Backend (Terminal 2)

```bash
cd apps/k8s-agent
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```
K8s Agent Documentation: [http://localhost:8002/docs](http://localhost:8002/docs)

### 4. Start the Web Frontend (Terminal 3)

```bash
cd apps/web
npm install
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## Running with Docker Compose

To run the entire stack (FastAPI + Next.js + PostgreSQL) in containers:

```bash
docker-compose up --build
```

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database:** `localhost:5432`

---

## Free Cloud Deployment (100% Free)

OpsPilot is engineered for zero-cost cloud deployment:
- **Frontend (Next.js):** Deployed on **Vercel** ([Vercel Deployment Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/deployment_guide.md))
- **AI Backend (FastAPI):** Deployed on **Hugging Face Spaces** ([Hugging Face Spaces Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/huggingface_deployment.md)) or **Render** ([Render Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/deployment_guide.md))
- Automated CI/CD: Push to GitHub auto-syncs the backend to Hugging Face Spaces using GitHub Actions.

---

## Running Tests

### Backend Test Suite (Pytest)

The test suite covers schema validation, secret redaction, input boundary limits, deterministic mock scenarios, persistence, and API endpoints:

```bash
# From workspace root:
apps/api/.venv/bin/pytest tests/api/ -v
```

### Frontend Typecheck & Build

```bash
cd apps/web
npm run build
```

---

## 6 Realistic SRE Failure Scenarios

OpsPilot includes 6 preloaded realistic scenarios accessible directly from the Dashboard or Analyzer quick-selector:

1. **PostgreSQL Connection Refused:** `PSQLException` on port 5432 with pool exhaustion and connection timeout.
2. **Docker Container Startup Exit:** Containerized worker crashing with `OCI runtime create failed: permission denied` (exit 126).
3. **Kubernetes CrashLoopBackOff (OOMKilled):** Kernel OOM-killer SIGKILL with exit code 137 and cgroup memory limits.
4. **Kubernetes ImagePullBackOff:** Kubelet failing on missing tag in private container registry.
5. **GitHub Actions CI Test Failure:** Pytest assertion failure on token bucket rate limiter burst test.
6. **Application HTTP 500 Runtime Exception:** Unhandled `KeyError` & `TypeError` producing 500 responses.

---

## AI Provider Configuration

OpsPilot defaults to `AI_PROVIDER=mock`, enabling full local functionality without API credentials.

To enable real AI providers, configure `.env`:

### Google Gemini
```ini
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### OpenAI or Compatible Endpoints (Groq / vLLM / Ollama)
```ini
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
# OPENAI_BASE_URL=https://api.openai.com/v1
```

If an external key is absent or a network call fails, OpsPilot automatically falls back to the deterministic mock engine with an explicit limitation note.

---

## Troubleshooting

- **`API Disconnected` badge in frontend:** Ensure FastAPI is running on port 8000 (`curl http://localhost:8000/health`).
- **Database error on startup:** By default, SQLite stores data in `./opspilot.db`. If you change `DATABASE_URL` to PostgreSQL, ensure the PostgreSQL service is running or use `docker-compose up`.
- **CORS error:** Ensure the frontend URL (`http://localhost:3000`) is present in `CORS_ORIGINS` in `config.py` or `.env`.
