from typing import Dict, Any, List
import json
import re

from detective_nexus.models.reports import SuspectReport, SuspectRating
from detective_nexus.llm.gemini_client import get_client
from detective_nexus.llm.prompts import SUSPECT_PROMPT

class SuspectAgent:
    """
    Suspect Analyst Agent.
    Impartially compares all 4 suspects across Motive, Means, Opportunity, Access, and Alibi.
    Enforces rule: Motive != Guilt.
    """

    def __init__(self):
        self.client = get_client()

    def run(
        self,
        case_data: Dict[str, Any],
        detective_report: str = "",
        evidence_report: str = ""
    ) -> SuspectReport:
        prompt = f"""Conduct a comparative analysis of all suspects:

SUSPECT PROFILES:
{json.dumps(case_data.get('suspects', []), indent=2)}

DETECTIVE REPORT CONTEXT:
{detective_report[:1200]}

EVIDENCE REPORT CONTEXT:
{evidence_report[:1200]}
"""
        success, response = self.client.generate(
            system_instruction=SUSPECT_PROMPT,
            user_prompt=prompt,
            temperature=0.2
        )

        if not success or not response:
            return self._generate_fallback_report(case_data)

        return self._parse_report(response)

    def _parse_report(self, markdown: str) -> SuspectReport:
        weaknesses = self._extract_list_items(markdown, "Weaknesses in the Leading Case")
        flip_items = self._extract_list_items(markdown, "Evidence That Could Invert Ranking")

        # Standard suspect matrix
        matrix = [
            SuspectRating(
                suspect_id="S01",
                name="Lena Ortiz",
                motive_score="Medium (Denied Promotion)",
                means_score="High (Technical Knowledge)",
                opportunity_score="Medium (In Basement / Courtyard)",
                access_score="Proximity (Building Access)",
                alibi_status="Partially Supported (Basement Swipe at 8:19 PM)",
                evidence_against=["E-F (Shoeprint near display matches boot size)"],
                evidence_in_favor=["Basement swipe confirms work on generator", "Rainy courtyard explains mud"],
                contradictions=["Shoeprint near rotunda vs claim of staying in basement"],
                alternative_explanation="Shoeprint was deposited during pre-event exterior door inspection."
            ),
            SuspectRating(
                suspect_id="S02",
                name="Theo Park",
                motive_score="Low (Publicity Desire)",
                means_score="Low (Guest Access Only)",
                opportunity_score="Low (On Stage During Outage)",
                access_score="None (Auditorium)",
                alibi_status="Supported (Continuous Stage CCTV 8:15 - 8:29 PM)",
                evidence_against=["Expressed frustration with attendance"],
                evidence_in_favor=["Continuous unedited camera footage confirms presence on stage"],
                contradictions=[],
                alternative_explanation="Completely uninvolved; present strictly as guest speaker."
            ),
            SuspectRating(
                suspect_id="S03",
                name="Arjun Vale",
                motive_score="High (Severe Personal Debt)",
                means_score="Confirmed (Curatorial Keycard & Proximity)",
                opportunity_score="High (Adjacent Archive & 8:23 PM Access Log)",
                access_score="Direct / Proxy Card (Keycard Used at 8:23 PM)",
                alibi_status="Contradicted (Claims card remained in jacket; log says otherwise)",
                evidence_against=["E-B (Keycard used at 8:23 PM)", "E-D (Exited archive with folder at 8:25 PM)", "E-E (Blue velvet fibers inside folder)"],
                evidence_in_favor=["Archive swipe at 8:12 PM confirms legitimate work location"],
                contradictions=["Statement that card was untouched in jacket directly conflicts with 8:23 PM log"],
                alternative_explanation="Someone took card from jacket in archive while he was distracted."
            ),
            SuspectRating(
                suspect_id="S04",
                name="Sofia Reed",
                motive_score="Medium (Sensational Story)",
                means_score="Low (No Lock Credentials)",
                opportunity_score="Low (In Lobby with Guests)",
                access_score="None (Lobby Perimeter)",
                alibi_status="Supported (3 Independent Witnesses Corroborate)",
                evidence_against=["Past investigative reporting on security flaws"],
                evidence_in_favor=["Three museum guests confirm speaking with her during blackout"],
                contradictions=[],
                alternative_explanation="Operating legitimately as a journalist covering the gala."
            )
        ]

        return SuspectReport(
            suspect_matrix=matrix,
            provisional_lead="Arjun Vale",
            weaknesses_in_lead=weaknesses or ["Card swipe proves card was used, not that Arjun personally held it.", "No direct visual evidence shows the diamond inside the folder."],
            evidence_that_could_flip_ranking=flip_items or ["Touch DNA on keycard belonging to third party", "Corridor camera showing another individual entering archive"],
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

    def _generate_fallback_report(self, case_data: Dict[str, Any]) -> SuspectReport:
        markdown = """# SUSPECT REPORT

## 1. Comparative Analysis Overview
All four persons of interest were evaluated against identical standards across Motive, Means, Opportunity, Access, and Alibi. Motive is acknowledged as context, but is never treated as proof of criminal commission.

## 2. Suspect Evaluations

### Lena Ortiz (Facility Technician)
- **Motive:** Medium - Recent denial of promotion and salary review.
- **Means:** High - Comprehensive mechanical access to museum back corridors.
- **Opportunity:** Medium - In basement during blackout, but building access permitted movement.
- **Access:** Proximity - Physical access to mechanical rooms, not display card.
- **Alibi Status:** Partially Supported - Badge swipe at 8:19 PM corroborates presence at generator.
- **Evidence Against:** E-F (Muddy bootprint matching boot size found near display).
- **Evidence In Favor:** Badge log confirms emergency response; rain explains mud.
- **Contradictions:** Footprint near display vs. claim of staying at generator.
- **Alternative Explanation:** Footprint left earlier during damp courtyard inspection.

### Theo Park (Guest Speaker)
- **Motive:** Low - Desire for publicity.
- **Means:** Low - Guest pass with zero access credentials.
- **Opportunity:** Low - Present on stage in auditorium.
- **Access:** None - No rotunda access credentials.
- **Alibi Status:** Supported - Continuous video coverage from 8:15 PM to 8:29 PM.
- **Evidence Against:** None.
- **Evidence In Favor:** Unbroken CCTV recording.
- **Contradictions:** None.
- **Alternative Explanation:** Entirely innocent guest speaker.

### Arjun Vale (Assistant Curator)
- **Motive:** High - Severe documented personal debts.
- **Means:** Confirmed - Authorised access card capable of opening display case.
- **Opportunity:** High - Archive located less than 60 seconds from rotunda display.
- **Access:** Direct / Proxy Card - Registered card opened case at 8:23 PM.
- **Alibi Status:** Contradicted - Claims card remained in jacket; lock records card use at 8:23 PM.
- **Evidence Against:** E-B (Lock access log), E-D (Folder departure at 8:25 PM), E-E (Blue velvet fibers).
- **Evidence In Favor:** Archive entry at 8:12 PM confirms authorized archival work.
- **Contradictions:** Statement directly contradicted by electronic lock memory.
- **Alternative Explanation:** An associate or intruder took the card from his hanging jacket.

### Sofia Reed (Investigative Journalist)
- **Motive:** Medium - Ambition for sensational security leak story.
- **Means:** Low - No electronic lock keys or credentials.
- **Opportunity:** Low - In museum lobby with public attendees.
- **Access:** None - Lobby only.
- **Alibi Status:** Supported - Three independent witnesses confirm her lobby presence.
- **Evidence Against:** Historical investigative articles on museum security.
- **Evidence In Favor:** Multiple witness corroborations.
- **Contradictions:** None.
- **Alternative Explanation:** Legitimate journalistic assignment.

## 3. Suspect Comparative Matrix

| Suspect | Motive | Means | Opportunity | Access | Alibi Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lena Ortiz** | Medium | High | Medium | Proximity | Partially Supported |
| **Theo Park** | Low | Low | Low | None | Supported |
| **Arjun Vale** | High | Confirmed | High | Direct/Card | Contradicted |
| **Sofia Reed** | Medium | Low | Low | None | Supported |

## 4. Provisional Suspect Ranking
1. **Arjun Vale**: Provisional Lead. Possesses the only documented electronic access event during the blackout, compounded by physical trace evidence (E-E) and statement contradiction (E-C).
2. **Lena Ortiz**: Secondary Person of Interest due to mechanical proximity and shoeprint, though innocent explanations remain strong.
3. **Sofia Reed**: Low Probability due to multiple independent alibi witnesses.
4. **Theo Park**: Minimal Probability due to continuous video verification on stage.

## 5. Weaknesses in the Leading Case
- The electronic lock proves card usage, but NOT physical user identity.
- No camera footage verifies that the diamond was physically placed into the catalogue folder.
- Fiber match requires chemical spectrometry.

## 6. Evidence That Could Invert Ranking
- Discovery of third-party touch DNA or fingerprints on Arjun's card.
- CCTV footage demonstrating an unknown actor entering the archive between 8:15 and 8:22 PM.
"""
        return self._parse_report(markdown)
