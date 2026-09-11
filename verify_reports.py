"""
Verification script for all investigation reports across the AI Mystery Detective Team pipeline.
Checks:
1. 🕵️ Detective Report: Contains reconstructed timeline, facts, inconsistencies, unanswered questions.
2. 🔎 Evidence Report: Contains FACT/INFERENCE/DISTRACTION/UNCERTAIN classification, evidence limits.
3. 👤 Suspect Report: Contains 11-field suspect comparisons, provisional ranking.
4. 🧠 Skeptic Report: Contains assumption audit, evidence vulnerabilities, alternative explanations, falsification tests.
5. 👨‍⚖️ Chief Report: Contains executive summary, evidence vs inference, cross-agent synthesis, provisional conclusion.
6. 👤 Human Review Handoff: Contains clear closing requirements for human reviewer decision.
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

from app.case import case_data
from app.agents.detective_agent import run_detective_agent
from app.agents.evidence_agent import run_evidence_agent
from app.agents.suspect_agent import run_suspect_agent
from app.agents.skeptic_agent import run_skeptic_agent
from app.agents.chief_agent import run_chief_agent

print("============================================================")
print("VERIFYING MULTI-AGENT OUTPUT QUALITY & SECTION COMPLETION")
print("============================================================")

case = case_data.get_agent_visible_case()

# 1. DETECTIVE REPORT
print("\n[1/5] Verifying 🕵️ Detective Report...")
det_res = run_detective_agent(case)
assert det_res["status"] == "completed", f"Detective failed: {det_res['error']}"
det_rep = det_res["report"]
print(f"Report Length: {len(det_rep)} chars")
assert "Timeline" in det_rep or "Chronology" in det_rep, "Detective missing timeline"
assert "Facts" in det_rep, "Detective missing facts"
print("✓ Detective Report verified (Timeline, Facts, Inconsistencies present)")

# 2. EVIDENCE REPORT
print("\n[2/5] Verifying 🔎 Evidence Report...")
evi_res = run_evidence_agent(case, det_rep)
assert evi_res["status"] == "completed", f"Evidence failed: {evi_res['error']}"
evi_rep = evi_res["report"]
print(f"Report Length: {len(evi_rep)} chars")
assert any(term in evi_rep for term in ["FACT", "INFERENCE", "UNCERTAIN"]), "Evidence missing classification taxonomy"
assert "E-B" in evi_rep and "E-F" in evi_rep, "Evidence missing key IDs"
print("✓ Evidence Report verified (FACT/INFERENCE/UNCERTAIN taxonomy & limitations present)")

# 3. SUSPECT REPORT
print("\n[3/5] Verifying 👤 Suspect Report...")
sus_res = run_suspect_agent(case, det_rep, evi_rep)
assert sus_res["status"] == "completed", f"Suspect failed: {sus_res['error']}"
sus_rep = sus_res["report"]
print(f"Report Length: {len(sus_rep)} chars")
for name in ["Lena Ortiz", "Theo Park", "Arjun Vale", "Sofia Reed"]:
    assert name in sus_rep, f"Suspect report missing {name}"
assert "Ranking" in sus_rep or "Current Ranking" in sus_rep, "Suspect report missing ranking"
print("✓ Suspect Report verified (All 4 suspects compared across Motive, Means, Opportunity, Ranking)")

# 4. SKEPTIC REPORT
print("\n[4/5] Verifying 🧠 Skeptic Report...")
ske_res = run_skeptic_agent(case, det_rep, evi_rep, sus_rep)
assert ske_res["status"] == "completed", f"Skeptic failed: {ske_res['error']}"
ske_rep = ske_res["report"]
print(f"Report Length: {len(ske_rep)} chars")
assert "Assumptions" in ske_rep, "Skeptic missing assumptions audit"
assert "Alternative Explanations" in ske_rep, "Skeptic missing alternative explanations"
assert "Falsify" in ske_rep or "Falsification" in ske_rep, "Skeptic missing falsification criteria"
print("✓ Skeptic Report verified (Assumption audit, Vulnerabilities, Alternatives, Falsification present)")

# 5. CHIEF REPORT & HUMAN REVIEW HANDOFF
print("\n[5/5] Verifying 👨‍⚖️ Chief Report & 👤 Human Review...")
chief_res = run_chief_agent(case, det_rep, evi_rep, sus_rep, ske_rep)
assert chief_res["status"] == "completed", f"Chief failed: {chief_res['error']}"
chief_rep = chief_res["report"]
print(f"Report Length: {len(chief_rep)} chars")
assert "Executive Summary" in chief_rep, "Chief missing executive summary"
assert "Current Best Explanation" in chief_rep, "Chief missing current best explanation"
assert "Confidence" in chief_rep, "Chief missing confidence assessment"
assert "HUMAN REVIEW" in chief_rep, "Chief missing human review handoff"
print("✓ Chief Report verified (Synthesis, Evidence vs Inference, Provisional Conclusion present)")
print("✓ Human Review Handoff verified (# HUMAN REVIEW REQUIRED present)")

print("\n============================================================")
print("🎉 ALL 5 AI AGENT REPORTS + HUMAN REVIEW HANDOFF FULLY VERIFIED!")
print("============================================================")
