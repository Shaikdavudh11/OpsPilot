from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    """
    Standard health check endpoint reporting service status,
    active AI provider, and timestamp.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
