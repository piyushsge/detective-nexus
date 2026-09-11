"""
Detective Nexus Courtroom Trial Simulator
Simulates a formal criminal trial before a 12-person jury:
- AI Prosecution Case Argumentation
- AI Defense Cross-Examination & Reasonable Doubt Challenges
- 12-Person Jury Deliberation & Verdict Engine
"""

from typing import Dict, Any, Tuple
import random
from detective_nexus.llm.gemini_client import get_client

class CourtroomTrialEngine:
    """
    Simulates adversarial court trials testing if the investigative evidence
    satisfies the judicial standard of 'Proof Beyond a Reasonable Doubt'.
    """

    @classmethod
    def conduct_trial(
        cls,
        indicted_suspect: str,
        case_data: Dict[str, Any],
        has_lab_certificate: bool = False
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Runs the courtroom trial simulation.
        Returns: (proceedings_markdown, html_verdict_banner, jury_metrics)
        """
        suspect_lower = indicted_suspect.lower()
        is_arjun = "arjun" in suspect_lower

        # Evaluate reasonable doubt
        # Arjun without lab certification has strong defense doubt (card theft); with lab test, guilt is overwhelming!
        if is_arjun:
            guilty_votes = 12 if has_lab_certificate else random.choice([10, 11, 10])
        elif "lena" in suspect_lower:
            guilty_votes = 4 # Circumstantial bootprint only
        elif "theo" in suspect_lower:
            guilty_votes = 1 # Strong auditorium alibi
        else:
            guilty_votes = 3

        not_guilty_votes = 12 - guilty_votes

        if guilty_votes == 12:
            verdict = "GUILTY AS CHARGED // FIRST-DEGREE GRAND LARCENY"
            verdict_color = "#ef4444" # Crimson
            verdict_summary = f"The 12-person jury unanimously finds {indicted_suspect} GUILTY. The combination of verified keycard telemetry and physical fiber matching proved insurmountable for the defense."
        elif guilty_votes >= 10:
            verdict = "CONVICTION SECURED (MAJORITY VERDICT)"
            verdict_color = "#f59e0b" # Amber
            verdict_summary = f"The jury convicts {indicted_suspect} on a {guilty_votes}-{not_guilty_votes} majority. Minor dissent centered on whether third-party card cloning was theoretically feasible."
        elif guilty_votes <= 4:
            verdict = "NOT GUILTY // ACQUITTAL BY REASON OF REASONABLE DOUBT"
            verdict_color = "#10b981" # Emerald
            verdict_summary = f"The jury acquits {indicted_suspect} ({not_guilty_votes} to {guilty_votes}). The state failed to eliminate reasonable hypotheses of innocence."
        else:
            verdict = "MISTRIAL // HUNG JURY (DEADLOCKED)"
            verdict_color = "#a855f7" # Purple
            verdict_summary = f"The jury is permanently deadlocked ({guilty_votes}-{not_guilty_votes}). A mistrial is declared by the presiding judge."

        proceedings_md = f"""# ⚖️ SUPREME JUDICIAL COURT // TRIAL PROCEEDINGS
**State Prosecution vs. {indicted_suspect}** | **Grand Criminal Session**

---

### 🏛️ 1. State Prosecution Opening Argument
> *"Your Honor, members of the jury: The evidence against {indicted_suspect} is an unbroken chain of forensic telemetry. At 8:23 PM, while the museum was plunged into total darkness, the defendant's master access credential operated the electronic vitrine. Two minutes later, security cameras captured the defendant leaving with a flat folder containing identical blue velvet fibers. Motive, means, and exclusive opportunity all point to the defendant."*

---

### 🛡️ 2. Defense Cross-Examination & Motion for Dismissal
> *"Objection, Your Honor! The prosecution relies entirely on digital inference. A keycard swipe proves a piece of plastic was near the door—it does NOT prove whose hand held that card! The archive egress fire door was unmonitored. Anyone could have lifted the card from my client's desk during the power surge. Without physical touch DNA, reasonable doubt reigns supreme!"*

---

### ⚡ 3. Prosecution Rebuttal
> *"The defense asks you to believe in miracles of coincidence—that an unknown thief stole the card at 8:22 PM, opened the case at 8:23 PM, returned it immediately, and mysteriously planted display velvet fibers inside the defendant's personal folder. The physical evidence speaks for itself."*

---

### 🗳️ 4. Presiding Judge's Charge to the Jury
> *"Members of the jury, the burden of proof rests entirely with the prosecution. If there remains in your mind a reasonable doubt based on reason and common sense, you must acquit the accused."*
"""

        jury_boxes = "".join([
            f"<div style='background: {'#ef4444' if i < guilty_votes else '#10b981'}; color: white; padding: 6px 10px; border-radius: 4px; text-align: center; font-weight: bold; font-size: 0.75rem;'>Juror {i+1}: {'GUILTY' if i < guilty_votes else 'NOT GUILTY'}</div>"
            for i in range(12)
        ])

        html_verdict = f"""
<div style="
    background: #0b1120;
    border: 2px solid #1e293b;
    border-top: 5px solid {verdict_color};
    border-radius: 10px;
    padding: 24px;
    margin: 18px 0;
    font-family: 'JetBrains Mono', monospace;
    color: #f8fafc;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
">
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 12px; margin-bottom: 16px;">
        <div style="font-size: 0.8rem; letter-spacing: 0.15em; color: #94a3b8; text-transform: uppercase;">
            12-PERSON JURY DELIBERATION RECORD
        </div>
        <div style="background: #111a2e; border: 1px solid {verdict_color}; color: {verdict_color}; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85rem;">
            {verdict}
        </div>
    </div>

    <div style="font-size: 1.25rem; font-weight: 800; color: #f8fafc; margin-bottom: 12px;">
        FINAL JUDICIAL VERDICT: <span style="color: {verdict_color};">{verdict.split('//')[0].strip()}</span>
    </div>

    <div style="background: #080c16; border: 1px solid #1e293b; border-radius: 6px; padding: 14px; margin-bottom: 18px; font-size: 0.9rem; line-height: 1.5;">
        {verdict_summary}
    </div>

    <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 8px; font-weight: bold;">
        JUROR VOTE TALLY ({guilty_votes} GUILTY vs {not_guilty_votes} NOT GUILTY):
    </div>
    <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px;">
        {jury_boxes}
    </div>
</div>
"""
        return proceedings_md, html_verdict, {"guilty_votes": guilty_votes, "not_guilty_votes": not_guilty_votes, "verdict": verdict}
