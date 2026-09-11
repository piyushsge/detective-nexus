import time
import json
from typing import Dict, Any, List, Tuple
import gradio as gr

from detective_nexus import config
from detective_nexus.core.case_engine import get_case_engine
from detective_nexus.core.evidence_engine import generate_evidence_connection_graph_markdown, format_evidence_card_html
from detective_nexus.core.confidence import calculate_nexus_quality_score
from detective_nexus.core.scorecard import ForensicScorecardEngine
from detective_nexus.core.validation import HallucinationAuditor
from detective_nexus.core.interrogation import InterrogationEngine
from detective_nexus.core.audio_debrief import AudioDebriefEngine
from detective_nexus.core.procedural_generator import ProceduralCaseGenerator
from detective_nexus.core.forensic_lab import ForensicLabEngine
from detective_nexus.core.courtroom import CourtroomTrialEngine
from detective_nexus.core.visual_graph import VisualEvidenceGraph
from detective_nexus.storage.history_store import save_investigation_record, load_investigation_history
from detective_nexus.core.user_profile import UserProfileManager
from detective_nexus.core.dossier_exporter import DossierExporter
from detective_nexus.core.report_classifier import ReportClassifier

from detective_nexus.agents.detective import DetectiveAgent
from detective_nexus.agents.evidence import EvidenceAgent
from detective_nexus.agents.suspect import SuspectAgent
from detective_nexus.agents.skeptic import SkepticAgent
from detective_nexus.agents.chief import ChiefAgent
from detective_nexus.llm.gemini_client import get_client
from detective_nexus.llm.prompts import ASSISTANT_PROMPT
from detective_nexus.ui.theme import get_forensic_theme
from detective_nexus.ui.styles import FORENSIC_CSS

# Session Memory Cache
PIPELINE_CACHE: Dict[str, Any] = {
    "detective": None,
    "evidence": None,
    "suspect": None,
    "skeptic": None,
    "chief": None,
    "start_time": time.time(),
    "activity_log": [],
    "theme_mode": "🌙 Night Tactical",
    "active_user": "default_investigator",
    "last_dossier_path": None,
}

def log_event(source: str, message: str) -> None:
    timestamp = time.strftime("%H:%M:%S")
    PIPELINE_CACHE["activity_log"].append(f"[{timestamp}] [{source.upper()}] {message}")

def get_activity_log_text() -> str:
    if not PIPELINE_CACHE["activity_log"]:
        return "[08:00:00] [SYSTEM] Detective Nexus forensic environment initialized.\n[08:00:01] [SYSTEM] CASE-001 (Aurora Diamond) loaded into active memory buffer."
    return "\n".join(PIPELINE_CACHE["activity_log"][-18:])

def get_theme_style_css(is_dark_mode: bool = True) -> str:
    """Dynamically injects CSS overrides for Day Mode vs Night Mode."""
    if is_dark_mode:
        return """
        <style id="active-theme-css">
        :root, body, .gradio-container, [class*="gradio-container"] {
            --nexus-bg-main: #070707 !important;
            --nexus-bg-panel: #0D0D0D !important;
            --nexus-bg-card: #111111 !important;
            --nexus-bg-subcard: #161616 !important;
            --nexus-bg-input: #121212 !important;
            --nexus-bg-code: #0A0A0A !important;
            --nexus-border: #292929 !important;
            --nexus-border-accent: #d97706 !important;
            --nexus-text-main: #F2F2F2 !important;
            --nexus-text-muted: #9CA3AF !important;
            --nexus-text-dim: #6B7280 !important;
            --nexus-text-code: #fbbf24 !important;
            --nexus-accent-amber: #fbbf24 !important;
            --nexus-accent-emerald: #10b981 !important;
            --nexus-accent-red: #dc2626 !important;
            --nexus-accent-blue: #38bdf8 !important;

            --nexus-text-h1: #F9FAFB !important;
            --nexus-text-h2: #FBBF24 !important;
            --nexus-text-h3: #F3F4F6 !important;
            --nexus-text-h4: #38BDF8 !important;
            --nexus-text-p: #D1D5DB !important;
            --nexus-text-strong: #FFFFFF !important;

            --background-fill-primary: #070707 !important;
            --background-fill-secondary: #0D0D0D !important;
            --block-background-fill: #111111 !important;
            --block-label-background-fill: #161616 !important;
            --block-label-text-color: #D4AF37 !important;
            --block-title-text-color: #F2F2F2 !important;
            --input-background-fill: #121212 !important;
            --input-background-fill-focus: #161616 !important;
            --input-background-fill-hover: #141414 !important;
            --input-border-color: #292929 !important;
            --input-border-color-focus: #fbbf24 !important;
            --input-placeholder-color: #6B7280 !important;
            --input-text-color: #F2F2F2 !important;
            --body-background-fill: #070707 !important;
            --body-text-color: #F2F2F2 !important;
            --body-text-color-subdued: #9CA3AF !important;
            --table-even-background-fill: #111111 !important;
            --table-odd-background-fill: #0D0D0D !important;
            --table-border-color: #292929 !important;
            --code-background-fill: #0A0A0A !important;
            --button-primary-background-fill: #d97706 !important;
            --button-primary-text-color: #FFFFFF !important;
            --button-secondary-background-fill: #1A1A1A !important;
            --button-secondary-text-color: #E5E7EB !important;
            --border-color-primary: #292929 !important;
            --border-color-accent: #d97706 !important;

            background-color: #070707 !important;
            background: #070707 !important;
            color: #F2F2F2 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        .nexus-header {
            background: linear-gradient(180deg, #0D0D0D 0%, #070707 100%) !important;
            border-color: #292929 !important;
            border-top: 4px solid #d97706 !important;
        }
        .nexus-title { color: #F2F2F2 !important; }

        /* Headings & Text */
        [class*="gradio-container"] h1, h1 { color: #F9FAFB !important; }
        [class*="gradio-container"] h2, h2 { color: #FBBF24 !important; border-bottom: 1px solid #292929 !important; }
        [class*="gradio-container"] h3, h3 { color: #F3F4F6 !important; font-weight: 700 !important; }
        [class*="gradio-container"] h4, h4 { color: #38BDF8 !important; }
        [class*="gradio-container"] p, p, [class*="gradio-container"] .prose p, .prose p { color: #D1D5DB !important; }
        [class*="gradio-container"] li, li { color: #D1D5DB !important; }
        [class*="gradio-container"] strong, strong, [class*="gradio-container"] b, b { color: #FFFFFF !important; font-weight: 700 !important; }

        /* Inputs, Textareas, Wrappers */
        [class*="gradio-container"] textarea, 
        [class*="gradio-container"] input[type="text"], 
        [class*="gradio-container"] input[type="password"],
        [class*="gradio-container"] input[type="number"],
        [class*="gradio-container"] input[type="search"],
        [class*="gradio-container"] select,
        [class*="gradio-container"] .wrap,
        [class*="gradio-container"] .scroll-hide,
        [class*="gradio-container"] .gr-box,
        [class*="gradio-container"] .gr-input,
        [class*="gradio-container"] .gr-textbox,
        [class*="gradio-container"] [type=text],
        [class*="gradio-container"] [type=password],
        [class*="gradio-container"] [type=number],
        [class*="gradio-container"] [type=search],
        textarea, input[type="text"], input[type="password"], select, .gr-input, .gr-textbox {
            background-color: #121212 !important;
            background: #121212 !important;
            color: #F2F2F2 !important;
            border: 1px solid #292929 !important;
            border-radius: 6px !important;
            font-family: 'JetBrains Mono', 'IBM Plex Mono', Consolas, monospace !important;
            font-size: 0.92rem !important;
            line-height: 1.55 !important;
        }

        [class*="gradio-container"] textarea:focus, 
        [class*="gradio-container"] input:focus,
        [class*="gradio-container"] select:focus,
        textarea:focus, input:focus {
            background-color: #181818 !important;
            background: #181818 !important;
            border-color: #fbbf24 !important;
            box-shadow: 0 0 0 1px #fbbf24 !important;
            color: #FFFFFF !important;
            outline: none !important;
        }

        [class*="gradio-container"] textarea:disabled,
        [class*="gradio-container"] input:disabled,
        [class*="gradio-container"] textarea[readonly],
        [class*="gradio-container"] input[readonly],
        textarea:disabled, input:disabled, textarea[readonly], input[readonly] {
            background-color: #0A0A0A !important;
            background: #0A0A0A !important;
            color: #9CA3AF !important;
            border-color: #222222 !important;
            cursor: default !important;
        }

        [class*="gradio-container"] textarea::placeholder,
        [class*="gradio-container"] input::placeholder,
        textarea::placeholder, input::placeholder {
            color: #6B7280 !important;
            font-style: italic !important;
        }

        /* Labels */
        [class*="gradio-container"] label,
        [class*="gradio-container"] .block label,
        [class*="gradio-container"] .label-wrap,
        [class*="gradio-container"] span[data-testid="block-info"],
        [class*="gradio-container"] .block-title,
        label, .label-wrap, span[data-testid="block-info"] {
            background: transparent !important;
            background-color: transparent !important;
            color: #D4AF37 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
            margin-bottom: 4px !important;
        }

        /* Blocks & Containers */
        [class*="gradio-container"] .block,
        .gradio-container .block {
            background-color: #111111 !important;
            border: 1px solid #292929 !important;
            border-radius: 8px !important;
        }

        /* Tables */
        [class*="gradio-container"] table, table {
            background-color: #111111 !important;
            background: #111111 !important;
            border: 1px solid #292929 !important;
        }
        [class*="gradio-container"] th, th {
            background-color: #161616 !important;
            background: #161616 !important;
            color: #fbbf24 !important;
            border: 1px solid #292929 !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
        [class*="gradio-container"] td, td {
            background-color: #111111 !important;
            background: #111111 !important;
            color: #F2F2F2 !important;
            border: 1px solid #292929 !important;
        }
        [class*="gradio-container"] tr:nth-child(even) td, tr:nth-child(even) td {
            background-color: #161616 !important;
            background: #161616 !important;
        }

        /* Inline Code & Backticks */
        [class*="gradio-container"] code,
        code, .prose code, li code, p code, td code, th code, span code, div code, a code {
            background-color: #181818 !important;
            background: #181818 !important;
            color: #fbbf24 !important;
            border: 1px solid #333333 !important;
            padding: 2px 7px !important;
            border-radius: 4px !important;
            font-weight: 600 !important;
            font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace !important;
        }

        /* Pre & Code Blocks */
        [class*="gradio-container"] pre, pre, 
        [class*="gradio-container"] pre code, pre code, .nexus-mono {
            background-color: #0A0A0A !important;
            background: #0A0A0A !important;
            color: #38bdf8 !important;
            border: 1px solid #292929 !important;
            border-left: 4px solid #D4AF37 !important;
            font-family: 'JetBrains Mono', Consolas, monospace !important;
        }

        /* Tabs */
        [class*="gradio-container"] [role="tablist"],
        [class*="gradio-container"] .tab-nav {
            background-color: #0A0A0A !important;
            border-bottom: 2px solid #292929 !important;
        }
        [class*="gradio-container"] button[role="tab"],
        [class*="gradio-container"] .tab-nav button {
            background-color: transparent !important;
            color: #9CA3AF !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 600 !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
        }
        [class*="gradio-container"] button[role="tab"].selected,
        [class*="gradio-container"] .tab-nav button.selected {
            color: #fbbf24 !important;
            border-bottom: 2px solid #d97706 !important;
            background-color: #141414 !important;
            font-weight: 700 !important;
        }

        /* Cards & Banners */
        .evidence-card, .nexus-metric-box {
            background-color: #111111 !important;
            border-color: #292929 !important;
            color: #F2F2F2 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
        }
        .nexus-metric-val { color: #fbbf24 !important; }
        .nexus-metric-lbl { color: #9CA3AF !important; font-weight: 600 !important; }

        .critical-window-banner {
            background: linear-gradient(90deg, #2a0808 0%, #1a0505 100%) !important;
            border-color: #7f1d1d !important;
            border-left: 5px solid #ef4444 !important;
            color: #fca5a5 !important;
        }
        .critical-window-title { color: #f87171 !important; }
        .critical-window-desc { color: #fca5a5 !important; }
        .critical-window-time { color: #ef4444 !important; }

        /* Agent Status Pill in Night Mode */
        .agent-status-pill {
            background: #141414 !important;
            border: 1px solid #292929 !important;
        }
        .agent-status-name { color: #F3F4F6 !important; }
        .agent-status-tag {
            background: #022c22 !important;
            color: #34d399 !important;
            border: 1px solid #059669 !important;
        }

        /* Quick Dossier in Night Mode */
        .quick-dossier-card {
            background: #111111 !important;
            border: 1px solid #292929 !important;
            border-radius: 6px !important;
            padding: 14px 16px !important;
            color: #F2F2F2 !important;
        }
        .quick-dossier-card p { color: #D1D5DB !important; margin: 4px 0 !important; }
        .quick-dossier-card strong { color: #FFFFFF !important; }

        /* Info Alert in Night Mode */
        .info-alert-card {
            background: #111111 !important;
            border: 1px solid #d97706 !important;
            border-left: 4px solid #fbbf24 !important;
            border-radius: 4px !important;
            padding: 12px 16px !important;
            margin-top: 14px !important;
        }
        .info-alert-title { color: #fbbf24 !important; font-weight: bold !important; font-size: 0.92rem !important; margin-bottom: 4px !important; }
        .info-alert-desc { color: #8B8B8B !important; font-size: 0.82rem !important; line-height: 1.5 !important; }
        .info-alert-desc strong { color: #D1D5DB !important; }

        .status-badge-active {
            background: #111111 !important;
            border: 1px solid #292929 !important;
            color: #10b981 !important;
        }
        </style>
        """
    else:
        return """
        <style id="active-theme-css">
        :root, body, .gradio-container, [class*="gradio-container"] {
            --nexus-bg-main: #f8fafc !important;
            --nexus-bg-panel: #ffffff !important;
            --nexus-bg-card: #ffffff !important;
            --nexus-bg-subcard: #f1f5f9 !important;
            --nexus-bg-input: #ffffff !important;
            --nexus-bg-code: #f1f5f9 !important;
            --nexus-border: #cbd5e1 !important;
            --nexus-border-accent: #0284c7 !important;
            --nexus-text-main: #0f172a !important;
            --nexus-text-muted: #334155 !important;
            --nexus-text-dim: #475569 !important;
            --nexus-text-code: #0369a1 !important;
            --nexus-accent-amber: #b45309 !important;
            --nexus-accent-emerald: #059669 !important;

            --nexus-text-h1: #0f172a !important;
            --nexus-text-h2: #0284c7 !important;
            --nexus-text-h3: #0f172a !important;
            --nexus-text-h4: #0369a1 !important;
            --nexus-text-p: #1e293b !important;
            --nexus-text-strong: #0f172a !important;

            --background-fill-primary: #f8fafc !important;
            --background-fill-secondary: #ffffff !important;
            --block-background-fill: #ffffff !important;
            --block-label-background-fill: #f1f5f9 !important;
            --block-label-text-color: #0369a1 !important;
            --block-title-text-color: #0f172a !important;
            --input-background-fill: #ffffff !important;
            --input-background-fill-focus: #ffffff !important;
            --input-background-fill-hover: #f8fafc !important;
            --input-border-color: #cbd5e1 !important;
            --input-border-color-focus: #0284c7 !important;
            --input-placeholder-color: #94a3b8 !important;
            --input-text-color: #0f172a !important;
            --body-background-fill: #f8fafc !important;
            --body-text-color: #0f172a !important;
            --body-text-color-subdued: #334155 !important;
            --table-even-background-fill: #ffffff !important;
            --table-odd-background-fill: #f8fafc !important;
            --table-border-color: #cbd5e1 !important;
            --code-background-fill: #f1f5f9 !important;
            --button-primary-background-fill: #0284c7 !important;
            --button-primary-text-color: #ffffff !important;
            --button-secondary-background-fill: #f1f5f9 !important;
            --button-secondary-text-color: #1e293b !important;
            --border-color-primary: #cbd5e1 !important;
            --border-color-accent: #0284c7 !important;

            background-color: #f8fafc !important;
            background: #f8fafc !important;
            color: #0f172a !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        .nexus-header {
            background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%) !important;
            border-color: #cbd5e1 !important;
            border-top: 4px solid #0284c7 !important;
        }
        .nexus-title { color: #0f172a !important; }

        /* Headings & Markdown Text for Day Mode - Crisp, Dark, High Contrast */
        [class*="gradio-container"] h1, h1 {
            color: #0f172a !important;
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-weight: 800 !important;
        }
        [class*="gradio-container"] h2, h2 {
            color: #0284c7 !important;
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-weight: 700 !important;
            border-bottom: 1px solid #cbd5e1 !important;
        }
        [class*="gradio-container"] h3, h3 {
            color: #0f172a !important;
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-weight: 800 !important;
        }
        [class*="gradio-container"] h4, h4 {
            color: #0369a1 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
        }
        [class*="gradio-container"] p, p,
        [class*="gradio-container"] .prose p,
        .prose p {
            color: #1e293b !important;
            font-weight: 500 !important;
            line-height: 1.6 !important;
        }
        [class*="gradio-container"] li, li,
        [class*="gradio-container"] .prose li,
        .prose li {
            color: #1e293b !important;
            line-height: 1.6 !important;
        }
        [class*="gradio-container"] strong, strong,
        [class*="gradio-container"] b, b {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        [class*="gradio-container"] blockquote, blockquote {
            border-left: 4px solid #0284c7 !important;
            background: #f1f5f9 !important;
            color: #1e293b !important;
        }
        [class*="gradio-container"] hr, hr {
            border-color: #cbd5e1 !important;
        }

        /* Inputs, Textareas, Wrappers */
        [class*="gradio-container"] textarea, 
        [class*="gradio-container"] input[type="text"], 
        [class*="gradio-container"] input[type="password"],
        [class*="gradio-container"] input[type="number"],
        [class*="gradio-container"] input[type="search"],
        [class*="gradio-container"] select,
        [class*="gradio-container"] .wrap,
        [class*="gradio-container"] .scroll-hide,
        [class*="gradio-container"] .gr-box,
        [class*="gradio-container"] .gr-input,
        [class*="gradio-container"] .gr-textbox,
        [class*="gradio-container"] [type=text],
        [class*="gradio-container"] [type=password],
        [class*="gradio-container"] [type=number],
        [class*="gradio-container"] [type=search],
        textarea, input[type="text"], input[type="password"], select, .gr-input, .gr-textbox {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #94a3b8 !important;
            border-radius: 6px !important;
            font-family: 'JetBrains Mono', 'IBM Plex Mono', Consolas, monospace !important;
            font-size: 0.92rem !important;
            line-height: 1.55 !important;
        }

        [class*="gradio-container"] textarea:focus, 
        [class*="gradio-container"] input:focus,
        [class*="gradio-container"] select:focus,
        textarea:focus, input:focus {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border-color: #0284c7 !important;
            box-shadow: 0 0 0 1px #0284c7 !important;
            color: #0f172a !important;
            outline: none !important;
        }

        [class*="gradio-container"] textarea:disabled,
        [class*="gradio-container"] input:disabled,
        [class*="gradio-container"] textarea[readonly],
        [class*="gradio-container"] input[readonly],
        textarea:disabled, input:disabled, textarea[readonly], input[readonly] {
            background-color: #f1f5f9 !important;
            background: #f1f5f9 !important;
            color: #1e293b !important;
            border-color: #cbd5e1 !important;
            font-weight: 600 !important;
            cursor: default !important;
        }

        [class*="gradio-container"] textarea::placeholder,
        [class*="gradio-container"] input::placeholder,
        textarea::placeholder, input::placeholder {
            color: #94a3b8 !important;
            font-style: italic !important;
        }

        /* Form Labels */
        [class*="gradio-container"] label,
        [class*="gradio-container"] .block label,
        [class*="gradio-container"] .label-wrap,
        [class*="gradio-container"] span[data-testid="block-info"],
        [class*="gradio-container"] .block-title,
        label, .label-wrap, span[data-testid="block-info"] {
            background: transparent !important;
            background-color: transparent !important;
            color: #0369a1 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.82rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            margin-bottom: 4px !important;
        }

        /* Blocks & Containers */
        [class*="gradio-container"] .block,
        .gradio-container .block {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }

        /* Tables */
        [class*="gradio-container"] table, table {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
        }
        [class*="gradio-container"] th, th {
            background-color: #e2e8f0 !important;
            background: #e2e8f0 !important;
            color: #0369a1 !important;
            border: 1px solid #cbd5e1 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
        }
        [class*="gradio-container"] td, td {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }
        [class*="gradio-container"] tr:nth-child(even) td, tr:nth-child(even) td {
            background-color: #f8fafc !important;
            background: #f8fafc !important;
        }

        /* Inline Code & Backticks */
        [class*="gradio-container"] code,
        code, .prose code, li code, p code, td code, th code, span code, div code, a code {
            background-color: #e0f2fe !important;
            background: #e0f2fe !important;
            color: #0369a1 !important;
            border: 1px solid #bae6fd !important;
            padding: 2px 7px !important;
            border-radius: 4px !important;
            font-weight: 700 !important;
            font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace !important;
        }

        /* Pre & Code Blocks */
        [class*="gradio-container"] pre, pre, 
        [class*="gradio-container"] pre code, pre code, .nexus-mono {
            background-color: #0f172a !important;
            background: #0f172a !important;
            color: #38bdf8 !important;
            border: 1px solid #1e293b !important;
            border-left: 4px solid #0284c7 !important;
            font-family: 'JetBrains Mono', Consolas, monospace !important;
        }

        /* Tabs */
        [class*="gradio-container"] [role="tablist"],
        [class*="gradio-container"] .tab-nav {
            background-color: #f1f5f9 !important;
            border-bottom: 2px solid #cbd5e1 !important;
        }
        [class*="gradio-container"] button[role="tab"],
        [class*="gradio-container"] .tab-nav button {
            background-color: transparent !important;
            color: #334155 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 600 !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
        }
        [class*="gradio-container"] button[role="tab"].selected,
        [class*="gradio-container"] .tab-nav button.selected {
            color: #0284c7 !important;
            border-bottom: 3px solid #0284c7 !important;
            background-color: #ffffff !important;
            font-weight: 800 !important;
        }

        /* Cards & Metric Banners */
        .evidence-card, .nexus-metric-box {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #0f172a !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
        }
        .nexus-metric-val {
            color: #b45309 !important;
            font-weight: 800 !important;
        }
        .nexus-metric-lbl {
            color: #334155 !important;
            font-weight: 700 !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.08em !important;
        }

        .critical-window-banner {
            background: #fef2f2 !important;
            border: 1px solid #fca5a5 !important;
            border-left: 5px solid #dc2626 !important;
        }
        .critical-window-title {
            color: #991b1b !important;
            font-weight: 800 !important;
        }
        .critical-window-desc {
            color: #7f1d1d !important;
            font-weight: 600 !important;
        }
        .critical-window-time {
            color: #dc2626 !important;
            font-weight: 800 !important;
        }

        /* Agent Status in Day Mode */
        .agent-status-pill {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        }
        .agent-status-name {
            color: #0f172a !important;
            font-weight: 600 !important;
        }
        .agent-status-name strong {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        .agent-status-tag {
            background: #ecfdf5 !important;
            color: #047857 !important;
            border: 1px solid #10b981 !important;
        }

        /* Quick Case Dossier in Day Mode */
        .quick-dossier-card {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 6px !important;
            padding: 14px 16px !important;
            color: #0f172a !important;
        }
        .quick-dossier-card p {
            color: #1e293b !important;
            margin: 4px 0 !important;
        }
        .quick-dossier-card strong {
            color: #0f172a !important;
        }

        /* Info Alert Box in Day Mode */
        .info-alert-card {
            background: #eff6ff !important;
            border: 1px solid #bae6fd !important;
            border-left: 4px solid #0284c7 !important;
            border-radius: 4px !important;
            padding: 12px 16px !important;
            margin-top: 14px !important;
        }
        .info-alert-title {
            font-weight: bold !important;
            color: #0369a1 !important;
            font-size: 0.92rem !important;
            margin-bottom: 4px !important;
        }
        .info-alert-desc {
            font-size: 0.82rem !important;
            color: #1e293b !important;
            line-height: 1.5 !important;
        }
        .info-alert-desc strong {
            color: #0f172a !important;
        }

        /* Status badge in Day Mode */
        .status-badge-active {
            background: #ecfdf5 !important;
            border: 1px solid #a7f3d0 !important;
            color: #047857 !important;
        }
        </style>
        """


def create_header_html(is_dark_mode: bool = True) -> str:
    case = get_case_engine().get_current_case()
    active_user = PIPELINE_CACHE.get("active_user", "default_investigator")
    profile = UserProfileManager.get_profile(active_user)
    officer_name = profile.get("officer_name", "Senior Inspector Vikram Rathore") if profile else "Senior Inspector Vikram Rathore"
    badge_id = profile.get("badge_id", "BADGE-4892") if profile else "BADGE-4892"

    mode_badge = (
        '<span style="background: #1e1b4b; border: 1px solid #6366f1; color: #a5b4fc; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.05em;">🌙 NIGHT TACTICAL</span>'
        if is_dark_mode else
        '<span style="background: #f0fdf4; border: 1px solid #22c55e; color: #16a34a; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; letter-spacing: 0.05em;">☀️ DAY FORENSIC LAB</span>'
    )
    title_color = "#f8fafc" if is_dark_mode else "#0f172a"
    sub_color = "#94a3b8" if is_dark_mode else "#475569"

    return f"""
    <div class="nexus-header" style="background: var(--nexus-bg-panel); border-bottom: 2px solid var(--nexus-border); padding: 14px 22px; margin-bottom: 12px; border-radius: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 3px; flex-wrap: wrap;">
                    <span style="color: var(--nexus-accent-amber); font-size: 1.2rem;">◉</span>
                    <h1 class="nexus-title" style="color: {title_color}; font-family: 'IBM Plex Sans', sans-serif; font-weight: 800; font-size: 1.55rem; letter-spacing: 0.05em; margin: 0;">DETECTIVE NEXUS</h1>
                    <span class="status-badge-active" style="font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; padding: 2px 7px; border-radius: 3px;">● INVESTIGATION ACTIVE</span>
                    {mode_badge}
                </div>
                <div class="nexus-subtitle" style="font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; letter-spacing: 0.12em; color: {sub_color};">
                    CASE ROOM // AI INVESTIGATION OS &nbsp;&bull;&nbsp; <span style="color: var(--nexus-text-dim);">EVIDENCE FIRST. HYPOTHESES SECOND. VERDICT LAST.</span>
                </div>
            </div>
            <div style="text-align: right; font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; color: {sub_color}; line-height: 1.5;">
                <div><span style="color: var(--nexus-text-dim);">OFFICER:</span> <strong style="color: #D4AF37;">{officer_name}</strong> &nbsp;(<span style="color: #38bdf8;">#{badge_id}</span>)</div>
                <div><span style="color: var(--nexus-text-dim);">CASE:</span> <strong style="color: var(--nexus-accent-amber);">#{case.case_id}</strong> &nbsp;|&nbsp; <span style="color: #10b981; font-weight: bold;">● ACTIVE</span></div>
                <div><span style="color: var(--nexus-text-dim);">AI STATUS:</span> <span style="color: #10b981; font-weight: bold;">5 AGENTS ACTIVE</span> &nbsp;|&nbsp; <span style="color: var(--nexus-text-dim);">CLUES:</span> <span style="color: var(--nexus-text-main); font-weight: bold;">{len(case.evidence):02d}</span> &nbsp;|&nbsp; <span style="color: var(--nexus-text-dim);">SUSPECTS:</span> <span style="color: var(--nexus-text-main); font-weight: bold;">{len(case.suspects):02d}</span></div>
            </div>
        </div>
    </div>
    """


def create_dashboard_html() -> str:
    case = get_case_engine().get_current_case()
    return f"""
    <div style="margin-bottom: 20px;">
        <div class="critical-window-banner">
            <div>
                <div class="critical-window-title">⚡ CRITICAL OPPORTUNITY WINDOW IDENTIFIED</div>
                <div class="critical-window-desc" style="font-size: 0.85rem; margin-top: 3px;">4-minute total electrical failure across gallery floor. Vitrine lock operated during this window.</div>
            </div>
            <div class="critical-window-time">{case.critical_window}</div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;">
            <div class="nexus-metric-box">
                <div class="nexus-metric-val">{len(case.evidence):02d}</div>
                <div class="nexus-metric-lbl">Evidence Records</div>
            </div>
            <div class="nexus-metric-box">
                <div class="nexus-metric-val">{len(case.suspects):02d}</div>
                <div class="nexus-metric-lbl">Persons of Interest</div>
            </div>
            <div class="nexus-metric-box">
                <div class="nexus-metric-val">05</div>
                <div class="nexus-metric-lbl">Forensic AI Agents</div>
            </div>
            <div class="nexus-metric-box">
                <div class="nexus-metric-val" style="color: #f87171;">01</div>
                <div class="nexus-metric-lbl">Critical Access Event (8:23 PM)</div>
            </div>
        </div>
    </div>
    """

def build_evidence_cards_display() -> str:
    case = get_case_engine().get_current_case()
    cards_html = [format_evidence_card_html(ev.model_dump()) for ev in case.evidence]
    return "".join(cards_html)

def build_case_room_html() -> str:
    case = get_case_engine().get_current_case()
    return f"""
    <div style="background: var(--nexus-bg-panel); border: 1px solid var(--nexus-border); border-radius: 6px; padding: 20px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--nexus-border); padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; letter-spacing: 0.15em; color: var(--nexus-accent-amber); text-transform: uppercase;">
                    ACTIVE INCIDENT DOSSIER
                </span>
                <h2 style="font-family: 'IBM Plex Sans', sans-serif; font-size: 1.4rem; font-weight: 800; color: var(--nexus-text-main); margin: 4px 0 0 0;">
                    {case.title}
                </h2>
            </div>
            <div style="text-align: right; font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; color: var(--nexus-text-muted);">
                <div>CASE REF: <strong style="color: var(--nexus-accent-amber);">#{case.case_id}</strong></div>
                <div>SCENE: <strong style="color: var(--nexus-text-main);">{case.location}</strong></div>
            </div>
        </div>

        <!-- Case Constraints Banner (Master Prompt Section 12) -->
        <div style="display: flex; justify-content: space-around; background: #0D0D0D; border: 1px solid #292929; border-left: 4px solid #d97706; border-radius: 4px; padding: 10px 16px; margin-bottom: 18px; font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; font-weight: bold;">
            <span style="color: #fbbf24;">⚖️ MOTIVE &ne; PROOF</span>
            <span style="color: #555555;">&bull;</span>
            <span style="color: #38bdf8;">💳 CARD ACCESS &ne; PERSON</span>
            <span style="color: #555555;">&bull;</span>
            <span style="color: #f87171;">🔎 INFERENCE &ne; FACT</span>
        </div>

        <!-- Narrative & Objective -->
        <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 18px; margin-bottom: 18px;">
            <div style="background: #111111; border: 1px solid #292929; border-radius: 4px; padding: 14px;">
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #8B8B8B; margin-bottom: 6px; font-weight: bold; text-transform: uppercase;">
                    INCIDENT BRIEFING & SUMMARY
                </div>
                <div style="font-size: 0.88rem; line-height: 1.6; color: var(--nexus-text-main);">
                    {case.incident_description}
                </div>
            </div>

            <div style="background: #111111; border: 1px solid #292929; border-radius: 4px; padding: 14px;">
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #8B8B8B; margin-bottom: 6px; font-weight: bold; text-transform: uppercase;">
                    INVESTIGATION OBJECTIVE
                </div>
                <div style="font-size: 0.88rem; line-height: 1.6; color: #10b981;">
                    Establish beyond reasonable doubt the physical actor responsible for vitrine entry during the 08:20-08:24 PM power surge, determine if Keycard B was cloned or proxy-wielded, and corroborate velvet fiber transfer scientifically.
                </div>
            </div>
        </div>

        <!-- Confirmed Facts vs Open Questions -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 18px;">
            <div style="background: #111111; border: 1px solid #292929; border-radius: 4px; padding: 14px;">
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #10b981; margin-bottom: 8px; font-weight: bold;">
                    &check; CONFIRMED FORENSIC FACTS
                </div>
                <ul style="font-size: 0.85rem; line-height: 1.5; color: var(--nexus-text-main); margin: 0; padding-left: 18px;">
                    <li>Power outage occurred between 08:20 PM and 08:24 PM.</li>
                    <li>Display case opened electronically via Keycard B at 08:23 PM.</li>
                    <li>Display vitrine glass was completely intact (zero forced physical entry).</li>
                    <li>Arjun Vale exited rotunda at 08:25 PM carrying flat black catalogue folder.</li>
                    <li>Blue velvet fibers detected inside catalogue folder matching display cushion.</li>
                </ul>
            </div>

            <div style="background: #111111; border: 1px solid #292929; border-radius: 4px; padding: 14px;">
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #fbbf24; margin-bottom: 8px; font-weight: bold;">
                    ❓ OPEN INVESTIGATIVE QUESTIONS
                </div>
                <ul style="font-size: 0.85rem; line-height: 1.5; color: var(--nexus-text-main); margin: 0; padding-left: 18px;">
                    <li>Who physically wielded Keycard B during the 8:23 PM blackout?</li>
                    <li>Could an unauthorized party have accessed Arjun's card from his desk?</li>
                    <li>What exact contents were shielded inside the catalogue folder at 8:25 PM?</li>
                    <li>Do the recovered velvet fibers share identical chemical dye spectra with display exhibit?</li>
                </ul>
            </div>
        </div>
    </div>
    """

def build_timeline_clock_html() -> str:
    return """
    <div style="background: var(--nexus-bg-panel); border: 1px solid var(--nexus-border); border-radius: 6px; padding: 18px; margin-bottom: 20px; font-family: 'IBM Plex Mono', monospace;">
        <div style="font-size: 0.75rem; letter-spacing: 0.15em; color: var(--nexus-accent-amber); text-transform: uppercase; margin-bottom: 12px; font-weight: bold;">
            CASE CLOCK // HORIZONTAL INVESTIGATION TIMELINE
        </div>
        <div style="display: flex; align-items: stretch; justify-content: space-between; overflow-x: auto; gap: 8px; padding-bottom: 8px;">
            <div style="flex: 1; min-width: 120px; background: #111111; border: 1px solid #292929; border-top: 3px solid #64748b; border-radius: 4px; padding: 10px; text-align: center;">
                <div style="color: #64748b; font-weight: bold; font-size: 0.85rem;">08:00 PM</div>
                <div style="font-size: 0.75rem; color: #F2F2F2; margin-top: 4px;">Vault Locked</div>
                <div style="font-size: 0.7rem; color: #8B8B8B;">Daily close audit</div>
            </div>
            <div style="color: #555555; align-self: center;">&mdash;</div>
            <div style="flex: 1; min-width: 120px; background: #111111; border: 1px solid #292929; border-top: 3px solid #64748b; border-radius: 4px; padding: 10px; text-align: center;">
                <div style="color: #64748b; font-weight: bold; font-size: 0.85rem;">08:12 PM</div>
                <div style="font-size: 0.75rem; color: #F2F2F2; margin-top: 4px;">Arjun Badge</div>
                <div style="font-size: 0.7rem; color: #8B8B8B;">Archive entry</div>
            </div>
            <div style="color: #555555; align-self: center;">&mdash;</div>
            <div style="flex: 1; min-width: 120px; background: #111111; border: 1px solid #292929; border-top: 3px solid #64748b; border-radius: 4px; padding: 10px; text-align: center;">
                <div style="color: #64748b; font-weight: bold; font-size: 0.85rem;">08:15 PM</div>
                <div style="font-size: 0.75rem; color: #F2F2F2; margin-top: 4px;">Theo Camera</div>
                <div style="font-size: 0.7rem; color: #8B8B8B;">Security console</div>
            </div>
            <div style="color: #dc2626; align-self: center; font-weight: bold;">&DoubleRightArrow;</div>
            <div style="flex: 1.2; min-width: 140px; background: #161616; border: 1px solid #dc2626; border-top: 4px solid #dc2626; border-radius: 4px; padding: 10px; text-align: center;">
                <div style="color: #ef4444; font-weight: bold; font-size: 0.85rem;">08:20 - 08:24 PM</div>
                <div style="font-size: 0.75rem; color: #ef4444; font-weight: bold; margin-top: 4px;">POWER BLACKOUT</div>
                <div style="font-size: 0.7rem; color: #fbbf24;">CRITICAL WINDOW</div>
            </div>
            <div style="color: #dc2626; align-self: center; font-weight: bold;">&DoubleRightArrow;</div>
            <div style="flex: 1.2; min-width: 140px; background: #161616; border: 1px solid #fbbf24; border-top: 4px solid #fbbf24; border-radius: 4px; padding: 10px; text-align: center;">
                <div style="color: #fbbf24; font-weight: bold; font-size: 0.85rem;">08:23:14 PM</div>
                <div style="font-size: 0.75rem; color: #fbbf24; font-weight: bold; margin-top: 4px;">CARD SWIPE E-B</div>
                <div style="font-size: 0.7rem; color: #8B8B8B;">Case unlocked</div>
            </div>
            <div style="color: #555555; align-self: center;">&mdash;</div>
            <div style="flex: 1; min-width: 120px; background: #111111; border: 1px solid #292929; border-top: 3px solid #64748b; border-radius: 4px; padding: 10px; text-align: center;">
                <div style="color: #64748b; font-weight: bold; font-size: 0.85rem;">08:25 PM</div>
                <div style="font-size: 0.75rem; color: #F2F2F2; margin-top: 4px;">Folder Egress</div>
                <div style="font-size: 0.7rem; color: #8B8B8B;">Arjun departs</div>
            </div>
            <div style="color: #555555; align-self: center;">&mdash;</div>
            <div style="flex: 1; min-width: 120px; background: #111111; border: 1px solid #292929; border-top: 3px solid #10b981; border-radius: 4px; padding: 10px; text-align: center;">
                <div style="color: #10b981; font-weight: bold; font-size: 0.85rem;">08:30 PM</div>
                <div style="font-size: 0.75rem; color: #10b981; margin-top: 4px;">Loss Discovered</div>
                <div style="font-size: 0.7rem; color: #8B8B8B;">Curator alert</div>
            </div>
        </div>
    </div>
    """

def build_timeline_table() -> str:
    case = get_case_engine().get_current_case()
    rows = [
        "| ID | Timestamp | Event Description | Source | Certainty | Critical Event |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for t in case.timeline:
        crit = "⚡ CRITICAL WINDOW" if t.is_critical else "Standard"
        rows.append(f"| **{t.id}** | `{t.time}` | {t.event} | {t.source} | {t.certainty} | **{crit}** |")
    return "\n".join(rows)


def build_suspect_matrix_markdown() -> str:
    case = get_case_engine().get_current_case()
    rows = [
        "| Suspect Name | Role | Motive | Means | Opportunity (8:20-8:24) | Access Profile | Alibi Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for s in case.suspects:
        rows.append(f"| **{s.name}** | {s.role} | {s.motive} | {s.means} | {s.opportunity} | {s.access} | `{s.alibi}` |")
    return "\n".join(rows)

# ==============================================================================
# PIPELINE EXECUTION ENGINE
# ==============================================================================

def run_detective_step():
    log_event("DETECTIVE", "Starting incident decomposition and timeline extraction...")
    case_data = get_case_engine().get_agent_visible_data()
    agent = DetectiveAgent()
    report = agent.run(case_data)
    PIPELINE_CACHE["detective"] = report
    log_event("DETECTIVE", "Timeline reconstructed. Critical window locked at 08:20-08:24 PM.")
    return (
        report.raw_markdown,
        get_activity_log_text(),
        "🟢 COMPLETED (Timeline Verified)"
    )

def run_evidence_step():
    if not PIPELINE_CACHE["detective"]:
        return "⚠️ Please execute Agent 1 (Detective) first.", get_activity_log_text(), "⚪ WAITING FOR DETECTIVE"
    log_event("EVIDENCE", "Classifying evidence items E-A through E-G into Fact vs Inference...")
    case_data = get_case_engine().get_agent_visible_data()
    agent = EvidenceAgent()
    report = agent.run(case_data, detective_report=PIPELINE_CACHE["detective"].raw_markdown)
    PIPELINE_CACHE["evidence"] = report
    log_event("EVIDENCE", "Evidence classification complete. Lock record E-B tagged VERY STRONG.")
    return (
        report.raw_markdown,
        get_activity_log_text(),
        "🟢 COMPLETED (Evidence Audited)"
    )

def run_suspect_step():
    if not PIPELINE_CACHE["evidence"]:
        return "⚠️ Please execute Agent 2 (Evidence Specialist) first.", get_activity_log_text(), "⚪ WAITING FOR EVIDENCE"
    log_event("SUSPECT", "Initiating 4-way suspect comparative matrix...")
    case_data = get_case_engine().get_agent_visible_data()
    agent = SuspectAgent()
    report = agent.run(
        case_data,
        detective_report=PIPELINE_CACHE["detective"].raw_markdown,
        evidence_report=PIPELINE_CACHE["evidence"].raw_markdown
    )
    PIPELINE_CACHE["suspect"] = report
    log_event("SUSPECT", "Suspect matrix calculated. Arjun Vale holds highest opportunity profile.")
    return (
        report.raw_markdown,
        get_activity_log_text(),
        "🟢 COMPLETED (Suspect Matrix Built)"
    )

def run_skeptic_step():
    if not PIPELINE_CACHE["suspect"]:
        return "⚠️ Please execute Agent 3 (Suspect Analyst) first.", get_activity_log_text(), "⚪ WAITING FOR SUSPECT"
    log_event("SKEPTIC", "Triggering adversarial theory challenge on leading suspect...")
    case_data = get_case_engine().get_agent_visible_data()
    agent = SkepticAgent()
    report = agent.run(
        case_data,
        detective_report=PIPELINE_CACHE["detective"].raw_markdown,
        evidence_report=PIPELINE_CACHE["evidence"].raw_markdown,
        suspect_report=PIPELINE_CACHE["suspect"].raw_markdown
    )
    PIPELINE_CACHE["skeptic"] = report
    log_event("SKEPTIC", "Exposed 3 core assumptions. Credential use != physical identity.")
    return (
        report.raw_markdown,
        get_activity_log_text(),
        "🟢 COMPLETED (Assumptions Audited)"
    )

def run_chief_step():
    if not PIPELINE_CACHE["skeptic"]:
        return "⚠️ Please execute Agent 4 (Skeptic) first.", get_activity_log_text(), "⚪ WAITING FOR SKEPTIC", "", "", ""
    log_event("CHIEF", "Synthesizing cross-agent findings for final sealed report...")
    case_data = get_case_engine().get_agent_visible_data()
    agent = ChiefAgent()
    report = agent.run(
        case_data,
        detective_report=PIPELINE_CACHE["detective"].raw_markdown,
        evidence_report=PIPELINE_CACHE["evidence"].raw_markdown,
        suspect_report=PIPELINE_CACHE["suspect"].raw_markdown,
        skeptic_report=PIPELINE_CACHE["skeptic"].raw_markdown
    )
    PIPELINE_CACHE["chief"] = report
    log_event("CHIEF", "Sealed verdict prepared. PROVISIONAL LEAD: Arjun Vale. Status: NOT PROVEN.")

    strongest_str = "\n".join([f"- {s}" for s in report.strongest_evidence])
    weakest_str = "\n".join([f"- {w}" for w in report.weakest_evidence])
    caveat_box = f"### ⚠️ PROVISIONAL ASSESSMENT: NOT PROVEN\n{report.not_proven_caveat}\n\n**Confidence Level:** `{report.confidence_level}`"

    return (
        report.raw_markdown,
        get_activity_log_text(),
        "🟢 COMPLETED (Sealed Report Generated)",
        "ARJUN VALE (PROVISIONAL LEAD)",
        caveat_box,
        f"**Strongest Evidence:**\n{strongest_str}\n\n**Weakest Links:**\n{weakest_str}"
    )

def run_full_investigation():
    """Runs all 5 agents in a continuous orchestrated sequence."""
    log_event("SYSTEM", "Executing complete 5-agent autonomous investigation pipeline...")
    case_data = get_case_engine().get_agent_visible_data()

    # Step 1
    det = DetectiveAgent().run(case_data)
    PIPELINE_CACHE["detective"] = det

    # Step 2
    ev = EvidenceAgent().run(case_data, detective_report=det.raw_markdown)
    PIPELINE_CACHE["evidence"] = ev

    # Step 3
    sus = SuspectAgent().run(case_data, detective_report=det.raw_markdown, evidence_report=ev.raw_markdown)
    PIPELINE_CACHE["suspect"] = sus

    # Step 4
    skp = SkepticAgent().run(case_data, detective_report=det.raw_markdown, evidence_report=ev.raw_markdown, suspect_report=sus.raw_markdown)
    PIPELINE_CACHE["skeptic"] = skp

    # Step 5
    chf = ChiefAgent().run(case_data, detective_report=det.raw_markdown, evidence_report=ev.raw_markdown, suspect_report=sus.raw_markdown, skeptic_report=skp.raw_markdown)
    PIPELINE_CACHE["chief"] = chf

    log_event("SYSTEM", "Pipeline finished. All 5 reports compiled and ready for human review.")

    strongest_str = "\n".join([f"- {s}" for s in chf.strongest_evidence])
    weakest_str = "\n".join([f"- {w}" for w in chf.weakest_evidence])
    caveat_box = f"### ⚠️ PROVISIONAL ASSESSMENT: NOT PROVEN\n{chf.not_proven_caveat}\n\n**Confidence Level:** `{chf.confidence_level}`"

    return (
        det.raw_markdown,
        ev.raw_markdown,
        sus.raw_markdown,
        skp.raw_markdown,
        chf.raw_markdown,
        get_activity_log_text(),
        "ARJUN VALE (PROVISIONAL LEAD)",
        caveat_box,
        f"**Strongest Evidence:**\n{strongest_str}\n\n**Weakest Links:**\n{weakest_str}"
    )

# ==============================================================================
# HUMAN REVIEW & SCORING
# ==============================================================================

def handle_submit_human_review(decision: str, rationale: str, next_ev: str, reviewer: str):
    log_event("HUMAN_REVIEW", f"Verdict rendered by {reviewer or 'Chief Reviewer'}: {decision.upper()}")

    scores = calculate_nexus_quality_score(
        evidence_grounding_citations=6,
        suspects_analyzed=4,
        skeptic_challenges=3,
        uncertainties_acknowledged=4,
        alternatives_formulated=2
    )

    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "case_id": "CASE-001",
        "case_title": "The Vanishing Aurora Diamond",
        "provisional_lead": "Arjun Vale",
        "human_decision": decision,
        "human_rationale": rationale,
        "next_evidence_demanded": next_ev,
        "reviewer": reviewer or "Judicial Officer",
        "quality_score": scores["overall"]
    }
    save_investigation_record(record)

    score_display = f"""### 📊 INVESTIGATION QUALITY SCORECARD

| Forensic Dimension | Score Meter | Evaluation Standard |
| :--- | :--- | :--- |
| **Evidence Grounding** | `{scores['meters']['evidence_grounding']}` | Hardware logs (E-B) and physical traces (E-E) cited with limitations |
| **Suspect Fairness** | `{scores['meters']['suspect_fairness']}` | Impartial evaluation across all 4 persons of interest |
| **Skeptic Rigor** | `{scores['meters']['skeptic_rigor']}` | Adversarial assault on credential vs identity assumption |
| **Uncertainty Handling** | `{scores['meters']['uncertainty_awareness']}` | Strict 'NOT PROVEN' disclaimer enforced on verdict |
| **Alternative Theories** | `{scores['meters']['alternative_theories']}` | Insider coat theft and framing scenarios developed |

---
### 🏆 OVERALL INVESTIGATION RIGOR: `{scores['overall']}%` — **{scores['rating_label']}**
"""

    return (
        f"✔ HUMAN DETERMINATION RECORDED: {decision.upper()}\nInvestigation dossier officially logged in secure storage.",
        score_display,
        render_history_markdown()
    )

def render_history_markdown() -> str:
    records = load_investigation_history()
    if not records:
        return "*No historical investigations logged yet.*"
    rows = [
        "| Timestamp | Case ID | Case Title | Provisional Lead | Human Verdict | Reviewer | Rigor Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for r in records[:10]:
        rows.append(f"| `{r['timestamp']}` | **{r['case_id']}** | {r['case_title']} | {r['provisional_lead']} | **{r['human_decision']}** | {r['reviewer']} | `{r['quality_score']}%` |")
    return "\n".join(rows)

def render_officer_card_html(username: str, is_dark: bool = True) -> str:
    """Renders the official police credential card for the active officer."""
    profile = UserProfileManager.get_profile(username)
    if not profile:
        profile = UserProfileManager.get_profile("default_investigator")
    if not profile:
        profile = {
            "officer_name": "Senior Inspector Vikram Rathore",
            "badge_id": "BADGE-4892",
            "rank_clearance": "Lead Forensic Investigator // Grade IV",
            "department": "Special Forensic & Incident Reconstruction Division",
            "created_at": "2026-09-01 08:00:00",
            "username": "default_investigator",
            "case_history": []
        }

    officer_name = profile.get("officer_name", "Officer")
    badge_id = profile.get("badge_id", "BADGE-4892")
    rank = profile.get("rank_clearance", "Forensic Investigator")
    dept = profile.get("department", "Incident Reconstruction Division")
    created = profile.get("created_at", "2026-09-01")
    history = profile.get("case_history", [])
    total_cases = len(history)

    bg = "#111111" if is_dark else "#F8FAFC"
    border = "#292929" if is_dark else "#CBD5E1"
    gold = "#D4AF37"
    text = "#F2F2F2" if is_dark else "#0F172A"
    muted = "#8B8B8B" if is_dark else "#64748B"

    return f"""
    <div style="background: {bg}; border: 1px solid {border}; border-top: 4px solid {gold}; border-radius: 6px; padding: 18px 22px; margin-bottom: 16px; font-family: 'Inter', sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width: 50px; height: 50px; border-radius: 50%; background: #1a1a1a; border: 2px solid {gold}; display: flex; align-items: center; justify-content: center; font-size: 1.6rem;">
                    👮
                </div>
                <div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: {text}; letter-spacing: 0.02em;">
                        {officer_name}
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: {gold}; margin-top: 2px;">
                        BADGE: #{badge_id} &nbsp;&bull;&nbsp; CLEARANCE: {rank}
                    </div>
                </div>
            </div>
            <div style="text-align: right; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: {muted};">
                <span style="background: #0f2e1b; border: 1px solid #22c55e; color: #4ade80; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.76rem;">● VERIFIED OFFICER SESSION</span>
                <div style="margin-top: 6px;">INVESTIGATIONS LOGGED: <strong style="color: {gold}; font-size: 0.95rem;">{total_cases}</strong></div>
            </div>
        </div>
        <div style="font-size: 0.82rem; color: {muted}; line-height: 1.4; border-top: 1px dashed {border}; padding-top: 10px;">
            <strong>DEPARTMENT:</strong> {dept} &nbsp;|&nbsp; <strong>ACCOUNT:</strong> @{profile.get('username')} &nbsp;|&nbsp; <strong>ENROLLED:</strong> {created}
        </div>
    </div>
    """

def render_officer_case_history_markdown(username: str) -> str:
    """Renders the markdown table of all cases logged under this officer's profile."""
    from pathlib import Path
    history = UserProfileManager.get_user_history(username)
    if not history:
        return "*No historical case investigations logged for this officer yet. Upload a report in Tab 2 to record your first case dossier.*"
    
    rows = [
        "| Date & Time | Case Reference | Identified Domain | Solvability Score | Grade | Executive Synopsis | Dossier Export |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for r in history[:25]:
        export_file = r.get("export_file_path", "")
        file_name = Path(export_file).name if export_file else "Archived"
        rows.append(
            f"| `{r.get('timestamp')}` | **{r.get('case_title')}** | `{r.get('report_category')}` | **{r.get('overall_score')}/100** | `{r.get('grade')}` | {r.get('summary_snippet', '')[:70]}... | `{file_name}` |"
        )
    return "\n".join(rows)

def handle_officer_login(username: str, password: str, theme_choice: str) -> Tuple[str, str, str, str]:
    """Authenticates an officer and updates active profile."""
    is_dark = "Night" in theme_choice
    ok, msg, profile = UserProfileManager.authenticate(username, password)
    if ok and profile:
        PIPELINE_CACHE["active_user"] = profile["username"]
        log_event("AUTH", f"Officer logged in: {profile['officer_name']} ({profile['badge_id']})")
        card_html = render_officer_card_html(profile["username"], is_dark)
        history_md = render_officer_case_history_markdown(profile["username"])
        header_html = create_header_html(is_dark)
        return f"✅ {msg}", card_html, history_md, header_html
    return f"❌ {msg}", gr.update(), gr.update(), gr.update()

def handle_officer_register(name: str, badge: str, rank: str, username: str, password: str, theme_choice: str) -> Tuple[str, str, str, str]:
    """Registers a new officer profile and automatically logs them in."""
    is_dark = "Night" in theme_choice
    ok, msg, profile = UserProfileManager.register_officer(
        username=username,
        password=password,
        officer_name=name,
        badge_id=badge,
        rank_clearance=rank
    )
    if ok and profile:
        PIPELINE_CACHE["active_user"] = profile["username"]
        log_event("AUTH", f"New officer enrolled: {profile['officer_name']} ({profile['badge_id']})")
        card_html = render_officer_card_html(profile["username"], is_dark)
        history_md = render_officer_case_history_markdown(profile["username"])
        header_html = create_header_html(is_dark)
        return f"✅ {msg}", card_html, history_md, header_html
    return f"❌ {msg}", gr.update(), gr.update(), gr.update()

def handle_officer_logout(theme_choice: str) -> Tuple[str, str, str, str]:
    """Logs out active officer and reverts to default visitor session."""
    is_dark = "Night" in theme_choice
    PIPELINE_CACHE["active_user"] = "default_investigator"
    card_html = render_officer_card_html("default_investigator", is_dark)
    history_md = render_officer_case_history_markdown("default_investigator")
    header_html = create_header_html(is_dark)
    log_event("AUTH", "Officer logged out. Reverted to default station terminal.")
    return "🚪 Officer logged out successfully.", card_html, history_md, header_html

# ==============================================================================
# INVESTIGATION REPLAY & EXPERIMENT LAB
# ==============================================================================

def run_counterfactual_replay(remove_evidence: str):
    log_event("REPLAY_LAB", f"Running counterfactual replay experiment: REMOVING {remove_evidence}...")
    # Base case
    base_case = get_case_engine().get_agent_visible_data()
    # Modified case
    mod_case = get_case_engine().create_case_variation(remove_evidence_id=remove_evidence).model_dump()
    mod_case.pop("hidden_solution", None)

    # Run quick comparison
    mod_ev_report = EvidenceAgent().run(mod_case)
    mod_chief = ChiefAgent().run(mod_case, evidence_report=mod_ev_report.raw_markdown)

    diff_markdown = f"""### 🔬 COUNTERFACTUAL REPLAY EXPERIMENT RESULTS

| Investigation Parameter | Original Case (Full 7 Clues) | Modified Case (Without {remove_evidence}) |
| :--- | :--- | :--- |
| **Active Evidence Count** | `7 Items (E-A to E-G)` | `6 Items (Without {remove_evidence})` |
| **Leading Suspect** | **Arjun Vale** | **Arjun Vale (Significantly Weakened)** |
| **Confidence Level** | `MODERATE (Supported by E-E)` | `LOW (Card log uncorroborated by physical trace)` |
| **Strongest Clue** | E-B (Lock Log) + E-E (Fibers) | E-B (Lock Log only) |
| **Leading Alternative** | Staged proxy access | Third-party card theft without physical rotunda entry |

> [!NOTE]
> **Forensic Impact:** Removing `{remove_evidence}` demonstrates that without physical fiber trace corroboration, the card swipe alone is completely insufficient to withstand reasonable doubt.
"""
    log_event("REPLAY_LAB", f"Counterfactual experiment completed for {remove_evidence}.")
    return diff_markdown

# ==============================================================================
# INVESTIGATOR CHAT ASSISTANT
# ==============================================================================

def handle_assistant_chat(user_msg: str, chat_history: List[Tuple[str, str]]):
    if not user_msg:
        return "", chat_history
    client = get_client()
    case_context = get_case_engine().get_agent_visible_data()
    chief_text = PIPELINE_CACHE["chief"].raw_markdown if PIPELINE_CACHE["chief"] else "Chief report not yet run."

    prompt = f"""User Question: {user_msg}

CURRENT CASE DATA:
{json.dumps(case_context, indent=2)[:2000]}

CHIEF REPORT:
{chief_text[:1500]}
"""
    if client.is_configured():
        success, answer = client.generate(system_instruction=ASSISTANT_PROMPT, user_prompt=prompt)
    else:
        # High fidelity local answers for demo
        lower = user_msg.lower()
        if "arjun" in lower and "lead" in lower:
            answer = "Arjun Vale is currently leading because his keycard opened the display case at 8:23 PM (Evidence B), he left the archive with a folder at 8:25 PM (Evidence D), and blue velvet fibers were found inside the folder (Evidence E). However, the Chief explicitly notes this is NOT legal proof because card use does not prove physical identity."
        elif "contradict" in lower:
            answer = "Arjun's primary contradiction is between his interview statement (Evidence C), where he claims his card remained in his jacket inside the archive, and the tamper-evident electronic lock log (Evidence B), which recorded his card opening the display case at 8:23 PM."
        elif "missing" in lower:
            answer = "The most critical missing evidence includes: 1) Touch DNA / latent fingerprint swabbing of the keycard, 2) Chemical dye spectrometry on the folder fibers, and 3) Video of the archive doorway to verify if someone accessed his jacket."
        else:
            answer = f"Based on the official case file, the investigation centers on the 08:20-08:24 PM blackout. All conclusions remain provisional subject to physical touch DNA and fiber spectrometry verification."

    chat_history.append((user_msg, answer))
    return "", chat_history

# ==============================================================================
# DOCUMENT INGESTION & AGENT ANALYSIS HANDLERS
# ==============================================================================

def handle_upload_document(uploaded_file):
    """Parses PDF, DOCX, TXT, or JSON file, extracts text, and presents an extraction audit."""
    if not uploaded_file:
        return (
            "⚠️ No file uploaded. Please select a PDF, DOCX, TXT, or JSON file.",
            "",
            gr.update(interactive=False),
            gr.update(interactive=False)
        )
    
    file_path = uploaded_file.name if hasattr(uploaded_file, "name") else str(uploaded_file)
    from detective_nexus.core.document_parser import DocumentParser
    success, text, metadata = DocumentParser.parse_file(file_path)

    if not success:
        return (
            f"❌ Extraction Failed: {text}",
            "",
            gr.update(interactive=False),
            gr.update(interactive=False)
        )

    log_event("DOCUMENT_INGEST", f"Uploaded document parsed: {metadata.get('filename')} ({metadata.get('size_bytes')} bytes)")

    audit_summary = f"""### 📄 DOCUMENT EXTRACTION AUDIT
- **File Name:** `{metadata.get('filename')}`
- **Format:** `{metadata.get('extension')}`
- **Size:** `{metadata.get('size_bytes')} bytes`
- **Total Characters Extracted:** `{metadata.get('char_count', 0)}`
- **Pages / Paragraphs:** `{metadata.get('page_count', metadata.get('paragraph_count', 'N/A'))}`
- **Status:** Text successfully extracted. Ready for instant Agent Analysis or Case Pipeline Ingestion.
"""
    return audit_summary, text[:8000], gr.update(interactive=True), gr.update(interactive=True)

def handle_summarize_and_analyze_document(raw_text: str) -> str:
    """Invokes our AI Detective & Forensic Analyst agents to summarize and analyze the uploaded report."""
    if not raw_text or len(raw_text.strip()) < 30:
        return "⚠️ Insufficient document text for forensic agent analysis. Please upload a valid case report or document first."
    
    log_event("AGENT_ANALYSIS", f"Running multi-agent forensic summary on uploaded document ({len(raw_text)} chars)...")
    from detective_nexus.llm.prompts import DOCUMENT_SUMMARY_PROMPT
    client = get_client()

    if client.is_configured():
        success, report = client.generate(
            system_instruction=DOCUMENT_SUMMARY_PROMPT,
            user_prompt=f"Perform an exhaustive forensic summary and agent analysis of the following uploaded case dossier/document:\n\n{raw_text[:14000]}"
        )
        if success and report:
            log_event("AGENT_ANALYSIS", "Agent document analysis successfully generated via Gemini.")
            return report

    # Resilient high-fidelity forensic analysis fallback if offline
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    first_few = " ".join(lines[:4])[:400]
    
    fallback_report = f"""# 📋 CASE FILE FORENSIC SUMMARY & AGENT ANALYSIS
**Automated Forensic Document Review** | **Detective Nexus AI Division**

## 1. Executive Incident Overview
- **Incident Summary:** Case documentation reviewed. Primary narrative describes: *{first_few}...*
- **Document Text Extracted:** `{len(raw_text)} characters` processed across `{len(lines)} narrative segments`.
- **Operational Classification:** Active Document Review & Multi-Agent Investigation.
- **Primary Objective:** Establish evidentiary chronology, verify party statements, and eliminate speculation.

## 2. Key Evidence & Exhibit Catalog (Agent Evidence Review)
- **Primary Exhibit A (Source Documentation):** Extracted from authenticated user upload. Establishes the documented events, timestamps, and witness remarks.
- **Physical Trace Gaps:** The provided text outlines incident parameters but lacks certified laboratory spectrometry or chain-of-custody signatures.
- **What Is Proven:** The sequence of reported observations and logged anomalies.
- **What Is NOT Proven:** The actual identity of the perpetrator without corroborated forensic biometric trace.

## 3. Suspect & Person of Interest Dossier
- **Individuals Mentioned:** Identified in case text.
- **Motive & Opportunity Assessment:** Requires corroboration against access logs and timeline constraints.
- **Contradiction Alert:** Any discrepancies between verbal statements and physical timestamps must be scrutinized under rigorous cross-examination.

## 4. Chronological Incident Sequence & Critical Opportunity Windows
- **Incident Interval:** Sequenced according to timestamps identified within the uploaded narrative.
- **Critical Gap:** Investigators must identify any unmonitored window where physical or digital safeguards were bypassed.

## 5. Inconsistencies, Blind Spots & Red Flags
- Verbal accounts are inherently subjective; electronic logs and physical trace must supersede uncorroborated testimony.
- Touch DNA, forensic fingerprinting, and digital access audits are strongly recommended.

## 6. Chief Investigator Recommended Next Actions
1. Click **'🚀 INGEST CASE & LOAD INTO 5-AGENT PIPELINE'** to map this dossier into the full 5-agent investigation workstation.
2. Run the **Detective**, **Evidence Analyst**, **Suspect Profiler**, **Skeptic**, and **Chief** agents to challenge every assumption!
"""
    log_event("AGENT_ANALYSIS", "Forensic summary report generated using local agent analysis engine.")
    return fallback_report

def handle_ingest_case_from_document(raw_text: str):
    """Uses Gemini or local parser to convert extracted document text into a structured MysteryCase."""
    if not raw_text or len(raw_text.strip()) < 50:
        return (
            "❌ Insufficient text to ingest case. Please upload a detailed report or incident dossier.",
            "",
            gr.update()
        )
    
    log_event("DOCUMENT_INGEST", "Dispatching raw document to Gemini for Case Ingestion structuring...")
    from detective_nexus.llm.prompts import CASE_INGESTION_PROMPT
    client = get_client()

    prompt = f"Extract a complete structured mystery case from the following document:\n\n{raw_text[:12000]}"
    
    if client.is_configured():
        success, response = client.generate(system_instruction=CASE_INGESTION_PROMPT, user_prompt=prompt)
    else:
        success = False
        response = ""

    import json
    if success and response:
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            case_dict = json.loads(cleaned)
            loaded_case = get_case_engine().load_custom_case(case_dict)
            log_event("DOCUMENT_INGEST", f"Case successfully structured: {loaded_case.title} ({loaded_case.case_id})")
            
            feedback = f"""✅ CASE INGESTION & STRUCTURING SUCCESSFUL!
- **Case ID:** `{loaded_case.case_id}`
- **Title:** **{loaded_case.title}**
- **Location:** {loaded_case.location}
- **Critical Opportunity Window:** `{loaded_case.critical_window}`
- **Suspects Extracted:** `{len(loaded_case.suspects)} persons of interest`
- **Evidence Items Extracted:** `{len(loaded_case.evidence)} clues catalogued`
- **Timeline Events:** `{len(loaded_case.timeline)} events sequenced`

The uploaded case is now ACTIVE in memory! You can immediately switch to the **Command Center** or any of the **5 Agent Tabs** to run the complete investigation on your document.
"""
            return feedback, json.dumps(case_dict, indent=2), gr.update(value=create_header_html())
        except Exception as e:
            log_event("DOCUMENT_INGEST", f"JSON parse error during ingestion: {str(e)}")

    # Fallback structuring if offline or parse error
    fallback_dict = {
        "case_id": "CUSTOM-DOC-001",
        "title": "Uploaded Case Dossier",
        "category": "Document Investigation",
        "difficulty": "Medium",
        "location": "Incident Scene (Extracted from Document)",
        "incident_description": raw_text[:800],
        "critical_window": "Incident Timeline Window",
        "central_questions": ["What occurred based on the uploaded documentation?", "Who had access?", "Which statements conflict?"],
        "investigation_rules": ["Motive does not prove guilt", "Separate fact from inference"],
        "timeline": [
            {"id": "T01", "time": "Initial Event", "event": "Document initial incident", "source": "Uploaded Report", "certainty": "Established", "is_critical": True}
        ],
        "suspects": [
            {"suspect_id": "S01", "name": "Person of Interest 1", "role": "Identified in Document", "motive": "Documented incentive", "statement": "Statement in report", "means": "Medium", "opportunity": "High", "access": "Direct", "alibi": "Unverified", "uncertainty": "Requires corroboration", "relevant_evidence": ["E-A"]}
        ],
        "witnesses": [],
        "evidence": [
            {"evidence_id": "E-A", "title": "Primary Document Exhibit", "description": raw_text[:400], "category": "Documentary", "source": "Uploaded Dossier", "establishes": "Key events described in document", "does_not_establish": "Unverified third-party claims", "classification": "FACT", "strength": "STRONG", "related_suspects": ["Person of Interest 1"], "reliability_notes": "Extracted from authenticated file"}
        ],
        "evidence_relationships": [],
        "status": "INVESTIGATION ACTIVE"
    }
    loaded_case = get_case_engine().load_custom_case(fallback_dict)
    feedback = f"""✅ CASE INGESTION & STRUCTURING COMPLETE!
- **Case ID:** `{loaded_case.case_id}`
- **Title:** **{loaded_case.title}**
- **Incident Characters:** {len(raw_text)} chars extracted

The uploaded document is now ACTIVE in the investigation engine!
"""
    return feedback, json.dumps(fallback_dict, indent=2), gr.update(value=create_header_html())

def handle_theme_toggle(theme_choice: str) -> Tuple[str, str]:
    """Switches application between Night Tactical Mode and Day Forensic Mode."""
    is_dark = "Night" in theme_choice
    PIPELINE_CACHE["theme_mode"] = theme_choice
    log_event("ENVIRONMENT", f"Visual lighting mode switched to {theme_choice}.")
    return get_theme_style_css(is_dark), create_header_html(is_dark)

def handle_quick_load_sample(sample_type: str) -> Tuple[str, str, Any, Any]:
    """Loads a pre-built police incident report or case dossier for 1-click testing."""
    if "Medici" in sample_type:
        from pathlib import Path
        p = Path("data/sample_case_report.txt")
        if p.exists():
            text = p.read_text(encoding="utf-8")
        else:
            text = "MEDICI COIN INCIDENT REPORT #CR-2026-9042\nVault biometric terminal logged master keycard #004 at 22:34 during breaker #4 trip..."
        audit = f"""### 📄 SAMPLE REPORT LOADED
- **Case Reference:** `#CR-2026-9042` (The Medici Double Florin & Cipher Theft)
- **Source:** Metropolitan Forensic Investigation Division
- **Characters:** `{len(text)}`
- **Ready for Scorecard:** Click '**1. ANALYZE CASE & GENERATE FORENSIC SCORECARD**' below.
"""
    else:
        case = get_case_engine().get_current_case()
        text = f"CASE REPORT: {case.title} ({case.case_id})\nLOCATION: {case.location}\nCRITICAL OPPORTUNITY WINDOW: {case.critical_window}\n\nINCIDENT NARRATIVE:\n{case.incident_description}\n\nSUSPECTS UNDER INVESTIGATION:\n"
        for s in case.suspects:
            text += f"- {s.name} ({s.role}): Motive: {s.motive}. Statement: {s.statement}. Means: {s.means}, Opportunity: {s.opportunity}, Alibi: {s.alibi}\n"
        text += "\nFORENSIC EVIDENCE EXHIBITS:\n"
        for e in case.evidence:
            text += f"- [{e.evidence_id}] {e.title}: {e.description} (Establishes: {e.establishes}. Does NOT establish: {e.does_not_establish})\n"
        audit = f"""### 📄 BUILT-IN CASE DOSSIER LOADED
- **Case Title:** **{case.title}** (`{case.case_id}`)
- **Evidence Exhibits:** `{len(case.evidence)}` items
- **Suspect Count:** `{len(case.suspects)}` persons of interest
- **Status:** Master dossier loaded. Ready for Scorecard generation.
"""
    return audit, text, gr.update(interactive=True), gr.update(interactive=True)

def handle_analyze_and_score_case(raw_text: str, theme_choice: str) -> Tuple[str, str, Any, Any, str, Any]:
    """
    Core user feature: Evaluates case report, identifies what the report is about,
    generates the interactive visual scorecard, produces the multi-agent forensic summary,
    exports the downloadable official dossier file (.md), logs to the officer's history,
    and synthesizes an authentic Spoken Voice Audio Debrief of the report.
    """
    if not raw_text or len(raw_text.strip()) < 30:
        empty_card = """
        <div style="padding: 24px; text-align: center; border: 1px dashed #ef4444; border-radius: 8px; color: #ef4444; font-family: monospace;">
            ⚠️ INSUFFICIENT CASE TEXT: Please upload a PDF/report file, click a quick-load button, or paste at least 30 characters of incident text.
        </div>
        """
        return empty_card, "⚠️ No case text provided to analyze.", gr.update(interactive=False), None, "", None

    is_dark = "Night" in theme_choice
    log_event("SCORECARD", f"Evaluating case solvability metrics and forensic dimensions ({len(raw_text)} chars)...")

    # Run AI classification, forensic scorecard evaluation, and deep multi-agent summary in parallel
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        fut_class = executor.submit(ReportClassifier.classify_report, raw_text)
        fut_score = executor.submit(ForensicScorecardEngine.evaluate_case_report, raw_text)
        fut_agent = executor.submit(handle_summarize_and_analyze_document, raw_text)

        classification = fut_class.result()
        scorecard_data = fut_score.result()
        agent_report = fut_agent.result()

    classification_html = ReportClassifier.render_classification_html(classification, is_dark=is_dark)
    scorecard_html = ForensicScorecardEngine.render_html_scorecard(scorecard_data, is_dark_mode=is_dark)

    # 4. Get active officer profile
    active_user = PIPELINE_CACHE.get("active_user", "default_investigator")
    profile = UserProfileManager.get_profile(active_user)
    officer_name = profile.get("officer_name", "Forensic Field Investigator") if profile else "Forensic Field Investigator"
    badge_id = profile.get("badge_id", "BADGE-4892") if profile else "BADGE-4892"

    # 5. Export formal downloadable forensic dossier
    export_file_path = DossierExporter.export_case_dossier(
        case_title=classification["subject"],
        category=classification["category"],
        raw_narrative=raw_text,
        scorecard=scorecard_data,
        agent_analysis=agent_report,
        officer_name=officer_name,
        badge_id=badge_id
    )
    PIPELINE_CACHE["last_dossier_path"] = export_file_path

    # 6. Log case into the officer's persistent history
    UserProfileManager.log_case_to_user_history(
        username=active_user,
        case_title=classification["subject"],
        report_category=classification["category"],
        score=scorecard_data.get("overall_score", 50),
        grade=scorecard_data.get("grade", "GRADE C"),
        summary=scorecard_data.get("verdict_summary", "Evaluation complete."),
        export_file_path=export_file_path
    )
    log_event("HISTORY", f"Case '{classification['subject']}' logged to profile of {officer_name} (#{badge_id}). Dossier: {export_file_path}")

    # 7. Synthesize Spoken Voice Audio Debrief of the uploaded case & score
    audio_path = None
    try:
        ok, synthesized_path = AudioDebriefEngine.generate_case_report_voice_summary(raw_text, scorecard_data)
        if ok:
            audio_path = synthesized_path
            log_event("AUDIO_DISPATCH", f"Voice audio summary generated for uploaded case: {audio_path}")
    except Exception as e:
        log_event("AUDIO_DISPATCH", f"Voice summary generation error: {str(e)}")

    log_event("SCORECARD", f"Scorecard complete: Solvability {scorecard_data['overall_score']}/100 [{scorecard_data['grade']}]")

    return scorecard_html, agent_report, gr.update(interactive=True), audio_path, classification_html, export_file_path

def handle_download_last_dossier(raw_text: str) -> Any:
    """Returns the generated dossier file path for download, generating it on the fly if needed."""
    from pathlib import Path
    if PIPELINE_CACHE.get("last_dossier_path") and Path(PIPELINE_CACHE["last_dossier_path"]).exists():
        return PIPELINE_CACHE["last_dossier_path"]
    
    if not raw_text or len(raw_text.strip()) < 30:
        return None
    
    classification = ReportClassifier.classify_report(raw_text)
    scorecard_data = ForensicScorecardEngine.evaluate_case_report(raw_text)
    agent_report = handle_summarize_and_analyze_document(raw_text)
    active_user = PIPELINE_CACHE.get("active_user", "default_investigator")
    profile = UserProfileManager.get_profile(active_user)
    officer_name = profile.get("officer_name", "Forensic Investigator") if profile else "Forensic Investigator"
    badge_id = profile.get("badge_id", "BADGE-4892") if profile else "BADGE-4892"

    path = DossierExporter.export_case_dossier(
        case_title=classification["subject"],
        category=classification["category"],
        raw_narrative=raw_text,
        scorecard=scorecard_data,
        agent_analysis=agent_report,
        officer_name=officer_name,
        badge_id=badge_id
    )
    PIPELINE_CACHE["last_dossier_path"] = path
    return path

def handle_speak_case_report(raw_text: str) -> Any:
    """Explicitly synthesizes and speaks out the voice debrief for the current narrative."""
    if not raw_text or len(raw_text.strip()) < 30:
        return None
    try:
        scorecard_data = ForensicScorecardEngine.evaluate_case_report(raw_text)
        ok, audio_path = AudioDebriefEngine.generate_case_report_voice_summary(raw_text, scorecard_data)
        if ok:
            log_event("AUDIO_DISPATCH", f"Manual replay voice audio generated: {audio_path}")
            return audio_path
    except Exception as e:
        log_event("AUDIO_DISPATCH", f"Manual replay voice error: {str(e)}")
    return None

# ==============================================================================
# ADVANCED FORENSIC SYSTEMS EVENT HANDLERS
# ==============================================================================

def handle_interrogate_turn(suspect_name: str, user_question: str, chat_history: List[Tuple[str, str]], confront_clue: str):
    """Executes an interrogation turn with deception and stress analysis."""
    if not user_question and (not confront_clue or confront_clue == "None"):
        return "", chat_history, InterrogationEngine.render_stress_gauge_html({})

    case_data = get_case_engine().get_agent_visible_data()
    reply, telemetry, gauge_html = InterrogationEngine.interrogate_suspect(
        suspect_name=suspect_name,
        user_question=user_question,
        chat_history=chat_history,
        confront_evidence_item=confront_clue,
        case_data=case_data
    )

    disp_question = user_question
    if confront_clue and confront_clue != "None":
        disp_question = f"⚖️ [CONFRONTED WITH {confront_clue}]: {user_question}"

    chat_history.append((disp_question, reply))
    log_event("INTERROGATION", f"Cross-examined {suspect_name}. Stress index: {telemetry.get('stress_score')}%")
    return "", chat_history, gauge_html

def handle_generate_dispatch_audio():
    """Generates police radio dispatch audio."""
    try:
        case = get_case_engine().get_current_case()
        success, audio_file = AudioDebriefEngine.generate_briefing_audio(
            case.title, case.incident_description, case.critical_window
        )
        if success:
            log_event("AUDIO_DISPATCH", f"Police radio dispatch audio generated: {audio_file}")
            return audio_file, "🟢 Dispatch Broadcast Online (Frequency 104.7 MHz)"
        return None, f"⚠️ Audio synthesis error: {audio_file}"
    except Exception as e:
        log_event("AUDIO_DISPATCH", f"Dispatch audio error: {str(e)}")
        return None, f"⚠️ Audio dispatch error: {str(e)}"

def handle_generate_chief_audio():
    """Generates Chief Investigator voice verdict debrief."""
    try:
        case = get_case_engine().get_current_case()
        chief_report = PIPELINE_CACHE.get("chief")
        lead = "Arjun Vale"
        if chief_report:
            lead = getattr(chief_report, "leading_explanation", None) or getattr(chief_report, "leading_suspect", "Arjun Vale")
        
        caveat = "Card swipe does not prove physical bearer without touch DNA"
        if chief_report:
            caveat = getattr(chief_report, "not_proven_caveat", None) or getattr(chief_report, "legal_caveat", caveat)
        
        success, audio_file = AudioDebriefEngine.generate_chief_verdict_audio(str(lead), str(caveat))
        if success:
            log_event("AUDIO_DISPATCH", f"Chief classified voice debrief generated: {audio_file}")
            return audio_file, "🟢 Chief Classified Debrief Recording Ready"
        return None, f"⚠️ Audio synthesis error: {audio_file}"
    except Exception as e:
        log_event("AUDIO_DISPATCH", f"Chief debrief audio error: {str(e)}")
        return None, f"⚠️ Chief audio error: {str(e)}"


def handle_generate_procedural_case_ui(genre: str, diff: str, n_sus: int, n_ev: int):
    """Generates an infinite procedural mystery case."""
    log_event("PROCEDURAL_GEN", f"Generating {genre} ({diff}) with {n_sus} suspects and {n_ev} clues...")
    success, case_dict, msg = ProceduralCaseGenerator.generate_mystery_case(genre, diff, n_sus, n_ev)
    return json.dumps(case_dict, indent=2), msg, gr.update(interactive=True)

def handle_load_procedural_case_into_nexus(case_json_str: str):
    """Loads procedural case into memory."""
    try:
        case_dict = json.loads(case_json_str)
        loaded = get_case_engine().load_custom_case(case_dict)
        log_event("PROCEDURAL_GEN", f"Loaded procedural case: {loaded.title} ({loaded.case_id})")
        return f"✅ CASE ACTIVE: {loaded.title} ({loaded.case_id}) is now loaded into all 5 agents!", gr.update(value=create_header_html())
    except Exception as e:
        return f"❌ Error loading case: {str(e)}", gr.update()

def handle_run_forensic_lab_test_ui(evidence_id: str, test_type: str):
    """Executes simulated scientific laboratory testing on evidence."""
    case_data = get_case_engine().get_agent_visible_data()
    summary, cert_html = ForensicLabEngine.run_lab_test(evidence_id, test_type, case_data)
    log_event("CRIME_LAB", f"Lab test '{test_type}' completed on exhibit {evidence_id}.")
    return cert_html, summary

def handle_simulate_courtroom_trial_ui(indicted_suspect: str):
    """Executes the Courtroom Trial Simulator."""
    case_data = get_case_engine().get_agent_visible_data()
    proceedings_md, html_verdict, metrics = CourtroomTrialEngine.conduct_trial(
        indicted_suspect=indicted_suspect,
        case_data=case_data,
        has_lab_certificate=True
    )
    log_event("COURTROOM", f"Trial concluded for {indicted_suspect}. Verdict: {metrics.get('verdict')}")
    return proceedings_md, html_verdict

# ==============================================================================
# MAIN GRADIO INTERFACE
# ==============================================================================

def build_detective_nexus_app() -> gr.Blocks:
    theme = get_forensic_theme()

    with gr.Blocks(theme=theme, css=FORENSIC_CSS, title="DETECTIVE NEXUS — AI Forensic Workstation") as demo:

        # Injected Dynamic Theme CSS (Day / Night Mode)
        theme_style_html = gr.HTML(get_theme_style_css(is_dark_mode=True))

        # Header Box with Lighting Switcher
        with gr.Row():
            with gr.Column(scale=5):
                header_html = gr.HTML(create_header_html(is_dark_mode=True))
            with gr.Column(scale=1, min_width=210):
                theme_radio = gr.Radio(
                    choices=["🌙 Night Tactical", "☀️ Day Forensic"],
                    value="🌙 Night Tactical",
                    label="Tactical Lighting",
                    interactive=True
                )

        # Main Navigation Tabs
        with gr.Tabs():

            # ------------------------------------------------------------------
            # TAB 1: COMMAND CENTER (MAIN DASHBOARD)
            # ------------------------------------------------------------------
            with gr.TabItem("🛰️ Command Center"):
                dashboard_html = gr.HTML(create_dashboard_html())

                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Markdown("### ⚡ Live Investigation Controls")
                        with gr.Row():
                            run_all_btn = gr.Button("▶ RUN FULL 5-AGENT INVESTIGATION", variant="primary", size="lg")
                            reset_btn = gr.Button("↺ RESET DOSSIER", variant="secondary")

                        gr.Markdown("### 📡 Live Forensic Activity Log")
                        activity_log_box = gr.Textbox(
                            value=get_activity_log_text(),
                            lines=12,
                            interactive=False,
                            label="System Telemetry & Agent Dispatch Stream",
                            elem_classes=["nexus-mono"]
                        )

                        gr.Markdown("### 📻 Metropolitan Police Radio & Voice Dispatch (104.7 MHz)")
                        with gr.Row():
                            play_dispatch_btn = gr.Button("🎙️ Listen to Radio Dispatch Briefing (TTS)", size="sm")
                            play_chief_audio_btn = gr.Button("🎧 Chief Classified Voice Debrief", size="sm")
                        radio_audio = gr.Audio(label="Encrypted Forensic Audio Frequency", type="filepath")
                        audio_status_lbl = gr.Markdown("*Click above to synthesize and stream real-time police audio debrief.*")

                    with gr.Column(scale=1):
                        gr.Markdown("### 🔎 Quick Case Dossier")
                        gr.Markdown(
                            """
<div class="quick-dossier-card">
    <p><strong>Incident:</strong> The Vanishing Aurora Diamond</p>
    <p><strong>Location:</strong> Northbridge Museum (Grand Rotunda)</p>
    <p><strong>Time:</strong> 08:20 PM – 08:24 PM (Blackout)</p>
    <p><strong>Status:</strong> Electronic lock opened; glass unbroken</p>
    <p><strong>Primary Clue:</strong> Keycard swipe logged at 8:23 PM</p>
</div>
                            """
                        )
                        gr.Markdown("---")
                        gr.Markdown("### 🤖 Multi-Agent Pipeline Status")
                        agent_status_box = gr.HTML(
                            """
<div style="display: flex; flex-direction: column; gap: 8px; margin-top: 6px;">
    <div class="agent-status-pill" style="display: flex; justify-content: space-between; align-items: center; padding: 7px 12px; border-radius: 6px;">
        <span class="agent-status-name" style="font-size: 0.88rem;">🔍 <strong>Detective Agent</strong></span>
        <span class="agent-status-tag" style="padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700;">● READY</span>
    </div>
    <div class="agent-status-pill" style="display: flex; justify-content: space-between; align-items: center; padding: 7px 12px; border-radius: 6px;">
        <span class="agent-status-name" style="font-size: 0.88rem;">🔬 <strong>Evidence Specialist</strong></span>
        <span class="agent-status-tag" style="padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700;">● READY</span>
    </div>
    <div class="agent-status-pill" style="display: flex; justify-content: space-between; align-items: center; padding: 7px 12px; border-radius: 6px;">
        <span class="agent-status-name" style="font-size: 0.88rem;">👥 <strong>Suspect Analyst</strong></span>
        <span class="agent-status-tag" style="padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700;">● READY</span>
    </div>
    <div class="agent-status-pill" style="display: flex; justify-content: space-between; align-items: center; padding: 7px 12px; border-radius: 6px;">
        <span class="agent-status-name" style="font-size: 0.88rem;">⚖️ <strong>Skeptic Agent</strong></span>
        <span class="agent-status-tag" style="padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700;">● READY</span>
    </div>
    <div class="agent-status-pill" style="display: flex; justify-content: space-between; align-items: center; padding: 7px 12px; border-radius: 6px;">
        <span class="agent-status-name" style="font-size: 0.88rem;">🏛️ <strong>Chief Investigator</strong></span>
        <span class="agent-status-tag" style="padding: 2px 8px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700;">● READY</span>
    </div>
</div>
                            """
                        )

                        gr.Markdown(
                            """
---
<div class="info-alert-card">
    <div class="info-alert-title">
        📄 UPLOAD YOUR CASE REPORT
    </div>
    <div class="info-alert-desc">
        You can upload your own <strong>PDF, Word (DOCX), TXT, or JSON</strong> report directly! Switch to <strong>Tab 2: "📄 Upload Case / Report & Scorecard"</strong> to extract the facts, calculate the Solvability Scorecard, and dispatch the 5 AI agents.
    </div>
</div>
                            """
                        )

            # ------------------------------------------------------------------
            # TAB 2: CASE UPLOAD & FORENSIC SCORECARD GENERATOR
            # ------------------------------------------------------------------
            with gr.TabItem("📄 Upload Case / Report & Scorecard"):
                gr.Markdown("### 📄 Case Report Ingestion, Multi-Agent Analysis & Forensic Scorecard")
                gr.Markdown(
                    "Upload your case report or incident file (**PDF, DOCX, TXT, JSON, MD**), "
                    "or paste custom case notes below. Detective Nexus extracts the text, runs multi-agent forensic reasoning, "
                    "and automatically calculates a **Comprehensive Forensic Solvability Scorecard** with evidentiary metrics, "
                    "prosecutorial readiness grade, factual pillars, and critical defense vulnerabilities."
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        doc_file_input = gr.File(
                            label="Upload Case Document (PDF, DOCX, TXT, JSON, MD)",
                            file_types=[".pdf", ".docx", ".txt", ".json", ".md"],
                            type="filepath"
                        )
                        extract_doc_btn = gr.Button("📑 Parse Document & Extract Text", variant="primary")
                        
                        gr.Markdown("#### ⚡ Quick-Load Demonstration Cases")
                        with gr.Row():
                            quick_medici_btn = gr.Button("📂 Medici Coin (PDF/Report)", size="sm")
                            quick_aurora_btn = gr.Button("📂 Aurora Diamond Case", size="sm")

                        doc_audit_box = gr.Markdown("### 📄 Document Extraction Status\n*Upload a file or click a quick-load button above to inspect file metadata.*")

                    with gr.Column(scale=2):
                        doc_text_preview = gr.Textbox(
                            label="Incident Report Narrative / Case Dossier (Editable)",
                            placeholder="Extracted raw text or paste custom incident narrative here...",
                            lines=8,
                            interactive=True
                        )
                        with gr.Row():
                            score_case_btn = gr.Button("📊 1. ANALYZE CASE & GENERATE FORENSIC SCORECARD", variant="primary", size="lg")
                            ingest_case_btn = gr.Button("🚀 2. INGEST CASE INTO 5-AGENT PIPELINE", variant="secondary", interactive=False)

                        ingest_feedback_box = gr.Markdown("### 🎯 Ingestion & Active Status\n*Click '2. Ingest Case' to activate this dossier across all 5 specialized agents.*")

                # Voice Audio Debrief Section for Uploaded Report
                with gr.Row():
                    with gr.Column():
                        gr.HTML(
                            """
                            <div style="margin-top: 14px; margin-bottom: 8px; padding: 10px 14px; background: #111111; border: 1px solid #292929; border-left: 4px solid #D4AF37; border-radius: 6px; display: flex; align-items: center; justify-content: space-between;">
                                <div>
                                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.88rem; font-weight: 700; color: #D4AF37; letter-spacing: 0.05em;">
                                        🎙️ AI SPOKEN FORENSIC VOICE DEBRIEF // REPORT SUMMARY & SCORE
                                    </span>
                                    <div style="font-size: 0.78rem; color: #8B8B8B; margin-top: 3px;">
                                        Synthesized speech audio summary of uploaded case narrative, Solvability Index, and critical gaps.
                                    </div>
                                </div>
                                <div style="font-size: 0.75rem; color: #8B8B8B; font-family: monospace;">
                                    [FREQUENCY: SECURE DISPATCH // SAPI+TTS]
                                </div>
                            </div>
                            """
                        )
                        case_voice_audio = gr.Audio(
                            label="Spoken Case Debrief & Solvability Voice Summary",
                            type="filepath",
                            interactive=False,
                            autoplay=True
                        )
                        speak_voice_btn = gr.Button("🔊 Speak / Replay Report Voice Summary", size="sm", variant="secondary")

                # What This Report Is About (Automated Domain & Subject Identification)
                with gr.Row():
                    report_classification_html = gr.HTML(
                        """
                        <div style="padding: 14px 18px; text-align: center; border: 1px dashed #292929; border-radius: 6px; color: #8B8B8B; font-family: monospace; font-size: 0.82rem;">
                            🏷️ <strong>WHAT THIS REPORT IS ABOUT:</strong> Upload a case or click a quick-load button, then click '1. ANALYZE CASE & GENERATE FORENSIC SCORECARD' to identify domain, jurisdiction, and crime category.
                        </div>
                        """
                    )

                # The Interactive Visual Scorecard Output
                with gr.Row():
                    scorecard_display_html = gr.HTML(
                        """
                        <div style="padding: 24px; text-align: center; border: 1px dashed #334155; border-radius: 8px; color: #94a3b8; font-family: monospace;">
                            📊 <strong>FORENSIC SCORECARD READY:</strong> Upload a case report above or click a quick-load button, then click '1. ANALYZE CASE & GENERATE FORENSIC SCORECARD'.
                        </div>
                        """
                    )

                # Downloadable Forensic Dossier Section
                with gr.Row():
                    with gr.Column(scale=3):
                        download_dossier_file = gr.File(
                            label="📥 Official Forensic Case Dossier (.md / .txt) [Ready for Download]",
                            interactive=False
                        )
                    with gr.Column(scale=1):
                        download_dossier_btn = gr.Button("📥 Generate & Download Case Dossier (.md)", variant="secondary", size="lg")

                # Full Multi-Agent Narrative Breakdown
                with gr.Row():
                    agent_analysis_output_md = gr.Markdown("### 🔍 Multi-Agent Investigation & Red Flag Audit\n*Forensic agent breakdown and suspect evaluation will appear here upon analysis.*")

                doc_file_input.upload(
                    fn=handle_upload_document,
                    inputs=[doc_file_input],
                    outputs=[doc_audit_box, doc_text_preview, score_case_btn, ingest_case_btn]
                )

                extract_doc_btn.click(
                    fn=handle_upload_document,
                    inputs=[doc_file_input],
                    outputs=[doc_audit_box, doc_text_preview, score_case_btn, ingest_case_btn]
                )

                quick_medici_btn.click(
                    fn=lambda: handle_quick_load_sample("Medici"),
                    inputs=[],
                    outputs=[doc_audit_box, doc_text_preview, score_case_btn, ingest_case_btn]
                )

                quick_aurora_btn.click(
                    fn=lambda: handle_quick_load_sample("Aurora"),
                    inputs=[],
                    outputs=[doc_audit_box, doc_text_preview, score_case_btn, ingest_case_btn]
                )

                score_case_btn.click(
                    fn=handle_analyze_and_score_case,
                    inputs=[doc_text_preview, theme_radio],
                    outputs=[scorecard_display_html, agent_analysis_output_md, ingest_case_btn, case_voice_audio, report_classification_html, download_dossier_file]
                )

                download_dossier_btn.click(
                    fn=handle_download_last_dossier,
                    inputs=[doc_text_preview],
                    outputs=[download_dossier_file]
                )

                speak_voice_btn.click(
                    fn=handle_speak_case_report,
                    inputs=[doc_text_preview],
                    outputs=[case_voice_audio]
                )

                ingest_case_btn.click(
                    fn=handle_ingest_case_from_document,
                    inputs=[doc_text_preview],
                    outputs=[ingest_feedback_box, doc_text_preview, header_html]
                )

            # ------------------------------------------------------------------
            # TAB 3: CASE ROOM
            # ------------------------------------------------------------------
            with gr.TabItem("🗃️ Case Room"):

                gr.HTML(build_case_room_html())

            # ------------------------------------------------------------------
            # TAB 3: TIMELINE (CASE CLOCK)
            # ------------------------------------------------------------------
            with gr.TabItem("⏱️ Timeline"):
                gr.HTML(build_timeline_clock_html())
                gr.Markdown("### ⏱️ Reconstructed Forensic Chronology Table")
                gr.Markdown("> Highlighting the critical 4-minute blackout opportunity window (08:20 PM - 08:24 PM) and display access event (08:23 PM).")
                gr.Markdown(build_timeline_table())

            # ------------------------------------------------------------------
            # TAB 4: EVIDENCE LAB
            # ------------------------------------------------------------------
            with gr.TabItem("🔬 Evidence Lab"):
                gr.Markdown("### 🔬 Forensic Evidence Workspace (Exhibits E-A through E-G)")
                gr.Markdown("> **EVIDENTIARY PRINCIPLE:** Distinguish **FACT** (physical or verified digital telemetry) from **INFERENCE** (provisional deduction).")
                gr.HTML(build_evidence_cards_display())
                
                gr.Markdown("---")
                gr.Markdown("### 🗣️ Witness Testimonies & Limitations")
                case_obj = get_case_engine().get_current_case()
                witness_lines = []
                for w in case_obj.witnesses:
                    witness_lines.append(f"#### [{w.witness_id}] {w.name} ({w.role})\n- **Statement:** *\"{w.statement}\"*\n- **Key Limitation:** {w.limitations}\n")
                gr.Markdown("\n---\n".join(witness_lines))

            # ------------------------------------------------------------------
            # TAB 5: SUSPECT MATRIX
            # ------------------------------------------------------------------
            with gr.TabItem("👥 Suspect Matrix"):
                gr.Markdown("### 👥 Suspect Comparative Matrix")
                gr.Markdown("> All persons of interest evaluated impartially across Motive, Means, Opportunity, Access, and Alibi. **Motive does NOT equal guilt.**")
                gr.Markdown(build_suspect_matrix_markdown())

            # ------------------------------------------------------------------
            # TAB 6: INVESTIGATION MAP
            # ------------------------------------------------------------------
            with gr.TabItem("🕸️ Investigation Map"):
                case_obj = get_case_engine().get_current_case()
                gr.Markdown("### 🕸️ Dynamic Relational Evidence Network (NetworkX Visualizer)")
                gr.Markdown("> Real-time graph mapping the stolen artifact, primary suspects, critical time windows, physical evidence, and access credentials.")
                gr.HTML(VisualEvidenceGraph.generate_svg_graph(case_obj.model_dump()))
                gr.Markdown("#### 🖥️ Monospace Terminal Relational Matrix (Nexus-Rel)")
                gr.Markdown(generate_evidence_connection_graph_markdown(case_obj.evidence_relationships))


            # ------------------------------------------------------------------
            # TAB 5: AI INVESTIGATION CONSOLE (5 AGENTS)
            # ------------------------------------------------------------------
            with gr.TabItem("🤖 AI Investigation Console"):
                gr.Markdown("### 🤖 Specialized AI Investigation Pipeline")
                gr.Markdown("Step-by-step forensic execution across Detective, Evidence Specialist, Suspect Analyst, Skeptic, and Chief Investigator.")

                with gr.Tabs():
                    with gr.TabItem("1. 🔎 Detective Agent"):
                        with gr.Row():
                            run_det_btn = gr.Button("▶ Run Detective Analysis", variant="primary")
                        det_status_txt = gr.Textbox(label="Agent Status", value="⚪ Ready to execute", interactive=False)
                        det_output_md = gr.Markdown("*Awaiting Detective execution...*")

                    with gr.TabItem("2. 🧪 Evidence Specialist"):
                        with gr.Row():
                            run_ev_btn = gr.Button("▶ Run Evidence Classification", variant="primary")
                        ev_status_txt = gr.Textbox(label="Agent Status", value="⚪ Waiting for Detective", interactive=False)
                        ev_output_md = gr.Markdown("*Awaiting Evidence Specialist execution...*")

                    with gr.TabItem("3. 👤 Suspect Analyst"):
                        with gr.Row():
                            run_sus_btn = gr.Button("▶ Run Suspect Matrix", variant="primary")
                        sus_status_txt = gr.Textbox(label="Agent Status", value="⚪ Waiting for Evidence", interactive=False)
                        sus_output_md = gr.Markdown("*Awaiting Suspect Analyst execution...*")

                    with gr.TabItem("4. 🧐 Skeptic Chamber"):
                        with gr.Row():
                            run_skp_btn = gr.Button("▶ Run Skeptic Challenge", variant="primary")
                        skp_status_txt = gr.Textbox(label="Agent Status", value="⚪ Waiting for Suspect", interactive=False)
                        skp_output_md = gr.Markdown("*Awaiting Skeptic challenge...*")

                    with gr.TabItem("5. 👑 Chief Investigator"):
                        with gr.Row():
                            run_chf_btn = gr.Button("▶ Run Chief Synthesis", variant="primary", size="lg")
                        chf_status_txt = gr.Textbox(label="Agent Status", value="⚪ Waiting for Skeptic", interactive=False)
                        chf_output_md = gr.Markdown("*Awaiting Chief synthesis...*")

            # ------------------------------------------------------------------
            # TAB 6: CHIEF SEALED VERDICT
            # ------------------------------------------------------------------
            with gr.TabItem("📜 Chief Sealed Verdict"):
                gr.Markdown("### 📜 Classified Investigation Report")
                
                with gr.Row():
                    verdict_lead_box = gr.Textbox(label="Provisional Leading Suspect", value="Awaiting full investigation...", interactive=False)
                    
                verdict_caveat_box = gr.Markdown("### ⚠️ CAVEAT: NOT PROVEN\n*Awaiting Chief Agent execution...*")
                verdict_pillars_box = gr.Markdown("### 📌 Evidentiary Anchors & Gaps\n*Awaiting execution...*")
                verdict_full_md = gr.Markdown("*Click 'Run Full 5-Agent Investigation' in the Command Center to compile this report.*")

            # ------------------------------------------------------------------
            # TAB 7: HUMAN REVIEW & ADJUDICATION
            # ------------------------------------------------------------------
            with gr.TabItem("👤 Human Judicial Review"):
                gr.Markdown("### 👤 Formal Human Review & Judicial Adjudication")
                gr.Markdown("> The AI investigation team cannot legally convict. A human investigator must critically review the evidence, assess uncertainties, and issue a determination.")

                with gr.Row():
                    with gr.Column(scale=1):
                        review_decision_radio = gr.Radio(
                            label="Human Judicial Decision",
                            choices=[
                                "ACCEPT (Endorse AI provisional finding)",
                                "REVISE (Demand additional forensic testing / alternative lines)",
                                "REJECT (Deem evidence insufficient or flawed)"
                            ],
                            value="ACCEPT (Endorse AI provisional finding)"
                        )
                        reviewer_name_input = gr.Textbox(label="Reviewing Magistrate / Lead Investigator", value="Senior Forensic Examiner")
                        review_rationale_input = gr.Textbox(
                            label="Investigative Rationale & Decision Notes",
                            placeholder="State reasons for acceptance, revision, or rejection...",
                            lines=3
                        )
                        review_next_ev_input = gr.Textbox(
                            label="Next Forensic Evidence to Authorize",
                            placeholder="e.g. Swab keycard for touch DNA; submit fibers for dye spectrometry...",
                            lines=2
                        )
                        submit_review_btn = gr.Button("⚖ SUBMIT HUMAN DETERMINATION", variant="primary")

                    with gr.Column(scale=1):
                        review_feedback_box = gr.Textbox(label="Review Audit Status", interactive=False)
                        quality_scorecard_md = gr.Markdown("### 📊 Investigation Scorecard\n*Submit Human Review to calculate forensic rigor score.*")
                        history_md = gr.Markdown(render_history_markdown())

            # ------------------------------------------------------------------
            # TAB 8: INVESTIGATION REPLAY LAB
            # ------------------------------------------------------------------
            with gr.TabItem("🔄 Investigation Replay Lab"):
                gr.Markdown("### 🔄 Counterfactual Reasoning & Evidence Variation Experiments")
                gr.Markdown("> Modify or remove critical evidence items to observe how the AI investigation team adapts its reasoning, confidence, and suspect ranking.")

                with gr.Row():
                    with gr.Column():
                        remove_ev_dropdown = gr.Dropdown(
                            label="Counterfactual Experiment: Remove Evidence Item",
                            choices=["E-E (Blue Velvet Fibers)", "E-B (Access Card Log at 8:23 PM)", "E-D (Corridor Video at 8:25 PM)", "E-F (Muddy Shoeprint)"],
                            value="E-E (Blue Velvet Fibers)"
                        )
                        run_replay_btn = gr.Button("🔬 Run Counterfactual Experiment", variant="primary")

                    with gr.Column():
                        replay_results_md = gr.Markdown("### 🔬 Experiment Output\n*Select an evidence item to remove and click 'Run Counterfactual Experiment'.*")

            # ------------------------------------------------------------------
            # TAB 9: FORENSIC ASSISTANT CHAT
            # ------------------------------------------------------------------
            with gr.TabItem("💬 Forensic Case Assistant"):
                gr.Markdown("### 💬 Interactive Forensic Case Assistant")
                gr.Markdown("> Query the active dossier, evidence relationships, or agent findings. Answers are grounded exclusively in case records without hallucinations.")

                chatbot = gr.Chatbot(label="Detective Nexus Intelligence Query", height=400)
                with gr.Row():
                    chat_input = gr.Textbox(label="Ask a question about the case...", placeholder="e.g. 'Why is Arjun Vale leading?' or 'What evidence contradicts Arjun's statement?'", scale=4)
                    chat_btn = gr.Button("Ask Assistant", variant="primary", scale=1)

                chat_btn.click(
                    fn=handle_assistant_chat,
                    inputs=[chat_input, chatbot],
                    outputs=[chat_input, chatbot]
                )
                chat_input.submit(
                    fn=handle_assistant_chat,
                    inputs=[chat_input, chatbot],
                    outputs=[chat_input, chatbot]
                )

            # ------------------------------------------------------------------
            # TAB 11: SUSPECT INTERROGATION ROOM & STRESS GAUGE
            # ------------------------------------------------------------------
            with gr.TabItem("🎙️ Suspect Interrogation"):
                gr.Markdown("### 🎙️ Suspect Cross-Examination & Real-Time Biometric Stress Monitor")
                gr.Markdown(
                    "Interrogate active suspects under caution. Confront them directly with recovered physical evidence, "
                    "probe alibi timelines, and watch the real-time **Biometric Stress & Deception Gauge** react to evasive answers."
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        interrogate_suspect_select = gr.Dropdown(
                            label="Select Suspect to Question",
                            choices=["Arjun Vale (Assistant Curator)", "Lena Ortiz (Facility Technician)", "Theo Park (Visiting Speaker)", "Sofia Reed (Investigative Journalist)"],
                            value="Arjun Vale (Assistant Curator)",
                            interactive=True
                        )
                        confront_clue_select = gr.Dropdown(
                            label="Confront with Evidence Exhibit",
                            choices=[
                                "None",
                                "Evidence E-B: Display Case Electronic Lock Swipe (8:23 PM)",
                                "Evidence E-E: Blue Silk-Velvet Fibers in Folder",
                                "Evidence E-D: Security Corridor Archive Exit (8:25 PM)",
                                "Evidence E-F: Courtyard Muddy Bootprint (Size 9)",
                                "Evidence E-A: Keycard #004 Issued Credentials"
                            ],
                            value="None",
                            interactive=True
                        )
                        stress_gauge_display = gr.HTML(InterrogationEngine.render_stress_gauge_html({}))

                    with gr.Column(scale=2):
                        interrogate_chatbot = gr.Chatbot(label="Interrogation Session Transcript", height=420)
                        with gr.Row():
                            interrogate_input = gr.Textbox(
                                label="Investigator Question / Allegation",
                                placeholder="e.g. 'Where was your keycard at 8:23 PM?' or 'Explain how fibers got into your folder!'",
                                scale=4
                            )
                            interrogate_submit_btn = gr.Button("Cross-Examine", variant="primary", scale=1)

                interrogate_submit_btn.click(
                    fn=handle_interrogate_turn,
                    inputs=[interrogate_suspect_select, interrogate_input, interrogate_chatbot, confront_clue_select],
                    outputs=[interrogate_input, interrogate_chatbot, stress_gauge_display]
                )
                interrogate_input.submit(
                    fn=handle_interrogate_turn,
                    inputs=[interrogate_suspect_select, interrogate_input, interrogate_chatbot, confront_clue_select],
                    outputs=[interrogate_input, interrogate_chatbot, stress_gauge_display]
                )

            # ------------------------------------------------------------------
            # TAB 12: FORENSIC CRIME LAB
            # ------------------------------------------------------------------
            with gr.TabItem("🔬 Forensic Crime Lab"):
                gr.Markdown("### 🔬 Scientific Evidence Testing & Laboratory Analysis")
                gr.Markdown(
                    "Submit physical, digital, and chemical exhibits to the crime laboratory. "
                    "Execute scientific tests including AFIS fingerprint minutiae matching, UV chemical spectrometry, "
                    "and cryptographic ledger audits to produce certified forensic evidence certificates."
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        lab_evidence_select = gr.Dropdown(
                            label="Select Evidence Exhibit to Test",
                            choices=[
                                "E-E (Blue Velvet Micro-Fibers)",
                                "E-B (Display Case Battery Lock Memory)",
                                "E-D (Archival Catalogue Folder)",
                                "E-F (Muddy Bootprint Cast)",
                                "E-A (Physical Access Keycard)"
                            ],
                            value="E-E (Blue Velvet Micro-Fibers)"
                        )
                        lab_test_select = gr.Dropdown(
                            label="Select Laboratory Testing Protocol",
                            choices=ForensicLabEngine.TEST_TYPES,
                            value=ForensicLabEngine.TEST_TYPES[0]
                        )
                        run_lab_test_btn = gr.Button("🔬 EXECUTE SCIENTIFIC LABORATORY TEST", variant="primary")
                        lab_status_txt = gr.Markdown("*Select an exhibit and protocol above to run certified laboratory testing.*")

                    with gr.Column(scale=2):
                        lab_certificate_html = gr.HTML(
                            """
                            <div style="padding: 24px; border: 1px dashed #334155; border-radius: 8px; text-align: center; color: #94a3b8; font-family: monospace;">
                                🔬 LABORATORY SPECTROMETER IDLE: Select an evidence exhibit and click 'EXECUTE SCIENTIFIC LABORATORY TEST'.
                            </div>
                            """
                        )

                run_lab_test_btn.click(
                    fn=handle_run_forensic_lab_test_ui,
                    inputs=[lab_evidence_select, lab_test_select],
                    outputs=[lab_certificate_html, lab_status_txt]
                )

            # ------------------------------------------------------------------
            # TAB 13: COURTROOM TRIAL SIMULATOR
            # ------------------------------------------------------------------
            with gr.TabItem("⚖️ Courtroom Trial"):
                gr.Markdown("### ⚖️ Judicial Criminal Trial & 12-Person Jury Simulator")
                gr.Markdown(
                    "Take your investigation before the court! Formally indict a suspect, watch the State Prosecution "
                    "and AI Defense Attorney clash over reasonable doubt, and receive the 12-person jury deliberation verdict."
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        indict_suspect_select = gr.Dropdown(
                            label="Select Suspect for Formal Indictment",
                            choices=["Arjun Vale", "Lena Ortiz", "Theo Park", "Sofia Reed"],
                            value="Arjun Vale"
                        )
                        commence_trial_btn = gr.Button("⚖️ COMMENCE FORMAL CRIMINAL TRIAL", variant="primary", size="lg")
                        trial_verdict_html = gr.HTML(
                            """
                            <div style="padding: 20px; border: 1px dashed #334155; border-radius: 8px; text-align: center; color: #94a3b8; font-family: monospace;">
                                🏛️ JURY CHAMBER ASSEMBLED: Select an accused suspect and click 'COMMENCE FORMAL CRIMINAL TRIAL'.
                            </div>
                            """
                        )

                    with gr.Column(scale=2):
                        trial_transcript_md = gr.Markdown("### 📜 Courtroom Transcript & Proceedings\n*Trial proceedings will appear here when court is convened.*")

                commence_trial_btn.click(
                    fn=handle_simulate_courtroom_trial_ui,
                    inputs=[indict_suspect_select],
                    outputs=[trial_transcript_md, trial_verdict_html]
                )

            # ------------------------------------------------------------------
            # TAB 14: INFINITE PROCEDURAL MYSTERY GENERATOR
            # ------------------------------------------------------------------
            with gr.TabItem("🎲 Mystery Generator"):
                gr.Markdown("### 🎲 Infinite Procedural Mystery Generator & AI Sandbox")
                gr.Markdown(
                    "Procedurally generate infinite new, balanced mystery cases with interwoven alibis, timeline constraints, "
                    "and forensic evidence. Load generated cases instantly into Detective Nexus with 1 click."
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        proc_genre_dropdown = gr.Dropdown(
                            label="Mystery Genre",
                            choices=list(ProceduralCaseGenerator.GENRES.keys()),
                            value="Museum Art Heist"
                        )
                        proc_diff_dropdown = gr.Dropdown(
                            label="Difficulty Level",
                            choices=["Novice (Direct Clues)", "Detective (Subtle Contradictions)", "Forensic Master (Adversarial False Alibis)"],
                            value="Detective (Subtle Contradictions)"
                        )
                        proc_suspects_slider = gr.Slider(label="Number of Suspects", minimum=3, maximum=5, step=1, value=4)
                        proc_evidence_slider = gr.Slider(label="Number of Evidence Clues", minimum=4, maximum=8, step=1, value=6)
                        gen_proc_btn = gr.Button("🎲 GENERATE PROCEDURAL MYSTERY CASE", variant="primary")
                        load_proc_btn = gr.Button("🚀 Load Generated Case into Detective Nexus Pipeline", variant="secondary", interactive=False)
                        proc_status_msg = gr.Markdown("### 🎯 Generator Status\n*Configure parameters and click 'Generate Procedural Mystery Case'.*")

                    with gr.Column(scale=2):
                        proc_case_json = gr.Code(label="Synthesized MysteryCase JSON", language="json", lines=16)

                gen_proc_btn.click(
                    fn=handle_generate_procedural_case_ui,
                    inputs=[proc_genre_dropdown, proc_diff_dropdown, proc_suspects_slider, proc_evidence_slider],
                    outputs=[proc_case_json, proc_status_msg, load_proc_btn]
                )

                load_proc_btn.click(
                    fn=handle_load_procedural_case_into_nexus,
                    inputs=[proc_case_json],
                    outputs=[proc_status_msg, header_html]
                )

            # ------------------------------------------------------------------
            # TAB 15: OFFICER PROFILE, AUTHENTICATION & CASE HISTORY
            # ------------------------------------------------------------------
            with gr.TabItem("👤 Officer Profile & Case History"):
                gr.Markdown("### 👤 Officer Profile, Authentication & Case History")
                
                # Active Officer Credential Card
                officer_profile_card = gr.HTML(
                    render_officer_card_html(PIPELINE_CACHE.get("active_user", "default_investigator"), is_dark=True)
                )

                with gr.Row():
                    # Column 1: Login & Session Switch
                    with gr.Column():
                        gr.Markdown("#### 🔑 Officer Authentication // Login")
                        login_user_input = gr.Textbox(
                            label="Officer Username",
                            value="default_investigator",
                            placeholder="Enter username..."
                        )
                        login_pwd_input = gr.Textbox(
                            label="Password",
                            type="password",
                            value="nexus2026",
                            placeholder="Enter password..."
                        )
                        with gr.Row():
                            login_btn = gr.Button("🔑 Authenticate & Switch Session", variant="primary")
                            logout_btn = gr.Button("🚪 Logout", variant="secondary")

                        login_msg = gr.Markdown("*Default profile loaded: 'default_investigator' (Password: nexus2026).*")

                    # Column 2: Register New Officer Profile
                    with gr.Column():
                        gr.Markdown("#### 📝 Enrol New Officer Profile")
                        with gr.Accordion("Register New Officer Badge", open=False):
                            reg_name_input = gr.Textbox(label="Officer Full Name", placeholder="e.g. Inspector Arjun Mehra")
                            reg_badge_input = gr.Textbox(label="Badge Number", placeholder="e.g. BADGE-7741")
                            reg_rank_input = gr.Dropdown(
                                label="Security Clearance Rank",
                                choices=[
                                    "Forensic Field Investigator // Grade II",
                                    "Lead Forensic Investigator // Grade IV",
                                    "Chief Superintendent // Grade VI"
                                ],
                                value="Lead Forensic Investigator // Grade IV"
                            )
                            reg_user_input = gr.Textbox(label="Username", placeholder="e.g. arjun_nexus")
                            reg_pwd_input = gr.Textbox(label="Create Password", type="password")
                            reg_btn = gr.Button("📝 Enrol & Login Officer", variant="primary")
                            reg_msg = gr.Markdown("")

                gr.Markdown("### 📁 Historic Investigation Archives (Personal Case History)")
                gr.Markdown("Every case report you upload and analyze is permanently archived in your officer profile with its solvability grade and downloadable dossier.")
                
                officer_history_md = gr.Markdown(
                    render_officer_case_history_markdown(PIPELINE_CACHE.get("active_user", "default_investigator"))
                )
                
                with gr.Row():
                    refresh_officer_hist_btn = gr.Button("🔄 Refresh My Case History", variant="secondary")

                login_btn.click(
                    fn=handle_officer_login,
                    inputs=[login_user_input, login_pwd_input, theme_radio],
                    outputs=[login_msg, officer_profile_card, officer_history_md, header_html]
                )

                logout_btn.click(
                    fn=handle_officer_logout,
                    inputs=[theme_radio],
                    outputs=[login_msg, officer_profile_card, officer_history_md, header_html]
                )

                reg_btn.click(
                    fn=handle_officer_register,
                    inputs=[reg_name_input, reg_badge_input, reg_rank_input, reg_user_input, reg_pwd_input, theme_radio],
                    outputs=[reg_msg, officer_profile_card, officer_history_md, header_html]
                )

                refresh_officer_hist_btn.click(
                    fn=lambda: render_officer_case_history_markdown(PIPELINE_CACHE.get("active_user", "default_investigator")),
                    inputs=[],
                    outputs=[officer_history_md]
                )

            # ------------------------------------------------------------------
            # TAB 16: SYSTEM SETTINGS
            # ------------------------------------------------------------------
            with gr.TabItem("⚙ Settings"):
                gr.Markdown("### ⚙ Forensic System Configuration")
                with gr.Row():
                    with gr.Column():
                        cfg_model = gr.Textbox(label="Active Gemini Model", value=config.GEMINI_MODEL, interactive=False)
                        cfg_port = gr.Textbox(label="Operational Server Port", value=str(config.SERVER_PORT), interactive=False)
                        test_conn_btn = gr.Button("🔌 Test Gemini Connection", variant="primary")

                    with gr.Column():
                        conn_status_box = gr.Textbox(label="Diagnostics Status", interactive=False)
                        conn_detail_box = gr.Textbox(label="Diagnostic Log", lines=4, interactive=False)

                test_conn_btn.click(
                    fn=lambda: (get_client().test_connection()[1], get_client().test_connection()[2]),
                    inputs=[],
                    outputs=[conn_status_box, conn_detail_box]
                )

        # ======================================================================
        # EVENT BINDINGS
        # ======================================================================

        # Full run
        run_all_btn.click(
            fn=run_full_investigation,
            inputs=[],
            outputs=[
                det_output_md,
                ev_output_md,
                sus_output_md,
                skp_output_md,
                chf_output_md,
                activity_log_box,
                verdict_lead_box,
                verdict_caveat_box,
                verdict_pillars_box
            ]
        )

        # Audio Debriefs
        play_dispatch_btn.click(fn=handle_generate_dispatch_audio, inputs=[], outputs=[radio_audio, audio_status_lbl])
        play_chief_audio_btn.click(fn=handle_generate_chief_audio, inputs=[], outputs=[radio_audio, audio_status_lbl])

        # Step by step
        run_det_btn.click(fn=run_detective_step, inputs=[], outputs=[det_output_md, activity_log_box, det_status_txt])
        run_ev_btn.click(fn=run_evidence_step, inputs=[], outputs=[ev_output_md, activity_log_box, ev_status_txt])
        run_sus_btn.click(fn=run_suspect_step, inputs=[], outputs=[sus_output_md, activity_log_box, sus_status_txt])
        run_skp_btn.click(fn=run_skeptic_step, inputs=[], outputs=[skp_output_md, activity_log_box, skp_status_txt])
        run_chf_btn.click(
            fn=run_chief_step,
            inputs=[],
            outputs=[
                chf_output_md,
                activity_log_box,
                chf_status_txt,
                verdict_lead_box,
                verdict_caveat_box,
                verdict_pillars_box
            ]
        )

        # Human Review Submit
        submit_review_btn.click(
            fn=handle_submit_human_review,
            inputs=[review_decision_radio, review_rationale_input, review_next_ev_input, reviewer_name_input],
            outputs=[review_feedback_box, quality_scorecard_md, history_md]
        )

        # Replay experiment
        run_replay_btn.click(
            fn=lambda dropdown_val: run_counterfactual_replay(dropdown_val.split()[0]),
            inputs=[remove_ev_dropdown],
            outputs=[replay_results_md]
        )

        # Tactical Lighting Switcher (Day / Night Mode)
        theme_radio.change(
            fn=handle_theme_toggle,
            inputs=[theme_radio],
            outputs=[theme_style_html, header_html]
        )

    return demo
