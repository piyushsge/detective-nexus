from detective_nexus.llm.gemini_client import NexusGeminiClient, get_client
from detective_nexus.llm.prompts import (
    DETECTIVE_PROMPT,
    EVIDENCE_PROMPT,
    SUSPECT_PROMPT,
    SKEPTIC_PROMPT,
    CHIEF_PROMPT,
    ASSISTANT_PROMPT
)

__all__ = [
    "NexusGeminiClient",
    "get_client",
    "DETECTIVE_PROMPT",
    "EVIDENCE_PROMPT",
    "SUSPECT_PROMPT",
    "SKEPTIC_PROMPT",
    "CHIEF_PROMPT",
    "ASSISTANT_PROMPT"
]
