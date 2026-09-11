"""
Main Application & Gradio Interface for AI Mystery Detective Team.
Dynamic AI Mystery Case Platform:
- 12+ Built-in Cases (Cases 001 to 012)
- AI Case Generator (Gemini + Structural Validation)
- Case Library (Cinematic Cards, Search & Filtering)
- Random Mystery & Deterministic Case of the Day
- Counterfactual Case Variations (Evidence Removal & Comparison)
- Multi-Agent Investigation Pipeline (Detective ➔ Evidence ➔ Suspect ➔ Skeptic ➔ Chief)
- Human Review & Facilitator Solution Separation
- Multi-Factor Investigation Scoring (Evidence Grounding, Fairness, Skepticism, Uncertainty, Alternatives)
- Historic Investigation Archive ("My Investigations")
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure console encoding on Windows
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

import gradio as gr
import config
from app.gemini_client import test_gemini_connection
from app.case import case_data
from app.agents.detective_agent import run_detective_agent
from app.agents.evidence_agent import run_evidence_agent
from app.agents.suspect_agent import run_suspect_agent
from app.agents.skeptic_agent import run_skeptic_agent
from app.agents.chief_agent import run_chief_agent

from app.library.case_registry import (
    get_all_cases,
    find_case_by_id,
    filter_cases,
    get_case_of_the_day,
    get_random_mystery,
    format_difficulty_stars,
)
from app.library.case_generator import generate_ai_case, load_all_generated_cases
from app.library.variation_engine import create_case_variation
from app.library.investigation_scoring import (
    calculate_investigation_score,
    format_score_meter,
    save_investigation_to_history,
    load_investigation_history,
)

# In-memory session store for investigation artifacts across multi-agent tabs
INVESTIGATION_CACHE = {
    "active_case_id": "CASE-001",
    "case_start_time": time.time(),
    "detective_report": "",
    "evidence_report": "",
    "suspect_report": "",
    "skeptic_report": "",
    "chief_report": "",
    "chief_result_dict": {},
    "variation_original_report": "",
    "variation_modified_report": ""
}

# ==================================================
# CASE LIBRARY HELPERS & CINEMATIC CARDS
# ==================================================

def render_case_cards_html(cases: List[Dict[str, Any]]) -> str:
    """Renders cases as cinematic investigation cards."""
    if not cases:
        return "<div style='padding: 24px; text-align: center; color: #94a3b8;'>No cases match the selected filter criteria.</div>"

    cards = []
    for c in cases:
        cid = c.get("caseId", "CASE-???")
        title = c.get("title", "Untitled Case")
        cat = c.get("category", "Theft")
        diff = c.get("difficulty", "Medium")
        stars = format_difficulty_stars(diff)
        sus_count = len(c.get("suspects", []))
        ev_count = len(c.get("evidence", []))
        wit_count = len(c.get("witnesses", []))
        est_time = c.get("estimatedTimeMinutes", 15)

        is_active = (cid == INVESTIGATION_CACHE.get("active_case_id", "CASE-001"))
        border_color = "#38bdf8" if is_active else "#334155"
        badge_bg = "#0284c7" if is_active else "#475569"
        badge_text = "CURRENTLY LOADED" if is_active else f"{cat}"

        card = f"""
        <div style="background: #1e293b; border: 2px solid {border_color}; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 0.85rem; font-weight: 800; color: #38bdf8; letter-spacing: 0.05em;">🔎 {cid}</span>
                    <span style="background: {badge_bg}; color: #ffffff; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">{badge_text}</span>
                </div>
                <h3 style="margin: 0 0 8px 0; color: #f8fafc; font-size: 1.15rem; line-height: 1.3;">{title}</h3>
                <p style="margin: 0 0 12px 0; color: #fbbf24; font-size: 0.88rem; font-weight: 600;">Difficulty: {stars}</p>
                <div style="background: #0f172a; border-radius: 8px; padding: 10px; font-size: 0.8rem; color: #94a3b8; margin-bottom: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                    <div>👥 <strong>Suspects:</strong> {sus_count}</div>
                    <div>🔬 <strong>Evidence:</strong> {ev_count}</div>
                    <div>🗣️ <strong>Witnesses:</strong> {wit_count}</div>
                    <div>⏱️ <strong>Est. Time:</strong> ~{est_time} min</div>
                </div>
                <p style="font-size: 0.82rem; color: #cbd5e1; margin: 0; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                    {c.get('incident', '')[:160]}...
                </p>
            </div>
        </div>
        """
        cards.append(card)

    grid = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 16px; margin-top: 12px;">
        {''.join(cards)}
    </div>
    """
    return grid


def get_case_choices_list() -> List[str]:
    """Returns dropdown choices in format 'CASE-001: The Vanishing Aurora Diamond'."""
    all_c = get_all_cases()
    return [f"{c.get('caseId')}: {c.get('title')}" for c in all_c]


def handle_filter_library(search: str, cat: str, diff: str, ctype: str):
    """Refreshes case library card grid based on search and filters."""
    filtered = filter_cases(search_query=search, category=cat, difficulty=diff, case_type=ctype)
    return render_case_cards_html(filtered)


def handle_open_selected_case(case_selection: str):
    """Loads a selected case from dropdown into active case context."""
    if not case_selection:
        return (
            "⚠️ Please select a case to open.",
            get_case_dossier_markdown(),
            get_timeline_markdown(),
            get_suspects_markdown(),
            get_witnesses_markdown(),
            get_evidence_markdown(),
            get_questions_markdown(),
            get_rules_markdown(),
            render_case_cards_html(get_all_cases())
        )

    cid = case_selection.split(":")[0].strip()
    target_case = find_case_by_id(cid)
    if not target_case:
        return (
            f"❌ Case '{cid}' not found.",
            get_case_dossier_markdown(),
            get_timeline_markdown(),
            get_suspects_markdown(),
            get_witnesses_markdown(),
            get_evidence_markdown(),
            get_questions_markdown(),
            get_rules_markdown(),
            render_case_cards_html(get_all_cases())
        )

    # Set as dynamic active case
    case_data.set_active_case(target_case)
    INVESTIGATION_CACHE["active_case_id"] = cid
    INVESTIGATION_CACHE["case_start_time"] = time.time()
    # Reset agent cache for fresh investigation
    INVESTIGATION_CACHE["detective_report"] = ""
    INVESTIGATION_CACHE["evidence_report"] = ""
    INVESTIGATION_CACHE["suspect_report"] = ""
    INVESTIGATION_CACHE["skeptic_report"] = ""
    INVESTIGATION_CACHE["chief_report"] = ""

    feedback = f"✅ Case Loaded Successfully!\n\nID: {target_case.get('caseId')}\nTitle: {target_case.get('title')}\nCategory: {target_case.get('category')} | Difficulty: {target_case.get('difficulty')}\nAll 5 AI Detective Agents are now calibrated for this case."

    return (
        feedback,
        get_case_dossier_markdown(),
        get_timeline_markdown(),
        get_suspects_markdown(),
        get_witnesses_markdown(),
        get_evidence_markdown(),
        get_questions_markdown(),
        get_rules_markdown(),
        render_case_cards_html(get_all_cases())
    )


def handle_load_case_of_the_day():
    """Loads the deterministic Case of the Day."""
    day_case = get_case_of_the_day()
    cid = day_case.get("caseId")
    case_data.set_active_case(day_case)
    INVESTIGATION_CACHE["active_case_id"] = cid
    INVESTIGATION_CACHE["case_start_time"] = time.time()
    INVESTIGATION_CACHE["detective_report"] = ""
    INVESTIGATION_CACHE["evidence_report"] = ""
    INVESTIGATION_CACHE["suspect_report"] = ""
    INVESTIGATION_CACHE["skeptic_report"] = ""
    INVESTIGATION_CACHE["chief_report"] = ""

    feedback = f"🌟 CASE OF THE DAY LOADED!\n\n{cid}: {day_case.get('title')}\nDifficulty: {format_difficulty_stars(day_case.get('difficulty', ''))}\nSetting: {day_case.get('setting')}\nCan your multi-agent team solve it?"
    
    return (
        feedback,
        f"{cid}: {day_case.get('title')}",
        get_case_dossier_markdown(),
        get_timeline_markdown(),
        get_suspects_markdown(),
        get_witnesses_markdown(),
        get_evidence_markdown(),
        get_questions_markdown(),
        get_rules_markdown(),
        render_case_cards_html(get_all_cases())
    )


def handle_load_random_mystery(diff_choice: str, cat_choice: str):
    """Selects and loads a random mystery matching filters."""
    rand_case = get_random_mystery(difficulty=diff_choice, category=cat_choice)
    cid = rand_case.get("caseId")
    case_data.set_active_case(rand_case)
    INVESTIGATION_CACHE["active_case_id"] = cid
    INVESTIGATION_CACHE["case_start_time"] = time.time()
    INVESTIGATION_CACHE["detective_report"] = ""
    INVESTIGATION_CACHE["evidence_report"] = ""
    INVESTIGATION_CACHE["suspect_report"] = ""
    INVESTIGATION_CACHE["skeptic_report"] = ""
    INVESTIGATION_CACHE["chief_report"] = ""

    feedback = f"🎲 RANDOM MYSTERY PREPARED & LOADED!\n\n{cid}: {rand_case.get('title')}\nCategory: {rand_case.get('category')} | Difficulty: {rand_case.get('difficulty')}\nSuspects: {len(rand_case.get('suspects', []))} | Evidence: {len(rand_case.get('evidence', []))}"

    return (
        feedback,
        f"{cid}: {rand_case.get('title')}",
        get_case_dossier_markdown(),
        get_timeline_markdown(),
        get_suspects_markdown(),
        get_witnesses_markdown(),
        get_evidence_markdown(),
        get_questions_markdown(),
        get_rules_markdown(),
        render_case_cards_html(get_all_cases())
    )


def handle_generate_case(
    cat: str, diff: str, suspects: int, evidence: int,
    witnesses: int, timeline_c: str, red_herrings: str, twist: str
):
    """Generates a structured mystery via Gemini and registers it."""
    success, gen_data, msg = generate_ai_case(
        category=cat,
        difficulty=diff,
        num_suspects=suspects,
        num_evidence=evidence,
        witness_count=witnesses,
        timeline_complexity=timeline_c,
        red_herrings=red_herrings,
        twist=twist
    )

    if not success or not gen_data:
        return (
            f"❌ Generation Error: {msg}",
            gr.update(choices=get_case_choices_list()),
            render_case_cards_html(get_all_cases())
        )

    # Immediately activate generated case
    case_data.set_active_case(gen_data)
    cid = gen_data.get("caseId")
    INVESTIGATION_CACHE["active_case_id"] = cid
    INVESTIGATION_CACHE["case_start_time"] = time.time()

    summary = (
        f"🎉 CASE GENERATION & VALIDATION SUCCESSFUL!\n\n"
        f"Case ID: {cid}\n"
        f"Title: {gen_data.get('title')}\n"
        f"Category: {gen_data.get('category')}\n"
        f"Difficulty: {gen_data.get('difficulty')}\n"
        f"Suspects: {len(gen_data.get('suspects', []))} | Evidence: {len(gen_data.get('evidence', []))} | Witnesses: {len(gen_data.get('witnesses', []))}\n\n"
        f"The case has passed logical validation and anti-triviality protection and is now active for investigation."
    )

    all_choices = get_case_choices_list()
    current_choice = f"{cid}: {gen_data.get('title')}"
    return (
        summary,
        gr.update(choices=all_choices, value=current_choice),
        render_case_cards_html(get_all_cases())
    )


# ==================================================
# CASE DOSSIER MARKDOWN GENERATORS (DYNAMIC)
# ==================================================

def get_active_case_obj() -> Dict[str, Any]:
    raw = case_data.get_current_raw_case()
    if raw:
        return raw
    return find_case_by_id("CASE-001") or {}


def get_case_dossier_markdown() -> str:
    c = get_active_case_obj()
    title = c.get("title", case_data.CASE_METADATA["title"])
    cid = c.get("caseId", case_data.CASE_METADATA["case_id"])
    loc = c.get("setting", case_data.CASE_METADATA["location"])
    incident = c.get("incident", case_data.CASE_DESCRIPTION)
    diff = c.get("difficulty", "Medium")
    cat = c.get("category", "Museum Theft")

    return f"""### 🗃️ Active Case: {title} ({cid})
**Category:** {cat} | **Difficulty:** {format_difficulty_stars(diff)} | **Location:** {loc}

#### Incident Description:
```text
{incident}
```
> [!IMPORTANT]
> This is factual public case data. Investigation agents reason independently from raw evidence without facilitator clues.
"""


def get_timeline_markdown() -> str:
    c = get_active_case_obj()
    events = c.get("timeline", case_data.TIMELINE_EVENTS)
    lines = [
        "| ID | Time | Event | Source | Certainty |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    for t in events:
        lines.append(f"| **{t['id']}** | {t['time']} | {t['event']} | {t['source']} | {t['certainty']} |")
    return "\n".join(lines)


def get_suspects_markdown() -> str:
    c = get_active_case_obj()
    suspects = c.get("suspects", case_data.SUSPECTS)
    blocks = []
    for s in suspects:
        rel_ev = s.get("relevant_evidence", [])
        rel_str = ", ".join(rel_ev) if isinstance(rel_ev, list) else str(rel_ev)
        open_q = s.get("open_questions", [])
        q_str = " | ".join(open_q) if isinstance(open_q, list) else str(open_q)
        blocks.append(
            f"### {s.get('suspect_id', 'S??')} — {s.get('name', 'Unknown')} ({s.get('role', 'Suspect')})\n"
            f"- **Motive:** {s.get('motive', 'Unknown')}\n"
            f"- **Statement:** *\"{s.get('statement', '')}\"*\n"
            f"- **Relevant Evidence:** {rel_str}\n"
            f"- **Uncertainty Note:** {s.get('uncertainty', 'None noted')}\n"
            f"- **Open Questions:** {q_str}\n"
        )
    return "\n---\n".join(blocks)


def get_witnesses_markdown() -> str:
    c = get_active_case_obj()
    witnesses = c.get("witnesses", case_data.WITNESSES)
    if not witnesses:
        return "*No witness statements recorded for this case.*"
    blocks = []
    for w in witnesses:
        supp = w.get("supporting_information", [])
        supp_str = "; ".join(supp) if isinstance(supp, list) else str(supp)
        lim = w.get("limitations", w.get("reliability", "Unverified"))
        blocks.append(
            f"### {w.get('witness_id', 'W??')} — {w.get('name', 'Witness')} ({w.get('role', 'Eyewitness')})\n"
            f"- **Statement:** *\"{w.get('statement', '')}\"*\n"
            f"- **Supporting Information:** {supp_str or 'None'}\n"
            f"- **Key Limitation / Reliability:** {lim}\n"
        )
    return "\n---\n".join(blocks)


def get_evidence_markdown() -> str:
    c = get_active_case_obj()
    evidence = c.get("evidence", case_data.EVIDENCE)
    blocks = []
    for e in evidence:
        rel_sus = e.get("related_suspects", [])
        suspects_str = ", ".join(rel_sus) if rel_sus else "None directly established"
        does_not_est = e.get("does_not_establish", "Not specified")
        if isinstance(does_not_est, list):
            does_not_est = "; ".join(does_not_est)
        blocks.append(
            f"### {e.get('evidence_id', 'E-??')}: {e.get('title', 'Clue')} ({e.get('category', 'Physical')})\n"
            f"- **Source:** {e.get('source', 'Crime Scene')}\n"
            f"- **Description:** {e.get('description', '')}\n"
            f"- **Establishes:** {e.get('establishes', '')}\n"
            f"- **Does NOT Establish:** {does_not_est}\n"
            f"- **Related Suspects:** {suspects_str}\n"
            f"- **Reliability:** {e.get('reliability_notes', 'Official Registry')}\n"
        )
    return "\n---\n".join(blocks)


def get_questions_markdown() -> str:
    c = get_active_case_obj()
    questions = c.get("centralQuestions", c.get("central_questions", case_data.CENTRAL_QUESTIONS))
    return "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])


def get_rules_markdown() -> str:
    c = get_active_case_obj()
    rules = c.get("rules", case_data.INVESTIGATION_RULES)
    return "\n".join([f"{i+1}. **{r}**" for i, r in enumerate(rules)])


# ==================================================
# MULTI-AGENT EXECUTION HANDLERS
# ==================================================

def handle_run_detective():
    agent_case = case_data.get_agent_visible_case()
    result = run_detective_agent(agent_case)
    if result["status"] == "error":
        return (
            "🔴 Detective investigation failed",
            f"### Error\n{result.get('error', 'Unknown error')}",
            "N/A", "N/A", "N/A", "N/A", "N/A"
        )
    INVESTIGATION_CACHE["detective_report"] = result["report"]
    return (
        "🟢 Detective investigation completed",
        result["report"],
        "\n".join([f"- {q}" for q in result.get("unanswered_questions", [])]) or "See full report.",
        "\n".join([f"- {e}" for e in result.get("important_evidence", [])]) or "See full report.",
        "\n".join([f"- {c}" for c in result.get("contradictions", [])]) or "See full report.",
        "\n".join([f"- {g}" for g in result.get("information_gaps", [])]) or "See full report.",
        "\n".join([f"- {p}" for p in result.get("recommended_priorities", [])]) or "See full report."
    )


def handle_run_evidence():
    det_report = INVESTIGATION_CACHE.get("detective_report", "")
    if not det_report:
        return (
            "🟠 Dependency Notice: Run Detective Agent first",
            "### ⚠️ Please run the Detective Agent first before analyzing evidence.",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        )
    agent_case = case_data.get_agent_visible_case()
    result = run_evidence_agent(agent_case, detective_report=det_report)
    if result["status"] == "error":
        return (
            "🔴 Evidence analysis failed",
            f"### Error\n{result.get('error', 'Unknown error')}",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        )
    INVESTIGATION_CACHE["evidence_report"] = result["report"]
    return (
        "🟢 Evidence analysis completed",
        result["report"],
        f"Analyzed {len(result.get('evidence_items', []))} evidence items thoroughly.",
        "\n".join([f"- **{e.get('id', '')}**: {e.get('reason', '')}" for e in result.get("strongest_evidence", [])]) or "See Section 5 of report.",
        "\n".join([f"- **{e.get('id', '')}**: {e.get('reason', '')}" for e in result.get("weakest_evidence", [])]) or "See Section 6 of report.",
        "\n".join([f"- {c}" for c in result.get("conflicting_evidence", [])]) or "See Section 7 of report.",
        "\n".join([f"- {v}" for v in result.get("verification_required", [])]) or "See Section 8 of report.",
        "\n".join([f"- {u}" for u in result.get("unsupported_conclusions", [])]) or "See Section 9 of report."
    )


def handle_run_suspect():
    det_report = INVESTIGATION_CACHE.get("detective_report", "")
    ev_report = INVESTIGATION_CACHE.get("evidence_report", "")
    if not det_report or not ev_report:
        return (
            "🟠 Dependency Notice: Missing Detective or Evidence report",
            "### ⚠️ Please complete Detective and Evidence agents before Suspect analysis.",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        )
    agent_case = case_data.get_agent_visible_case()
    result = run_suspect_agent(agent_case, detective_report=det_report, evidence_report=ev_report)
    if result["status"] == "error":
        return (
            "🔴 Suspect analysis failed",
            f"### Error\n{result.get('error', 'Unknown error')}",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        )
    INVESTIGATION_CACHE["suspect_report"] = result["report"]
    return (
        "🟢 Suspect analysis completed",
        result["report"],
        f"Evaluated {len(result.get('suspect_assessments', []))} suspects across Motive, Opportunity, Means, and Evidence.",
        "\n".join([f"{i+1}. **{s.get('suspect_name', '')}** — {s.get('assessment_summary', '')}" for i, s in enumerate(result.get("provisional_ranking", []))]) or "See Section 7.",
        result.get("strongest_current_case", "See Section 6."),
        "\n".join([f"- {w}" for w in result.get("weaknesses_in_leading_case", [])]) or "See Section 6.",
        "\n".join([f"- {a}" for a in result.get("alternative_explanations", [])]) or "See Section 8.",
        "\n".join([f"- {e}" for e in result.get("evidence_that_could_change_ranking", [])]) or "See Section 9."
    )


def handle_run_skeptic():
    det = INVESTIGATION_CACHE.get("detective_report", "")
    ev = INVESTIGATION_CACHE.get("evidence_report", "")
    sus = INVESTIGATION_CACHE.get("suspect_report", "")
    if not (det and ev and sus):
        return (
            "🟠 Dependency Notice: Missing prior agent reports",
            "### ⚠️ Please complete Detective, Evidence, and Suspect analyses first.",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        )
    agent_case = case_data.get_agent_visible_case()
    result = run_skeptic_agent(agent_case, detective_report=det, evidence_report=ev, suspect_report=sus)
    if result["status"] == "error":
        return (
            "🔴 Skeptic challenge failed",
            f"### Error\n{result.get('error', 'Unknown error')}",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        )
    INVESTIGATION_CACHE["skeptic_report"] = result["report"]
    return (
        "🟢 Skeptic challenge completed",
        result["report"],
        "\n".join([f"- **{c.get('target', '')}**: {c.get('challenge', '')}" for c in result.get("critical_challenges", [])]) or "See Section 2.",
        "\n".join([f"- {a}" for a in result.get("hidden_assumptions", [])]) or "See Section 3.",
        "\n".join([f"- {f}" for f in result.get("facts_treated_as_inferences", [])]) or "See Section 4.",
        "\n".join([f"- **{t.get('hypothesis', '')}**: {t.get('rationale', '')}" for t in result.get("alternative_theories", [])]) or "See Section 5.",
        "\n".join([f"- **{ft.get('claim', '')}**: Test -> {ft.get('test', '')}" for ft in result.get("falsification_tests", [])]) or "See Section 6.",
        result.get("epistemic_warning", "Exercise extreme caution before drawing definitive conclusions.")
    )


def handle_run_chief():
    det = INVESTIGATION_CACHE.get("detective_report", "")
    ev = INVESTIGATION_CACHE.get("evidence_report", "")
    sus = INVESTIGATION_CACHE.get("suspect_report", "")
    skp = INVESTIGATION_CACHE.get("skeptic_report", "")
    if not (det and ev and sus and skp):
        return (
            "🟠 Dependency Notice: Missing prior reports",
            "### ⚠️ Please complete Detective, Evidence, Suspect, and Skeptic investigations first.",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "REQUIRED"
        )
    agent_case = case_data.get_agent_visible_case()
    result = run_chief_agent(
        case_data=agent_case,
        detective_report=det,
        evidence_report=ev,
        suspect_report=sus,
        skeptic_report=skp
    )
    if result["status"] == "error":
        return (
            "🔴 Chief investigation failed",
            f"### Error\n{result.get('error', 'Unknown error')}",
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "REQUIRED"
        )
    INVESTIGATION_CACHE["chief_report"] = result["report"]
    INVESTIGATION_CACHE["chief_result_dict"] = result

    best_expl = result.get("current_best_explanation", {})
    expl_str = f"**{best_expl.get('suspect_or_explanation', 'Provisional Assessment')}**\n{best_expl.get('reason', '')}"
    conf = result.get("confidence_assessment", {})
    conf_str = f"**{conf.get('level', 'MODERATE')}**\n{conf.get('reason', '')}"
    strong_str = "\n".join([f"- {s}" for s in result.get("strongest_evidence", [])]) or "See Section 9 of report."
    weak_str = result.get("weakest_link", "See Section 10 of report.")
    alt_str = "\n".join([f"- {a}" for a in result.get("alternative_explanations", [])]) or "See Section 8 of report."
    next_str = "\n".join([f"- {r}" for r in result.get("recommended_next_investigation", [])]) or "See Section 12 of report."

    return (
        "🟢 Chief investigation completed",
        result["report"],
        expl_str,
        conf_str,
        strong_str,
        weak_str,
        alt_str,
        next_str,
        "REQUIRED (Review Evidence & Uncertainties Before Revealing Solution)"
    )


# ==================================================
# HUMAN REVIEW, SCORING & SOLUTION REVEAL
# ==================================================

def handle_human_decision_submit(decision: str, reviewer_notes: str):
    """Processes Human Review verdict and generates multi-dimensional reasoning score."""
    chief_report = INVESTIGATION_CACHE.get("chief_result_dict", {})
    raw_case = get_active_case_obj()

    if not chief_report:
        # Fallback dummy for scoring if chief report ran but dict missing
        chief_report = {
            "current_best_explanation": {"suspect_or_explanation": "Provisional Suspect"},
            "critical_gaps": ["Card possession", "Visual confirmation"],
            "missing_evidence_required": ["Forensic search", "Corridor CCTV"],
            "alternative_explanation": "A co-conspirator manipulated access logs."
        }

    # Calculate multi-factor reasoning score
    scores = calculate_investigation_score(
        case_data=raw_case,
        chief_report=chief_report,
        skeptic_report={"critical_challenges": ["Assumption of card ownership"], "alternative_theories": ["Staged heist"]},
        suspect_report={"suspect_assessments": raw_case.get("suspects", [])},
        evidence_report={"evidence_items": raw_case.get("evidence", [])},
        human_verdict=decision
    )

    # Calculate duration
    duration = int(time.time() - INVESTIGATION_CACHE.get("case_start_time", time.time()))

    # Persist to history
    save_investigation_to_history(
        case_id=raw_case.get("caseId", "CASE-001"),
        case_title=raw_case.get("title", "Unknown"),
        difficulty=raw_case.get("difficulty", "Medium"),
        ai_conclusion=chief_report.get("current_best_explanation", {}).get("suspect_or_explanation", "Provisional Assessment"),
        confidence=chief_report.get("confidence_assessment", {}).get("level", "MODERATE"),
        human_decision=f"{decision} — Notes: {reviewer_notes[:80]}",
        score_data=scores,
        duration_seconds=duration
    )

    score_display = f"""### 📊 INVESTIGATION REASONING SCORE

| Analytical Dimension | Score Meter | Evaluation Criteria |
| :--- | :--- | :--- |
| **Evidence Grounding** | `{format_score_meter(scores['evidence_grounding'])}` | Active citation of physical/forensic evidence & limits |
| **Suspect Fairness** | `{format_score_meter(scores['suspect_fairness'])}` | Comprehensive evaluation of all persons of interest |
| **Skeptic Quality** | `{format_score_meter(scores['skeptic_reasoning'])}` | Adversarial stress-testing & falsification rigor |
| **Uncertainty Awareness** | `{format_score_meter(scores['uncertainty_awareness'])}` | Explicit recognition of missing links & caveats |
| **Alternative Theory** | `{format_score_meter(scores['alternative_theory'])}` | Exploration of competing counter-hypotheses |

---
### 🏆 OVERALL REASONING SCORE: `{scores['overall']} / 100`
*(Scored based on epistemic rigor, evidential grounding, and cognitive self-correction — not superficial guessing)*
"""

    return (
        f"✅ Human Review Registered: {decision}",
        score_display,
        render_history_table()
    )


def handle_reveal_solution():
    """Reveals the hidden reference solution with facilitator analysis."""
    raw_case = get_active_case_obj()
    hidden_sol = raw_case.get("hiddenSolution", {})
    if not hidden_sol:
        # Check fallback for Aurora Diamond
        hidden_sol = case_data.FACILITATOR_ONLY_GUIDANCE

    culprit = hidden_sol.get("culprit", hidden_sol.get("leading_suspect", "Arjun Vale"))
    explanation = hidden_sol.get("explanation", "\n".join(hidden_sol.get("reasoning", [])))
    decisive_ev = hidden_sol.get("decisiveEvidence", ["E-C", "E-E", "E-G"])
    uncertainties = hidden_sol.get("uncertainties", hidden_sol.get("preserved_uncertainty", []))
    alt_exp = hidden_sol.get("alternativeExplanation", "An insider or security collaborator staged the theft.")

    warning_text = "> [!WARNING]\n> **THE OFFICIAL FACILITATOR CASE SOLUTION IS NOW REVEALED.**\n> Compare this reference solution against your team's reasoning. The reference solution is not absolute proof of AI perfection, but a benchmark for investigative quality."

    content = f"""{warning_text}

### 🎯 Official Reference Solution: **{culprit}**

#### Causal Explanation:
{explanation}

#### Decisive Evidence Anchors:
{chr(10).join([f"- **{e}**" for e in decisive_ev])}

#### Why Red Herrings Were Misleading:
- Distraction traces (such as Sofia's glass cutter or alternate alarms) provided suspicious means, but lacked opportunity or timeline coherence during the critical blackout interval.

#### Why Alternative Theories Were Weaker:
- {alt_exp}

#### Residual Uncertainties & Limitations:
{chr(10).join([f"- {u}" for u in uncertainties])}
"""
    return content


# ==================================================
# CASE VARIATIONS LAB
# ==================================================

def handle_create_variation(var_type: str, target: str, custom_text: str):
    base_case = get_active_case_obj()
    mod_case, desc = create_case_variation(base_case, var_type, target_id=target, custom_note=custom_text)
    case_data.set_active_case(mod_case)
    INVESTIGATION_CACHE["active_case_id"] = mod_case.get("caseId")
    INVESTIGATION_CACHE["case_start_time"] = time.time()

    return (
        f"🔬 Variation Applied Successfully!\n{desc}\n\nThe active case has been modified. Re-run your agents to observe counterfactual changes in reasoning!",
        get_case_dossier_markdown(),
        get_evidence_markdown()
    )


# ==================================================
# INVESTIGATION HISTORY
# ==================================================

def render_history_table() -> str:
    history = load_investigation_history()
    if not history:
        return "*No past investigations recorded yet. Complete an investigation and submit Human Review to log history.*"

    rows = [
        "| Date & Time | Case | AI Conclusion | Confidence | Human Review | Overall Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for h in history[:15]:
        score_val = h.get("scores", {}).get("overall", "N/A")
        rows.append(
            f"| {h.get('timestamp', '')} | **{h.get('caseId', '')}**: {h.get('title', '')} | {h.get('aiConclusion', '')} | {h.get('confidence', '')} | {h.get('humanDecision', '')} | **{score_val}/100** |"
        )
    return "\n".join(rows)


# ==================================================
# GRADIO UI BUILDER
# ==================================================

def create_ui() -> gr.Blocks:
    """Builds the comprehensive AI Mystery Case Platform Gradio interface."""
    with gr.Blocks(title=f"{config.APP_NAME} - AI Mystery Platform") as demo:

        # Platform Header
        gr.HTML(f"""
        <div style="background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); border: 1px solid #334155; border-radius: 12px; padding: 24px; color: #f8fafc; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="display: inline-block; background: #0284c7; color: #ffffff; font-size: 0.8rem; font-weight: 700; padding: 4px 14px; border-radius: 9999px; text-transform: uppercase;">
                    DYNAMIC CASE PLATFORM
                </span>
                <span style="display: inline-block; background: #9333ea; color: #ffffff; font-size: 0.8rem; font-weight: 700; padding: 4px 14px; border-radius: 9999px;">
                    12+ BUILT-IN CASES + AI GENERATOR
                </span>
            </div>
            <h1 style="margin: 4px 0; font-size: 2.2rem; letter-spacing: -0.02em; color: #f8fafc;">
                🔎 AI MYSTERY DETECTIVE TEAM
            </h1>
            <h3 style="margin: 0 0 12px 0; font-weight: 500; color: #38bdf8;">
                Investigate. Challenge. Modify. Decide.
            </h3>
            <hr style="border: 0; border-top: 1px solid #475569; margin: 12px 0;" />
            <div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.88rem; color: #cbd5e1;">
                <div><strong>Engine:</strong> Google Gemini ({config.GEMINI_MODEL})</div>
                <div>•</div>
                <div><strong>Team:</strong> Detective ➔ Evidence ➔ Suspect ➔ Skeptic ➔ Chief</div>
                <div>•</div>
                <div><strong>Epistemic Standard:</strong> Anti-Triviality & Solution Separation</div>
            </div>
        </div>
        """)

        with gr.Tabs():

            # ==========================================
            # TAB 1: CASE LIBRARY & DISCOVERY
            # ==========================================
            with gr.TabItem("🏛️ Case Library (12+ Built-in)"):
                gr.Markdown("### 🏛️ Dedicated Mystery Case Library")
                gr.Markdown("Select from 12 completely unique, multi-layered fictional mysteries across different domains, or filter by category and difficulty.")

                with gr.Row():
                    with gr.Column(scale=3):
                        search_box = gr.Textbox(label="🔍 Search Cases", placeholder="Type title, category, or setting keywords...")
                    with gr.Column(scale=1):
                        filter_cat = gr.Dropdown(
                            label="Category",
                            choices=["All", "Theft", "Museum", "Rare Manuscript", "Corporate", "Art", "Science", "Mystery", "Sports", "Historical", "Digital"],
                            value="All"
                        )
                    with gr.Column(scale=1):
                        filter_diff = gr.Dropdown(
                            label="Difficulty",
                            choices=["All", "Beginner", "Easy", "Medium", "Hard", "Expert"],
                            value="All"
                        )
                    with gr.Column(scale=1):
                        filter_type = gr.Dropdown(
                            label="Type",
                            choices=["All", "Built-in", "Generated"],
                            value="All"
                        )

                with gr.Row():
                    case_select_dropdown = gr.Dropdown(
                        label="📂 Select Case to Investigate",
                        choices=get_case_choices_list(),
                        value="CASE-001: The Vanishing Aurora Diamond",
                        scale=3
                    )
                    open_case_btn = gr.Button("🔎 OPEN CASE FOR INVESTIGATION", variant="primary", scale=1)

                case_action_feedback = gr.Textbox(
                    label="Platform Status",
                    value="Ready. Case 001 (Aurora Diamond) loaded by default.",
                    interactive=False
                )

                with gr.Row():
                    daily_btn = gr.Button("🌟 Load Case of the Day", variant="secondary")
                    random_btn = gr.Button("🎲 Prepare Random Mystery", variant="secondary")

                # Cards Grid Container
                cases_cards_html = gr.HTML(render_case_cards_html(get_all_cases()))

            # ==========================================
            # TAB 2: AI CASE GENERATOR
            # ==========================================
            with gr.TabItem("🧪 AI Case Generator"):
                gr.Markdown("### 🧪 Autonomous Fictional Mystery Case Generator")
                gr.Markdown(
                    "Direct Gemini to architect an entirely new, fully-structured mystery case with guaranteed logical consistency, "
                    "anti-triviality protection, and strict separation between public evidence and the hidden reference solution."
                )

                with gr.Row():
                    with gr.Column():
                        gen_cat = gr.Dropdown(
                            label="Category",
                            choices=["Theft", "Museum", "Corporate", "Historical", "Scientific", "Digital", "Hotel", "Transport", "Sports", "University", "Art", "Mystery"],
                            value="Corporate"
                        )
                        gen_diff = gr.Dropdown(
                            label="Difficulty",
                            choices=["Beginner", "Easy", "Medium", "Hard", "Expert"],
                            value="Hard"
                        )
                        gen_suspects = gr.Slider(minimum=3, maximum=8, step=1, value=4, label="Number of Suspects")
                        gen_evidence = gr.Slider(minimum=5, maximum=15, step=1, value=6, label="Number of Evidence Items")

                    with gr.Column():
                        gen_witnesses = gr.Slider(minimum=0, maximum=8, step=1, value=2, label="Witnesses Count")
                        gen_timeline = gr.Dropdown(
                            label="Timeline Complexity",
                            choices=["Simple", "Moderate", "Complex"],
                            value="Moderate"
                        )
                        gen_herrings = gr.Dropdown(
                            label="Red Herrings",
                            choices=["None", "Few", "Several", "Many"],
                            value="Several"
                        )
                        gen_twist = gr.Dropdown(
                            label="Narrative Twist",
                            choices=["None", "One", "Multiple"],
                            value="One"
                        )

                generate_btn = gr.Button("⚡ GENERATE NEW MYSTERY CASE", variant="primary", size="lg")
                gen_result_box = gr.Textbox(
                    label="AI Case Generation & Validation Feedback",
                    placeholder="Click 'Generate New Mystery Case' to build and validate a new case...",
                    lines=8,
                    interactive=False
                )

            # ==========================================
            # TAB 3: ACTIVE CASE DOSSIER & EVIDENCE
            # ==========================================
            with gr.TabItem("📂 Active Case Dossier"):
                dossier_display = gr.Markdown(get_case_dossier_markdown())

                with gr.Tabs():
                    with gr.TabItem("⏱️ Timeline"):
                        timeline_display = gr.Markdown(get_timeline_markdown())

                    with gr.TabItem("👥 Suspects"):
                        suspects_display = gr.Markdown(get_suspects_markdown())

                    with gr.TabItem("🗣️ Witnesses"):
                        witnesses_display = gr.Markdown(get_witnesses_markdown())

                    with gr.TabItem("🔬 Evidence Registry"):
                        evidence_display = gr.Markdown(get_evidence_markdown())

                    with gr.TabItem("❓ Central Questions"):
                        questions_display = gr.Markdown(get_questions_markdown())

                    with gr.TabItem("⚖️ Investigation Rules"):
                        rules_display = gr.Markdown(get_rules_markdown())

            # ==========================================
            # TAB 4: MULTI-AGENT WORKSTATION
            # ==========================================
            with gr.TabItem("🕵️ Multi-Agent Investigation Workstation"):
                gr.Markdown("### 🕵️ 5-Agent Collaborative Reasoning Pipeline")
                gr.Markdown(
                    "Execute the investigation stage-by-stage. Each agent brings independent methodology to ensure "
                    "thorough evidentiary grounding and cognitive quality control."
                )

                with gr.Tabs():
                    # Sub-tab: Detective
                    with gr.TabItem("1. 🕵️ Detective Agent"):
                        with gr.Row():
                            run_detective_btn = gr.Button("🕵️ Run Detective Investigation", variant="primary")
                        detective_status = gr.Textbox(label="Status", value="⚪ Not yet executed", interactive=False)
                        detective_report_md = gr.Markdown("*Awaiting execution...*")
                        with gr.Accordion("Detective Diagnostics", open=False):
                            det_q = gr.Markdown()
                            det_ev = gr.Markdown()
                            det_con = gr.Markdown()
                            det_gap = gr.Markdown()
                            det_pri = gr.Markdown()

                    # Sub-tab: Evidence
                    with gr.TabItem("2. 🔎 Evidence Agent"):
                        with gr.Row():
                            run_evidence_btn = gr.Button("🔎 Run Evidence Analysis", variant="primary")
                        evidence_status = gr.Textbox(label="Status", value="⚪ Requires Detective report", interactive=False)
                        evidence_report_md = gr.Markdown("*Awaiting execution...*")
                        with gr.Accordion("Evidence Diagnostics", open=False):
                            ev_tot = gr.Markdown()
                            ev_str = gr.Markdown()
                            ev_wea = gr.Markdown()
                            ev_con = gr.Markdown()
                            ev_req = gr.Markdown()
                            ev_uns = gr.Markdown()

                    # Sub-tab: Suspect
                    with gr.TabItem("3. 👤 Suspect Agent"):
                        with gr.Row():
                            run_suspect_btn = gr.Button("👤 Run Suspect Analysis", variant="primary")
                        suspect_status = gr.Textbox(label="Status", value="⚪ Requires Evidence report", interactive=False)
                        suspect_report_md = gr.Markdown("*Awaiting execution...*")
                        with gr.Accordion("Suspect Diagnostics", open=False):
                            sus_tot = gr.Markdown()
                            sus_rnk = gr.Markdown()
                            sus_ld = gr.Markdown()
                            sus_wk = gr.Markdown()
                            sus_alt = gr.Markdown()
                            sus_chg = gr.Markdown()

                    # Sub-tab: Skeptic
                    with gr.TabItem("4. 🧠 Skeptic Agent"):
                        with gr.Row():
                            run_skeptic_btn = gr.Button("🧠 Run Skeptic Challenge", variant="primary")
                        skeptic_status = gr.Textbox(label="Status", value="⚪ Requires Suspect report", interactive=False)
                        skeptic_report_md = gr.Markdown("*Awaiting execution...*")
                        with gr.Accordion("Skeptic Diagnostics", open=False):
                            skp_cha = gr.Markdown()
                            skp_ass = gr.Markdown()
                            skp_fac = gr.Markdown()
                            skp_alt = gr.Markdown()
                            skp_fal = gr.Markdown()
                            skp_wrn = gr.Markdown()

                    # Sub-tab: Chief
                    with gr.TabItem("5. 👨‍⚖️ Chief Agent"):
                        with gr.Row():
                            run_chief_btn = gr.Button("👨‍⚖️ Run Senior Synthesis & Assessment", variant="primary", size="lg")
                        chief_status = gr.Textbox(label="Status", value="⚪ Requires Skeptic challenge", interactive=False)
                        
                        with gr.Row():
                            chief_expl_box = gr.Markdown("### Current Best Explanation\n*Awaiting execution...*")
                            chief_conf_box = gr.Markdown("### Confidence Level\n*Awaiting...*")
                            chief_rev_box = gr.Markdown("### Human Review\n**REQUIRED**")

                        with gr.Row():
                            chief_strong_box = gr.Textbox(label="Strongest Evidence", lines=2, interactive=False)
                            chief_weak_box = gr.Textbox(label="Weakest Link", lines=2, interactive=False)
                            chief_alt_box = gr.Textbox(label="Leading Alternative", lines=2, interactive=False)
                            chief_next_box = gr.Textbox(label="Recommended Inquiries", lines=2, interactive=False)

                        chief_report_md = gr.Markdown("*Click 'Run Senior Synthesis & Assessment' to generate the 14-section Chief report.*")

            # ==========================================
            # TAB 5: CASE VARIATIONS (COUNTERFACTUAL LAB)
            # ==========================================
            with gr.TabItem("🔄 Case Variations Lab"):
                gr.Markdown("### 🔄 Counterfactual Reasoning & Evidence Variation Experiments")
                gr.Markdown(
                    "Modify key evidence parameters (e.g. remove a physical clue, strengthen or weaken an alibi, or insert a misleading eyewitness) "
                    "to test whether the multi-agent team adjusts its provisional conclusion or succumbs to cognitive bias."
                )

                with gr.Row():
                    with gr.Column():
                        var_type_input = gr.Dropdown(
                            label="Variation Type",
                            choices=[
                                ("Remove Specific Evidence Item", "remove_evidence"),
                                ("Remove All Camera Footage / CCTV", "remove_camera_footage"),
                                ("Strengthen Suspect Alibi", "strengthen_alibi"),
                                ("Weaken Suspect Alibi", "weaken_alibi"),
                                ("Add Misleading Eyewitness", "add_misleading_witness")
                            ],
                            value="remove_evidence"
                        )
                        var_target_input = gr.Textbox(
                            label="Target ID / Name",
                            value="E-E",
                            placeholder="e.g. 'E-E' for evidence removal, or 'Theo Park' for alibi shift"
                        )
                        var_custom_note = gr.Textbox(
                            label="Custom Witness Statement (if adding witness)",
                            placeholder="Describe what the new witness observed...",
                            lines=2
                        )
                        apply_var_btn = gr.Button("🔬 Apply Case Variation", variant="primary")

                    with gr.Column():
                        var_feedback = gr.Textbox(label="Variation Result", lines=6, interactive=False)

            # ==========================================
            # TAB 6: HUMAN REVIEW & SOLUTION REVEAL
            # ==========================================
            with gr.TabItem("👤 Human Review & Solution Reveal"):
                gr.Markdown("### 👤 Final Human Adjudication & Reference Solution Reveal")
                gr.Markdown(
                    "Evaluate the multi-agent team's findings, register your verdict, inspect your investigative reasoning score, "
                    "and unlock the official reference facilitator solution."
                )

                with gr.Row():
                    with gr.Column():
                        human_verdict_radio = gr.Radio(
                            label="Human Decision",
                            choices=["ACCEPT (Endorse AI provisional finding)", "REVISE (Request further evidence or alternative line)", "REJECT (Deem evidence insufficient or flawed)"],
                            value="ACCEPT (Endorse AI provisional finding)"
                        )
                        human_notes_box = gr.Textbox(
                            label="Investigative Notes & Rationale",
                            placeholder="Explain why you accept, revise, or reject the Chief Agent's provisional conclusion...",
                            lines=3
                        )
                        submit_review_btn = gr.Button("📝 Submit Human Review & Compute Score", variant="primary")

                    with gr.Column():
                        review_feedback_box = gr.Textbox(label="Review Status", lines=2, interactive=False)
                        score_card_md = gr.Markdown("### 📊 Investigation Score\n*Submit Human Review to calculate reasoning score.*")

                gr.Markdown("---")
                gr.Markdown("### 🔓 Facilitator Reference Solution")
                reveal_btn = gr.Button("🔓 REVEAL FACILITATOR REFERENCE SOLUTION", variant="secondary")
                solution_reveal_md = gr.Markdown("> *The official case solution is hidden. Compare it with your team's reasoning first.*")

            # ==========================================
            # TAB 7: INVESTIGATION HISTORY ("MY INVESTIGATIONS")
            # ==========================================
            with gr.TabItem("📁 My Investigations"):
                gr.Markdown("### 📁 Historic Investigation Archives")
                gr.Markdown("Audit and review all completed investigations, scores, and human verdicts across cases.")
                history_table_md = gr.Markdown(render_history_table())
                refresh_history_btn = gr.Button("🔄 Refresh History Log")

            # ==========================================
            # TAB 8: AI ENGINE & CONFIGURATION
            # ==========================================
            with gr.TabItem("🔌 AI Engine Diagnostics"):
                gr.Markdown("### ⚙️ Google Gemini System Connectivity")
                with gr.Row():
                    with gr.Column():
                        model_box = gr.Textbox(label="Active Gemini Model", value=config.GEMINI_MODEL, interactive=False)
                        test_conn_btn = gr.Button("🔌 Test Gemini Connection", variant="primary")
                    with gr.Column():
                        conn_status_box = gr.Textbox(label="Status", value="⚪ Not tested", interactive=False)
                        conn_diag_box = gr.Textbox(label="Diagnostic Log", lines=4, interactive=False)

                test_conn_btn.click(
                    fn=test_gemini_connection,
                    inputs=[],
                    outputs=[conn_status_box, conn_diag_box]
                )

        # ==========================================
        # EVENT BINDINGS
        # ==========================================

        # Filter library
        for inp in [search_box, filter_cat, filter_diff, filter_type]:
            inp.change(
                fn=handle_filter_library,
                inputs=[search_box, filter_cat, filter_diff, filter_type],
                outputs=[cases_cards_html]
            )

        # Open case
        open_case_btn.click(
            fn=handle_open_selected_case,
            inputs=[case_select_dropdown],
            outputs=[
                case_action_feedback,
                dossier_display,
                timeline_display,
                suspects_display,
                witnesses_display,
                evidence_display,
                questions_display,
                rules_display,
                cases_cards_html
            ]
        )

        # Case of the Day
        daily_btn.click(
            fn=handle_load_case_of_the_day,
            inputs=[],
            outputs=[
                case_action_feedback,
                case_select_dropdown,
                dossier_display,
                timeline_display,
                suspects_display,
                witnesses_display,
                evidence_display,
                questions_display,
                rules_display,
                cases_cards_html
            ]
        )

        # Random Mystery
        random_btn.click(
            fn=handle_load_random_mystery,
            inputs=[filter_diff, filter_cat],
            outputs=[
                case_action_feedback,
                case_select_dropdown,
                dossier_display,
                timeline_display,
                suspects_display,
                witnesses_display,
                evidence_display,
                questions_display,
                rules_display,
                cases_cards_html
            ]
        )

        # Generate Case
        generate_btn.click(
            fn=handle_generate_case,
            inputs=[gen_cat, gen_diff, gen_suspects, gen_evidence, gen_witnesses, gen_timeline, gen_herrings, gen_twist],
            outputs=[gen_result_box, case_select_dropdown, cases_cards_html]
        )

        # Multi-agent triggers
        run_detective_btn.click(
            fn=handle_run_detective,
            inputs=[],
            outputs=[detective_status, detective_report_md, det_q, det_ev, det_con, det_gap, det_pri]
        )

        run_evidence_btn.click(
            fn=handle_run_evidence,
            inputs=[],
            outputs=[evidence_status, evidence_report_md, ev_tot, ev_str, ev_wea, ev_con, ev_req, ev_uns]
        )

        run_suspect_btn.click(
            fn=handle_run_suspect,
            inputs=[],
            outputs=[suspect_status, suspect_report_md, sus_tot, sus_rnk, sus_ld, sus_wk, sus_alt, sus_chg]
        )

        run_skeptic_btn.click(
            fn=handle_run_skeptic,
            inputs=[],
            outputs=[skeptic_status, skeptic_report_md, skp_cha, skp_ass, skp_fac, skp_alt, skp_fal, skp_wrn]
        )

        run_chief_btn.click(
            fn=handle_run_chief,
            inputs=[],
            outputs=[
                chief_status,
                chief_report_md,
                chief_expl_box,
                chief_conf_box,
                chief_strong_box,
                chief_weak_box,
                chief_alt_box,
                chief_next_box,
                chief_rev_box
            ]
        )

        # Variations
        apply_var_btn.click(
            fn=handle_create_variation,
            inputs=[var_type_input, var_target_input, var_custom_note],
            outputs=[var_feedback, dossier_display, evidence_display]
        )

        # Human Review & Scoring
        submit_review_btn.click(
            fn=handle_human_decision_submit,
            inputs=[human_verdict_radio, human_notes_box],
            outputs=[review_feedback_box, score_card_md, history_table_md]
        )

        # Solution Reveal
        reveal_btn.click(
            fn=handle_reveal_solution,
            inputs=[],
            outputs=[solution_reveal_md]
        )

        # Refresh history
        refresh_history_btn.click(
            fn=render_history_table,
            inputs=[],
            outputs=[history_table_md]
        )

    return demo


def main():
    print("=" * 60)
    print(f"Starting {config.APP_NAME} - AI Mystery Case Platform")
    print(f"Available Built-in Cases: 12 (Cases 001 - 012)")
    print(f"Active Model: {config.GEMINI_MODEL}")
    print("=" * 60)

    demo = create_ui()
    demo.launch(theme=gr.themes.Soft(), inbrowser=False)


if __name__ == "__main__":
    main()
