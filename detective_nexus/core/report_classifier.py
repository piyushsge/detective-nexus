"""
Detective Nexus Case Report Classifier & Domain Identification Engine
Automatically determines what an uploaded case or report is about ("Report kis cheez ki hai"),
its forensic classification, jurisdiction, and executive synopsis using Gemini AI
with robust local heuristic fallback.
"""

import json
import re
from typing import Dict, Any
from detective_nexus.llm.gemini_client import get_client


class ReportClassifier:
    """Analyzes raw report text to classify its domain, subject matter, and operational jurisdiction."""

    @classmethod
    def classify_report(cls, text: str) -> Dict[str, str]:
        """
        Classifies the report domain and extracts a plain-language summary of what it is about.
        Uses Gemini when online, or dynamic text extraction fallback if offline.
        """
        if not text or not text.strip():
            return cls._default_classification("No text provided")

        clean_text = text.strip()

        # 1. Try Gemini AI classification
        client = get_client()
        if client.is_configured():
            try:
                system_instruction = (
                    "You are a forensic report classification expert. "
                    "Analyze the uploaded document or report and identify what it is about. "
                    "Return ONLY a valid JSON object matching this exact schema:\n"
                    "{\n"
                    '  "subject": "<Accurate, specific title of this exact report or incident>",\n'
                    '  "category": "<Specific domain/category, e.g. Train Passenger Theft / Corporate Embezzlement / Cyber Intrusion / Homicide / Burglary>",\n'
                    '  "jurisdiction": "<Responsible law enforcement agency, department, or jurisdiction implied by the document>",\n'
                    '  "synopsis": "<2-3 sentence clear, objective factual synopsis of what this specific document reports, mentioning specific entities, places, and events in the text>",\n'
                    '  "icon": "<A single relevant emoji representing this domain, e.g. 🚆, 💼, 📱, 💻, 🏛️, 🩸, 💎, 📄>"\n'
                    "}\n"
                    "Do NOT invent facts, names, or locations not present in or directly implied by the document."
                )
                user_prompt = f"Analyze and classify this document text:\n\n{clean_text[:6000]}"
                ok, response = client.generate(
                    system_instruction=system_instruction,
                    user_prompt=user_prompt,
                    temperature=0.1
                )
                if ok and response:
                    cleaned = response.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    elif cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()
                    
                    data = json.loads(cleaned)
                    if data.get("subject") and data.get("synopsis"):
                        return {
                            "category": str(data.get("category", "General Incident Report")),
                            "subject": str(data.get("subject", "Extracted Incident Narrative")),
                            "jurisdiction": str(data.get("jurisdiction", "General Law Enforcement")),
                            "synopsis": str(data.get("synopsis", "")),
                            "icon": str(data.get("icon", "📋"))
                        }
            except Exception:
                pass

        # 2. Dynamic Heuristic Extraction (Fallback without hardcoded fake data)
        return cls._dynamic_heuristic_classification(clean_text)

    @classmethod
    def _dynamic_heuristic_classification(cls, text: str) -> Dict[str, str]:
        """Extracts genuine metadata directly from document lines without hardcoding canned titles."""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        # Determine subject/title from first meaningful line
        subject = "Incident Investigation Report"
        for line in lines[:5]:
            clean_l = re.sub(r"^[#\*\-=\d\.\s]+", "", line).strip()
            if len(clean_l) >= 6 and not clean_l.lower().startswith(("case report:", "location:", "date:")):
                subject = clean_l[:90]
                break
        
        lower = text.lower()
        
        # Domain detection
        if any(w in lower for w in ["railway", "train", "rpf", "grp", "berth", "coach", "station", "locomotive"]):
            category = "Railway & Transit Crime Investigation"
            jurisdiction = "Railway Protection Force (RPF) & Transit Police"
            icon = "🚆"
        elif any(w in lower for w in ["cyber", "malware", "ransomware", "server", "ip address", "phishing", "encryption"]):
            category = "Cybercrime & Digital Infrastructure Breach"
            jurisdiction = "Cybercrime Investigation Division"
            icon = "💻"
        elif any(w in lower for w in ["homicide", "murder", "victim", "coroner", "stab", "gunshot", "autopsy"]):
            category = "Homicide & Fatal Incident Investigation"
            jurisdiction = "Forensic Medical Examiner & Homicide Squad"
            icon = "🩸"
        elif any(w in lower for w in ["embezzlement", "fraud", "audit", "transaction", "invoice", "bank", "ledger"]):
            category = "Financial Fraud & Economic Offense Audit"
            jurisdiction = "Economic Offenses Investigation Wing"
            icon = "📊"
        elif any(w in lower for w in ["diamond", "vault", "jewelry", "museum", "gallery", "art", "heist"]):
            category = "High-Value Asset Theft & Burglary"
            jurisdiction = "Metropolitan Asset Recovery & Criminal Investigation"
            icon = "💎"
        else:
            category = "Official Criminal Incident Dossier"
            jurisdiction = "General Criminal Investigation Division"
            icon = "📋"

        # Build genuine synopsis from first 2-3 substantive sentences in user text
        sentences = re.split(r"(?<=[.!?])\s+", text)
        substantive = [s.strip() for s in sentences if len(s.strip()) > 25 and not s.startswith("#")]
        if substantive:
            synopsis = " ".join(substantive[:3])
            if len(synopsis) > 350:
                synopsis = synopsis[:350] + "..."
        else:
            synopsis = f"This document outlines an active investigation regarding: '{subject}'. Evidentiary timeline and witness records have been cataloged for multi-agent forensic review."

        return {
            "category": category,
            "subject": subject,
            "jurisdiction": jurisdiction,
            "synopsis": synopsis,
            "icon": icon
        }

    @classmethod
    def _default_classification(cls, reason: str) -> Dict[str, str]:
        return {
            "category": "Pending Documentation",
            "subject": "Awaiting Document Upload",
            "jurisdiction": "Forensic Intake Division",
            "synopsis": reason,
            "icon": "📄"
        }

    @classmethod
    def render_classification_html(cls, classification: Dict[str, str], is_dark: bool = True) -> str:
        """Renders an authentic, forensic classification banner."""
        bg = "#111111" if is_dark else "#F8FAFC"
        border = "#292929" if is_dark else "#CBD5E1"
        gold = "#D4AF37"
        text_color = "#F2F2F2" if is_dark else "#0F172A"
        muted = "#8B8B8B" if is_dark else "#64748B"

        return f"""
        <div style="background: {bg}; border: 1px solid {border}; border-left: 5px solid {gold}; border-radius: 6px; padding: 14px 18px; margin-bottom: 14px; font-family: 'Inter', sans-serif;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.3rem;">{classification.get('icon', '📋')}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; color: {gold}; letter-spacing: 0.08em; text-transform: uppercase;">
                        IDENTIFIED REPORT DOMAIN // WHAT THIS REPORT IS ABOUT
                    </span>
                </div>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: {muted}; border: 1px solid {border}; padding: 2px 8px; border-radius: 4px;">
                    JURISDICTION: {classification.get('jurisdiction', 'Law Enforcement')}
                </span>
            </div>
            <div style="font-size: 1.05rem; font-weight: 700; color: {text_color}; margin-bottom: 6px;">
                {classification.get('subject', 'Incident Report')}
            </div>
            <div style="font-size: 0.85rem; color: {muted}; line-height: 1.5; margin-bottom: 8px;">
                {classification.get('synopsis', '')}
            </div>
            <div style="font-size: 0.76rem; font-family: 'JetBrains Mono', monospace; color: {gold};">
                OPERATIONAL CLASSIFICATION: <strong>{classification.get('category', 'Incident Dossier')}</strong>
            </div>
        </div>
        """
