"""
Detective Nexus Suspect Interrogation & Deception Detection Engine
Simulates live suspect cross-examination, psychological stress modeling,
confrontation with physical evidence exhibits, and real-time biometric stress gauges.
"""

from typing import Dict, Any, List, Tuple
import json
import re
from detective_nexus.llm.gemini_client import get_client

class InterrogationEngine:
    """
    Manages active suspect interrogation sessions, evaluates behavioral cues,
    calculates deception probability, and renders live physiological stress gauges.
    """

    @classmethod
    def interrogate_suspect(
        cls,
        suspect_name: str,
        user_question: str,
        chat_history: List[Tuple[str, str]],
        confront_evidence_item: str = None,
        case_data: Dict[str, Any] = None
    ) -> Tuple[str, Dict[str, Any], str]:
        """
        Executes suspect cross-examination turn.
        Returns: (suspect_reply, telemetry_dict, html_stress_gauge)
        """
        if not user_question and not confront_evidence_item:
            return "...", {}, ""

        prompt_input = user_question
        if confront_evidence_item and confront_evidence_item != "None":
            prompt_input = f"[CONFRONTING SUSPECT WITH EXHIBIT: {confront_evidence_item}]\nQuestion: {user_question}"

        client = get_client()
        system_prompt = f"""You are roleplaying as {suspect_name}, a key person of interest in a high-stakes forensic investigation.
Stay strictly in character. If innocent, defend yourself firmly but show realistic human nervousness.
If guilty or having something to hide (like Arjun Vale about his debt and keycard swipe), act somewhat guarded, deflect questions when pressed on exact timestamps (8:20-8:24 PM), and react defensively if confronted with physical or digital evidence.
Do not confess immediately under normal questioning, but if cornered with undeniable physical proof (e.g. keycard electronic log or fibers), offer a flustered alternative explanation (e.g. claims card was stolen or jacket was left unattended).
Keep responses under 4 sentences to maintain conversational tension."""

        if client.is_configured():
            full_context = f"CASE DATA:\n{json.dumps(case_data or {}, indent=2)[:1500]}\n\nINVESTIGATOR PROMPT:\n{prompt_input}"
            success, reply = client.generate(system_instruction=system_prompt, user_prompt=full_context)
            if not success or not reply:
                reply = cls._generate_local_reply(suspect_name, user_question, confront_evidence_item)
        else:
            reply = cls._generate_local_reply(suspect_name, user_question, confront_evidence_item)

        # Compute psychological stress and deception metrics
        telemetry = cls._calculate_deception_metrics(suspect_name, user_question, reply, confront_evidence_item)
        gauge_html = cls.render_stress_gauge_html(telemetry)

        return reply, telemetry, gauge_html

    @classmethod
    def _calculate_deception_metrics(
        cls,
        suspect_name: str,
        question: str,
        reply: str,
        confront_evidence: str
    ) -> Dict[str, Any]:
        """Calculates deception probability and psychological stress indicators."""
        reply_lower = reply.lower()
        q_lower = question.lower() if question else ""

        # Baseline stress by suspect
        base_stress = 42 if "arjun" in suspect_name.lower() else 30

        # Confrontation spike
        confront_spike = 30 if (confront_evidence and confront_evidence != "None") else 0
        if any(w in (confront_evidence or "").lower() for w in ["keycard", "lock", "e-b", "fiber", "e-e"]):
            confront_spike += 15

        # Linguistic markers
        evasive_count = sum(1 for w in ["i don't recall", "someone else", "framed", "stolen", "wasn't me", "impossible", "desk", "coat", "jacket", "why are you asking"] if w in reply_lower)
        evasive_spike = min(25, evasive_count * 8)

        total_stress = min(98, max(15, base_stress + confront_spike + evasive_spike))

        if total_stress >= 80:
            level = "CRITICAL DECEPTION SPIKE // PERJURY RISK"
            color = "#ef4444"
            tells = ["Rapid breathing detected", "Severe timeline deflection", "Denies physical telemetry"]
        elif total_stress >= 55:
            level = "ELEVATED ANXIETY // DEFENSIVE POSTURE"
            color = "#f59e0b"
            tells = ["Nervous hand fidgeting", "Guarded vocal inflection", "Qualifying statements"]
        else:
            level = "COMPOSED // BASELINE PSYCHOLOGICAL STATE"
            color = "#10b981"
            tells = ["Steady eye contact", "Consistent narrative cadence", "Direct factual responses"]

        return {
            "suspect": suspect_name,
            "stress_score": total_stress,
            "level": level,
            "color": color,
            "tells": tells,
            "confronted": bool(confront_evidence and confront_evidence != "None")
        }

    @classmethod
    def _generate_local_reply(cls, suspect_name: str, question: str, confront_evidence: str) -> str:
        s_lower = suspect_name.lower()
        q_lower = question.lower() if question else ""
        c_lower = (confront_evidence or "").lower()

        if "arjun" in s_lower:
            if "keycard" in c_lower or "lock" in c_lower or "8:23" in q_lower:
                return "Look, I've told you three times! I left my security keycard inside my suit jacket in the archive office while I was searching for the ledgers. Someone must have taken it during the blackout!"
            elif "fiber" in c_lower or "folder" in q_lower:
                return "That folder was on the archival desk for weeks. If there are blue velvet fibers on it, anyone who inspected the display vitrine could have transferred them. You can't pin this on me!"
            else:
                return "I was in the archival vault fulfilling my curatorial duties. I had nothing to do with the power outage, and I certainly didn't steal the Aurora Diamond."

        elif "lena" in s_lower:
            if "boot" in c_lower or "footprint" in q_lower:
                return "I was doing external perimeter rounds in the pouring rain when the generator warning tripped! Of course my work boots have courtyard mud on them!"
            else:
                return "I am the facility technician. When the main electrical feed collapsed at 8:20 PM, I ran straight down to breaker panel 4 to restore lighting."

        elif "theo" in s_lower:
            return "I was literally standing at the podium addressing three hundred attendees in the main auditorium until the lights flickered out. Check the camera recordings!"

        else:
            return "As an investigative journalist, my presence in the museum is completely documented. I ask the questions here, detective."

    @classmethod
    def render_stress_gauge_html(cls, telemetry: Dict[str, Any]) -> str:
        if not telemetry:
            return """
            <div style="padding: 16px; border: 1px dashed #334155; border-radius: 8px; text-align: center; color: #94a3b8; font-family: monospace;">
                🎙️ Suspect Interrogation Room idle. Select a suspect and ask a question to begin live psychological stress monitoring.
            </div>
            """

        score = telemetry.get("stress_score", 45)
        color = telemetry.get("color", "#f59e0b")
        level = telemetry.get("level", "ELEVATED")
        suspect = telemetry.get("suspect", "Suspect")
        tells = telemetry.get("tells", [])
        tells_html = "".join([f"<li style='color: {color};'>• {t}</li>" for t in tells])

        return f"""
<div style="background: #0b1120; border: 1px solid #1e293b; border-left: 5px solid {color}; border-radius: 8px; padding: 16px; font-family: 'JetBrains Mono', monospace;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8;">
            SUBJECT: <strong style="color: #f8fafc;">{suspect}</strong> // BIOMETRIC STRESS MONITOR
        </div>
        <div style="background: #111a2e; border: 1px solid {color}; color: {color}; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">
            {level}
        </div>
    </div>

    <!-- Stress Level Bar -->
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 12px;">
        <div style="font-size: 1.8rem; font-weight: 900; color: {color}; width: 65px;">
            {score}%
        </div>
        <div style="flex-grow: 1; background: #1e293b; height: 12px; border-radius: 6px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #10b981 0%, #f59e0b 50%, #ef4444 100%); width: {score}%; height: 100%; transition: width 0.4s ease;"></div>
        </div>
    </div>

    <!-- Detected Tells -->
    <div style="font-size: 0.75rem; color: #cbd5e1;">
        <strong>DETECTED BEHAVIORAL INDICATORS:</strong>
        <ul style="margin: 4px 0 0 0; padding-left: 18px; line-height: 1.4;">
            {tells_html}
        </ul>
    </div>
</div>
"""
