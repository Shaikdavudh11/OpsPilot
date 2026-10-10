from abc import ABC, abstractmethod
from app.schemas.incident import IncidentAnalysisResponse


class BaseAIProvider(ABC):
    """
    Abstract base class for all AI incident analysis providers.
    Ensures that mock, local, and external LLM implementations
    conform to the identical contract.
    """

    @abstractmethod
    async def analyze(
        self,
        sanitized_logs: str,
        title: str,
        environment: str,
        service_name: str,
    ) -> IncidentAnalysisResponse:
        """
        Takes sanitized logs and incident metadata, executes the model analysis,
        and returns a validated IncidentAnalysisResponse.
        """
        pass
