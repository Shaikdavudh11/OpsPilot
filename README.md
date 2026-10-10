# OpsPilot — AI-Powered DevOps & SRE Incident Assistant

OpsPilot is an AI-powered incident investigation assistant engineered for Site Reliability Engineers (SREs), DevOps engineers, and cloud architects. It ingests application error logs, container crashes, Kubernetes pod events, and deployment pipeline failures to produce grounded, hallucination-free diagnostic reports with actionable recommendations.

> [!NOTE]
> For the comprehensive engineering review, architecture breakdown, and detailed operator runbook, see [Implementation & Runbook Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/implementation_and_runbook.md).

---

## Key Capabilities

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
│   ├── api/                           # FastAPI backend (Python 3.12+)
│   │   ├── app/
│   │   │   ├── api/v1/endpoints/      # /health, /api/incidents, /api/demo-scenarios
│   │   │   ├── core/                  # config.py, security.py (redactor), prompt_templates.py
│   │   │   ├── db/                    # session.py, models.py (SQLAlchemy)
│   │   │   ├── schemas/               # Pydantic v2 request/response models
│   │   │   └── services/              # analyzer.py, providers/ (Mock, Gemini, OpenAI)
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── web/                           # Next.js 16 (App Router, TypeScript, Tailwind CSS)
│       ├── src/
│       │   ├── app/                   # / (Dashboard), /analyzer, /history
│       │   ├── components/            # UI badges, CommandBox, ResultsView, Navbar
│       │   └── lib/                   # api.ts, types.ts
│       └── Dockerfile
├── docs/
│   ├── architecture.md                # System topology & pipeline specification
│   └── api.md                         # OpenAPI endpoint specifications & schemas
├── examples/
│   └── failure-scenarios/             # 6 standalone realistic failure scenario JSONs
├── tests/
│   └── api/                           # Pytest unit, security, schema, & integration tests
├── .github/
│   └── workflows/ci.yml               # Automated CI test and build workflow
├── docker-compose.yml                 # Multi-container orchestration (Web, API, Postgres)
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

## Local Development (macOS)

### 1. Clone & Setup Environment

```bash
cd OpsPilot
cp .env.example .env
```

### 2. Start the Backend API (FastAPI)

```bash
# Using uv (recommended) or standard venv:
cd apps/api
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Start FastAPI server on port 8000:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify backend health:
```bash
curl http://localhost:8000/health
```

### 3. Start the Frontend (Next.js)

In a separate terminal:
```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

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
