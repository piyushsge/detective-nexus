import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from detective_nexus.models.case import MysteryCase

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class CaseEngine:
    """
    Manages loading, validation, and in-memory representation of case dossiers.
    Ensures strict separation between agent-visible evidence and facilitator secrets.
    """

    def __init__(self):
        self._current_case: Optional[MysteryCase] = None
        self.load_aurora_diamond_case()

    def load_aurora_diamond_case(self) -> MysteryCase:
        """Loads the default Aurora Diamond case dossier."""
        case_file = DATA_DIR / "aurora_diamond.json"
        if not case_file.exists():
            raise FileNotFoundError(f"Case file not found at {case_file}")

        with open(case_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._current_case = MysteryCase(**data)
        return self._current_case

    def load_custom_case(self, case_dict: Dict[str, Any]) -> MysteryCase:
        """Loads a user-created or uploaded case."""
        case_obj = MysteryCase(**case_dict)
        self._current_case = case_obj
        return self._current_case

    def get_current_case(self) -> MysteryCase:
        if self._current_case is None:
            self.load_aurora_diamond_case()
        return self._current_case

    def get_agent_visible_data(self) -> Dict[str, Any]:
        """
        CRITICAL SECURITY RULE:
        Sanitizes case data, completely stripping hidden_solution before dispatching to agents.
        """
        c = self.get_current_case()
        raw = c.model_dump()
        raw.pop("hidden_solution", None)
        return raw

    def create_case_variation(self, remove_evidence_id: Optional[str] = None) -> MysteryCase:
        """Creates a counterfactual variation (e.g. removing Evidence E)."""
        c = self.get_current_case()
        data = c.model_dump()
        if remove_evidence_id:
            data["evidence"] = [e for e in data["evidence"] if e["evidence_id"] != remove_evidence_id]
            data["title"] = f"{data['title']} (Without {remove_evidence_id})"
            data["case_id"] = f"{data['case_id']}-VAR"
        return MysteryCase(**data)

# Singleton instance
_case_engine_instance: Optional[CaseEngine] = None

def get_case_engine() -> CaseEngine:
    global _case_engine_instance
    if _case_engine_instance is None:
        _case_engine_instance = CaseEngine()
    return _case_engine_instance
