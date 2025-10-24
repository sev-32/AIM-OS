# LLM Client Integration L3: Detailed Implementation

**Detail Level:** 3 of 5 (10,000 words)  
**Context Budget:** ~50,000 tokens  
**Purpose:** Complete implementation guide for LLM Client Integration system  

---

## 🎯 **Implementation Overview**

This document provides complete implementation guidance for the LLM Client Integration system, including detailed code examples, integration patterns, testing strategies, and deployment procedures.

## 🏗️ **LLM Client Integration Implementation**

### **Core LLM Client Integration Implementation**
```python
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import aiohttp
import json
import uuid
from datetime import datetime, timezone
import logging
import hashlib
import time
from abc import ABC, abstractmethod
import ssl
import certifi
from urllib.parse import urljoin
import backoff
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMProvider(Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    CEREBRAS = "cerebras"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"

class RequestType(Enum):
    """Types of requests"""
    COMPLETION = "completion"
    CHAT = "chat"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    CODE_GENERATION = "code_generation"

@dataclass
class LLMRequest:
    """LLM request data structure"""
    request_id: str
    provider: LLMProvider
    request_type: RequestType
    prompt: str
    model: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class LLMResponse:
    """LLM response data structure"""
    response_id: str
    request_id: str
    provider: LLMProvider
    model: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0

class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    def __init__(self, provider: LLMProvider, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(f"LLMClient_{provider.value}")
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter(config.get("rate_limit", {}))
        self.cache = ResponseCache(config.get("cache", {}))
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the LLM client"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup the LLM client"""
        pass
    
    @abstractmethod
    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """Send a request to the LLM provider"""
        pass
    
    @abstractmethod
    async def get_models(self) -> List[str]:
        """Get available models from the provider"""
        pass
    
    async def send_request_with_retry(self, request: LLMRequest) -> LLMResponse:
        """Send request with retry logic"""
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=10)
        )
        async def _send_request():
            # Check rate limits
            await self.rate_limiter.wait_if_needed()
            
            # Check cache
            cached_response = await self.cache.get(request)
            if cached_response:
                self.logger.info(f"Cache hit for request {request.request_id}")
                return cached_response
            
            # Send request
            start_time = time.time()
            response = await self.send_request(request)
            processing_time = (time.time() - start_time) * 1000
            response.processing_time_ms = processing_time
            
            # Cache response
            await self.cache.set(request, response)
            
            return response
        
        return await _send_request()

class GeminiClient(LLMClient):
    """Google Gemini LLM client"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(LLMProvider.GEMINI, config)
        self.api_key = config.get("api_key")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.models_endpoint = f"{self.base_url}/models"
        self.generate_endpoint = f"{self.base_url}/models/{{model}}:generateContent"
    
    async def initialize(self) -> None:
        """Initialize Gemini client"""
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Create SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Create session
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        
        self.logger.info("Gemini client initialized")
    
    async def cleanup(self) -> None:
        """Cleanup Gemini client"""
        if self.session:
            await self.session.close()
        self.logger.info("Gemini client cleaned up")
    
    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """Send request to Gemini"""
        url = self.generate_endpoint.format(model=request.model)
        
        # Prepare request payload
        payload = {
            "contents": [{
                "parts": [{"text": request.prompt}]
            }],
            "generationConfig": {
                "temperature": request.parameters.get("temperature", 0.7),
                "topP": request.parameters.get("top_p", 0.9),
                "maxOutputTokens": request.parameters.get("max_tokens", 1024),
                "stopSequences": request.parameters.get("stop_sequences", [])
            }
        }
        
        # Add safety settings
        if request.parameters.get("safety_settings"):
            payload["safetySettings"] = request.parameters["safety_settings"]
        
        # Send request
        async with self.session.post(
            url,
            params={"key": self.api_key},
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise LLMClientError(f"Gemini request failed: {response.status} - {error_text}")
            
            result = await response.json()
        
        # Parse response
        content = result["candidates"][0]["content"]["parts"][0]["text"]
        usage = result.get("usageMetadata", {})
        
        return LLMResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider=LLMProvider.GEMINI,
            model=request.model,
            content=content,
            usage=usage,
            metadata=result.get("metadata", {})
        )
    
    async def get_models(self) -> List[str]:
        """Get available Gemini models"""
        async with self.session.get(
            self.models_endpoint,
            params={"key": self.api_key}
        ) as response:
            if response.status != 200:
                raise LLMClientError(f"Failed to get Gemini models: {response.status}")
            
            result = await response.json()
        
        return [model["name"].split("/")[-1] for model in result["models"]]

class CerebrasClient(LLMClient):
    """Cerebras LLM client"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(LLMProvider.CEREBRAS, config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.cerebras.ai")
        self.models_endpoint = f"{self.base_url}/v1/models"
        self.completions_endpoint = f"{self.base_url}/v1/completions"
    
    async def initialize(self) -> None:
        """Initialize Cerebras client"""
        if not self.api_key:
            raise ValueError("Cerebras API key is required")
        
        # Create SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Create session
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        
        self.logger.info("Cerebras client initialized")
    
    async def cleanup(self) -> None:
        """Cleanup Cerebras client"""
        if self.session:
            await self.session.close()
        self.logger.info("Cerebras client cleaned up")
    
    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """Send request to Cerebras"""
        
        # Prepare request payload
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "temperature": request.parameters.get("temperature", 0.7),
            "max_tokens": request.parameters.get("max_tokens", 1024),
            "top_p": request.parameters.get("top_p", 0.9),
            "frequency_penalty": request.parameters.get("frequency_penalty", 0.0),
            "presence_penalty": request.parameters.get("presence_penalty", 0.0),
            "stop": request.parameters.get("stop_sequences", [])
        }
        
        # Send request
        async with self.session.post(
            self.completions_endpoint,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise LLMClientError(f"Cerebras request failed: {response.status} - {error_text}")
            
            result = await response.json()
        
        # Parse response
        content = result["choices"][0]["text"]
        usage = result.get("usage", {})
        
        return LLMResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider=LLMProvider.CEREBRAS,
            model=request.model,
            content=content,
            usage=usage,
            metadata=result.get("metadata", {})
        )
    
    async def get_models(self) -> List[str]:
        """Get available Cerebras models"""
        async with self.session.get(self.models_endpoint) as response:
            if response.status != 200:
                raise LLMClientError(f"Failed to get Cerebras models: {response.status}")
            
            result = await response.json()
        
        return [model["id"] for model in result["data"]]

class OpenAIClient(LLMClient):
    """OpenAI LLM client"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(LLMProvider.OPENAI, config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.models_endpoint = f"{self.base_url}/models"
        self.completions_endpoint = f"{self.base_url}/completions"
        self.chat_endpoint = f"{self.base_url}/chat/completions"
    
    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Create SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Create session
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        
        self.logger.info("OpenAI client initialized")
    
    async def cleanup(self) -> None:
        """Cleanup OpenAI client"""
        if self.session:
            await self.session.close()
        self.logger.info("OpenAI client cleaned up")
    
    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """Send request to OpenAI"""
        
        # Determine endpoint based on request type
        if request.request_type == RequestType.CHAT:
            endpoint = self.chat_endpoint
            payload = {
                "model": request.model,
                "messages": [{"role": "user", "content": request.prompt}],
                "temperature": request.parameters.get("temperature", 0.7),
                "max_tokens": request.parameters.get("max_tokens", 1024),
                "top_p": request.parameters.get("top_p", 0.9),
                "frequency_penalty": request.parameters.get("frequency_penalty", 0.0),
                "presence_penalty": request.parameters.get("presence_penalty", 0.0),
                "stop": request.parameters.get("stop_sequences", [])
            }
        else:
            endpoint = self.completions_endpoint
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "temperature": request.parameters.get("temperature", 0.7),
                "max_tokens": request.parameters.get("max_tokens", 1024),
                "top_p": request.parameters.get("top_p", 0.9),
                "frequency_penalty": request.parameters.get("frequency_penalty", 0.0),
                "presence_penalty": request.parameters.get("presence_penalty", 0.0),
                "stop": request.parameters.get("stop_sequences", [])
            }
        
        # Send request
        async with self.session.post(endpoint, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise LLMClientError(f"OpenAI request failed: {response.status} - {error_text}")
            
            result = await response.json()
        
        # Parse response
        if request.request_type == RequestType.CHAT:
            content = result["choices"][0]["message"]["content"]
        else:
            content = result["choices"][0]["text"]
        
        usage = result.get("usage", {})
        
        return LLMResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            provider=LLMProvider.OPENAI,
            model=request.model,
            content=content,
            usage=usage,
            metadata=result.get("metadata", {})
        )
    
    async def get_models(self) -> List[str]:
        """Get available OpenAI models"""
        async with self.session.get(self.models_endpoint) as response:
            if response.status != 200:
                raise LLMClientError(f"Failed to get OpenAI models: {response.status}")
            
            result = await response.json()
        
        return [model["id"] for model in result["data"]]

class LLMClientManager:
    """Manager for multiple LLM clients"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clients: Dict[LLMProvider, LLMClient] = {}
        self.model_selector = ModelSelector(config.get("model_selection", {}))
        self.cross_model_orchestrator = CrossModelOrchestrator(config.get("cross_model", {}))
        self.logger = logging.getLogger("LLMClientManager")
    
    async def initialize(self) -> None:
        """Initialize all LLM clients"""
        self.logger.info("Initializing LLM clients")
        
        # Initialize Gemini client
        if self.config.get("gemini", {}).get("enabled", False):
            self.clients[LLMProvider.GEMINI] = GeminiClient(self.config["gemini"])
            await self.clients[LLMProvider.GEMINI].initialize()
        
        # Initialize Cerebras client
        if self.config.get("cerebras", {}).get("enabled", False):
            self.clients[LLMProvider.CEREBRAS] = CerebrasClient(self.config["cerebras"])
            await self.clients[LLMProvider.CEREBRAS].initialize()
        
        # Initialize OpenAI client
        if self.config.get("openai", {}).get("enabled", False):
            self.clients[LLMProvider.OPENAI] = OpenAIClient(self.config["openai"])
            await self.clients[LLMProvider.OPENAI].initialize()
        
        # Initialize model selector
        await self.model_selector.initialize()
        
        # Initialize cross-model orchestrator
        await self.cross_model_orchestrator.initialize()
        
        self.logger.info(f"Initialized {len(self.clients)} LLM clients")
    
    async def cleanup(self) -> None:
        """Cleanup all LLM clients"""
        self.logger.info("Cleaning up LLM clients")
        
        for client in self.clients.values():
            await client.cleanup()
        
        self.clients.clear()
        self.logger.info("LLM clients cleaned up")
    
    async def send_request(self, request: LLMRequest) -> LLMResponse:
        """Send request using the best available client"""
        
        # Select the best client for the request
        selected_client = await self.model_selector.select_client(request, self.clients)
        
        if not selected_client:
            raise LLMClientError("No suitable client found for request")
        
        # Send request
        response = await selected_client.send_request_with_retry(request)
        
        # Log request and response
        self.logger.info(f"Request {request.request_id} completed using {selected_client.provider.value}")
        
        return response
    
    async def send_cross_model_request(self, request: LLMRequest) -> List[LLMResponse]:
        """Send request to multiple models for cross-model collaboration"""
        
        # Use cross-model orchestrator to coordinate multiple models
        responses = await self.cross_model_orchestrator.orchestrate_request(
            request, self.clients
        )
        
        return responses
    
    async def get_available_models(self) -> Dict[LLMProvider, List[str]]:
        """Get available models from all clients"""
        models = {}
        
        for provider, client in self.clients.items():
            try:
                models[provider] = await client.get_models()
            except Exception as e:
                self.logger.error(f"Failed to get models from {provider.value}: {e}")
                models[provider] = []
        
        return models

class ModelSelector:
    """Selects the best LLM model for a given request"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.performance_tracker = PerformanceTracker()
        self.cost_calculator = CostCalculator()
        self.logger = logging.getLogger("ModelSelector")
    
    async def initialize(self) -> None:
        """Initialize model selector"""
        await self.performance_tracker.initialize()
        await self.cost_calculator.initialize()
        self.logger.info("Model selector initialized")
    
    async def select_client(self, request: LLMRequest, clients: Dict[LLMProvider, LLMClient]) -> Optional[LLMClient]:
        """Select the best client for the request"""
        
        if not clients:
            return None
        
        # Get performance metrics for each client
        performance_metrics = {}
        for provider, client in clients.items():
            metrics = await self.performance_tracker.get_metrics(provider)
            performance_metrics[provider] = metrics
        
        # Get cost estimates for each client
        cost_estimates = {}
        for provider, client in clients.items():
            cost = await self.cost_calculator.estimate_cost(request, provider)
            cost_estimates[provider] = cost
        
        # Select best client based on criteria
        best_client = None
        best_score = float('inf')
        
        for provider, client in clients.items():
            # Calculate score based on performance, cost, and other factors
            performance_score = performance_metrics[provider].get("average_response_time", 1000)
            cost_score = cost_estimates[provider]
            
            # Weighted score (lower is better)
            total_score = (
                self.config.get("performance_weight", 0.5) * performance_score +
                self.config.get("cost_weight", 0.3) * cost_score +
                self.config.get("availability_weight", 0.2) * (100 - performance_metrics[provider].get("availability_percent", 100))
            )
            
            if total_score < best_score:
                best_score = total_score
                best_client = client
        
        return best_client

class CrossModelOrchestrator:
    """Orchestrates cross-model collaboration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.knowledge_sharer = KnowledgeSharer()
        self.context_manager = ContextManager()
        self.response_synthesizer = ResponseSynthesizer()
        self.logger = logging.getLogger("CrossModelOrchestrator")
    
    async def initialize(self) -> None:
        """Initialize cross-model orchestrator"""
        await self.knowledge_sharer.initialize()
        await self.context_manager.initialize()
        await self.response_synthesizer.initialize()
        self.logger.info("Cross-model orchestrator initialized")
    
    async def orchestrate_request(self, request: LLMRequest, clients: Dict[LLMProvider, LLMClient]) -> List[LLMResponse]:
        """Orchestrate request across multiple models"""
        
        # Determine which models to use for collaboration
        collaborating_models = self._select_collaborating_models(request, clients)
        
        if len(collaborating_models) < 2:
            # Fall back to single model
            selected_client = collaborating_models[0]
            response = await selected_client.send_request_with_retry(request)
            return [response]
        
        # Share context between models
        shared_context = await self.context_manager.share_context(request, collaborating_models)
        
        # Send request to each collaborating model
        tasks = []
        for client in collaborating_models:
            # Create modified request with shared context
            modified_request = LLMRequest(
                request_id=f"{request.request_id}_{client.provider.value}",
                provider=client.provider,
                request_type=request.request_type,
                prompt=request.prompt,
                model=request.model,
                parameters=request.parameters,
                context={**request.context, **shared_context},
                metadata=request.metadata
            )
            
            task = client.send_request_with_retry(modified_request)
            tasks.append(task)
        
        # Wait for all responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_responses = []
        for response in responses:
            if isinstance(response, LLMResponse):
                valid_responses.append(response)
            else:
                self.logger.error(f"Request failed: {response}")
        
        # Synthesize responses if needed
        if len(valid_responses) > 1 and self.config.get("synthesize_responses", True):
            synthesized_response = await self.response_synthesizer.synthesize_responses(
                valid_responses, request
            )
            valid_responses.append(synthesized_response)
        
        return valid_responses
    
    def _select_collaborating_models(self, request: LLMRequest, clients: Dict[LLMProvider, LLMClient]) -> List[LLMClient]:
        """Select models for collaboration"""
        
        # For now, return all available clients
        # In the future, this could be more sophisticated
        return list(clients.values())
```

## 🧪 **Testing Implementation**

### **Unit Testing Framework**
```python
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import aiohttp
from llm_client_integration import (
    LLMClientManager, GeminiClient, CerebrasClient, OpenAIClient,
    ModelSelector, CrossModelOrchestrator, LLMRequest, LLMResponse
)

class TestLLMClientManager:
    """Unit tests for LLM Client Manager"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            "gemini": {"enabled": True, "api_key": "test_key"},
            "cerebras": {"enabled": True, "api_key": "test_key"},
            "openai": {"enabled": True, "api_key": "test_key"}
        }
        self.client_manager = LLMClientManager(self.config)
    
    def test_client_manager_initialization(self):
        """Test client manager initialization"""
        assert self.client_manager is not None
        assert self.client_manager.config is not None
        assert self.client_manager.clients is not None
        assert self.client_manager.model_selector is not None
        assert self.client_manager.cross_model_orchestrator is not None
    
    @pytest.mark.asyncio
    async def test_send_request(self):
        """Test sending a request"""
        # Mock clients
        mock_client = Mock()
        mock_client.send_request_with_retry = AsyncMock()
        mock_response = LLMResponse(
            response_id="test_response",
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            model="test_model",
            content="test content"
        )
        mock_client.send_request_with_retry.return_value = mock_response
        
        self.client_manager.clients[LLMProvider.GEMINI] = mock_client
        
        # Mock model selector
        self.client_manager.model_selector.select_client = AsyncMock()
        self.client_manager.model_selector.select_client.return_value = mock_client
        
        # Create test request
        request = LLMRequest(
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            request_type=RequestType.COMPLETION,
            prompt="test prompt",
            model="test_model"
        )
        
        # Send request
        response = await self.client_manager.send_request(request)
        
        assert response is not None
        assert response.content == "test content"
        assert response.request_id == "test_request"
    
    @pytest.mark.asyncio
    async def test_send_cross_model_request(self):
        """Test sending cross-model request"""
        # Mock clients
        mock_client1 = Mock()
        mock_client1.send_request_with_retry = AsyncMock()
        mock_response1 = LLMResponse(
            response_id="test_response_1",
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            model="test_model",
            content="test content 1"
        )
        mock_client1.send_request_with_retry.return_value = mock_response1
        
        mock_client2 = Mock()
        mock_client2.send_request_with_retry = AsyncMock()
        mock_response2 = LLMResponse(
            response_id="test_response_2",
            request_id="test_request",
            provider=LLMProvider.CEREBRAS,
            model="test_model",
            content="test content 2"
        )
        mock_client2.send_request_with_retry.return_value = mock_response2
        
        self.client_manager.clients[LLMProvider.GEMINI] = mock_client1
        self.client_manager.clients[LLMProvider.CEREBRAS] = mock_client2
        
        # Mock cross-model orchestrator
        self.client_manager.cross_model_orchestrator.orchestrate_request = AsyncMock()
        self.client_manager.cross_model_orchestrator.orchestrate_request.return_value = [mock_response1, mock_response2]
        
        # Create test request
        request = LLMRequest(
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            request_type=RequestType.COMPLETION,
            prompt="test prompt",
            model="test_model"
        )
        
        # Send cross-model request
        responses = await self.client_manager.send_cross_model_request(request)
        
        assert len(responses) == 2
        assert responses[0].content == "test content 1"
        assert responses[1].content == "test content 2"

class TestGeminiClient:
    """Unit tests for Gemini Client"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {"api_key": "test_key"}
        self.gemini_client = GeminiClient(self.config)
    
    def test_gemini_client_initialization(self):
        """Test Gemini client initialization"""
        assert self.gemini_client is not None
        assert self.gemini_client.provider == LLMProvider.GEMINI
        assert self.gemini_client.config == self.config
        assert self.gemini_client.api_key == "test_key"
    
    @pytest.mark.asyncio
    async def test_send_request(self):
        """Test sending request to Gemini"""
        # Mock session
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "test response"}]
                }
            }],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5}
        }
        
        mock_session.post.return_value.__aenter__.return_value = mock_response
        self.gemini_client.session = mock_session
        
        # Create test request
        request = LLMRequest(
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            request_type=RequestType.COMPLETION,
            prompt="test prompt",
            model="test_model"
        )
        
        # Send request
        response = await self.gemini_client.send_request(request)
        
        assert response is not None
        assert response.content == "test response"
        assert response.provider == LLMProvider.GEMINI
        assert response.model == "test_model"
    
    @pytest.mark.asyncio
    async def test_get_models(self):
        """Test getting available models from Gemini"""
        # Mock session
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock()
        mock_response.json.return_value = {
            "models": [
                {"name": "models/gemini-pro"},
                {"name": "models/gemini-pro-vision"}
            ]
        }
        
        mock_session.get.return_value.__aenter__.return_value = mock_response
        self.gemini_client.session = mock_session
        
        # Get models
        models = await self.gemini_client.get_models()
        
        assert len(models) == 2
        assert "gemini-pro" in models
        assert "gemini-pro-vision" in models

class TestModelSelector:
    """Unit tests for Model Selector"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            "performance_weight": 0.5,
            "cost_weight": 0.3,
            "availability_weight": 0.2
        }
        self.model_selector = ModelSelector(self.config)
    
    def test_model_selector_initialization(self):
        """Test model selector initialization"""
        assert self.model_selector is not None
        assert self.model_selector.config == self.config
        assert self.model_selector.performance_tracker is not None
        assert self.model_selector.cost_calculator is not None
    
    @pytest.mark.asyncio
    async def test_select_client(self):
        """Test client selection"""
        # Mock clients
        mock_client1 = Mock()
        mock_client1.provider = LLMProvider.GEMINI
        
        mock_client2 = Mock()
        mock_client2.provider = LLMProvider.CEREBRAS
        
        clients = {
            LLMProvider.GEMINI: mock_client1,
            LLMProvider.CEREBRAS: mock_client2
        }
        
        # Mock performance tracker
        self.model_selector.performance_tracker.get_metrics = AsyncMock()
        self.model_selector.performance_tracker.get_metrics.side_effect = [
            {"average_response_time": 500, "availability_percent": 99},
            {"average_response_time": 800, "availability_percent": 95}
        ]
        
        # Mock cost calculator
        self.model_selector.cost_calculator.estimate_cost = AsyncMock()
        self.model_selector.cost_calculator.estimate_cost.side_effect = [0.01, 0.02]
        
        # Create test request
        request = LLMRequest(
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            request_type=RequestType.COMPLETION,
            prompt="test prompt",
            model="test_model"
        )
        
        # Select client
        selected_client = await self.model_selector.select_client(request, clients)
        
        assert selected_client is not None
        assert selected_client in clients.values()

class TestCrossModelOrchestrator:
    """Unit tests for Cross-Model Orchestrator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {"synthesize_responses": True}
        self.orchestrator = CrossModelOrchestrator(self.config)
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        assert self.orchestrator is not None
        assert self.orchestrator.config == self.config
        assert self.orchestrator.knowledge_sharer is not None
        assert self.orchestrator.context_manager is not None
        assert self.orchestrator.response_synthesizer is not None
    
    @pytest.mark.asyncio
    async def test_orchestrate_request(self):
        """Test orchestrating request across multiple models"""
        # Mock clients
        mock_client1 = Mock()
        mock_client1.provider = LLMProvider.GEMINI
        mock_client1.send_request_with_retry = AsyncMock()
        mock_response1 = LLMResponse(
            response_id="test_response_1",
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            model="test_model",
            content="test content 1"
        )
        mock_client1.send_request_with_retry.return_value = mock_response1
        
        mock_client2 = Mock()
        mock_client2.provider = LLMProvider.CEREBRAS
        mock_client2.send_request_with_retry = AsyncMock()
        mock_response2 = LLMResponse(
            response_id="test_response_2",
            request_id="test_request",
            provider=LLMProvider.CEREBRAS,
            model="test_model",
            content="test content 2"
        )
        mock_client2.send_request_with_retry.return_value = mock_response2
        
        clients = {
            LLMProvider.GEMINI: mock_client1,
            LLMProvider.CEREBRAS: mock_client2
        }
        
        # Mock context manager
        self.orchestrator.context_manager.share_context = AsyncMock()
        self.orchestrator.context_manager.share_context.return_value = {"shared": "context"}
        
        # Mock response synthesizer
        self.orchestrator.response_synthesizer.synthesize_responses = AsyncMock()
        mock_synthesized_response = LLMResponse(
            response_id="test_response_synthesized",
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            model="test_model",
            content="synthesized content"
        )
        self.orchestrator.response_synthesizer.synthesize_responses.return_value = mock_synthesized_response
        
        # Create test request
        request = LLMRequest(
            request_id="test_request",
            provider=LLMProvider.GEMINI,
            request_type=RequestType.COMPLETION,
            prompt="test prompt",
            model="test_model"
        )
        
        # Orchestrate request
        responses = await self.orchestrator.orchestrate_request(request, clients)
        
        assert len(responses) == 3  # 2 original responses + 1 synthesized
        assert responses[0].content == "test content 1"
        assert responses[1].content == "test content 2"
        assert responses[2].content == "synthesized content"
```

## 🚀 **Deployment Implementation**

### **Production Deployment Configuration**
```python
class LLMClientIntegrationDeployment:
    """Production deployment for LLM Client Integration system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.deployment_manager = DeploymentManager()
        self.monitoring_setup = MonitoringSetup()
        self.scaling_manager = ScalingManager()
    
    def deploy(self) -> DeploymentResult:
        """Deploy LLM Client Integration system to production"""
        try:
            # Initialize components
            self._initialize_components()
            
            # Configure LLM clients
            self._configure_llm_clients()
            
            # Setup monitoring
            self._setup_monitoring()
            
            # Configure scaling
            self._configure_scaling()
            
            # Validate deployment
            validation_result = self._validate_deployment()
            
            if validation_result.is_valid:
                return DeploymentResult(
                    success=True,
                    deployment_id=str(uuid.uuid4()),
                    deployment_timestamp=datetime.utcnow(),
                    validation_result=validation_result
                )
            else:
                return DeploymentResult(
                    success=False,
                    error=validation_result.error,
                    deployment_timestamp=datetime.utcnow()
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                error=str(e),
                deployment_timestamp=datetime.utcnow()
            )
    
    def _initialize_components(self) -> None:
        """Initialize all LLM client integration components"""
        # Implementation for component initialization
        pass
    
    def _configure_llm_clients(self) -> None:
        """Configure LLM clients"""
        # Implementation for LLM client configuration
        pass
    
    def _setup_monitoring(self) -> None:
        """Setup monitoring and health checks"""
        # Implementation for monitoring setup
        pass
    
    def _configure_scaling(self) -> None:
        """Configure scaling for LLM client integration system"""
        # Implementation for scaling configuration
        pass
    
    def _validate_deployment(self) -> ValidationResult:
        """Validate deployment configuration"""
        # Implementation for deployment validation
        return ValidationResult(is_valid=True)
```

---

**Next Level:** [L4 Complete (15kw+)](L4_complete.md)  
**Code:** `packages/llm_client/`
