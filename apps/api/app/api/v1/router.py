from fastapi import APIRouter
from app.api.v1.endpoints import incidents, scenarios

api_router = APIRouter(prefix="/api")
api_router.include_router(incidents.router, tags=["Incidents"])
api_router.include_router(scenarios.router, tags=["Demo Scenarios"])
