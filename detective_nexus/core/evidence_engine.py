from typing import Dict, Any, List

def generate_evidence_connection_graph_markdown(relationships: List[Dict[str, str]]) -> str:
    """
    Renders an ASCII / Markdown forensic evidence connection graph.
    Visualizes key relationships between Suspects, Credentials, Crime Scene, and Physical Traces.
    """
    graph_md = """```text
========================================================================================
                      FORENSIC EVIDENCE CONNECTION GRAPH (NEXUS-REL)
========================================================================================

   [ SUSPECT: S03 ARJUN VALE ]
             |
             +==== (ISSUED TO) =====> [ EVIDENCE E-A / E-B: ACCESS CARD ]
             |                                    |
             |                                    +==== (OPERATED AT 8:23 PM) ====> [ ROTUNDA VITRINE ]
             |                                                                             |
             |                                                                     (CONCEALED GEM)
             |                                                                             |
             +==== (CARRIED AT 8:25 PM) ==> [ EVIDENCE E-D: FLAT FOLDER ]                  |
                                                          |                                |
                                                          +==== (CONTAINS TRACE) =========+
                                                                         |
                                                                         v
                                                       [ EVIDENCE E-E: BLUE FIBERS ]
                                                                         |
                                                               (MATERIAL SIMILARITY)
                                                                         |
                                                                         v
                                                        [ ROTUNDA DISPLAY CUSHION ]

----------------------------------------------------------------------------------------
   [ SUSPECT: S01 LENA ORTIZ ]
             |
             +==== (TREAD SIZE MATCH) => [ EVIDENCE E-F: MUDDY BOOTPRINT ]
                                                       |
                                            (ALTERNATIVE EXPLANATION)
                                                       |
                                                       v
                                            [ RAINY COURTYARD PATROL ]
========================================================================================
```
"""
    return graph_md

def format_evidence_card_html(evidence_item: Dict[str, Any]) -> str:
    """Generates forensic terminal card HTML for an evidence item."""
    eid = evidence_item.get("evidence_id", "E-??")
    title = evidence_item.get("title", "Unknown Clue")
    cat = evidence_item.get("category", "Forensic")
    strength = evidence_item.get("strength", "MODERATE")
    classification = evidence_item.get("classification", "FACT")
    establishes = evidence_item.get("establishes", "")
    does_not = evidence_item.get("does_not_establish", "")

    badge_color = "#10b981" if "VERY STRONG" in strength or "STRONG" in strength else "#f59e0b" if "MODERATE" in strength else "#ef4444"

    return f"""
    <div style="background: #111827; border: 1px solid #374151; border-left: 4px solid {badge_color}; border-radius: 6px; padding: 14px; margin-bottom: 12px; font-family: 'Segoe UI', Tahoma, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-family: monospace; font-size: 0.9rem; font-weight: bold; color: #fbbf24;">[{eid}] {title.upper()}</span>
            <span style="background: #1f2937; border: 1px solid #4b5563; color: {badge_color}; font-size: 0.72rem; font-weight: bold; padding: 2px 8px; border-radius: 4px; font-family: monospace;">{classification} // {strength}</span>
        </div>
        <div style="font-size: 0.85rem; color: #9ca3af; margin-bottom: 8px;"><strong>Category:</strong> {cat} | <strong>Source:</strong> {evidence_item.get('source', 'Unknown')}</div>
        <div style="background: #0b0f19; border-radius: 4px; padding: 8px; font-size: 0.82rem; color: #e5e7eb; margin-bottom: 6px;">
            <span style="color: #34d399; font-weight: bold;">✔ ESTABLISHES:</span> {establishes}
        </div>
        <div style="background: #0b0f19; border-radius: 4px; padding: 8px; font-size: 0.82rem; color: #f87171;">
            <span style="color: #ef4444; font-weight: bold;">✖ DOES NOT ESTABLISH:</span> {does_not}
        </div>
    </div>
    """
