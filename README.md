# NEXUS — Autonomous Multi-Agent Enterprise Workflow System

> SLA Breach Prevention · Real-time Monitoring · Cost ROI Tracking

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND DASHBOARD                           │
│          HTML + CSS + JS  (index.html)                          │
│   Live Logs │ Agent Status │ Cost Savings │ Audit Trail         │
└─────────────────────┬───────────────────────────────────────────┘
                      │  SSE Stream + REST API
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    FASTAPI BACKEND                              │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                ORCHESTRATOR AGENT                        │  │
│   │       Controls pipeline, dispatches tickets              │  │
│   └─────┬──────────────────────────────────────────────┬────┘  │
│         │ assigns                                  ◄─── │        │
│   ┌─────▼──────┐  ┌──────────────┐  ┌────────────┐    │        │
│   │ MONITORING │→ │   DECISION   │→ │   ACTION   │    │        │
│   │   AGENT    │  │    AGENT     │  │   AGENT    │    │        │
│   │ Detects    │  │ Chooses fix  │  │ Executes   │    │        │
│   │ breaches   │  │ & strategy   │  │ + retries  │    │        │
│   └────────────┘  └──────────────┘  └─────┬──────┘    │        │
│                                            │           │        │
│   ┌────────────────────┐   ┌───────────────▼──────┐   │        │
│   │    AUDIT AGENT     │◄──│  COST ANALYZER AGENT │───┘        │
│   │  Logs all actions  │   │  Calculates ROI/savings            │
│   └────────────────────┘   └──────────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent Descriptions

| Agent | Role | Key Actions |
|-------|------|-------------|
| **Orchestrator** | Master controller | Dispatches tickets, manages pipeline flow |
| **Monitoring** | Issue detection | Scans SLA timers, detects breaches & risks |
| **Decision** | Remediation planner | Analyzes issue type, selects best fix |
| **Action** | Executor | Runs fix, retries up to 3× on failure |
| **Audit** | Compliance logger | Records every event for traceability |
| **Cost Analyzer** | ROI calculator | Calculates and displays cost savings |

---

## 💰 Cost Savings Formula

```
Savings per resolved ticket =
  SLA Breach Penalty Avoided  →  ₹5,000
+ Manual Labor Saved           →  ₹800 - ₹50 = ₹750
+ Downtime Prevention          →  ₹200/min × 15 min = ₹3,000
+ Escalation Avoided           →  ₹1,500 (if 0 retries)
                               ─────────────────────────
                                  Up to ₹10,250 per ticket
```

---

## 📁 Project Structure

```
multi-agent-system/
├── backend/
│   ├── main.py              # FastAPI app + all 6 agent classes
│   └── requirements.txt     # Python dependencies
└── frontend/
    └── index.html           # Single-file dashboard (HTML/CSS/JS)
```

---

## ⚡ Setup Instructions

### Prerequisites
- Python 3.9+
- Modern web browser

### Step 1 — Install Backend Dependencies

```bash
cd multi-agent-system/backend
pip install -r requirements.txt
```

### Step 2 — Start the Backend

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 3 — Open the Frontend

Simply open `frontend/index.html` in your browser:
```bash
# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html

# Windows
start frontend/index.html
```

Or serve it with Python:
```bash
cd frontend
python -m http.server 3000
# then visit http://localhost:3000
```

### Step 4 — Run the Workflow

1. Click **"Launch Dashboard"** on the welcome modal
2. Click **"▶ Run Workflow"** in the top right
3. Watch all 6 agents collaborate in real-time!

---

## 🧪 Sample Output

```
08:42:01  [SYSTEM]        🚀 Workflow #A3F7B2 started — SLA Monitoring for 5 enterprise services
08:42:01  [ORCHESTRATOR]  🎯 Orchestrator online. Starting SLA monitoring workflow.
08:42:02  [ORCHESTRATOR]  📋 Dispatching ticket TKT-001 (API_FAILURE) to monitoring pipeline
08:42:02  [MONITORING]    🔍 Scanning TKT-001 — Payment Gateway...
08:42:03  [MONITORING]    🚨 BREACH DETECTED on TKT-001! Elapsed: 18min / SLA: 15min
08:42:03  [DECISION]      🧠 Decision Agent analyzing TKT-001 (anomaly score: 0.87)...
08:42:04  [DECISION]      💡 Decision for TKT-001: → RESTART_SERVICE — Restart microservice pod
08:42:04  [ACTION]        ⚙️  Executing [restart_service] for TKT-001 (attempt 1/3)...
08:42:05  [ACTION]        🔄 Attempt 1 failed for TKT-001. Retrying in 1s...
08:42:06  [ACTION]        ✅ Action SUCCESS: restart_service applied after 2 attempt(s)
08:42:06  [AUDIT]         📝 Audit record committed: TKT-001 → RESOLVED | Retries: 1
08:42:07  [COST ANALYZER] 💰 Cost savings for TKT-001: ₹8,750 saved
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/start` | Start workflow |
| GET | `/api/state` | Get current state |
| GET | `/api/stream` | SSE live event stream |
| GET | `/api/costs` | Cost breakdown |
| GET | `/docs` | Swagger UI |

---

## 🎯 Use Case: SLA Monitoring

The system monitors 5 enterprise service tickets:
- **TKT-001** — Payment Gateway (P1, 15-min SLA)
- **TKT-002** — User Database (P2, 30-min SLA)
- **TKT-003** — Search Service (P2, 30-min SLA)
- **TKT-004** — Auth Service (P1, 15-min SLA)
- **TKT-005** — Message Queue (P3, 60-min SLA)

Each ticket goes through the full agent pipeline: Monitor → Decide → Act → Audit → Cost
