"""
Case Registry & Catalog for AI Mystery Case Platform.
Manages all built-in, generated, and custom cases.
Supports filtering, searching, Random Mystery selection, and deterministic Daily Mystery.
"""

import datetime
import hashlib
import random
from typing import Dict, List, Any, Optional
from app.library.builtin_cases import BUILTIN_CASES, load_all_builtin_cases
from app.library.case_generator import load_all_generated_cases


def get_all_cases() -> List[Dict[str, Any]]:
    """Returns a unified list of all available cases (built-in + generated)."""
    builtin = load_all_builtin_cases()
    generated = load_all_generated_cases()
    return builtin + generated


def find_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    """Locates a case by its unique ID across built-in and generated cases."""
    cid_norm = case_id.strip().upper()
    for c in get_all_cases():
        if c.get("caseId", "").upper() == cid_norm:
            return c
    return None


def filter_cases(
    search_query: str = "",
    category: str = "All",
    difficulty: str = "All",
    case_type: str = "All",  # "All", "Built-in", "Generated"
) -> List[Dict[str, Any]]:
    """Filters cases according to user criteria."""
    all_cases = get_all_cases()
    filtered = []

    query = search_query.strip().lower()

    for c in all_cases:
        cid = c.get("caseId", "")
        title = c.get("title", "")
        cat = c.get("category", "")
        diff = c.get("difficulty", "")
        is_gen = cid.startswith("GEN-")

        # Type filter
        if case_type == "Built-in" and is_gen:
            continue
        if case_type == "Generated" and not is_gen:
            continue

        # Category filter
        if category != "All" and category.lower() not in cat.lower():
            continue

        # Difficulty filter
        if difficulty != "All" and difficulty.lower() not in diff.lower():
            continue

        # Search query
        if query:
            searchable = f"{cid} {title} {cat} {c.get('setting', '')} {c.get('incident', '')}".lower()
            if query not in searchable:
                continue

        filtered.append(c)

    return filtered


def get_case_of_the_day() -> Dict[str, Any]:
    """
    Returns a consistent 'Case of the Day' based on today's UTC calendar date.
    Deterministic: stays identical for everyone on the same day without altering every refresh.
    """
    cases = load_all_builtin_cases()
    if not cases:
        cases = BUILTIN_CASES

    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    hash_int = int(hashlib.md5(today_str.encode("utf-8")).hexdigest(), 16)
    idx = hash_int % len(cases)
    return cases[idx]


def get_random_mystery(
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Selects a random mystery case, optionally filtered by difficulty or category."""
    cases = get_all_cases()
    if difficulty and difficulty != "All":
        cases = [c for c in cases if difficulty.lower() in c.get("difficulty", "").lower()]
    if category and category != "All":
        cases = [c for c in cases if category.lower() in c.get("category", "").lower()]

    if not cases:
        cases = load_all_builtin_cases()

    return random.choice(cases)


def format_difficulty_stars(difficulty: str) -> str:
    """Helper to format difficulty string into cinematic star ratings."""
    diff_lower = difficulty.lower()
    if "expert" in diff_lower:
        return "★★★★★ (Expert)"
    if "hard" in diff_lower:
        return "★★★★☆ (Hard)"
    if "medium" in diff_lower:
        return "★★★☆☆ (Medium)"
    if "easy" in diff_lower:
        return "★★☆☆☆ (Easy)"
    return "★☆☆☆☆ (Beginner)"
