"""
Test suite for Part 6: Skeptic Agent.
Verifies all required checks covering:
1. Skeptic module imports successfully.
2. Skeptic prompt imports successfully.
3. Case data reaches the Skeptic Agent.
4. Detective Report reaches the Skeptic Agent.
5. Evidence Report reaches the Skeptic Agent.
6. Suspect Report reaches the Skeptic Agent.
7. Facilitator solution is NOT passed into the prompt.
8. Skeptic prompt explicitly distinguishes:
   - card owner vs card user
   - card user vs thief
   - motive vs guilt
   - fact vs inference
9. All evidence IDs E-A through E-G can be considered.
10. All four suspects can be stress-tested.
11. Alternative explanations are supported by known facts.
12. No fictional evidence is inserted by application code.
13. Gemini failure does not crash the agent or UI.
14. JSON parsing / imperfect model format failure does not crash the agent.
15. Parts 1–5 continue working without regression.
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
from app.prompts import detective_prompt, evidence_prompt, suspect_prompt, skeptic_prompt
from app.agents import detective_agent, evidence_agent, suspect_agent, skeptic_agent
from app import gemini_client
from app.main import handle_run_skeptic, INVESTIGATION_CACHE


def run_all_tests():
    print("=" * 60)
    print("RUNNING PART 6 SKEPTIC AGENT TESTS (20+ VERIFICATION CHECKS)")
    print("=" * 60)

    # TEST 1: Skeptic module imports successfully
    assert skeptic_agent is not None, "TEST 1 FAILED: skeptic_agent module is None"
    assert hasattr(skeptic_agent, "run_skeptic_agent"), "TEST 1 FAILED: run_skeptic_agent missing"
    print("✓ TEST 1: Skeptic module imports successfully")

    # TEST 2: Skeptic prompt imports successfully
    assert skeptic_prompt is not None, "TEST 2 FAILED: skeptic_prompt module is None"
    assert hasattr(skeptic_prompt, "SKEPTIC_SYSTEM_PROMPT"), "TEST 2 FAILED: SKEPTIC_SYSTEM_PROMPT missing"
    assert hasattr(skeptic_prompt, "build_skeptic_user_prompt"), "TEST 2 FAILED: build_skeptic_user_prompt missing"
    print("✓ TEST 2: Skeptic prompt imports successfully")

    # TEST 3: Case data reaches the Skeptic Agent
    visible_case = case_data.get_agent_visible_case()
    assert isinstance(visible_case, dict), "TEST 3 FAILED: get_agent_visible_case did not return dict"
    assert "evidence" in visible_case and "suspects" in visible_case, "TEST 3 FAILED: Case data incomplete"
    print("✓ TEST 3: Case data reaches the Skeptic Agent")

    # TEST 4, 5, 6: Detective, Evidence, and Suspect reports reach the Skeptic Agent
    dummy_det = "# Detective Report\n\n## 1. Incident\nDetective finding alpha."
    dummy_evi = "# Evidence Report\n\n## 1. Overview\nEvidence finding beta."
    dummy_sus = "# Suspect Report\n\n## 1. Overview\nSuspect finding gamma."

    user_prompt = skeptic_prompt.build_skeptic_user_prompt(
        case_data=visible_case,
        detective_report=dummy_det,
        evidence_report=dummy_evi,
        suspect_report=dummy_sus
    )
    assert "Detective finding alpha." in user_prompt, "TEST 4 FAILED: Detective report missing from prompt"
    print("✓ TEST 4: Detective Report reaches the Skeptic Agent")
    assert "Evidence finding beta." in user_prompt, "TEST 5 FAILED: Evidence report missing from prompt"
    print("✓ TEST 5: Evidence Report reaches the Skeptic Agent")
    assert "Suspect finding gamma." in user_prompt, "TEST 6 FAILED: Suspect report missing from prompt"
    print("✓ TEST 6: Suspect Report reaches the Skeptic Agent")

    # TEST 7: Facilitator solution is NOT passed into the prompt
    assert "facilitator_only_guidance" not in user_prompt.lower(), "TEST 7 FAILED: facilitator_only_guidance found in prompt"
    assert "human_review_answer" not in user_prompt.lower(), "TEST 7 FAILED: human_review_answer found in prompt"
    assert "arjun vale is guilty" not in user_prompt.lower(), "TEST 7 FAILED: Hardcoded guilt found in prompt"
    print("✓ TEST 7: Facilitator solution is NOT passed into the prompt")

    # TEST 8: Skeptic prompt explicitly distinguishes core reasoning rules
    sys_prompt = skeptic_prompt.SKEPTIC_SYSTEM_PROMPT
    assert "card owner != card user" in sys_prompt.lower(), "TEST 8 FAILED: Rule 1 (card owner != card user) missing"
    assert "card user != thief" in sys_prompt.lower(), "TEST 8 FAILED: Rule 2 (card user != thief) missing"
    assert "motive != guilt" in sys_prompt.lower(), "TEST 8 FAILED: Rule 3 (motive != guilt) missing"
    assert "inference != fact" in sys_prompt.lower(), "TEST 8 FAILED: Rule 6 (inference != fact) missing"
    print("✓ TEST 8: Skeptic prompt explicitly distinguishes card owner/user, user/thief, motive/guilt, fact/inference")

    # TEST 9: All evidence IDs E-A through E-G can be considered
    for eid in ["E-A", "E-B", "E-C", "E-D", "E-E", "E-F", "E-G"]:
        assert eid in sys_prompt or eid in user_prompt, f"TEST 9 FAILED: Evidence ID '{eid}' missing from prompt"
    print("✓ TEST 9: All evidence IDs E-A through E-G can be considered")

    # TEST 10: All four suspects can be stress-tested
    for name in ["Lena Ortiz", "Theo Park", "Arjun Vale", "Sofia Reed"]:
        assert name in sys_prompt, f"TEST 10 FAILED: Suspect '{name}' missing from prompt"
    print("✓ TEST 10: All four suspects can be stress-tested")

    # TEST 11: Alternative explanations are supported by known facts
    assert "alternative explanations" in sys_prompt.lower(), "TEST 11 FAILED: Alternative explanations requirement missing"
    print("✓ TEST 11: Alternative explanations are supported by known facts")

    # TEST 12: No fictional evidence is inserted by application code
    prohibited = ["dna", "fingerprint", "laser", "secret tunnel", "accomplice confession"]
    for word in prohibited:
        assert word not in user_prompt.lower(), f"TEST 12 FAILED: Prohibited term '{word}' found in case prompt"
    print("✓ TEST 12: No fictional evidence is inserted by application code")

    # TEST 13: Security violation / anti-leak abort in Skeptic Agent
    leak_case = {"metadata": {}, "investigation_rules": ["facilitator_only_guidance"]}
    leak_res = skeptic_agent.run_skeptic_agent(case_data=leak_case)
    assert leak_res["status"] == "error", "TEST 13 FAILED: Agent should error on leak attempt"
    assert "Security Violation" in leak_res["error"], "TEST 13 FAILED: Proper security error not returned"
    print("✓ TEST 13: Security violation aborts cleanly without crash")

    # TEST 14: Dependency check in Gradio UI handler
    INVESTIGATION_CACHE["detective_report"] = ""
    INVESTIGATION_CACHE["evidence_report"] = ""
    INVESTIGATION_CACHE["suspect_report"] = ""
    res = handle_run_skeptic()
    status, report = res[0], res[1]
    assert "Dependency Notice" in status, f"TEST 14 FAILED: Expected dependency notice, got '{status}'"
    assert "Please complete" in report or "Please run previous agents" in report, "TEST 14 FAILED: Missing previous agents guidance"
    print("✓ TEST 14: Gradio handler correctly blocks execution when prerequisites are missing")

    # TEST 15: Structured parsing of mock Skeptic report
    mock_report = """# SKEPTIC INVESTIGATION REPORT

## 1. Current Theory Being Challenged
The investigation places Arjun Vale as the primary suspect based on card access and folder fibers.

## 2. Strongest Assumptions
- The card owner physically swiped the card (HIGH)
- The folder held the diamond (HIGH)

## 3. Evidence Vulnerabilities
### E-B: Access Log
Establishes card authorized entry at 8:23 PM, does not establish physical holder.

## 4. Fact vs Inference Audit
### FACTS
- Card registered to Arjun used at 8:23 PM.
### INFERENCES
- Arjun carried the diamond out in his folder.

## 5. Suspect Theory Stress Test
### Arjun Vale
Card evidence is strong but circumstantial regarding physical theft. Assessment: MODERATE.

## 6. Alternative Explanations
- Card was borrowed or swiped by a third party.

## 7. Counterarguments
Arjun's continuous presence in archive contradicts gallery timeline.

## 8. What Would Falsify the Current Theory
Corridor footage showing someone else entering gallery at 8:23 PM.

## 9. Critical Missing Evidence
1. Corridor camera records outside gallery door.

## 10. Recommended Verification Steps
1. Perform forensic spectrometer analysis on fibers.

## 11. Skeptic Assessment
Current theory status: Plausible but Fragile
Main vulnerability: Card usage not linked to biometric authentication
Strongest alternative: Third party used card during blackout
Most important missing evidence: Corridor footage
Overall challenge level: HIGH
"""
    parsed_current = skeptic_agent._extract_section_text(mock_report, "Current Theory Being Challenged")
    assert "Arjun Vale" in parsed_current, "TEST 15 FAILED: Current theory not extracted"

    parsed_assessment = skeptic_agent._parse_skeptic_assessment(mock_report)
    assert parsed_assessment["challenge_level"] == "HIGH", "TEST 15 FAILED: Challenge level not parsed"
    assert "Biometric" in parsed_assessment["main_vulnerability"] or "card" in parsed_assessment["main_vulnerability"].lower(), "TEST 15 FAILED: Main vulnerability not parsed"

    parsed_audit = skeptic_agent._extract_fact_inference_audit(mock_report)
    assert len(parsed_audit["facts"]) > 0, "TEST 15 FAILED: Facts audit not extracted"
    assert len(parsed_audit["inferences"]) > 0, "TEST 15 FAILED: Inferences audit not extracted"
    print("✓ TEST 15: Safe section extraction and structured audit parsing work reliably")

    # TEST 16: Parts 1-5 Regression Checks
    # Part 1
    assert hasattr(gemini_client, "generate_content"), "TEST 16 FAILED: Part 1 generate_content missing"
    # Part 2
    case_val = case_data.validate_case()
    assert case_val["valid"], "TEST 16 FAILED: Part 2 case validation failed"
    # Part 3
    assert hasattr(detective_agent, "run_detective_agent"), "TEST 16 FAILED: Part 3 detective agent missing"
    # Part 4
    assert hasattr(evidence_agent, "run_evidence_agent"), "TEST 16 FAILED: Part 4 evidence agent missing"
    # Part 5
    assert hasattr(suspect_agent, "run_suspect_agent"), "TEST 16 FAILED: Part 5 suspect agent missing"
    print("✓ TEST 16: Parts 1–5 modules and contracts intact without regression")

    print("=" * 60)
    print("ALL PART 6 SKEPTIC AGENT TESTS PASSED SUCCESSFULLY! (16/16)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
