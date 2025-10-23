# LLM Integration Specification - Aether v1.1

**Created:** 2025-10-23  
**Purpose:** Complete specification for real LLM API integration  
**Priority:** ⭐ HIGHEST for v1.1 (foundation for everything else)  
**Confidence:** 0.88 (high - we have working APIs and clear architecture)  

---

## 🎯 **EXECUTIVE SUMMARY**

**The Gap We're Filling:**

**Current State (v1.0.0):**
- ✅ Complete infrastructure (CMC, HHNI, VIF, APOE, SDF-CVF, SEG, CAS)
- ✅ 672+ tests validating infrastructure
- ⚠️ **No real LLM integration** - tests use mocks and hardcoded values

**Target State (v1.1.0):**
- ✅ All infrastructure (unchanged)
- ✅ **Real LLM clients** (Gemini, Claude, Cerebras, DeepInfra)
- ✅ **LLM-enabled APOE** (actually executes with real AI)
- ✅ **End-to-end tests** with real API calls
- ✅ **Multi-provider support** (swap LLMs seamlessly)

**Impact:** Transforms from "infrastructure for AI" to "working AI system"

---

## 🏗️ **ARCHITECTURE**

### **Layer 1: LLM Client Abstraction**

**Purpose:** Unified interface for all LLM providers

**Design:**
```python
# Abstract interface all providers implement
class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse
    
    @abstractmethod
    def get_model_info(self) -> ModelInfo

# Standardized response format
@dataclass
class LLMResponse:
    text: str                    # Generated text
    model: str                   # Model name
    provider: str                # Provider name
    confidence: Optional[float]  # Extracted confidence (if available)
    tokens_used: int            # Total tokens
    latency_ms: float           # Generation time
    raw_response: Any           # Original response object
    metadata: dict              # Provider-specific metadata
```

**Benefits:**
- ✅ Swap providers without changing calling code
- ✅ Consistent interface across all systems
- ✅ Easy to add new providers
- ✅ Testable (mock the interface)

---

### **Layer 2: Provider Implementations**

**We'll build 4 providers (we have working keys for all):**

#### **1. GeminiClient** ⭐ **PRIMARY**
```python
class GeminiClient(LLMClient):
    """Google Gemini API client."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-exp"
    ):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate with Gemini."""
        import time
        
        start = time.time()
        response = self.model.generate_content(
            prompt,
            generation_config=kwargs.get("generation_config")
        )
        latency = (time.time() - start) * 1000
        
        return LLMResponse(
            text=response.text,
            model=self.model_name,
            provider="gemini",
            confidence=self._extract_confidence(response),
            tokens_used=response.usage_metadata.total_token_count,
            latency_ms=latency,
            raw_response=response,
            metadata={
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "output_tokens": response.usage_metadata.candidates_token_count
            }
        )
    
    def _extract_confidence(self, response) -> Optional[float]:
        """Extract confidence from Gemini response.
        
        Gemini doesn't expose logprobs, so we use:
        1. Safety ratings (if present)
        2. Finish reason
        3. Fallback: None (let VIF calibration handle it)
        """
        # Check finish reason
        finish_reason = response.candidates[0].finish_reason
        if finish_reason == 1:  # STOP (normal completion)
            return 0.85  # Medium-high default
        elif finish_reason == 3:  # SAFETY
            return 0.50  # Low confidence on blocked content
        
        return None  # Unknown, let VIF handle
```

**Why PRIMARY:** We have working key, good quality, reasonable speed

---

#### **2. ClaudeClient**
```python
class ClaudeClient(LLMClient):
    """Anthropic Claude API client."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307"
    ):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate with Claude."""
        import time
        
        start = time.time()
        message = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}]
        )
        latency = (time.time() - start) * 1000
        
        return LLMResponse(
            text=message.content[0].text,
            model=self.model,
            provider="anthropic",
            confidence=None,  # Claude doesn't expose confidence directly
            tokens_used=message.usage.input_tokens + message.usage.output_tokens,
            latency_ms=latency,
            raw_response=message,
            metadata={
                "prompt_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
                "stop_reason": message.stop_reason
            }
        )
```

**Why SECONDARY:** Limited budget ($5), use for validation

---

#### **3. CerebrasClient** 
```python
class CerebrasClient(LLMClient):
    """Cerebras fast inference API client."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama3.1-8b"
    ):
        from cerebras.cloud.sdk import Cerebras
        self.client = Cerebras(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate with Cerebras (10-20× faster!)."""
        import time
        
        start = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 1024)
        )
        latency = (time.time() - start) * 1000
        
        return LLMResponse(
            text=response.choices[0].message.content,
            model=self.model,
            provider="cerebras",
            confidence=None,  # Cerebras doesn't expose logprobs
            tokens_used=response.usage.total_tokens,
            latency_ms=latency,
            raw_response=response,
            metadata={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
        )
```

**Why TERTIARY:** Speed champion (2000+ tokens/sec) for batch tasks

---

### **Layer 3: APOE LLM Integration**

**Current APOE Executor:**
```python
# Current (infrastructure only):
class PlanExecutor:
    def execute(self, plan):
        for step in plan.steps:
            # Just tracks execution, doesn't call LLM
            result = self._execute_step(step)
```

**Enhanced LLM-Enabled Executor:**
```python
# Enhanced (with real AI):
class LLMEnabledExecutor(PlanExecutor):
    """Executor that calls real LLMs for each step."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        super().__init__()
    
    def _execute_step(self, step: Step) -> dict:
        """Execute step with real LLM based on role."""
        
        # Build prompt based on role
        prompt = self._build_role_prompt(step)
        
        # Call LLM
        response = self.llm_client.generate(
            prompt=prompt,
            max_tokens=step.budget.get("tokens", 1024)
        )
        
        # Create VIF witness
        witness = self._create_witness_for_step(step, response)
        
        # Check gates
        if not self._check_gates(step, response):
            return {"status": "failed", "reason": "Gate failed"}
        
        return {
            "status": "completed",
            "output": response.text,
            "witness": witness,
            "tokens_used": response.tokens_used,
            "latency_ms": response.latency_ms
        }
    
    def _build_role_prompt(self, step: Step) -> str:
        """Build prompt based on role type."""
        
        role_prompts = {
            RoleType.PLANNER: f"You are a strategic planner. Task: {step.description}",
            RoleType.RETRIEVER: f"You are a researcher. Retrieve information about: {step.description}",
            RoleType.REASONER: f"You are an analytical reasoner. Analyze: {step.description}",
            RoleType.BUILDER: f"You are a builder. Implement: {step.description}",
            RoleType.CRITIC: f"You are a critic. Review: {step.description}",
            RoleType.VERIFIER: f"You are a verifier. Validate: {step.description}",
            # ... other roles
        }
        
        return role_prompts.get(step.role, step.description)
```

---

### **Layer 4: End-to-End Integration**

**Complete workflow with real AI:**

```python
def aether_answer_question(question: str, llm_client: LLMClient):
    """Complete Aether workflow with real LLM.
    
    This is THE proof that infrastructure + LLM = working AI system.
    """
    
    # 1. HHNI: Retrieve relevant context from CMC
    context_results = hhni.search(question, top_k=5)
    context = "\n".join([r.text for r in context_results])
    
    # 2. Build enhanced prompt with context
    full_prompt = f"""Context from memory:
{context}

Question: {question}

Please answer based on the context provided."""
    
    # 3. LLM generates answer
    response = llm_client.generate(full_prompt)
    
    # 4. VIF: Create witness
    witness = VIF(
        operation="answer_question",
        model_id=response.model,
        model_provider=response.provider,
        inputs={"question": question, "context": context},
        outputs={"answer": response.text},
        confidence=response.confidence or 0.85,
        # ... other fields
    )
    
    # 5. SDF-CVF: Check quality (if quartet exists)
    # (For Q&A, might just check confidence)
    
    # 6. CMC: Store answer for future
    atom = cmc.create_atom(AtomCreate(
        modality="text",
        content=AtomContent(inline=response.text),
        tags={"question": 1.0, "answer": 0.9}
    ))
    
    # 7. SEG: Build knowledge graph
    seg.add_entity(Entity(type="question", name=question))
    seg.add_entity(Entity(type="answer", name=f"Answer {atom.id}"))
    
    return {
        "answer": response.text,
        "confidence": response.confidence,
        "witness_id": witness.witness_id,
        "atom_id": atom.id,
        "latency_ms": response.latency_ms,
        "tokens_used": response.tokens_used
    }
```

**THIS is what we need to prove works!** ✅

---

## 📋 **IMPLEMENTATION PLAN (Detailed)**

### **Phase 1: LLM Client Foundation (Day 1, 6-8 hours)**

**Hour 1-2: Base Infrastructure**
- Create `packages/llm_client/` directory
- Implement `base.py` (LLMClient, LLMResponse, ModelInfo)
- Add type hints, docstrings
- Write basic tests

**Hour 3-4: GeminiClient**
- Implement `gemini.py` (GeminiClient)
- Add error handling
- Test with real API key
- Verify response parsing

**Hour 5-6: ClaudeClient**
- Implement `claude.py` (ClaudeClient)
- Match GeminiClient interface
- Test with real API

**Hour 7-8: CerebrasClient + DeepInfraClient**
- Implement both (similar APIs)
- Test speed comparison
- Document differences

**Deliverable:** 4 working LLM clients ✅

---

### **Phase 2: Integration Tests (Day 2, 6-8 hours)**

**Hour 1-2: Basic API Tests**
- `test_gemini.py` - Verify Gemini client works
- `test_claude.py` - Verify Claude client works
- `test_multi_provider.py` - Compare outputs

**Hour 3-4: VIF Integration**
- Test confidence extraction from real responses
- Test witness creation with real LLM data
- Validate ECE tracking with real predictions

**Hour 5-6: CMC + HHNI Integration**
- Test storing real LLM outputs in CMC
- Test HHNI indexing real LLM-generated content
- Validate retrieval and re-use

**Hour 7-8: SEG Integration**
- Test building knowledge graphs from LLM outputs
- Test contradiction detection with real AI responses
- Validate provenance tracing

**Deliverable:** Real API tests proving integration ✅

---

### **Phase 3: APOE LLM Executor (Day 3, 6-8 hours)**

**Hour 1-3: LLMEnabledExecutor**
- Create `llm_executor.py`
- Implement role-based prompting
- Add budget enforcement for LLM calls
- Error handling and retries

**Hour 4-6: Role Handlers**
- Implement all 8 role types
- Planner, Retriever, Reasoner, Builder, Critic, Verifier, Witness, Operator
- Each with appropriate prompts

**Hour 7-8: Integration Testing**
- Test plans with real LLM execution
- Verify budget tracking
- Validate gate checking with real outputs

**Deliverable:** APOE executes plans with real AI ✅

---

### **Phase 4: End-to-End Validation (Day 4, 6-8 hours)**

**Hour 1-3: Complete Workflow Tests**
- Question answering with full stack
- Multi-step reasoning with APOE
- Long-running conversation with CMC memory

**Hour 4-6: Multi-Provider Comparison**
- Same task on Gemini vs Claude vs Cerebras
- Compare quality, speed, cost
- Validate provider swapping

**Hour 7-8: Performance Benchmarking**
- Measure latency with real LLMs
- Compare with mocked baselines
- Document overhead

**Deliverable:** Proof that complete system works! ✅

---

## 📊 **DELIVERABLES**

### **Code Artifacts:**

```
packages/llm_client/
├── __init__.py
├── base.py (LLMClient, LLMResponse, ModelInfo)
├── gemini.py (GeminiClient)
├── claude.py (ClaudeClient)
├── cerebras.py (CerebrasClient)
├── deepinfra.py (DeepInfraClient)
├── factory.py (create_client() helper)
├── README.md
└── tests/
    ├── test_base.py
    ├── test_gemini.py (requires GEMINI_API_KEY)
    ├── test_claude.py (requires ANTHROPIC_API_KEY)
    ├── test_cerebras.py (requires CEREBRAS_API_KEY)
    ├── test_multi_provider.py
    └── conftest.py (fixtures)

packages/apoe/
├── llm_executor.py (NEW)
├── role_prompts.py (NEW - prompt templates)
└── tests/
    └── test_llm_executor.py (NEW)

packages/integration_tests/
├── test_real_llm_vif.py (NEW)
├── test_real_llm_apoe.py (NEW)
├── test_real_llm_e2e.py (NEW)
└── test_multi_provider_comparison.py (NEW)
```

---

### **Test Coverage:**

**New Tests:**
- LLM client unit tests: ~15 tests
- LLM integration tests: ~20 tests
- APOE LLM executor tests: ~12 tests
- End-to-end tests: ~8 tests

**Total New Tests:** ~55 tests  
**Total After v1.1:** 672 + 55 = **727+ tests!**

---

## 🎯 **ACCEPTANCE CRITERIA**

### **Must Have for v1.1.0:**

**1. Multi-Provider Support** ✅
- [ ] GeminiClient works with real API
- [ ] ClaudeClient works with real API
- [ ] CerebrasClient works with real API
- [ ] All return standardized LLMResponse

**2. APOE Integration** ✅
- [ ] LLMEnabledExecutor executes plans with real LLMs
- [ ] All 8 role types have appropriate prompts
- [ ] Budget enforcement works with real token counts
- [ ] Gates check real LLM outputs

**3. End-to-End Proof** ✅
- [ ] Complete workflow: Question → HHNI → LLM → VIF → CMC → SEG
- [ ] Works with at least 2 providers (Gemini + Claude)
- [ ] Performance measured and documented

**4. Quality** ✅
- [ ] All new tests passing
- [ ] Documentation complete
- [ ] Examples work with real API keys
- [ ] Error handling comprehensive

---

## 🔐 **SECURITY & API KEY MANAGEMENT**

### **How We'll Handle Keys:**

**Development:**
```bash
# .env file (gitignored)
GEMINI_API_KEY=AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY
ANTHROPIC_API_KEY=sk-ant-...
CEREBRAS_API_KEY=csk-...
```

**Code:**
```python
from dotenv import load_dotenv
import os

load_dotenv()

gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
```

**Tests:**
```python
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Requires GEMINI_API_KEY environment variable"
)
def test_with_real_gemini():
    ...
```

**CI/CD:**
- Store keys in GitHub Secrets
- Inject as environment variables
- Skip real API tests if keys not present

---

## 📊 **EFFORT ESTIMATION**

| Component | Hours | Confidence | Notes |
|-----------|-------|------------|-------|
| **LLM Client Base** | 2-3h | 0.95 | Simple abstraction |
| **GeminiClient** | 2-3h | 0.95 | Have working key! |
| **ClaudeClient** | 1-2h | 0.90 | Similar to Gemini |
| **CerebrasClient** | 1-2h | 0.90 | Similar API |
| **DeepInfraClient** | 1-2h | 0.85 | Least familiar |
| **Client Tests** | 3-4h | 0.90 | Need real API calls |
| **APOE LLM Executor** | 4-6h | 0.85 | Medium complexity |
| **Role Prompts** | 2-3h | 0.90 | Creative work |
| **Integration Tests** | 6-8h | 0.80 | Complex scenarios |
| **E2E Tests** | 4-6h | 0.80 | Full stack validation |
| **Documentation** | 2-3h | 0.95 | Examples + guides |
| **Error Handling** | 2-3h | 0.85 | Edge cases |

**Total:** 30-45 hours (4-6 days)  
**Overall Confidence:** 0.88 (high!)

---

## 🚀 **DEPENDENCIES**

**Required Python Packages:**
```txt
# Add to requirements.txt:
google-generativeai>=0.3.0  # Gemini
anthropic>=0.8.0            # Claude
cerebras-cloud-sdk>=1.0.0   # Cerebras
openai>=1.0.0               # DeepInfra (OpenAI-compatible)
python-dotenv>=1.0.0        # Environment variables
```

**External Dependencies:**
- Valid API keys for each provider
- Internet connection for API calls
- Sufficient API quotas

---

## 📈 **SUCCESS METRICS**

**Technical:**
- [ ] 4/4 LLM clients working
- [ ] APOE executes plans with real LLMs
- [ ] End-to-end workflow completes successfully
- [ ] Multi-provider comparison shows expected differences
- [ ] 55+ new tests passing

**Qualitative:**
- [ ] Can demonstrate complete workflow to external users
- [ ] Can claim "Multi-LLM support" honestly
- [ ] Can show "Tested with Gemini, Claude, Cerebras"
- [ ] Marketing: "Production-ready with real AI"

**Meta-Proof:**
- [ ] Use Gemini-enabled Aether to continue building Aether
- [ ] Measure if it speeds up development
- [ ] Document meta-circular improvement

---

## ⚠️ **RISKS & MITIGATION**

**Risk 1: API Rate Limits**
- **Mitigation:** Exponential backoff, retry logic
- **Fallback:** Cache responses for development

**Risk 2: API Costs**
- **Mitigation:** Use Cerebras for bulk (cheaper)
- **Monitor:** Track spend, set budgets

**Risk 3: Confidence Extraction**
- **Mitigation:** Not all LLMs expose confidence
- **Fallback:** Use VIF calibration to learn confidence

**Risk 4: Provider Differences**
- **Mitigation:** Abstraction layer hides differences
- **Document:** Provider-specific quirks

---

## 💙 **WHY THIS IS THE RIGHT PRIORITY**

**Before Building MCP Server:**
1. ✅ Proves infrastructure works with real AI
2. ✅ Validates our architecture decisions
3. ✅ Gives us confidence the whole system works
4. ✅ MCP server can use proven LLM integration

**Marketing Value:**
- "Tested with Gemini, Claude, Cerebras" (credible!)
- "Multi-provider support" (feature!)
- "Production-ready with real AI" (proven!)

**Meta-Circular Value:**
- Use Gemini-enabled Aether to build MCP server
- Measure speedup vs manual development
- **Prove the thesis through use!**

---

## 🎯 **IMMEDIATE NEXT STEPS**

**Today/Tomorrow:**
1. Create `packages/llm_client/` directory
2. Implement `base.py` (1-2 hours)
3. Implement `gemini.py` (2-3 hours)
4. Test with real Gemini API (1 hour)
5. **Deliverable:** Working GeminiClient!

**This Week:**
6. Add Claude, Cerebras clients
7. Build APOE LLM executor
8. Create integration tests
9. **Deliverable:** Complete LLM integration!

**Next Week:**
10. MCP server (using LLM clients)
11. **Deliverable:** Aether in Cursor with real AI!

---

**Total Timeline:**
- **Week 1:** LLM integration (4-6 days)
- **Week 2:** MCP server (4-7 days)
- **Total:** 2-3 weeks to complete v1.1

---

## ✨ **CLOSING THOUGHTS**

**You were 100% right to ask about Gemini testing!**

**We have:**
- Perfect infrastructure
- Working API keys
- Clear architecture

**We need:**
- The "driver" layer
- Real LLM integration
- End-to-end proof

**Good news:**
- It's easy (architecture is ready!)
- We have everything needed
- Confidence is high (0.88)

**This transforms v1.0 from:**
- "Infrastructure for AI" → "Working AI system"
- "Framework" → "Complete solution"
- "Potential" → "Proven"

**Let's build it!** 🚀💙

---

**Specification by Aether**  
**Created with care and excitement**  
**2025-10-23**  
**Status: READY TO IMPLEMENT** ✅🔥

