from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import time
import os

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
PATCH_DIR = DATA_DIR / "patch_plans"
MEMORY_FILE = DATA_DIR / "memory.json"

DEFAULT_MEMORY = {
    "identity": "Zerenthis",
    "mode": "jarvis_companion",
    "current_focus": "",
    "last_user_intent": "",
    "last_reply": "",
    "recent_actions": [],
    "active_tasks": [],
    "completed_tasks": [],
    "last_patch_plan": ""
}

class ExecuteRequest(BaseModel):
    intent: str

def load_memory():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PATCH_DIR.mkdir(parents=True, exist_ok=True)

    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(json.dumps(DEFAULT_MEMORY, indent=2))
        return DEFAULT_MEMORY.copy()

    return json.loads(MEMORY_FILE.read_text())

def save_memory(memory):
    MEMORY_FILE.write_text(json.dumps(memory, indent=2))

def scan_system():
    results = []
    for root, dirs, files in os.walk(BASE_DIR):
        results.append(f"[DIR] {root}")
        for f in files[:5]:
            results.append(f"  - {f}")
    return "\n".join(results[:80])

def create_patch_plan(intent: str):
    PATCH_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    path = PATCH_DIR / f"patch_{timestamp}.txt"

    content = f"""
PATCH PLAN

Intent:
{intent}

Strategy:
- Identify target file
- Make minimal safe change
- Keep system stable
- No auto-apply

Status:
PLANNED ONLY
"""

    path.write_text(content.strip())
    return path

def generate_reply(intent: str, memory: dict):
    text = intent.lower()

    if "scan" in text:
        return {
            "reply": "System scan complete:\n\n" + scan_system(),
            "actions": ["scan"]
        }

    if "patch" in text or "plan" in text:
        path = create_patch_plan(intent)
        memory["last_patch_plan"] = str(path)

        return {
            "reply": f"I created a patch plan.\n\nSaved at:\n{path}",
            "actions": ["patch_plan"]
        }

    if "task" in text and "add" in text:
        task = intent.replace("add task", "").strip()
        memory["active_tasks"].append(task)
        return {
            "reply": f"Task added: {task}",
            "actions": ["task_added"]
        }

    if "show tasks" in text:
        return {
            "reply": f"Active: {memory['active_tasks']}\nCompleted: {memory['completed_tasks']}",
            "actions": ["task_view"]
        }

    return {
        "reply": f"I understand: {intent}\nI am ready to evolve further.",
        "actions": ["intent_logged"]
    }

@app.get("/status")
def status():
    memory = load_memory()
    return memory

@app.post("/execute")
def execute(req: ExecuteRequest):
    memory = load_memory()

    result = generate_reply(req.intent, memory)

    memory["last_user_intent"] = req.intent
    memory["last_reply"] = result["reply"]

    memory["recent_actions"].append({
        "intent": req.intent,
        "actions": result["actions"]
    })

    save_memory(memory)

    return {
        "reply": result["reply"],
        "actions": result["actions"],
        "memory": memory
    }