"""
Case Generator Engine for AI Mystery Detective Team.
Generates structured fictional cases using Gemini, passes them through the
Case Validator for logical consistency, evidence quality, and anti-triviality,
and persists valid cases to data/generated-cases/.
"""

import os
import json
import uuid
import re
from typing import Dict, Any, Optional, Tuple
from app.gemini_client import generate_content
from app.library.case_validator import validate_case

GENERATED_CASES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "generated-cases")
)
os.makedirs(GENERATED_CASES_DIR, exist_ok=True)

CASE_GENERATOR_SYSTEM_PROMPT = """You are an expert fictional mystery case designer.

Create a logically consistent fictional investigation.

The case must contain:
- a compelling incident
- 3–8 suspects
- 5–15 evidence items
- a coherent timeline
- misleading but explainable clues
- multiple plausible hypotheses
- one strongest explanation
- uncertainty
- missing evidence

Never make the solution obvious.
Do not use real criminal cases.
Do not rely on real-world private information.
Every conclusion in the hidden solution must be traceable to generated evidence.
The public investigation data and hidden solution must remain logically separable.
Do not include the hidden solution in the public case data.
All generated cases must be explicitly fictional.

Return valid structured JSON only matching the schema exactly:
{
  "caseId": "GEN-XXXX",
  "title": "Title of the Case",
  "category": "Category",
  "difficulty": "Difficulty",
  "setting": "Detailed fictional setting",
  "incident": "Description of the event",
  "centralQuestions": ["Question 1", "Question 2"],
  "timeline": [
    {"id": "T01", "time": "Time", "event": "Event description", "source": "Source", "certainty": "High/Medium/Low"}
  ],
  "suspects": [
    {
      "suspect_id": "S01",
      "name": "Full Name",
      "role": "Job/Relation",
      "motive": "Plausible motive",
      "statement": "What they told investigators",
      "relevant_evidence": ["Evidence 1"],
      "supporting_evidence": ["Alibi detail"],
      "suspicious_evidence": ["Inconsistency"],
      "uncertainty": "Doubt factor",
      "open_questions": ["Question"]
    }
  ],
  "witnesses": [
    {"witness_id": "W01", "name": "Name", "statement": "Statement", "reliability": "High/Medium/Low"}
  ],
  "evidence": [
    {
      "evidence_id": "E-A",
      "title": "Evidence Title",
      "description": "Factual description",
      "category": "Physical/Digital/Forensic/Documentary",
      "source": "Where found",
      "establishes": "What it definitely proves",
      "does_not_establish": "Crucial limitation or what it does NOT prove",
      "related_suspects": ["Suspect Name"],
      "reliability_notes": "Chain of custody / analysis note"
    }
  ],
  "redHerrings": [
    "Misleading clue 1 and why it seems incriminating but has an innocent explanation"
  ],
  "hiddenSolution": {
    "culprit": "Full Name of Culprit",
    "explanation": "Comprehensive step-by-step causal explanation of how the act occurred",
    "decisiveEvidence": ["E-A", "E-C"],
    "uncertainties": ["Remaining ambiguous point"],
    "alternativeExplanation": "Plausible competing theory and why it is slightly weaker"
  },
  "missingEvidence": [
    "Evidence that investigators would need to verify certainty"
  ],
  "rules": [
    "Heuristic or logical rule for this mystery"
  ],
  "estimatedTimeMinutes": 15
}
"""


def generate_ai_case(
    category: str = "Corporate",
    difficulty: str = "Medium",
    num_suspects: int = 4,
    num_evidence: int = 6,
    witness_count: int = 2,
    timeline_complexity: str = "Moderate",
    red_herrings: str = "Several",
    twist: str = "One",
    max_retries: int = 2,
) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Calls Gemini to design a fresh fictional mystery, validates it with case_validator,
    and saves it to data/generated-cases/. Returns (success, case_dict, message).
    """
    gen_id = f"GEN-{uuid.uuid4().hex[:6].upper()}"

    user_prompt = f"""Design a unique, completely original fictional mystery case with the following specifications:
- Case ID: {gen_id}
- Category: {category}
- Difficulty: {difficulty}
- Number of Suspects: {num_suspects} (all must have motive, statement, and relevant evidence)
- Number of Evidence Items: {num_evidence} (each MUST have both 'establishes' and 'does_not_establish' limitations)
- Number of Witnesses: {witness_count}
- Timeline Complexity: {timeline_complexity} (at least 4-8 chronological events)
- Red Herrings: {red_herrings} (explainable misleading clues)
- Narrative Twist: {twist}

IMPORTANT ANTI-TRIVIALITY INSTRUCTIONS:
- Do NOT have any suspect confess.
- Do NOT make camera footage directly show the theft or act.
- Multiple suspects must have genuine opportunity and motive.
- Provide a robust 'hiddenSolution' with culprit, causal explanation, decisive evidence list, uncertainties, and an alternative explanation.
- Return ONLY valid JSON.
"""

    for attempt in range(max_retries + 1):
        try:
            response_text = generate_content(
                prompt=user_prompt,
                system_instruction=CASE_GENERATOR_SYSTEM_PROMPT,
                temperature=0.75,
            )

            # Strip markdown fences if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            case_data = json.loads(cleaned)
            case_data["caseId"] = gen_id

            # Validation check
            validation_res = validate_case(case_data)
            if validation_res["valid"]:
                # Save to generated directory
                file_name = f"case-{gen_id.lower()}.json"
                file_path = os.path.join(GENERATED_CASES_DIR, file_name)
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(case_data, f, indent=2)

                return (
                    True,
                    case_data,
                    f"Successfully generated and validated case '{case_data.get('title')}' ({gen_id})!",
                )
            else:
                err_msg = "; ".join(validation_res["errors"])
                print(f"[CaseGenerator] Attempt {attempt+1} failed validation: {err_msg}")
                # Append critique to next attempt prompt
                user_prompt += f"\n\nPrevious attempt failed validation due to: {err_msg}. Fix these issues."
        except Exception as e:
            print(f"[CaseGenerator] Attempt {attempt+1} error: {e}")

    return False, None, "Case generation failed validation after multiple attempts."


def load_all_generated_cases() -> list:
    """Loads all previously generated and validated cases from disk."""
    cases = []
    if not os.path.exists(GENERATED_CASES_DIR):
        return cases

    for fname in sorted(os.listdir(GENERATED_CASES_DIR)):
        if fname.endswith(".json"):
            fpath = os.path.join(GENERATED_CASES_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cases.append(data)
            except Exception as e:
                print(f"Error loading generated case {fpath}: {e}")
    return cases
