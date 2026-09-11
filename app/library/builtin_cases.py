import os
import json
from typing import Dict, List, Any, Optional
from app.library.case_models import MysteryCase, Suspect, EvidenceItem, TimelineEvent, Witness, HiddenSolution

BACKEND_CASES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "backend", "src", "cases")
)


def load_all_builtin_cases() -> List[Dict[str, Any]]:
    """Loads all 12 built-in cases from backend/src/cases/ directory."""
    cases = []
    if not os.path.exists(BACKEND_CASES_DIR):
        return cases

    for entry in sorted(os.listdir(BACKEND_CASES_DIR)):
        case_file = os.path.join(BACKEND_CASES_DIR, entry, "case.json")
        if os.path.isfile(case_file):
            try:
                with open(case_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cases.append(data)
            except Exception as e:
                print(f"Error loading case from {case_file}: {e}")

    cases.sort(key=lambda c: c.get("caseId", ""))
    return cases


BUILTIN_CASES: List[Dict[str, Any]] = load_all_builtin_cases()


def get_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a specific built-in case by its Case ID."""
    for c in BUILTIN_CASES:
        if c.get("caseId", "").upper() == case_id.strip().upper():
            return c
    return None
