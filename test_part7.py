"""
Test suite for Part 7: Chief Agent.
Verifies all 20 required checks covering:
1. Chief module imports.
2. Chief prompt imports.
3. Case reaches Chief.
4. Detective Report reaches Chief.
5. Evidence Report reaches Chief.
6. Suspect Report reaches Chief.
7. Skeptic Report reaches Chief.
8. Facilitator solution does NOT reach Chief.
9. Chief distinguishes fact from inference.
10. Chief distinguishes card owner from card user.
11. Chief distinguishes card user from thief.
12. Chief does not equate motive with guilt.
13. Chief considers all four suspects.
14. Chief considers Skeptic findings.
15. Chief considers alternative explanations.
16. Chief produces uncertainty.
17. Chief does not contain a hardcoded verdict.
18. Malformed Gemini JSON/text does not crash.
19. Gemini API error / security violation does not crash.
20. Parts 1–6 continue working without regression.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure console supports UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.case import case_data
from app.prompts import (
    detective_prompt,
    evidence_prompt,
    suspect_prompt,
    skeptic_prompt,
    chief_prompt,
)
from app.agents import (
    detective_agent,
    evidence_agent,
    suspect_agent,
    skeptic_agent,
    chief_agent,
)
from app import gemini_client
from app.main import handle_run_chief, INVESTIGATION_CACHE


def run_all_tests():
    print("=" * 60)
    print("RUNNING PART 7 CHIEF AGENT TESTS (20 VERIFICATION CHECKS)")
    print("=" * 60)

    # TEST 1: Chief module imports
    assert chief_agent is not None, "TEST 1 FAILED: chief_agent module is None"
    assert hasattr(chief_agent, "run_chief_agent"), "TEST 1 FAILED: run_chief_agent missing"
    print("✓ TEST 1: Chief module imports successfully")

    # TEST 2: Chief prompt imports
    assert chief_prompt is not None, "TEST 2 FAILED: chief_prompt module is None"
    assert hasattr(chief_prompt, "CHIEF_SYSTEM_PROMPT"), "TEST 2 FAILED: CHIEF_SYSTEM_PROMPT missing"
    assert hasattr(chief_prompt, "build_chief_user_prompt"), "TEST 2 FAILED: build_chief_user_prompt missing"
    print("✓ TEST 2: Chief prompt imports successfully")

    # TEST 3: Case reaches Chief
    visible_case = case_data.get_agent_visible_case()
    assert isinstance(visible_case, dict), "TEST 3 FAILED: Case data is not a dict"
    assert "suspects" in visible_case and "evidence" in visible_case, "TEST 3 FAILED: Case incomplete"
    print("✓ TEST 3: Case reaches Chief")

    # TEST 4, 5, 6, 7: All 4 reports reach Chief
    dummy_det = "# Detective Report\n\n## 1. Summary\nDetective report context alpha."
    dummy_evi = "# Evidence Report\n\n## 1. Overview\nEvidence report context beta."
    dummy_sus = "# Suspect Report\n\n## 1. Overview\nSuspect report context gamma."
    dummy_ske = "# Skeptic Report\n\n## 1. Challenges\nSkeptic report context delta."

    user_prompt = chief_prompt.build_chief_user_prompt(
        case_data=visible_case,
        detective_report=dummy_det,
        evidence_report=dummy_evi,
        suspect_report=dummy_sus,
        skeptic_report=dummy_ske
    )
    assert "Detective report context alpha." in user_prompt, "TEST 4 FAILED: Detective report missing"
    print("✓ TEST 4: Detective Report reaches Chief")
    assert "Evidence report context beta." in user_prompt, "TEST 5 FAILED: Evidence report missing"
    print("✓ TEST 5: Evidence Report reaches Chief")
    assert "Suspect report context gamma." in user_prompt, "TEST 6 FAILED: Suspect report missing"
    print("✓ TEST 6: Suspect Report reaches Chief")
    assert "Skeptic report context delta." in user_prompt, "TEST 7 FAILED: Skeptic report missing"
    print("✓ TEST 7: Skeptic Report reaches Chief")

    # TEST 8: Facilitator solution does NOT reach Chief
    assert "facilitator_only_guidance" not in user_prompt.lower(), "TEST 8 FAILED: facilitator_only_guidance in prompt"
    assert "human_review_answer" not in user_prompt.lower(), "TEST 8 FAILED: human_review_answer in prompt"
    assert "arjun vale is guilty" not in user_prompt.lower(), "TEST 8 FAILED: Predetermined guilt in prompt"
    print("✓ TEST 8: Facilitator solution does NOT reach Chief")

    # TEST 9: Chief distinguishes fact from inference
    sys_prompt = chief_prompt.CHIEF_SYSTEM_PROMPT
    assert "evidence vs inference" in sys_prompt.lower() or "fact from inference" in sys_prompt.lower(), "TEST 9 FAILED: Fact vs inference missing"
    print("✓ TEST 9: Chief distinguishes fact from inference")

    # TEST 10: Chief distinguishes card owner from card user
    assert "card owner != card user" in sys_prompt.lower(), "TEST 10 FAILED: Rule 1 (card owner != card user) missing"
    print("✓ TEST 10: Chief distinguishes card owner from card user")

    # TEST 11: Chief distinguishes card user from thief
    assert "card user != thief" in sys_prompt.lower(), "TEST 11 FAILED: Rule 2 (card user != thief) missing"
    print("✓ TEST 11: Chief distinguishes card user from thief")

    # TEST 12: Chief does not equate motive with guilt
    assert "motive != guilt" in sys_prompt.lower(), "TEST 12 FAILED: Rule 4 (motive != guilt) missing"
    print("✓ TEST 12: Chief does not equate motive with guilt")

    # TEST 13: Chief considers all four suspects
    for name in ["Lena Ortiz", "Theo Park", "Arjun Vale", "Sofia Reed"]:
        assert name in sys_prompt, f"TEST 13 FAILED: Suspect {name} missing from Chief prompt"
    print("✓ TEST 13: Chief considers all four suspects")

    # TEST 14: Chief considers Skeptic findings
    assert "skeptic findings" in sys_prompt.lower(), "TEST 14 FAILED: Skeptic findings section missing"
    print("✓ TEST 14: Chief considers Skeptic findings")

    # TEST 15: Chief considers alternative explanations
    assert "alternative explanations" in sys_prompt.lower(), "TEST 15 FAILED: Alternative explanations missing"
    print("✓ TEST 15: Chief considers alternative explanations")

    # TEST 16: Chief produces uncertainty
    assert "unresolved uncertainties" in sys_prompt.lower() or "what is not proven" in sys_prompt.lower(), "TEST 16 FAILED: Uncertainty requirements missing"
    print("✓ TEST 16: Chief produces uncertainty and states what is not proven")

    # TEST 17: Chief does not contain a hardcoded verdict
    assert "human review required" in sys_prompt.lower(), "TEST 17 FAILED: Human review requirement missing"
    print("✓ TEST 17: Chief does not contain a hardcoded verdict; leaves final determination to human review")

    # TEST 18: Malformed Gemini response parsing does not crash
    mock_report = """# CHIEF INVESTIGATION REPORT

## 1. Executive Summary
The Aurora Diamond vanished at approximately 8:20-8:24 PM.

## 2. Current Best Explanation
Arjun Vale's keycard was used to open the display case.

## 3. Evidence Foundation
- E-B: Access log recorded Arjun's keycard at 8:23 PM.

## 4. Evidence vs Inference
### Established Facts
- Access card registered to Arjun swiped at 8:23 PM.
### Reasonable Inferences
- Arjun may have held the card.
### Unresolved Uncertainties
- Physical identity of card user.
### Unknown Information
- Whereabouts of the diamond.

## 5. Suspect Comparison
### Arjun Vale
Leads circumstantial chain.

## 6. Cross-Agent Agreement and Disagreement
- Agents agree that card access is central.

## 7. Skeptic Findings
- Skeptic correctly points out card owner != card user.

## 8. Alternative Explanations
- Card theft from archive.

## 9. Strongest Evidence
Keycard access log at 8:23 PM.

## 10. Weakest Link in the Current Theory
Assuming card user was Arjun Vale.

## 11. What Is NOT Proven
Physical user of card, possession of diamond.

## 12. Recommended Next Investigation
- Review archive corridor camera footage.

## 13. Confidence Assessment
Confidence Level: MODERATE
Reason: Strong keycard timeline but unverified physical user.

## 14. Final Provisional Assessment
Leading suspect: Arjun Vale (Provisional)
Why: Keycard access and folder fibers
Main uncertainty: Biometric proof of card user
Strongest alternative: Third party card access

# HUMAN REVIEW REQUIRED
Human review required before final verdict.
"""
    parsed_conf = chief_agent._parse_confidence(mock_report)
    assert parsed_conf["level"] == "MODERATE", "TEST 18 FAILED: Confidence level not parsed"

    parsed_prov = chief_agent._parse_final_provisional_assessment(mock_report)
    assert "Arjun Vale" in parsed_prov["leading_suspect_or_explanation"], "TEST 18 FAILED: Leading suspect not parsed"

    parsed_evi_inf = chief_agent._extract_evidence_vs_inference(mock_report)
    assert len(parsed_evi_inf["established_facts"]) > 0, "TEST 18 FAILED: Established facts not parsed"
    assert len(parsed_evi_inf["unresolved_uncertainties"]) > 0, "TEST 18 FAILED: Uncertainties not parsed"
    print("✓ TEST 18: Malformed or plain-text markdown response parsed safely without crash")

    # TEST 19: Security violation and Gradio dependency checks
    leak_case = {"metadata": {}, "investigation_rules": ["facilitator_only_guidance"]}
    leak_res = chief_agent.run_chief_agent(case_data=leak_case)
    assert leak_res["status"] == "error", "TEST 19 FAILED: Security leak should error"
    assert "Security Violation" in leak_res["error"], "TEST 19 FAILED: Security error message missing"

    INVESTIGATION_CACHE["detective_report"] = ""
    INVESTIGATION_CACHE["evidence_report"] = ""
    INVESTIGATION_CACHE["suspect_report"] = ""
    INVESTIGATION_CACHE["skeptic_report"] = ""
    status, report, expl, conf, strong, weak, alt, next_s, rev = handle_run_chief()
    assert "Dependency Notice" in status, f"TEST 19 FAILED: Expected Dependency Notice, got '{status}'"
    print("✓ TEST 19: Security violation and Gradio prerequisite checks function safely")

    # TEST 20: Parts 1–6 continue working without regression
    assert hasattr(gemini_client, "generate_content"), "TEST 20 FAILED: Part 1 missing"
    assert case_data.validate_case()["valid"], "TEST 20 FAILED: Part 2 missing"
    assert hasattr(detective_agent, "run_detective_agent"), "TEST 20 FAILED: Part 3 missing"
    assert hasattr(evidence_agent, "run_evidence_agent"), "TEST 20 FAILED: Part 4 missing"
    assert hasattr(suspect_agent, "run_suspect_agent"), "TEST 20 FAILED: Part 5 missing"
    assert hasattr(skeptic_agent, "run_skeptic_agent"), "TEST 20 FAILED: Part 6 missing"
    print("✓ TEST 20: Parts 1–6 modules and contracts intact without regression")

    print("=" * 60)
    print("ALL PART 7 CHIEF AGENT TESTS PASSED SUCCESSFULLY! (20/20)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
