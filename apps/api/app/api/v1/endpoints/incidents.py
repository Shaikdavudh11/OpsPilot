import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.incident import (
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
)
from app.services.analyzer import IncidentAnalyzerService
from app.services.incident_repository import IncidentRepository

logger = logging.getLogger("opspilot.incidents")
router = APIRouter()


@router.post(
    "/incidents/analyze",
    response_model=IncidentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze incident logs and persist report",
    description="Submits application/infrastructure logs for SRE analysis, root cause diagnosis, recommendations, and saves report to database.",
)
async def analyze_incident(
    payload: IncidentAnalysisRequest,
    db: Session = Depends(get_db),
) -> IncidentAnalysisResponse:
    try:
        service = IncidentAnalyzerService()
        result = await service.analyze_incident(payload)

        # Persist to database
        try:
            repo = IncidentRepository(db)
            repo.save_incident(
                analysis=result,
                environment=payload.environment or "production",
                service_name=payload.service_name or "unknown-service",
                raw_logs_snippet=payload.raw_logs,
            )
        except Exception as db_err:
            logger.warning("Could not persist incident to database: %s", str(db_err))

        return result
    except ValueError as ve:
        logger.warning("Validation error during log analysis: %s", str(ve))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve),
        )
    except Exception as exc:
        logger.error("Unexpected error during incident analysis: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while analyzing the incident. Please check server logs.",
        )


@router.get(
    "/incidents",
    summary="List saved incident reports",
    description="Retrieves summaries of previously analyzed incidents from persistence.",
)
def list_incidents(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    repo = IncidentRepository(db)
    return repo.list_incidents(limit=limit)


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentAnalysisResponse,
    summary="Get saved incident report by ID",
    description="Retrieves a complete saved analysis report with all evidence, root cause, recommendations, and limitations.",
)
def get_incident_by_id(
    incident_id: str,
    db: Session = Depends(get_db),
):
    repo = IncidentRepository(db)
    incident = repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID '{incident_id}' not found.",
        )
    return incident
