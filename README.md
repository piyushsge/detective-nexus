# DETECTIVE NEXUS — AI MYSTERY INVESTIGATION SYSTEM

A multi-agent forensic mystery investigation platform built completely with **Python, Gradio Blocks, and Google Gemini API**.

Instead of treating mystery solving as a single chatbot guessing prompt, **Detective Nexus** orchestrates an elite team of 5 specialized forensic AI agents that analyze, stress-test, and synthesize evidence using strict epistemological standards.

---

## 🏛️ System Architecture

```
                                CASE DOSSIER
                                     │
                                     ▼
                          AGENT 1: LEAD DETECTIVE
                     Reconstruct Timeline & Facts
                                     │
                                     ▼
                      AGENT 2: EVIDENCE SPECIALIST
                    Classify Fact vs. Inference & Limits
                                     │
                                     ▼
                        AGENT 3: SUSPECT ANALYST
                     Comparative Motive/Means/Alibi
                                     │
                                     ▼
                         AGENT 4: SKEPTIC AGENT
                    Adversarial Challenge & Doubts
                                     │
                                     ▼
                       AGENT 5: CHIEF INVESTIGATOR
                     Senior Synthesis & Verdict
                                     │
                                     ▼
                       HUMAN JUDICIAL ADJUDICATION
                       [ACCEPT] [REVISE] [REJECT]
```

---

## 🌟 Core Features

1. **Dark Forensic Command Center UI (Pure Gradio)**:
   - Near-black palette (`#07090e`), dark charcoal panels (`#111827`), subtle borders (`#1e293b`), and muted amber/gold evidence accents (`#fbbf24`).
   - Monospaced typography for timestamps, technical codes, and metadata; clean sans-serif for report body text.
   - Built exclusively with Gradio Blocks, components, themes, and CSS injection — **zero external frontend frameworks**.

2. **Five Specialized Forensic Agents**:
   - **🔎 Detective Agent**: Extracts verified facts, reconstructs the timeline, and isolates the critical opportunity window (**08:20 PM – 08:24 PM**).
   - **🧪 Evidence Specialist**: Audits all 7 clues (E-A to E-G) across `FACT`, `INFERENCE`, `DISTRACTION`, and `UNCERTAIN`. Strictly states what each item proves and does *not* prove.
   - **👤 Suspect Analyst**: Evaluates all 4 suspects (Lena Ortiz, Theo Park, Arjun Vale, Sofia Reed) across Motive, Means, Opportunity, Access, and Alibi. Motive is never equated to proof.
   - **🧐 Skeptic Agent**: Adversarially challenges the leading hypothesis, audits hidden assumptions (e.g. credential ownership != physical identity), and demands falsification tests.
   - **👑 Chief Investigator**: Reconciles cross-agent findings, discloses all uncertainty, declares the provisional lead with an explicit **NOT PROVEN** caveat, and mandates Human Review.

3. **Investigation Replay & Counterfactual Lab**:
   - Experiment with evidence removal (e.g., removing Evidence `E-E: Blue Velvet Fibers`) to observe how the AI team adjusts its confidence and reasoning side-by-side.

4. **Human Judicial Review & Investigation Scoring**:
   - Mandatory human adjudication panel allowing investigators to `ACCEPT`, `REVISE`, or `REJECT` the verdict.
   - Computes an **Investigation Rigor Score** (0–100%) evaluating Evidence Grounding, Suspect Fairness, Skeptic Rigor, Uncertainty Awareness, and Alternative Theories.

5. **Interactive Forensic Assistant**:
   - Real-time Q&A assistant grounded strictly in active case records without hallucinating non-existent facts.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- A valid Google Gemini API Key

### 2. Installation
```bash
git clone <repository_url>
cd AI_Mystery_Detective_Team
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the project root:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

### 4. Launching Detective Nexus
```bash
python -m detective_nexus.app
```
Then navigate to **`http://127.0.0.1:7860`** in your browser.

---

## 🧪 Running Automated Tests

Run the complete unit test suite:
```bash
python -m unittest detective_nexus/tests/test_nexus.py
```

---

## 📂 Project Structure

```
detective_nexus/
├── app.py                      # Application launcher & main entrypoint
├── config.py                   # Secure environment loader and validation
├── data/
│   └── aurora_diamond.json     # Ground truth case file
├── models/
│   ├── case.py                 # Pydantic models for Case, Suspects, Evidence, Timeline
│   └── reports.py              # Pydantic models for all 5 agent reports
├── llm/
│   ├── gemini_client.py        # Resilient Gemini SDK client with retry logic
│   └── prompts.py              # System instructions for all 5 agents
├── agents/
│   ├── detective.py            # Detective Agent
│   ├── evidence.py             # Evidence Specialist Agent
│   ├── suspect.py              # Suspect Analyst Agent
│   ├── skeptic.py              # Skeptic Agent
│   └── chief.py                # Chief Investigator Agent
├── core/
│   ├── case_engine.py          # Case loading and data isolation
│   ├── evidence_engine.py      # Relational graph generator and card HTML
│   ├── confidence.py           # Multi-factor investigation quality scoring
│   └── validation.py           # Hallucination and unsupported claim auditor
├── storage/
│   └── history_store.py        # Case history and adjudication logger
├── ui/
│   ├── theme.py                # Gradio dark forensic command center theme
│   ├── styles.py               # Custom CSS for forensic terminal aesthetics
│   └── dashboard.py            # Main Gradio Blocks UI and event orchestrator
└── tests/
    └── test_nexus.py           # Comprehensive unit tests
```

---

## ⚖️ Security & Epistemic Standards
- **Secret Separation**: The public case data provided to agents strictly excludes facilitator reference solutions.
- **Hallucination Protection**: The system rejects fabricated evidence IDs and unsupported confessions.
- **Zero External Frontend Frameworks**: 100% pure Python and Gradio implementation.
