
# AI‑Powered Resume Tailor (RAG + Auto‑Apply)

A developer‑friendly tool that tailors your resume to a target Job Description (JD) and optionally auto‑fills common ATS forms. It combines a light Retrieval‑Augmented Generation (RAG) pipeline over your local career documents with LLM‑powered rewriting and Playwright automation for job applications.

---

## What this does

1. **RAG Grounding (Local PDFs/CSVs)**
   - Ingests PDFs and CSVs from a `data/` folder.
   - Chunks text, creates embeddings with `sentence-transformers`, and stores them in **FAISS**.
   - Retrieves the most relevant chunks against your JD to ground the rewrite.

2. **Resume Tailoring**
   - Extracts keywords from the JD.
   - Rewrites your base resume text to emphasize matching skills and impact aligned to the JD.
   - Saves the output as a **.docx** file in the `output/` folder.

3. **Auto‑Apply (Optional)**
   - Uses **Playwright** (Chromium) to navigate to a job application URL and populate common fields.
   - Keeps a configurable headless mode for CI or local control via `HEADLESS`.

---

## Project Structure

```
app.py                  # Entry point: prompts for JD text/URL, triggers RAG + rewrite + optional auto-apply
__init__.py             # setup_rag_system() and retrieve_answer() wiring
ingest.py               # Loads PDFs/CSVs from data/, extracts text, calls chunking/embeddings, stores in FAISS
chunking.py             # Chunking utilities for PDFs/CSVs
embeddings.py           # SentenceTransformer model ('all-MiniLM-L6-v2') to encode chunks
retrieval.py            # FAISSVectorStore wrapper: add/search, keep metadata per chunk
llm_utils.py            # OpenAI client helpers: extract JD keywords, LLM rewrite, save .docx
requirements.txt        # Python dependencies
dockerfile              # Container build: installs deps and Chromium for Playwright
docker-compose.yml      # Runs container, maps ./output, sets HEADLESS/OUTPUT_DIR
```

> Notes
> - The app assumes a `data/` directory at the repo root containing PDFs/CSVs you want to use as grounding material.
> - The final tailored resume is written to `output/tailored_resume.docx`.

---

## Prerequisites

- Python 3.11+
- An OpenAI API key
- For local Playwright runs: Chromium and dependencies. The Docker path installs these for you inside the image.

---

## Quick Start (Local)

1. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Playwright Chromium**
   ```bash
   python -m playwright install chromium
   ```

4. **Create an `.env` file**
   ```env
   OPENAI_API_KEY=sk-...
   HEADLESS=1               # 1=headless, 0=show browser
   OUTPUT_DIR=output
   ```

5. **Add your grounding data**
   - Create a `data/` folder.
   - Drop in relevant PDFs (projects, reports, certificates) and CSVs (skills matrices, accomplishments).

6. **Run**
   ```bash
   python app.py
   ```
   The script will prompt for:
   - `JD_TEXT` (paste the job description) or it will read it from your `.env` if set.
   - `JOB_URL` (the application URL) for auto‑apply. Leave empty to skip.

7. **Result**
   - The tailored resume is saved to `output/tailored_resume.docx`.

---

## Quick Start (Docker)

Build the image:
```bash
docker build -t ai-powered-resume-tailor .
```

Run with Compose (recommended):
```bash
docker compose up --build
```
Compose sets:
- `HEADLESS=1`
- `OUTPUT_DIR=/app/output`
- Binds local `./output` to `/app/output` so the resume appears on your host.

You can also pass environment at run time:
```bash
JD_TEXT="$(pbpaste)" JOB_URL="https://..." docker compose up --build
```
Or with plain Docker:
```bash
docker run --rm -it   --env-file .env   -e JD_TEXT="$(pbpaste)"   -e JOB_URL="https://..."   -v "$(pwd)/output:/app/output"   -p 8000:8000   ai-powered-resume-tailor
```

---

## Configuration

Environment variables:

| Name            | Required | Default | Description                                              |
|-----------------|----------|---------|----------------------------------------------------------|
| `OPENAI_API_KEY`| Yes      | —       | OpenAI key used by `llm_utils.py`                        |
| `HEADLESS`      | No       | `1`     | `1` to run Playwright headless, `0` to show the browser  |
| `OUTPUT_DIR`    | No       | `output`| Where the .docx is written                               |
| `JD_TEXT`       | No       | —       | If provided, used instead of interactive prompt          |
| `JOB_URL`       | No       | —       | Application URL to auto‑apply. Leave empty to skip       |

---

## How it Works (RAG Pipeline)

1. **Ingestion** (`ingest.py`)
   - Reads PDFs via `PyPDF2` and CSVs via `pandas`.
   - Produces clean text payloads.

2. **Chunking** (`chunking.py`)
   - Splits long text into word‑bounded chunks.
   - For CSVs: per‑row or grouped chunks.

3. **Embeddings** (`embeddings.py`)
   - Encodes chunks with `sentence-transformers` model `all-MiniLM-L6-v2`.
   - Stores `[{"chunk", "embedding"}]` per file.

4. **Vector Store** (`retrieval.py`)
   - Adds vectors to FAISS index and keeps metadata.
   - Nearest‑neighbor search returns top‑k chunks with distances.

5. **LLM Orchestration** (`llm_utils.py`, `__init__.py`)
   - Extracts JD keywords.
   - Rewrites resume text, grounding on retrieved chunks.
   - Exports the final resume to `.docx`.

6. **Automation** (`app.py`)
   - Optionally opens a Chromium page and fills common ATS fields using flexible selectors.
   - Honors `HEADLESS` for CI and scripting.

---

## Troubleshooting

- **Playwright timeouts or blank pages**  
  Increase timeouts or set `HEADLESS=0` to observe UI. Ensure `python -m playwright install chromium` has run locally.

- **`/dev/shm` issues inside Docker**  
  `docker-compose.yml` sets `shm_size: "1g"`. Increase if pages crash in Chromium.

- **FAISS dimension errors**  
  Ensure embeddings are generated before searching. Verify your `data/` folder has readable PDFs/CSVs.

- **No output file**  
  Check `OUTPUT_DIR` and file permissions. The app should create `output/` automatically.

---

## Roadmap Ideas

- Expose a minimal REST API with FastAPI for browser‑based control.
- Add cover‑letter generation grounded by the same RAG store.
- Add scoring for JD‑resume match and keyword coverage.
- Support additional file types (DOCX parsing for base resumes).

---

## License

MIT (or your preferred license).

