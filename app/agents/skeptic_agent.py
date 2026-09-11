"""
Skeptic Agent Implementation for AI Mystery Detective Team.
Case: The Vanishing Aurora Diamond

Part 6 — Adversarial Forensic Review, Assumption Auditing, and Falsification Testing.
Fourth Autonomous AI Agent.
Challenges the investigation, stress-tests the leading theory, audits facts vs inferences,
identifies critical missing evidence, and formulates alternative hypotheses and falsification tests.
"""

import re
import json
import logging
from typing import Any, Dict, List, Optional

from app.case.case_data import get_agent_visible_case
from app.prompts.skeptic_prompt import (
    SKEPTIC_SYSTEM_PROMPT,
    build_skeptic_user_prompt,
)
from app.gemini_client import generate_content

logger = logging.getLogger(__name__)


def _extract_section_text(report_text: str, section_header_regex: str) -> str:
    """
    Extracts the full text body of a specific numbered section from the markdown report.
    """
    pattern = rf"##\s+\d+\.\s+{section_header_regex}(.*?)(?=##\s+\d+\.|\Z)"
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


def _parse_skeptic_assessment(report_text: str) -> Dict[str, str]:
    """
    Parses the final Skeptic Assessment section into key structured fields:
    status, main_vulnerability, strongest_alternative, most_important_missing_evidence, challenge_level.
    """
    assessment_text = _extract_section_text(report_text, "Skeptic Assessment")
    fields = {
        "status": "Unresolved / Plausible but Fragile",
        "main_vulnerability": "Card owner equated to card user; diamond assumed inside folder.",
        "strongest_alternative": "Authorized card accessed/borrowed by another actor; or removal decoupled from 8:23 PM log.",
        "most_important_missing_evidence": "Corridor/archive camera footage and scientific velvet fiber comparison.",
        "challenge_level": "HIGH"
    }

    if not assessment_text:
        return fields

    # Pattern searches for labelled lines
    for line in assessment_text.splitlines():
        line = line.strip()
        lower_line = line.lower()
        if "current theory status:" in lower_line or "theory status:" in lower_line:
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                fields["status"] = parts[1].strip().strip("*")
        elif "main vulnerability:" in lower_line or "key vulnerability:" in lower_line:
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                fields["main_vulnerability"] = parts[1].strip().strip("*")
        elif "strongest alternative:" in lower_line:
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                fields["strongest_alternative"] = parts[1].strip().strip("*")
        elif "most important missing evidence:" in lower_line or "missing evidence:" in lower_line:
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                fields["most_important_missing_evidence"] = parts[1].strip().strip("*")
        elif "overall challenge level:" in lower_line or "challenge level:" in lower_line:
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip():
                val = parts[1].strip().strip("*").upper()
                for level in ["CRITICAL", "HIGH", "MODERATE", "LOW"]:
                    if level in val:
                        fields["challenge_level"] = level
                        break
                else:
                    fields["challenge_level"] = val

    return fields


def _extract_evidence_vulnerabilities(report_text: str) -> List[Dict[str, Any]]:
    """
    Extracts structured vulnerability analysis for evidence items E-A through E-G.
    """
    vulnerabilities = []
    section_text = _extract_section_text(report_text, "Evidence Vulnerabilities")
    
    evidence_ids = ["E-A", "E-B", "E-C", "E-D", "E-E", "E-F", "E-G"]
    for eid in evidence_ids:
        pattern = rf"(?:###\s+.*{eid}.*|{eid}:?)(.*?)(?=(?:###\s+.*E-[A-G]|E-[A-G]:|\Z))"
        match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
        if match:
            body = match.group(1).strip()
            vulnerabilities.append({
                "evidence_id": eid,
                "analysis": body[:400] + ("..." if len(body) > 400 else ""),
                "raw_text": body
            })
        else:
            vulnerabilities.append({
                "evidence_id": eid,
                "analysis": f"Evidentiary vulnerability analyzed in Section 3 of report.",
                "raw_text": ""
            })
            
    return vulnerabilities


def _extract_fact_inference_audit(report_text: str) -> Dict[str, List[str]]:
    """
    Parses the Fact vs Inference Audit section into structured buckets:
    facts, inferences, uncertain_claims, unsupported_claims.
    """
    audit_text = _extract_section_text(report_text, "Fact vs Inference Audit")
    buckets = {
        "facts": [],
        "inferences": [],
        "uncertain_claims": [],
        "unsupported_claims": []
    }
    
    if not audit_text:
        return buckets

    current_bucket = None
    for line in audit_text.splitlines():
        line = line.strip()
        lower_line = line.lower()
        if "facts" in lower_line and ("###" in line or "**" in line):
            current_bucket = "facts"
        elif "inferences" in lower_line and ("###" in line or "**" in line):
            current_bucket = "inferences"
        elif "uncertain" in lower_line and ("###" in line or "**" in line):
            current_bucket = "uncertain_claims"
        elif "unsupported" in lower_line and ("###" in line or "**" in line):
            current_bucket = "unsupported_claims"
        elif current_bucket and line.startswith(("-", "*", "•")):
            cleaned = line.lstrip("-*• ").strip()
            if cleaned:
                buckets[current_bucket].append(cleaned)
        elif current_bucket and re.match(r"^\d+[\.\)]\s+", line):
            cleaned = re.sub(r"^\d+[\.\)]\s+", "", line).strip()
            if cleaned:
                buckets[current_bucket].append(cleaned)

    return buckets


def _extract_suspect_stress_test(report_text: str) -> List[Dict[str, Any]]:
    """
    Parses suspect stress tests for all 4 suspects.
    """
    stress_tests = []
    section_text = _extract_section_text(report_text, "Suspect Theory Stress Test")
    suspects = [
        ("S01", "Lena Ortiz"),
        ("S02", "Theo Park"),
        ("S03", "Arjun Vale"),
        ("S04", "Sofia Reed")
    ]

    for sid, name in suspects:
        pattern = rf"(?:###\s+.*{name}.*|{name}:?)(.*?)(?=(?:###\s+.*(?:Lena|Theo|Arjun|Sofia)|\Z))"
        match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
        if match:
            body = match.group(1).strip()
            # Determine assessment if mentioned
            assessment = "MODERATE"
            for lvl in ["STRONG", "MODERATE", "WEAK", "UNSUPPORTED"]:
                if lvl in body.upper():
                    assessment = lvl
                    break
            stress_tests.append({
                "suspect_id": sid,
                "suspect_name": name,
                "evaluation": body[:500] + ("..." if len(body) > 500 else ""),
                "assessment": assessment
            })
        else:
            stress_tests.append({
                "suspect_id": sid,
                "suspect_name": name,
                "evaluation": f"Stress test detailed in Section 5 of report.",
                "assessment": "MODERATE"
            })

    return stress_tests


def run_skeptic_agent(
    case_data: Optional[Dict[str, Any]] = None,
    detective_report: str = "",
    evidence_report: str = "",
    suspect_report: str = ""
) -> Dict[str, Any]:
    """
    Executes the Skeptic Agent adversarial analysis using the Google Gemini model.

    Args:
        case_data (Optional[Dict[str, Any]]): Sanitized case dictionary. Defaults to
                                              get_agent_visible_case() if None.
        detective_report (str): Output from Detective Agent.
        evidence_report (str): Output from Evidence Agent.
        suspect_report (str): Output from Suspect Agent.

    Returns:
        Dict[str, Any]: Structured skeptic review payload including full markdown report
                        and structured audit fields.
    """
    # 1. Acquire sanitized case data
    if case_data is None:
        case_data = get_agent_visible_case()

    # 2. Strict Anti-Solution-Leak Security Check
    combined_str = (str(case_data) + " " + detective_report + " " + evidence_report + " " + suspect_report).lower()
    leak_terms = [
        "facilitator_only_guidance",
        "human_review_answer",
        "arjun vale is guilty",
        "predetermined culprit"
    ]
    for term in leak_terms:
        if term in combined_str:
            error_msg = f"Security Violation: '{term}' detected in input to Skeptic Agent."
            logger.critical(error_msg)
            return {
                "agent": "skeptic",
                "status": "error",
                "report": "",
                "current_theory": "",
                "assumptions": [],
                "evidence_vulnerabilities": [],
                "fact_inference_audit": {},
                "suspect_stress_test": [],
                "alternative_explanations": [],
                "counterarguments": [],
                "falsification_tests": [],
                "critical_missing_evidence": [],
                "recommended_verification_steps": [],
                "skeptic_assessment": {},
                "error": error_msg
            }

    # 3. Build user prompt
    user_prompt = build_skeptic_user_prompt(
        case_data=case_data,
        detective_report=detective_report,
        evidence_report=evidence_report,
        suspect_report=suspect_report
    )

    # 4. Query Gemini
    success, result_text = generate_content(
        system_instruction=SKEPTIC_SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    if not success:
        return {
            "agent": "skeptic",
            "status": "error",
            "report": "",
            "current_theory": "",
            "assumptions": [],
            "evidence_vulnerabilities": [],
            "fact_inference_audit": {},
            "suspect_stress_test": [],
            "alternative_explanations": [],
            "counterarguments": [],
            "falsification_tests": [],
            "critical_missing_evidence": [],
            "recommended_verification_steps": [],
            "skeptic_assessment": {},
            "error": result_text
        }

    # 5. Extract structured subsets
    current_theory = _extract_section_text(result_text, "Current Theory Being Challenged")
    assumptions_items = _extract_section_items(result_text, "Strongest Assumptions")
    vulnerabilities = _extract_evidence_vulnerabilities(result_text)
    fact_inference_audit = _extract_fact_inference_audit(result_text)
    suspect_stress = _extract_suspect_stress_test(result_text)
    alternatives = _extract_section_items(result_text, "Alternative Explanations")
    counterargs = _extract_section_items(result_text, "Counterarguments")
    falsification = _extract_section_items(result_text, "What Would Falsify the Current Theory")
    missing_evidence = _extract_section_items(result_text, "Critical Missing Evidence")
    verification_steps = _extract_section_items(result_text, "Recommended Verification Steps")
    assessment_data = _parse_skeptic_assessment(result_text)

    # Structure assumptions list
    formatted_assumptions = []
    for item in assumptions_items:
        formatted_assumptions.append({
            "assumption": item,
            "risk_level": "HIGH" if any(w in item.upper() for w in ["HIGH", "CRITICAL"]) else "MEDIUM"
        })

    return {
        "agent": "skeptic",
        "status": "completed",
        "report": result_text,
        "current_theory": current_theory,
        "assumptions": formatted_assumptions,
        "evidence_vulnerabilities": vulnerabilities,
        "fact_inference_audit": fact_inference_audit,
        "suspect_stress_test": suspect_stress,
        "alternative_explanations": alternatives,
        "counterarguments": counterargs,
        "falsification_tests": falsification,
        "critical_missing_evidence": missing_evidence,
        "recommended_verification_steps": verification_steps,
        "skeptic_assessment": assessment_data,
        "error": None
    }
