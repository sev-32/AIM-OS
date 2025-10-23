"""Tests for Gemini client.

These tests require GEMINI_API_KEY environment variable.
Skip if not available (CI can skip, local development can test).
"""

from __future__ import annotations

import os
import pytest

from llm_client import GeminiClient, LLMResponse, AuthenticationError


# Skip all tests in this file if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Requires GEMINI_API_KEY environment variable"
)


def test_gemini_client_initialization():
    """Test Gemini client initializes with valid API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    client = GeminiClient(api_key=api_key)
    
    assert client.model_name == "gemini-2.0-flash-exp"  # Default model


def test_gemini_client_custom_model():
    """Test Gemini client with custom model."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    client = GeminiClient(api_key=api_key, model="gemini-pro")
    
    assert client.model_name == "gemini-pro"


def test_gemini_generate_simple():
    """Test basic text generation with Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    response = client.generate("Say 'Hello, World!' and nothing else.")
    
    assert isinstance(response, LLMResponse)
    assert len(response.text) > 0
    assert response.model == "gemini-2.0-flash-exp"
    assert response.provider == "gemini"
    assert response.tokens_used > 0
    assert response.latency_ms > 0


def test_gemini_generate_longer():
    """Test longer generation with Gemini."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    response = client.generate(
        "Explain the concept of bitemporal databases in 3 sentences."
    )
    
    assert len(response.text) > 50  # Should be multiple sentences
    assert response.tokens_used > 20  # Non-trivial token count
    assert "time" in response.text.lower() or "temporal" in response.text.lower()


def test_gemini_with_max_tokens():
    """Test max_tokens parameter."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    response = client.generate(
        "Write a very long essay about AI",
        max_tokens=50  # Limit output
    )
    
    # Should respect token limit (approximately)
    assert response.tokens_used < 100  # Some overhead, but limited


def test_gemini_with_temperature():
    """Test temperature parameter."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    # High temperature = more creative
    response = client.generate(
        "Write a creative metaphor for AI",
        temperature=0.9
    )
    
    assert len(response.text) > 10


def test_gemini_confidence_extraction():
    """Test confidence extraction from Gemini response."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    response = client.generate("What is 2+2?")
    
    # Should have confidence (extracted from finish reason)
    assert response.confidence is not None
    assert 0.0 <= response.confidence <= 1.0


def test_gemini_metadata():
    """Test metadata extraction."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    response = client.generate("Hello!")
    
    # Should have metadata
    assert "prompt_tokens" in response.metadata
    assert "output_tokens" in response.metadata
    assert "finish_reason" in response.metadata
    assert response.metadata["prompt_tokens"] > 0


def test_gemini_model_info():
    """Test model info retrieval."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    info = client.get_model_info()
    
    assert info.name == "gemini-2.0-flash-exp"
    assert info.provider == "gemini"
    assert info.context_window > 0
    assert info.max_output_tokens > 0


def test_gemini_invalid_api_key():
    """Test error handling for invalid API key."""
    with pytest.raises(AuthenticationError):
        client = GeminiClient(api_key="invalid_key_12345")
        # Might fail on init or first call, depending on SDK


@pytest.mark.slow
def test_gemini_multiple_calls():
    """Test multiple sequential calls (rate limiting check)."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    responses = []
    for i in range(5):
        response = client.generate(f"Count to {i+1}")
        responses.append(response)
    
    assert len(responses) == 5
    assert all(r.tokens_used > 0 for r in responses)


@pytest.mark.slow
def test_gemini_technical_accuracy():
    """Test Gemini's technical accuracy (sanity check)."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    response = client.generate(
        "What is the capital of France? Answer in one word only."
    )
    
    # Should answer correctly
    assert "paris" in response.text.lower()


def test_gemini_handles_multiline_prompt():
    """Test Gemini with multiline prompts."""
    api_key = os.getenv("GEMINI_API_KEY")
    client = GeminiClient(api_key=api_key)
    
    prompt = """Context: Our authentication system uses JWT tokens.

Question: How does authentication work?

Please answer based on the context."""
    
    response = client.generate(prompt)
    
    assert len(response.text) > 20
    assert "jwt" in response.text.lower() or "token" in response.text.lower()

