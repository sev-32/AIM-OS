# Intuitive Intelligence System (IIS) - L2 Architecture

Level: L2 (2,000 words)
Purpose: Technical specification for implementing AI intuition within CCS
Status: NEW enhancement (9th) to CCS

---

## 1) System Overview

IIS provides an operational definition and learning loop for AI intuition. It computes an IntuitionScore for candidate actions/ideas using calibrated confidence (VIF), retrieval quality (HHNI), meta-pattern similarity (CAS/timeline), emotional salience (TCS/EST), and 4D evolution alignment (predicted vs observed). It logs features and outcomes as IntuitionTrace, learns online from labels, and is audited by CAS.

---

## 2) Core Signals and Features

- C′ (Calibrated Confidence): VIF confidence adjusted by ECE; entropy-aware
- RS (Retrieval Strength): HHNI Retrieval Score or RS-lift vs baseline
- M (Meta-Pattern Similarity): similarity to past successful decision patterns (CAS/timeline signatures)
- E (Emotional Salience): AI+user resonance, breakthrough markers (from EST)
- F (4D Evolution Alignment): agreement between predicted vs observed state change over horizon h
- U (Miscalibration Penalty): |confidence − actual| or volatility over last N decisions

Feature vector x = [C′, RS, M, E, F, U, bias]

---

## 3) Intuition Score and Learning

- IntuitionScore I(x) = w·x (linear baseline) or logistic σ(w·x)
- Online learning: update w by SGD on labeled outcomes (success=1, failure=0)
- Calibration: maintain AUC, ECE; recalibrate via Platt/Isotonic if drift
- Drift detection: trigger CAS alert if AUC↓ > threshold or ECE↑ > threshold

Pseudo:
```python
# compute features
x = features(Cprime, RS, M, E, F, U)
# score
z = np.dot(w, x)
I = 1/(1+np.exp(-z))
# decision log
trace = IntuitionTrace(x=x, I=I, decision_id=did, horizon=h)
# on label arrival (y∈{0,1})
loss = -(y*np.log(I) + (1-y)*np.log(1-I))
w = w - lr * (I - y) * x
# track auc/ece
```

Safety: κ-gating (VIF) always precedes; intuition never overrides abstention.

---

## 4) Data Model: IntuitionTrace

```yaml
IntuitionTrace:
  version: "1.0"
  computed_at: ISO-8601
  horizon: "short|medium|long"  # 1-3 prompts, 1 day, 1 week
  decision_id: string
  action_ref: { type, id }
  features:
    Cprime: float
    RS: float
    M: float
    E: float
    F: float
    U: float
    extra: { … }
  score: float  # IntuitionScore
  feature_hash: sha256
  predicted_outcome: float
  label: { value: 0|1|null, observed_at: ISO-8601 }
  calibration_snapshot: { auc: float, ece: float, n: int }
  provenance:
    vif_witness_id: string
    context_snapshot_id: string
```

Storage: attach to CMC atom `ccs_metadata.intuition_trace` and include `intuition_score` + `intuition_features_hash` in VIF witness.

---

## 5) 4D Evolution Predictor (v0)

State vectors:
- S_ai(t): capability, calibration, load, focus
- S_user(t): satisfaction, engagement, trust
- S_collab(t): velocity, alignment, cohesion

v0 predictor: EWMA trend + simple Bayesian update; F = cosine(predictedΔ, observedΔ). Upgrade path: ESN/RNN-lite.

---

## 6) Integration Points

- CMC: extend CCSMetadata with IntuitionTrace
- VIF: add `intuition_score`, `intuition_features_hash` to witness
- HHNI: optional re-rank hook using I for tie-breaking; no semantic override
- TCS/EST: supply E via emotional salience/resonance + breakthrough detection
- CAS: audit AUC/ECE drift, failure modes, trigger recalibration
- SEG: record relations `intuitively_predicted`, `matched_prediction`, `missed_prediction`

---

## 7) APIs (internal)

- compute_intuition(features) -> score, trace
- update_intuition(decision_id, label) -> updated metrics
- get_intuition_metrics() -> { auc, ece, drift }

---

## 8) MVP Plan

- Day 1-2: schema + logging; attach IntuitionTrace
- Day 3-4: baseline I (C′, RS, E, basic M)
- Day 5-6: labels + online logistic + AUC/ECE
- Day 7-8: 4D predictor v0 → F added
- Day 9: HHNI re-rank hook (optional)
- Day 10: CAS dashboard + alerts

---

## 9) Validation

- Unit: monotonicity, serialization, hashing
- Backtest: AUC lift vs confidence-only baseline
- E2E: vague idea + high resonance elevates priority; κ respected
- Drift: synthetic shift triggers alert + re-calibration

---

## 10) Risks & Mitigations

- Overfitting: regularization, replay splits
- Feedback loops: cap weight on E and tie-break only in HHNI
- Misuse: κ precedence; human review for critical domains
- Latency: compute features asynchronously; cache traces
