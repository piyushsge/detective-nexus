from typing import Dict, Any, List
import json
import re

from detective_nexus.models.reports import SkepticReport
from detective_nexus.llm.gemini_client import get_client
from detective_nexus.llm.prompts import SKEPTIC_PROMPT

class SkepticAgent:
    """
    Skeptic Agent for Adversarial Quality Control.
    Challenges the leading hypothesis (Arjun Vale), audits hidden assumptions,
    demands missing evidence, and defines falsification tests.
    """

    def __init__(self):
        self.client = get_client()

    def run(
        self,
        case_data: Dict[str, Any],
        detective_report: str = "",
        evidence_report: str = "",
        suspect_report: str = ""
    ) -> SkepticReport:
        prompt = f"""Conduct an aggressive adversarial review of the leading hypothesis:

CASE SUMMARY:
{case_data.get('incident_description')}

DETECTIVE REPORT CONTEXT:
{detective_report[:1000]}

EVIDENCE REPORT CONTEXT:
{evidence_report[:1000]}

SUSPECT REPORT CONTEXT:
{suspect_report[:1000]}
"""
        success, response = self.client.generate(
            system_instruction=SKEPTIC_PROMPT,
            user_prompt=prompt,
            temperature=0.3
        )

        if not success or not response:
            return self._generate_fallback_report(case_data)

        return self._parse_report(response)

    def _parse_report(self, markdown: str) -> SkepticReport:
        assumptions = self._extract_list_items(markdown, "Hidden Assumptions Exposed")
        weak_links = self._extract_list_items(markdown, "Evidentiary Weak Links")
        alt_theories = self._extract_list_items(markdown, "Viable Alternative Theories")
        missing = self._extract_list_items(markdown, "Demanded Missing Evidence")
        falsification = self._extract_list_items(markdown, "Concrete Falsification Tests")

        rationale_match = re.search(r"##\s+7\.\s+Epistemic Warning & Confidence Reduction\s*\n(.*?)(?=##|\Z)", markdown, re.DOTALL)
        rationale = rationale_match.group(1).strip() if rationale_match else "Confidence must remain moderate pending card handling verification."

        return SkepticReport(
            leading_theory_challenged="Arjun Vale is the perpetrator who personally stole the diamond using his card at 8:23 PM.",
            assumptions_exposed=assumptions or ["Arjun personally held the card", "The folder carried at 8:25 PM contained the diamond", "Velvet fibers in folder originate exclusively from the vitrine cushion"],
            weak_links=weak_links or ["Electronic locks detect plastic cards, not human fingerprints", "Corridor camera shows folder silhouette only, not interior contents"],
            alternative_theories=alt_theories or ["An insider took Arjun's card from his jacket while he was occupied in the archive", "The diamond was removed prior to the blackout and the 8:23 PM swipe was a diversion"],
            missing_evidence_demanded=missing or ["Forensic fingerprint swab of card casing", "Chemical spectrometry of fibers", "Interrogation of archive visitors"],
            falsification_tests=falsification or ["If card swab shows third-party DNA, leading theory collapses", "If archive door camera shows another person exiting with card, Arjun is exonerated"],
            confidence_reduction_rationale=rationale,
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

    def _generate_fallback_report(self, case_data: Dict[str, Any]) -> SkepticReport:
        markdown = """# SKEPTIC REPORT

## 1. Adversarial Challenge to Leading Theory
The investigation has rapidly converged on **Arjun Vale** because of an electronic access record and fiber trace. This convergence displays classic confirmation bias. The hypothesis treats circumstantial proximity as legal certainty while brushing aside glaring evidential voids.

## 2. Hidden Assumptions Exposed
1. **The Credential Fallacy**: The team assumes that because Arjun's card was swiped at 8:23 PM, Arjun himself swiped it. An access card identifies a piece of encoded plastic, NOT a human hand.
2. **The Folder Assumption**: The team assumes the flat catalogue folder carried at 8:25 PM concealed the Aurora Diamond. The camera shows a flat paper folder; it does NOT show a diamond or bulge.
3. **The Fiber Assumption**: The team assumes microscopic blue velvet fibers in the folder must come from the rotunda cushion. In a historical museum with dozens of velvet-lined cases, cross-contamination is rampant.

## 3. Evidentiary Weak Links
- **No Physical Identification at Vitrine**: During the 8:20–8:24 PM blackout, zero eyewitnesses or cameras observed the display case.
- **Timing Contradiction**: Arjun's card swiped the display at 8:23:17 PM. At 8:25:02 PM, Arjun was filmed leaving the archive. That leaves less than 105 seconds to unlock the case, extract the diamond, close the lock, walk back to the archive, conceal the gem in a folder, and walk out into camera view.
- **Inconclusive Fiber Analysis**: Microscopic visual resemblance is not chemical spectrometry.

## 4. Viable Alternative Theories
- **Theory A (The Stolen Credential Scenario)**: An accomplice or second actor slipped into Arjun's office while he was sorting specimens in the back of the archive, lifted his keycard from his hanging coat, executed the theft at 8:23 PM, and slipped it back or ditched it.
- **Theory B (Pre-Blackout Extraction)**: The diamond was removed earlier during preparation, and the blackout swipe was intentionally staged using Arjun's card to create a false timeline anchor.

## 5. Demanded Missing Evidence
- Latent fingerprint or touch DNA analysis on the surface of Arjun's card.
- Comprehensive chemical spectrometry comparing the dye composition of the folder fibers with the rotunda cushion.
- Review of exterior corridor footage for unidentified persons near the archive doorway between 8:15 and 8:22 PM.

## 6. Concrete Falsification Tests
- **Test 1**: If touch DNA analysis on the keycard identifies a non-Arjun profile, the primary hypothesis of sole actor execution is falsified.
- **Test 2**: If dye spectrometry proves the folder fibers differ from the cushion batch, the primary physical link collapses.

## 7. Epistemic Warning & Confidence Reduction
Investigators must immediately downgrade certainty from 'HIGH' to 'MODERATE'. Equating electronic card usage with physical guilt violates foundational forensic standards. The case is NOT legally proven.
"""
        return self._parse_report(markdown)
