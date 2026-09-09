"""Explainable candidate gap analysis built from verified evidence."""
from __future__ import annotations

import re
from typing import Any

from ats_scorer import requirement_match


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9+#.]+", text.lower()))


def _requirement_evidence(requirement: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        chunk for chunk in chunks
        if requirement_match(requirement, str(chunk.get("chunk", "")))
    ]


def _best_partial_evidence(requirement: str, chunks: list[dict[str, Any]]) -> tuple[float, list[dict[str, Any]]]:
    requirement_tokens = _tokens(requirement)
    if not requirement_tokens:
        return 0.0, []

    scored = []
    for chunk in chunks:
        chunk_tokens = _tokens(str(chunk.get("chunk", "")))
        overlap = len(requirement_tokens & chunk_tokens) / len(requirement_tokens)
        if overlap > 0:
            scored.append((overlap, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    best_score = scored[0][0] if scored else 0.0
    return best_score, [item[1] for item in scored if item[0] == best_score][:3]


def analyze_gaps(parsed_jd: dict[str, Any], evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify JD requirements as strong, partial, or missing.

    Strong requires an explicit deterministic requirement match. Partial is
    reserved for evidence containing at least half of the requirement's
    lexical terms without satisfying the full matcher. Missing means no
    meaningful lexical evidence was retrieved.
    """
    groups = [
        ("required", parsed_jd.get("required_skills", [])),
        ("preferred", parsed_jd.get("preferred_skills", [])),
        ("technology", parsed_jd.get("frameworks_tools", []) + parsed_jd.get("cloud_platforms", []) + parsed_jd.get("genai_ml_concepts", [])),
    ]
    results = []
    for category, requirements in groups:
        for requirement in requirements:
            strong_evidence = _requirement_evidence(requirement, evidence_chunks)
            if strong_evidence:
                status = "strong"
                strength = 1.0
                evidence = strong_evidence
            else:
                strength, partial_evidence = _best_partial_evidence(requirement, evidence_chunks)
                status = "partial" if strength >= 0.5 else "missing"
                evidence = partial_evidence if status == "partial" else []

            results.append({
                "requirement": requirement,
                "category": category,
                "status": status,
                "evidence_strength": round(strength, 2),
                "evidence": [
                    {"filename": item.get("filename", ""), "chunk": item.get("chunk", "")}
                    for item in evidence
                ],
            })

    summary = {
        "strong": sum(item["status"] == "strong" for item in results),
        "partial": sum(item["status"] == "partial" for item in results),
        "missing": sum(item["status"] == "missing" for item in results),
        "total": len(results),
    }
    return {"items": results, "summary": summary}
