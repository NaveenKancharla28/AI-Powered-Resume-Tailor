"""Evidence verification helpers for grounded resume generation."""
from __future__ import annotations

from typing import Any

from ats_scorer import requirement_match


def build_evidence_index(chunks: list[dict[str, Any]], requirements: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Map each JD requirement to the retrieved career chunks that explicitly support it."""
    index: dict[str, list[dict[str, Any]]] = {}
    for requirement in requirements:
        matches = []
        for chunk in chunks:
            text = str(chunk.get("chunk", ""))
            if requirement_match(requirement, text):
                matches.append({
                    "filename": chunk.get("filename", "unknown"),
                    "chunk": text,
                    "distance": chunk.get("distance"),
                })
        index[requirement] = matches
    return index


def verified_requirements(index: dict[str, list[dict[str, Any]]]) -> list[str]:
    return [requirement for requirement, matches in index.items() if matches]


def unsupported_requirements(index: dict[str, list[dict[str, Any]]]) -> list[str]:
    return [requirement for requirement, matches in index.items() if not matches]


def evidence_summary(index: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    total = len(index)
    verified = len(verified_requirements(index))
    return {
        "total_requirements": total,
        "verified_requirements": verified,
        "grounding_coverage": round(100 * verified / total, 1) if total else 100.0,
        "verified": verified_requirements(index),
        "unsupported": unsupported_requirements(index),
    }
