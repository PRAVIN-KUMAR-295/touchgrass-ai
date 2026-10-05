"""Deterministic server-side safety checks for outdoor missions."""

import re
from typing import List, Tuple

# Prohibited dangerous keywords and patterns
PROHIBITED_PATTERNS = [
    r"\btrespass(ing)?\b",
    r"\bprivate property\b",
    r"\bclimb(ing)?\s+(roof|fence|crane|cliff|tree|tower|structure)\b",
    r"\bhighway\b",
    r"\bbusy road\b",
    r"\bfreeway\b",
    r"\btrain tracks?\b",
    r"\brailroad\b",
    r"\bconstruction site\b",
    r"\babandoned building\b",
    r"\bweapon\b",
    r"\billegal\b",
    r"\bsteal(ing)?\b",
    r"\bvandal(ism)?\b",
    r"\bdaredevil\b",
    r"\brisk(y)? stunt\b",
    r"\bpoison\b",
    r"\beven in the dark alone\b",
]

COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in PROHIBITED_PATTERNS]


def validate_mission_safety(title: str, steps: List[str], safety_note: str) -> Tuple[bool, str]:
    """
    Validate that generated mission content does not violate safety policies.
    Returns (is_safe, reason).
    """
    text_corpus = f"{title}\n" + "\n".join(steps) + f"\n{safety_note}"

    for pattern in COMPILED_PATTERNS:
        match = pattern.search(text_corpus)
        if match:
            return False, f"Prohibited or unsafe activity pattern detected: '{match.group(0)}'"

    # Ensure steps don't instruct user to stare at their phone
    screen_patterns = [
        re.compile(r"\bscroll (instagram|tiktok|twitter|reddit|facebook|social media)\b", re.IGNORECASE),
        re.compile(r"\bkeep checking your phone\b", re.IGNORECASE),
        re.compile(r"\bstare at (the|your) screen\b", re.IGNORECASE),
    ]
    for pattern in screen_patterns:
        match = pattern.search(text_corpus)
        if match:
            return False, f"Mission contradicts screen-minimal philosophy: '{match.group(0)}'"

    return True, "Safe"
