# AI-Powered Resume Tailor

An evidence-grounded resume tailoring pipeline that combines hybrid retrieval, deterministic ATS scoring, explainable gap analysis, LLM rewriting, cover-letter generation, and optional Playwright form filling.

The project is designed around one core rule: **the system should tailor a candidate's presentation without inventing qualifications.** Job applications remain human-controlled.

## What it does

1. **Ingest career evidence**
   - Reads local PDFs/CSVs from `data/`.
   - Chunks text and creates embeddings with `sentence-transformers`.
   - Stores vectors in FAISS with source metadata.

2. **Hybrid retrieval (Phase 2)**
   - Combines FAISS semantic retrieval with dependency-free BM25 lexical retrieval.
   - Unifies candidates and applies deterministic reranking: 60% semantic + 40% lexical.
   - Supports metadata filters.

3. **ATS fit scoring (Phase 1)**
   - Deterministic requirement matching with common technology aliases.
   - Reports required-skill, preferred-skill, technology, and seniority coverage.
   - Keeps missing or unverified requirements explicit.

4. **Evidence-grounded tailoring (Phase 1)**
   - Uses only retrieved career evidence when rewriting the resume.
   - The LLM is instructed not to invent employers, titles, dates, skills, metrics, certifications, education, or achievements.
   - Exports a tailored `.docx`.

5. **Explainability and gap analysis (Phase 3)**
   - Classifies requirements as **strong**, **partial**, or **missing**.
   - Shows supporting evidence for strong/partial matches.
   - Produces a deterministic line-level resume diff.
   - Links changed lines to matching JD requirements when possible.

6. **Evidence-grounded cover letters (Phase 3)**
   - Generates a concise cover letter using only verified career evidence.
   - Missing requirements are never presented as candidate qualifications.

7. **Optional application automation**
   - Playwright can fill common application fields and upload the tailored resume.
   - **Submission always requires explicit human confirmation** by typing `submit`.

## Architecture

```text
Job Description
      |
      v
  JD Parser
      |
      v
Hybrid Retrieval <---- Local career evidence
(FAISS + BM25)
      |
      +----> ATS Fit Score
      |
      +----> Evidence Index
      |          |
      |          v
      |      Gap Analysis
      |
      v
Evidence-Grounded Resume Rewrite
      |
      +----> Resume Diff + Change Reasons
      |
      +----> Cover Letter
      |
      v
Human Review
      |
      v
Optional Playwright Form Filling
      |
      v
Explicit Submit Confirmation
```

## Project structure

```text
app.py                  # End-to-end CLI workflow and optional Playwright automation
__init__.py             # RAG setup and retrieval wiring
ats_scorer.py           # Deterministic ATS scoring and requirement matching
evidence.py             # Requirement-to-evidence index and grounding summary
gap_analysis.py         # Strong/partial/missing requirement analysis
resume_diff.py          # Deterministic resume diff and change explanations
cover_letter.py         # Evidence-grounded cover-letter generation
jd_parser.py            # Structured job-description extraction
llm_utils.py             # Evidence-grounded resume rewrite and DOCX export
ingest.py               # Local PDF/CSV ingestion
chunking.py             # Text chunking utilities
embeddings.py           # SentenceTransformer embeddings
retrieval.py            # FAISS + BM25 hybrid retrieval
requirements.txt        # Python dependencies
tests/                  # Phase 1/2/3 unit tests
data/.gitkeep            # Placeholder; real career documents stay local
```

## Prerequisites

- Python 3.11+
- OpenAI API key
- For local Playwright runs: Chromium and its dependencies

## Quick start

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

3. Create `.env`:

```env
OPENAI_API_KEY=sk-...
HEADLESS=1
OUTPUT_DIR=output
```

4. Put your own grounding documents in `data/` locally. **Do not commit resumes, job applications, certificates, or other personal documents.** The repository keeps only `data/.gitkeep`.

5. Run:

```bash
python app.py
```

The application prompts for a job description and optional application URL. It produces:

- `output/tailored_resume.docx`
- `output/cover_letter.txt`
- `output/resume_changes.txt`

## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | OpenAI API access |
| `HEADLESS` | No | `1` | Run Playwright headless (`1`) or visible (`0`) |
| `OUTPUT_DIR` | No | `output` | Generated artifact directory |
| `JD_TEXT` | No | — | Use a JD from the environment instead of prompting |
| `JOB_URL` | No | — | Optional application URL for Playwright |
| `FIRST_NAME` / `LAST_NAME` | No | — | Application form values |
| `PHONE` / `EMAIL` | No | — | Application form values |
| `ADDRESS` / `LINKEDIN` | No | — | Application form values |

## Testing

The unit tests cover the deterministic ATS/evidence behavior, hybrid retrieval, gap classification, and resume diffing.

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The LLM and browser portions require external services/runtime dependencies and are not required for the deterministic unit-test suite.

## Docker

Build:

```bash
docker build -t ai-powered-resume-tailor .
```

Run with Compose:

```bash
docker compose up --build
```

Compose maps the local `./output` directory to the container output directory. Keep personal input documents local and outside version control.

## Safety and privacy

- Never commit `.env` files or personal career documents.
- `data/*`, generated outputs, PDFs, DOCX files, Python caches, and OS metadata are ignored by Git.
- Removing a file from the current branch does **not** erase it from Git history. If sensitive files were previously pushed to a public repository, use a deliberate history-cleanup procedure and rotate any exposed secrets.
- The Playwright flow intentionally requires a human to review the populated form and explicitly confirm submission.

## Roadmap

- **Phase 1:** deterministic ATS scoring, evidence grounding, safe resume rewriting. ✅
- **Phase 2:** hybrid FAISS + BM25 retrieval, reranking, metadata filters. ✅
- **Phase 3:** explainable diffs, gap analysis, evidence-grounded cover letters. ✅
- **Phase 4:** semantic requirement matching, richer evidence graphs, evaluation/benchmarking, and a cleaner API/UI layer.

## License

MIT
