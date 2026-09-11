"""
End-to-End Execution Script for AI Mystery Detective Team.
Case: The Vanishing Aurora Diamond

Executes the complete sequential pipeline across all 7 stages:
1. 🔌 Test Gemini Connection
2. 📁 Load Case File
3. 🕵️ Run Detective Investigation
4. 🔎 Run Evidence Analysis
5. 👤 Run Suspect Analysis
6. 🧠 Run Skeptic Challenge
7. 👨‍⚖️ Run Chief Investigation
"""

import sys
from pathlib import Path

# Ensure utf-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("============================================================")
print("RUNNING COMPLETE END-TO-END MULTI-AGENT PIPELINE EXECUTION")
print("============================================================")

# STEP 1: Test Gemini Connection
print("\n[STEP 1/7] 🔌 Testing Gemini Connection...")
from app.gemini_client import test_gemini_connection
status, diag = test_gemini_connection()
print(f"Status: {status}")
print(f"Diagnostic: {diag.strip()[:140]}...")
assert "successful" in status.lower(), "Connection test failed!"

# STEP 2: Load & Validate Case File
print("\n[STEP 2/7] 📁 Loading Case File...")
from app.case import case_data
val_res = case_data.validate_case()
assert val_res["valid"], f"Case validation failed: {val_res['errors']}"
visible_case = case_data.get_agent_visible_case()
summary = case_data.get_case_summary()
print(f"Case: {summary['Case']} ({summary['Case ID']})")
print(f"Suspects: {summary['Suspects']}, Witnesses: {summary['Witnesses']}, Evidence: {summary['Evidence']}")
print("✓ Case data loaded and isolated from facilitator solution.")

# STEP 3: Run Detective Agent
print("\n[STEP 3/7] 🕵️ Running Detective Investigation...")
from app.agents.detective_agent import run_detective_agent
det_res = run_detective_agent(visible_case)
assert det_res["status"] == "completed", f"Detective failed: {det_res['error']}"
det_report = det_res["report"]
print(f"✓ Detective Report generated ({len(det_report)} chars)")
print(f"Summary preview: {det_report[:180]}...")

# STEP 4: Run Evidence Agent
print("\n[STEP 4/7] 🔎 Running Evidence Analysis...")
from app.agents.evidence_agent import run_evidence_agent
evi_res = run_evidence_agent(visible_case, det_report)
assert evi_res["status"] == "completed", f"Evidence Agent failed: {evi_res['error']}"
evi_report = evi_res["report"]
print(f"✓ Evidence Report generated ({len(evi_report)} chars)")
print(f"Strongest Evidence: {evi_res.get('strongest_evidence', [])[:2]}")

# STEP 5: Run Suspect Agent
print("\n[STEP 5/7] 👤 Running Suspect Analysis...")
from app.agents.suspect_agent import run_suspect_agent
sus_res = run_suspect_agent(visible_case, det_report, evi_report)
assert sus_res["status"] == "completed", f"Suspect Agent failed: {sus_res['error']}"
sus_report = sus_res["report"]
print(f"✓ Suspect Report generated ({len(sus_report)} chars)")
print(f"Provisional Ranking: {sus_res.get('ranking', [])[:3]}")

# STEP 6: Run Skeptic Agent
print("\n[STEP 6/7] 🧠 Running Skeptic Challenge...")
from app.agents.skeptic_agent import run_skeptic_agent
ske_res = run_skeptic_agent(visible_case, det_report, evi_report, sus_report)
assert ske_res["status"] == "completed", f"Skeptic Agent failed: {ske_res['error']}"
ske_report = ske_res["report"]
print(f"✓ Skeptic Report generated ({len(ske_report)} chars)")
print(f"Skeptic Assessment: {ske_res.get('skeptic_assessment', {})}")

# STEP 7: Run Chief Agent
print("\n[STEP 7/7] 👨‍⚖️ Running Chief Investigation...")
from app.agents.chief_agent import run_chief_agent
chief_res = run_chief_agent(visible_case, det_report, evi_report, sus_report, ske_report)
assert chief_res["status"] == "completed", f"Chief Agent failed: {chief_res['error']}"
chief_report = chief_res["report"]
print(f"✓ Chief Report generated ({len(chief_report)} chars)")
print(f"Chief Confidence: {chief_res.get('confidence_assessment', {})}")
print(f"Provisional Assessment: {chief_res.get('final_provisional_assessment', {})}")

print("\n============================================================")
print("🎉 FULL 7-STAGE MULTI-AGENT PIPELINE COMPLETED SUCCESSFULLY!")
print("============================================================")
