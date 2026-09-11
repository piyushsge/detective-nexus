"""
Case Variation Engine for Counterfactual Mystery Experiments.
Allows removing specific evidence, adding misleading witnesses,
altering timeline timestamps, and comparing before-and-after reasoning.
"""

import copy
from typing import Dict, Any, List, Tuple


def create_case_variation(
    base_case: Dict[str, Any],
    variation_type: str,
    target_id: str = "",
    custom_note: str = "",
) -> Tuple[Dict[str, Any], str]:
    """
    Produces a modified case instance based on specified counterfactual changes:
    - 'remove_evidence': Deletes an evidence item by its evidence_id.
    - 'strengthen_alibi': Alters suspect's alibi to be airtight.
    - 'weaken_alibi': Adds doubt to suspect's alibi statement.
    - 'add_misleading_witness': Inserts a witness giving contradictory account.
    - 'remove_camera_footage': Strips any camera/CCTV evidence items.
    """
    mod_case = copy.deepcopy(base_case)
    mod_case["caseId"] = f"{base_case.get('caseId', 'CASE')}-VAR"
    mod_case["title"] = f"{base_case.get('title', 'Case')} (Variation)"

    description = ""

    if variation_type == "remove_evidence":
        eid_to_remove = target_id.strip() or "E-E"
        original_ev = mod_case.get("evidence", [])
        filtered_ev = [e for e in original_ev if e.get("evidence_id") != eid_to_remove]
        mod_case["evidence"] = filtered_ev
        description = f"Removed Evidence Item '{eid_to_remove}' from the case file."

    elif variation_type == "remove_camera_footage":
        original_ev = mod_case.get("evidence", [])
        filtered_ev = [
            e
            for e in original_ev
            if "camera" not in e.get("title", "").lower()
            and "cctv" not in e.get("title", "").lower()
            and "footage" not in e.get("description", "").lower()
        ]
        mod_case["evidence"] = filtered_ev
        description = "Removed all camera footage and CCTV visual recordings."

    elif variation_type == "strengthen_alibi":
        suspect_name = target_id.strip()
        for s in mod_case.get("suspects", []):
            if suspect_name.lower() in s.get("name", "").lower():
                s["supporting_evidence"].append(
                    "Biometric scan verified physical presence 15 miles away with independent supervisor co-signature."
                )
                s["statement"] += " [Independently verified by tamper-proof biometric logs]."
                description = f"Strengthened alibi for suspect '{s.get('name')}': airtight corroboration added."
                break

    elif variation_type == "weaken_alibi":
        suspect_name = target_id.strip()
        for s in mod_case.get("suspects", []):
            if suspect_name.lower() in s.get("name", "").lower():
                s["suspicious_evidence"].append(
                    "Witness reported the keycard or phone was left behind on a desk while the suspect stepped out unmonitored."
                )
                description = f"Weakened alibi for suspect '{s.get('name')}': proxy device discrepancy introduced."
                break

    elif variation_type == "add_misleading_witness":
        new_witness = {
            "witness_id": f"W-VAR-{len(mod_case.get('witnesses', [])) + 1}",
            "name": "Anonymous Bystander",
            "statement": custom_note
            or "Reported seeing a shadowy figure in a long grey coat running toward the east exit clutching a metallic container.",
            "reliability": "Low",
        }
        mod_case.setdefault("witnesses", []).append(new_witness)
        description = f"Added misleading eyewitness '{new_witness['name']}' with unverified report."

    else:
        description = "No modifications applied."

    return mod_case, description
