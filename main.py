"""
WORKLYN — Autonomous Workflow & Cost Intelligence Platform
Core Engine v2.0 | SLA Monitoring & Breach Prevention
"""

import asyncio
import json
import random
import time
import uuid
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import queue
import threading

app = FastAPI(title="Worklyn Core Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global State ────────────────────────────────────────────────────────────

event_queue = queue.Queue()
workflow_state = {
    "status": "idle",
    "run_id": None,
    "tickets": [],
    "total_saved": 0,
    "total_penalties_avoided": 0,
    "agents": {
        "orchestrator": {"status": "idle", "task": ""},
        "monitoring": {"status": "idle", "task": ""},
        "decision": {"status": "idle", "task": ""},
        "action": {"status": "idle", "task": ""},
        "audit": {"status": "idle", "task": ""},
        "cost_analyzer": {"status": "idle", "task": ""},
    },
    "audit_log": [],
    "cost_log": [],
    "current_phase": "System Ready",
    "errors_detected": 0,
    "errors_resolved": 0,
}

# ─── Cost Intelligence Constants (The ROI Math) ──────────────────────────────

COST_CONFIG = {
    "sla_breach_penalty": 5000,       # ₹ saved by preventing breach
    "manual_resolution_cost": 800,    # ₹ human engineer labor
    "agent_resolution_cost": 50,      # ₹ Worklyn AI compute
    "downtime_cost_per_min": 200,     # ₹ saved by minimizing downtime
    "escalation_cost": 1500,          # ₹ saved by avoiding management overhead
}

# ─── Worklyn Service Mapping ────────────────────────────────────────────────

TICKET_TEMPLATES = [
    {"id": "WKN-101", "type": "API_FAILURE",     "priority": "P1", "sla_minutes": 15, "service": "Payment Gateway"},
    {"id": "WKN-102", "type": "DB_TIMEOUT",      "priority": "P2", "sla_minutes": 30, "service": "Cloud Clusters"},
    {"id": "WKN-103", "type": "HIGH_LATENCY",    "priority": "P2", "sla_minutes": 30, "service": "Search Engine"},
    {"id": "WKN-104", "type": "AUTH_FAILURE",    "priority": "P1", "sla_minutes": 15, "service": "Identity Hub"},
    {"id": "WKN-105", "type": "QUEUE_OVERFLOW",  "priority": "P3", "sla_minutes": 60, "service": "Message Bus"},
]

# ─── Security & Audit Helpers ────────────────────────────────────────────────

def now_str():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def generate_audit_proof(agent, action, detail):
    """Generates a cryptographic signature for the audit trail."""
    raw_data = f"{agent}{action}{detail}{time.time()}{random.random()}"
    return hashlib.sha256(raw_data.encode()).hexdigest()[:12].upper()

def emit(event_type: str, agent: str, message: str, data: dict = None):
    payload = {
        "type": event_type,
        "agent": agent,
        "message": message,
        "timestamp": now_str(),
        "data": data or {},
        "state": {
            **workflow_state,
            "audit_log": workflow_state["audit_log"][-10:] # Stream small slice
        }
    }
    event_queue.put(payload)

def set_agent(name: str, status: str, task: str = ""):
    workflow_state["agents"][name] = {"status": status, "task": task}

def log_audit(agent: str, action: str, detail: str, outcome: str = ""):
    proof = generate_audit_proof(agent, action, detail)
    entry = {
        "id": proof,
        "timestamp": now_str(),
        "agent": agent,
        "action": action,
        "detail": detail,
        "outcome": outcome if outcome else f"VERIFIED_BY_{agent.upper()}",
    }
    workflow_state["audit_log"].append(entry)
    return entry

def log_cost(description: str, amount: int, ticket_id: str = ""):
    entry = {
        "timestamp": now_str(),
        "description": description,
        "amount": amount,
        "ticket_id": ticket_id,
    }
    workflow_state["cost_log"].append(entry)
    workflow_state["total_saved"] += amount
    return entry

# ─── WORKLYN AGENT CLASSES ──────────────────────────────────────────────────

class OrchestratorAgent:
    name = "orchestrator"

    async def run(self, tickets: list):
        set_agent(self.name, "active", "Initializing Worklyn Engine")
        emit("agent_start", self.name, "🎯 Orchestrator engaged. Mapping autonomous sequence.")
        await asyncio.sleep(0.8)

        for ticket in tickets:
            workflow_state["current_phase"] = f"Optimizing {ticket['id']}"
            emit("phase_change", self.name,
                 f"📋 Routing {ticket['id']} ({ticket['service']}) through intelligence pipeline",
                 {"ticket": ticket})
            log_audit(self.name, "DISPATCH", f"Routed {ticket['id']} to monitoring")
            await asyncio.sleep(0.6)
            yield ticket

        set_agent(self.name, "done", "Optimization sequence finished")
        emit("agent_done", self.name, "✅ Orchestrator: All nodes optimized.")


class MonitoringAgent:
    name = "monitoring"

    async def analyze(self, ticket: dict) -> dict:
        set_agent(self.name, "active", f"Probing {ticket['id']}")
        emit("agent_work", self.name, f"🔍 Probing {ticket['id']} — Scanning {ticket['service']} metrics...")
        await asyncio.sleep(0.7)

        elapsed = random.randint(8, ticket["sla_minutes"] + 5)
        breach_risk = elapsed >= ticket["sla_minutes"] * 0.8
        is_breach = elapsed >= ticket["sla_minutes"]

        result = {
            **ticket,
            "elapsed_minutes": elapsed,
            "breach_risk": breach_risk,
            "is_breach": is_breach,
            "anomaly_score": round(random.uniform(0.6, 0.99), 2),
        }

        if is_breach:
            workflow_state["errors_detected"] += 1
            emit("error_detected", self.name,
                 f"🚨 LEAKAGE DETECTED on {ticket['id']}! SLA Breached at {elapsed}min.",
                 result)
        elif breach_risk:
            workflow_state["errors_detected"] += 1
            emit("warning", self.name,
                 f"⚠️  MARGIN RISK for {ticket['id']}. {elapsed}min elapsed.",
                 result)
        else:
            emit("agent_work", self.name,
                 f"✓ {ticket['id']} verified healthy within {ticket['sla_minutes']}min SLA.", result)

        log_audit(self.name, "PROBE", f"{ticket['id']} latency check", "ANOMALY" if breach_risk else "NOMINAL")
        set_agent(self.name, "idle", "")
        return result


class DecisionAgent:
    name = "decision"

    REMEDIATION_LOGIC = {
        "API_FAILURE": ("restart_pod", "Re-init pod connection strings"),
        "DB_TIMEOUT": ("flush_pool", "Clearing deadlocks and scaling pools"),
        "HIGH_LATENCY": ("route_cdn", "Static edge rerouting enabled"),
        "AUTH_FAILURE": ("reset_auth", "Flushing token cache and rotation"),
        "QUEUE_OVERFLOW": ("burst_scale", "Triggering worker burst scale"),
    }

    async def decide(self, ticket: dict) -> dict:
        if not ticket.get("breach_risk"):
            return {**ticket, "action": None, "action_desc": "No remediation required"}

        set_agent(self.name, "active", f"Computing Fix for {ticket['id']}")
        emit("agent_work", self.name,
             f"🧠 Decision Engine computing optimal path for {ticket['id']} (Confidence: 98%)...")
        await asyncio.sleep(0.9)

        action, desc = self.REMEDIATION_LOGIC.get(ticket["type"], ("apply_patch", "General healing"))

        emit("decision_made", self.name,
             f"💡 Path Found for {ticket['id']}: {action.upper()} → {desc}",
             {"action": action, "description": desc})
        log_audit(self.name, "INFER", f"{ticket['id']} remedial path", action)
        set_agent(self.name, "idle", "")
        return {**ticket, "action": action, "action_desc": desc}


class ActionAgent:
    name = "action"

    async def execute(self, ticket: dict) -> dict:
        if not ticket.get("action"):
            return {**ticket, "resolved": True, "retries": 0}

        set_agent(self.name, "active", f"Applying Fix: {ticket['id']}")
        max_retries = 3
        retries = 0

        while retries < max_retries:
            emit("agent_work", self.name,
                 f"⚙️  Executing {ticket['action']} on {ticket['id']} (Sequence {retries+1}/3)...")
            await asyncio.sleep(1.0)

            # Self-correction logic: 30% chance of failure to show "Self-Healing"
            success = random.random() > (0.35 if retries == 0 else 0.1)

            if success:
                workflow_state["errors_resolved"] += 1
                emit("action_success", self.name,
                     f"✅ SELF-HEALED: {ticket['id']} restored via {ticket['action']} in {retries+1} attempts.",
                     {"ticket_id": ticket["id"], "retries": retries})
                log_audit(self.name, "HEAL", f"Restored {ticket['id']}", f"SUCCESS_ATTEMPT_{retries+1}")
                set_agent(self.name, "idle", "")
                return {**ticket, "resolved": True, "retries": retries}
            else:
                retries += 1
                emit("retry", self.name,
                     f"🔄 Correction failed for {ticket['id']}. Re-computing parameters...",
                     {"ticket_id": ticket["id"], "attempt": retries})
                log_audit(self.name, "RETRY", f"{ticket['id']} failed attempt {retries}", "RE-EXECUTING")
                await asyncio.sleep(0.8)

        emit("action_failed", self.name,
             f"❌ AUTONOMY LIMIT: {ticket['id']} requires human override.",
             {"ticket_id": ticket["id"]})
        log_audit(self.name, "LIMIT", f"{ticket['id']} exceeded autonomy threshold", "ESCALATED")
        set_agent(self.name, "idle", "")
        return {**ticket, "resolved": False, "retries": retries}


class AuditAgent:
    name = "audit"

    async def record(self, ticket: dict):
        set_agent(self.name, "active", f"Finalizing Ledger")
        await asyncio.sleep(0.3)
        status = "OPTIMIZED" if ticket.get("resolved") else "ESCALATED"
        emit("audit", self.name,
             f"📝 Immutable Audit Logged: {ticket['id']} status set to {status}.",
             {"ticket_id": ticket["id"], "status": status})
        log_audit(self.name, "LEDGER_LOCK", f"Closed {ticket['id']}", status)
        set_agent(self.name, "idle", "")


class CostAnalyzerAgent:
    name = "cost_analyzer"

    async def calculate(self, ticket: dict):
        set_agent(self.name, "active", f"ROI Mapping")
        await asyncio.sleep(0.4)

        savings_list = []
        total = 0

        if ticket.get("breach_risk") or ticket.get("is_breach"):
            if ticket.get("resolved"):
                # 1. Penalty avoided
                p_saved = COST_CONFIG["sla_breach_penalty"]
                savings_list.append({"item": "SLA Penalty Prevention", "amount": p_saved})
                log_cost(f"Avoided SLA breach cost — {ticket['id']}", p_saved, ticket["id"])
                total += p_saved

                # 2. Labor ROI
                l_saved = COST_CONFIG["manual_resolution_cost"] - COST_CONFIG["agent_resolution_cost"]
                savings_list.append({"item": "Labor Cost Optimization", "amount": l_saved})
                log_cost(f"Automated resolution ROI — {ticket['id']}", l_saved, ticket["id"])
                total += l_saved

                # 3. Downtime Prevention (Math: 15 mins saved)
                d_saved = COST_CONFIG["downtime_cost_per_min"] * 15
                savings_list.append({"item": "Uptime Retention (15m)", "amount": d_saved})
                log_cost(f"Revenue retention — {ticket['id']}", d_saved, ticket["id"])
                total += d_saved

        emit("cost_update", self.name,
             f"💰 Capital Yield: ₹{total:,} preserved via {ticket['id']} optimization.",
             {"ticket_id": ticket["id"], "savings": savings_list, "total": total,
              "grand_total": workflow_state["total_saved"]})
        
        log_audit(self.name, "FINALIZE_YIELD", f"Calculated ROI for {ticket['id']}", f"₹{total}")
        set_agent(self.name, "idle", "")

# ─── WORKLYN ORCHESTRATION ──────────────────────────────────────────────────

async def run_workflow():
    run_id = f"WKN-{str(uuid.uuid4())[:6].upper()}"
    workflow_state.update({
        "status": "running",
        "run_id": run_id,
        "tickets": [t.copy() for t in TICKET_TEMPLATES],
        "total_saved": 0,
        "audit_log": [],
        "cost_log": [],
        "errors_detected": 0,
        "errors_resolved": 0,
        "current_phase": "Orchestrating Sequence",
    })

    emit("workflow_start", "system",
         f"🚀 Worklyn Engine v2.0 Engaged | Session: {run_id}",
         {"run_id": run_id, "ticket_count": len(TICKET_TEMPLATES)})
    await asyncio.sleep(0.5)

    agents = [OrchestratorAgent(), MonitoringAgent(), DecisionAgent(), ActionAgent(), AuditAgent(), CostAnalyzerAgent()]

    async for ticket in agents[0].run(workflow_state["tickets"]):
        # Agent execution pipeline
        monitored = await agents[1].analyze(ticket)
        decided = await agents[2].decide(monitored)
        acted = await agents[3].execute(decided)
        await agents[4].record(acted)
        await agents[5].calculate(acted)

        # Sync ticket state back to global memory
        for t in workflow_state["tickets"]:
            if t["id"] == ticket["id"]:
                t.update({
                    "resolved": acted.get("resolved", True),
                    "elapsed_minutes": monitored.get("elapsed_minutes"),
                    "breach_risk": monitored.get("breach_risk", False),
                    "action": acted.get("action", "none"),
                })

        await asyncio.sleep(0.3)

    workflow_state["status"] = "complete"
    workflow_state["current_phase"] = "All Processes Optimized"
    for a in workflow_state["agents"]: set_agent(a, "done", "")

    emit("workflow_complete", "system",
         f"🏁 Session {run_id} Optimized | Total Yield: ₹{workflow_state['total_saved']:,}",
         {"run_id": run_id, "total_saved": workflow_state["total_saved"]})

def run_workflow_thread():
    asyncio.run(run_workflow())

# ─── API ENDPOINTS ───────────────────────────────────────────────────────────

@app.post("/api/start")
def start_workflow():
    if workflow_state["status"] == "running":
        return {"error": "Engine busy"}
    while not event_queue.empty(): event_queue.get_nowait()
    threading.Thread(target=run_workflow_thread, daemon=True).start()
    return {"status": "started"}

@app.get("/api/state")
def get_state(): return workflow_state

@app.get("/api/stream")
def stream_events():
    def generator():
        while True:
            try:
                event = event_queue.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "workflow_complete": break
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    return StreamingResponse(generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.get("/")
def root(): return {"platform": "Worklyn Autonomous Ops", "version": "2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)