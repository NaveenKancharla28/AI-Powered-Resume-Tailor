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


def _evidence_strength(requirement: str, evidence: list[dict[str, Any]]) -> float:
    """Estimate lexical evidence coverage without inventing semantic support."""
    requirement_tokens = _tokens(requirement)
    if not requirement_tokens:
        return 0.0
    evidence_tokens = _tokens(" ".join(str(item.get("chunk", "")) for item in evidence))
    return len(requirement_tokens & evidence_tokens) / len(requirement_tokens)


def analyze_gaps(parsed_jd: dict[str, Any], evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify each JD requirement as strong, partial, or missing.

    Matching is deliberately conservative. A requirement is only strong when
    the existing deterministic requirement matcher finds explicit evidence.
    Partial means some requirement terms are present but the full requirement
    is not verified. Missing means there is no meaningful lexical evidence.
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
            strength = _evidence_strength(requirement, evidence)
            if evidence:
                status = "strong"
            elif strength >= 0.5:
                status = "partial"
            else:
                status = "missing"
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
