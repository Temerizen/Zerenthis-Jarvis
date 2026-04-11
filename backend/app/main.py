from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import time

app = FastAPI(title="Zerenthis Jarvis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")
MEMORY_FILE = DATA_DIR / "memory.json"

DEFAULT_MEMORY = {
    "identity": "Zerenthis",
    "mode": "jarvis_companion",
    "current_focus": "Become a persistent operator companion",
    "last_user_intent": "",
    "last_reply": "",
    "recent_actions": [],
    "notes": []
}

def load_memory():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(json.dumps(DEFAULT_MEMORY, indent=2), encoding="utf-8")
        return DEFAULT_MEMORY.copy()
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        MEMORY_FILE.write_text(json.dumps(DEFAULT_MEMORY, indent=2), encoding="utf-8")
        return DEFAULT_MEMORY.copy()

def save_memory(memory):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(memory, indent=2), encoding="utf-8")

class ExecuteRequest(BaseModel):
    intent: str

@app.get("/")
def root():
    return {"status": "ok", "service": "zerenthis-jarvis", "version": "clean-rebuild"}

@app.get("/status")
def status():
    memory = load_memory()
    return {
        "status": "online",
        "identity": memory.get("identity", "Zerenthis"),
        "mode": memory.get("mode", "jarvis_companion"),
        "current_focus": memory.get("current_focus", ""),
        "last_user_intent": memory.get("last_user_intent", ""),
        "last_reply": memory.get("last_reply", ""),
        "recent_actions": memory.get("recent_actions", [])[-5:],
        "notes": memory.get("notes", [])[-5:]
    }

@app.post("/execute")
def execute(req: ExecuteRequest):
    memory = load_memory()
    intent = (req.intent or "").strip()
    lowered = intent.lower()

    actions = []
    if not intent:
        reply = "I am here. Give me a real objective and I will turn it into the next concrete move."
        actions.append("idle_waiting")
    elif "status" in lowered:
        reply = f"I am online. My current focus is: {memory.get('current_focus', 'unknown')}."
        actions.append("status_report")
    elif "repo" in lowered or "code" in lowered:
        reply = "I can inspect repo state, summarize the current focus, and prepare the next safe engineering move."
        actions.append("repo_operator_brief")
    elif "memory" in lowered or "remember" in lowered:
        memory["notes"].append(intent)
        reply = "Stored. I will carry this forward as active context."
        actions.append("memory_note_saved")
    else:
        reply = f"I understand your objective: {intent}. My next move is to keep this as active focus and stay ready to operate."
        actions.append("intent_registered")

    memory["last_user_intent"] = intent
    memory["last_reply"] = reply
    memory["recent_actions"].append({
        "ts": int(time.time()),
        "intent": intent,
        "actions": actions
    })
    if intent:
        memory["current_focus"] = intent

    save_memory(memory)

    return {
        "status": "ok",
        "reply": reply,
        "actions": actions,
        "memory_focus": memory["current_focus"]
    }
