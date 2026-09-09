# llm_utils.py
import os
from openai import OpenAI
from docx import Document

DEFAULT_MODEL = "gpt-4o-mini"


def _client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_keywords_from_jd(jd_text):
    """Legacy keyword extraction retained for backwards compatibility."""
    response = _client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{
            "role": "user",
            "content": (
                "Extract the key skills, tools, technologies, and role keywords from this "
                "job description as a comma-separated list.\n\n" + jd_text
            ),
        }],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def rewrite_resume(chunks, jd_text, verified_requirements=None, missing_requirements=None):
    """Rewrite only from supplied evidence; never invent candidate facts."""
    verified_requirements = verified_requirements or []
    missing_requirements = missing_requirements or []
    prompt = f"""
You are an evidence-grounded professional resume editor.

NON-NEGOTIABLE RULES:
1. Use ONLY facts explicitly present in the CAREER EVIDENCE below.
2. Never invent or infer employers, job titles, dates, technologies, metrics, certifications,
   education, responsibilities, or achievements.
3. Do not add a JD requirement merely because it appears in the job description.
4. You may improve wording, ordering, and emphasis of supported facts.
5. Preserve truthful numbers exactly; never manufacture metrics.
6. Return only the tailored resume text.

Verified JD requirements supported by evidence:
{', '.join(verified_requirements) or 'None'}

JD requirements NOT verified by evidence. Do not add them:
{', '.join(missing_requirements) or 'None'}

CAREER EVIDENCE:
{chunks}

JOB DESCRIPTION:
{jd_text}
"""
    response = _client().chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def save_resume_to_docx(text, filename="tailored_resume.docx"):
    """Save the tailored resume to a .docx file."""
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(filename)
    print(f"Saved tailored resume to {filename}")
