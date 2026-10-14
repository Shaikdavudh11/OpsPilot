# OpsPilot — Engineering Documentation Directory

Welcome to the OpsPilot documentation library. Documentation is organized into dedicated service and deployment directories:

---

## 📂 Documentation Structure

```
docs/
├── frontend/                          # Next.js 16 Web Application Documentation
│   └── README.md                      # Architecture, Pages, Components, & Multi-Backend Router
│
├── api/                               # Incident Investigation API Service Documentation
│   └── README.md                      # Log Redaction, Security, Providers, Database & Testing
│
├── k8s-agent/                         # Autonomous Kubernetes Agent Documentation
│   └── README.md                      # Repo Inspection, Manifest Generator, Pod Troubleshooter
│
└── deployment/                        # Unified Deployment Guides
    ├── local_setup.md                 # 🚀 Complete Local Run, Installation & Setup Guide
    ├── README.md                      # Architecture, Docker Compose, Cloud & Kind/K8s Cluster Setup
    ├── cloud_guide.md                 # Vercel & Render Free Cloud Deployment Guide
    └── huggingface.md                 # Hugging Face Spaces & GitHub Actions CI Sync Guide
```

---

## 📑 Service Guides

### 1. [Kubernetes Agent Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/k8s-agent/README.md)
Detailed specification of the autonomous Kubernetes Copilot:
- Architecture & Mermaid workflows
- Language & framework detection heuristics (Python, Node.js, Go, Java, Rust)
- Production Kubernetes manifest synthesis (Deployment, Service, ConfigMap, Secret, Ingress, HPA)
- CIS Kubernetes Security Benchmark & Non-root enforcement (`USER 10001`)
- Pod lifecycle troubleshooting (CrashLoopBackOff, OOMKilled, ImagePullBackOff, Probe flaps)
- REST API contract reference

### 2. [Frontend Web Application Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/frontend/README.md)
Architecture of the Next.js 16 (React 19) frontend:
- Page routing (`/`, `/k8s-agent`, `/analyzer`, `/history`)
- Reusable UI component design system (Tailwind CSS 4)
- Multi-backend API client routing (`NEXT_PUBLIC_API_URL` vs. `NEXT_PUBLIC_K8S_API_URL`)
- Live service health tracking & error boundaries

### 3. [Incident API Service Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/api/README.md)
FastAPI incident analysis backend specification:
- Automated credential & token scrubbing (`security.py`)
- Prompt injection defense framing (`prompt_templates.py`)
- Multi-provider AI engine (Deterministic Mock, Gemini, OpenAI)
- SQLite & PostgreSQL database persistence via SQLAlchemy 2.0
- 11-test Pytest test suite

### 4. [Unified Deployment Guide](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/docs/deployment/README.md)
Complete deployment manual:
- Local multi-service development setup (Ports 8001, 8002, 3000)
- Docker Compose multi-container orchestration (`db`, `api`, `k8s-agent`, `web`)
- Free cloud deployment (Vercel + Hugging Face / Render)
- Deploying OpsPilot directly to local Kind or cloud Kubernetes clusters
