import os
import json
from datetime import datetime
from config.configs import STATE_FILE

def load_ingestion_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_ingestion_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def is_already_ingested(filename, checksum, state):
    return filename in state and state[filename]["checksum"] == checksum

def update_ingestion_record(filename, checksum, session_id, state):
    state[filename] = {
        "checksum": checksum,
        "processed_at": datetime.now().isoformat(),
        "session_id": session_id
    }
