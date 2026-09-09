"""Deterministic ATS scoring and requirement matching.

The scorer intentionally uses lexical/alias matching rather than an LLM so the
reported score is reproducible and auditable.
"""
from __future__ import annotations

import re
from typing import Any


ALIASES = {
    "machine learning": {"machine learning", "ml"},
    "deep learning": {"deep learning", "neural networks", "neural network"},
    "generative ai": {"generative ai", "genai", "gen ai"},
    "retrieval augmented generation": {"retrieval augmented generation", "rag"},
    "vector databases": {"vector database", "vector databases", "vector db", "vector dbs"},
    "natural language processing": {"natural language processing", "nlp"},
    "postgresql": {"postgresql", "postgres"},
    "javascript": {"javascript", "js"},
    "typescript": {"typescript", "ts"},
    "kubernetes": {"kubernetes", "k8s"},
    "amazon web services": {"amazon web services", "aws"},
    "microsoft azure": {"microsoft azure", "azure"},
    "google cloud": {"google cloud", "gcp"},
}

SENIORITY_LEVELS = ["intern", "entry", "junior", "associate", "mid", "mid-level", "senior", "lead", "staff", "principal", "director"]


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9+#.\- ]+", " ", str(value).lower()).strip()


def _variants(term: str) -> set[str]:
    normalized = _normalize(term)
    return {normalized, *ALIASES.get(normalized, set())}


def requirement_match(requirement: str, evidence_text: str) -> bool:
    evidence = _normalize(evidence_text)
    return any(re.search(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])", evidence) for v in _variants(requirement) if v)


def _coverage(requirements: list[str], evidence: str) -> tuple[float, list[str], list[str]]:
    if not requirements:
        return 100.0, [], []
    matched, missing = [], []
    for requirement in requirements:
        (matched if requirement_match(requirement, evidence) else missing).append(requirement)
    return round(100 * len(matched) / len(requirements), 1), matched, missing


def score_job_fit(parsed_jd: dict[str, Any], evidence_chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """Return an auditable ATS score from structured JD requirements and evidence."""
    evidence = "\n".join(str(chunk.get("chunk", "")) for chunk in evidence_chunks)
    required = list(parsed_jd.get("required_skills", []))
    preferred = list(parsed_jd.get("preferred_skills", []))
    technologies = list(parsed_jd.get("frameworks_tools", [])) + list(parsed_jd.get("cloud_platforms", [])) + list(parsed_jd.get("genai_ml_concepts", []))

    required_pct, required_matches, required_missing = _coverage(required, evidence)
    preferred_pct, preferred_matches, preferred_missing = _coverage(preferred, evidence)
    tech_pct, tech_matches, tech_missing = _coverage(technologies, evidence)

    seniority = _normalize(parsed_jd.get("seniority", "unknown"))
    seniority_match = 100.0 if seniority in {"", "unknown", "not specified"} else (100.0 if requirement_match(seniority, evidence) else 50.0)

    # Required requirements carry the most weight; technology overlap is a separate signal.
    overall = round(required_pct * 0.50 + tech_pct * 0.25 + preferred_pct * 0.15 + seniority_match * 0.10, 1)
    missing = list(dict.fromkeys(required_missing + tech_missing + preferred_missing))
    return {
        "overall_score": overall,
        "required_skill_coverage": required_pct,
        "preferred_skill_coverage": preferred_pct,
        "technology_coverage": tech_pct,
        "seniority_alignment": seniority_match,
        "required_matches": required_matches,
        "preferred_matches": preferred_matches,
        "technology_matches": tech_matches,
        "missing_requirements": missing,
    }
