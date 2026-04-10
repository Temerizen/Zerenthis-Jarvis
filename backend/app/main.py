from fastapi import FastAPI
from backend.app.core.companion import Companion

app = FastAPI(title="Zerenthis Operator Core")
companion = Companion()

@app.get("/health")
def health():
    return companion.health()

@app.get("/status")
def status():
    return companion.status()

@app.get("/memory")
def memory():
    return companion.memory()

@app.get("/repo-map")
def repo_map():
    return companion.scan_repo()

@app.post("/execute")
def execute(payload: dict):
    return companion.handle(payload.get("intent", ""))

@app.post("/step")
def step():
    return companion.step()
