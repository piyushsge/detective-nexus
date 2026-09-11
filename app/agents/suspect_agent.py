"""
Suspect Agent Implementation for AI Mystery Detective Team.
Case: The Vanishing Aurora Diamond

Part 5 — Third Autonomous AI Agent.
Performs a comparative evaluation of all four suspects (Lena, Theo, Arjun, Sofia)
across Motive, Means, Opportunity, Access, Alibi, Evidence, Contradictions, and Unknowns.
Synthesizes findings from Detective & Evidence reports without premature conviction.
"""

import re
import logging
from typing import Any, Dict, List

from app.case.case_data import get_agent_visible_case
from app.prompts.suspect_prompt import (
    SUSPECT_SYSTEM_PROMPT,
    build_suspect_user_prompt,
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


def _extract_suspect_profiles(report_text: str) -> Dict[str, Dict[str, Any]]:
    """
    Parses suspect profiles for S01 (Lena), S02 (Theo), S03 (Arjun), and S04 (Sofia).
    """
    suspect_map = {
        "S01": "Lena Ortiz",
        "S02": "Theo Park",
        "S03": "Arjun Vale",
        "S04": "Sofia Reed"
    }
    profiles = {}

    for sid, name in suspect_map.items():
        pattern = rf"###\s+{name}(.*?)(?=(?:###\s+[A-Za-z]+|\#\#\s+\d+\.|\Z))"
        match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)
        if match:
            body = match.group(1).strip()
            profiles[sid] = {
                "name": name,
                "summary": body[:400] + ("..." if len(body) > 400 else "")
            }
        else:
            profiles[sid] = {
                "name": name,
                "summary": f"Detailed profile for {name} analyzed in Section 2 of report."
            }

    return profiles


def run_suspect_agent(
    case_data: Dict[str, Any] | None = None,
    detective_report: str = "",
    evidence_report: str = ""
) -> Dict[str, Any]:
    """
    Executes the Suspect Agent comparative analysis using the Google Gemini model.

    Args:
        case_data (Dict[str, Any] | None): Sanitized case dictionary. Defaults to
                                          get_agent_visible_case() if None.
        detective_report (str): Output from Detective Agent.
        evidence_report (str): Output from Evidence Agent.

    Returns:
        Dict[str, Any]: Structured suspect analysis payload.
    """
    # 1. Acquire sanitized case data
    if case_data is None:
        case_data = get_agent_visible_case()

    # 2. Strict Anti-Solution-Leak Security Check
    combined_str = (str(case_data) + " " + detective_report + " " + evidence_report).lower()
    leak_terms = [
        "facilitator_only_guidance",
        "leading_suspect",
        "arjun is the leading suspect",
        "arjun vale is guilty"
    ]
    for term in leak_terms:
        if term in combined_str:
            error_msg = f"Security Violation: '{term}' detected in input to Suspect Agent."
            logger.critical(error_msg)
            return {
                "agent": "suspect",
                "status": "error",
                "report": "",
                "suspect_analysis": {},
                "comparison": [],
                "ranking": [],
                "leading_case": {},
                "weaknesses": [],
                "alternative_explanations": [],
                "ranking_change_evidence": [],
                "error": error_msg
            }

    # 3. Build user prompt
    user_prompt = build_suspect_user_prompt(case_data, detective_report, evidence_report)

    # 4. Query Gemini
    success, result_text = generate_content(
        system_instruction=SUSPECT_SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    if not success:
        return {
            "agent": "suspect",
            "status": "error",
            "report": "",
            "suspect_analysis": {},
            "comparison": [],
            "ranking": [],
            "leading_case": {},
            "weaknesses": [],
            "alternative_explanations": [],
            "ranking_change_evidence": [],
            "error": result_text
        }

    # 5. Extract structured subsets for downstream agents
    suspect_profiles = _extract_suspect_profiles(result_text)
    ranking_items = _extract_section_items(result_text, "Current Ranking")
    weaknesses_items = _extract_section_items(result_text, "Weaknesses in the Leading Case")
    alternatives_items = _extract_section_items(result_text, "Alternative Explanations")
    change_evidence_items = _extract_section_items(result_text, "Evidence That Could Change the Ranking")

    # Leading case summary
    leading_match = re.search(r"##\s+5\.\s+Strongest Current Case(.*?)(?=##\s+\d+\.|\Z)", result_text, re.DOTALL | re.IGNORECASE)
    leading_summary = leading_match.group(1).strip()[:500] if leading_match else "Analyzed in main report."

    return {
        "agent": "suspect",
        "status": "completed",
        "report": result_text,
        "suspect_analysis": suspect_profiles,
        "comparison": list(suspect_profiles.values()),
        "ranking": ranking_items,
        "leading_case": {"summary": leading_summary},
        "weaknesses": weaknesses_items,
        "alternative_explanations": alternatives_items,
        "ranking_change_evidence": change_evidence_items,
        "error": None
    }
