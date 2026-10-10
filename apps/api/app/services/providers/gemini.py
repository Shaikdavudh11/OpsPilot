import json
import logging
import httpx
from app.core.config import settings
from app.core.prompt_templates import SRE_SYSTEM_PROMPT, build_analysis_user_prompt
from app.schemas.incident import IncidentAnalysisResponse
from app.services.providers.base import BaseAIProvider
from app.services.providers.mock import MockAIProvider

logger = logging.getLogger("opspilot.providers.gemini")


class GeminiAIProvider(BaseAIProvider):
    """
    Real AI Provider integrating Google Gemini via official REST endpoints.
    Enforces structured JSON output and schema validation.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL or "gemini-1.5-flash"
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        )

    async def analyze(
        self,
        sanitized_logs: str,
        title: str,
        environment: str,
        service_name: str,
    ) -> IncidentAnalysisResponse:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured. Falling back to deterministic MockAIProvider.")
            mock = MockAIProvider()
            res = await mock.analyze(sanitized_logs, title, environment, service_name)
            res.limitations.append("Analysis produced by mock engine: GEMINI_API_KEY was not configured in environment.")
            return res

        user_content = build_analysis_user_prompt(
            sanitized_logs=sanitized_logs,
            title=title,
            environment=environment,
            service_name=service_name,
        )

        payload = {
            "system_instruction": {
                "parts": [{"text": SRE_SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "parts": [{"text": user_content}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.endpoint, json=payload)
                response.raise_for_status()
                data = response.json()

                # Extract content
                candidates = data.get("candidates", [])
                if not candidates:
                    raise ValueError("No analysis candidates returned by Gemini API")

                text_response = candidates[0]["content"]["parts"][0]["text"].strip()
                # Clean optional markdown fencing
                if text_response.startswith("```json"):
                    text_response = text_response[7:]
                if text_response.startswith("```"):
                    text_response = text_response[3:]
                if text_response.endswith("```"):
                    text_response = text_response[:-3]

                parsed_json = json.loads(text_response.strip())
                return IncidentAnalysisResponse.model_validate(parsed_json)

        except Exception as exc:
            logger.error("Gemini API call failed (%s). Falling back to grounded mock.", str(exc))
            mock = MockAIProvider()
            res = await mock.analyze(sanitized_logs, title, environment, service_name)
            res.limitations.append(f"Gemini API invocation fallback: {str(exc)}")
            return res
