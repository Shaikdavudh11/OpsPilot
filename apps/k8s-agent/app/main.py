import sys
from pathlib import Path

# Ensure apps/k8s-agent root is on sys.path
_current_dir = Path(__file__).resolve().parent.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.core.config import settings
    from app.api.v1.endpoints import health
    from app.api.v1.router import api_router
except (ImportError, ModuleNotFoundError):
    from .core.config import settings
    from .api.v1.endpoints import health
    from .api.v1.router import api_router


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="OpsPilot: Autonomous Kubernetes DevOps Copilot & Remediation Service",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(api_router)

    return app


app = create_application()
