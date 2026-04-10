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
