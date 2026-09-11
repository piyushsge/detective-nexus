import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
NEXUS_ROOT = Path(__file__).resolve().parent

# Load .env file from project root
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Application Settings
APP_NAME = "DETECTIVE NEXUS"
APP_SUBTITLE = "CASE ROOM // AI INVESTIGATION OPERATING SYSTEM"
APP_VERSION = "2.0.0-FORENSIC"
SERVER_PORT = int(os.getenv("PORT", 7860))

# Investigation Flags
DEFAULT_STRICT_EVIDENCE = True
DEFAULT_CONFIDENCE_THRESHOLD = "HIGH"

def validate_gemini_config() -> tuple[bool, str]:
    """Validates presence and format of GEMINI_API_KEY."""
    if not GEMINI_API_KEY:
        return False, "GEMINI_API_KEY is not set in environment or .env file."
    if len(GEMINI_API_KEY.strip()) < 10:
        return False, "GEMINI_API_KEY appears malformed or placeholder."
    return True, "GEMINI_API_KEY configured and verified."
