# AI-Powered Resume Tailor

An evidence-grounded AI system that tailors a resume to a target job description, explains the changes it makes, identifies skill gaps, generates a grounded cover letter, and can optionally fill an application form with Playwright.

## What it does

The pipeline is designed to keep generated claims tied to the candidate's local career evidence:

1. **Ingest** local PDFs/CSVs from `data/`.
2. **Chunk + embed** career evidence with Sentence Transformers.
3. **Hybrid retrieve** with FAISS semantic search and BM25 lexical search.
4. **Rerank** the candidate evidence deterministically.
5. **Parse the JD** into required, preferred, technology, cloud, and GenAI/ML requirements.
6. **Score job fit** with a deterministic ATS-style baseline.
7. **Analyze gaps** as `strong`, `partial`, or `missing` with evidence and explanations.
8. **Tailor the resume** using verified evidence only.
9. **Diff the resume** and explain meaningful additions against JD requirements.
10. **Generate a cover letter** grounded only in retrieved career evidence.
11. **Export** the tailored resume and cover letter to `output/`.
12. **Optionally auto-fill** an application form; submission always requires explicit human confirmation.

## Explainability and safety

- Requirements are classified conservatively: a direct lexical/alias match is **strong**; related evidence without direct verification is **partial**; no evidence is **missing**.
- Resume diffs are deterministic and show added/removed lines.
- Added lines are traced to matching JD requirements when a deterministic match exists.
- LLM prompts prohibit invented skills, employers, dates, metrics, certifications, education, or achievements.
- Missing requirements are never silently added to the resume or cover letter.
- The browser automation never submits an application without the user explicitly typing `submit`.

## Project structure

```text
app.py                  # End-to-end orchestration and optional Playwright apply flow
__init__.py             # RAG setup and retrieval wiring
ingest.py               # PDF/CSV ingestion
chunking.py             # Text chunking
embeddings.py           # Sentence Transformer embeddings
retrieval.py            # FAISS + BM25 hybrid retrieval and reranking
jd_parser.py            # Structured job-description extraction
ats_scorer.py           # Deterministic ATS-style scoring and aliases
evidence.py             # Requirement-to-career-evidence grounding
gap_analysis.py         # Strong/partial/missing gap analysis
resume_diff.py          # Deterministic resume diff + explanations
llm_utils.py            # Evidence-grounded resume rewriting + DOCX export
cover_letter.py         # Evidence-grounded cover-letter generation
tests/                  # Unit tests
Dockerfile              # Container image
docker-compose.yml      # Local container orchestration
```

## Requirements

- Python 3.11+
- OpenAI API key
- Chromium for local Playwright runs

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

Create `.env`:

```env
OPENAI_API_KEY=sk-...
HEADLESS=1
OUTPUT_DIR=output
```

## Run

Place your own PDFs/CSVs in `data/` locally. They are intentionally ignored by Git.

```bash
python app.py
```

The app asks for a job description and an optional application URL. It produces:

```text
output/tailored_resume.docx
output/cover_letter.txt
```

`OUTPUT_DIR` can be used to change the output location.

## Docker

```bash
docker build -t ai-powered-resume-tailor .
docker compose up --build
```

Compose maps the local `./output` directory into the container. Keep personal career documents outside the public repository.

## Tests

Run the deterministic unit tests with:

```bash
python -m unittest discover -s tests -v
```

The Phase 3.1 suite covers strong/partial/missing gap analysis, missing-evidence explanations, resume additions/removals/replacements, and requirement traceability.

## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | OpenAI API access |
| `HEADLESS` | No | `1` | Playwright browser mode |
| `OUTPUT_DIR` | No | `output` | Generated artifact directory |
| `JD_TEXT` | No | — | Non-interactive job description input |
| `JOB_URL` | No | — | Optional application URL |

## Architecture

```text
Job Description
      |
      v
  JD Parser
      |
      v
Hybrid Retrieval (FAISS + BM25)
      |
      v
Career Evidence -----> ATS Score
      |
      v
  Gap Analysis
   /       \
strong    partial/missing
   |           |
   +-----+-----+
         v
 Evidence-Grounded Resume Tailoring
         |
         +----> Deterministic Diff + Explanations
         |
         +----> Grounded Cover Letter
         |
         v
     Human Review
         |
         v
 Optional Playwright Auto-Fill
         |
         v
 Explicit Submit Confirmation
```

## Privacy

`data/` and generated `output/` artifacts are local-only. Do not commit resumes, job documents, credentials, or other personal career documents to the public repository. The repository keeps `data/.gitkeep` only as the directory placeholder.

## Roadmap

- Semantic requirement matching while retaining the deterministic baseline.
- Better evidence provenance and source-level traceability.
- FastAPI service/UI for interactive job tailoring.
- Evaluation datasets and retrieval/grounding metrics.

## License

MIT
