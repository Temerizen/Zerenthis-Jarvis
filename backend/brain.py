import os
from pathlib import Path

BASE_DIR = Path("C:/ZerenthisCore")

def scan_system():
    summary = []

    for root, dirs, files in os.walk(BASE_DIR):
        depth = root.replace(str(BASE_DIR), "").count("\\")
        if depth > 2:
            continue

        summary.append(f"\n📁 {root}")
        for f in files[:10]:
            summary.append(f"  - {f}")

    return "\n".join(summary)


def generate_reply(intent: str):
    intent_lower = intent.lower()

    if "scan" in intent_lower or "system" in intent_lower:
        data = scan_system()
        return f"I scanned your system. Here's what I can see:\n{data}"

    if "improve" in intent_lower or "upgrade" in intent_lower:
        return (
            "Right now, I lack real execution and reasoning.\n"
            "Next upgrades should be:\n"
            "1. File modification capability\n"
            "2. Task memory tracking\n"
            "3. Multi-step planning\n"
            "4. Autonomous loop execution\n"
        )

    return (
        f"I received your request: '{intent}'.\n"
        "I'm beginning to develop reasoning, but need more capabilities to act fully."
    )
