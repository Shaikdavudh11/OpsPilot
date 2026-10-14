import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, status

try:
    from app.schemas.k8s import (
        RepoAnalysisRequest,
        K8sAnalysisResponse,
        PodTroubleshootRequest,
        PodTroubleshootResponse,
        SampleRepo,
    )
    from app.services.inspector import RepoInspector
    from app.services.generator import K8sManifestGenerator
    from app.services.troubleshooter import PodTroubleshooter
except (ImportError, ModuleNotFoundError):
    from ...schemas.k8s import (
        RepoAnalysisRequest,
        K8sAnalysisResponse,
        PodTroubleshootRequest,
        PodTroubleshootResponse,
        SampleRepo,
    )
    from ...services.inspector import RepoInspector
    from ...services.generator import K8sManifestGenerator
    from ...services.troubleshooter import PodTroubleshooter

router = APIRouter(prefix="/k8s")


@router.post(
    "/analyze-repo",
    response_model=K8sAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze software repository and generate production Kubernetes deployment plan",
)
async def analyze_repository(request: RepoAnalysisRequest) -> K8sAnalysisResponse:
    temp_dir = None
    try:
        if request.repo_source == "github":
            if not request.repo_url or not request.repo_url.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="repo_url is required when repo_source is 'github'",
                )
            inspector, temp_dir = RepoInspector.clone_github_repo(
                repo_url=request.repo_url, branch=request.branch or "main"
            )
            repo_ref = request.repo_url
            app_default = request.repo_url.rstrip("/").split("/")[-1].replace(".git", "")

        elif request.repo_source == "local":
            raw_path = (request.local_path or "").strip()
            if not raw_path:
                target_path = Path.cwd().resolve()
            else:
                target_path = Path(raw_path).resolve()

            if not target_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Local path does not exist: {target_path}",
                )
            if not target_path.is_dir():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Local path must be a directory: {target_path}",
                )

            inspector = RepoInspector(str(target_path))
            repo_ref = str(target_path)
            app_default = target_path.name

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported repo_source: '{request.repo_source}'. Must be 'github' or 'local'.",
            )

        detected_stack = inspector.scan()
        app_name = (request.app_name or app_default or "production-app").lower()

        generator = K8sManifestGenerator(
            app_name=app_name,
            namespace=request.namespace or "default",
            stack=detected_stack,
            target_port=request.target_port,
        )

        return generator.generate_all(
            repo_source=request.repo_source,
            repo_ref=repo_ref,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Repository analysis failed: {str(e)}",
        )
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@router.post(
    "/troubleshoot-pod",
    response_model=PodTroubleshootResponse,
    status_code=status.HTTP_200_OK,
    summary="Diagnose Kubernetes pod failure, identify root cause, and generate YAML patch",
)
async def troubleshoot_pod(request: PodTroubleshootRequest) -> PodTroubleshootResponse:
    troubleshooter = PodTroubleshooter()
    return troubleshooter.diagnose(request)


@router.get(
    "/sample-repos",
    response_model=List[SampleRepo],
    status_code=status.HTTP_200_OK,
    summary="Get preset sample repositories and troubleshooting scenarios",
)
async def get_sample_repositories() -> List[SampleRepo]:
    workspace_root = str(Path.cwd().resolve())

    return [
        SampleRepo(
            id="opspilot-workspace",
            name="OpsPilot (Current Local Workspace)",
            description="Inspect the active OpsPilot monorepo locally — FastAPI backend, Next.js frontend, SQLite database.",
            repo_source="local",
            local_path=workspace_root,
            language="Python / TypeScript",
            framework="FastAPI + Next.js",
            sample_pod_issues=[
                {
                    "title": "CrashLoopBackOff: DB Connection Refused",
                    "failure_type": "CrashLoopBackOff",
                    "describe_output": "State: Waiting (CrashLoopBackOff)\nLast State: Terminated (Exit Code 1)\nEvents: Back-off restarting failed container app in pod opspilot-api-7b89d6b47c-2x9wl",
                    "pod_logs": "psycopg.OperationalError: connection to server at '127.0.0.1', port 5432 failed: Connection refused\nIs the server running on host '127.0.0.1' and accepting TCP/IP connections?",
                },
                {
                    "title": "OOMKilled: Exit Code 137 under traffic spike",
                    "failure_type": "OOMKilled",
                    "describe_output": "State: Terminated\nReason: OOMKilled\nExit Code: 137\nStarted: Tue, 14 Oct 2026 10:14:00 +0000\nFinished: Tue, 14 Oct 2026 10:14:22 +0000",
                    "pod_logs": "FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory",
                },
                {
                    "title": "ImagePullBackOff: Private Registry Auth Missing",
                    "failure_type": "ImagePullBackOff",
                    "describe_output": "Failed to pull image \"myregistry.azurecr.io/opspilot-api:v1.0.0\": rpc error: code = Unknown desc = failed to pull and unpack image: failed to resolve reference: unexpected status code 401 Unauthorized",
                    "pod_logs": "",
                },
            ],
        ),
        SampleRepo(
            id="fastapi-realworld",
            name="FastAPI RealWorld Example App (GitHub)",
            description="Production-grade asynchronous Python REST API with PostgreSQL, SQLAlchemy, and JWT authentication.",
            repo_source="github",
            repo_url="https://github.com/nsidnev/fastapi-realworld-example-app",
            language="Python",
            framework="FastAPI",
        ),
        SampleRepo(
            id="express-microservice",
            name="Node.js Express Microservice (GitHub)",
            description="Node.js TypeScript microservice with MongoDB and Redis caching layer.",
            repo_source="github",
            repo_url="https://github.com/goldbergyoni/nodebestpractices",
            language="TypeScript",
            framework="Express.js",
        ),
        SampleRepo(
            id="go-fiber-starter",
            name="Go Fiber Microservice (GitHub)",
            description="High-performance Go lightweight HTTP microservice with health checks and Dockerfile.",
            repo_source="github",
            repo_url="https://github.com/gofiber/recipes",
            language="Go",
            framework="Fiber",
        ),
    ]
