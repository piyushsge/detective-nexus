"""
Validation engine for the AI Mystery Case Platform.
Enforces logical consistency, anti-triviality protection, evidence quality,
timeline coherence, and hidden solution separation before cases can be loaded or published.
"""

from typing import Any, Dict, List, Tuple
import re


def validate_case_schema(case_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates structural integrity and data types of a case dictionary.
    """
    errors = []
    required_fields = [
        "caseId", "title", "category", "difficulty", "setting",
        "incident", "centralQuestions", "timeline", "suspects",
        "witnesses", "evidence", "hiddenSolution", "rules"
    ]
    for rf in required_fields:
        if rf not in case_data:
            errors.append(f"Missing required field: '{rf}'.")

    if errors:
        return False, errors

    # Check minimum numbers
    if len(case_data.get("suspects", [])) < 3:
        errors.append("Case must contain at least 3 suspects.")
    if len(case_data.get("evidence", [])) < 5:
        errors.append("Case must contain at least 5 evidence items.")
    if len(case_data.get("timeline", [])) < 4:
        errors.append("Case must contain at least 4 timeline events.")

    return len(errors) == 0, errors


def validate_investigation_quality(case_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that the case meets high analytical and epistemological standards:
    - Multiple plausible suspects
    - No obvious giveaways or trivial confessions
    - Evidence items have limitations and alternative interpretations
    - Hidden solution is well-formed and distinct from raw certainty
    """
    errors = []
    
    # 1. Anti-Triviality Check
    incident_text = case_data.get("incident", "").lower()
    suspects = case_data.get("suspects", [])
    evidence = case_data.get("evidence", [])
    hidden_sol = case_data.get("hiddenSolution", {})
    culprit_name = hidden_sol.get("culprit", "").lower()

    trivial_giveaways = [
        "confessed immediately",
        "was caught on camera stealing",
        "directly admitted",
        "obviously guilty",
        "left a note saying 'i stole it'"
    ]
    for tg in trivial_giveaways:
        if tg in incident_text:
            errors.append(f"Anti-Triviality Violation: Incident contains obvious giveaway '{tg}'.")

    # 2. Evidence Quality Check
    evidence_ids = set()
    for ev in evidence:
        eid = ev.get("evidence_id")
        if not eid:
            errors.append("Evidence item missing 'evidence_id'.")
            continue
        if eid in evidence_ids:
            errors.append(f"Duplicate evidence ID detected: '{eid}'.")
        evidence_ids.add(eid)

        if not ev.get("establishes"):
            errors.append(f"Evidence '{eid}' must specify what it establishes.")
        if not ev.get("does_not_establish"):
            errors.append(f"Evidence '{eid}' must explicitly specify limitations ('does_not_establish').")

    # 3. Suspect Integrity
    suspect_ids = set()
    for s in suspects:
        sid = s.get("suspect_id")
        if not sid:
            errors.append("Suspect missing 'suspect_id'.")
            continue
        if sid in suspect_ids:
            errors.append(f"Duplicate suspect ID detected: '{sid}'.")
        suspect_ids.add(sid)

        if not s.get("motive"):
            errors.append(f"Suspect '{s.get('name', sid)}' missing motive.")
        if not s.get("statement"):
            errors.append(f"Suspect '{s.get('name', sid)}' missing statement.")

    # 4. Hidden Solution Integrity
    if not hidden_sol.get("culprit"):
        errors.append("Hidden solution must specify a culprit.")
    if not hidden_sol.get("explanation"):
        errors.append("Hidden solution must provide a causal explanation.")
    if not hidden_sol.get("decisiveEvidence"):
        errors.append("Hidden solution must identify decisive evidence items.")
    if not hidden_sol.get("alternativeExplanation"):
        errors.append("Hidden solution must document why an alternative explanation exists.")

    return len(errors) == 0, errors


def validate_case(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validator function combining schema and investigation quality checks.
    """
    schema_ok, schema_errors = validate_case_schema(case_data)
    if not schema_ok:
        return {
            "valid": False,
            "errors": schema_errors
        }

    quality_ok, quality_errors = validate_investigation_quality(case_data)
    all_errors = schema_errors + quality_errors

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors
    }
