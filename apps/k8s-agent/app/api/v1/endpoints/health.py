from fastapi import APIRouter, status

try:
    from app.core.config import settings
    from app.schemas.k8s import HealthResponse
except (ImportError, ModuleNotFoundError):
    from ...core.config import settings
    from ...schemas.k8s import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check for Kubernetes Agent API",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        port=settings.PORT,
    )
