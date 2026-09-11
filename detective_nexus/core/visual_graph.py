"""
Detective Nexus Dynamic Visual Evidence Graph
Constructs relational graph structures using NetworkX and renders crisp,
theme-responsive SVGs directly into Gradio gr.HTML components without external JS libraries.
"""

from typing import Dict, Any, List
import networkx as nx
import math

class VisualEvidenceGraph:
    """
    Builds relational forensic network graphs connecting suspects, credentials,
    crime scenes, and recovered trace evidence. Renders pure vector SVG.
    """

    @classmethod
    def generate_svg_graph(cls, case_data: Dict[str, Any], is_dark_mode: bool = True) -> str:
        """
        Builds a NetworkX graph from active case data and renders an SVG diagram.
        """
        G = nx.DiGraph()

        # Add Nodes with categories
        suspects = [s.get("name") for s in case_data.get("suspects", [])]
        evidence = [e.get("evidence_id") for e in case_data.get("evidence", [])]
        location = case_data.get("location", "Crime Scene")
        window = case_data.get("critical_window", "Critical Window")

        G.add_node(location, type="scene")
        G.add_node(window, type="window")

        for s in suspects:
            G.add_node(s, type="suspect")

        for e in case_data.get("evidence", []):
            eid = e.get("evidence_id", "E")
            title = e.get("title", eid)
            G.add_node(eid, type="evidence", label=f"{eid}: {title[:16]}")

        # Add Edges based on forensic facts
        if "Arjun Vale" in suspects and "E-B" in evidence:
            G.add_edge("Arjun Vale", "E-B", label="CARD SWIPED")
            G.add_edge("E-B", location, label="OPENED VITRINE")

        if "Arjun Vale" in suspects and "E-D" in evidence:
            G.add_edge("Arjun Vale", "E-D", label="CARRIED AT 8:25")

        if "E-D" in evidence and "E-E" in evidence:
            G.add_edge("E-D", "E-E", label="CONTAINS TRACE")
            G.add_edge("E-E", location, label="MATERIAL MATCH")

        if "Lena Ortiz" in suspects and "E-F" in evidence:
            G.add_edge("Lena Ortiz", "E-F", label="BOOT TREAD MATCH")

        G.add_edge(window, location, label="BLACKOUT DURATION")

        # Layout computation using spring layout with deterministic seed
        pos = nx.spring_layout(G, seed=42, k=1.4, iterations=50)

        # SVG Dimensions
        width = 860
        height = 480
        padding = 70

        # Scale pos to canvas
        xs = [p[0] for p in pos.values()] or [0]
        ys = [p[1] for p in pos.values()] or [0]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        range_x = (max_x - min_x) or 1
        range_y = (max_y - min_y) or 1

        scaled_pos = {}
        for node, (x, y) in pos.items():
            sx = padding + ((x - min_x) / range_x) * (width - 2 * padding)
            sy = padding + ((y - min_y) / range_y) * (height - 2 * padding)
            scaled_pos[node] = (sx, sy)

        # Theme Colors
        if is_dark_mode:
            bg_color = "#07090e"
            border_color = "#1e293b"
            text_color = "#f8fafc"
            edge_color = "#475569"
            suspect_color = "#a855f7" # Purple
            evidence_color = "#f59e0b" # Amber
            scene_color = "#ef4444" # Red
            window_color = "#38bdf8" # Cyan
        else:
            bg_color = "#ffffff"
            border_color = "#cbd5e1"
            text_color = "#0f172a"
            edge_color = "#94a3b8"
            suspect_color = "#7c3aed"
            evidence_color = "#d97706"
            scene_color = "#dc2626"
            window_color = "#0284c7"

        # Generate SVG Edges
        edge_svg = []
        for u, v, data in G.edges(data=True):
            if u in scaled_pos and v in scaled_pos:
                x1, y1 = scaled_pos[u]
                x2, y2 = scaled_pos[v]
                label = data.get("label", "")
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                edge_svg.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{edge_color}" stroke-width="2" stroke-dasharray="4,4" />'
                )
                if label:
                    edge_svg.append(
                        f'<text x="{mid_x:.1f}" y="{mid_y - 4:.1f}" fill="{edge_color}" font-size="9" font-family="monospace" text-anchor="middle">{label}</text>'
                    )

        # Generate SVG Nodes
        node_svg = []
        for node, data in G.nodes(data=True):
            if node in scaled_pos:
                x, y = scaled_pos[node]
                ntype = data.get("type", "default")

                if ntype == "suspect":
                    fill = suspect_color
                    rad = 22
                    shape = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{fill}" fill-opacity="0.25" stroke="{fill}" stroke-width="2.5" />'
                elif ntype == "evidence":
                    fill = evidence_color
                    rad = 20
                    shape = f'<rect x="{x-rad:.1f}" y="{y-rad:.1f}" width="{rad*2}" height="{rad*2}" rx="4" fill="{fill}" fill-opacity="0.25" stroke="{fill}" stroke-width="2.5" />'
                elif ntype == "scene":
                    fill = scene_color
                    rad = 24
                    shape = f'<polygon points="{x:.1f},{y-rad:.1f} {x+rad:.1f},{y+rad:.1f} {x-rad:.1f},{y+rad:.1f}" fill="{fill}" fill-opacity="0.25" stroke="{fill}" stroke-width="2.5" />'
                else: # window
                    fill = window_color
                    rad = 18
                    shape = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{fill}" fill-opacity="0.25" stroke="{fill}" stroke-width="2" />'

                node_svg.append(shape)
                clean_name = str(node)[:14]
                node_svg.append(
                    f'<text x="{x:.1f}" y="{y + rad + 14:.1f}" fill="{text_color}" font-size="10" font-weight="bold" font-family="sans-serif" text-anchor="middle">{clean_name}</text>'
                )

        svg_content = f"""
<div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 10px; padding: 12px; margin: 12px 0; overflow-x: auto;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-family: monospace; font-size: 0.8rem; color: {text_color};">
        <strong>FORENSIC RELATIONAL EVIDENCE NETWORK (NETWORKX VISUALIZER)</strong>
        <span>● Purple: Suspects | ■ Amber: Evidence | ▲ Red: Crime Scene | ○ Cyan: Window</span>
    </div>
    <svg width="100%" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="display: block; margin: 0 auto;">
        <!-- Edges -->
        {"".join(edge_svg)}
        <!-- Nodes -->
        {"".join(node_svg)}
    </svg>
</div>
"""
        return svg_content
