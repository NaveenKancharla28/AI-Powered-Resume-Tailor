import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from __init__ import setup_rag_system, retrieve_answer
from llm_utils import extract_keywords_from_jd, rewrite_resume, save_resume_to_docx
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json

# User profile data (can be moved to a config file later)
USER_PROFILE = {
    "first_name": "First name",#Enter Your First Name
    "last_name": "Last name",#Enter your Last name
    "phone": "5123456789",#Enter mobile number
    "email": "you@exmaple.com",#Enter your mail
    "address": "123 Main St, Cincinnati, OH 45202",#Enter your address
    "linkedin": "https://www.linkedin.com/in/sample",#Enter your linkdin profile
}

def auto_apply_job(job_url, resume_path):
    """
    Automatically fill out job application forms using Playwright and allow user review before submission.
    Supports common ATS platforms and LinkedIn.
    """
    print(f"🚀 Starting application process for {job_url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Keep headless=False to show browser
        page = browser.new_page()
        
        try:
            # Navigate to the job application URL
            page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            print(f"📄 Navigated to {job_url}")

            # Wait for form elements to load
            page.wait_for_selector("form", timeout=10000)

            # Common field selectors for various platforms
            field_mappings = [
                # First Name
                {"selector": 'input[name*="first"][name*="name"], input[id*="first"][id*="name"], input[placeholder*="First Name"]', "value": USER_PROFILE["first_name"]},
                # Last Name
                {"selector": 'input[name*="last"][name*="name"], input[id*="last"][id*="name"], input[placeholder*="Last Name"]', "value": USER_PROFILE["last_name"]},
                # Email
                {"selector": 'input[type="email"], input[name*="email"], input[id*="email"], input[placeholder*="Email"]', "value": USER_PROFILE["email"]},
                # Phone
                {"selector": 'input[type="tel"], input[name*="phone"], input[id*="phone"], input[placeholder*="Phone"]', "value": USER_PROFILE["phone"]},
                # Address
                {"selector": 'input[name*="address"], input[id*="address"], input[placeholder*="Address"]', "value": USER_PROFILE["address"]},
                # LinkedIn Profile
                {"selector": 'input[name*="linkedin"], input[id*="linkedin"], input[placeholder*="LinkedIn"]', "value": USER_PROFILE["linkedin"]},
            ]

            # Fill text fields
            for field in field_mappings:
                try:
                    elements = page.query_selector_all(field["selector"])
                    for element in elements:
                        element.fill(field["value"])
                        print(f"✅ Filled field matching {field['selector']} with {field['value']}")
                except Exception as e:
                    print(f"⚠️ Could not fill field {field['selector']}: {str(e)}")

            # Handle file upload for resume
            try:
                file_input = page.query_selector('input[type="file"]')
                if file_input:
                    file_input.set_input_files(resume_path)
                    print(f"📎 Uploaded resume: {resume_path}")
                else:
                    print("⚠️ No file upload field found.")
            except Exception as e:
                print(f"⚠️ Error uploading resume: {str(e)}")

            # Pause for user review
            print("\n📋 Application form filled. The browser is open for you to review the form.")
            print("Please check the form in the browser window.")
            user_input = input("Type 'submit' to submit the application, or 'cancel' to abort: ").strip().lower()

            if user_input == 'submit':
                # Attempt to submit the form
                try:
                    submit_button = page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Apply")')
                    if submit_button:
                        submit_button.click()
                        print(f"✅ Application submitted for {job_url}")
                    else:
                        print("⚠️ No submit button found. Manual submission may be required.")
                except Exception as e:
                    print(f"⚠️ Error submitting form: {str(e)}")
            else:
                print("🚫 Application cancelled by user.")

        except PlaywrightTimeoutError:
            print(f" Timeout error while processing {job_url}. Page may not have loaded correctly.")
        except Exception as e:
            print(f"❌ Error processing {job_url}: {str(e)}")
        finally:
            print("\n Closing browser. If you cancelled, you can manually submit the form in the browser before it closes.")
            browser.close()

if __name__ == "__main__":
    setup_rag_system()  # Initialize FAISS and store embeddings

    # Input for job description and URL
    jd_text = input("Paste job description: ")
    job_url = input("Paste job application URL: ")

    if not jd_text.strip():
        print("No job description provided. Exiting.")
        sys.exit(0)

    if not job_url.strip():
        print("No job application URL provided. Exiting.")
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
    resume_path = "tailored_resume.docx"
    save_resume_to_docx(tailored_resume, resume_path)

    # Step 6: Auto-apply to job
    print("\n🤖 Auto-applying to job...")
    auto_apply_job(job_url, resume_path)