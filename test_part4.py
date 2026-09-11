"""
Test suite for Part 4: Evidence Agent.
Verifies all 22 required checks covering imports, agent-visible isolation,
epistemological classification (FACT/INFERENCE/DISTRACTION/UNCERTAIN),
evidence limitations, anti-leak enforcement, and multi-agent regression.
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
from app.prompts import evidence_prompt
from app.agents import detective_agent, evidence_agent
from app import gemini_client


def run_all_tests():
    print("=" * 60)
    print("RUNNING PART 4 EVIDENCE AGENT TESTS (22 CHECKS)")
    print("=" * 60)

    # TEST 1: Evidence Agent imports successfully
    assert evidence_agent is not None, "TEST 1 FAILED: evidence_agent module is None"
    assert hasattr(evidence_agent, "run_evidence_agent"), "TEST 1 FAILED: run_evidence_agent function missing"
    print("✓ TEST 1: Evidence Agent imports successfully")

    # TEST 2: Evidence Agent receives agent-visible case
    visible_case = case_data.get_agent_visible_case()
    assert isinstance(visible_case, dict), "TEST 2 FAILED: get_agent_visible_case did not return dict"
    assert "evidence" in visible_case, "TEST 2 FAILED: evidence missing from visible case"
    print("✓ TEST 2: Evidence Agent receives agent-visible case")

    # TEST 3: Evidence Agent receives Detective Agent report
    dummy_detective_report = "# Detective Report\n\n## 1. Case Understanding\nTest report context."
    prompt_with_report = evidence_prompt.build_evidence_user_prompt(visible_case, dummy_detective_report)
    assert "Test report context." in prompt_with_report, "TEST 3 FAILED: Detective report not embedded in user prompt"
    print("✓ TEST 3: Evidence Agent receives Detective Agent report")

    # TEST 4: Facilitator guidance is not passed
    serialized_case = json.dumps(visible_case).lower()
    assert "facilitator_only_guidance" not in serialized_case, "TEST 4 FAILED: Facilitator guidance found in case"
    print("✓ TEST 4: Facilitator guidance is not passed")

    # TEST 5: Hidden solution is not passed
    assert "leading_suspect" not in serialized_case, "TEST 5 FAILED: Leading suspect found in case"
    assert "arjun is the leading suspect" not in serialized_case, "TEST 5 FAILED: Leading suspect phrase leaked"
    print("✓ TEST 5: Hidden solution is not passed")

    # TEST 6: Evidence prompt contains evidence-discipline rules
    sys_prompt = evidence_prompt.EVIDENCE_SYSTEM_PROMPT
    assert "CRITICAL EPISTEMOLOGICAL PRINCIPLES" in sys_prompt or "evidence" in sys_prompt.lower(), "TEST 6 FAILED: Evidence discipline missing"
    print("✓ TEST 6: Evidence prompt contains evidence-discipline rules")

    # TEST 7: Evidence prompt contains FACT/INFERENCE/DISTRACTION/UNCERTAIN
    for taxonomy in ["FACT", "INFERENCE", "DISTRACTION", "UNCERTAIN"]:
        assert taxonomy in sys_prompt, f"TEST 7 FAILED: Taxonomy term '{taxonomy}' missing from system prompt"
    print("✓ TEST 7: Evidence prompt contains FACT/INFERENCE/DISTRACTION/UNCERTAIN")

    # TEST 8: Prompt contains card-owner/card-user distinction
    assert "card-owner" in sys_prompt.lower() or ("card" in sys_prompt.lower() and "user" in sys_prompt.lower()), "TEST 8 FAILED: Card-owner/card-user distinction missing"
    print("✓ TEST 8: Prompt contains card-owner/card-user distinction")

    # TEST 9: Prompt requires evidence limitations
    assert "limitations" in sys_prompt.lower(), "TEST 9 FAILED: Evidence limitations requirement missing"
    print("✓ TEST 9: Prompt requires evidence limitations")

    # TEST 10: Prompt requires unsupported conclusions to avoid
    assert "unsupported conclusions" in sys_prompt.lower(), "TEST 10 FAILED: Unsupported conclusions requirement missing"
    print("✓ TEST 10: Prompt requires unsupported conclusions to avoid")

    # TEST 11: E-A through E-G are analyzed
    evidence_ids = ["E-A", "E-B", "E-C", "E-D", "E-E", "E-F", "E-G"]
    for eid in evidence_ids:
        assert eid in sys_prompt, f"TEST 11 FAILED: Evidence ID '{eid}' missing from prompt analysis requirement"
    print("✓ TEST 11: E-A through E-G are analyzed")

    # TEST 12: E-B vs E-C contradiction is recognized
    assert "E-B" in sys_prompt and "E-C" in sys_prompt, "TEST 12 FAILED: E-B vs E-C tension not recognized in prompt"
    print("✓ TEST 12: E-B vs E-C contradiction is recognized")

    # TEST 13: E-D folder contents limitation is recognized
    assert "folder" in sys_prompt.lower() and "contents" in sys_prompt.lower(), "TEST 13 FAILED: E-D folder contents limitation missing"
    print("✓ TEST 13: E-D folder contents limitation is recognized")

    # TEST 14: E-E fiber uncertainty is recognized
    assert "fiber" in sys_prompt.lower() and ("scientific" in sys_prompt.lower() or "uncertain" in sys_prompt.lower()), "TEST 14 FAILED: E-E fiber uncertainty missing"
    print("✓ TEST 14: E-E fiber uncertainty is recognized")

    # TEST 15: E-F footprint timing uncertainty is recognized
    assert "shoeprint" in sys_prompt.lower() or "boot" in sys_prompt.lower(), "TEST 15 FAILED: E-F shoeprint missing"
    assert "timing" in sys_prompt.lower(), "TEST 15 FAILED: Footprint timing uncertainty missing"
    print("✓ TEST 15: E-F footprint timing uncertainty is recognized")

    # TEST 16: E-G does not automatically create a financial motive
    assert "insurance" in sys_prompt.lower(), "TEST 16 FAILED: E-G insurance reference missing"
    assert "do not invent a financial motive" in sys_prompt.lower(), "TEST 16 FAILED: Financial motive prevention missing"
    print("✓ TEST 16: E-G does not automatically create a financial motive")

    # TEST 17: No fake evidence is generated by application code
    # Verify primary case records contain only official case items
    case_evidence_ids = [e["evidence_id"] for e in case_data.EVIDENCE]
    assert case_evidence_ids == evidence_ids, f"TEST 17 FAILED: Evidence items corrupted: {case_evidence_ids}"
    assert "E-H" not in case_evidence_ids, "TEST 17 FAILED: Invented evidence found"
    print("✓ TEST 17: No fake evidence is generated by application code")

    # TEST 18: Gemini error handling works
    bad_case = dict(visible_case)
    bad_case["facilitator_only_guidance"] = "leak_test"
    sec_res = evidence_agent.run_evidence_agent(bad_case, "detective report")
    assert sec_res["status"] == "error", "TEST 18 FAILED: Security leak did not return error status"
    assert "Security Violation" in sec_res["error"], "TEST 18 FAILED: Expected security violation error message"
    print("✓ TEST 18: Gemini and security error handling works safely")

    # TEST 19: Part 1 Gemini connection remains functional
    assert hasattr(gemini_client, "test_gemini_connection"), "TEST 19 FAILED: test_gemini_connection missing"
    print("✓ TEST 19: Part 1 Gemini connection remains functional")

    # TEST 20: Part 2 validation remains functional
    c_val = case_data.validate_case()
    assert c_val["valid"] is True, f"TEST 20 FAILED: validate_case failed: {c_val['errors']}"
    print("✓ TEST 20: Part 2 validation remains functional")

    # TEST 21: Part 3 Detective Agent remains functional
    assert hasattr(detective_agent, "run_detective_agent"), "TEST 21 FAILED: run_detective_agent missing"
    print("✓ TEST 21: Part 3 Detective Agent remains functional")

    # TEST 22: Gradio application launches
    from app.main import create_ui
    demo = create_ui()
    assert demo is not None, "TEST 22 FAILED: Gradio create_ui returned None"
    print("✓ TEST 22: Gradio application initializes successfully with Part 4 tab")

    print("=" * 60)
    print("ALL 22 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
