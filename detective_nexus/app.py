"""
Detective Nexus: AI Mystery Investigation System
Root executable launcher.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 stdout configuration
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from detective_nexus import config
from detective_nexus.ui.dashboard import build_detective_nexus_app

from detective_nexus.ui.theme import get_forensic_theme
from detective_nexus.ui.styles import FORENSIC_CSS

def main():
    print("=" * 70)
    print(f"STARTING {config.APP_NAME} — {config.APP_SUBTITLE}")
    print(f"Version: {config.APP_VERSION}")
    print(f"Active Case: CASE-001 (The Vanishing Aurora Diamond)")
    print(f"Gemini Model: {config.GEMINI_MODEL}")
    print("=" * 70)

    theme = get_forensic_theme()
    demo = build_detective_nexus_app()
    demo.launch(
        server_port=config.SERVER_PORT,
        inbrowser=False,
        theme=theme,
        css=FORENSIC_CSS,
        allowed_paths=[
            str(PROJECT_ROOT.resolve()),
            str((PROJECT_ROOT / "data" / "audio").resolve())
        ]
    )

if __name__ == "__main__":
    main()
