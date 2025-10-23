"""LLM Client - Unified interface for multiple LLM providers.

Provides standardized access to Gemini, Claude, Cerebras, and other LLM APIs
with consistent response format and error handling.

Example:
    >>> import os
    >>> from llm_client import GeminiClient
    >>> 
    >>> client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
    >>> response = client.generate("Explain quantum computing in 2 sentences")
    >>> print(response.text)
    >>> print(f"Tokens: {response.tokens_used}, Latency: {response.latency_ms}ms")
"""

from .base import (
    LLMClient,
    LLMResponse,
    ModelInfo,
    LLMError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
)
from .gemini import GeminiClient
from .cerebras import CerebrasClient

__all__ = [
    # Base classes
    "LLMClient",
    "LLMResponse",
    "ModelInfo",
    # Errors
    "LLMError",
    "RateLimitError",
    "AuthenticationError",
    "ModelNotFoundError",
    # Providers
    "GeminiClient",
    "CerebrasClient",
]

__version__ = "1.0.0"

