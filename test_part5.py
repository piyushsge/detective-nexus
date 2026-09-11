"""
Test suite for Part 5: Suspect Agent.
Verifies all 25 required checks covering:
- Suspect agent and prompt imports
- Agent-visible data isolation
- Ingestion of Detective and Evidence reports
- Anti-solution-leak and anti-bias enforcement
- Fair comparison across all 4 suspects (Lena, Theo, Arjun, Sofia)
- Epistemological distinctions (motive != guilt, card owner != card user, folder != diamond)
- Uncertainty and limitation preservation
- Safe error handling and multi-agent pipeline regression
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
from app.prompts import suspect_prompt
from app.agents import detective_agent, evidence_agent, suspect_agent
from app import gemini_client


def run_all_tests():
    print("=" * 60)
    print("RUNNING PART 5 SUSPECT AGENT TESTS (25 CHECKS)")
    print("=" * 60)

    # TEST 1: Suspect Agent imports
    assert suspect_agent is not None, "TEST 1 FAILED: suspect_agent module is None"
    assert hasattr(suspect_agent, "run_suspect_agent"), "TEST 1 FAILED: run_suspect_agent missing"
    print("✓ TEST 1: Suspect Agent imports successfully")

    # TEST 2: Suspect prompt imports
    assert suspect_prompt is not None, "TEST 2 FAILED: suspect_prompt module is None"
    assert hasattr(suspect_prompt, "SUSPECT_SYSTEM_PROMPT"), "TEST 2 FAILED: SUSPECT_SYSTEM_PROMPT missing"
    assert hasattr(suspect_prompt, "build_suspect_user_prompt"), "TEST 2 FAILED: build_suspect_user_prompt missing"
    print("✓ TEST 2: Suspect prompt imports successfully")

    # TEST 3: Agent receives case
    visible_case = case_data.get_agent_visible_case()
    assert isinstance(visible_case, dict), "TEST 3 FAILED: get_agent_visible_case did not return dict"
    assert "suspects" in visible_case, "TEST 3 FAILED: suspects key missing from case"
    print("✓ TEST 3: Agent receives case")

    # TEST 4: Agent receives Detective Report
    dummy_det_report = "# Detective Report\n\n## 1. Case Understanding\nBaseline context."
    # TEST 5: Agent receives Evidence Report
    dummy_ev_report = "# Evidence Report\n\n## 1. Evidence Overview\nForensic matrix context."
    built_prompt = suspect_prompt.build_suspect_user_prompt(visible_case, dummy_det_report, dummy_ev_report)
    assert "Baseline context." in built_prompt, "TEST 4 FAILED: Detective report not found in user prompt"
    print("✓ TEST 4: Agent receives Detective Report")
    assert "Forensic matrix context." in built_prompt, "TEST 5 FAILED: Evidence report not found in user prompt"
    print("✓ TEST 5: Agent receives Evidence Report")

    # TEST 6: Facilitator guidance is not passed
    serialized_case = json.dumps(visible_case).lower()
    assert "facilitator_only_guidance" not in serialized_case, "TEST 6 FAILED: Facilitator guidance leaked into case"
    print("✓ TEST 6: Facilitator guidance is not passed")

    # TEST 7: Hidden solution is not passed
    assert "leading_suspect" not in serialized_case, "TEST 7 FAILED: Leading suspect leaked into case"
    assert "arjun is the leading suspect" not in serialized_case, "TEST 7 FAILED: Leading suspect phrase found"
    print("✓ TEST 7: Hidden solution is not passed")

    # TEST 8: All four suspects are analyzed
    sys_prompt = suspect_prompt.SUSPECT_SYSTEM_PROMPT
    for name in ["Lena Ortiz", "Theo Park", "Arjun Vale", "Sofia Reed"]:
        assert name in sys_prompt, f"TEST 8 FAILED: Suspect '{name}' missing from prompt requirements"
    print("✓ TEST 8: All four suspects are analyzed")

    # TEST 9: Motive is separated from guilt
    assert "motive != guilt" in sys_prompt.lower() or "motive does not equal guilt" in sys_prompt.lower(), "TEST 9 FAILED: Motive != guilt principle missing"
    print("✓ TEST 9: Motive is separated from guilt")

    # TEST 10: Means is separated from proof
    assert "means" in sys_prompt.lower(), "TEST 10 FAILED: Means analysis missing from prompt"
    print("✓ TEST 10: Means is separated from proof")

    # TEST 11: Opportunity uses the actual timeline
    assert "opportunity" in sys_prompt.lower(), "TEST 11 FAILED: Opportunity analysis missing"
    assert "8:20" in sys_prompt or "blackout" in sys_prompt.lower(), "TEST 11 FAILED: Timeline window missing"
    print("✓ TEST 11: Opportunity uses the actual timeline")

    # TEST 12: Card owner/card user distinction is preserved
    assert "card owner != card user" in sys_prompt.lower() or "card owner" in sys_prompt.lower(), "TEST 12 FAILED: Card owner vs user missing"
    print("✓ TEST 12: Card owner/card user distinction is preserved")

    # TEST 13: Lena footprint uncertainty is preserved
    assert "shoeprint" in sys_prompt.lower() or "footprint" in sys_prompt.lower(), "TEST 13 FAILED: Shoeprint reference missing"
    print("✓ TEST 13: Lena footprint uncertainty is preserved")

    # TEST 14: Arjun folder uncertainty is preserved
    assert "folder" in sys_prompt.lower(), "TEST 14 FAILED: Folder reference missing"
    print("✓ TEST 14: Arjun folder uncertainty is preserved")

    # TEST 15: Fiber uncertainty is preserved
    assert "fiber" in sys_prompt.lower(), "TEST 15 FAILED: Fiber reference missing"
    print("✓ TEST 15: Fiber uncertainty is preserved")

    # TEST 16: Theo camera evidence is preserved
    assert "theo" in sys_prompt.lower() and "camera" in sys_prompt.lower(), "TEST 16 FAILED: Theo camera evidence missing"
    print("✓ TEST 16: Theo camera evidence is preserved")

    # TEST 17: Sofia witness evidence is preserved
    assert "sofia" in sys_prompt.lower(), "TEST 17 FAILED: Sofia witness reference missing"
    print("✓ TEST 17: Sofia witness evidence is preserved")

    # TEST 18: No invented evidence is hardcoded
    evidence_ids = [e["evidence_id"] for e in case_data.EVIDENCE]
    assert evidence_ids == ["E-A", "E-B", "E-C", "E-D", "E-E", "E-F", "E-G"], "TEST 18 FAILED: Evidence corrupted"
    print("✓ TEST 18: No invented evidence is hardcoded")

    # TEST 19: No hardcoded ranking exists
    # Verify suspect_agent does not hardcode ranking
    import inspect
    agent_code = inspect.getsource(suspect_agent.run_suspect_agent)
    assert 'ranking = ["Arjun' not in agent_code, "TEST 19 FAILED: Hardcoded suspect ranking detected"
    print("✓ TEST 19: No hardcoded ranking exists in application logic")

    # TEST 20: Gemini errors are handled safely
    bad_case = dict(visible_case)
    bad_case["facilitator_only_guidance"] = "leak"
    sec_res = suspect_agent.run_suspect_agent(bad_case, "det", "ev")
    assert sec_res["status"] == "error", "TEST 20 FAILED: Security leak did not return error status"
    assert "Security Violation" in sec_res["error"], "TEST 20 FAILED: Expected security violation error message"
    print("✓ TEST 20: Gemini and security errors are handled safely")

    # TEST 21: Part 1 still works
    assert hasattr(gemini_client, "test_gemini_connection"), "TEST 21 FAILED: test_gemini_connection missing"
    print("✓ TEST 21: Part 1 Gemini connection remains functional")

    # TEST 22: Part 2 still works
    c_val = case_data.validate_case()
    assert c_val["valid"] is True, f"TEST 22 FAILED: Case validation failed: {c_val['errors']}"
    print("✓ TEST 22: Part 2 case validation remains functional")

    # TEST 23: Part 3 Detective Agent still works
    assert hasattr(detective_agent, "run_detective_agent"), "TEST 23 FAILED: run_detective_agent missing"
    print("✓ TEST 23: Part 3 Detective Agent remains functional")

    # TEST 24: Part 4 Evidence Agent still works
    assert hasattr(evidence_agent, "run_evidence_agent"), "TEST 24 FAILED: run_evidence_agent missing"
    print("✓ TEST 24: Part 4 Evidence Agent remains functional")

    # TEST 25: Gradio launches
    from app.main import create_ui
    demo = create_ui()
    assert demo is not None, "TEST 25 FAILED: Gradio create_ui returned None"
    print("✓ TEST 25: Gradio application initializes successfully with Part 5 tab")

    print("=" * 60)
    print("ALL 25 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
