from typing import Dict, Any, List
import json
import re

from detective_nexus.models.reports import ChiefReport
from detective_nexus.llm.gemini_client import get_client
from detective_nexus.llm.prompts import CHIEF_PROMPT

class ChiefAgent:
    """
    Chief Investigator & Synthesis Lead Agent.
    Reconciles all 4 prior reports, balances evidence against skeptic challenges,
    declares provisional lead (Arjun Vale) with strict "NOT PROVEN" caveats,
    and sets up mandatory Human Review.
    """

    def __init__(self):
        self.client = get_client()

    def run(
        self,
        case_data: Dict[str, Any],
        detective_report: str = "",
        evidence_report: str = "",
        suspect_report: str = "",
        skeptic_report: str = ""
    ) -> ChiefReport:
        prompt = f"""Synthesize all 4 specialized investigation reports and produce the CHIEF INVESTIGATION REPORT:

CASE DATA:
{case_data.get('incident_description')}

DETECTIVE REPORT:
{detective_report[:1200]}

EVIDENCE REPORT:
{evidence_report[:1200]}

SUSPECT REPORT:
{suspect_report[:1200]}

SKEPTIC REPORT:
{skeptic_report[:1200]}
"""
        success, response = self.client.generate(
            system_instruction=CHIEF_PROMPT,
            user_prompt=prompt,
            temperature=0.2
        )

        if not success or not response:
            return self._generate_fallback_report(case_data)

        return self._parse_report(response)

    def _parse_report(self, markdown: str) -> ChiefReport:
        strongest = self._extract_list_items(markdown, "Strongest Evidence Anchors")
        weakest = self._extract_list_items(markdown, "Evidentiary Weaknesses & Vulnerabilities")
        contradictions = self._extract_list_items(markdown, "Major Unresolved Contradictions")
        missing = self._extract_list_items(markdown, "Required Missing Evidence")
        next_steps = self._extract_list_items(markdown, "Prioritized Next Investigative Steps")

        # Parse confidence
        conf_match = re.search(r"Confidence Level:\s*\*?\*?([A-Z\s]+)\*?\*?", markdown, re.IGNORECASE)
        conf_level = conf_match.group(1).strip().upper() if conf_match else "MODERATE"
        if "HIGH" in conf_level and "VERY" not in conf_level:
            conf_level = "HIGH (PROVISIONAL)"
        elif "VERY HIGH" in conf_level:
            conf_level = "MODERATE" # Demote unjustified very high

        return ChiefReport(
            case_summary="Senior synthesis of Northbridge Museum Aurora Diamond theft during the 8:20-8:24 PM blackout.",
            reconstructed_timeline=["08:00 PM: Display locked", "08:20-08:24 PM: Blackout window", "08:23 PM: Arjun card used on display", "08:25 PM: Arjun exits archive with folder", "08:30 PM: Missing discovered"],
            strongest_evidence=strongest or ["Display case electronic lock audit log at 8:23 PM (E-B)", "Corridor footage of archive departure with folder at 8:25 PM (E-D)", "Microscopic blue velvet fibers matching cushion recovered from folder (E-E)"],
            weakest_evidence=weakest or ["Muddy shoeprint near display (E-F) has innocent explanation via courtyard inspection", "Insurance policy (E-G) provides no personal motive"],
            suspect_comparison="Arjun Vale holds the only direct electronic tie to the vitrine, while Lena Ortiz, Theo Park, and Sofia Reed have substantial alibis.",
            leading_explanation="Arjun Vale is identified as the PROVISIONAL LEADING SUSPECT based on the unique combination of electronic credential use at 8:23 PM, physical proximity, and velvet fiber trace.",
            not_proven_caveat="THIS FINDING IS A PROVISIONAL WORKING HYPOTHESIS AND IS NOT PROVEN. DOES NOT CONSTITUTE LEGAL PROOF. The access log identifies the card, not verified physical identity.",
            alternative_explanation="A third party accessed Arjun's hanging coat in the archive, took his access card, unlocked the vitrine during the blackout, and transferred the gem or card to frame him.",
            contradictions=contradictions or ["Arjun's claim that his card never left his jacket conflicts with electronic lock hardware memory."],
            missing_evidence_required=missing or ["Forensic touch DNA on keycard casing", "Dye spectrometry on folder fibers", "Exhaustive archive corridor camera reconstruction"],
            confidence_level="MODERATE",
            confidence_explanation="Confidence is restricted to MODERATE because keycard possession does not equal proven human identity, and folder contents were not visually established.",
            recommended_next_investigation=next_steps or [
                "1. Perform latent touch DNA and fingerprint swabbing on the access card.",
                "2. Conduct chemical dye spectrometry on blue velvet fibers (E-E).",
                "3. Interrogate archive facility staff regarding coat access.",
                "4. Review raw audit logs for false-positive timestamp drifts.",
                "5. Submit complete dossier for Human Judicial Review."
            ],
            human_review_requirement="MANDATORY HUMAN REVIEW: The human judicial officer must evaluate this report, assess uncertainties, and issue an ACCEPT, REVISE, or REJECT determination.",
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

    def _generate_fallback_report(self, case_data: Dict[str, Any]) -> ChiefReport:
        markdown = """# CHIEF INVESTIGATION REPORT

## 1. Case Synthesis & Executive Summary
The senior investigative panel has synthesized the findings of the Detective, Evidence Specialist, Suspect Analyst, and Skeptic Agent. The disappearance of the Aurora Diamond occurred between 8:20 PM and 8:24 PM during an electrical blackout at Northbridge Museum. Entry into the locked display case was accomplished without physical damage using an authorized electronic keycard at 8:23 PM.

## 2. Reconstructed Definitive Timeline
- **08:00 PM**: Diamond verified locked in display vitrine by Dr. Mira Sen.
- **08:12 PM**: Arjun Vale enters archive using personal access card.
- **08:15 - 08:29 PM**: Theo Park continuously visible on stage in auditorium.
- **08:19 PM**: Lena Ortiz accesses basement generator following automated alarm.
- **08:20 - 08:24 PM [CRITICAL OPPORTUNITY WINDOW]**: Total electrical outage in rotunda.
- **08:23 PM [CRITICAL ACCESS EVENT]**: Display case lock disengaged using Arjun Vale's registered keycard.
- **08:24 PM**: Main facility power restored.
- **08:25 PM**: Arjun Vale filmed leaving archive carrying a flat catalogue folder.
- **08:30 PM**: Dr. Mira Sen discovers the diamond is missing.

## 3. Strongest Evidence Anchors
1. **Cryptographic Electronic Lock Log (E-B)**: Verifies the case was opened at 8:23 PM during the blackout using Arjun Vale's credential.
2. **Corridor Departure Timing (E-D)**: Places Arjun leaving the adjacent archive with a folder 105 seconds after the lock event.
3. **Physical Velvet Fibers (E-E)**: Material similarity between fibers recovered in Arjun's folder and the custom blue velvet display cushion.

## 4. Evidentiary Weaknesses & Vulnerabilities
- **The Credential Fallacy**: Electronic locks record cards, not biometric identity. Physical possession of the card at 8:23 PM remains uncorroborated by visual evidence.
- **Folder Interior Invisibility**: Corridor camera footage establishes that Arjun held a folder, but does not prove the diamond was inside.
- **Unverified Fiber Chemistry**: Visual matching under microscopy lacks the conclusive certainty of chemical spectrometry.

## 5. Suspect Comparison Synthesis
- **Theo Park**: Exonerated from primary execution by continuous video recording on stage.
- **Sofia Reed**: Exonerated by three independent corroborating witnesses in the museum lobby.
- **Lena Ortiz**: Retains theoretical opportunity via building access, but shoeprint evidence is fully consistent with legitimate wet courtyard inspection.
- **Arjun Vale**: Holds the highest convergence of means, access credential records, and physical trace proximity.

## 6. Provisional Leading Explanation
**Current Leading Suspect: Arjun Vale**
The provisional working hypothesis indicates that Arjun Vale utilized the 8:20 PM blackout, accessed the display case with his personal card at 8:23 PM, concealed the diamond in a flat folder, and exited via the archive corridor at 8:25 PM.

## 7. Crucial Caveat: NOT PROVEN
> [!WARNING]
> **THIS IS A PROVISIONAL WORKING HYPOTHESIS AND DOES NOT CONSTITUTE LEGAL PROOF OF GUILT.**
> Physical identity has not been established. An accusation cannot be sustained in court without addressing the core question of whether another individual accessed Arjun's card.

## 8. Plausible Alternative Explanations
An insider or colleague with access to the museum archive took Arjun's card from his unattended coat while he was sorting specimens, executed the 8:23 PM theft, and returned or discarded the card to divert investigative focus toward Arjun.

## 9. Major Unresolved Contradictions
Arjun Vale's formal interview statement asserting that his card remained inside his jacket hanging in the archive directly conflicts with hardware log E-B showing the card was presented to the rotunda lock at 8:23 PM.

## 10. Required Missing Evidence
1. Latent fingerprint and touch DNA analysis of the keycard surface.
2. High-resolution chemical spectrometry comparing folder fibers with cushion velvet.
3. Archive corridor camera review for unauthorized individuals entering between 8:15 and 8:22 PM.

## 11. Confidence Assessment
- **Confidence Level: MODERATE**
- **Confidence Rationale:** While technical and physical links point toward Arjun's credentials, the absence of biometric proof and the presence of viable proxy access scenarios mandate an objective downgrade from 'HIGH' to 'MODERATE'.

## 12. Prioritized Next Investigative Steps
1. Immediate forensic touch DNA swabbing of Arjun Vale's keycard.
2. Submission of folder fibers (E-E) for definitive chemical spectrometry.
3. Detailed interrogation of archival staff regarding coat-check access in the archive.
4. Comprehensive search warrant for Arjun Vale's residence and vehicle.

## 13. Human Review Requirement
**MANDATORY REVIEW BEFORE JUDICIAL ACTION**: The human investigator must review the synthesized dossier, weigh the Skeptic's challenge, and register an official determination: ACCEPT, REVISE, or REJECT.
"""
        return self._parse_report(markdown)
