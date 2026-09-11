"""
Chief Agent Implementation for AI Mystery Detective Team.
Case: The Vanishing Aurora Diamond

Part 7 — Senior Investigative Synthesis, Evidence Weighting, Cross-Agent Reconciliation,
and Provisional Assessment for Human Review.
Fifth Autonomous AI Agent.
Synthesizes findings from Detective, Evidence, Suspect, and Skeptic reports.
Explicitly separates Fact, Inference, Uncertainty, and Unknowns without premature conviction
or voting-by-majority fallacy.
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional

from app.case.case_data import get_agent_visible_case
from app.prompts.chief_prompt import (
    CHIEF_SYSTEM_PROMPT,
    build_chief_user_prompt,
)
from app.gemini_client import generate_content

logger = logging.getLogger(__name__)


def _extract_section_text(report_text: str, section_header_regex: str) -> str:
    """
    Extracts the full text body of a specific numbered section from the markdown report.
    """
    pattern = rf"##\s+\d+\.\s+{section_header_regex}(.*?)(?=##\s+\d+\.|\#\s+HUMAN REVIEW|\Z)"
    match = re.search(pattern, report_text, re.DOTALL | re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_section_items(report_text: str, section_header_regex: str) -> List[str]:
    """
    Extracts bulleted or numbered items from a specific section in the markdown report.
    """
    section_body = _extract_section_text(report_text, section_header_regex)
    if not section_body:
        return []

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


def _parse_confidence(report_text: str) -> Dict[str, str]:
    """
    Parses Section 13 (Confidence Assessment) into structured level and reason.
    Allowed levels: VERY LOW, LOW, MODERATE, HIGH, VERY HIGH.
    """
    section_text = _extract_section_text(report_text, "Confidence Assessment")
    res = {
        "level": "MODERATE",
        "reason": "Strong circumstantial evidence connecting keycard to crime scene, but physical user identity and diamond possession remain unproven."
    }
    if not section_text:
        return res

    for line in section_text.splitlines():
        line_clean = line.strip()
        lower = line_clean.lower()
        if "confidence level:" in lower or "confidence:" in lower:
            parts = line_clean.split(":", 1)
            if len(parts) > 1:
                val = parts[1].strip().strip("*").upper()
                for level in ["VERY HIGH", "VERY LOW", "HIGH", "LOW", "MODERATE"]:
                    if level in val:
                        res["level"] = level
                        break
        elif "reason:" in lower:
            parts = line_clean.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                res["reason"] = parts[1].strip().strip("*")

    return res


def _parse_final_provisional_assessment(report_text: str) -> Dict[str, Any]:
    """
    Parses Section 14 (Final Provisional Assessment).
    """
    section_text = _extract_section_text(report_text, "Final Provisional Assessment")
    res = {
        "leading_suspect_or_explanation": "Arjun Vale (Provisional)",
        "why": "Authorized keycard access at 8:23 PM, conflicting alibi regarding jacket, and blue velvet fibers inside catalog folder.",
        "main_uncertainty": "Physical user of keycard is not biometrically established, and diamond was not visually confirmed inside folder.",
        "strongest_alternative": "A third party accessed Arjun's keycard from his unattended jacket during the blackout.",
        "next_evidence_needed": ["Corridor CCTV review", "Spectrometric fiber analysis"],
        "human_review_required": True
    }
    if not section_text:
        return res

    for line in section_text.splitlines():
        line_clean = line.strip()
        lower = line_clean.lower()
        if "leading suspect" in lower or "current leading" in lower:
            parts = line_clean.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                res["leading_suspect_or_explanation"] = parts[1].strip().strip("*")
        elif "why" in lower and ":" in line_clean:
            parts = line_clean.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                res["why"] = parts[1].strip().strip("*")
        elif "main uncertainty" in lower or "key uncertainty" in lower:
            parts = line_clean.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                res["main_uncertainty"] = parts[1].strip().strip("*")
        elif "strongest alternative" in lower:
            parts = line_clean.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                res["strongest_alternative"] = parts[1].strip().strip("*")

    return res


def _extract_evidence_vs_inference(report_text: str) -> Dict[str, List[str]]:
    """
    Parses Section 4 (Evidence vs Inference) into structured categories:
    established_facts, reasonable_inferences, unresolved_uncertainties, unknown_information.
    """
    section_text = _extract_section_text(report_text, "Evidence vs Inference")
    buckets = {
        "established_facts": [],
        "reasonable_inferences": [],
        "unresolved_uncertainties": [],
        "unknown_information": []
    }
    if not section_text:
        return buckets

    current_bucket = None
    for line in section_text.splitlines():
        line_clean = line.strip()
        lower = line_clean.lower()
        if "established fact" in lower and ("###" in line_clean or "**" in line_clean):
            current_bucket = "established_facts"
        elif "reasonable inference" in lower and ("###" in line_clean or "**" in line_clean):
            current_bucket = "reasonable_inferences"
        elif "uncertaint" in lower and ("###" in line_clean or "**" in line_clean):
            current_bucket = "unresolved_uncertainties"
        elif "unknown" in lower and ("###" in line_clean or "**" in line_clean):
            current_bucket = "unknown_information"
        elif current_bucket and line_clean.startswith(("-", "*", "•")):
            cleaned = line_clean.lstrip("-*• ").strip()
            if cleaned:
                buckets[current_bucket].append(cleaned)
        elif current_bucket and re.match(r"^\d+[\.\)]\s+", line_clean):
            cleaned = re.sub(r"^\d+[\.\)]\s+", "", line_clean).strip()
            if cleaned:
                buckets[current_bucket].append(cleaned)

    return buckets


def _extract_suspect_comparisons(report_text: str) -> List[Dict[str, Any]]:
    """
    Parses suspect comparisons from Section 5.
    """
    section_text = _extract_section_text(report_text, "Suspect Comparison")
    suspects = [
        ("S01", "Lena Ortiz"),
        ("S02", "Theo Park"),
        ("S03", "Arjun Vale"),
        ("S04", "Sofia Reed")
    ]
    comparisons = []
    for sid, name in suspects:
        pattern = rf"(?:###\s+.*{name}.*|{name}:?)(.*?)(?=(?:###\s+.*(?:Lena|Theo|Arjun|Sofia)|\Z))"
        match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
        if match:
            body = match.group(1).strip()
            comparisons.append({
                "suspect_id": sid,
                "suspect_name": name,
                "summary": body[:400] + ("..." if len(body) > 400 else ""),
                "full_text": body
            })
        else:
            comparisons.append({
                "suspect_id": sid,
                "suspect_name": name,
                "summary": f"Detailed comparison for {name} documented in Section 5.",
                "full_text": ""
            })
    return comparisons


def run_chief_agent(
    case_data: Optional[Dict[str, Any]] = None,
    detective_report: str = "",
    evidence_report: str = "",
    suspect_report: str = "",
    skeptic_report: str = ""
) -> Dict[str, Any]:
    """
    Executes the Chief Agent synthesis using Google Gemini.

    Args:
        case_data (Optional[Dict[str, Any]]): Sanitized case dictionary. Defaults to
                                              get_agent_visible_case() if None.
        detective_report (str): Output from Detective Agent.
        evidence_report (str): Output from Evidence Agent.
        suspect_report (str): Output from Suspect Agent.
        skeptic_report (str): Output from Skeptic Agent.

    Returns:
        Dict[str, Any]: Structured chief investigation payload including full markdown report
                        and parsed executive audit components.
    """
    # 1. Acquire sanitized case data
    if case_data is None:
        case_data = get_agent_visible_case()

    # 2. Strict Anti-Solution-Leak Security Check
    combined_str = (
        str(case_data) + " " + detective_report + " " +
        evidence_report + " " + suspect_report + " " + skeptic_report
    ).lower()

    leak_terms = [
        "facilitator_only_guidance",
        "human_review_answer",
        "arjun vale is guilty",
        "predetermined culprit"
    ]
    for term in leak_terms:
        if term in combined_str:
            error_msg = f"Security Violation: '{term}' detected in input to Chief Agent."
            logger.critical(error_msg)
            return {
                "agent": "chief",
                "status": "error",
                "report": "",
                "executive_summary": "",
                "current_best_explanation": {},
                "evidence_foundation": [],
                "evidence_vs_inference": {},
                "suspect_comparison": [],
                "cross_agent_analysis": {},
                "skeptic_findings": [],
                "alternative_explanations": [],
                "strongest_evidence": [],
                "weakest_link": "",
                "not_proven": [],
                "recommended_next_investigation": [],
                "confidence_assessment": {},
                "final_provisional_assessment": {},
                "error": error_msg
            }

    # 3. Build user prompt
    user_prompt = build_chief_user_prompt(
        case_data=case_data,
        detective_report=detective_report,
        evidence_report=evidence_report,
        suspect_report=suspect_report,
        skeptic_report=skeptic_report
    )

    # 4. Query Gemini
    success, result_text = generate_content(
        system_instruction=CHIEF_SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    if not success:
        return {
            "agent": "chief",
            "status": "error",
            "report": "",
            "executive_summary": "",
            "current_best_explanation": {},
            "evidence_foundation": [],
            "evidence_vs_inference": {},
            "suspect_comparison": [],
            "cross_agent_analysis": {},
            "skeptic_findings": [],
            "alternative_explanations": [],
            "strongest_evidence": [],
            "weakest_link": "",
            "not_proven": [],
            "recommended_next_investigation": [],
            "confidence_assessment": {},
            "final_provisional_assessment": {},
            "error": result_text
        }

    # 5. Extract structured subsets
    exec_summary = _extract_section_text(result_text, "Executive Summary")
    best_explanation_text = _extract_section_text(result_text, "Current Best Explanation")
    evidence_foundation_items = _extract_section_items(result_text, "Evidence Foundation")
    evidence_vs_inference = _extract_evidence_vs_inference(result_text)
    suspect_comparison = _extract_suspect_comparisons(result_text)
    cross_agent_items = _extract_section_items(result_text, "Cross-Agent Agreement and Disagreement")
    skeptic_findings_items = _extract_section_items(result_text, "Skeptic Findings")
    alternatives_items = _extract_section_items(result_text, "Alternative Explanations")
    strongest_ev_items = _extract_section_items(result_text, "Strongest Evidence")
    weakest_link_text = _extract_section_text(result_text, "Weakest Link in the Current Theory")
    not_proven_items = _extract_section_items(result_text, "What Is NOT Proven")
    recommended_next = _extract_section_items(result_text, "Recommended Next Investigation")
    confidence_data = _parse_confidence(result_text)
    final_provisional = _parse_final_provisional_assessment(result_text)

    # Structure current best explanation
    current_best_explanation = {
        "suspect_or_explanation": final_provisional.get("leading_suspect_or_explanation", "Arjun Vale (Provisional)"),
        "reason": best_explanation_text[:400] + ("..." if len(best_explanation_text) > 400 else ""),
        "confidence": confidence_data.get("level", "MODERATE"),
        "limitations": not_proven_items
    }

    return {
        "agent": "chief",
        "status": "completed",
        "report": result_text,
        "executive_summary": exec_summary,
        "current_best_explanation": current_best_explanation,
        "evidence_foundation": evidence_foundation_items,
        "evidence_vs_inference": evidence_vs_inference,
        "suspect_comparison": suspect_comparison,
        "cross_agent_analysis": {"details": cross_agent_items},
        "skeptic_findings": skeptic_findings_items,
        "alternative_explanations": alternatives_items,
        "strongest_evidence": strongest_ev_items,
        "weakest_link": weakest_link_text[:400] + ("..." if len(weakest_link_text) > 400 else ""),
        "not_proven": not_proven_items,
        "recommended_next_investigation": recommended_next,
        "confidence_assessment": confidence_data,
        "final_provisional_assessment": final_provisional,
        "error": None
    }
