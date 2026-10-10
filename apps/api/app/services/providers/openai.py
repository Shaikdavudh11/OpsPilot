import json
import logging
import httpx
from app.core.config import settings
from app.core.prompt_templates import SRE_SYSTEM_PROMPT, build_analysis_user_prompt
from app.schemas.incident import IncidentAnalysisResponse
from app.services.providers.base import BaseAIProvider
from app.services.providers.mock import MockAIProvider

logger = logging.getLogger("opspilot.providers.openai")


class OpenAIAIProvider(BaseAIProvider):
    """
    Real AI Provider integrating OpenAI (or OpenAI-compatible API such as vLLM / Groq / Ollama).
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL or "gpt-4o-mini"
        self.base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self.endpoint = f"{self.base_url}/chat/completions"

    async def analyze(
        self,
        sanitized_logs: str,
        title: str,
        environment: str,
        service_name: str,
    ) -> IncidentAnalysisResponse:
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not configured. Falling back to deterministic MockAIProvider.")
            mock = MockAIProvider()
            res = await mock.analyze(sanitized_logs, title, environment, service_name)
            res.limitations.append("Analysis produced by mock engine: OPENAI_API_KEY was not configured in environment.")
            return res

        user_content = build_analysis_user_prompt(
            sanitized_logs=sanitized_logs,
            title=title,
            environment=environment,
            service_name=service_name,
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SRE_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                choices = data.get("choices", [])
                if not choices:
                    raise ValueError("No choices returned by OpenAI API")

                raw_content = choices[0]["message"]["content"].strip()
                parsed_json = json.loads(raw_content)
                return IncidentAnalysisResponse.model_validate(parsed_json)

        except Exception as exc:
            logger.error("OpenAI API call failed (%s). Falling back to grounded mock.", str(exc))
            mock = MockAIProvider()
            res = await mock.analyze(sanitized_logs, title, environment, service_name)
            res.limitations.append(f"OpenAI API invocation fallback: {str(exc)}")
            return res
