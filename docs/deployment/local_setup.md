# OpsPilot — Local Development, Setup & Run Guide

This step-by-step guide walks you through setting up and running the entire OpsPilot platform on your local machine (macOS or Linux).

---

## 1. System Overview & Port Allocation

OpsPilot runs 3 independent services locally:

```
┌────────────────────────────────────────────────────────┐
│               Frontend: Next.js 16 Web                 │
│                 http://localhost:3000                  │
└───────────────┬────────────────────────┬───────────────┘
                │                        │
       REST HTTP (Port 8001)    REST HTTP (Port 8002)
                │                        │
┌───────────────▼────────┐      ┌────────▼───────────────┐
│ Incident API (FastAPI) │      │  K8s Agent (FastAPI)   │
│ http://localhost:8001  │      │ http://localhost:8002  │
│  (Docs: /docs)         │      │  (Docs: /docs)         │
└────────────────────────┘      └────────────────────────┘
```

| Service | Directory | Local URL | Swagger Docs | Port | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend Web** | `apps/web` | `http://localhost:3000` | N/A | **`3000`** | Next.js 16 SRE Dashboard & K8s Copilot Studio |
| **Incident API** | `apps/api` | `http://localhost:8001` | `/docs` | **`8001`** | Log redaction, root cause analysis, mock/Gemini/OpenAI |
| **K8s Agent** | `apps/k8s-agent` | `http://localhost:8002` | `/docs` | **`8002`** | Repo inspection, K8s manifests synthesis, pod diagnostics |

---

## 2. Prerequisites

Ensure you have the following installed on your machine:

1. **Python 3.12+** (verify with `python3 --version`)
2. **`uv`** (recommended ultra-fast Python package manager) or standard `python3 -m venv`
   - Install `uv` on macOS via Homebrew: `brew install uv` (or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
3. **Node.js 20+ & npm** (verify with `node -v` and `npm -v`)
4. **Git** (verify with `git --version`)
5. *(Optional)* **Kind** or **Docker Desktop** (if you want to apply manifests directly to a local Kubernetes cluster)

---

## 3. Step-by-Step Setup & Run

### Step 1: Configure Environment Variables

From the root `OpsPilot` directory, create the `.env` files for each service:

```bash
cd /Users/shaik/Desktop/DevOpsProjects/OpsPilot

# 1. Incident API environment
cp apps/api/.env.example apps/api/.env 2>/dev/null || cat <<EOF > apps/api/.env
ENVIRONMENT=development
PORT=8001
HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8001"]
MAX_LOG_SIZE_CHARS=65536
DATABASE_URL=sqlite:///./opspilot.db
AI_PROVIDER=mock
NEXT_PUBLIC_API_URL=http://localhost:8001
EOF

# 2. Kubernetes Agent environment
cp apps/k8s-agent/.env.example apps/k8s-agent/.env 2>/dev/null || cat <<EOF > apps/k8s-agent/.env
ENVIRONMENT=development
PORT=8002
HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8002"]
PROJECT_NAME=OpsPilot Kubernetes Agent API
VERSION=1.0.0
EOF

# 3. Web Frontend environment
cat <<EOF > apps/web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_K8S_API_URL=http://localhost:8002
EOF
```

---

### Step 2: Start the Incident Backend API (Terminal 1)

In your first terminal tab:

```bash
cd /Users/shaik/Desktop/DevOpsProjects/OpsPilot/apps/api

# Using uv (fastest):
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Or using standard python:
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt

# Start FastAPI server on port 8001:
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Verify Terminal 1:**
- Open [http://localhost:8001/health](http://localhost:8001/health) (returns `{"status":"healthy","service":"OpsPilot API",...}`)
- Open [http://localhost:8001/docs](http://localhost:8001/docs) (Interactive Swagger UI)

---

### Step 3: Start the Kubernetes Agent Backend API (Terminal 2)

In a second terminal tab:

```bash
cd /Users/shaik/Desktop/DevOpsProjects/OpsPilot/apps/k8s-agent

# Using uv:
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Start FastAPI server on port 8002:
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Verify Terminal 2:**
- Open [http://localhost:8002/health](http://localhost:8002/health) (returns `{"status":"healthy","service":"OpsPilot Kubernetes Agent API",...}`)
- Open [http://localhost:8002/docs](http://localhost:8002/docs) (Interactive Swagger UI)

---

### Step 4: Start the Web Frontend (Terminal 3)

In a third terminal tab:

```bash
cd /Users/shaik/Desktop/DevOpsProjects/OpsPilot/apps/web

# Install frontend dependencies:
npm install

# Start Next.js development server on port 3000:
npm run dev
```

**Open in Browser:**
- **Executive SRE Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Kubernetes Copilot Studio:** [http://localhost:3000/k8s-agent](http://localhost:3000/k8s-agent)
- **Incident Log Analyzer:** [http://localhost:3000/analyzer](http://localhost:3000/analyzer)
- **Incident Audit History:** [http://localhost:3000/history](http://localhost:3000/history)

---

## 4. Alternative: 1-Command Run with Docker Compose

If you have Docker Desktop installed, you can start the entire stack (PostgreSQL + Incident API + Kubernetes Agent + Web) in containers with a single command:

```bash
cd /Users/shaik/Desktop/DevOpsProjects/OpsPilot
docker-compose up --build
```

- Web UI: [http://localhost:3000](http://localhost:3000)
- Incident API: [http://localhost:8000/docs](http://localhost:8000/docs)
- K8s Agent API: [http://localhost:8002/docs](http://localhost:8002/docs)
- PostgreSQL: `localhost:5432`

---

## 5. Running the Test Suites

To verify that your local environment is 100% healthy:

### 1. Test Incident API (11 tests):
```bash
apps/api/.venv/bin/pytest tests/api/ -v
```

### 2. Test Kubernetes Agent (4 tests):
```bash
apps/k8s-agent/.venv/bin/pytest apps/k8s-agent/tests/ -v
```

### 3. Test Frontend TypeScript & Build:
```bash
cd apps/web
npm run build
```

---

## 6. Common Local Troubleshooting

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| **`Address already in use: 8000`** | Docker or another background process is using port 8000. | OpsPilot is pre-configured to use **Port 8001** for Incident API and **Port 8002** for K8s Agent to avoid port 8000 collisions. |
| **`ModuleNotFoundError: No module named 'app'`** | Running `uvicorn` or `python` from the root directory without `PYTHONPATH`. | Always `cd apps/api` or `cd apps/k8s-agent` before running `uvicorn app.main:app`. |
| **`K8s Backend Standby (:8002)` in UI** | The `k8s-agent` service is not running in Terminal 2. | Run `uvicorn app.main:app --port 8002` in `apps/k8s-agent`. Once started, the UI badge updates to green **"Backend Online (Port 8002)"**. |
| **`Pylance reportMissingImports` in IDE** | IDE looking at root workspace instead of sub-packages. | Already fixed via [.vscode/settings.json](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/.vscode/settings.json) with `python.analysis.extraPaths`. |
