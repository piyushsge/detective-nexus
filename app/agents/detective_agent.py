"""
Detective Agent Implementation for AI Mystery Detective Team.
Case: The Vanishing Aurora Diamond

Part 3 — First AI Agent in the Multi-Agent Architecture.
Analyzes sanitized case data to construct an objective investigation report
without assigning premature guilt or receiving facilitator solutions.
"""

import re
import logging
from typing import Any, Dict, List

from app.case.case_data import get_agent_visible_case
from app.prompts.detective_prompt import (
    DETECTIVE_SYSTEM_PROMPT,
    build_detective_user_prompt,
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
        # Look for bullet points or numbered lists
        if line.startswith(("-", "*", "•")):
            cleaned = line.lstrip("-*• ").strip()
            if cleaned:
                items.append(cleaned)
        elif re.match(r"^\d+[\.\)]\s+", line):
            cleaned = re.sub(r"^\d+[\.\)]\s+", "", line).strip()
            if cleaned:
                items.append(cleaned)
    return items


def run_detective_agent(case_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Executes the Detective Agent analysis using the Google Gemini model.

    Args:
        case_data (Dict[str, Any] | None): Sanitized case dictionary. Defaults to
                                          get_agent_visible_case() if not provided.

    Returns:
        Dict[str, Any]: Structured detective investigation payload containing:
            - agent: "detective"
            - status: "completed" | "error"
            - report: full markdown investigation report
            - key_questions: list of extracted unanswered questions
            - important_evidence: list of extracted evidence focus items
            - contradictions: list of extracted tension/conflict items
            - information_gaps: list of extracted information gaps
            - recommended_priorities: list of recommended investigation priorities
            - error: error message if status == "error", else None
    """
    # 1. Acquire sanitized case data
    if case_data is None:
        case_data = get_agent_visible_case()

    # 2. Strict Anti-Solution-Leak Security Check
    case_str = str(case_data).lower()
    leak_terms = [
        "facilitator_only_guidance",
        "leading_suspect",
        "arjun is the leading suspect",
        "arjun vale is guilty"
    ]
    for term in leak_terms:
        if term in case_str:
            error_msg = f"Security Violation: '{term}' detected in input to Detective Agent."
            logger.critical(error_msg)
            return {
                "agent": "detective",
                "status": "error",
                "report": "",
                "key_questions": [],
                "important_evidence": [],
                "contradictions": [],
                "information_gaps": [],
                "recommended_priorities": [],
                "error": error_msg
            }

    # 3. Build the prompt
    user_prompt = build_detective_user_prompt(case_data)

    # 4. Query Gemini
    success, result_text = generate_content(
        system_instruction=DETECTIVE_SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    if not success:
        return {
            "agent": "detective",
            "status": "error",
            "report": "",
            "key_questions": [],
            "important_evidence": [],
            "contradictions": [],
            "information_gaps": [],
            "recommended_priorities": [],
            "error": result_text
        }

    # 5. Extract structured subsets for downstream agents
    key_questions = _extract_section_items(result_text, "Unanswered Questions")
    important_evidence = _extract_section_items(result_text, "Important Evidence to Investigate")
    contradictions = _extract_section_items(result_text, "Contradictions and Tensions")
    information_gaps = _extract_section_items(result_text, "Information Gaps")
    priorities = _extract_section_items(result_text, "Recommended Investigation Priorities")

    return {
        "agent": "detective",
        "status": "completed",
        "report": result_text,
        "key_questions": key_questions,
        "important_evidence": important_evidence,
        "contradictions": contradictions,
        "information_gaps": information_gaps,
        "recommended_priorities": priorities,
        "error": None
    }
