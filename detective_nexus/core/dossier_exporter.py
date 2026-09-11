"""
Detective Nexus Forensic Dossier Exporter
Generates formal, formatted investigation dossiers (.md and .txt) for instant download.
100% Pure Python with zero external dependencies.
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXPORTS_DIR = (PROJECT_ROOT / "data" / "exports").resolve()


class DossierExporter:
    """Exports comprehensive forensic investigation dossiers for user download."""

    @classmethod
    def export_case_dossier(
        cls,
        case_title: str,
        category: str,
        raw_narrative: str,
        scorecard: Dict[str, Any],
        agent_analysis: str,
        officer_name: str = "Forensic Field Investigator",
        badge_id: str = "BADGE-4892"
    ) -> str:
        """
        Creates a structured markdown file and returns the file path.
        """
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in case_title if c.isalnum() or c in ("-", "_")).strip() or "CASE"
        filename = f"FORENSIC_DOSSIER_{safe_title}_{timestamp_str}.md"
        file_path = EXPORTS_DIR / filename

        score = scorecard.get("overall_score", 50)
        grade = scorecard.get("grade", "GRADE C")
        summary = scorecard.get("verdict_summary", "Evaluation complete.")
        ev_score = scorecard.get("evidence_completeness", 50)
        tm_score = scorecard.get("timeline_integrity", 50)
        sus_score = scorecard.get("suspect_profiling", 50)
        sk_score = scorecard.get("skeptic_resistance", 50)

        strengths_lines = "\n".join([f"- [x] {s}" for s in scorecard.get("strengths", ["Incident recorded"])])
        vulns_lines = "\n".join([f"- [!] {v}" for v in scorecard.get("vulnerabilities", ["Corroboration required"])])
        tests_lines = "\n".join([f"- [ ] {t}" for t in scorecard.get("missing_tests", ["Physical trace swabbing"])])

        content = f"""# ==============================================================================
# OFFICIAL FORENSIC INVESTIGATION DOSSIER & SOLVABILITY AUDIT
# DETECTIVE NEXUS // METROPOLITAN CRIME & DOCUMENT ANALYSIS DIVISION
# ==============================================================================

DATE OF GENERATION: {time.strftime("%Y-%m-%d %H:%M:%S")}
CASE REFERENCE: {case_title}
REPORT CLASSIFICATION: {category.upper()}
INVESTIGATING OFFICER: {officer_name} (Badge #{badge_id})
OPERATIONAL STATUS: FORENSIC REVIEW COMPLETE

--------------------------------------------------------------------------------
1. FORENSIC SOLVABILITY SCORECARD & READINESS METRICS
--------------------------------------------------------------------------------
OVERALL SOLVABILITY INDEX: {score} / 100
PROSECUTORIAL READINESS GRADE: {grade}
PROSECUTORIAL ASSESSMENT:
{summary}

DIMENSIONAL RIGOR METRICS:
- Evidentiary Completeness:    {ev_score}%
- Timeline & Window Rigor:     {tm_score}%
- Suspect & Alibi Rigor:       {sus_score}%
- Reasonable Doubt Resistance: {sk_score}%

ESTABLISHED FACTUAL PILLARS:
{strengths_lines}

CRITICAL DEFENSE VULNERABILITIES:
{vulns_lines}

MANDATORY PRE-TRIAL CONFIRMATORY TESTS:
{tests_lines}

--------------------------------------------------------------------------------
2. PRIMARY INCIDENT NARRATIVE / EXTRACTED TEXT
--------------------------------------------------------------------------------
{raw_narrative}

--------------------------------------------------------------------------------
3. MULTI-AGENT FORENSIC INVESTIGATION & RED-FLAG AUDIT
--------------------------------------------------------------------------------
{agent_analysis}

--------------------------------------------------------------------------------
4. EPISTEMIC & FORENSIC CERTIFICATION
--------------------------------------------------------------------------------
- Motive does NOT constitute legal proof of guilt.
- Credential access does NOT prove physical presence without biometric corroboration.
- All conclusions remain provisional pending certified laboratory spectrometry.

CERTIFIED BY: Detective Nexus AI Operating System
ARCHIVED UNDER BADGE: #{badge_id}
# ==============================================================================
"""
        file_path.write_text(content, encoding="utf-8")
        return str(file_path.resolve().as_posix())
