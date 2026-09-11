"""
Detective Nexus Forensic Dossier Exporter
Generates formal, formatted investigation dossiers (.md and .txt) for instant download.
100% Pure Python with zero external dependencies.
"""

import re
import time
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXPORTS_DIR = (PROJECT_ROOT / "data" / "exports").resolve()


class DossierExporter:
    """Exports comprehensive forensic investigation dossiers for user download."""

    @classmethod
    def clean_professional_filename(cls, case_title: str, custom_filename: str = "", extension: str = "md") -> str:
        """
        Creates a clean, human-readable, professional forensic evidence filename.
        Example: 'FORENSIC_DOSSIER_The_Vanishing_Aurora_Diamond_20260911.md'
                 'FORENSIC_DOSSIER_Train_Passenger_Theft_FIR_20260911.md'
        """
        if custom_filename and custom_filename.strip():
            raw = custom_filename.strip()
            # Remove extension if already supplied
            if raw.lower().endswith(f".{extension.lower()}"):
                raw = raw[:-len(extension)-1]
            clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', raw)
            clean = re.sub(r'_+', '_', clean).strip('_')
            return f"{clean}.{extension}" if clean else f"FORENSIC_DOSSIER_{time.strftime('%Y%m%d')}.{extension}"

        # Clean words from title
        clean_text = re.sub(r'[^a-zA-Z0-9\s_-]', ' ', case_title or "Case")
        raw_words = [w for w in clean_text.split() if w]
        # Keep meaningful words up to 6 words max
        selected_words = []
        for w in raw_words:
            if len(selected_words) < 6:
                selected_words.append(w.capitalize())

        short_title = "_".join(selected_words) if selected_words else "Case_Investigation"
        date_str = time.strftime("%Y%m%d")
        return f"FORENSIC_DOSSIER_{short_title}_{date_str}.{extension}"

    @classmethod
    def rename_existing_dossier(cls, current_file_path: str, new_name: str) -> str:
        """
        Renames an existing dossier file to a user-specified professional name.
        """
        p = Path(current_file_path)
        if not p.exists():
            return current_file_path
        
        clean_name = cls.clean_professional_filename("", custom_filename=new_name, extension=p.suffix.lstrip("."))
        new_path = p.parent / clean_name
        if p != new_path:
            p.rename(new_path)
        return str(new_path.resolve().as_posix())

    @classmethod
    def export_case_dossier(
        cls,
        case_title: str,
        category: str,
        raw_narrative: str,
        scorecard: Dict[str, Any],
        agent_analysis: str,
        officer_name: str = "Forensic Field Investigator",
        badge_id: str = "BADGE-4892",
        custom_filename: str = ""
    ) -> str:
        """
        Creates a structured markdown file with a clean professional filename and returns the file path.
        """
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        filename = cls.clean_professional_filename(case_title=case_title, custom_filename=custom_filename, extension="md")
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
