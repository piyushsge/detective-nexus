"""
Case Schema and Data Model Definitions for the AI Mystery Case Platform.
Ensures strict typing, standard serialization, and separation of public case data
from the hidden facilitator solution.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TimelineEvent:
    id: str
    time: str
    event: str
    source: str
    certainty: str


@dataclass
class Suspect:
    suspect_id: str
    name: str
    role: str
    motive: str
    statement: str
    relevant_evidence: List[str]
    supporting_evidence: List[str]
    suspicious_evidence: List[str]
    uncertainty: str
    open_questions: List[str]


@dataclass
class Witness:
    witness_id: str
    name: str
    role: str
    statement: str
    supporting_information: List[str]
    limitations: str


@dataclass
class EvidenceItem:
    evidence_id: str
    title: str
    description: str
    category: str
    source: str
    establishes: str
    does_not_establish: str
    related_suspects: List[str]
    reliability_notes: str
    alternative_explanation: Optional[str] = None


@dataclass
class HiddenSolution:
    culprit: str
    explanation: str
    decisiveEvidence: List[str]
    uncertainties: List[str]
    alternativeExplanation: str
    whyRedHerringsMisled: Optional[str] = None
    whatAiGotRight: Optional[str] = None
    whatAiGotWrong: Optional[str] = None


@dataclass
class MysteryCase:
    caseId: str
    title: str
    category: str
    difficulty: str
    setting: str
    incident: str
    centralQuestions: List[str]
    timeline: List[Dict[str, Any]]
    suspects: List[Dict[str, Any]]
    witnesses: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    redHerrings: List[str]
    hiddenSolution: Dict[str, Any]
    missingEvidence: List[str]
    rules: List[str]
    estimatedTimeMinutes: int = 15
    isCustom: bool = False
    isGenerated: bool = False

    def to_agent_visible_dict(self) -> Dict[str, Any]:
        """
        Extracts only the agent-visible public case data.
        CRITICAL ARCHITECTURE: The hiddenSolution is NEVER included in this output.
        """
        return {
            "metadata": {
                "case_id": self.caseId,
                "title": self.title,
                "case_type": f"{self.difficulty} {self.category} Mystery",
                "location": self.setting,
                "difficulty": self.difficulty,
                "category": self.category,
                "status": "Ready for multi-agent investigation"
            },
            "incident_description": self.incident,
            "central_investigation_questions": self.centralQuestions,
            "investigation_rules": self.rules,
            "timeline": self.timeline,
            "suspects": self.suspects,
            "witnesses": self.witnesses,
            "evidence": self.evidence,
            "missing_evidence_lines": self.missingEvidence
        }

    def to_full_dict(self) -> Dict[str, Any]:
        """Returns the full case dictionary including the hidden solution."""
        return asdict(self)
