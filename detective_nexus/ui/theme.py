import gradio as gr

def get_forensic_theme() -> gr.Theme:
    """
    Constructs the official Forensic Command Center theme:
    - Primary background: #070707 (void black)
    - Secondary background: #0D0D0D (charcoal)
    - Panel: #111111
    - Panel elevated / Inputs: #121212
    - Border: #292929
    - Primary text: #F2F2F2
    - Secondary text: #9CA3AF
    - Muted text: #6B7280
    - Evidence accent: muted amber/gold (#d97706, #fbbf24)
    - Typography: Monospace for technical metadata; clean sans-serif for body
    """
    theme = gr.themes.Base(
        primary_hue=gr.themes.colors.amber,
        secondary_hue=gr.themes.colors.neutral,
        neutral_hue=gr.themes.colors.neutral,
        font=[gr.themes.GoogleFont("Inter"), gr.themes.GoogleFont("IBM Plex Sans"), "sans-serif"],
        font_mono=[gr.themes.GoogleFont("JetBrains Mono"), gr.themes.GoogleFont("IBM Plex Mono"), "monospace"]
    ).set(
        # Base backgrounds (set both normal and dark to eliminate light-mode leakage)
        body_background_fill="#070707",
        body_background_fill_dark="#070707",
        background_fill_primary="#070707",
        background_fill_primary_dark="#070707",
        background_fill_secondary="#0D0D0D",
        background_fill_secondary_dark="#0D0D0D",

        # Text colors
        body_text_color="#F2F2F2",
        body_text_color_dark="#F2F2F2",
        body_text_color_subdued="#9CA3AF",
        body_text_color_subdued_dark="#9CA3AF",

        # Borders
        border_color_primary="#292929",
        border_color_primary_dark="#292929",
        border_color_accent="#d97706",
        border_color_accent_dark="#d97706",

        # Blocks & Panels
        block_background_fill="#111111",
        block_background_fill_dark="#111111",
        block_border_color="#292929",
        block_border_color_dark="#292929",
        block_title_text_color="#F2F2F2",
        block_title_text_color_dark="#F2F2F2",
        block_label_text_color="#D4AF37",
        block_label_text_color_dark="#D4AF37",
        block_label_background_fill="#161616",
        block_label_background_fill_dark="#161616",
        panel_background_fill="#0D0D0D",
        panel_background_fill_dark="#0D0D0D",

        # Inputs & Textboxes (High Contrast, No White-on-White)
        input_background_fill="#121212",
        input_background_fill_dark="#121212",
        input_background_fill_focus="#161616",
        input_background_fill_focus_dark="#161616",
        input_background_fill_hover="#141414",
        input_background_fill_hover_dark="#141414",
        input_border_color="#292929",
        input_border_color_dark="#292929",
        input_border_color_focus="#fbbf24",
        input_border_color_focus_dark="#fbbf24",
        input_placeholder_color="#6B7280",
        input_placeholder_color_dark="#6B7280",

        # Tables
        table_border_color="#292929",
        table_border_color_dark="#292929",
        table_even_background_fill="#111111",
        table_even_background_fill_dark="#111111",
        table_odd_background_fill="#0D0D0D",
        table_odd_background_fill_dark="#0D0D0D",

        # Buttons
        button_primary_background_fill="#d97706",
        button_primary_background_fill_hover="#b45309",
        button_primary_text_color="#FFFFFF",
        button_secondary_background_fill="#1A1A1A",
        button_secondary_background_fill_hover="#262626",
        button_secondary_text_color="#E5E7EB",

        # Code
        code_background_fill="#0A0A0A",
        code_background_fill_dark="#0A0A0A"
    )
    return theme
