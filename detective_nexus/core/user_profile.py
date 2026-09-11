"""
Detective Nexus Officer Profile & Authentication Engine
Pure Python implementation for officer registration, authentication, session management,
and persistent case history tracking stored in local JSON format.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = (PROJECT_ROOT / "data").resolve()
PROFILES_FILE = DATA_DIR / "user_profiles.json"


class UserProfileManager:
    """Manages forensic officer accounts, authentication, and individual case histories."""

    @classmethod
    def _ensure_storage(cls):
        """Ensures storage directory and default accounts exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not PROFILES_FILE.exists():
            default_profiles = {
                "default_investigator": {
                    "username": "default_investigator",
                    "password_hash": cls._hash_password("nexus2026"),
                    "officer_name": "Senior Inspector Vikram Rathore",
                    "badge_id": "BADGE-4892",
                    "rank_clearance": "Lead Forensic Investigator // Grade IV",
                    "department": "Special Forensic & Incident Reconstruction Division",
                    "created_at": "2026-09-01 08:00:00",
                    "case_history": []
                }
            }
            PROFILES_FILE.write_text(json.dumps(default_profiles, indent=2), encoding="utf-8")

    @classmethod
    def _hash_password(cls, password: str) -> str:
        """Computes SHA-256 hash for secure local password storage."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def _load_all(cls) -> Dict[str, Any]:
        """Loads all user profiles from storage."""
        cls._ensure_storage()
        try:
            return json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @classmethod
    def _save_all(cls, data: Dict[str, Any]):
        """Persists all user profiles to storage."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PROFILES_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def register_officer(
        cls,
        username: str,
        password: str,
        officer_name: str,
        badge_id: str,
        rank_clearance: str = "Forensic Field Investigator // Grade II",
        department: str = "Metropolitan Crimes & Document Analysis Unit"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Registers a new officer profile."""
        username = username.strip().lower()
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters.", None
        if not password or len(password) < 4:
            return False, "Password must be at least 4 characters.", None
        if not officer_name.strip():
            officer_name = f"Officer {username.title()}"
        if not badge_id.strip():
            badge_id = f"BADGE-{int(time.time()) % 10000:04d}"

        profiles = cls._load_all()
        if username in profiles:
            return False, f"Officer username '{username}' already exists. Please login instead.", None

        new_profile = {
            "username": username,
            "password_hash": cls._hash_password(password),
            "officer_name": officer_name.strip(),
            "badge_id": badge_id.strip(),
            "rank_clearance": rank_clearance,
            "department": department,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "case_history": []
        }
        profiles[username] = new_profile
        cls._save_all(profiles)

        sanitized = dict(new_profile)
        sanitized.pop("password_hash", None)
        return True, f"Officer profile '{officer_name}' (Badge {badge_id}) registered successfully.", sanitized

    @classmethod
    def authenticate(cls, username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Authenticates an officer by username and password."""
        username = username.strip().lower()
        profiles = cls._load_all()

        if username not in profiles:
            return False, "Officer credentials not found. Please register an officer profile.", None

        user = profiles[username]
        if user.get("password_hash") != cls._hash_password(password):
            return False, "Incorrect password. Authentication denied.", None

        sanitized = dict(user)
        sanitized.pop("password_hash", None)
        return True, f"Welcome back, {user.get('officer_name')} (Badge {user.get('badge_id')}).", sanitized

    @classmethod
    def get_profile(cls, username: str) -> Optional[Dict[str, Any]]:
        """Retrieves profile without sensitive password hash."""
        profiles = cls._load_all()
        user = profiles.get(username.strip().lower())
        if not user:
            return None
        sanitized = dict(user)
        sanitized.pop("password_hash", None)
        return sanitized

    @classmethod
    def log_case_to_user_history(
        cls,
        username: str,
        case_title: str,
        report_category: str,
        score: int,
        grade: str,
        summary: str,
        export_file_path: str = ""
    ) -> bool:
        """Appends an uploaded or analyzed case to the officer's history log."""
        username = username.strip().lower()
        profiles = cls._load_all()
        if username not in profiles:
            # Fallback to default investigator if user not found
            username = "default_investigator"
            if username not in profiles:
                return False

        record = {
            "record_id": f"REC-{int(time.time())}-{len(profiles[username].get('case_history', [])) + 1}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "case_title": case_title,
            "report_category": report_category,
            "overall_score": score,
            "grade": grade,
            "summary_snippet": summary[:250] + ("..." if len(summary) > 250 else ""),
            "export_file_path": export_file_path
        }

        if "case_history" not in profiles[username]:
            profiles[username]["case_history"] = []

        profiles[username]["case_history"].insert(0, record)
        cls._save_all(profiles)
        return True

    @classmethod
    def get_user_history(cls, username: str) -> List[Dict[str, Any]]:
        """Returns the list of cases analyzed by this officer."""
        user = cls.get_profile(username)
        if not user:
            return []
        return user.get("case_history", [])
