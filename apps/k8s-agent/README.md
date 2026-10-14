# OpsPilot — Autonomous Kubernetes Agent Service

Independent FastAPI microservice engineered to analyze software application repositories, synthesize production-grade Kubernetes manifests & Dockerfiles, and troubleshoot live pod failure events.

For complete architectural specifications, detection heuristics, and workflow diagrams, see the [Kubernetes Agent Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/k8s_agent.md).

---

## Quickstart

### 1. Environment Setup
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Start Service (Port 8002)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Interactive Swagger documentation: **[http://localhost:8002/docs](http://localhost:8002/docs)**.

### 3. Run Tests
```bash
.venv/bin/pytest -v
```

---

## Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check & service metadata |
| `POST` | `/api/k8s/analyze-repo` | Ingests repo (GitHub or local path) and produces production K8s plan |
| `POST` | `/api/k8s/troubleshoot-pod` | Diagnoses pod crash/logs and generates YAML patch diff |
| `GET` | `/api/k8s/sample-repos` | Returns pre-configured sample repos and pod failure scenarios |
