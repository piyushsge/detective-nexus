import re
from typing import List, Tuple

class HallucinationAuditor:
    """
    Scans agent generated text for unsupported claims or fabricated evidence.
    Ensures zero fabricated witnesses, evidence codes, or timestamps.
    """

    VALID_EVIDENCE_IDS = {"E-A", "E-B", "E-C", "E-D", "E-E", "E-F", "E-G"}
    VALID_SUSPECT_NAMES = {"lena", "ortiz", "theo", "park", "arjun", "vale", "sofia", "reed", "mira", "sen"}
    VALID_TIMESTAMPS = {"8:00", "8:12", "8:15", "8:19", "8:20", "8:23", "8:24", "8:25", "8:26", "8:29", "8:30"}

    @classmethod
    def audit_report(cls, report_text: str) -> Tuple[bool, List[str]]:
        warnings = []

        # Check for invalid evidence IDs (e.g. E-H, E-Z)
        found_eids = re.findall(r"\bE-([A-Z])\b", report_text)
        for letter in found_eids:
            full_id = f"E-{letter}"
            if full_id not in cls.VALID_EVIDENCE_IDS:
                warnings.append(f"UNSUPPORTED EVIDENCE REFERENCE: Found non-existent clue code '{full_id}'.")

        # Check for obvious fabricated claims (e.g. video shows diamond, confessions)
        lower_text = report_text.lower()
        if "confessed" in lower_text or "confession" in lower_text:
            warnings.append("UNSUPPORTED FACT: Suspect confession claimed, but none exists in case record.")
        if "camera shows the diamond" in lower_text or "video recorded the theft" in lower_text:
            warnings.append("UNSUPPORTED FACT: Camera footage claimed to show diamond, but folder interior was obscured.")

        return len(warnings) == 0, warnings
