import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from __init__ import setup_rag_system, retrieve_answer
from llm_utils import extract_keywords_from_jd, rewrite_resume, save_resume_to_docx

if __name__ == "__main__":
    setup_rag_system()  # Initialize FAISS and store embeddings

    jd_text = input("Paste job description: ")
    if not jd_text.strip():
        print("No job description provided. Exiting.")
        sys.exit(0)

    # Step 1: Extract keywords
    print("\n🔍 Extracting keywords from JD...")
    keywords = extract_keywords_from_jd(jd_text)
    print(f"🎯 Extracted Keywords: {keywords}")

    # Step 2: Search resume chunks with keywords
    print("\n📂 Retrieving relevant resume sections...")
    results = retrieve_answer(keywords)

    if not results:
        print("⚠️ No relevant chunks found.")
        sys.exit(0)

    # Combine chunks
    resume_text = "\n\n".join([res['chunk'] for res in results])

    # Step 3: Rewrite resume
    print("\n✏️ Tailoring resume to JD...")
    tailored_resume = rewrite_resume(resume_text, jd_text)

    # Step 4: Show output
    print("\n📝 Tailored Resume:\n")
    print(tailored_resume)

    # Step 5: Save to file
    save_resume_to_docx(tailored_resume)

    from playwright.sync_api import sync_playwright

    def auto_apply_job(job_url, resume_path):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.fill('input[firstname="name"]',"Naveen Chaitanya")
            
            page.fill('input[lastname="name"]',"kancharla")
            page.fill('input[number="phone]',"5134137242")
            

            page.fill('input[type="file"]', resume_path)
            print(f"✅ Application submitted for {job_url}")
        browser.close()

            