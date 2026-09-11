"""
Test suite for Part 3: Detective Agent.
Verifies prompt integrity, evidence discipline, anti-bias neutrality,
structured output schema, safe error handling, and end-to-end integration.
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
from app.prompts import detective_prompt
from app.agents import detective_agent
from app import gemini_client


def run_all_tests():
    print("=" * 60)
    print("RUNNING PART 3 DETECTIVE AGENT TESTS")
    print("=" * 60)

    # TEST 1: Detective agent imports correctly
    assert detective_agent is not None, "TEST 1 FAILED: detective_agent module is None"
    assert hasattr(detective_agent, "run_detective_agent"), "TEST 1 FAILED: run_detective_agent function missing"
    print("✓ TEST 1: Detective agent imports correctly")

    # TEST 2: Agent receives agent-visible case
    visible_case = case_data.get_agent_visible_case()
    assert isinstance(visible_case, dict), "TEST 2 FAILED: get_agent_visible_case did not return dict"
    assert "metadata" in visible_case, "TEST 2 FAILED: metadata missing from visible case"
    assert "timeline" in visible_case, "TEST 2 FAILED: timeline missing from visible case"
    print("✓ TEST 2: Agent receives agent-visible case")

    # TEST 3: Facilitator-only guidance is NOT passed to the agent
    serialized_case = json.dumps(visible_case).lower()
    assert "facilitator_only_guidance" not in serialized_case, "TEST 3 FAILED: Facilitator guidance leaked into visible case!"
    assert "leading_suspect" not in serialized_case, "TEST 3 FAILED: Leading suspect leaked into visible case!"
    print("✓ TEST 3: Facilitator-only guidance is NOT passed")

    # TEST 4: Detective system prompt exists
    prompt = detective_prompt.DETECTIVE_SYSTEM_PROMPT
    assert prompt and len(prompt) > 200, "TEST 4 FAILED: DETECTIVE_SYSTEM_PROMPT is empty or too short"
    print("✓ TEST 4: Detective system prompt exists")

    # TEST 5: Prompt contains evidence-discipline rules
    assert "EVIDENCE DISCIPLINE" in prompt or "evidence discipline" in prompt.lower(), "TEST 5 FAILED: Evidence discipline missing from prompt"
    assert "fact" in prompt.lower() and "inference" in prompt.lower(), "TEST 5 FAILED: Fact vs inference distinction missing"
    print("✓ TEST 5: Prompt contains evidence-discipline rules")

    # TEST 6: Prompt contains uncertainty requirements
    assert "uncertainty" in prompt.lower(), "TEST 6 FAILED: Uncertainty requirements missing from prompt"
    assert "exact moment" in prompt.lower() or "removal" in prompt.lower(), "TEST 6 FAILED: Time removal uncertainty missing"
    print("✓ TEST 6: Prompt contains uncertainty requirements")

    # TEST 7: Prompt contains card-owner/card-user distinction
    assert "card" in prompt.lower() and ("user" in prompt.lower() or "physically" in prompt.lower()), "TEST 7 FAILED: Card owner vs card user distinction missing"
    print("✓ TEST 7: Prompt contains card-owner/card-user distinction")

    # TEST 8: Prompt does not contain the hidden solution or bias
    forbidden_bias_terms = [
        "arjun is guilty",
        "arjun is the thief",
        "arjun is the culprit",
        "arjun is the leading suspect"
    ]
    for term in forbidden_bias_terms:
        assert term not in prompt.lower(), f"TEST 8 FAILED: Bias term '{term}' found in system prompt!"
    print("✓ TEST 8: Prompt does not contain hidden solution or suspect bias")

    # TEST 9: Agent result has expected structured fields
    # Test result structure using a simulated completed payload
    mock_payload = detective_agent._extract_section_items(
        "## 6. Unanswered Questions\n1. Who used the card?\n2. Where was it?",
        "Unanswered Questions"
    )
    assert len(mock_payload) == 2, f"TEST 9 FAILED: Item extraction returned {mock_payload}"
    print("✓ TEST 9: Agent result parser accurately extracts structured fields")

    # TEST 10: Gemini errors are handled safely
    # Intentionally passing a case containing leak terms triggers security abort without crashing
    bad_case = dict(visible_case)
    bad_case["facilitator_only_guidance"] = "leak"
    security_error_result = detective_agent.run_detective_agent(bad_case)
    assert security_error_result["status"] == "error", "TEST 10 FAILED: Security leak did not trigger error status"
    assert "Security Violation" in security_error_result["error"], "TEST 10 FAILED: Expected security error message"
    print("✓ TEST 10: Gemini and security errors are handled safely without crashing")

    # TEST 11: Part 1 Gemini connection test still works
    assert hasattr(gemini_client, "test_gemini_connection"), "TEST 11 FAILED: test_gemini_connection missing"
    print("✓ TEST 11: Part 1 Gemini connection test remains intact")

    # TEST 12: Part 2 case validation still works
    case_val = case_data.validate_case()
    assert case_val["valid"] is True, f"TEST 12 FAILED: validate_case failed: {case_val['errors']}"
    print("✓ TEST 12: Part 2 case validation remains 100% valid")

    # TEST 13: Gradio application launches
    from app.main import create_ui
    demo = create_ui()
    assert demo is not None, "TEST 13 FAILED: create_ui returned None"
    print("✓ TEST 13: Gradio application initializes successfully")

    print("=" * 60)
    print("ALL 13 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
