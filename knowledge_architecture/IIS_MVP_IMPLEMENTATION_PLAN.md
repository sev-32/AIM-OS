# IIS MVP Implementation Plan (10 Days)

Scope: Implement Intuitive Intelligence System minimal viable product safely under κ-gating.

## Day 1-2: Schema & Logging
- Add IntuitionTrace schema in docs + model stub
- Attach to CMC CCSMetadata; add fields to VIF witness (docs-first)
- Timeline writer for intuition decisions

## Day 3-4: Baseline IntuitionScore
- Compute C′ (VIF), RS (HHNI), E (EST), basic M via nearest successful pattern
- Linear/logistic score; store trace

## Day 5-6: Labels & Calibration
- Outcome labeling (parity, user acceptance)
- Online logistic regression update
- Report AUC/ECE; CAS monitors

## Day 7-8: 4D Predictor v0
- Trend-based predictor for AI/user/collab states
- Compute F and add to features

## Day 9: HHNI Hook (Optional)
- Tie-break re-rank using I (bounded effect)

## Day 10: CAS Dashboard + Alerts
- Drift thresholds; recalibration procedure

## Validation
- Unit: monotonicity, serialization
- Backtest: AUC↑ vs confidence-only
- E2E: resonance boost works; κ-gating respected
- Drift: alert + re-calibration
