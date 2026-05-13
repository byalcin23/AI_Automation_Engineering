"""Tests for LLM provider functionality."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_provider import (
    BaseLLMProvider,
    GitHubModelsProvider,
    MockLLMProvider,
    get_llm_provider,
)


class TestMockLLMProvider:
    """Tests for mock LLM provider."""

    def test_mock_provider_initialization(self):
        """Test MockLLMProvider can be initialized."""
        provider = MockLLMProvider()
        assert provider is not None

    def test_mock_provider_generates_response(self):
        """Test that mock provider generates a response."""
        provider = MockLLMProvider()
        response = provider.generate("system", "user message")

        assert "content" in response
        assert "model" in response
        assert response["model"] == "mock-provider"

    def test_mock_provider_response_is_json(self):
        """Test that mock provider response contains valid JSON."""
        import json

        provider = MockLLMProvider()
        response = provider.generate("system", "database lag issue")

        # Should be valid JSON
        parsed = json.loads(response["content"])
        assert "category" in parsed
        assert "urgency" in parsed

    def test_mock_provider_detects_database_issues(self):
        """Test that mock provider detects database-related keywords."""
        import json

        provider = MockLLMProvider()
        response = provider.generate("system", "database replication lag")

        parsed = json.loads(response["content"])
        assert "database" in parsed["category"].lower()

    def test_mock_provider_detects_cpu_issues(self):
        """Test that mock provider detects CPU-related keywords."""
        import json

        provider = MockLLMProvider()
        response = provider.generate("system", "high cpu load on servers")

        parsed = json.loads(response["content"])
        assert "performance" in parsed["category"].lower()

    def test_mock_provider_detects_disk_issues(self):
        """Test that mock provider detects disk-related keywords."""
        import json

        provider = MockLLMProvider()
        response = provider.generate("system", "disk space full")

        parsed = json.loads(response["content"])
        assert parsed["urgency"] == "critical"


class TestGitHubModelsProvider:
    """Tests for GitHub Models provider."""

    def test_github_provider_requires_token(self):
        """Test that GitHub provider requires GITHUB_TOKEN."""
        with pytest.raises(ValueError, match="GITHUB_TOKEN is required"):
            GitHubModelsProvider(github_token="")

    def test_github_provider_initialization_with_token(self):
        """Test GitHub provider initialization with token."""
        provider = GitHubModelsProvider(github_token="test_token")
        assert provider.github_token == "test_token"

    def test_github_provider_custom_model(self):
        """Test GitHub provider with custom model."""
        provider = GitHubModelsProvider(
            github_token="test_token",
            model="custom-model",
        )
        assert provider.model == "custom-model"

    def test_github_provider_custom_endpoint(self):
        """Test GitHub provider with custom endpoint."""
        custom_endpoint = "https://custom.endpoint/api"
        provider = GitHubModelsProvider(
            github_token="test_token",
            endpoint=custom_endpoint,
        )
        assert provider.endpoint == custom_endpoint


class TestProviderFactory:
    """Tests for get_llm_provider factory function."""

    def test_get_mock_provider(self):
        """Test getting mock provider."""
        provider = get_llm_provider("mock")
        assert isinstance(provider, MockLLMProvider)

    def test_get_github_models_provider_without_token(self):
        """Test getting GitHub provider without token raises error."""
        with pytest.raises(ValueError):
            get_llm_provider("github_models", github_token="")

    def test_get_github_models_provider_with_token(self):
        """Test getting GitHub provider with token."""
        provider = get_llm_provider("github_models", github_token="test_token")
        assert isinstance(provider, GitHubModelsProvider)

    def test_get_invalid_provider(self):
        """Test getting invalid provider raises error."""
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm_provider("invalid_provider")

    def test_provider_factory_with_custom_settings(self):
        """Test factory with custom settings."""
        provider = get_llm_provider(
            "github_models",
            github_token="token",
            github_model="custom-model",
            github_endpoint="https://custom/endpoint",
        )
        assert provider.model == "custom-model"
        assert provider.endpoint == "https://custom/endpoint"


class TestBaseLLMProvider:
    """Tests for BaseLLMProvider abstract class."""

    def test_base_provider_is_abstract(self):
        """Test that BaseLLMProvider cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseLLMProvider()

    def test_base_provider_generate_is_abstract(self):
        """Test that generate method must be implemented."""

        class BadProvider(BaseLLMProvider):
            pass

        with pytest.raises(TypeError):
            BadProvider()
