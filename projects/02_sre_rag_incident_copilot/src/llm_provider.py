"""LLM provider abstraction for incident analysis.

Supports multiple LLM backends with a consistent interface.
Currently includes mock provider for testing and GitHub Models provider.
"""

import json
from abc import ABC, abstractmethod
from typing import Optional, TypedDict


class LLMResponse(TypedDict):
    """Represents an LLM response."""

    content: str
    model: str


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_message: str,
    ) -> LLMResponse:
        """Generate a response from the LLM.

        Args:
            system_prompt: System context for the LLM.
            user_message: User message to process.

        Returns:
            LLMResponse with content and model information.

        Raises:
            Exception: If generation fails.
        """


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing without real API calls."""

    def generate(
        self,
        system_prompt: str,
        user_message: str,
    ) -> LLMResponse:
        """Generate a mock response based on keywords.

        Args:
            system_prompt: System context (unused in mock).
            user_message: User message to analyze.

        Returns:
            LLMResponse with mocked analysis.
        """
        # Simple keyword-based mock response generation
        message_lower = user_message.lower()

        # Determine category and urgency
        if any(word in message_lower for word in ["replication", "lag", "database"]):
            category = "Database Issue"
            urgency = "high"
        elif any(word in message_lower for word in ["cpu", "high cpu", "load"]):
            category = "Performance Issue"
            urgency = "high"
        elif any(word in message_lower for word in ["disk", "space", "full"]):
            category = "Infrastructure Issue"
            urgency = "critical"
        elif any(word in message_lower for word in ["deploy", "deployment", "failed"]):
            category = "Deployment Issue"
            urgency = "high"
        elif any(word in message_lower for word in ["error", "spike", "500"]):
            category = "Application Error"
            urgency = "high"
        else:
            category = "General Issue"
            urgency = "medium"

        # Create mock response with all required fields
        response_text = json.dumps(
            {
                "category": category,
                "urgency": urgency,
                "first_checks": [
                    "Check recent changes or deployments",
                    "Monitor system resources",
                    "Review application logs",
                ],
                "action_plan": (
                    "1. Assess current service impact and availability. "
                    "2. Review recent deployments or configuration changes. "
                    "3. Monitor key metrics and system resources. "
                    "4. Gather logs and error messages for root cause analysis."
                ),
                "escalation": (
                    "Escalate to on-call engineer if issue persists "
                    "or impacts user-facing services"
                ),
                "confidence": 0.72,
            },
            indent=2,
        )

        return {
            "content": response_text,
            "model": "mock-provider",
        }


class GitHubModelsProvider(BaseLLMProvider):
    """LLM provider using GitHub Models API."""

    def __init__(
        self,
        github_token: str,
        model: str = "openai/gpt-4o-mini",
        endpoint: str = "https://models.github.ai/inference/chat/completions",
    ):
        """Initialize GitHub Models provider.

        Args:
            github_token: GitHub authentication token.
            model: Model identifier to use.
            endpoint: API endpoint URL.

        Raises:
            ValueError: If github_token is empty.
        """
        if not github_token:
            raise ValueError("GITHUB_TOKEN is required for GitHub Models provider")

        self.github_token = github_token
        self.model = model
        self.endpoint = endpoint

    def generate(
        self,
        system_prompt: str,
        user_message: str,
    ) -> LLMResponse:
        """Generate response using GitHub Models API.

        Args:
            system_prompt: System context for the LLM.
            user_message: User message to process.

        Returns:
            LLMResponse with content from GitHub Models.

        Raises:
            Exception: If API call fails.
        """
        try:
            import httpx
        except ImportError:
            raise ImportError(
                "httpx is required for GitHub Models provider. "
                "Install with: pip install httpx"
            )

        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        try:
            response = httpx.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30.0,
            )

            if response.status_code != 200:
                raise Exception(
                    f"GitHub Models API error {response.status_code}: "
                    f"{response.text}"
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            return {
                "content": content,
                "model": self.model,
            }

        except Exception as e:
            raise Exception(f"GitHub Models API call failed: {str(e)}")


def get_llm_provider(
    provider_name: str,
    github_token: Optional[str] = None,
    github_model: str = "openai/gpt-4o-mini",
    github_endpoint: str = "https://models.github.ai/inference/chat/completions",
) -> BaseLLMProvider:
    """Get an LLM provider instance.

    Args:
        provider_name: Name of provider ('mock' or 'github_models').
        github_token: GitHub token for GitHub Models provider.
        github_model: Model identifier for GitHub Models.
        github_endpoint: Endpoint URL for GitHub Models.

    Returns:
        Configured LLM provider instance.

    Raises:
        ValueError: If provider_name is invalid.
    """
    if provider_name == "mock":
        return MockLLMProvider()

    if provider_name == "github_models":
        if not github_token:
            raise ValueError(
                "GITHUB_TOKEN is required for github_models provider"
            )
        return GitHubModelsProvider(
            github_token=github_token,
            model=github_model,
            endpoint=github_endpoint,
        )

    raise ValueError(f"Unknown LLM provider: {provider_name}")
