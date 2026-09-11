"""
Configuration Module for AI Mystery Detective Team.

Responsibilities:
- Load environment variables using python-dotenv.
- Read GEMINI_API_KEY safely.
- Read GEMINI_MODEL.
- Provide application and case metadata.
- Validate configuration without leaking secrets.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure console supports UTF-8 on Windows
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

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

# Load environment variables
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE, override=True)
else:
    load_dotenv(override=True)

# Application & Case Metadata
APP_NAME = "AI Mystery Detective Team"
CASE_NAME = "The Vanishing Aurora Diamond"
APP_STAGE = "PART 1 — System Foundation"

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash"


def validate_config() -> tuple[bool, str]:
    """
    Validates whether the Gemini configuration is present and usable.

    Returns:
        tuple[bool, str]: (is_valid, status_message)
        Never exposes the actual API key or sensitive values.
    """
    # Re-read in case .env was modified while running
    current_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    if not current_key:
        return False, "GEMINI_API_KEY is missing. Please configure it in your .env file."

    if current_key == "YOUR_GEMINI_API_KEY_HERE":
        return (
            False,
            "GEMINI_API_KEY is still set to placeholder 'YOUR_GEMINI_API_KEY_HERE'. "
            "Please replace it with your actual Gemini API key in .env."
        )

    return True, "Configuration valid. Ready to connect."
