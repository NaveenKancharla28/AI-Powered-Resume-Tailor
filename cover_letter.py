"""Evidence-grounded cover-letter generation."""
from __future__ import annotations

import os

from openai import OpenAI


DEFAULT_MODEL = "gpt-4o-mini"


def generate_cover_letter(jd_text: str, career_evidence: str, verified_requirements=None, missing_requirements=None) -> str:
    """Generate a concise cover letter using only verified career evidence."""
    verified_requirements = verified_requirements or []
    missing_requirements = missing_requirements or []
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
You are an evidence-grounded cover-letter writer.

Rules:
- Use ONLY facts explicitly present in CAREER EVIDENCE.
- Do not claim unsupported skills, employers, titles, dates, metrics, certifications, education, or achievements.
- Do not mention a missing requirement as if the candidate has it.
- Connect verified requirements to evidence naturally.
- If a requirement is missing, do not discuss it unless useful as a truthful qualification gap.
- Keep the letter professional, specific, and concise (250-350 words).
- Return only the cover letter.

VERIFIED REQUIREMENTS:
{', '.join(verified_requirements) or 'None'}

UNVERIFIED REQUIREMENTS:
{', '.join(missing_requirements) or 'None'}

CAREER EVIDENCE:
{career_evidence}

JOB DESCRIPTION:
{jd_text}
"""
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()
