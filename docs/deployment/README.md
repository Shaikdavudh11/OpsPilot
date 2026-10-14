# OpsPilot — Unified Deployment Guide

This guide details all deployment strategies for OpsPilot across local development, container orchestration, zero-cost cloud tiers, and production Kubernetes clusters.

---

## 1. System Topology & Ports

OpsPilot is engineered as a clean, modular multi-service architecture:

| Service | Technology | Internal Port | External Port | Role |
| :--- | :--- | :--- | :--- | :--- |
| **`web`** | Next.js 16 (React 19) | `3000` | `3000` | SRE Dashboard, K8s Copilot Studio, Log Analyzer |
| **`api`** | FastAPI (Python 3.12+) | `8001` (local) / `8000` (Docker) | `8001` / `8000` | Incident Log Redaction, SRE Root Cause Analysis |
| **`k8s-agent`**| FastAPI (Python 3.12+) | `8002` | `8002` | Repo Inspector, K8s Manifest Generator, Pod Diagnostician |
| **`db`** | PostgreSQL 16 (Alpine) | `5432` | `5432` | Incident Audit Trail & Report Persistence |

---

## 2. Local Development (macOS / Linux)

### Prerequisites:
- Python 3.12+ (with `uv` or `venv`)
- Node.js 20+ and `npm`
- Git

### Step 1: Clone & Configure Environments
```bash
git clone <repo-url> OpsPilot
cd OpsPilot
```

Create environment files for each service:
```bash
# Incident API config
cp apps/api/.env.example apps/api/.env

# Kubernetes Agent config
cp apps/k8s-agent/.env.example apps/k8s-agent/.env

# Web Frontend config
cp apps/web/.env.example apps/web/.env.local 2>/dev/null || cat <<EOF > apps/web/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_K8S_API_URL=http://localhost:8002
EOF
```

### Step 2: Start the Incident API (Terminal 1)
```bash
cd apps/api
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
Verify health:
```bash
curl http://localhost:8001/health
```

### Step 3: Start the Kubernetes Agent Service (Terminal 2)
```bash
cd apps/k8s-agent
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```
Verify health:
```bash
curl http://localhost:8002/health
```

### Step 4: Start the Web Frontend (Terminal 3)
```bash
cd apps/web
npm install
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

## 3. Container Orchestration (Docker Compose)

To spin up the entire production stack (Postgres + Incident API + Kubernetes Agent + Web) in isolated containers with a single command:

```bash
docker-compose up --build
```

- **Frontend Web UI:** [http://localhost:3000](http://localhost:3000)
- **Incident API Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Kubernetes Agent Swagger:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **PostgreSQL Database:** `localhost:5432`

To shut down:
```bash
docker-compose down -v
```

---

## 4. Zero-Cost Cloud Deployment (100% Free)

OpsPilot is engineered to run seamlessly on free-tier cloud platforms:

### 1. Frontend on Vercel (Edge CDN)
- Import your repository into **Vercel**.
- Set **Root Directory** to `apps/web`.
- Configure Environment Variables:
  - `NEXT_PUBLIC_API_URL`: Your deployed `apps/api` HTTPS URL
  - `NEXT_PUBLIC_K8S_API_URL`: Your deployed `apps/k8s-agent` HTTPS URL
- Click **Deploy**. Vercel builds the standalone Next.js application automatically.

### 2. Backends on Hugging Face Spaces (Docker CPU)
- Create a new Space on **Hugging Face** with **Docker** SDK.
- Point the Dockerfile to [apps/api/Dockerfile.hf](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/apps/api/Dockerfile.hf) or [apps/k8s-agent/Dockerfile](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/apps/k8s-agent/Dockerfile).
- Automatic GitHub Actions CI/CD auto-syncs pushes to your Hugging Face Space.

### 3. Backends on Render (Free Web Service)
- Use the included [render.yaml](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/render.yaml) specification:
  - `rootDir: apps/api` for the incident assistant.
  - `rootDir: apps/k8s-agent` for the Kubernetes agent.

---

## 5. Deploying OpsPilot to Kubernetes (Kind, Minikube, EKS, GKE)

You can deploy OpsPilot itself directly to your local **Kind** or cloud cluster:

### Step 1: Create Namespace
```bash
kubectl create namespace opspilot
```

### Step 2: Deploy PostgreSQL
```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opspilot-db
  namespace: opspilot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: opspilot-db
  template:
    metadata:
      labels:
        app: opspilot-db
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          env:
            - name: POSTGRES_USER
              value: opspilot
            - name: POSTGRES_PASSWORD
              value: opspilot_password
            - name: POSTGRES_DB
              value: opspilot
          ports:
            - containerPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: opspilot-db
  namespace: opspilot
spec:
  selector:
    app: opspilot-db
  ports:
    - port: 5432
      targetPort: 5432
EOF
```

### Step 3: Deploy Incident API & Kubernetes Agent
```bash
# Build & load into your Kind cluster (e.g. demo-kebernetes-ai-agent)
docker build -t opspilot-api:latest -f apps/api/Dockerfile apps/api
docker build -t opspilot-k8s-agent:latest -f apps/k8s-agent/Dockerfile apps/k8s-agent

kind load docker-image opspilot-api:latest --name demo-kebernetes-ai-agent
kind load docker-image opspilot-k8s-agent:latest --name demo-kebernetes-ai-agent
```

### Step 4: Verify Cluster Workloads
```bash
kubectl get pods -n opspilot -o wide
```
Once all pods show `Running (1/1)`, port-forward the web frontend:
```bash
kubectl port-forward -n opspilot svc/opspilot-web 3000:3000
```
