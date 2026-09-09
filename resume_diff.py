"""Deterministic resume diffing and requirement explanations."""
from __future__ import annotations

import difflib
import re
from typing import Any

from ats_scorer import requirement_match


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())


def build_resume_diff(original: str, tailored: str) -> list[dict[str, str]]:
    """Return added and removed resume lines."""
    original_lines = original.splitlines()
    tailored_lines = tailored.splitlines()
    matcher = difflib.SequenceMatcher(
        a=[_normalize_line(line) for line in original_lines],
        b=[_normalize_line(line) for line in tailored_lines],
    )
    changes = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        for line in original_lines[i1:i2]:
            changes.append({"type": "removed", "text": line})
        for line in tailored_lines[j1:j2]:
            changes.append({"type": "added", "text": line})
    return changes


def summarize_changes(original: str, tailored: str) -> dict[str, int]:
    changes = build_resume_diff(original, tailored)
    return {
        "added": sum(change["type"] == "added" for change in changes),
        "removed": sum(change["type"] == "removed" for change in changes),
        "total": len(changes),
    }


def explain_changes(changes: list[dict[str, str]], requirements: list[str]) -> list[dict[str, Any]]:
    """Trace added lines to JD requirements when a deterministic match exists."""
    explanations = []
    for change in changes:
        if change["type"] != "added":
            continue
        matched = [req for req in requirements if requirement_match(req, change["text"])]
        explanations.append({
            "change": change["text"],
            "matched_requirements": matched,
            "explanation": (
                f"Added to better emphasize: {', '.join(matched)}."
                if matched else
                "Added as a relevance-focused tailoring change; no single requirement matched deterministically."
            ),
        })
    return explanations
