# CCS L2 Addendum: Intuitive Intelligence System (IIS) Integration

Purpose: Document integration of IIS (9th enhancement) into CCS.

- New Component: IIS computes IntuitionScore per candidate action/idea
- Safety: κ-gating remains primary guard; IIS cannot bypass abstention
- Data Flow:
  - TCS/EST → E (emotional salience)
  - HHNI → RS (retrieval strength)
  - VIF → C′ (calibrated confidence), κ thresholds
  - CAS/timeline → M (meta-pattern similarity), labels
  - 4D predictor → F (evolution alignment)
  - IIS → IntuitionTrace (stored in CMC; reference in VIF)
- Optional: HHNI re-rank by I for ties; APOE can use I in role planning
- CAS expands audits: AUC/ECE for intuition, drift alerts, recalibration hooks
