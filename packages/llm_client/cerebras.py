"""Cerebras Cloud API Client - Ultra-fast inference for speed-critical tasks."""

from __future__ import annotations

import os
import time
from typing import Optional, Any, Dict

from .base import LLMClient, LLMResponse, ModelInfo, LLMError, RateLimitError, AuthenticationError


class CerebrasClient(LLMClient):
    """Cerebras Cloud API client.
    
    Optimized for:
    - Ultra-low latency (70-100 tokens/sec)
    - High-volume operations
    - Cost-effective inference
    
    Best for:
    - Quick summaries
    - Fast classification
    - Rapid iteration
    - Context preparation
    
    Example:
        >>> client = CerebrasClient(api_key=os.getenv("CEREBRAS_API_KEY"))
        >>> response = client.generate("Summarize quantum computing in 3 sentences")
        >>> print(response.text)
        >>> # Ultra-fast response!
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3.1-8b",
        base_url: str = "https://api.cerebras.ai/v1"
    ):
        """Initialize Cerebras client.
        
        Args:
            api_key: Cerebras API key (or set CEREBRAS_API_KEY env var)
            model: Model to use (llama3.1-8b, llama3.1-70b)
            base_url: API base URL
        """
        self.api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Cerebras API key required. Set CEREBRAS_API_KEY env var or pass api_key parameter."
            )
        
        self.model_name = model
        self.base_url = base_url
        
        # Import requests for API calls
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests library required for Cerebras client. Install with: pip install requests")
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Cerebras.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse with generated text and metadata
        
        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            LLMError: Other API errors
        """
        # Build request payload
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            start_time = time.time()
            response = self.requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            latency = (time.time() - start_time) * 1000
            
            # Check for errors
            if response.status_code == 401:
                raise AuthenticationError(
                    message="Cerebras authentication failed. Check API key.",
                    provider="cerebras",
                    error_code="AUTH_ERROR",
                    original_error=None
                )
            
            if response.status_code == 429:
                raise RateLimitError(
                    message="Cerebras rate limit exceeded.",
                    provider="cerebras",
                    error_code="RATE_LIMIT",
                    original_error=None
                )
            
            if response.status_code != 200:
                raise LLMError(
                    message=f"Cerebras API error: {response.status_code} - {response.text}",
                    provider="cerebras",
                    error_code=f"HTTP_{response.status_code}",
                    original_error=None
                )
            
            # Parse response
            data = response.json()
            
            if "choices" not in data or len(data["choices"]) == 0:
                raise LLMError(
                    message="Cerebras response missing choices",
                    provider="cerebras",
                    error_code="INVALID_RESPONSE",
                    original_error=None
                )
            
            choice = data["choices"][0]
            generated_text = choice["message"]["content"]
            
            # Extract token counts
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            
            # Extract finish reason
            finish_reason = choice.get("finish_reason", "unknown")
            
            # Estimate confidence (Cerebras doesn't provide logprobs)
            # Use heuristics based on finish reason
            if finish_reason == "stop":
                confidence = 0.85
            elif finish_reason == "length":
                confidence = 0.75
            else:
                confidence = 0.70
            
            return LLMResponse(
                text=generated_text,
                model=self.model_name,
                provider="cerebras",
                tokens_used=total_tokens,
                latency_ms=latency,
                confidence=confidence,
                raw_response=data,
                metadata={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "finish_reason": finish_reason,
                    "model_version": data.get("model", self.model_name)
                }
            )
        
        except self.requests.exceptions.Timeout:
            raise LLMError(
                message="Cerebras request timed out",
                provider="cerebras",
                error_code="TIMEOUT",
                original_error=None
            )
        except self.requests.exceptions.RequestException as e:
            raise LLMError(
                message=f"Cerebras request failed: {str(e)}",
                provider="cerebras",
                error_code="REQUEST_ERROR",
                original_error=e
            )
        except Exception as e:
            if isinstance(e, (LLMError, AuthenticationError, RateLimitError)):
                raise
            raise LLMError(
                message=f"Cerebras generation failed: {str(e)}",
                provider="cerebras",
                error_code="UNKNOWN_ERROR",
                original_error=e
            )
    
    def get_model_info(self) -> ModelInfo:
        """Get information about the current model.
        
        Returns:
            ModelInfo with model specifications
        """
        # Model-specific information
        if "8b" in self.model_name.lower():
            return ModelInfo(
                name=self.model_name,
                provider="cerebras",
                context_window=8192,
                max_output_tokens=4096,
                supports_streaming=True,
                supports_function_calling=False,
                metadata={
                    "pricing_input_1k": 0.00010,  # $0.10 per 1M tokens
                    "pricing_output_1k": 0.00010,
                    "speed": "ultra-fast (70-100 tokens/sec)"
                }
            )
        elif "70b" in self.model_name.lower():
            return ModelInfo(
                name=self.model_name,
                provider="cerebras",
                context_window=8192,
                max_output_tokens=4096,
                supports_streaming=True,
                supports_function_calling=False,
                metadata={
                    "pricing_input_1k": 0.00060,  # $0.60 per 1M tokens
                    "pricing_output_1k": 0.00060,
                    "speed": "very-fast (40-60 tokens/sec)"
                }
            )
        else:
            # Default/unknown model
            return ModelInfo(
                name=self.model_name,
                provider="cerebras",
                context_window=8192,
                max_output_tokens=4096,
                supports_streaming=True,
                supports_function_calling=False,
                metadata={
                    "pricing_input_1k": 0.00010,
                    "pricing_output_1k": 0.00010,
                    "speed": "fast"
                }
            )

