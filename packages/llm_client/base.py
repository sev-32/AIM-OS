"""Base classes for LLM client abstraction.

Provides unified interface for all LLM providers (Gemini, Claude, Cerebras, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ModelInfo:
    """Information about an LLM model."""
    
    name: str
    provider: str
    context_window: int
    max_output_tokens: int
    supports_streaming: bool = False
    supports_function_calling: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider.
    
    All provider implementations must return this format for consistency.
    """
    
    text: str
    """Generated text content."""
    
    model: str
    """Model name (e.g., 'gemini-2.0-flash-exp')."""
    
    provider: str
    """Provider name (e.g., 'gemini', 'anthropic', 'cerebras')."""
    
    tokens_used: int
    """Total tokens consumed (prompt + output)."""
    
    latency_ms: float
    """Generation latency in milliseconds."""
    
    confidence: Optional[float] = None
    """Extracted confidence score (0-1) if available from provider."""
    
    raw_response: Any = None
    """Original provider response object for debugging."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Provider-specific metadata (prompt_tokens, safety_ratings, etc.)."""


class LLMClient(ABC):
    """Abstract base class for all LLM providers.
    
    All LLM clients must implement this interface to ensure
    consistent behavior across providers.
    
    Example:
        >>> client = GeminiClient(api_key="...")
        >>> response = client.generate("Explain quantum computing")
        >>> print(response.text)
        >>> print(f"Tokens used: {response.tokens_used}")
    """
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion for prompt.
        
        Args:
            prompt: Input prompt for the LLM
            max_tokens: Maximum tokens to generate (provider default if None)
            temperature: Sampling temperature 0-1 (provider default if None)
            **kwargs: Provider-specific parameters
        
        Returns:
            LLMResponse with standardized format
        
        Raises:
            LLMError: If generation fails
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """Get information about the model.
        
        Returns:
            ModelInfo with model capabilities and limits
        """
        pass


class LLMError(Exception):
    """Base exception for LLM client errors."""
    
    def __init__(
        self,
        message: str,
        provider: str,
        error_code: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.provider = provider
        self.error_code = error_code
        self.original_error = original_error
        super().__init__(message)


class RateLimitError(LLMError):
    """Raised when API rate limit is hit."""
    pass


class AuthenticationError(LLMError):
    """Raised when API authentication fails."""
    pass


class ModelNotFoundError(LLMError):
    """Raised when requested model doesn't exist."""
    pass

