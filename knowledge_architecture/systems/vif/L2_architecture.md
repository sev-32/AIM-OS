# VIF L2: Technical Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Complete technical specification of VIF

---

## SYSTEM OVERVIEW

VIF (Verifiable Intelligence Framework) makes every AI operation fully traceable and trustworthy through complete provenance envelopes, uncertainty quantification, and deterministic replay. The core innovation: instead of black-box AI where you can't verify how conclusions were reached, VIF captures EVERYTHING—model version, exact prompts, context used, tools invoked, confidence levels, and enables bit-identical reproduction of outputs.

---

## ARCHITECTURE DIAGRAM

```
┌────────────────────────────────────────────────────────────┐
│            VERIFIABLE INTELLIGENCE FRAMEWORK                │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  AI Operation                                                │
│      ↓                                                       │
│  ┌──────────────┐                                           │
│  │ Pre-Execution│                                           │
│  │ Witness Prep │ ← Capture: model, context, prompt, seed  │
│  └──────┬───────┘                                           │
│         ↓                                                    │
│  ┌──────────────┐                                           │
│  │ κ-Gate       │ ← Check confidence >= threshold           │
│  │ (Abstention) │   If < κ: ABSTAIN (don't guess!)         │
│  └──────┬───────┘                                           │
│         ↓                                                    │
│  ┌──────────────┐                                           │
│  │ AI Execution │ ← With deterministic seed                 │
│  └──────┬───────┘                                           │
│         ↓                                                    │
│  ┌──────────────┐                                           │
│  │ Post-Exec    │                                           │
│  │ Witness Gen  │ ← Generate VIF envelope                   │
│  └──────┬───────┘                                           │
│         ↓                                                    │
│  ┌──────────────────────────────────┐                      │
│  │      WITNESS ENVELOPE (VIF)      │                      │
│  ├──────────────────────────────────┤                      │
│  │ • Model ID + weights hash        │                      │
│  │ • Context snapshot ID            │                      │
│  │ • Prompt hash                    │                      │
│  │ • Tools invoked                  │                      │
│  │ • Confidence band (A/B/C)        │                      │
│  │ • ECE score (calibration)        │                      │
│  │ • Replay seed                    │                      │
│  │ • Timestamp                      │                      │
│  └──────┬───────────────────────────┘                      │
│         ↓                                                    │
│  ┌──────────────┐                                           │
│  │ ECE Tracker  │ ← Update calibration metrics             │
│  └──────┬───────┘                                           │
│         ↓                                                    │
│  ┌──────────────┐                                           │
│  │ SEG Storage  │ ← Witness becomes provenance node        │
│  └──────────────┘                                           │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## CORE COMPONENTS

### 1. Witness Envelopes - Complete Provenance

**Schema (Complete):**
```python
@dataclass
class VIF:
    """Verifiable Intelligence Framework witness envelope"""
    
    # === IDENTITY ===
    id: str = field(default_factory=lambda: f"vif_{uuid.uuid4().hex}")
    version: str = "1.0"
    
    # === WHAT MODEL ===
    model_id: str                    # "gpt-4-turbo-2025-01-15"
    model_provider: str              # "openai", "anthropic", "local"
    weights_hash: Optional[str]      # SHA-256 of weights file (if available)
    
    # === WHAT DATA ===
    context_snapshot_id: str         # CMC snapshot reference
    prompt_template: str             # Template used (before variable substitution)
    prompt_hash: str                 # SHA-256 of exact prompt sent
    prompt_tokens: int               # Token count
    retrieved_atom_ids: List[str]    # From HHNI retrieval
    
    # === WHAT TOOLS ===
    tool_ids: List[str]              # ["hhni.retrieve", "cmc.store", "code.exec"]
    tool_parameters: Dict[str, Any]  # Exact params for each tool
    tool_results_hash: str           # Hash of tool outputs
    
    # === UNCERTAINTY ===
    confidence_score: float          # 0.0-1.0 (model's reported confidence)
    confidence_band: str             # "A" (0.95-1.0) | "B" (0.80-0.94) | "C" (<0.80)
    ece_score: Optional[float]       # Expected Calibration Error (if computed)
    entropy: float                   # Output distribution entropy
    top_k_probs: List[Tuple[str, float]]  # Top-K token probabilities
    
    # === REPLAY ===
    replay_seed: Optional[int]       # For deterministic reproduction
    temperature: float               # Generation parameter
    top_p: Optional[float]           # Nucleus sampling parameter
    other_params: Dict[str, Any]     # Any other generation params
    
    # === META ===
    writer: str                      # "system" | "user" | "agent_planner" | "apoe_step_X"
    created_at: datetime             # When witness created
    execution_time_ms: float         # How long operation took
    parent_vif_id: Optional[str]     # Chain of witnesses
    
    # === VALIDATION ===
    signature: Optional[str]         # Cryptographic signature (future)
    
    class Config:
        frozen = True  # Immutable after creation
```

**Creation Example:**
```python
def create_witness(
    model_id: str,
    prompt: str,
    context: List[Atom],
    output: str,
    confidence: float,
    tools_used: List[ToolCall],
    seed: int
) -> VIF:
    """Generate VIF witness for AI operation"""
    
    # Create context snapshot
    snapshot = create_snapshot(context, notes="VIF context capture")
    
    # Calculate confidence band
    band = determine_confidence_band(confidence)
    
    # Hash prompt for verification
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    
    # Create witness
    vif = VIF(
        model_id=model_id,
        model_provider="openai",
        context_snapshot_id=snapshot.id,
        prompt_template="[template]",
        prompt_hash=prompt_hash,
        prompt_tokens=count_tokens(prompt),
        retrieved_atom_ids=[atom.id for atom in context],
        tool_ids=[call.name for call in tools_used],
        tool_parameters={call.name: call.params for call in tools_used},
        tool_results_hash=hash_tool_results(tools_used),
        confidence_score=confidence,
        confidence_band=band,
        entropy=calculate_entropy(output),
        replay_seed=seed,
        temperature=0.7,
        writer="system",
        created_at=datetime.utcnow(),
        execution_time_ms=100.5
    )
    
    return vif
```

**Current Status:** 40% implemented (basic fields work, missing: weights hash, tool tracking, full metadata)

---

### 2. κ-Gating (Behavioral Abstention)

**Core Concept:** AI must say "I don't know" when confidence < threshold, not guess

**Formula:**
```
κ(task) = confidence threshold for task criticality

If confidence(output) < κ(task):
    → ABSTAIN (escalate to HITL)
Else:
    → PROCEED (use output)
```

**Task-Specific Thresholds:**
```python
class KappaThresholds:
    """Per-task confidence thresholds"""
    CRITICAL = 0.95      # Medical, legal, safety-critical
    IMPORTANT = 0.85     # Code generation, data analysis
    ROUTINE = 0.70       # Summarization, formatting
    LOW_STAKES = 0.60    # Suggestions, recommendations

def determine_kappa(task_criticality: str) -> float:
    """Get κ threshold for task"""
    return {
        "critical": KappaThresholds.CRITICAL,
        "important": KappaThresholds.IMPORTANT,
        "routine": KappaThresholds.ROUTINE,
        "low_stakes": KappaThresholds.LOW_STAKES
    }[task_criticality]
```

**Gate Implementation:**
```python
@dataclass
class KappaGateResult:
    """Result of κ-gate check"""
    status: str              # "PASS" | "ABSTAIN"
    confidence: float        # Reported confidence
    threshold: float         # κ threshold
    task_criticality: str    # Task type
    reason: Optional[str]    # Why abstained (if applicable)
    escalation: Optional[str]  # Escalation path (HITL, retry, etc.)

def kappa_gate(
    output: Any,
    confidence: float,
    task_criticality: str,
    enable_abstention: bool = True
) -> KappaGateResult:
    """Enforce behavioral abstention"""
    
    kappa = determine_kappa(task_criticality)
    
    if confidence < kappa:
        if enable_abstention:
            return KappaGateResult(
                status="ABSTAIN",
                confidence=confidence,
                threshold=kappa,
                task_criticality=task_criticality,
                reason=f"Confidence {confidence:.2f} below threshold {kappa:.2f}",
                escalation="hitl"  # Human-in-the-loop
            )
        else:
            # Log warning but proceed (abstention disabled)
            log.warning(f"κ-gate would abstain but abstention disabled: conf={confidence}, κ={kappa}")
    
    return KappaGateResult(
        status="PASS",
        confidence=confidence,
        threshold=kappa,
        task_criticality=task_criticality
    )
```

**Example Usage:**
```python
# Critical task (medical diagnosis)
diagnosis = model.generate(prompt, task="medical_diagnosis")
confidence = model.get_confidence()

gate_result = kappa_gate(diagnosis, confidence, "critical")

if gate_result.status == "ABSTAIN":
    # Don't use uncertain diagnosis!
    return f"I don't have sufficient confidence ({confidence:.0%}) to provide a diagnosis. " \
           f"Medical tasks require {gate_result.threshold:.0%} confidence. " \
           f"Escalating to human medical professional."
else:
    return diagnosis
```

**Current Status:** 20% implemented (design complete, enforcement not yet automated)

---

### 3. ECE Tracking (Calibration Quality)

**Expected Calibration Error:**
```
ECE = (1/N) × Σ |confidence_i - accuracy_i|

Where:
- N = number of predictions
- confidence_i = AI's reported confidence (0-1)
- accuracy_i = actual correctness (1 if correct, 0 if wrong)

Target: ECE ≤ 0.05 (well-calibrated)
```

**Implementation:**
```python
@dataclass
class CalibrationTracker:
    """Track confidence vs accuracy over time"""
    predictions: List[Prediction] = field(default_factory=list)
    
    @dataclass
    class Prediction:
        id: str
        confidence: float
        output: Any
        ground_truth: Optional[Any] = None  # Set when verified
        correct: Optional[bool] = None      # Set when verified
        timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def record_prediction(self, confidence: float, output: Any) -> str:
        """Record a prediction"""
        pred = self.Prediction(
            id=f"pred_{uuid.uuid4().hex[:8]}",
            confidence=confidence,
            output=output
        )
        self.predictions.append(pred)
        return pred.id
    
    def verify_prediction(self, pred_id: str, ground_truth: Any):
        """Verify prediction correctness"""
        pred = self.find_prediction(pred_id)
        pred.ground_truth = ground_truth
        pred.correct = (pred.output == ground_truth)
    
    def calculate_ece(self) -> float:
        """Calculate Expected Calibration Error"""
        verified = [p for p in self.predictions if p.correct is not None]
        
        if not verified:
            return None  # Not enough data
        
        total_error = 0.0
        for pred in verified:
            accuracy = 1.0 if pred.correct else 0.0
            error = abs(pred.confidence - accuracy)
            total_error += error
        
        ece = total_error / len(verified)
        return ece
    
    def calibration_status(self) -> str:
        """Assess calibration quality"""
        ece = self.calculate_ece()
        
        if ece is None:
            return "INSUFFICIENT_DATA"
        elif ece <= 0.05:
            return "WELL_CALIBRATED"
        elif ece <= 0.10:
            return "ACCEPTABLE"
        else:
            return "POORLY_CALIBRATED"
```

**Calibration Visualization:**
```python
def plot_calibration(tracker: CalibrationTracker):
    """Plot confidence vs accuracy"""
    verified = [p for p in tracker.predictions if p.correct is not None]
    
    # Group by confidence bins
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    bin_confidences = []
    bin_accuracies = []
    
    for i in range(len(bins) - 1):
        low, high = bins[i], bins[i+1]
        in_bin = [p for p in verified if low <= p.confidence < high]
        
        if in_bin:
            avg_conf = np.mean([p.confidence for p in in_bin])
            avg_acc = np.mean([1.0 if p.correct else 0.0 for p in in_bin])
            
            bin_confidences.append(avg_conf)
            bin_accuracies.append(avg_acc)
    
    # Plot: perfect calibration = diagonal line
    plt.plot(bin_confidences, bin_accuracies, 'o-', label='Actual')
    plt.plot([0, 1], [0, 1], '--', label='Perfect calibration')
    plt.xlabel('Confidence')
    plt.ylabel('Accuracy')
    plt.title(f'Calibration Plot (ECE={tracker.calculate_ece():.3f})')
    plt.legend()
    plt.show()
```

**Current Status:** 15% implemented (formula documented, tracking not automated)

---

### 4. Deterministic Replay

**Goal:** Reproduce exact outputs bit-identically

**Requirements:**
1. Same model (version + weights)
2. Same prompt (exact text)
3. Same context (snapshot)
4. Same seed
5. Same generation params (temperature, top_p, etc.)

**Implementation:**
```python
def generate_with_replay(
    prompt: str,
    context: List[Atom],
    model_id: str,
    task_criticality: str = "routine"
) -> Tuple[str, VIF]:
    """Generate output with replay capability"""
    
    # Set deterministic seed
    replay_seed = random.randint(0, 2**32 - 1)
    set_seed(replay_seed)
    
    # Create context snapshot
    snapshot = create_snapshot(context, notes="Replay-capable generation")
    
    # Generate with fixed params (deterministic)
    output = model.generate(
        prompt=prompt,
        temperature=0.0,  # Deterministic (or use temperature=0.7 with seed)
        seed=replay_seed,
        max_tokens=1000
    )
    
    # Get confidence
    confidence = model.get_confidence()
    
    # κ-gate check
    gate_result = kappa_gate(output, confidence, task_criticality)
    if gate_result.status == "ABSTAIN":
        raise ConfidenceTooLow(gate_result.reason)
    
    # Create VIF witness
    vif = VIF(
        model_id=model_id,
        context_snapshot_id=snapshot.id,
        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
        prompt_tokens=count_tokens(prompt),
        confidence_score=confidence,
        confidence_band=gate_result.confidence_band,
        replay_seed=replay_seed,
        temperature=0.0,
        created_at=datetime.utcnow(),
        ...
    )
    
    return output, vif

def replay_from_vif(vif: VIF) -> str:
    """Reproduce exact output from VIF witness"""
    
    # Load exact context
    snapshot = load_snapshot(vif.context_snapshot_id)
    context = snapshot.get_atoms()
    
    # Reconstruct prompt (need to store template + vars, or full prompt)
    prompt = reconstruct_prompt(vif)
    
    # Verify prompt hash
    actual_hash = hashlib.sha256(prompt.encode()).hexdigest()
    if actual_hash != vif.prompt_hash:
        raise ReplayError("Prompt hash mismatch!")
    
    # Set same seed
    set_seed(vif.replay_seed)
    
    # Generate with exact same params
    output = model.generate(
        prompt=prompt,
        temperature=vif.temperature,
        top_p=vif.top_p,
        seed=vif.replay_seed,
        max_tokens=1000,
        **vif.other_params
    )
    
    return output  # Should be bit-identical to original!
```

**Replay Validation Test:**
```python
def test_deterministic_replay():
    """Verify replay produces identical output"""
    
    # Generate original
    original_output, vif = generate_with_replay(
        prompt="What is 2+2?",
        context=[],
        model_id="gpt-4-turbo"
    )
    
    # Replay
    replayed_output = replay_from_vif(vif)
    
    # Should be identical
    assert original_output == replayed_output, "Replay failed to reproduce output!"
```

**Current Status:** 25% implemented (basic seed tracking, full replay not yet working)

---

### 5. Confidence Bands (Human-Readable Uncertainty)

**The Three Bands:**

**Band A (High Confidence): 0.95-1.00**
```python
@dataclass
class ConfidenceBandA:
    range = (0.95, 1.00)
    color = "green"
    recommendation = "Proceed with confidence"
    typical_use_cases = [
        "Well-established facts",
        "Simple calculations",
        "Verified information",
        "High-certainty predictions"
    ]
    example = "AI: 95% confident that Python is a programming language"
```

**Band B (Medium Confidence): 0.80-0.94**
```python
@dataclass
class ConfidenceBandB:
    range = (0.80, 0.94)
    color = "yellow"
    recommendation = "Proceed with caution, verify key claims"
    typical_use_cases = [
        "Moderate complexity tasks",
        "Interpretations requiring judgment",
        "Predictions with some uncertainty",
        "Generated code (review needed)"
    ]
    example = "AI: 85% confident this code handles edge case X correctly (review recommended)"
```

**Band C (Low Confidence): 0.00-0.79**
```python
@dataclass
class ConfidenceBandC:
    range = (0.00, 0.79)
    color = "red"
    recommendation = "Review carefully or abstain (κ-gate may trigger)"
    typical_use_cases = [
        "High uncertainty tasks",
        "Ambiguous inputs",
        "Novel scenarios",
        "Critical decisions (abstain if κ > 0.79)"
    ]
    example = "AI: 70% confident about this medical diagnosis (TOO LOW - ABSTAIN for critical task)"
```

**Band Determination:**
```python
def determine_confidence_band(confidence: float) -> str:
    """Map numeric confidence to band"""
    if confidence >= 0.95:
        return "A"
    elif confidence >= 0.80:
        return "B"
    else:
        return "C"

def band_to_color(band: str) -> str:
    """UI color for band"""
    return {"A": "green", "B": "yellow", "C": "red"}[band]

def band_to_recommendation(band: str) -> str:
    """User-facing recommendation"""
    return {
        "A": "High confidence - proceed",
        "B": "Medium confidence - verify key claims",
        "C": "Low confidence - review carefully or abstain"
    }[band]
```

**UI Integration Example:**
```python
def display_with_confidence(output: str, vif: VIF):
    """Display AI output with confidence indicator"""
    band = vif.confidence_band
    color = band_to_color(band)
    recommendation = band_to_recommendation(band)
    
    return f"""
    <div class="ai-output" style="border-left: 4px solid {color};">
        <div class="confidence-indicator">
            <span class="band-{band}">Confidence: Band {band} ({vif.confidence_score:.0%})</span>
            <span class="recommendation">{recommendation}</span>
        </div>
        <div class="output-content">
            {output}
        </div>
        <div class="vif-link">
            <a href="/vif/{vif.id}">View full provenance</a>
        </div>
    </div>
    """
```

**Current Status:** ✅ 50% implemented (working, needs UI integration)

---

## INTEGRATION POINTS

**VIF → CMC:**
- VIF witnesses stored as atoms in CMC
- Context snapshots referenced from CMC

**VIF → SEG:**
- VIF witnesses become source nodes in SEG
- Provenance chains tracked as graph edges

**VIF → APOE:**
- Every APOE step emits VIF witness
- Witness role generates VIF envelopes

**VIF → SDF-CVF:**
- VIF traces are part of quartet (code/docs/tests/traces)
- Parity requires VIF witness coverage

---

## CURRENT IMPLEMENTATION STATUS

**Overall:** 30% complete

**Components:**
- Witness Envelopes: 40% ✅
- κ-Gating: 20%
- ECE Tracking: 15%
- Deterministic Replay: 25%
- Confidence Bands: 50% ✅

**Week 4 Priorities:**
- Implement κ-gating enforcement (automated abstention)
- Build ECE tracking system (continuous calibration monitoring)
- Complete deterministic replay (bit-identical reproduction)
- Integrate with APOE (witness every step)

---

## SUMMARY

VIF ensures trustworthy AI through:
1. **Witness Envelopes:** Complete provenance capture
2. **κ-Gating:** Behavioral abstention (honesty about uncertainty)
3. **ECE Tracking:** Calibration measurement (confidence vs accuracy)
4. **Deterministic Replay:** Bit-identical reproduction
5. **Confidence Bands:** Human-readable transparency

**Result:** Verifiable, calibrated, replay-capable, trustworthy AI! ✨

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md) (10,000 words, implementation guide)  
**Parent:** [README.md](README.md)  
**Implementation:** `packages/seg/witness.py`  
**Status:** 30% implemented, Week 4 priority (critical for trust!)

