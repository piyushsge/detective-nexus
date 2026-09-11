from typing import Dict, Any, List

def calculate_nexus_quality_score(
    evidence_grounding_citations: int,
    suspects_analyzed: int,
    skeptic_challenges: int,
    uncertainties_acknowledged: int,
    alternatives_formulated: int
) -> Dict[str, Any]:
    """
    Evaluates investigation rigor across 5 core forensic dimensions.
    Returns qualitative scores and ASCII meters.
    """
    # Max scores
    eg_score = min(100, max(50, 60 + evidence_grounding_citations * 5))
    sf_score = min(100, max(60, 70 + (suspects_analyzed >= 4) * 30))
    sk_score = min(100, max(50, 65 + skeptic_challenges * 10))
    un_score = min(100, max(50, 70 + uncertainties_acknowledged * 8))
    al_score = min(100, max(50, 65 + alternatives_formulated * 10))

    overall = int((eg_score * 0.25) + (sf_score * 0.20) + (sk_score * 0.20) + (un_score * 0.20) + (al_score * 0.15))

    rating_label = "STRONG FORENSIC INVESTIGATION" if overall >= 85 else "MODERATE INVESTIGATION" if overall >= 70 else "PRELIMINARY INQUIRY"

    return {
        "evidence_grounding": eg_score,
        "suspect_fairness": sf_score,
        "skeptic_rigor": sk_score,
        "uncertainty_awareness": un_score,
        "alternative_theories": al_score,
        "overall": overall,
        "rating_label": rating_label,
        "meters": {
            "evidence_grounding": _ascii_meter(eg_score),
            "suspect_fairness": _ascii_meter(sf_score),
            "skeptic_rigor": _ascii_meter(sk_score),
            "uncertainty_awareness": _ascii_meter(un_score),
            "alternative_theories": _ascii_meter(al_score),
            "overall": _ascii_meter(overall)
        }
    }

def _ascii_meter(val: int) -> str:
    filled = int(val / 10)
    empty = 10 - filled
    return f"{'█' * filled}{'░' * empty} {val}%"
