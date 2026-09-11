import json
import os
from pathlib import Path
from typing import List, Dict, Any

HISTORY_FILE = Path(__file__).resolve().parent.parent / "data" / "nexus_history.json"

def save_investigation_record(record: Dict[str, Any]) -> None:
    history = load_investigation_history()
    history.insert(0, record)
    os.makedirs(HISTORY_FILE.parent, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def load_investigation_history() -> List[Dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
