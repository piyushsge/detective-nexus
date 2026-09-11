"""
Evidence Agent Implementation for AI Mystery Detective Team.
Case: The Vanishing Aurora Diamond

Part 4 — Second Autonomous AI Agent.
Independently analyzes each evidence item (E-A to E-G), separates facts from inferences,
assesses evidentiary strength and limitations, and prevents premature guilt attribution.
"""

import re
import logging
from typing import Any, Dict, List

from app.case.case_data import get_agent_visible_case
from app.prompts.evidence_prompt import (
    EVIDENCE_SYSTEM_PROMPT,
    build_evidence_user_prompt,
)
from app.gemini_client import generate_content

logger = logging.getLogger(__name__)


def _extract_section_items(report_text: str, section_header_regex: str) -> List[str]:
    """
    Extracts bulleted or numbered items from a specific section in the markdown report.
    """
    pattern = rf"##\s+\d+\.\s+{section_header_regex}(.*?)(?=##\s+\d+\.|\Z)"
    match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)
    if not match:
        return []

    section_body = match.group(1).strip()
    items = []
    for line in section_body.splitlines():
        line = line.strip()
        if line.startswith(("-", "*", "•")):
            cleaned = line.lstrip("-*• ").strip()
            if cleaned:
                items.append(cleaned)
        elif re.match(r"^\d+[\.\)]\s+", line):
            cleaned = re.sub(r"^\d+[\.\)]\s+", "", line).strip()
            if cleaned:
                items.append(cleaned)
    return items


def _extract_evidence_item_blocks(report_text: str) -> List[Dict[str, Any]]:
    """
    Parses structured evidence items E-A through E-G from Section 2 of the report.
    """
    evidence_ids = ["E-A", "E-B", "E-C", "E-D", "E-E", "E-F", "E-G"]
    items = []

    for eid in evidence_ids:
        # Match from evidence header until next evidence item or section boundary
        pattern = rf"({eid}[:\s—\-].*?)(?=(?:E-[A-G][:\s—\-]|\#\#\s+\d+\.|\Z))"
        match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)
        if match:
            block = match.group(1).strip()
            # Extract classification if present
            class_match = re.search(r"Classification[:\s\*]+(FACT|INFERENCE|DISTRACTION|UNCERTAIN)", block, re.IGNORECASE)
            strength_match = re.search(r"(?:Evidentiary\s+)?Strength[:\s\*]+(VERY\s+STRONG|STRONG|MODERATE|WEAK|UNDETERMINED)", block, re.IGNORECASE)
            
            items.append({
                "evidence_id": eid,
                "classification": class_match.group(1).upper() if class_match else "UNCERTAIN",
                "strength": strength_match.group(1).upper() if strength_match else "MODERATE",
                "raw_text": block[:300]
            })
        else:
            items.append({
                "evidence_id": eid,
                "classification": "UNCERTAIN",
                "strength": "MODERATE",
                "raw_text": f"{eid} analyzed in main report."
            })

    return items


def run_evidence_agent(case_data: Dict[str, Any] | None = None, detective_report: str = "") -> Dict[str, Any]:
    """
    Executes the Evidence Agent analysis using the Google Gemini model.

    Args:
        case_data (Dict[str, Any] | None): Sanitized case dictionary. Defaults to
                                          get_agent_visible_case() if None.
        detective_report (str): Output from the Detective Agent.

    Returns:
        Dict[str, Any]: Structured evidence analysis payload.
    """
    # 1. Acquire sanitized case data
    if case_data is None:
        case_data = get_agent_visible_case()

    # 2. Strict Anti-Solution-Leak Security Check
    combined_str = (str(case_data) + " " + detective_report).lower()
    leak_terms = [
        "facilitator_only_guidance",
        "leading_suspect",
        "arjun is the leading suspect",
        "arjun vale is guilty"
    ]
    for term in leak_terms:
        if term in combined_str:
            error_msg = f"Security Violation: '{term}' detected in input to Evidence Agent."
            logger.critical(error_msg)
            return {
                "agent": "evidence",
                "status": "error",
                "report": "",
                "evidence_analysis": [],
                "strongest_evidence": [],
                "weakest_evidence": [],
                "conflicting_evidence": [],
                "verification_required": [],
                "unsupported_conclusions": [],
                "error": error_msg
            }

    # 3. Build the prompt
    user_prompt = build_evidence_user_prompt(case_data, detective_report)

    # 4. Query Gemini
    success, result_text = generate_content(
        system_instruction=EVIDENCE_SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    if not success:
        return {
            "agent": "evidence",
            "status": "error",
            "report": "",
            "evidence_analysis": [],
            "strongest_evidence": [],
            "weakest_evidence": [],
            "conflicting_evidence": [],
            "verification_required": [],
            "unsupported_conclusions": [],
            "error": result_text
        }

    # 5. Extract structured subsets for downstream agents
    evidence_analysis = _extract_evidence_item_blocks(result_text)
    strongest = _extract_section_items(result_text, "Strongest Evidence")
    weakest = _extract_section_items(result_text, "Weakest Evidence")
    conflicts = _extract_section_items(result_text, "Conflicting Evidence")
    verification = _extract_section_items(result_text, "Verification Required")
    unsupported = _extract_section_items(result_text, "Unsupported Conclusions to Avoid")

    return {
        "agent": "evidence",
        "status": "completed",
        "report": result_text,
        "evidence_analysis": evidence_analysis,
        "strongest_evidence": strongest,
        "weakest_evidence": weakest,
        "conflicting_evidence": conflicts,
        "verification_required": verification,
        "unsupported_conclusions": unsupported,
        "error": None
    }
