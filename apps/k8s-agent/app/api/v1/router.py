from fastapi import APIRouter

try:
    from app.api.v1.endpoints import k8s
except (ImportError, ModuleNotFoundError):
    from .endpoints import k8s

api_router = APIRouter(prefix="/api")
api_router.include_router(k8s.router, tags=["Kubernetes Agent"])
