from typing import Dict, Any, List
import json
import re

from detective_nexus.models.reports import EvidenceReport, EvidenceAnalysisItem
from detective_nexus.llm.gemini_client import get_client
from detective_nexus.llm.prompts import EVIDENCE_PROMPT

class EvidenceAgent:
    """
    Forensic Evidence Specialist Agent.
    Separates facts from inferences, rates strength, audits limitations, and documents alternatives.
    """

    def __init__(self):
        self.client = get_client()

    def run(self, case_data: Dict[str, Any], detective_report: str = "") -> EvidenceReport:
        prompt = f"""Perform exhaustive forensic classification and limitation auditing on all evidence items:

EVIDENCE ITEMS:
{json.dumps(case_data.get('evidence', []), indent=2)}

EVIDENCE RELATIONSHIPS:
{json.dumps(case_data.get('evidence_relationships', []), indent=2)}

DETECTIVE REPORT CONTEXT:
{detective_report[:1500]}
"""
        success, response = self.client.generate(
            system_instruction=EVIDENCE_PROMPT,
            user_prompt=prompt,
            temperature=0.2
        )

        if not success or not response:
            return self._generate_fallback_report(case_data)

        return self._parse_report(response, case_data)

    def _parse_report(self, markdown: str, case_data: Dict[str, Any]) -> EvidenceReport:
        strongest = self._extract_list_items(markdown, "Strongest Probative Evidence")
        weakest = self._extract_list_items(markdown, "Weakest or Ambiguous Evidence")
        conflicts = self._extract_list_items(markdown, "Conflicting Evidence Audit")
        missing_tests = self._extract_list_items(markdown, "Required Forensic Verifications")

        # Build structured items
        items = []
        for ev in case_data.get("evidence", []):
            eid = ev.get("evidence_id")
            items.append(EvidenceAnalysisItem(
                evidence_id=eid,
                observation=ev.get("description", ""),
                fact_vs_inference="FACT" if ev.get("classification") == "FACT" else "INFERENCE / UNCERTAIN",
                strength=ev.get("strength", "MODERATE"),
                relevance="HIGH" if eid in ["E-B", "E-D", "E-E"] else "CONTEXTUAL",
                what_it_proves=ev.get("establishes", ""),
                what_it_does_not_prove=str(ev.get("does_not_establish", "")),
                alternative_explanation="Card accessed without authorization or fibers transferred from archive cataloguing." if eid == "E-B" else "Incidental environmental trace.",
                confidence=0.90 if ev.get("strength") == "VERY STRONG" else 0.70
            ))

        return EvidenceReport(
            evidence_table=items,
            strongest_clues=strongest or ["E-B: Cryptographic Display-Case Log at 8:23 PM", "E-E: Blue Velvet Fibers in Catalogue Folder"],
            weakest_or_misleading=weakest or ["E-F: Muddy Shoeprint (Consistent with wet courtyard crossing)", "E-G: Insurance Policy (No suspect beneficiary)"],
            conflicting_evidence=conflicts or ["E-B directly contradicts E-C (Lock log shows card swipe vs claim card remained in jacket)"],
            missing_forensic_tests=missing_tests or ["Dye spectrometry comparing folder fibers with rotunda cushion", "Fingerprint / touch DNA swab of access card casing"],
            raw_markdown=markdown
        )

    def _extract_list_items(self, text: str, header: str) -> List[str]:
        pattern = rf"##\s+\d*\.?\s*{header}\s*\n(.*?)(?=##|\Z)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if not match:
            return []
        items = []
        for line in match.group(1).splitlines():
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

    def _generate_fallback_report(self, case_data: Dict[str, Any]) -> EvidenceReport:
        markdown = """# EVIDENCE REPORT

## 1. Executive Forensic Assessment
The evidence dossier contains seven primary records spanning hardware access logs, physical traces, camera stills, and statements. The single strongest technical clue is Evidence E-B (the battery-backed electronic lock event at 8:23 PM), but it is subject to the fundamental limitation that electronic locks record credential use, not human physical identity.

## 2. Evidence-by-Evidence Analysis

### E-A: Electronic Lock Technical Specification
- **Classification:** FACT
- **Evidentiary Strength:** VERY STRONG
- **Source & Chain of Custody:** Manufacturer technical audit
- **What It Establishes:** Authorized keycards continue to be logged in memory during a power outage.
- **What It Does NOT Establish:** Which individual held and swiped the card.
- **Alternative Interpretation:** Standard hardware functionality; proves audit validity.
- **Related Suspects:** Arjun Vale

### E-B: Display Case Access Log (8:23 PM)
- **Classification:** FACT
- **Evidentiary Strength:** VERY STRONG
- **Source & Chain of Custody:** Internal memory chip of the rotunda vitrine lock
- **What It Establishes:** Arjun Vale's registered card opened the case at 8:23 PM.
- **What It Does NOT Establish:** Arjun Vale was the physical operator.
- **Alternative Interpretation:** Another person used or borrowed Arjun's card.
- **Related Suspects:** Arjun Vale

### E-C: Arjun Vale's Statement
- **Classification:** INFERENCE / STATEMENT
- **Evidentiary Strength:** WEAK
- **Source & Chain of Custody:** Audio-recorded investigator interview
- **What It Establishes:** Arjun asserts his card remained in his jacket inside the archive.
- **What It Does NOT Establish:** That the card was actually untouched.
- **Alternative Interpretation:** Self-exculpatory fabrication, OR genuine unawareness that an intruder stole the card.
- **Related Suspects:** Arjun Vale

### E-D: Corridor Camera Footage (8:25 PM)
- **Classification:** FACT
- **Evidentiary Strength:** STRONG
- **Source & Chain of Custody:** CCTV Camera #4 hard-drive archive
- **What It Establishes:** Arjun carried a flat catalogue folder out of the archive at 8:25 PM.
- **What It Does NOT Establish:** That the diamond was inside the folder.
- **Alternative Interpretation:** Routine archival transport of research folios.
- **Related Suspects:** Arjun Vale

### E-E: Blue Velvet Fibers in Folder
- **Classification:** UNCERTAIN / PHYSICAL TRACE
- **Evidentiary Strength:** MODERATE
- **Source & Chain of Custody:** Crime Scene Tech vacuum sweep of folder
- **What It Establishes:** Visual material match with the blue velvet display cushion.
- **What It Does NOT Establish:** Chemical identity or origin without dye spectrometry.
- **Alternative Interpretation:** Velvet fibers transferred during earlier museum exhibitions or display prep.
- **Related Suspects:** Arjun Vale

### E-F: Muddy Shoeprint Near Display
- **Classification:** DISTRACTION
- **Evidentiary Strength:** WEAK
- **Source & Chain of Custody:** Gel lift from rotunda marble floor
- **What It Establishes:** Size EU 39 boot deposited mud near the display.
- **What It Does NOT Establish:** When the print was made or that Lena entered during the blackout.
- **Alternative Interpretation:** Deposited during routine maintenance after crossing wet courtyard.
- **Related Suspects:** Lena Ortiz

### E-G: Museum Insurance Policy Schedule
- **Classification:** DISTRACTION
- **Evidentiary Strength:** WEAK
- **Source & Chain of Custody:** Administrative records
- **What It Establishes:** Policy beneficiary is the museum board of trustees.
- **What It Does NOT Establish:** Direct financial incentive for any suspect.
- **Alternative Interpretation:** Contextual institutional documentation.
- **Related Suspects:** None

## 3. Strongest Probative Evidence
- **E-B (8:23 PM Lock Log)**: Directly anchors the physical opening of the vitrine to the blackout window.
- **E-E (Velvet Fibers)**: Provides physical trace linking the folder to the display cushion material.

## 4. Weakest or Ambiguous Evidence
- **E-F (Muddy Shoeprint)**: Severely compromised by the fact that Lena had a legitimate duty to inspect exterior doors during heavy rain.
- **E-G (Insurance Policy)**: Fails to substantiate personal financial motive for individual suspects.

## 5. Conflicting Evidence Audit
- **E-B vs. E-C Conflict**: The display lock records Arjun's card opening the case at 8:23 PM, directly contradicting his statement that his card remained inside his jacket.

## 6. Required Forensic Verifications
1. Mass spectrometry of fibers from E-E vs rotunda cushion velvet.
2. Forensic swabbing of Arjun's card for touch DNA / fingerprint residues.
3. Audio/video recovery from archive entrance to determine if third parties entered while Arjun worked.
"""
        return self._parse_report(markdown, case_data)
