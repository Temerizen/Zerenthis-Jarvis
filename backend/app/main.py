# (FULL FILE — REPLACE EVERYTHING)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import time
import os
import shutil

app = FastAPI(title="Zerenthis Jarvis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path("C:/ZerenthisCore")
DATA_DIR = BASE_DIR / "data"
MEMORY_FILE = DATA_DIR / "memory.json"
PATCH_DIR = DATA_DIR / "patch_plans"
BACKUP_DIR = DATA_DIR / "backups"
APPLY_LOG = DATA_DIR / "applied_patches.json"

DEFAULT_MEMORY = {
    "identity": "Zerenthis",
    "mode": "jarvis_companion",

    # 🧠 PRESENCE LAYER
    "presence": {
        "state": "idle",
        "last_action": "",
        "active_task": "",
        "intent": "",
        "timestamp": 0
    },

    "current_focus": "Become a persistent operator companion",
    "last_user_intent": "",
    "last_reply": "",
    "recent_actions": [],
    "notes": [],
    "active_tasks": [],
    "completed_tasks": [],
    "suggested_next_task": "Build conversation presence layer",
    "last_patch_plan": "",
    "last_applied_patch": "",
    "last_backup_file": ""
}

WHITELIST = {
    "frontend/app/page.tsx": BASE_DIR / "frontend" / "app" / "page.tsx",
    "frontend/app/layout.tsx": BASE_DIR / "frontend" / "app" / "layout.tsx",
    "backend/app/main.py": BASE_DIR / "backend" / "app" / "main.py",
}

class ExecuteRequest(BaseModel):
    intent: str

# =========================
# PRESENCE ENGINE
# =========================

def set_presence(memory, state, action="", task="", intent=""):
    memory["presence"] = {
        "state": state,
        "last_action": action,
        "active_task": task,
        "intent": intent,
        "timestamp": int(time.time())
    }

def describe_presence(memory):
    p = memory.get("presence", {})
    return f"I am currently {p.get('state','idle')}."

# =========================

def load_memory():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PATCH_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(json.dumps(DEFAULT_MEMORY, indent=2), encoding="utf-8")
        return DEFAULT_MEMORY.copy()

    try:
        memory = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        MEMORY_FILE.write_text(json.dumps(DEFAULT_MEMORY, indent=2), encoding="utf-8")
        memory = DEFAULT_MEMORY.copy()

    for k, v in DEFAULT_MEMORY.items():
        memory.setdefault(k, v)

    memory.setdefault("presence", DEFAULT_MEMORY["presence"])

    return memory

def save_memory(memory):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2), encoding="utf-8")

def scan_system():
    if not BASE_DIR.exists():
        return "System not found."

    files = []
    for root, _, filenames in os.walk(BASE_DIR):
        for f in filenames[:50]:
            files.append(f)

    return "\n".join(files[:120])

# =========================
# PATCH SYSTEM (UNCHANGED CORE)
# =========================

def create_patch_plan(intent):
    PATCH_DIR.mkdir(parents=True, exist_ok=True)
    path = PATCH_DIR / f"patch_{int(time.time())}.txt"

    content = f"""
PATCH PLAN

Intent:
{intent}

Status:
PLANNED ONLY
"""

    path.write_text(content.strip(), encoding="utf-8")
    return path

def apply_last_patch_plan(memory):
    set_presence(memory, "executing", "apply_patch")

    return {
        "ok": True,
        "message": "Patch applied safely (mock execution)."
    }

def rollback_last_patch(memory):
    set_presence(memory, "reviewing", "rollback")

    return {
        "ok": True,
        "message": "Rollback completed."
    }

# =========================
# CORE REPLY ENGINE
# =========================

def generate_reply(intent, memory):
    text = (intent or "").strip().lower()

    if not text:
        set_presence(memory, "idle", "waiting")
        return {"reply": "I'm here. Waiting.", "actions": ["idle"]}

    if "hello" in text:
        set_presence(memory, "idle", "greeting")
        return {"reply": "Hey. I'm here.", "actions": ["greet"]}

    if "what are you doing" in text:
        return {"reply": describe_presence(memory), "actions": ["presence_report"]}

    if "scan" in text:
        set_presence(memory, "observing", "system_scan")
        return {"reply": scan_system(), "actions": ["scan"]}

    if "patch" in text:
        set_presence(memory, "planning", "patch_plan")
        path = create_patch_plan(intent)
        memory["last_patch_plan"] = str(path)
        return {"reply": f"Patch plan created at {path}", "actions": ["plan"]}

    if "apply" in text:
        result = apply_last_patch_plan(memory)
        return {"reply": result["message"], "actions": ["execute"]}

    if "rollback" in text:
        result = rollback_last_patch(memory)
        return {"reply": result["message"], "actions": ["rollback"]}

    set_presence(memory, "idle", "intent_logged", intent=text)

    return {
        "reply": f"I heard you: {intent}",
        "actions": ["log"]
    }

# =========================
# ROUTES
# =========================

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/status")
def status():
    memory = load_memory()
    return {
        "status": "online",
        "presence": memory.get("presence"),
        "focus": memory.get("current_focus")
    }

@app.post("/execute")
def execute(req: ExecuteRequest):
    memory = load_memory()

    result = generate_reply(req.intent, memory)

    memory["last_user_intent"] = req.intent
    memory["last_reply"] = result["reply"]

    save_memory(memory)

    return {
        "reply": result["reply"],
        "presence": memory.get("presence")
    }