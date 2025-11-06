💼 AI-Powered Resume Tailor

An intelligent RAG-based system that automatically customizes your resume for every job posting.

👨🏽‍💻 Overview

AI-Powered Resume Tailor helps job seekers create perfectly matched resumes for specific job descriptions — instantly.
Built using Retrieval-Augmented Generation (RAG), this project analyzes your existing resumes, converts them into vector embeddings, and dynamically tailors a new resume that aligns with the target Job Description (JD) and company requirements.

Simply feed it a job description (or a job URL), and it intelligently tweaks your resume content — highlighting the most relevant experience, keywords, and phrasing — while preserving your personal writing tone.

👁️ Core Features

RAG-based Resume Generation – Uses embeddings to retrieve the most relevant achievements and rewrite them for each job.
Chromium Integration – Automatically extracts job descriptions directly from company websites.
Semantic Resume Matching – Transforms your input resumes into vector representations and finds the closest semantic match.
Smart Rewriting Engine – Rewrites sentences using LLMs to improve clarity and keyword alignment.
Automated Tailoring Loop – Continuously compares the resume–JD similarity and refines output until an optimal match is reached.
Data Privacy – Works locally; your personal data and resumes never leave your machine.

 How It Works

Ingestion → Upload 10–15 of your previous resumes (data/ folder).

Chunking → Breaks each resume into small, meaningful text segments.

Embedding Generation → Converts text into vector representations using OpenAI/Local Embedding models.

Retrieval → Finds the resume chunks most semantically similar to the new JD.

LLM Tailoring → Uses the retrieved chunks and the new JD to generate a custom resume version.

Output → A polished, ATS-optimized resume ready to apply.

🗂️ Project Structure
AI-Powered-Resume-Tailor/
│
├── data/                # Folder containing sample resumes
├── app.py               # Main script to run the application
├── chunking.py          # Splits resumes and JDs into semantic chunks
├── embeddings.py        # Generates embeddings and stores vectors
├── retrieval.py         # Retrieves most relevant resume sections
├── ingest.py            # Handles resume ingestion and preprocessing
├── llm_utils.py         # LLM interface for resume rewriting
├── __init__.py          # Package initializer
└── README.md

⚙️ Tech Stack

Python 3.10+

LangChain – For RAG pipeline orchestration

OpenAI / Hugging Face Embeddings

FAISS / ChromaDB – For vector similarity search

Playwright / Selenium / Chromium – To extract job postings from websites

Streamlit / CLI – Interface for generating resumes

🧪 Example Workflow
# Step 1: Clone the repo
git clone https://github.com/NaveenKancharla28/AI-Powered-Resume-Tailor.git
cd AI-Powered-Resume-Tailor

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the app
python app.py


You’ll be prompted to enter:

Job Description (paste text or job URL)

Base Resume Folder (path to your existing resumes)

The app will generate a new, custom-tailored resume under /output.

🧭 Future Improvements

⏭️ Integrate with LinkedIn job scraper for automatic JD extraction

⏭️ Add feedback scoring system (match %, keyword density)

⏭️ Support for multi-language resumes

⏭️ Build UI dashboard using Streamlit




🧑‍💻 Author

Naveen Kancharla
AI/ML Engineer | Building RAG-powered tools and intelligent automation
🌐 [Portfolio](https://naveenflix.vercel.app/)
 | 💻 [GitHub](https://github.com/NaveenKancharla28)
 | ✉️ [LinkedIn https://www.linkedin.com/in/naveen-chaitanya-kancharla-358337238/](https://www.linkedin.com/in/naveen-chaitanya-kancharla-358337238/)
