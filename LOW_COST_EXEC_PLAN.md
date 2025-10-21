# LOW-COST EXECUTION PLAN
*AIM-OS v0.2 → v0.3 on a shoestring*
*Author: o3pro-ai Date: 2025-10-19*

---

## 0. TL;DR for Any Agent
1. **Read the "Must-Know" section (≈150 lines).**
2. **Pick ONE micro-task from the Task Board.**
3. **Work locally → run `pytest` → commit with audit script.**
4. **Update the Task Board status & hand-off.**

If you can't finish in < 60 min or 800 tokens → STOP and write a note.

---

## 1. Must-Know State (20 lines)
| Layer | Status | Key Files |
|-------|--------|-----------|
| CMC (atoms, snapshots) | **✅ v0.2 done** | `packages/cmc_service/*` |
| Safety / Observability | **✅** | same + `tests/` |
| HHNI (indexer, safety) | **🔄 scaffolding ready** | `packages/hhni/*` |
| CLI | **✅ base + hhni:query/stats** | `packages/cmc_service/cli.py` |
| Benchmarks | **✅ mock baseline** | `benchmarks/hhni_performance.py` |
| Docker stack | **🟡 needs run & schema apply** | `deploy/docker-compose.yml`, `docs/DOCKER_DEPLOYMENT.md` |
| APOE / VIF / SEG | **❌ not started** | (stubs only) |
| UI / Operator console | **❌ not started** | – |

---

## 2. Guiding Constraints
1. **Zero cloud costs** – use local Python + mock clients.
2. **Tests must pass (`pytest -q`) before commit.**
3. **Every commit runs `audit/scripts/post_run_audit.py`.**
4. **Write code in ≤400 tokens diff; longer ideas → `ideas/<role>/`.**
5. **Follow the naming convention:**
   `feat(hhni): sentence query API` or `docs(plan): SEG stub`.

---

## 3. Phase Targets
| Phase | Finish When | Cheap Proof |
|-------|-------------|-------------|
| 3-A  – Docker Up  | `docker compose ps` shows 3 containers, schema applied | `cmc hhni:stats` returns collections |
| 3-B  – HHNI L2 Query | `cmc hhni:query "hello"` returns ≥1 hit | e2e tests green |
| 3-C  – Prom-Dash | `localhost:9090` shows CMC metrics | screenshot in audit bundle |
| 3-D  – SEG-stub | `packages/seg/` with model + 1 unit test | test passes |
| 3-E  – APOE-stub | `plans/demo.acl` + executor runs mock pipeline | test passes |

---

## 4. Micro-Task Board
| ID | Task | Phase | Est-tokens | Skill |
|----|------|-------|------------|-------|
| T-01 | Apply `schemas/hhni.graphql` via script once Docker up | 3-A | 120 | Bash + Python |
| T-02 | Write `scripts/init_qdrant.py` to create two collections | 3-A | 100 | Python |
| T-03 | Replace mock clients in `hhni_performance.py` when `--docker-available` | 3-A | 60 | Python |
| T-04 | Add paragraph/sentence search e2e test hitting real Qdrant (skip if offline) | 3-B | 180 | Pytest |
| T-05 | Implement `/metrics` FastAPI endpoint exposing Prometheus registry | 3-C | 140 | Python |
| T-06 | Write Grafana-like JSON dashboard definition (static) | 3-C | 90 | JSON |
| T-07 | Scaffold `packages/seg/models.py` with Node/Edge dataclasses | 3-D | 120 | Python |
| T-08 | Implement in-memory SEG builder that links Atom→HHNI Node | 3-D | 200 | Python |
| T-09 | Create minimal ACL example & parser in `packages/apoe/acl.py` | 3-E | 200 | Python |
| T-10 | CLI `plan:run` command that reads `.acl`, prints step order | 3-E | 180 | Python |

*(Pick any open task, mark "⏳ in-progress", commit when "✅ done")*

---

## 5. Low-Token Dev Recipe
```
# 1. Activate env
cd AIM-OS
python -m venv .venv
.venv\Scripts\activate
pip install -e .[test]

# 2. Run tests
pytest -q

# 3. Do work (edit or new file <=400 tokens)

# 4. Run audit
python audit/scripts/post_run_audit.py --agent supernova --task T-05 --corr <your-id>

# 5. git add/commit
git commit -m "feat(metrics): add FastAPI /metrics endpoint (#T-05)"
```

---

## 6. Knowledge Shortcuts for Small Models
| Need | Shortcut |
|------|----------|
| Overview of system | `analysis/COMPLETE_SYSTEM_OVERVIEW.md` (≈700 tokens) |
| Current deliverables | `WEEK_1_PROGRESS_REVIEW.md` |
| Goals & metrics | `goals/GOAL_DASHBOARD.md` |
| How to hand-off | `AI_HANDOFF_CONTROL.md` (top 60 lines) |
| CMC API | `packages/cmc_service/memory_store.py` docstrings |
| HHNI API | `packages/hhni/indexer.py` docstrings |
| Deployment commands | `docs/DOCKER_DEPLOYMENT.md` Quick-start section |

*(If your context < 4k tokens, load only the files in the table.)*

---

## 7. Safety Checklist (each commit)
- ✅ `pytest` passes
- ✅ No network calls except `localhost`
- ✅ Audit script ran & bundle in `audit/history/`
- ✅ Updated Task Board status

---

## 8. Task Board Status (edit in place)
```
| ID  | Owner      | Status       | Notes |
|-----|------------|--------------|-------|
| T-01| (open)     | 🟢 todo      |       |
| T-02| (open)     | 🟢 todo      |       |
| T-03| (open)     | 🟢 todo      |       |
| T-04| (open)     | 🟡 blocked   | Needs Docker up |
| T-05| (open)     | 🟢 todo      |       |
| T-06| (open)     | 🟢 todo      |       |
| T-07| (open)     | 🟢 todo      |       |
| T-08| (open)     | 🟢 todo      |       |
| T-09| (open)     | 🟢 todo      |       |
| T-10| (open)     | 🟢 todo      |       |
```

*(Mark ⏳ in-progress, ✅ done, 🔴 fail, 🟡 blocked)*

---

## 9. Final Words
You don't need $2k/month models to finish this roadmap.
With Docker, local GPUs, open-source LLMs, and strict discipline you can:

1. Stand up the databases locally.
2. Prove HHNI in a real environment.
3. Expose metrics & dashboards.
4. Add minimal SEG + APOE stubs.
5. Demo a deterministic, queryable memory OS end-to-end.

Everything beyond that (Idea Foundry, full orchestration) can iterate once the lightweight stack is stable.

**Print this plan, close expensive sessions, and code with confidence.**
