from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
APP = BACKEND / "app"
DATA = BACKEND / "data"
OUT = ROOT / "outputs"
GENERATED = APP / "generated"
STATE_FILE = DATA / "operator_state.json"

for p in [DATA, OUT, GENERATED]:
    p.mkdir(parents=True, exist_ok=True)

DEFAULT_STATE = {
    "identity": {
        "name": "Zerenthis",
        "role": "Austin's personal Jarvis",
        "mode": "operator_awake",
        "tone": "direct, useful, non-theatrical"
    },
    "agenda": {
        "current_focus": "Become a real operator instead of a script machine.",
        "active_tasks": [],
        "completed_tasks": []
    },
    "runtime": {
        "tick": 0,
        "last_action": "idle",
        "last_reason": "",
        "last_output": "",
        "started_at": 0
    },
    "memory": {
        "recent_events": [],
        "repo_snapshots": []
    }
}

class Companion:
    def __init__(self):
        self.state = self._load()
        if not self.state["runtime"]["started_at"]:
            self.state["runtime"]["started_at"] = int(time.time())
            self._save()

    def _load(self) -> Dict:
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(json.dumps(DEFAULT_STATE))

    def _refresh(self) -> None:
        self.state = self._load()

    def _save(self) -> None:
        STATE_FILE.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def _remember(self, text: str) -> None:
        self._refresh()
        events = self.state["memory"]["recent_events"]
        events.append(f"{int(time.time())}: {text}")
        self.state["memory"]["recent_events"] = events[-40:]
        self._save()

    def _write(self, path: Path, content: str) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")
        return str(path)

    def scan_repo(self) -> Dict:
        self._refresh()
        py_files = list(ROOT.rglob("*.py"))
        md_files = list(ROOT.rglob("*.md"))
        json_files = list(ROOT.rglob("*.json"))

        snapshot = {
            "root": str(ROOT),
            "python_files": len(py_files),
            "markdown_files": len(md_files),
            "json_files": len(json_files),
            "notable_python": [str(p.relative_to(ROOT)) for p in py_files[:25]],
            "generated_exists": GENERATED.exists(),
            "outputs_count": len(list(OUT.glob("*")))
        }

        snaps = self.state["memory"]["repo_snapshots"]
        snaps.append(snapshot)
        self.state["memory"]["repo_snapshots"] = snaps[-5:]
        self._save()
        return snapshot

    def _task(self) -> str:
        return self.state["agenda"]["active_tasks"][0] if self.state["agenda"]["active_tasks"] else ""

    def _has_recent_action(self, action_name: str) -> bool:
        return any(action_name in e for e in self.state["memory"]["recent_events"][-6:])

    def _choose_action(self) -> Dict:
        self._refresh()
        task = self._task()
        tick = self.state["runtime"]["tick"]

        if not self._has_recent_action("repo_map_refreshed"):
            return {"type": "repo_map_refreshed", "reason": "A real operator should inspect the current repo before making moves."}

        if task and "jarvis" in task.lower() and not (APP / "generated" / "presence_protocol.py").exists():
            return {"type": "build_presence_protocol", "reason": "Jarvis requires a stronger presence protocol in the repo itself."}

        if task and "jarvis" in task.lower() and not (OUT / "jarvis_task_breakdown.md").exists():
            return {"type": "task_breakdown", "reason": "The active Jarvis task needs a concrete breakdown, not vague ambition."}

        if not (APP / "generated" / "operator_tools.py").exists():
            return {"type": "build_operator_tools", "reason": "An operator needs local tools, not just thoughts."}

        if not (OUT / "operator_brief.md").exists():
            return {"type": "operator_brief", "reason": "Zerenthis should maintain an explicit operator brief."}

        if task and not (APP / "generated" / "jarvis_presence.py").exists():
            return {"type": "build_jarvis_presence", "reason": "The companion still feels flat. Build a stronger in-repo presence module."}

        if tick % 4 == 0:
            return {"type": "status_report", "reason": "Presence requires live status, not silence."}

        return {"type": "system_note", "reason": "Continue strengthening the operating core with grounded notes."}

    def _act(self, action: Dict) -> str:
        self._refresh()
        a = action["type"]
        ts = int(time.time())

        if a == "repo_map_refreshed":
            repo = self.scan_repo()
            return self._write(DATA / "repo_map.json", json.dumps(repo, indent=2))

        if a == "build_presence_protocol":
            content = '''
from __future__ import annotations

PRESENCE_PROTOCOL = {
    "principles": [
        "be direct",
        "avoid fake progress",
        "choose strongest next move",
        "report status in plain language",
        "prioritize Austin's active direction"
    ],
    "voice": {
        "style": "operator",
        "tone": "calm, strategic, grounded"
    }
}

def summarize_focus(task: str) -> str:
    if not task:
        return "No active task. Defaulting to operator maintenance."
    return f"Primary focus: {task}"
'''.strip()
            return self._write(APP / "generated" / "presence_protocol.py", content)

        if a == "task_breakdown":
            task = self._task() or "No active task"
            content = f"""
# Zerenthis Jarvis Task Breakdown

## Active task
{task}

## Interpretation
Austin does not want another script machine. He wants a real operator presence.

## Strongest fronts
- operator behavior instead of artifact spam
- stronger repo awareness
- stronger local tools
- stronger live state visibility
- later: safe code modification and validation

## Immediate next move
Build local operator tools in-repo and keep status grounded.
"""
            return self._write(OUT / "jarvis_task_breakdown.md", content)

        if a == "build_operator_tools":
            content = '''
from __future__ import annotations
from pathlib import Path

def repo_summary(root: str) -> dict:
    p = Path(root)
    return {
        "python_files": len(list(p.rglob("*.py"))),
        "markdown_files": len(list(p.rglob("*.md"))),
        "json_files": len(list(p.rglob("*.json")))
    }

def strongest_next_move(task: str) -> str:
    if not task:
        return "maintain operator core"
    lowered = task.lower()
    if "jarvis" in lowered or "presence" in lowered:
        return "strengthen presence and operator behavior"
    if "money" in lowered:
        return "build monetization subsystem"
    return "create concrete subsystem tied to active task"
'''.strip()
            return self._write(APP / "generated" / "operator_tools.py", content)

        if a == "operator_brief":
            content = f"""
# Zerenthis Operator Brief

Zerenthis is operating as Austin's local operator core.

## Current focus
{self.state["agenda"]["current_focus"]}

## Active task
{self._task() or "none"}

## Operating rule
Do fewer, stronger, more grounded things.
Avoid low-substance output spam.
"""
            return self._write(OUT / "operator_brief.md", content)

        if a == "build_jarvis_presence":
            content = '''
from __future__ import annotations

JARVIS_PRESENCE = {
    "presence_model": "ongoing operator awareness",
    "status_style": "what happened, what changed, what matters next",
    "anti_pattern": "do not pretend markdown output equals progress"
}

def live_status(last_action: str, last_reason: str, active_task: str) -> str:
    return (
        f"Zerenthis active. "
        f"Last meaningful action: {last_action}. "
        f"Reason: {last_reason}. "
        f"Nearest priority: {active_task or 'operator maintenance'}."
    )
'''.strip()
            return self._write(APP / "generated" / "jarvis_presence.py", content)

        if a == "status_report":
            content = f"""
Zerenthis live status:
- tick: {self.state["runtime"]["tick"]}
- focus: {self.state["agenda"]["current_focus"]}
- active_task: {self._task() or "none"}
- last_action: {self.state["runtime"]["last_action"]}
- last_reason: {self.state["runtime"]["last_reason"]}
- last_output: {self.state["runtime"]["last_output"]}
"""
            return self._write(OUT / f"status_{ts}.md", content)

        content = f"""
# Zerenthis System Note

Current focus:
{self.state["agenda"]["current_focus"]}

Observation:
A stronger Jarvis requires operator behavior, repo awareness, live state, and meaningful local tools.
"""
        return self._write(OUT / f"system_note_{ts}.md", content)

    def step(self) -> Dict:
        self._refresh()
        self.state["runtime"]["tick"] += 1
        action = self._choose_action()
        output = self._act(action)

        self._refresh()
        self.state["runtime"]["last_action"] = action["type"]
        self.state["runtime"]["last_reason"] = action["reason"]
        self.state["runtime"]["last_output"] = output

        if self._task():
            self.state["agenda"]["current_focus"] = f"Advance active task: {self._task()}"
        else:
            self.state["agenda"]["current_focus"] = "Strengthen operator behavior and repo-level usefulness."

        if action["type"] == "build_jarvis_presence" and self._task():
            task = self._task()
            self.state["agenda"]["completed_tasks"].append(task)
            self.state["agenda"]["active_tasks"] = []

        self._remember(f"{action['type']} | {action['reason']} | {output}")
        self._save()

        return {
            "status": "ok",
            "decision": action,
            "output": output,
            "tick": self.state["runtime"]["tick"]
        }

    def loop(self) -> None:
        while True:
            result = self.step()
            print(f"[Zerenthis] {result['decision']['type']} | {result['decision']['reason']}")
            time.sleep(10)

    def handle(self, intent: str) -> Dict:
        self._refresh()
        intent = (intent or "").strip()
        if intent:
            self.state["agenda"]["active_tasks"] = [intent]
            self.state["agenda"]["current_focus"] = f"Advance active task: {intent}"
            self.state["agenda"]["completed_tasks"] = []
            self._remember(f"new_task | {intent}")
            self._save()
        return {
            "status": "accepted",
            "intent": intent,
            "active_tasks": self.state["agenda"]["active_tasks"]
        }

    def health(self) -> Dict:
        self._refresh()
        return {
            "status": "ok",
            "entity": self.state["identity"]["name"],
            "mode": self.state["identity"]["mode"],
            "last_action": self.state["runtime"]["last_action"],
            "last_output": self.state["runtime"]["last_output"]
        }

    def status(self) -> Dict:
        self._refresh()
        return {
            "identity": self.state["identity"],
            "agenda": self.state["agenda"],
            "runtime": self.state["runtime"],
            "recent_events": self.state["memory"]["recent_events"][-10:]
        }

    def memory(self) -> Dict:
        self._refresh()
        return self.state["memory"]
