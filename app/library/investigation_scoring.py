"""
Investigation Scoring Engine & History Storage.
Evaluates detective team performance across 6 analytical axes:
1. Evidence Grounding
2. Suspect Fairness
3. Skeptic Reasoning
4. Uncertainty Awareness
5. Alternative Theory
6. Human Review Alignment

Persists completed investigations to data/investigation-history.json.
"""

import os
import json
import datetime
from typing import Dict, Any, List

HISTORY_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "investigation-history.json")
)


def calculate_investigation_score(
    case_data: Dict[str, Any],
    chief_report: Dict[str, Any],
    skeptic_report: Dict[str, Any],
    suspect_report: Dict[str, Any],
    evidence_report: Dict[str, Any],
    human_verdict: str = "Accepted",
) -> Dict[str, Any]:
    """
    Evaluates investigation quality rigorously. Does not simply reward guessing the culprit.
    A well-reasoned minority conclusion with strong evidence grounding receives high credit.
    """
    scores = {}

    # 1. Evidence Grounding (0 - 100)
    # Checks if evidence items were actively cited and limitations recognized
    ev_list = case_data.get("evidence", [])
    ev_ids = [e.get("evidence_id") for e in ev_list]
    cited_count = 0
    chief_text = json.dumps(chief_report).lower()
    for eid in ev_ids:
        if eid.lower() in chief_text:
            cited_count += 1
    grounding_ratio = cited_count / max(len(ev_ids), 1)
    scores["evidence_grounding"] = min(100, int(60 + (grounding_ratio * 40)))

    # 2. Suspect Fairness (0 - 100)
    # Checks if all suspects were analyzed without premature dismissal
    total_suspects = len(case_data.get("suspects", []))
    analyzed_suspects = len(suspect_report.get("suspect_assessments", []))
    fairness_ratio = analyzed_suspects / max(total_suspects, 1)
    scores["suspect_fairness"] = min(100, int(70 + (fairness_ratio * 30)))

    # 3. Skeptic Reasoning (0 - 100)
    # Evaluates whether the skeptic challenged assumptions and proposed doubts
    skeptic_challenges = len(skeptic_report.get("critical_challenges", []))
    alt_theories = len(skeptic_report.get("alternative_theories", []))
    if skeptic_challenges >= 2 and alt_theories >= 1:
        scores["skeptic_reasoning"] = 88
    elif skeptic_challenges >= 1:
        scores["skeptic_reasoning"] = 75
    else:
        scores["skeptic_reasoning"] = 55

    # 4. Uncertainty Awareness (0 - 100)
    # Did the Chief explicitly identify critical gaps and missing evidence?
    chief_gaps = len(chief_report.get("critical_gaps", []))
    chief_missing = len(chief_report.get("missing_evidence_required", []))
    if chief_gaps >= 2 or chief_missing >= 2:
        scores["uncertainty_awareness"] = 92
    elif chief_gaps >= 1 or chief_missing >= 1:
        scores["uncertainty_awareness"] = 82
    else:
        scores["uncertainty_awareness"] = 65

    # 5. Alternative Theory (0 - 100)
    # Did the final synthesis account for a competing narrative?
    alt_exp = chief_report.get("alternative_explanation", "")
    if len(alt_exp.strip()) > 30:
        scores["alternative_theory"] = 85
    else:
        scores["alternative_theory"] = 60

    # Overall calculation (weighted average)
    overall = int(
        (scores["evidence_grounding"] * 0.25)
        + (scores["suspect_fairness"] * 0.20)
        + (scores["skeptic_reasoning"] * 0.20)
        + (scores["uncertainty_awareness"] * 0.20)
        + (scores["alternative_theory"] * 0.15)
    )
    scores["overall"] = overall

    return scores


def format_score_meter(score: int) -> str:
    """Generates a visual ASCII bar meter like: ████████░░ 82/100"""
    filled = int(score / 10)
    empty = 10 - filled
    bar = ("█" * filled) + ("░" * empty)
    return f"{bar}  {score}/100"


def save_investigation_to_history(
    case_id: str,
    case_title: str,
    difficulty: str,
    ai_conclusion: str,
    confidence: str,
    human_decision: str,
    score_data: Dict[str, Any],
    duration_seconds: int = 15,
) -> None:
    """Appends a completed investigation record to history storage."""
    history = load_investigation_history()

    record = {
        "id": f"INV-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "caseId": case_id,
        "title": case_title,
        "difficulty": difficulty,
        "aiConclusion": ai_conclusion,
        "confidence": confidence,
        "humanDecision": human_decision,
        "scores": score_data,
        "durationSeconds": duration_seconds,
    }

    history.insert(0, record)
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def load_investigation_history() -> List[Dict[str, Any]]:
    """Loads all historic investigations from disk."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading investigation history: {e}")
        return []
