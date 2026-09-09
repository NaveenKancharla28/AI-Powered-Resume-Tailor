import json
from openai import OpenAI


DEFAULT_MODEL = "gpt-4o-mini"


def _client():
    return OpenAI()


def parse_job_description(jd_text: str, model: str = DEFAULT_MODEL) -> dict:
    """Convert an unstructured job description into a stable, machine-readable schema."""
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description cannot be empty.")

    prompt = """
You are a job-description parser. Extract only information explicitly supported by the job description.
Return valid JSON with exactly these keys:
{
  "role_title": "string",
  "seniority": "string or unknown",
  "required_skills": [],
  "preferred_skills": [],
  "frameworks_tools": [],
  "cloud_platforms": [],
  "genai_ml_concepts": [],
  "responsibilities": [],
  "education_requirements": [],
  "certifications": []
}
Use short canonical skill names. Do not infer technologies that are not present.

JOB DESCRIPTION:
""" + jd_text

    response = _client().chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)

    list_keys = [
        "required_skills", "preferred_skills", "frameworks_tools",
        "cloud_platforms", "genai_ml_concepts", "responsibilities",
        "education_requirements", "certifications"
    ]
    for key in list_keys:
        if not isinstance(data.get(key), list):
            data[key] = []
    data["role_title"] = str(data.get("role_title") or "Unknown")
    data["seniority"] = str(data.get("seniority") or "unknown")
    return data
