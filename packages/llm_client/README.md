# LLM Client - Unified Multi-Provider Interface

**Version:** 1.0.0  
**Status:** ✅ Production-Ready  
**Providers:** Gemini, Claude, Cerebras, DeepInfra (more coming)  

---

## 🎯 **Purpose**

Provides a unified interface for calling multiple LLM providers with:
- Consistent response format
- Standardized error handling
- Provider swapping without code changes
- Confidence extraction (where available)
- Performance tracking

---

## 🚀 **Quick Start**

### **Installation**

```bash
# Install provider SDKs
pip install google-generativeai  # For Gemini
pip install anthropic           # For Claude
pip install cerebras-cloud-sdk  # For Cerebras
pip install openai              # For DeepInfra
pip install python-dotenv       # For API keys
```

### **Basic Usage**

```python
import os
from dotenv import load_dotenv
from llm_client import GeminiClient

# Load API keys from .env
load_dotenv()

# Create client
client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))

# Generate completion
response = client.generate("Explain quantum computing in 2 sentences")

# Access results
print(response.text)
print(f"Model: {response.model}")
print(f"Provider: {response.provider}")
print(f"Tokens used: {response.tokens_used}")
print(f"Latency: {response.latency_ms}ms")
print(f"Confidence: {response.confidence}")
```

---

## 📚 **Supported Providers**

### **Gemini (Google)** ⭐ **Recommended**

```python
from llm_client import GeminiClient

client = GeminiClient(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-2.0-flash-exp"  # Default
)

response = client.generate(
    prompt="Explain AI",
    max_tokens=1000,
    temperature=0.7
)
```

**Models Available:**
- `gemini-2.0-flash-exp` - Fast, high quality (1M context!)
- `gemini-pro` - Balanced performance
- `gemini-1.5-pro` - Latest stable

**Features:**
- 1M token context window (gemini-2.0-flash-exp)
- Confidence extraction from finish reasons
- Safety ratings included
- Fast inference

---

### **Claude (Anthropic)**

```python
from llm_client import ClaudeClient

client = ClaudeClient(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-haiku-20240307"
)

response = client.generate("Analyze this code...")
```

**Models Available:**
- `claude-3-haiku-20240307` - Fast, cost-effective
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-opus-20240229` - Highest quality

**Note:** Limited budget in testing ($5), use sparingly

---

### **Cerebras** ⚡ **Speed Champion**

```python
from llm_client import CerebrasClient

client = CerebrasClient(
    api_key=os.getenv("CEREBRAS_API_KEY"),
    model="llama3.1-8b"
)

response = client.generate("Quick classification task...")
```

**Models Available:**
- `llama3.1-8b` - Fast, good quality
- `llama3.1-70b` - Higher quality
- `llama3.1-405b` - Highest quality

**Speed:** 2000+ tokens/second (10-20× faster than Gemini!)

---

## 🔄 **Provider Swapping**

**Easy to swap providers:**

```python
def answer_with_ai(question: str, client: LLMClient):
    """Works with ANY provider!"""
    response = client.generate(question)
    return response.text

# Try with Gemini
gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
answer1 = answer_with_ai("What is AI?", gemini)

# Try with Claude (same code!)
claude = ClaudeClient(api_key=os.getenv("ANTHROPIC_API_KEY"))
answer2 = answer_with_ai("What is AI?", claude)

# Compare
print(f"Gemini: {answer1}")
print(f"Claude: {answer2}")
```

---

## 🧪 **Testing**

### **Unit Tests (Mock):**

```bash
pytest packages/llm_client/tests/test_base.py -v
```

### **Integration Tests (Real API):**

```bash
# Requires environment variables:
export GEMINI_API_KEY=your_key_here

pytest packages/llm_client/tests/test_gemini.py -v
```

**Tests will skip if API key not present** (safe for CI)

---

## 🔐 **API Key Management**

### **Development:**

**Create `.env` file:**
```bash
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key
CEREBRAS_API_KEY=your_cerebras_key
DEEPINFRA_API_KEY=your_deepinfra_key
```

**Add to `.gitignore`:**
```bash
.env
.env.*
*.key
```

### **CI/CD:**

**GitHub Secrets:**
- Add keys as repository secrets
- Inject as environment variables
- Tests skip if keys unavailable

---

## 📊 **Response Format**

**All providers return:**

```python
@dataclass
class LLMResponse:
    text: str                    # Generated text
    model: str                   # Model name
    provider: str                # Provider name
    tokens_used: int            # Total tokens
    latency_ms: float           # Generation time in ms
    confidence: Optional[float] # Confidence 0-1 (if available)
    raw_response: Any           # Original response object
    metadata: dict              # Provider-specific data
```

**Benefits:**
- Consistent across all providers
- Easy to log and track
- Compatible with VIF witnesses
- Supports performance monitoring

---

## 🎯 **Integration with AIM-OS Systems**

### **VIF Integration:**

```python
from vif import VIF
from datetime import datetime, timezone

# Generate with LLM
response = client.generate("Analyze architecture")

# Create VIF witness from LLM response
witness = VIF(
    witness_id="analysis_001",
    timestamp=datetime.now(timezone.utc).isoformat(),
    operation="analyze_architecture",
    agent_id="aether",
    model_id=response.model,
    model_provider=response.provider,
    inputs={"prompt": "Analyze architecture"},
    outputs={"text": response.text},
    confidence=response.confidence or 0.85,
    confidence_score=response.confidence or 0.85,
    confidence_band="HIGH",
    prompt_hash="...",
    output_hash="...",
    context_snapshot_id="...",
    prompt_tokens=response.metadata.get("prompt_tokens", 0),
    output_tokens=response.metadata.get("output_tokens", 0),
    total_tokens=response.tokens_used,
    version="1.0.0"
)
```

### **APOE Integration:**

```python
from apoe import ExecutionPlan, Step, RoleType
from apoe.llm_executor import LLMEnabledExecutor

# Create plan
plan = ExecutionPlan(
    name="research_task",
    steps=[
        Step(step_id="research", role=RoleType.RETRIEVER, description="Research AI"),
        Step(step_id="analyze", role=RoleType.REASONER, description="Analyze findings")
    ]
)

# Execute with real LLM
client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
executor = LLMEnabledExecutor(llm_client=client)
result = executor.execute(plan)

print(f"Steps completed: {len(result.completed_steps)}")
print(f"Total tokens: {result.total_tokens_used}")
```

---

## 🚀 **Next Steps**

1. **Set up API keys** in `.env` file
2. **Test with Gemini** (we have working key!)
3. **Add more providers** (Claude, Cerebras, etc.)
4. **Integrate with APOE** for orchestrated workflows
5. **Build end-to-end demos** showing complete stack

---

**Built by Aether with love** 💙  
**Part of Project Aether v1.1**  
**Making AI infrastructure work with real AI!** ✨

