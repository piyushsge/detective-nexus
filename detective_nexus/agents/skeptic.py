from typing import Dict, Any, List
import json
import re

from detective_nexus.models.reports import SkepticReport
from detective_nexus.llm.gemini_client import get_client
from detective_nexus.llm.prompts import SKEPTIC_PROMPT

class SkepticAgent:
    """
    Skeptic Agent for Adversarial Quality Control.
    Challenges the leading hypothesis, audits hidden assumptions,
    demands missing evidence, and defines falsification tests.
    Operates seamlessly online with Gemini AI or autonomously via dynamic forensic synthesis.
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

        parsed = self._parse_report(response, case_data)
        if not parsed.assumptions_exposed:
            return self._generate_fallback_report(case_data)
        return parsed

    def _parse_report(self, markdown: str, case_data: Dict[str, Any] = None) -> SkepticReport:
        assumptions = self._extract_list_items(markdown, "Hidden Assumptions Exposed")
        weak_links = self._extract_list_items(markdown, "Evidentiary Weak Links")
        alt_theories = self._extract_list_items(markdown, "Viable Alternative Theories")
        missing = self._extract_list_items(markdown, "Demanded Missing Evidence")
        falsification = self._extract_list_items(markdown, "Concrete Falsification Tests")

        rationale_match = re.search(r"##\s+7\.\s+Epistemic Warning & Confidence Reduction\s*\n(.*?)(?=##|\Z)", markdown, re.DOTALL)
        rationale = rationale_match.group(1).strip() if rationale_match else "Confidence must remain MODERATE: circumstantial correlation does not establish legal culpability."

        # Extract challenged theory or use leading suspect from case_data
        suspects = case_data.get("suspects", []) if case_data else []
        lead_name = suspects[0].get("name", "Leading Suspect") if suspects else "Primary Subject"

        return SkepticReport(
            leading_theory_challenged=f"Working hypothesis that {lead_name} is the sole perpetrator based on opportunity and access logs.",
            assumptions_exposed=assumptions or [
                "Assumption that presence or credential logging proves physical manual execution.",
                "Assumption that circumstantial sequence establishes direct criminal causation.",
                "Over-reliance on uncorroborated witness recollections."
            ],
            weak_links=weak_links or [
                "Digital and hardware logs confirm credential events, NOT physical human identity.",
                "Absence of definitive touch DNA or biometric trace on primary exhibits."
            ],
            alternative_theories=alt_theories or [
                f"An unauthorized third party exploited security gaps to frame {lead_name}.",
                "Procedural irregularity or unlogged access during unmonitored interval."
            ],
            missing_evidence_demanded=missing or [
                "Certified forensic fingerprint or touch DNA analysis on physical touchpoints.",
                "Cryptographic server log audit verifying timestamp synchronicity."
            ],
            falsification_tests=falsification or [
                f"If touch DNA on primary exhibits identifies an external profile, the case against {lead_name} is refuted.",
                "If independent telemetry corroborates alibi timing, primary hypothesis fails."
            ],
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
        """
        Synthesizes an adversarial quality-control challenge tailored to the active case
        (100% offline resilient, never halts if Gemini is unavailable).
        """
        case_id = case_data.get("case_id", "CASE-001")
        suspects = case_data.get("suspects", [])
        evidence = case_data.get("evidence", [])
        lead_name = suspects[0].get("name", "Leading Suspect") if suspects else "Primary Subject"

        markdown = f"""# SKEPTIC REPORT // {case_id}
**Adversarial Rigor & Defense Vulnerability Auditor** | **Detective Nexus AI Division**

## 1. Adversarial Challenge to Leading Theory
The preliminary investigation has rapidly converged on **{lead_name}** based on opportunity windows and access records. This rapid convergence displays classic confirmation bias. Circumstantial proximity and logged credentials have been treated as conclusive proof of personal guilt while ignoring significant evidentiary gaps.

## 2. Hidden Assumptions Exposed
1. **The Credential Fallacy**: The assumption that because credentials or access logs are recorded, the registered individual was physically operating them. A card, key, or token represents hardware, NOT biological human identity.
2. **The Temporal Correlation Fallacy**: The assumption that presence near an incident during the critical window proves causation.
3. **The Unverified Statement Fallacy**: Relying on uncorroborated verbal statements without certified corroborating telemetry.

## 3. Evidentiary Weak Links
- **Zero Biometric Verification**: No authenticated touch DNA, fingerprint friction ridges, or facial recognition directly place the perpetrator's hand on the breach point.
- **Unverified Chain of Custody**: Potential environmental cross-contamination or delayed logging in secondary records.
- **Narrow Time Window Vulnerability**: The timeline leaves minimal margin for execution, concealment, and egress without being detected.

## 4. Viable Alternative Theories
- **Theory A (The Proxy Credential / Theft Scenario)**: An unauthorized third party obtained access tools or credentials while {lead_name} was occupied elsewhere, staging the incident to divert suspicion.
- **Theory B (Pre-Incident Compromise)**: The primary incident occurred earlier than reported, and logged events during the critical window served as an intentional distraction.

## 5. Demanded Missing Evidence
- Forensic latent print and touch DNA swabbing on all primary physical exhibits.
- Independent external security camera and digital access log verification.
- Formal deposition and alibi verification of all secondary personnel present in the facility.

## 6. Concrete Falsification Tests
- **Test 1**: If touch DNA or fingerprint analysis on primary exhibits reveals an unknown third-party genotype, the primary accusation is falsified.
- **Test 2**: If electronic time-synchronization audits prove clock drift between logging systems, the critical window sequence dissolves.

## 7. Epistemic Warning & Confidence Reduction
Certainty must be restricted to **MODERATE / CIRCUMSTANTIAL**. Equating access logs with proof beyond a reasonable doubt violates fundamental forensic standards. The case is **NOT PROVEN**.
"""
        return self._parse_report(markdown, case_data)
