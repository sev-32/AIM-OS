"""Google Gemini API client implementation.

Provides unified interface to Gemini models through google-generativeai SDK.
"""

from __future__ import annotations

import time
from typing import Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .base import (
    LLMClient,
    LLMResponse,
    ModelInfo,
    LLMError,
    AuthenticationError,
    RateLimitError
)


class GeminiClient(LLMClient):
    """Google Gemini API client.
    
    Supports Gemini models including:
    - gemini-2.0-flash-exp (fast, high quality)
    - gemini-pro (balanced)
    - gemini-ultra (highest quality)
    
    Example:
        >>> import os
        >>> client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        >>> response = client.generate("Explain bitemporal databases")
        >>> print(response.text)
        >>> print(f"Tokens: {response.tokens_used}, Latency: {response.latency_ms}ms")
    
    Args:
        api_key: Google AI API key
        model: Model name (default: gemini-2.0-flash-exp)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp"
    ):
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai not installed. "
                "Install with: pip install google-generativeai"
            )
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
            self.model_name = model
        except Exception as e:
            raise AuthenticationError(
                message=f"Failed to initialize Gemini: {str(e)}",
                provider="gemini",
                original_error=e
            )
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Gemini.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional Gemini-specific parameters
        
        Returns:
            LLMResponse with generated text and metadata
        
        Raises:
            LLMError: If generation fails
            RateLimitError: If rate limit exceeded
            AuthenticationError: If authentication fails
        """
        # Build generation config
        generation_config = {}
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        if temperature is not None:
            generation_config["temperature"] = temperature
        
        # Merge with any user-provided config
        if "generation_config" in kwargs:
            generation_config.update(kwargs["generation_config"])
        
        try:
            start_time = time.time()
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config if generation_config else None
            )
            
            latency = (time.time() - start_time) * 1000
            
            # Extract confidence from response
            confidence = self._extract_confidence(response)
            
            return LLMResponse(
                text=response.text,
                model=self.model_name,
                provider="gemini",
                tokens_used=response.usage_metadata.total_token_count,
                latency_ms=latency,
                confidence=confidence,
                raw_response=response,
                metadata={
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count,
                    "finish_reason": response.candidates[0].finish_reason,
                    "safety_ratings": [
                        {
                            "category": rating.category,
                            "probability": rating.probability
                        }
                        for rating in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            )
        
        except Exception as e:
            error_str = str(e).lower()
            
            # Detect specific error types
            if "rate" in error_str or "quota" in error_str:
                raise RateLimitError(
                    message=f"Gemini rate limit exceeded: {str(e)}",
                    provider="gemini",
                    error_code="RATE_LIMIT",
                    original_error=e
                )
            elif "auth" in error_str or "key" in error_str:
                raise AuthenticationError(
                    message=f"Gemini authentication failed: {str(e)}",
                    provider="gemini",
                    error_code="AUTH_FAILED",
                    original_error=e
                )
            else:
                raise LLMError(
                    message=f"Gemini generation failed: {str(e)}",
                    provider="gemini",
                    original_error=e
                )
    
    def _extract_confidence(self, response) -> Optional[float]:
        """Extract confidence score from Gemini response.
        
        Gemini doesn't expose token-level logprobs directly, so we use:
        1. Finish reason (STOP = high confidence)
        2. Safety ratings (blocked = low confidence)
        3. Fallback: Moderate confidence (let VIF calibration handle)
        
        Args:
            response: Gemini response object
        
        Returns:
            Confidence score 0-1, or None if can't determine
        """
        if not response.candidates:
            return 0.30  # No candidates = very low confidence
        
        candidate = response.candidates[0]
        finish_reason = candidate.finish_reason
        
        # Map finish reasons to confidence
        # 1 = STOP (normal completion)
        # 2 = MAX_TOKENS (truncated, medium confidence)
        # 3 = SAFETY (blocked, low confidence)
        # 4 = RECITATION (copyright, low confidence)
        # 5 = OTHER (unknown, low confidence)
        
        finish_reason_confidence = {
            1: 0.85,  # STOP - normal completion
            2: 0.70,  # MAX_TOKENS - truncated but valid
            3: 0.40,  # SAFETY - content blocked
            4: 0.35,  # RECITATION - copyright issue
            5: 0.50,  # OTHER - unknown issue
        }
        
        base_confidence = finish_reason_confidence.get(finish_reason, 0.50)
        
        # Adjust for safety ratings
        # If any safety rating is HIGH probability of harm, reduce confidence
        if hasattr(candidate, 'safety_ratings'):
            for rating in candidate.safety_ratings:
                if rating.probability in [4, 5]:  # HIGH or very HIGH probability
                    base_confidence *= 0.7  # Reduce confidence
        
        return base_confidence
    
    def get_model_info(self) -> ModelInfo:
        """Get information about current Gemini model.
        
        Returns:
            ModelInfo with model capabilities
        """
        # Model-specific information
        # These are approximations - Gemini doesn't expose all details
        model_specs = {
            "gemini-2.0-flash-exp": {
                "context_window": 1_000_000,  # 1M token context!
                "max_output": 8192,
                "streaming": True,
                "functions": True
            },
            "gemini-pro": {
                "context_window": 32_000,
                "max_output": 2048,
                "streaming": True,
                "functions": True
            },
            "gemini-1.5-pro": {
                "context_window": 1_000_000,
                "max_output": 8192,
                "streaming": True,
                "functions": True
            }
        }
        
        spec = model_specs.get(self.model_name, {
            "context_window": 32_000,  # Conservative default
            "max_output": 2048,
            "streaming": False,
            "functions": False
        })
        
        return ModelInfo(
            name=self.model_name,
            provider="gemini",
            context_window=spec["context_window"],
            max_output_tokens=spec["max_output"],
            supports_streaming=spec["streaming"],
            supports_function_calling=spec["functions"],
            metadata={
                "sdk": "google-generativeai",
                "docs": "https://ai.google.dev/docs"
            }
        )

