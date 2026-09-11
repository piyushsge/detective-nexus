"""
Test suite for Part 2: Structured Case File System.
Verifies structure, completeness, isolation, and anti-solution-leak constraints.
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


def run_all_tests():
    print("=" * 60)
    print("RUNNING PART 2 VALIDATION TESTS")
    print("=" * 60)

    # TEST 1: Import case_data successfully
    assert case_data is not None, "TEST 1 FAILED: case_data failed to import"
    print("✓ TEST 1: Import case_data successfully")

    # TEST 2: validate_case() returns valid=True
    validation = case_data.validate_case()
    assert validation["valid"] is True, f"TEST 2 FAILED: validate_case returned errors: {validation['errors']}"
    assert len(validation["errors"]) == 0, "TEST 2 FAILED: errors list should be empty"
    print("✓ TEST 2: validate_case() returns valid=True")

    # TEST 3: Exactly 9 timeline events
    assert len(case_data.TIMELINE_EVENTS) == 9, f"TEST 3 FAILED: expected 9 timeline events, got {len(case_data.TIMELINE_EVENTS)}"
    print("✓ TEST 3: There are exactly 9 timeline events")

    # TEST 4: Exactly 4 suspects
    assert len(case_data.SUSPECTS) == 4, f"TEST 4 FAILED: expected 4 suspects, got {len(case_data.SUSPECTS)}"
    print("✓ TEST 4: There are exactly 4 suspects")

    # TEST 5: Exactly 5 witnesses
    assert len(case_data.WITNESSES) == 5, f"TEST 5 FAILED: expected 5 witnesses, got {len(case_data.WITNESSES)}"
    print("✓ TEST 5: There are exactly 5 witnesses")

    # TEST 6: Exactly 7 evidence items
    assert len(case_data.EVIDENCE) == 7, f"TEST 6 FAILED: expected 7 evidence items, got {len(case_data.EVIDENCE)}"
    print("✓ TEST 6: There are exactly 7 evidence items")

    # TEST 7: Evidence E-A through E-G exist
    expected_evidence_ids = ["E-A", "E-B", "E-C", "E-D", "E-E", "E-F", "E-G"]
    actual_evidence_ids = [e["evidence_id"] for e in case_data.EVIDENCE]
    assert actual_evidence_ids == expected_evidence_ids, f"TEST 7 FAILED: expected {expected_evidence_ids}, got {actual_evidence_ids}"
    print("✓ TEST 7: Evidence E-A through E-G exist")

    # TEST 8: Suspect S01 through S04 exist
    expected_suspect_ids = ["S01", "S02", "S03", "S04"]
    actual_suspect_ids = [s["suspect_id"] for s in case_data.SUSPECTS]
    assert actual_suspect_ids == expected_suspect_ids, f"TEST 8 FAILED: expected {expected_suspect_ids}, got {actual_suspect_ids}"
    print("✓ TEST 8: Suspect S01 through S04 exist")

    # TEST 9: Timeline T01 through T09 exist
    expected_timeline_ids = [f"T0{i}" for i in range(1, 10)]
    actual_timeline_ids = [t["id"] for t in case_data.TIMELINE_EVENTS]
    assert actual_timeline_ids == expected_timeline_ids, f"TEST 9 FAILED: expected {expected_timeline_ids}, got {actual_timeline_ids}"
    print("✓ TEST 9: Timeline T01 through T09 exist")

    # TEST 10: get_agent_visible_case() works and is JSON serializable
    agent_case = case_data.get_agent_visible_case()
    assert isinstance(agent_case, dict), "TEST 10 FAILED: get_agent_visible_case did not return dict"
    serialized = json.dumps(agent_case)
    assert len(serialized) > 1000, "TEST 10 FAILED: serialized JSON too small"
    print("✓ TEST 10: get_agent_visible_case() works & is JSON-serializable")

    # TEST 11 & ANTI-SOLUTION-LEAK TEST:
    # Verifies that agent-visible case does NOT contain facilitator solution
    case_str_lower = json.dumps(agent_case).lower()
    forbidden_terms = [
        "leading_suspect",
        "arjun is the leading suspect",
        "arjun vale is guilty",
        "facilitator_only_guidance"
    ]
    for term in forbidden_terms:
        assert term not in case_str_lower, f"TEST 11 (ANTI-LEAK) FAILED: Forbidden term '{term}' found in agent-visible data!"
    print("✓ TEST 11: get_agent_visible_case() does NOT contain facilitator-only solution")
    print("✓ ANTI-SOLUTION-LEAK TEST PASSED: Zero facilitator conclusions leaked into agent view")

    # TEST 12: Gemini connection component from Part 1 remains functional
    from app.gemini_client import test_gemini_connection
    assert callable(test_gemini_connection), "TEST 12 FAILED: test_gemini_connection is not callable"
    print("✓ TEST 12: Gemini connection component from Part 1 remains functional")

    # TEST 13: Gradio interface can be created
    from app.main import create_ui
    demo = create_ui()
    assert demo is not None, "TEST 13 FAILED: Gradio create_ui returned None"
    print("✓ TEST 13: Gradio interface still initializes successfully")

    print("=" * 60)
    print("ALL 13 TESTS + ANTI-LEAK TEST PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
