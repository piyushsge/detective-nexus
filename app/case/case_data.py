"""
Structured Case File System for AI Mystery Detective Team.
Case: The Vanishing Aurora Diamond (CASE-AURORA-001)

Part 2 — Structured Case Data Layer.
Designed for multi-agent ingestion with complete separation between
agent-visible evidence and internal facilitator guidance.
"""

from typing import Any, Dict, List

# ==================================================
# 1. CASE IDENTITY & INCIDENT
# ==================================================

CASE_METADATA: Dict[str, str] = {
    "case_id": "CASE-AURORA-001",
    "title": "The Vanishing Aurora Diamond",
    "case_type": "Fictional Museum Theft Mystery",
    "location": "Northbridge Museum",
    "status": "Ready for AI investigation"
}

CASE_DESCRIPTION: str = (
    "At 8:00 PM, curator Dr. Mira Sen displayed the Aurora Diamond in a locked "
    "glass display case at Northbridge Museum.\n\n"
    "At 8:20 PM, the museum experienced a power failure lasting until 8:24 PM.\n\n"
    "At 8:30 PM, the diamond was discovered missing.\n\n"
    "The glass case remained intact with no obvious forced entry.\n\n"
    "The electronic lock has battery backup and continued recording valid "
    "authorized-card access during the power failure.\n\n"
    "The exact moment when the diamond was removed is not directly established."
)

# ==================================================
# 2. CENTRAL INVESTIGATION QUESTIONS
# ==================================================

CENTRAL_QUESTIONS: List[str] = [
    "Who removed the Aurora Diamond?",
    "How was the display case opened during the blackout?",
    "Who had access to the display case?",
    "Did the person whose access card was used actually use the card?",
    "Which evidence is direct evidence and which is circumstantial?",
    "Which suspect has the strongest combination of motive, means, opportunity, and evidence?",
    "What alternative explanations remain possible?",
    "What evidence is still required before reaching a stronger conclusion?"
]

# ==================================================
# 3. INVESTIGATION RULES
# ==================================================

INVESTIGATION_RULES: List[str] = [
    "Motive does not prove guilt.",
    "Access-card usage does not automatically prove that the card owner personally used the card.",
    "Separate FACT from INFERENCE.",
    "Distinguish direct evidence from circumstantial evidence.",
    "Consider all suspects fairly.",
    "Do not ignore evidence that conflicts with a leading theory.",
    "Explicitly identify uncertainty.",
    "Never manufacture missing evidence.",
    "Never present an inference as an established fact.",
    "Important factual claims must reference the relevant evidence or timeline.",
    "Confidence must match the available evidence.",
    "The human reviewer has authority over the final decision."
]

# ==================================================
# 4. TIMELINE (9 EVENTS: T01 - T09)
# ==================================================

TIMELINE_EVENTS: List[Dict[str, Any]] = [
    {
        "id": "T01",
        "time": "8:00 PM",
        "event": "Dr. Mira Sen displays the Aurora Diamond and locks the display case.",
        "source": "Dr. Mira Sen",
        "certainty": "Established",
        "notes": "Display case confirmed locked before the public event commenced."
    },
    {
        "id": "T02",
        "time": "8:12 PM",
        "event": "Arjun Vale's access card opens the archive.",
        "source": "Access record",
        "certainty": "Established",
        "notes": "Card use proves the card was used, not necessarily who physically used it."
    },
    {
        "id": "T03",
        "time": "8:15 PM–8:29 PM",
        "event": "Theo Park is continuously shown on camera on stage.",
        "source": "Camera footage",
        "certainty": "Established",
        "notes": "Continuous video recording confirms presence on stage during this entire interval."
    },
    {
        "id": "T04",
        "time": "8:19 PM",
        "event": "Lena Ortiz says she went to restart the basement generator.",
        "source": "Lena Ortiz statement + basement access",
        "certainty": "Partially supported",
        "notes": "Basement electronic badge log corroborates entry timing."
    },
    {
        "id": "T05",
        "time": "8:20 PM–8:24 PM",
        "event": "Museum power failure.",
        "source": "Case record",
        "certainty": "Established",
        "notes": "Main electrical grid down across gallery floor; battery backups active."
    },
    {
        "id": "T06",
        "time": "8:23 PM",
        "event": "Arjun Vale's access card opens the display case.",
        "source": "Display-case access log",
        "certainty": "Established",
        "notes": "This establishes use of Arjun's card, not necessarily Arjun's identity as the user."
    },
    {
        "id": "T07",
        "time": "8:24 PM",
        "event": "Power is restored.",
        "source": "Case record",
        "certainty": "Established",
        "notes": "Main lights and primary facility systems reactivated."
    },
    {
        "id": "T08",
        "time": "8:25 PM",
        "event": "Camera shows Arjun leaving the archive carrying a flat catalogue folder.",
        "source": "Camera footage",
        "certainty": "Established",
        "notes": "The contents of the folder are not visible."
    },
    {
        "id": "T09",
        "time": "8:30 PM",
        "event": "The Aurora Diamond is discovered missing.",
        "source": "Dr. Mira Sen / case record",
        "certainty": "Established",
        "notes": "The exact removal time is unknown."
    }
]

# ==================================================
# 5. SUSPECTS (4 SUSPECTS: S01 - S04)
# ==================================================

SUSPECTS: List[Dict[str, Any]] = [
    {
        "suspect_id": "S01",
        "name": "Lena Ortiz",
        "role": "Facility Technician",
        "motive": "Recently denied promotion.",
        "statement": "She says she restarted the basement generator from approximately 8:19 PM to 8:26 PM.",
        "relevant_evidence": [
            "Basement access supports part of her account.",
            "She crossed a wet courtyard earlier while inspecting an exterior door.",
            "A muddy shoeprint near the display matches her boot size."
        ],
        "supporting_evidence": [
            "Basement access log confirms badge entry at 8:19 PM."
        ],
        "suspicious_evidence": [
            "Muddy shoeprint matching her footwear profile discovered near the display case."
        ],
        "uncertainty": (
            "The muddy footprint could have resulted from her earlier movement through "
            "the wet courtyard. Do not treat the footprint as proof that Lena entered "
            "the display area during the theft."
        ),
        "open_questions": [
            "When exactly was the shoeprint created?",
            "Could another person have made a similar print?",
            "Is there evidence placing Lena at the display case during the critical window?"
        ]
    },
    {
        "suspect_id": "S02",
        "name": "Theo Park",
        "role": "Visiting Guest Speaker",
        "motive": "Wanted publicity.",
        "statement": "He says he remained on stage and did not enter the gallery.",
        "relevant_evidence": [
            "Camera continuously shows Theo on stage from 8:15 PM to 8:29 PM."
        ],
        "supporting_evidence": [
            "Unbroken auditorium CCTV footage covering the exact theft and blackout interval."
        ],
        "suspicious_evidence": [
            "Expressed public frustration regarding event attention earlier in the evening."
        ],
        "uncertainty": (
            "Continuous video makes it difficult for Theo to physically reach the display case "
            "during the relevant period. However, do not claim the footage proves every possible "
            "form of involvement is impossible."
        ),
        "open_questions": [
            "Does the camera coverage have any blind spots relevant to the investigation?",
            "Does any other evidence connect Theo to the display?"
        ]
    },
    {
        "suspect_id": "S03",
        "name": "Arjun Vale",
        "role": "Assistant Curator & Archivist",
        "motive": "Large private debt.",
        "statement": "He says he was working in the archive and that his access card remained in his jacket inside the archive.",
        "relevant_evidence": [
            "His access card opened the archive at 8:12 PM.",
            "His access card opened the display case at 8:23 PM.",
            "Camera shows him leaving the archive at 8:25 PM.",
            "He was carrying a flat catalogue folder.",
            "Blue velvet fibers were found inside the folder.",
            "The display cushion is blue velvet."
        ],
        "supporting_evidence": [
            "Camera footage confirms he was in the archive area at 8:12 PM and 8:25 PM."
        ],
        "suspicious_evidence": [
            "Access card was logged opening display case during blackout at 8:23 PM.",
            "Blue velvet fibers found inside the catalogue folder he carried."
        ],
        "uncertainty": (
            "The card record does not prove Arjun personally used the card. "
            "The camera does not show the contents of the folder. "
            "The fiber evidence requires proper scientific comparison."
        ),
        "open_questions": [
            "Who physically possessed the card at 8:23 PM?",
            "Could another person access Arjun's jacket?",
            "What exactly was inside the folder?",
            "Are the fibers scientifically consistent with the display cushion?"
        ]
    },
    {
        "suspect_id": "S04",
        "name": "Sofia Reed",
        "role": "Investigative Journalist",
        "motive": "Wanted an exclusive news story.",
        "statement": "She says she was interviewing visitors in the lobby during the blackout.",
        "relevant_evidence": [
            "Three lobby guests independently remember speaking with Sofia during the blackout.",
            "None reported seeing her enter the gallery."
        ],
        "supporting_evidence": [
            "Corroborating witness statements from three unrelated museum visitors."
        ],
        "suspicious_evidence": [
            "Was seen inquiring about gallery security protocols earlier in the day."
        ],
        "uncertainty": (
            "Witness recollection should be considered evidence but not treated as infallible."
        ),
        "open_questions": [
            "Is there camera coverage confirming Sofia's location?",
            "Could she have left the lobby without being noticed?",
            "Is there any physical evidence connecting her to the display?"
        ]
    }
]

# ==================================================
# 6. WITNESSES (5 WITNESS RECORDS: W01 - W05)
# ==================================================

WITNESSES: List[Dict[str, Any]] = [
    {
        "witness_id": "W01",
        "name": "Dr. Mira Sen",
        "role": "Chief Curator",
        "statement": (
            "She inspected and locked the diamond at 8:00 PM. She says she did not reopen "
            "the display case. The electronic lock has battery backup and records valid "
            "authorized-card access during a power failure."
        ),
        "supporting_information": [
            "Lock log confirms secure state established at 8:00 PM.",
            "Electronic lock technical documentation verifies battery backup capability."
        ],
        "limitations": (
            "She did not directly see who opened the display case at 8:23 PM."
        )
    },
    {
        "witness_id": "W02",
        "name": "Lena Ortiz",
        "role": "Facility Technician",
        "statement": (
            "The generator alarm sounded shortly before the blackout. She says she was in "
            "the basement from approximately 8:19 PM to 8:26 PM. She had crossed a wet "
            "courtyard earlier while inspecting an exterior door."
        ),
        "supporting_information": [
            "Basement card swipe recorded at 8:19 PM.",
            "Weather reports confirm heavy rain and damp courtyard ground."
        ],
        "limitations": (
            "Cannot account for movements in the upper gallery during the outage."
        )
    },
    {
        "witness_id": "W03",
        "name": "Theo Park",
        "role": "Guest Speaker",
        "statement": (
            "He remained on stage and did not enter the gallery."
        ),
        "supporting_information": [
            "Continuous camera footage from 8:15 PM to 8:29 PM."
        ],
        "limitations": (
            "Does not have visibility into non-stage areas of the museum."
        )
    },
    {
        "witness_id": "W04",
        "name": "Arjun Vale",
        "role": "Assistant Curator & Archivist",
        "statement": (
            "He says he was working in the archive. He says his access card remained in his "
            "jacket inside the archive. He was later seen leaving the archive carrying a "
            "flat catalogue folder."
        ),
        "supporting_information": [
            "Archive card swipe registered at 8:12 PM.",
            "Camera recorded exit from archive at 8:25 PM."
        ],
        "limitations": (
            "No independent witnesses were inside the private archive with him."
        )
    },
    {
        "witness_id": "W05",
        "name": "Sofia Reed",
        "role": "Journalist",
        "statement": (
            "She says she was interviewing visitors in the lobby during the blackout. "
            "She continued recording. Several guests were with her."
        ),
        "supporting_information": [
            "Three lobby guests independently remember speaking with Sofia during the blackout.",
            "None saw her enter the gallery."
        ],
        "limitations": (
            "Her audio recorder was turned on and off intermittently between interviews."
        )
    }
]

# ==================================================
# 7. EVIDENCE (7 RECORDS: E-A through E-G)
# ==================================================

EVIDENCE: List[Dict[str, Any]] = [
    {
        "evidence_id": "E-A",
        "title": "Electronic Lock Specification",
        "description": "The display case's electronic lock has battery backup and records valid authorized-card access during a power failure.",
        "category": "Technical evidence",
        "source": "Electronic lock specification",
        "establishes": "Authorized-card access can be recorded during the blackout.",
        "does_not_establish": "Which human physically used the card.",
        "related_suspects": ["Arjun Vale"],
        "reliability_notes": "Manufacturer technical documentation verified by facility engineers."
    },
    {
        "evidence_id": "E-B",
        "title": "Display-Case Access Log",
        "description": "Arjun Vale's access card opened the display case at 8:23 PM.",
        "category": "Electronic access record",
        "source": "Display-case access log",
        "establishes": "Arjun's card was used to open the case at 8:23 PM.",
        "does_not_establish": "Arjun personally used the card.",
        "related_suspects": ["Arjun Vale"],
        "reliability_notes": "Cryptographic access log stored on tamper-evident internal lock memory."
    },
    {
        "evidence_id": "E-C",
        "title": "Arjun's Statement",
        "description": "Arjun says his card remained in his jacket inside the archive.",
        "category": "Suspect statement",
        "source": "Arjun Vale",
        "establishes": "This is Arjun's account.",
        "does_not_establish": "That the card actually remained untouched.",
        "related_suspects": ["Arjun Vale"],
        "reliability_notes": "This statement conflicts with the access record and therefore requires investigation."
    },
    {
        "evidence_id": "E-D",
        "title": "Camera Image at 8:25 PM",
        "description": "Camera footage shows Arjun leaving the archive carrying a flat catalogue folder.",
        "category": "Camera evidence",
        "source": "Security camera",
        "establishes": "Arjun was carrying the folder at approximately 8:25 PM.",
        "does_not_establish": "What was inside the folder. It does not prove that the diamond was inside.",
        "related_suspects": ["Arjun Vale"],
        "reliability_notes": "Low-light corridor surveillance camera; clear silhouette but folder interior obscured."
    },
    {
        "evidence_id": "E-E",
        "title": "Blue Velvet Fibers",
        "description": "Blue velvet fibers were found inside Arjun's folder. The display cushion is blue velvet.",
        "category": "Physical evidence",
        "source": "Fiber examination",
        "establishes": "There is a potentially relevant material similarity.",
        "does_not_establish": "That the diamond was inside the folder. Does not establish that Arjun stole the diamond.",
        "related_suspects": ["Arjun Vale"],
        "reliability_notes": "Scientific comparison should be performed before drawing a stronger conclusion."
    },
    {
        "evidence_id": "E-F",
        "title": "Muddy Shoeprint",
        "description": "A muddy shoeprint near the display matches Lena's boot size. Records show Lena had inspected the exterior after crossing a wet courtyard.",
        "category": "Physical evidence",
        "source": "Footwear/scene examination",
        "establishes": "The shoeprint is consistent with Lena's boot size.",
        "does_not_establish": [
            "when the print was made",
            "who actually made it",
            "that Lena entered the display area during the theft",
            "that Lena stole the diamond"
        ],
        "related_suspects": ["Lena Ortiz"],
        "reliability_notes": "Boot tread pattern matches standard museum maintenance footwear distributed to multiple staff."
    },
    {
        "evidence_id": "E-G",
        "title": "Insurance Information",
        "description": "If the diamond remains missing, the insurance arrangement results in payment to the museum rather than a named suspect.",
        "category": "Background/context evidence",
        "source": "Insurance information",
        "establishes": "The insurance arrangement provides contextual information about the loss.",
        "does_not_establish": "Guilt or innocence of any suspect. IMPORTANT: Do not invent a financial motive from this evidence.",
        "related_suspects": [],
        "reliability_notes": "Official museum institutional policy document."
    }
]

# ==================================================
# 8. EVIDENCE RELATIONSHIPS
# ==================================================

EVIDENCE_RELATIONSHIPS: List[Dict[str, str]] = [
    {
        "relationship_id": "REL-01",
        "source": "E-A",
        "target": "E-B",
        "relation_type": "SUPPORTS_INTERPRETATION",
        "description": "E-A (Lock Specification) supports interpretation of E-B (Lock Log validity during blackout)."
    },
    {
        "relationship_id": "REL-02",
        "source": "E-B",
        "target": "E-C",
        "relation_type": "CONFLICTS_WITH",
        "description": "E-B (Display-case logged at 8:23 PM) conflicts with the claim in E-C (Card remained in jacket in archive)."
    },
    {
        "relationship_id": "REL-03",
        "source": "E-D",
        "target": "S03",
        "relation_type": "CONNECTS_TO",
        "description": "E-D connects Arjun to the flat catalogue folder at 8:25 PM."
    },
    {
        "relationship_id": "REL-04",
        "source": "E-E",
        "target": "E-D",
        "relation_type": "MATERIAL_SIMILARITY",
        "description": "E-E connects the folder in E-D to material associated with the display case cushion."
    },
    {
        "relationship_id": "REL-05",
        "source": "E-F",
        "target": "S01",
        "relation_type": "PHYSICAL_RELATION",
        "description": "E-F relates to Lena's footwear profile and courtyard transit."
    }
]

# ==================================================
# 9. FACT / INFERENCE / DISTRACTION CLASSIFICATION
# ==================================================

EVIDENCE_CLASSIFICATIONS: Dict[str, str] = {
    "FACT": "Verified, directly observed, or tamper-evident primary record.",
    "INFERENCE": "Logical deduction or theory derived from facts, but not directly observed.",
    "DISTRACTION": "Information present at the scene that may mislead without proving involvement.",
    "UNCERTAIN": "Information requiring further corroboration or scientific testing."
}


def classify_statement_example(statement_type: str) -> str:
    """Helper describing the distinction between fact and inference for agents."""
    return EVIDENCE_CLASSIFICATIONS.get(statement_type, "UNCERTAIN")


# ==================================================
# 10. AGENT-VISIBLE DATA ACCESSOR & DYNAMIC CASE CONTEXT
# ==================================================

_CURRENT_ACTIVE_CASE_DICT: Dict[str, Any] = {}


def set_active_case(case_dict: Dict[str, Any]) -> None:
    """Sets the currently active mystery case for all agents in the platform."""
    global _CURRENT_ACTIVE_CASE_DICT
    _CURRENT_ACTIVE_CASE_DICT = dict(case_dict) if case_dict else {}


def get_current_raw_case() -> Dict[str, Any]:
    """Returns the full dictionary of the currently active case (or None if default)."""
    return _CURRENT_ACTIVE_CASE_DICT


def get_agent_visible_case() -> Dict[str, Any]:
    """
    Returns the complete structured case data visible to AI detective agents.

    CRITICAL SECURITY & METHODOLOGY RULE:
    This dictionary MUST NEVER contain facilitator-only guidance, expected solutions,
    or pre-determined suspects. AI agents must reason independently from raw evidence.

    Returns:
        Dict[str, Any]: 100% JSON-serializable case structure.
    """
    if _CURRENT_ACTIVE_CASE_DICT:
        # Dynamically sanitize the loaded case
        return {
            "metadata": {
                "case_id": _CURRENT_ACTIVE_CASE_DICT.get("caseId", "CASE-DYNAMIC"),
                "title": _CURRENT_ACTIVE_CASE_DICT.get("title", "Active Mystery"),
                "case_type": f"{_CURRENT_ACTIVE_CASE_DICT.get('difficulty', 'Standard')} {_CURRENT_ACTIVE_CASE_DICT.get('category', 'Mystery')} Case",
                "location": _CURRENT_ACTIVE_CASE_DICT.get("setting", "Location Under Investigation"),
                "difficulty": _CURRENT_ACTIVE_CASE_DICT.get("difficulty", "Medium"),
                "category": _CURRENT_ACTIVE_CASE_DICT.get("category", "General"),
                "status": "Ready for AI investigation"
            },
            "incident_description": _CURRENT_ACTIVE_CASE_DICT.get("incident", ""),
            "central_questions": _CURRENT_ACTIVE_CASE_DICT.get("centralQuestions", list(CENTRAL_QUESTIONS)),
            "investigation_rules": _CURRENT_ACTIVE_CASE_DICT.get("rules", list(INVESTIGATION_RULES)),
            "timeline": [dict(event) for event in _CURRENT_ACTIVE_CASE_DICT.get("timeline", [])],
            "suspects": [dict(suspect) for suspect in _CURRENT_ACTIVE_CASE_DICT.get("suspects", [])],
            "witnesses": [dict(witness) for witness in _CURRENT_ACTIVE_CASE_DICT.get("witnesses", [])],
            "evidence": [dict(item) for item in _CURRENT_ACTIVE_CASE_DICT.get("evidence", [])],
            "evidence_relationships": [dict(rel) for rel in EVIDENCE_RELATIONSHIPS],
            "evidence_classification_guide": dict(EVIDENCE_CLASSIFICATIONS)
        }

    return {
        "metadata": dict(CASE_METADATA),
        "incident_description": CASE_DESCRIPTION,
        "central_questions": list(CENTRAL_QUESTIONS),
        "investigation_rules": list(INVESTIGATION_RULES),
        "timeline": [dict(event) for event in TIMELINE_EVENTS],
        "suspects": [dict(suspect) for suspect in SUSPECTS],
        "witnesses": [dict(witness) for witness in WITNESSES],
        "evidence": [dict(item) for item in EVIDENCE],
        "evidence_relationships": [dict(rel) for rel in EVIDENCE_RELATIONSHIPS],
        "evidence_classification_guide": dict(EVIDENCE_CLASSIFICATIONS)
    }


# ==================================================
# 11. FACILITATOR-ONLY GUIDANCE (HUMAN REVIEW ONLY)
# ==================================================

FACILITATOR_ONLY_GUIDANCE: Dict[str, Any] = {
    "leading_suspect": "Arjun Vale",
    "reasoning": [
        "Arjun's access card opened the display case at 8:23 PM.",
        "Arjun was seen leaving the archive two minutes later (8:25 PM) carrying a flat folder.",
        "Blue velvet fibers were found inside the folder, matching the cushion material.",
        "His statement that his card remained untouched in his jacket conflicts with access records."
    ],
    "preserved_uncertainty": [
        "Card usage does not prove Arjun personally used it.",
        "Camera footage does not show the diamond inside the folder.",
        "Fiber evidence requires scientific comparison.",
        "Another person could potentially have accessed the card.",
        "Additional evidence is required."
    ],
    "potential_next_evidence": [
        "1. Examine the access card for handling evidence and fingerprints.",
        "2. Review archive/corridor footage before and after the blackout.",
        "3. Search the folder and archive thoroughly.",
        "4. Scientifically compare the fibers using spectrometry.",
        "5. Determine whether anyone had physical access to Arjun's jacket/card."
    ]
}

# ==================================================
# 12. CASE SUMMARY & VALIDATION
# ==================================================

def get_case_summary() -> Dict[str, Any]:
    """
    Returns a safe summary of the case for user display and diagnostic verification.
    Does NOT include facilitator-only conclusions.
    """
    return {
        "Case": CASE_METADATA["title"],
        "Case ID": CASE_METADATA["case_id"],
        "Location": CASE_METADATA["location"],
        "Suspects": len(SUSPECTS),
        "Witnesses": len(WITNESSES),
        "Evidence": len(EVIDENCE),
        "Timeline events": len(TIMELINE_EVENTS),
        "Status": CASE_METADATA["status"]
    }


def validate_case() -> Dict[str, Any]:
    """
    Validates structural completeness and security isolation of the case file.

    Returns:
        Dict[str, Any]: {"valid": bool, "errors": List[str]}
    """
    errors: List[str] = []

    # 1. Metadata checks
    if not CASE_METADATA.get("case_id"):
        errors.append("Case ID is missing.")
    if not CASE_METADATA.get("title"):
        errors.append("Title is missing.")
    if not CASE_DESCRIPTION or len(CASE_DESCRIPTION.strip()) < 50:
        errors.append("Case description is missing or too brief.")

    # 2. Questions & Rules checks
    if not CENTRAL_QUESTIONS or len(CENTRAL_QUESTIONS) != 8:
        errors.append(f"Expected exactly 8 central questions, found {len(CENTRAL_QUESTIONS)}.")
    if not INVESTIGATION_RULES or len(INVESTIGATION_RULES) != 12:
        errors.append(f"Expected exactly 12 investigation rules, found {len(INVESTIGATION_RULES)}.")

    # 3. Timeline counts & IDs
    if len(TIMELINE_EVENTS) != 9:
        errors.append(f"Expected exactly 9 timeline events, found {len(TIMELINE_EVENTS)}.")
    timeline_ids = [t["id"] for t in TIMELINE_EVENTS]
    if len(timeline_ids) != len(set(timeline_ids)):
        errors.append("Duplicate timeline IDs detected.")
    expected_timeline = [f"T0{i}" for i in range(1, 10)]
    for tid in expected_timeline:
        if tid not in timeline_ids:
            errors.append(f"Timeline event {tid} missing.")

    # 4. Suspects counts & IDs
    if len(SUSPECTS) != 4:
        errors.append(f"Expected exactly 4 suspects, found {len(SUSPECTS)}.")
    suspect_ids = [s["suspect_id"] for s in SUSPECTS]
    if len(suspect_ids) != len(set(suspect_ids)):
        errors.append("Duplicate suspect IDs detected.")
    expected_suspects = [f"S0{i}" for i in range(1, 5)]
    for sid in expected_suspects:
        if sid not in suspect_ids:
            errors.append(f"Suspect {sid} missing.")

    # 5. Witnesses counts & IDs
    if len(WITNESSES) != 5:
        errors.append(f"Expected exactly 5 witnesses, found {len(WITNESSES)}.")
    witness_ids = [w["witness_id"] for w in WITNESSES]
    if len(witness_ids) != len(set(witness_ids)):
        errors.append("Duplicate witness IDs detected.")
    expected_witnesses = [f"W0{i}" for i in range(1, 6)]
    for wid in expected_witnesses:
        if wid not in witness_ids:
            errors.append(f"Witness {wid} missing.")

    # 6. Evidence counts & IDs
    if len(EVIDENCE) != 7:
        errors.append(f"Expected exactly 7 evidence items, found {len(EVIDENCE)}.")
    evidence_ids = [e["evidence_id"] for e in EVIDENCE]
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("Duplicate evidence IDs detected.")
    expected_evidence = [f"E-{letter}" for letter in ["A", "B", "C", "D", "E", "F", "G"]]
    for eid in expected_evidence:
        if eid not in evidence_ids:
            errors.append(f"Evidence item {eid} missing.")

    # 7. Agent-visible isolation & Anti-Solution-Leak test
    agent_case = get_agent_visible_case()
    if not isinstance(agent_case, dict):
        errors.append("Agent visible case is not a dictionary.")

    # Strict check: Facilitator content must NOT appear in agent-visible data
    agent_case_str = str(agent_case).lower()
    leak_phrases = [
        "leading_suspect",
        "leading suspect",
        "arjun is the leading suspect",
        "arjun vale is guilty",
        "facilitator_only_guidance"
    ]
    for phrase in leak_phrases:
        if phrase in agent_case_str:
            errors.append(f"Security leak detected: '{phrase}' found in agent-visible case data.")

    # 8. Secret leakage check
    if "api_key" in agent_case_str or "aizasy" in agent_case_str:
        errors.append("Security leak detected: API key reference detected in case data.")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
