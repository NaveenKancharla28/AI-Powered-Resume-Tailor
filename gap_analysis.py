"""Explainable candidate gap analysis built from verified career evidence."""
from __future__ import annotations

import re
from typing import Any

from ats_scorer import requirement_match


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9+#.]+", (text or "").lower()))


def _requirement_evidence(requirement: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        chunk for chunk in chunks
        if requirement_match(requirement, str(chunk.get("chunk", "")))
    ]


def _partial_evidence(requirement: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find related evidence without treating it as direct support."""
    requirement_tokens = _tokens(requirement)
    if not requirement_tokens:
        return []
    candidates = []
    for chunk in chunks:
        chunk_tokens = _tokens(str(chunk.get("chunk", "")))
        overlap = len(requirement_tokens & chunk_tokens) / len(requirement_tokens)
        if overlap >= 0.34:
            candidates.append((overlap, chunk))
    candidates.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in candidates[:3]]


def analyze_gaps(parsed_jd: dict[str, Any], evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify each JD requirement as strong, partial, or missing.

    Strong requires a direct deterministic match. Partial means related career
    evidence exists but does not directly verify the requirement. Missing means
    no meaningful evidence was found.
    """
    groups = [
        ("required", parsed_jd.get("required_skills", [])),
        ("preferred", parsed_jd.get("preferred_skills", [])),
        ("technology", parsed_jd.get("frameworks_tools", []) + parsed_jd.get("cloud_platforms", []) + parsed_jd.get("genai_ml_concepts", [])),
    ]
    results = []
    for category, requirements in groups:
        for requirement in requirements:
            direct = _requirement_evidence(requirement, evidence_chunks)
            evidence = direct
            if direct:
                status = "strong"
            else:
                evidence = _partial_evidence(requirement, evidence_chunks)
                status = "partial" if evidence else "missing"
            results.append({
                "requirement": requirement,
                "category": category,
                "status": status,
                "evidence": [
                    {"filename": item.get("filename", ""), "chunk": item.get("chunk", "")}
                    for item in evidence
                ],
                "explanation": (
                    "Direct evidence supports this requirement."
                    if status == "strong" else
                    "Related evidence exists, but it does not directly verify this requirement."
                    if status == "partial" else
                    "No relevant career evidence was retrieved for this requirement."
                ),
            })

    summary = {
        "strong": sum(item["status"] == "strong" for item in results),
        "partial": sum(item["status"] == "partial" for item in results),
        "missing": sum(item["status"] == "missing" for item in results),
        "total": len(results),
    }
    return {"items": results, "summary": summary}
