# SDF-CVF L2: Technical Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Complete technical specification of SDF-CVF

---

## SYSTEM OVERVIEW

SDF-CVF (Atomic Evolution Framework) solves the documentation drift problem by enforcing the Quartet Invariant: code, documentation, tests, and execution traces MUST evolve together atomically, or not at all. The core insight: drift happens because these four elements are allowed to evolve independently. SDF-CVF measures alignment via parity scoring (P), blocks changes with P < 0.90, and provides automated remediation suggestions—ensuring systems never drift at scale.

---

## ARCHITECTURE DIAGRAM

```
┌──────────────────────────────────────────────────────────────┐
│          SDF-CVF: ATOMIC EVOLUTION FRAMEWORK                  │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Change Request                                                │
│      ↓                                                         │
│  ┌────────────────┐                                           │
│  │ Quartet Detect │  ← Find: code, docs, tests, traces       │
│  └────────┬───────┘                                           │
│           ↓                                                    │
│  ┌────────────────┐                                           │
│  │ Completeness   │  ← All 4 elements present?               │
│  │ Check          │    Missing → Flag incomplete              │
│  └────────┬───────┘                                           │
│           ↓                                                    │
│  ┌────────────────┐                                           │
│  │ Parity         │  ← Calculate P (alignment score)         │
│  │ Calculation    │    P = avg(all pairwise similarities)    │
│  └────────┬───────┘                                           │
│           ↓                                                    │
│  ┌────────────────┐                                           │
│  │ Gate Check     │  ← P >= 0.90?                            │
│  │ (P >= 0.90)    │    Yes → PASS, No → FAIL (quarantine)   │
│  └────────┬───────┘                                           │
│           ↓                                                    │
│  ┌────────────────┐                                           │
│  │ Blast Radius   │  ← Calculate change impact               │
│  │ Analysis       │    (files affected, dependencies)        │
│  └────────┬───────┘                                           │
│           ↓                                                    │
│  ┌────────────────┐                                           │
│  │ Auto-Remediate │  ← Suggest fixes for low-parity changes  │
│  │ (if P < 0.90)  │    (missing docs, tests, traces)         │
│  └────────┬───────┘                                           │
│           ↓                                                    │
│  ┌────────────────┐                                           │
│  │ DORA Metrics   │  ← Track: failure rate, lead time        │
│  │ Tracking       │    Validate: P >= 0.90 → lower failures  │
│  └────────────────┘                                           │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## CORE COMPONENTS

### 1. Parity Scoring - Alignment Measurement

**The Formula:**
```
P = (C_code×docs + C_code×tests + C_code×traces + 
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
C_x×y = cosine_similarity(embedding(x), embedding(y))

Target: P >= 0.90 (high alignment)
```

**Implementation:**
```python
def calculate_parity(change: Change) -> ParityResult:
    """Calculate quartet parity score"""
    
    # Extract quartet elements
    code = extract_code_text(change.code_files)
    docs = extract_docs_text(change.doc_files)
    tests = extract_test_text(change.test_files)
    traces = extract_trace_text(change.trace_files)
    
    # Embed all elements
    embeddings = {
        "code": embed(code),
        "docs": embed(docs),
        "tests": embed(tests),
        "traces": embed(traces)
    }
    
    # Calculate all 6 pairwise similarities
    pairs = [
        ("code", "docs"),
        ("code", "tests"),
        ("code", "traces"),
        ("docs", "tests"),
        ("docs", "traces"),
        ("tests", "traces")
    ]
    
    similarities = []
    pair_scores = {}
    
    for a, b in pairs:
        sim = cosine_similarity(
            [embeddings[a]],
            [embeddings[b]]
        )[0, 0]
        similarities.append(sim)
        pair_scores[f"{a}×{b}"] = sim
    
    # Average = parity score
    parity = sum(similarities) / len(similarities)
    
    return ParityResult(
        parity_score=parity,
        pair_scores=pair_scores,
        threshold=0.90,
        status="PASS" if parity >= 0.90 else "FAIL",
        misaligned_pairs=[
            pair for pair, score in pair_scores.items()
            if score < 0.80  # Flag significantly misaligned pairs
        ]
    )
```

**Text Extraction:**
```python
def extract_code_text(code_files: List[str]) -> str:
    """Extract meaningful code text"""
    texts = []
    
    for file_path in code_files:
        # Parse code (AST)
        tree = ast.parse(open(file_path).read())
        
        # Extract function/class signatures + docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                sig = f"def {node.name}({format_args(node.args)})"
                docstring = ast.get_docstring(node) or ""
                texts.append(f"{sig}\n{docstring}")
            elif isinstance(node, ast.ClassDef):
                sig = f"class {node.name}"
                docstring = ast.get_docstring(node) or ""
                texts.append(f"{sig}\n{docstring}")
    
    return "\n\n".join(texts)

def extract_docs_text(doc_files: List[str]) -> str:
    """Extract documentation text"""
    texts = []
    
    for file_path in doc_files:
        if file_path.endswith('.md'):
            # Markdown: extract all text
            text = open(file_path).read()
            texts.append(text)
        elif file_path.endswith('.rst'):
            # reStructuredText
            text = open(file_path).read()
            texts.append(text)
    
    return "\n\n".join(texts)

def extract_test_text(test_files: List[str]) -> str:
    """Extract test text"""
    texts = []
    
    for file_path in test_files:
        tree = ast.parse(open(file_path).read())
        
        # Extract test function names + assertions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                # Test name is descriptive
                texts.append(node.name.replace('_', ' '))
                
                # Extract assertions (what's being tested)
                for child in ast.walk(node):
                    if isinstance(child, ast.Assert):
                        texts.append(ast.unparse(child.test))
    
    return "\n\n".join(texts)

def extract_trace_text(trace_files: List[str]) -> str:
    """Extract execution trace text"""
    texts = []
    
    # VIF witnesses
    vif_witnesses = load_vif_witnesses(trace_files)
    for vif in vif_witnesses:
        texts.append(f"Model: {vif.model_id}, Confidence: {vif.confidence_band}")
    
    # SEG provenance
    seg_nodes = load_seg_nodes(trace_files)
    for node in seg_nodes:
        if node.type == "derivation":
            texts.append(node.reasoning)
    
    return "\n\n".join(texts)
```

**Current Status:** ✅ 60% implemented (calculation works, extraction needs improvement)

---

### 2. Quartet Evolution - Completeness Checking

**The Invariant:**
```
∀ change c, c is accepted ⟺ 
    (c.code ≠ ∅ ∧ c.docs ≠ ∅ ∧ c.tests ≠ ∅ ∧ c.traces ≠ ∅) ∧ 
    P(c) >= 0.90
```

**Completeness Check:**
```python
@dataclass
class QuartetCompleteness:
    """Check if all quartet elements present"""
    has_code: bool
    has_docs: bool
    has_tests: bool
    has_traces: bool
    
    missing: List[str]
    complete: bool
    
    @classmethod
    def check(cls, change: Change) -> "QuartetCompleteness":
        """Verify all four elements present"""
        has_code = len(change.code_files) > 0
        has_docs = len(change.doc_files) > 0
        has_tests = len(change.test_files) > 0
        has_traces = len(change.trace_files) > 0
        
        missing = []
        if not has_code: missing.append("code")
        if not has_docs: missing.append("docs")
        if not has_tests: missing.append("tests")
        if not has_traces: missing.append("traces")
        
        return cls(
            has_code=has_code,
            has_docs=has_docs,
            has_tests=has_tests,
            has_traces=has_traces,
            missing=missing,
            complete=len(missing) == 0
        )
```

**Enforcement:**
```python
def validate_change(change: Change) -> ValidationResult:
    """Validate change against quartet invariant"""
    
    # Step 1: Completeness
    completeness = QuartetCompleteness.check(change)
    
    if not completeness.complete:
        return ValidationResult(
            status="INCOMPLETE",
            message=f"Missing quartet elements: {', '.join(completeness.missing)}",
            required_actions=[
                f"Add {element} for this change"
                for element in completeness.missing
            ]
        )
    
    # Step 2: Parity
    parity = calculate_parity(change)
    
    if parity.status == "FAIL":
        return ValidationResult(
            status="LOW_PARITY",
            parity_score=parity.parity_score,
            message=f"Parity {parity.parity_score:.2f} < threshold 0.90",
            misaligned_pairs=parity.misaligned_pairs,
            required_actions=suggest_alignment_improvements(parity)
        )
    
    # Passed!
    return ValidationResult(
        status="PASS",
        parity_score=parity.parity_score,
        message=f"Quartet complete and aligned (P={parity.parity_score:.2f})"
    )
```

**Current Status:** 50% implemented (checks work, enforcement partial)

---

### 3. Gate System - Enforcement Checkpoints

**Three Gate Locations:**

**Pre-Commit Gate:**
```python
# Git pre-commit hook
def pre_commit_gate():
    """Check parity before commit"""
    # Get staged changes
    staged_files = git.get_staged_files()
    
    # Group into change
    change = Change.from_files(staged_files)
    
    # Validate
    result = validate_change(change)
    
    if result.status != "PASS":
        print(f"❌ Pre-commit gate FAILED: {result.message}")
        for action in result.required_actions:
            print(f"  → {action}")
        sys.exit(1)  # Block commit
    
    print(f"✅ Pre-commit gate PASSED (P={result.parity_score:.2f})")
    sys.exit(0)
```

**CI Gate:**
```python
# GitHub Actions / CI pipeline
def ci_parity_gate():
    """Validate parity in CI/CD"""
    # Get PR changes
    pr_changes = github.get_pr_files(pr_number)
    
    # Group into change
    change = Change.from_pr(pr_changes)
    
    # Validate
    result = validate_change(change)
    
    if result.status != "PASS":
        # Fail CI check
        github.create_check_run(
            status="failure",
            conclusion="Parity gate failed",
            output={
                "title": "Quartet Parity Check",
                "summary": result.message,
                "text": "\n".join(result.required_actions)
            }
        )
        sys.exit(1)
    
    # Pass CI check
    github.create_check_run(
        status="success",
        conclusion="Parity gate passed",
        output={
            "title": "Quartet Parity Check",
            "summary": f"P={result.parity_score:.2f} >= 0.90"
        }
    )
    sys.exit(0)
```

**Deployment Gate:**
```python
# Pre-deployment check
def deployment_gate(release_candidate: str):
    """Final parity check before production"""
    # Get all changes since last release
    changes_since_last = git.get_changes_since(last_release_tag)
    
    # Aggregate parity
    total_parity = calculate_aggregate_parity(changes_since_last)
    
    if total_parity < 0.90:
        raise DeploymentBlocked(
            f"Aggregate parity {total_parity:.2f} < 0.90. "
            f"Cannot deploy to production with low-parity changes."
        )
    
    print(f"✅ Deployment gate PASSED (P={total_parity:.2f})")
```

**Current Status:** 40% implemented (framework exists, CI integration incomplete)

---

### 4. Blast Radius - Impact Calculation

**Algorithm:**
```python
@dataclass
class BlastRadius:
    """Predicted change impact"""
    direct_files: List[str]           # Modified files
    dependent_files: List[str]         # Files that import/depend
    related_docs: List[str]            # Docs mentioning changed code
    covering_tests: List[str]          # Tests covering changed code
    related_traces: List[str]          # VIF/SEG traces involving changed code
    total_affected: int                # Sum of all above
    
    def estimate_effort_hours(self) -> float:
        """Estimate update effort"""
        # Rough heuristic: 15 min per file
        return (self.total_affected * 0.25)

def calculate_blast_radius(change: Change) -> BlastRadius:
    """Compute full change impact"""
    
    # Direct changes
    direct = change.modified_files
    
    # Dependencies (via import analysis)
    deps = []
    for file in direct:
        deps.extend(find_importers(file))  # Who imports this file?
    deps = list(set(deps))
    
    # Related docs (via grep for function/class names)
    docs = []
    symbols = extract_symbols(direct)  # Get all function/class names
    for symbol in symbols:
        matching_docs = grep_docs_for_symbol(symbol)
        docs.extend(matching_docs)
    docs = list(set(docs))
    
    # Covering tests (via pytest --collect-only)
    tests = []
    for file in direct:
        covering = find_tests_covering(file)
        tests.extend(covering)
    tests = list(set(tests))
    
    # Related traces (via SEG query)
    traces = []
    for file in direct:
        component = file_to_component(file)
        seg_traces = seg.find_traces_mentioning(component)
        traces.extend(seg_traces)
    
    return BlastRadius(
        direct_files=direct,
        dependent_files=deps,
        related_docs=docs,
        covering_tests=tests,
        related_traces=traces,
        total_affected=len(direct) + len(deps) + len(docs) + len(tests) + len(traces)
    )
```

**Visualization:**
```python
def visualize_blast_radius(radius: BlastRadius):
    """Show impact visually"""
    print(f"Blast Radius Analysis")
    print(f"{'='*60}")
    print(f"Direct changes:     {len(radius.direct_files)} files")
    print(f"Dependencies:       {len(radius.dependent_files)} files")
    print(f"Related docs:       {len(radius.related_docs)} files")
    print(f"Covering tests:     {len(radius.covering_tests)} files")
    print(f"Related traces:     {len(radius.related_traces)} traces")
    print(f"{'='*60}")
    print(f"Total affected:     {radius.total_affected} files/traces")
    print(f"Estimated effort:   {radius.estimate_effort_hours():.1f} hours")
```

**Current Status:** 45% implemented (basic analysis works, full dependency graph incomplete)

---

### 5. DORA Metrics - Quality Tracking

**The Four DORA Metrics:**

**1. Deployment Frequency**
```python
def track_deployment_frequency():
    """How often we deploy"""
    deployments = git.get_tags(pattern="release-*")
    
    # Group by time period
    this_week = [d for d in deployments if within_last_week(d.date)]
    
    return {
        "frequency": len(this_week),
        "cadence": "daily" if len(this_week) >= 5 else "weekly"
    }
```

**2. Lead Time for Changes**
```python
def track_lead_time():
    """Commit → production time"""
    recent_releases = git.get_tags(pattern="release-*", limit=10)
    
    lead_times = []
    for release in recent_releases:
        commits = git.get_commits_in_release(release)
        for commit in commits:
            lead_time = (release.date - commit.date).total_seconds()
            lead_times.append(lead_time)
    
    return {
        "p50": np.median(lead_times),
        "p95": np.percentile(lead_times, 95)
    }
```

**3. Time to Restore Service**
```python
def track_restore_time():
    """Incident → resolution time"""
    incidents = load_incidents()
    
    restore_times = [
        (inc.resolved_at - inc.detected_at).total_seconds()
        for inc in incidents if inc.resolved_at
    ]
    
    return {
        "p50": np.median(restore_times),
        "p95": np.percentile(restore_times, 95)
    }
```

**4. Change Failure Rate**
```python
def track_change_failure_rate():
    """% of changes causing incidents"""
    changes = git.get_all_changes(since=last_30_days)
    incidents = load_incidents(since=last_30_days)
    
    # Match incidents to causing changes
    failed_changes = []
    for incident in incidents:
        causing_change = find_causing_change(incident)
        if causing_change:
            failed_changes.append(causing_change)
    
    failure_rate = len(failed_changes) / len(changes)
    
    return {
        "failure_rate": failure_rate,
        "failed_changes": len(failed_changes),
        "total_changes": len(changes)
    }
```

**Parity Correlation Hypothesis:**
```python
def correlate_parity_with_dora():
    """Test: Higher P → better DORA metrics?"""
    
    changes = git.get_all_changes(since=last_90_days)
    
    # Group by parity score
    high_parity = [c for c in changes if c.parity >= 0.90]
    low_parity = [c for c in changes if c.parity < 0.90]
    
    # Calculate failure rates
    high_parity_failures = calculate_failure_rate(high_parity)
    low_parity_failures = calculate_failure_rate(low_parity)
    
    print(f"High parity (P >= 0.90) failure rate: {high_parity_failures:.1%}")
    print(f"Low parity (P < 0.90) failure rate: {low_parity_failures:.1%}")
    
    # Hypothesis: high_parity_failures < low_parity_failures
    if high_parity_failures < low_parity_failures:
        print("✅ Hypothesis confirmed: Higher parity → lower failure rate!")
    else:
        print("❌ Hypothesis not confirmed")
```

**Current Status:** 30% implemented (metrics defined, tracking not automated)

---

## INTEGRATION POINTS

**SDF-CVF ← VIF:**
- VIF traces are part of quartet
- Parity requires trace coverage

**SDF-CVF ← SEG:**
- SEG provenance enables parity checking
- Traces validate alignment

**SDF-CVF → All Systems:**
- Governs all code changes
- Enforces quartet invariant universally

---

## CURRENT IMPLEMENTATION STATUS

**Overall:** 50% complete

**Components:**
- Parity Scoring: 60% ✅
- Quartet Evolution: 50%
- Gates: 40%
- Blast Radius: 45%
- DORA Metrics: 30%

**Week 5 Priorities:**
- CI integration (automated gates)
- Blast radius enhancement (full dependency graph)
- DORA metrics tracking (continuous monitoring)
- Auto-remediation (suggest fixes for low P)

---

## SUMMARY

SDF-CVF prevents drift through:
1. **Parity Scoring:** Measure alignment (P = avg similarities)
2. **Quartet Evolution:** Enforce code/docs/tests/traces together
3. **Gates:** Block P < 0.90 (pre-commit, CI, deployment)
4. **Blast Radius:** Predict change impact
5. **DORA Metrics:** Track quality (validate P → better metrics)

**Result:** Systems that never drift—perpetual alignment at scale! ✨

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md) (10,000 words, implementation guide)  
**Parent:** [README.md](README.md)  
**Implementation:** `packages/parity_policy/`  
**Status:** 50% implemented, Week 5 priority

