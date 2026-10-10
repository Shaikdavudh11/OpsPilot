import uuid
from datetime import datetime, timezone
from app.core.config import settings
from app.core.security import SecretRedactor, sanitize_and_validate_log_input
from app.schemas.incident import (
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
)
from app.services.providers.base import BaseAIProvider
from app.services.providers.mock import MockAIProvider


class IncidentAnalyzerService:
    """
    Core service layer coordinating incident analysis:
    - Input size and content validation
    - Secret and token redaction
    - AI provider selection and execution
    - Schema validation and metadata enhancement
    """

    def __init__(self, provider: BaseAIProvider | None = None):
        self.provider = provider or self._get_provider()

    def _get_provider(self) -> BaseAIProvider:
        provider_name = (settings.AI_PROVIDER or "mock").lower()

        if provider_name == "mock":
            return MockAIProvider()
        elif provider_name == "gemini":
            from app.services.providers.gemini import GeminiAIProvider
            return GeminiAIProvider()
        elif provider_name == "openai":
            from app.services.providers.openai import OpenAIAIProvider
            return OpenAIAIProvider()
        else:
            # Fallback to safe deterministic mock
            return MockAIProvider()

    async def analyze_incident(
        self, request: IncidentAnalysisRequest
    ) -> IncidentAnalysisResponse:
        # Step 1: Input size & sanity validation
        cleaned_logs = sanitize_and_validate_log_input(
            request.raw_logs, max_chars=settings.MAX_LOG_SIZE_CHARS
        )

        # Step 2: Redact credentials, API keys, passwords, and tokens
        sanitized_logs, redacted_count = SecretRedactor.redact(cleaned_logs)

        # Step 3: Run analysis through selected provider
        response = await self.provider.analyze(
            sanitized_logs=sanitized_logs,
            title=request.title or "Uncategorized Incident",
            environment=request.environment or "production",
            service_name=request.service_name or "unknown-service",
        )

        # Step 4: Inject metadata
        response.id = str(uuid.uuid4())
        response.redacted_secrets_count = redacted_count
        response.analyzed_at = datetime.now(timezone.utc).isoformat()

        return response
