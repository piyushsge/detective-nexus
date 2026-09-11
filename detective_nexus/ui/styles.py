"""
Detective Nexus Styling System
Provides forensic dark theme ('Night Tactical') and crisp forensic light theme ('Day Lab').
Enforces strict high-contrast readability across tables, code blocks, textboxes, and graphs.
Completely eliminates white-on-white text, mismatched boxes, or illegible fonts.
"""

FORENSIC_CSS = """
/* ==============================================================================
   CSS VARIABLES FOR DAY & NIGHT FORENSIC MODES
   ============================================================================== */

:root, 
body, 
.gradio-container,
[class*="gradio-container"] {
    --nexus-bg-main: #070707;
    --nexus-bg-panel: #0D0D0D;
    --nexus-bg-card: #111111;
    --nexus-bg-subcard: #161616;
    --nexus-bg-input: #121212;
    --nexus-bg-code: #0A0A0A;
    --nexus-border: #292929;
    --nexus-border-accent: #d97706;
    --nexus-text-main: #F2F2F2;
    --nexus-text-muted: #9CA3AF;
    --nexus-text-dim: #6B7280;
    --nexus-text-code: #fbbf24;
    --nexus-accent-amber: #fbbf24;
    --nexus-accent-emerald: #10b981;
    --nexus-accent-red: #dc2626;
    --nexus-accent-blue: #38bdf8;

    /* Gradio native theme tokens overridden to prevent white background bleed */
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
}

/* Global Container Background & Typography */
body, 
.gradio-container,
[class*="gradio-container"] {
    background-color: var(--nexus-bg-main) !important;
    background: var(--nexus-bg-main) !important;
    color: var(--nexus-text-main) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    transition: background-color 0.25s ease, color 0.25s ease;
}

/* ==============================================================================
   HIGH-CONTRAST TEXTAREA, INPUT & WRAPPER FIXES (NO WHITE-ON-WHITE)
   ============================================================================== */

[class*="gradio-container"] textarea, 
[class*="gradio-container"] input[type="text"], 
[class*="gradio-container"] input[type="password"],
[class*="gradio-container"] input[type="number"],
[class*="gradio-container"] input[type="search"],
[class*="gradio-container"] input[type="email"],
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
textarea, 
input[type="text"],
input[type="password"],
input[type="number"],
select,
.gr-input,
.gr-textbox,
.gr-box {
    background-color: #121212 !important;
    background: #121212 !important;
    color: #F2F2F2 !important;
    border: 1px solid #292929 !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', 'IBM Plex Mono', Consolas, monospace !important;
    font-size: 0.92rem !important;
    line-height: 1.55 !important;
    box-shadow: none !important;
}

/* Input Focus States */
[class*="gradio-container"] textarea:focus, 
[class*="gradio-container"] input:focus,
[class*="gradio-container"] select:focus,
textarea:focus,
input:focus {
    background-color: #181818 !important;
    background: #181818 !important;
    border-color: #fbbf24 !important;
    box-shadow: 0 0 0 1px #fbbf24 !important;
    color: #FFFFFF !important;
    outline: none !important;
}

/* Disabled & Readonly Textareas (Activity Log, Telemetry, Feedback) */
[class*="gradio-container"] textarea:disabled,
[class*="gradio-container"] input:disabled,
[class*="gradio-container"] textarea[readonly],
[class*="gradio-container"] input[readonly],
textarea:disabled,
input:disabled,
textarea[readonly],
input[readonly] {
    background-color: #0A0A0A !important;
    background: #0A0A0A !important;
    color: #9CA3AF !important;
    border-color: #222222 !important;
    cursor: default !important;
}

/* Placeholder Styling */
[class*="gradio-container"] textarea::placeholder,
[class*="gradio-container"] input::placeholder,
textarea::placeholder,
input::placeholder {
    color: #6B7280 !important;
    font-style: italic !important;
}

/* Form component labels */
label,
.gradio-container label,
[class*="gradio-container"] label,
[class*="gradio-container"] .block label,
[class*="gradio-container"] .label-wrap,
[class*="gradio-container"] span[data-testid="block-info"],
[class*="gradio-container"] .block-title,
.block label,
.label-wrap,
span[data-testid="block-info"],
.gr-form label {
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

/* Container blocks */
[class*="gradio-container"] .block,
.gradio-container .block {
    background-color: #111111 !important;
    border: 1px solid #292929 !important;
    border-radius: 8px !important;
}

/* ==============================================================================
   INLINE CODE & BACKTICKS (PERFECT LEGIBILITY EVERYWHERE - NO WHITE BOXES)
   ============================================================================== */

code,
.gradio-container code,
[class*="gradio-container"] code,
.prose code,
li code,
p code,
td code,
th code,
span code,
div code,
a code {
    background-color: #181818 !important;
    background: #181818 !important;
    color: #fbbf24 !important;
    border: 1px solid #333333 !important;
    border-radius: 4px !important;
    padding: 2px 7px !important;
    font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace !important;
    font-size: 0.84em !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    display: inline-block !important;
    line-height: 1.3 !important;
}

/* Pre & Code Blocks (ASCII Graph, Logs, Telemetry) */
[class*="gradio-container"] pre, 
pre, 
[class*="gradio-container"] pre code, 
pre code, 
.nexus-mono {
    background-color: #0A0A0A !important;
    background: #0A0A0A !important;
    color: #38bdf8 !important;
    border: 1px solid #292929 !important;
    border-left: 4px solid #D4AF37 !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    font-family: 'JetBrains Mono', 'Consolas', monospace !important;
    font-size: 0.88rem !important;
    line-height: 1.55 !important;
    overflow-x: auto !important;
}

/* ==============================================================================
   HIGH-CONTRAST MARKDOWN TABLES & MATRIX
   ============================================================================== */

[class*="gradio-container"] table, 
table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 16px 0 !important;
    background-color: #111111 !important;
    background: #111111 !important;
    border: 1px solid #292929 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

[class*="gradio-container"] th, 
th {
    background-color: #161616 !important;
    background: #161616 !important;
    color: #fbbf24 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    padding: 12px 14px !important;
    border: 1px solid #292929 !important;
    text-align: left !important;
}

[class*="gradio-container"] td, 
td {
    background-color: #111111 !important;
    background: #111111 !important;
    color: #F2F2F2 !important;
    border: 1px solid #292929 !important;
    padding: 10px 14px !important;
    font-size: 0.88rem !important;
    line-height: 1.5 !important;
}

[class*="gradio-container"] tr:nth-child(even) td,
tr:nth-child(even) td {
    background-color: #161616 !important;
    background: #161616 !important;
}

/* ==============================================================================
   HEADINGS & PROSE TEXT (ADAPTIVE TO DAY/NIGHT MODES)
   ============================================================================== */

[class*="gradio-container"] h1, h1 {
    color: var(--nexus-text-h1, #F9FAFB) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
}

[class*="gradio-container"] h2, h2 {
    color: var(--nexus-text-h2, #FBBF24) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 700 !important;
    border-bottom: 1px solid var(--nexus-border, #292929) !important;
    padding-bottom: 6px !important;
    margin-top: 18px !important;
}

[class*="gradio-container"] h3, h3 {
    color: var(--nexus-text-h3, #F3F4F6) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 700 !important;
    margin-top: 14px !important;
}

[class*="gradio-container"] h4, h4 {
    color: var(--nexus-text-h4, #38BDF8) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

[class*="gradio-container"] p, p {
    color: var(--nexus-text-p, #D1D5DB) !important;
    line-height: 1.6 !important;
}

[class*="gradio-container"] li, li {
    color: var(--nexus-text-p, #D1D5DB) !important;
    line-height: 1.6 !important;
}

[class*="gradio-container"] strong, strong,
[class*="gradio-container"] b, b {
    color: var(--nexus-text-strong, #FFFFFF) !important;
    font-weight: 700 !important;
}

[class*="gradio-container"] blockquote, blockquote {
    border-left: 4px solid #D4AF37 !important;
    background: #141414 !important;
    color: #E5E7EB !important;
    padding: 12px 16px !important;
    border-radius: 4px !important;
    margin: 12px 0 !important;
}

/* ==============================================================================
   TABS & NAVIGATION
   ============================================================================== */

[class*="gradio-container"] [role="tablist"],
[class*="gradio-container"] .tab-nav,
[class*="gradio-container"] .tabs > div:first-child {
    background-color: #0A0A0A !important;
    border-bottom: 2px solid #292929 !important;
    gap: 4px !important;
}

[class*="gradio-container"] button[role="tab"],
[class*="gradio-container"] .tab-nav button,
[class*="gradio-container"] button.tab-nav {
    background-color: transparent !important;
    color: #9CA3AF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 16px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease !important;
}

[class*="gradio-container"] button[role="tab"].selected,
[class*="gradio-container"] .tab-nav button.selected,
[class*="gradio-container"] button.tab-nav.selected {
    color: #fbbf24 !important;
    border-bottom: 2px solid #d97706 !important;
    background-color: #141414 !important;
    font-weight: 700 !important;
}

/* ==============================================================================
   DROPDOWNS & SELECTIONS
   ============================================================================== */

[class*="gradio-container"] .dropdown,
[class*="gradio-container"] .wrap-inner,
[class*="gradio-container"] .options,
[class*="gradio-container"] .item,
[class*="gradio-container"] .single-select {
    background-color: #121212 !important;
    color: #F2F2F2 !important;
    border-color: #292929 !important;
}

[class*="gradio-container"] .item:hover,
[class*="gradio-container"] .item.selected {
    background-color: #242424 !important;
    color: #fbbf24 !important;
}

/* ==============================================================================
   CHATBOT MESSAGES
   ============================================================================== */

[class*="gradio-container"] [data-testid="bot"],
[class*="gradio-container"] .bot-message,
[class*="gradio-container"] .bot {
    background-color: #111827 !important;
    color: #F3F4F6 !important;
    border: 1px solid #1F2937 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
}

[class*="gradio-container"] [data-testid="user"],
[class*="gradio-container"] .user-message,
[class*="gradio-container"] .user {
    background-color: #1C1917 !important;
    color: #FBBF24 !important;
    border: 1px solid #78350F !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
}

/* ==============================================================================
   ACCORDIONS
   ============================================================================== */

[class*="gradio-container"] details,
[class*="gradio-container"] .accordion {
    background-color: #0D0D0D !important;
    border: 1px solid #292929 !important;
    border-radius: 6px !important;
    margin-bottom: 8px !important;
}

[class*="gradio-container"] summary {
    color: #fbbf24 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    padding: 8px 12px !important;
    cursor: pointer !important;
}

/* ==============================================================================
   FILE UPLOAD DROPZONE
   ============================================================================== */

.gr-file,
.upload-container,
.file-preview,
.drop-target,
.file-upload,
[class*="gradio-container"] .file-upload,
[class*="gradio-container"] .upload-container {
    background-color: #121212 !important;
    border: 2px dashed #383838 !important;
    border-radius: 8px !important;
    color: #E5E7EB !important;
}

.file-preview {
    background-color: #161616 !important;
    border: 1px solid #2E2E2E !important;
    color: #FBBF24 !important;
}

/* ==============================================================================
   BUTTONS
   ============================================================================== */

button.primary,
.gr-button-primary,
button[variant="primary"],
[class*="gradio-container"] button[variant="primary"] {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
    color: #FFFFFF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
    border: 1px solid #f59e0b !important;
    border-radius: 6px !important;
    box-shadow: 0 2px 8px rgba(217, 119, 6, 0.25) !important;
    transition: all 0.2s ease !important;
}

button.primary:hover,
.gr-button-primary:hover,
[class*="gradio-container"] button[variant="primary"]:hover {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    box-shadow: 0 0 14px rgba(245, 158, 11, 0.4) !important;
}

button.secondary,
.gr-button-secondary,
button[variant="secondary"],
[class*="gradio-container"] button[variant="secondary"] {
    background-color: #1a1a1a !important;
    color: #E5E7EB !important;
    border: 1px solid #333333 !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
}

button.secondary:hover,
.gr-button-secondary:hover,
[class*="gradio-container"] button[variant="secondary"]:hover {
    background-color: #242424 !important;
    border-color: #D4AF37 !important;
    color: #FBBF24 !important;
}

/* ==============================================================================
   COMMAND CENTER BANNERS, CARDS & STATUS
   ============================================================================== */

.nexus-header {
    background: linear-gradient(180deg, var(--nexus-bg-panel) 0%, var(--nexus-bg-main) 100%);
    border: 1px solid var(--nexus-border);
    border-top: 4px solid var(--nexus-border-accent);
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.nexus-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: var(--nexus-text-main);
    margin: 0;
}

.nexus-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--nexus-accent-amber);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 4px;
}

.status-badge-active {
    display: inline-flex;
    align-items: center;
    background: #022c22;
    border: 1px solid #059669;
    color: #34d399;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: bold;
    letter-spacing: 0.05em;
}

.critical-window-banner {
    background: linear-gradient(90deg, #2a0808 0%, #1a0505 100%);
    border: 1px solid #7f1d1d;
    border-left: 5px solid #ef4444;
    border-radius: 8px;
    padding: 14px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
}

.critical-window-title {
    font-family: 'JetBrains Mono', monospace;
    color: #f87171;
    font-weight: 800;
    font-size: 0.95rem;
    letter-spacing: 0.06em;
}

.critical-window-time {
    font-family: 'JetBrains Mono', monospace;
    color: #ef4444;
    font-weight: 800;
    font-size: 1.1rem;
}

.nexus-metric-box {
    background: var(--nexus-bg-card);
    border: 1px solid var(--nexus-border);
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.nexus-metric-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--nexus-accent-amber);
    line-height: 1.1;
}

.nexus-metric-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--nexus-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 6px;
}

.evidence-card {
    background: var(--nexus-bg-card);
    border: 1px solid var(--nexus-border);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}

.evidence-card:hover {
    border-color: var(--nexus-accent-amber);
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.2);
}
"""
