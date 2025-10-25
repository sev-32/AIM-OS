# Sprint 1: KPI & Dashboard Evolution

**Goal:** Enable KPI tracking and basic trend visualization (backend focus, functional UI)

**Philosophy:** Perfect backend first, polish UI later. Get it working, not beautiful.

---

## Sprint Scope

### Priority 1: KPI Backend (High Priority)
**Make intelligence measurable**

#### Task 1.1: Timestamped KPI Snapshots
**File:** `goals/KPI_METRICS.json`

**Current state:**
```json
{
  "MIGE_VisionFit_current": "pending-baseline",
  "MIGE_LineageCompleteness_current": "pending-baseline",
  ...
}
```

**New structure:**
```json
{
  "current": {
    "MIGE_VisionFit": 0.85,
    "MIGE_LineageCompleteness": 0.92,
    ...
  },
  "history": [
    {
      "timestamp": "2025-10-21T12:00:00Z",
      "MIGE_VisionFit": 0.85,
      "MIGE_LineageCompleteness": 0.92,
      ...
    },
    ...
  ]
}
```

**Implementation:**
- Extend JSON schema to include history array
- Preserve current values for backward compat
- Add timestamp on each snapshot

**Time:** 1 hour

#### Task 1.2: KPI Refresh Script
**File:** `scripts/kpi_refresh.py`

**Features:**
- Read current system state (CMC, BTSM, VIF metrics)
- Calculate KPIs automatically
- Append to history with timestamp
- Emit trend CSVs for visualization

**Example output:**
```csv
timestamp,MIGE_VisionFit,MIGE_LineageCompleteness,...
2025-10-21T12:00:00Z,0.85,0.92,...
2025-10-21T13:00:00Z,0.87,0.93,...
```

**Time:** 2 hours

#### Task 1.3: KPI History Endpoint
**File:** `packages/cmc_service/api.py`

**New endpoint:** `GET /kpi/history`

**Query params:**
- `start_time`: ISO timestamp (optional)
- `end_time`: ISO timestamp (optional)
- `metrics`: Comma-separated metric names (optional)

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2025-10-21T12:00:00Z",
      "metrics": {
        "MIGE_VisionFit": 0.85,
        "MIGE_LineageCompleteness": 0.92
      }
    },
    ...
  ]
}
```

**Time:** 1.5 hours

---

### Priority 2: Basic Dashboard Updates (Medium Priority)
**Make KPIs visible (functional, not polished)**

#### Task 2.1: KPI Trend Display
**File:** `ui/btsm-dashboard/app/page.tsx`

**Add simple chart:**
- Line chart showing KPI trends over time
- Use existing charting library (recharts or similar)
- Basic styling, no animations
- **Functional, not beautiful**

**Time:** 2 hours

#### Task 2.2: KPI Card Updates
**File:** `ui/btsm-dashboard/components/KPICards.tsx` (or similar)

**Update existing KPI cards:**
- Show current value
- Show trend indicator (↑ up, ↓ down, → flat)
- Click to expand history
- **Simple, functional**

**Time:** 1 hour

---

## Definition of Done (Sprint 1)

- [ ] KPI_METRICS.json supports timestamped history
- [ ] kpi_refresh.py calculates and appends KPIs automatically
- [ ] /kpi/history endpoint returns historical metrics
- [ ] Dashboard displays KPI trends (basic line chart)
- [ ] KPI cards show trend indicators
- [ ] Tests pass for new endpoints
- [ ] Documentation updated

**Sprint 1 will be COMPLETE when all checkboxes are ✅**

---

## Notes

**Backend focus:**
- Perfect the KPI calculation logic
- Ensure data integrity (bitemporal if needed)
- Clean API design
- High test coverage

**UI is functional:**
- Shows the data clearly
- Basic interactivity
- Not polished or beautiful
- **Good enough to validate backend**

**Polish later:**
- Advanced visualizations
- Animations and transitions
- Perfect UX flows
- Beautiful styling

---

## Next Sprint Preview: MIGE Pipeline Completion

**After Sprint 1, focus on:**
- Complete ACL templates (tensor_to_trunk, branch_to_specs)
- HVCA scaffolding (Three Minds)
- Pipeline automation (full seed → deploy flow)
- **Complete the idea evolution engine**

**Time estimate:** 8-12 hours after Sprint 1

---

**Sprint 1: Make intelligence measurable**
**Sprint 2: Complete idea evolution**
**Then: Polish UI and scale**

**12-24 months to perfect IDE** ⚡

