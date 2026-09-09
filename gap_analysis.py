"""Explainable candidate gap analysis built from verified evidence."""
from __future__ import annotations

from typing import Any

from ats_scorer import requirement_match


def _requirement_evidence(requirement: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        chunk for chunk in chunks
        if requirement_match(requirement, str(chunk.get("chunk", "")))
    ]


def analyze_gaps(parsed_jd: dict[str, Any], evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify each JD requirement as strong, partial, or missing.

    The lexical evidence test is intentionally conservative: a requirement is
    never considered supported merely because it appears in the JD.
    """
    groups = [
        ("required", parsed_jd.get("required_skills", [])),
        ("preferred", parsed_jd.get("preferred_skills", [])),
        ("technology", parsed_jd.get("frameworks_tools", []) + parsed_jd.get("cloud_platforms", []) + parsed_jd.get("genai_ml_concepts", [])),
    ]
    results = []
    for category, requirements in groups:
        for requirement in requirements:
            evidence = _requirement_evidence(requirement, evidence_chunks)
            if evidence:
                status = "strong"
            else:
                status = "missing"
            results.append({
                "requirement": requirement,
                "category": category,
                "status": status,
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
