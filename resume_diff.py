"""Deterministic resume diffing and change explanations."""
from __future__ import annotations

import difflib
import re

from ats_scorer import requirement_match


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())


def build_resume_diff(original: str, tailored: str) -> list[dict[str, str]]:
    """Return added and removed resume lines with deterministic line numbers."""
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
        for offset, line in enumerate(original_lines[i1:i2]):
            changes.append({
                "type": "removed",
                "text": line,
                "line": str(i1 + offset + 1),
            })
        for offset, line in enumerate(tailored_lines[j1:j2]):
            changes.append({
                "type": "added",
                "text": line,
                "line": str(j1 + offset + 1),
            })
    return changes


def explain_changes(changes: list[dict[str, str]], requirements: list[str]) -> list[dict[str, str]]:
    """Attach a deterministic reason to each changed line when possible."""
    explanations = []
    for change in changes:
        matches = [
            requirement for requirement in requirements
            if requirement_match(requirement, change["text"])
        ]
        if change["type"] == "added":
            reason = f"Added to strengthen alignment with: {', '.join(matches)}." if matches else "Added during evidence-grounded tailoring; review against the source evidence."
        else:
            reason = f"Removed to de-emphasize content while aligning with: {', '.join(matches)}." if matches else "Removed during evidence-grounded tailoring; review against the source evidence."
        explanations.append({**change, "reason": reason})
    return explanations


def summarize_changes(original: str, tailored: str) -> dict[str, int]:
    changes = build_resume_diff(original, tailored)
    return {
        "added": sum(change["type"] == "added" for change in changes),
        "removed": sum(change["type"] == "removed" for change in changes),
        "total": len(changes),
    }
