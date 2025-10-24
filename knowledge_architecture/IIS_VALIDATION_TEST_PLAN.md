# IIS Validation Test Plan

## Unit Tests
- IntuitionScore monotonicity: ↑RS, ↑E ⇒ ↑I; ↑U ⇒ ↓I
- Serialization: IntuitionTrace round-trip with feature_hash stable
- κ precedence: low confidence under κ ⇒ abstain regardless of I

## Backtests
- Historical timelines: I AUC > confidence-only baseline by ≥5%
- ECE: post-calibration ECE ≤ 0.05 on validation split

## E2E Scenarios
- Vague idea + high resonance → elevated priority; κ respected
- Confident but low M/E → modest I; no override
- 4D mismatch (predicted≠observed) reduces F, I adapts over time

## Drift & Safety
- Synthetic drift reduces AUC ⇒ CAS alert fired, recalibration applied
- Cap effect of E to prevent hype loops; HHNI tie-break only

## Replay
- VIF witness + IntuitionTrace reproduces I and decision at time T
