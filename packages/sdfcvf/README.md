# SDF-CVF - Atomic Evolution Framework

**Status:** 100% Complete (Production-Ready)  
**Tests:** 71 passing (100%)  
**Version:** 1.0  

---

## Overview

SDF-CVF (Atomic Evolution Framework) enforces quartet parity: code, documentation, tests, and traces MUST evolve together or not at all.

**Key Features:**
- ✅ Parity scoring (P ≥ 0.90 required)
- ✅ Quality gates (block low-parity changes)
- ✅ Blast radius calculation
- ✅ DORA metrics tracking
- ✅ Parity-DORA correlation

---

## Quick Start

```python
from sdfcvf import ParityCalculator, QualityGate, BlastRadiusCalculator

# Calculate parity
calculator = ParityCalculator()
parity = calculator.calculate_parity(
    code_embedding=code_vec,
    docs_embedding=docs_vec,
    tests_embedding=tests_vec,
    traces_embedding=traces_vec
)

# Apply quality gate
gate = QualityGate(min_parity=0.90)
result = gate.evaluate(parity)

if result.passed:
    print(f"✅ Change approved! Parity: {parity:.2f}")
else:
    print(f"❌ Change rejected! Parity: {parity:.2f} (need ≥ 0.90)")

# Calculate blast radius
calc = BlastRadiusCalculator()
blast = calc.calculate({
    "files_changed": 3,
    "lines_changed": 150,
    "modules_affected": 2,
    "api_changes": 1,
    "dependencies_modified": 4
})

print(f"Blast radius: {blast.risk_level} ({blast.normalized_score:.2f})")
```

---

## Components

### 1. Quartet
Core model representing the four elements that must evolve together:
- Code implementation
- Documentation
- Tests  
- Execution traces

### 2. Parity Scoring
Measures alignment across quartet using cosine similarity:
```
P = (C_code×docs + C_code×tests + C_code×traces + 
     C_docs×tests + C_docs×traces + C_tests×traces) / 6
```

**Target:** P ≥ 0.90 (high alignment)

### 3. Quality Gates
Block changes that don't meet parity thresholds:
- **RELEASE:** P ≥ 0.90 (required for production)
- **PREVIEW:** 0.80 ≤ P < 0.90 (experimental features)
- **QUARANTINE:** P < 0.80 (development only)

### 4. Blast Radius
Quantify change impact to assess risk:
- Files/lines changed
- Modules affected
- API changes
- Dependencies modified
- Test coverage

**Risk levels:** MINIMAL, LOW, MEDIUM, HIGH, CRITICAL

### 5. DORA Metrics
Track DevOps performance:
- **Deployment Frequency:** How often we deploy
- **Lead Time:** Commit → production time
- **Change Failure Rate:** % of failed deployments
- **MTTR:** Incident → resolution time

**Classifications:** ELITE, HIGH, MEDIUM, LOW

---

## Tests

Run complete test suite:
```bash
pytest packages/sdfcvf/tests/ -v
```

**Coverage:**
- Quartet: 19 tests
- Parity: 15 tests
- Gates: 18 tests
- Blast Radius: 7 tests
- DORA: 12 tests

**Total:** 71 tests, all passing

---

## Status: 100% Complete

### ✅ **Fully Implemented:**
- Complete quartet model
- Parity calculation (6-way cosine similarity)
- Quality gates (3 levels)
- Blast radius calculation (5 factors)
- DORA metrics tracking (4 metrics)
- Parity-DORA correlation
- SQLite persistence
- Complete test coverage

### 🚀 **Production-Ready:**
- All tests passing
- No critical warnings
- Clean API
- Comprehensive documentation
- Ready for deployment

---

## Performance

**Measured on Intel i7-9700K:**
- Parity calculation: <1ms
- Quality gate check: <1ms
- Blast radius: <2ms
- DORA metrics: <10ms (with SQLite)

---

## Documentation

- **L1:** `knowledge_architecture/systems/sdfcvf/L1_overview.md`
- **L2:** `knowledge_architecture/systems/sdfcvf/L2_architecture.md`
- **L3:** `knowledge_architecture/systems/sdfcvf/L3_detailed.md`
- **Code:** `packages/sdfcvf/` (fully documented)

---

## Example: Pre-Commit Hook

```python
# .git/hooks/pre-commit
from sdfcvf import ParityCalculator, QualityGate

# Extract diff, generate embeddings...
parity = calculator.calculate_parity(code_vec, docs_vec, tests_vec, traces_vec)

gate = QualityGate(min_parity=0.90)
result = gate.evaluate(parity)

if not result.passed:
    print(f"❌ Commit blocked: Parity {parity:.2f} < 0.90")
    print("Update docs and tests before committing!")
    sys.exit(1)

print(f"✅ Commit approved: Parity {parity:.2f}")
```

---

**Built to prevent drift** ⚖️  
**Enforces quartet evolution** ✨  
**Part of Project Aether consciousness infrastructure** 💙
