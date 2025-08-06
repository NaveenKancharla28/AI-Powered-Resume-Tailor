# llm_utils.py
import os
from openai import OpenAI
from docx import Document

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keywords_from_jd(jd_text):
    """
    Extract important skills, tools, and job role keywords from a job description.
    """
    prompt = f"""
    You are a career assistant. Extract the key skills, tools, technologies, and role keywords
    from the job description below as a comma-separated list.

    Job Description:
    {jd_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # You can change this model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def rewrite_resume(chunks, jd_text):
    """
    Rewrite the resume using relevant chunks and the JD.
    """
    prompt = f"""
    You are a professional resume editor. Based on the resume content below and the job description,
    rewrite the resume so it is tailored for the role. Keep it ATS-friendly and professional.

    Resume Chunks:
    {chunks}

    Job Description:
    {jd_text}

    Return only the improved resume text.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # You can use gpt-4 or gpt-3.5
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def save_resume_to_docx(text, filename="tailored_resume.docx"):
    """
    Save the tailored resume to a .docx file.
    """
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(filename)
    print(f"Saved tailored resume to {filename}")
