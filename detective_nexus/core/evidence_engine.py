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
    <div class="evidence-card" style="background: var(--nexus-bg-card); border: 1px solid var(--nexus-border); border-left: 5px solid {badge_color}; border-radius: 6px; padding: 14px; margin-bottom: 12px; font-family: 'Segoe UI', Tahoma, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.92rem; font-weight: 800; color: var(--nexus-accent-amber);">[{eid}] {title.upper()}</span>
            <span style="background: var(--nexus-bg-subcard); border: 1px solid var(--nexus-border); color: {badge_color}; font-size: 0.72rem; font-weight: 800; padding: 3px 9px; border-radius: 4px; font-family: 'JetBrains Mono', monospace;">{classification} // {strength}</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--nexus-text-muted); margin-bottom: 8px;"><strong>Category:</strong> {cat} | <strong>Source:</strong> {evidence_item.get('source', 'Case Archive')}</div>
        <div style="background: var(--nexus-bg-subcard); border: 1px solid var(--nexus-border); border-radius: 4px; padding: 8px 10px; font-size: 0.84rem; color: var(--nexus-text-main); margin-bottom: 6px;">
            <span style="color: #10b981; font-weight: 800;">✔ ESTABLISHES:</span> {establishes}
        </div>
        <div style="background: var(--nexus-bg-subcard); border: 1px solid var(--nexus-border); border-radius: 4px; padding: 8px 10px; font-size: 0.84rem; color: #ef4444;">
            <span style="color: #ef4444; font-weight: 800;">✖ DOES NOT ESTABLISH:</span> {does_not}
        </div>
    </div>
    """
