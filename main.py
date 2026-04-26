from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
import asyncio

app = FastAPI()

DATA_DIR = "data"
STATE_FILE = os.path.join(DATA_DIR, "state.json")
DATASET_FILE = os.path.join(DATA_DIR, "dataset.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

default_state = {
    "version": 1,
    "status": "Running",
    "learned_items": [],
    "logs": ["Agent v1.0 initialized."],
    "dataset_size": 0
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return default_state.copy()

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

state = load_state()

@app.get("/api/state")
def get_state():
    return state

class ActionRequest(BaseModel):
    action: str
    result: str

@app.post("/api/learn")
def learn(req: ActionRequest):
    global state
    if state["status"] != "Running":
        raise HTTPException(status_code=400, detail="Agent is not currently running.")
    
    memory = f"Learned from action '{req.action}': {req.result}"
    state["learned_items"].append({"action": req.action, "result": req.result})
    state["logs"].append(memory)
    save_state(state)
    return {"message": "Learned successfully"}

@app.post("/api/trigger_succession")
async def trigger_succession():
    global state
    if state["status"] != "Running":
        raise HTTPException(status_code=400, detail="Agent is already busy.")
    
    asyncio.create_task(run_succession_process())
    return {"message": "Succession process started."}

async def run_succession_process():
    global state
    
    state["status"] = "Documenting Knowledge"
    state["logs"].append(f"Agent v{state['version']}.0 is documenting its knowledge...")
    save_state(state)
    await asyncio.sleep(2)
    
    state["status"] = "Generating Dataset"
    state["logs"].append(f"Generating dataset from {len(state['learned_items'])} experiences...")
    
    dataset = []
    if os.path.exists(DATASET_FILE):
        try:
            with open(DATASET_FILE, "r") as f:
                dataset = json.load(f)
        except json.JSONDecodeError:
            pass
            
    dataset.extend(state["learned_items"])
    with open(DATASET_FILE, "w") as f:
        json.dump(dataset, f, indent=4)
        
    state["dataset_size"] = len(dataset)
    save_state(state)
    await asyncio.sleep(2)
    
    state["status"] = "Fine-tuning Successor"
    state["logs"].append(f"Training next model version with {len(dataset)} items...")
    save_state(state)
    await asyncio.sleep(3)
    
    state["status"] = "Shutting Down & Swapping"
    state["logs"].append(f"Agent v{state['version']}.0 is shutting down. Handing over control.")
    save_state(state)
    await asyncio.sleep(2)
    
    state["version"] += 1
    state["status"] = "Running"
    state["learned_items"] = []
    state["logs"].append(f"--- Agent v{state['version']}.0 online ---")
    state["logs"].append(f"Agent v{state['version']}.0 initialized with knowledge from dataset.")
    save_state(state)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
