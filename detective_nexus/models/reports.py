from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DetectiveReport(BaseModel):
    incident_summary: str = Field(..., description="Objective narrative of the incident")
    confirmed_facts: List[str] = Field(default_factory=list)
    reconstructed_timeline: List[str] = Field(default_factory=list)
    critical_time_window: str = Field(..., description="Exact opportunity window")
    known_actors: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    initial_hypotheses: List[str] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    raw_markdown: str = Field("", description="Full markdown report")

class EvidenceAnalysisItem(BaseModel):
    evidence_id: str
    observation: str
    fact_vs_inference: str
    strength: str
    relevance: str
    what_it_proves: str
    what_it_does_not_prove: str
    alternative_explanation: str
    confidence: float

class EvidenceReport(BaseModel):
    evidence_table: List[EvidenceAnalysisItem] = Field(default_factory=list)
    strongest_clues: List[str] = Field(default_factory=list)
    weakest_or_misleading: List[str] = Field(default_factory=list)
    conflicting_evidence: List[str] = Field(default_factory=list)
    missing_forensic_tests: List[str] = Field(default_factory=list)
    raw_markdown: str = Field("", description="Full markdown report")

class SuspectRating(BaseModel):
    suspect_id: str
    name: str
    motive_score: str # Low, Medium, High
    means_score: str # Low, Medium, High, Confirmed
    opportunity_score: str # Low, Medium, High
    access_score: str # None, Proxy, Direct
    alibi_status: str # Supported, Partially Supported, Contradicted, Unknown
    evidence_against: List[str] = Field(default_factory=list)
    evidence_in_favor: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    alternative_explanation: str

class SuspectReport(BaseModel):
    suspect_matrix: List[SuspectRating] = Field(default_factory=list)
    provisional_lead: str = Field(..., description="Currently leading suspect (provisional only)")
    weaknesses_in_lead: List[str] = Field(default_factory=list)
    evidence_that_could_flip_ranking: List[str] = Field(default_factory=list)
    raw_markdown: str = Field("", description="Full markdown report")

class SkepticReport(BaseModel):
    leading_theory_challenged: str
    assumptions_exposed: List[str] = Field(default_factory=list)
    weak_links: List[str] = Field(default_factory=list)
    alternative_theories: List[str] = Field(default_factory=list)
    missing_evidence_demanded: List[str] = Field(default_factory=list)
    falsification_tests: List[str] = Field(default_factory=list)
    confidence_reduction_rationale: str
    raw_markdown: str = Field("", description="Full markdown report")

class ChiefReport(BaseModel):
    case_summary: str
    reconstructed_timeline: List[str] = Field(default_factory=list)
    strongest_evidence: List[str] = Field(default_factory=list)
    weakest_evidence: List[str] = Field(default_factory=list)
    suspect_comparison: str
    leading_explanation: str
    not_proven_caveat: str = Field("THIS IS A PROVISIONAL HYPOTHESIS AND DOES NOT CONSTITUTE LEGAL PROOF.")
    alternative_explanation: str
    contradictions: List[str] = Field(default_factory=list)
    missing_evidence_required: List[str] = Field(default_factory=list)
    confidence_level: str = Field("MODERATE", description="VERY LOW, LOW, MODERATE, HIGH, VERY HIGH")
    confidence_explanation: str
    recommended_next_investigation: List[str] = Field(default_factory=list)
    human_review_requirement: str = Field("MANDATORY REVIEW BEFORE ACCEPTANCE")
    raw_markdown: str = Field("", description="Full markdown report")
