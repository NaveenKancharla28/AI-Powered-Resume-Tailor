import os
import sys

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from __init__ import setup_rag_system, retrieve_answer
from ats_scorer import score_job_fit
from evidence import build_evidence_index, evidence_summary
from gap_analysis import analyze_gaps
from jd_parser import parse_job_description
from llm_utils import rewrite_resume, save_resume_to_docx
from resume_diff import build_resume_diff, summarize_changes, explain_changes
from cover_letter import generate_cover_letter

load_dotenv()
HEADLESS = os.getenv("HEADLESS", "1") == "1"
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
USER_PROFILE = {
    "first_name": os.getenv("FIRST_NAME", ""), "last_name": os.getenv("LAST_NAME", ""),
    "phone": os.getenv("PHONE", ""), "email": os.getenv("EMAIL", ""),
    "address": os.getenv("ADDRESS", ""), "linkedin": os.getenv("LINKEDIN", ""),
}


def auto_apply_job(job_url: str, resume_path: str) -> None:
    """Fill common application fields and require explicit user confirmation."""
    if not job_url:
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()
        try:
            page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector("form", timeout=10000)
            field_mappings = [
                ('input[name*="first"][name*="name"], input[id*="first"][id*="name"], input[placeholder*="First Name"]', "first_name"),
                ('input[name*="last"][name*="name"], input[id*="last"][id*="name"], input[placeholder*="Last Name"]', "last_name"),
                ('input[type="email"], input[name*="email"], input[id*="email"], input[placeholder*="Email"]', "email"),
                ('input[type="tel"], input[name*="phone"], input[id*="phone"], input[placeholder*="Phone"]', "phone"),
                ('input[name*="address"], input[id*="address"], input[placeholder*="Address"]', "address"),
                ('input[name*="linkedin"], input[id*="linkedin"], input[placeholder*="LinkedIn"]', "linkedin"),
            ]
            for selector, profile_key in field_mappings:
                value = USER_PROFILE[profile_key]
                if not value:
                    continue
                for element in page.query_selector_all(selector):
                    try:
                        element.fill(value)
                    except Exception:
                        pass
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(resume_path)
            print("Application form filled. Review it in the browser before submission.")
            confirmation = input("Type 'submit' to submit, or 'cancel' to abort: ").strip().lower()
            if confirmation == "submit":
                submit_button = page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Apply")')
                if submit_button:
                    submit_button.click()
                    print("Application submitted.")
                else:
                    print("No submit button found; manual submission required.")
            else:
                print("Application cancelled.")
        except PlaywrightTimeoutError:
            print("Timed out while loading the application page.")
        except Exception as exc:
            print(f"Application error: {exc}")
        finally:
            browser.close()


def _print_ats_report(report: dict, evidence: dict) -> None:
    print("\nATS FIT REPORT")
    print("=" * 48)
    print(f"ATS SCORE: {report['overall_score']}/100")
    print(f"Required Skills: {report['required_skill_coverage']}%")
    print(f"Preferred Skills: {report['preferred_skill_coverage']}%")
    print(f"Technology Match: {report['technology_coverage']}%")
    print(f"Seniority Match: {report['seniority_alignment']}%")
    print("\nVerified matches:")
    for item in report["required_matches"] + report["technology_matches"]:
        print(f"  ✓ {item}")
    if report["missing_requirements"]:
        print("\nMissing / unverified requirements:")
        for item in report["missing_requirements"]:
            print(f"  ⚠ {item}")
    print(f"\nEvidence grounding coverage: {evidence['grounding_coverage']}%")


def _print_gap_report(gap_report: dict) -> None:
    print("\nEXPLAINABLE GAP ANALYSIS")
    print("=" * 48)
    summary = gap_report["summary"]
    print(f"Strong: {summary['strong']} | Partial: {summary['partial']} | Missing: {summary['missing']}")
    for item in gap_report["items"]:
        evidence_count = len(item["evidence"])
        print(f"  {item['status'].upper():7} {item['requirement']} ({evidence_count} evidence chunks)")


def main() -> None:
    jd_text = os.getenv("JD_TEXT") or input("Paste job description: ").strip()
    job_url = os.getenv("JOB_URL") or input("Paste job application URL (optional): ").strip()
    if not jd_text:
        print("No job description provided. Exiting.")
        return

    print("\nSetting up RAG system...")
    setup_rag_system()
    print("\nParsing job description...")
    parsed_jd = parse_job_description(jd_text)
    print(f"Role: {parsed_jd['role_title']}")
    print(f"Required skills: {', '.join(parsed_jd['required_skills']) or 'None identified'}")

    retrieval_query = " ".join(
        parsed_jd["required_skills"] + parsed_jd["preferred_skills"] +
        parsed_jd["frameworks_tools"] + parsed_jd["cloud_platforms"] +
        parsed_jd["genai_ml_concepts"]
    ) or jd_text

    print("\nRetrieving relevant career evidence...")
    results = retrieve_answer(retrieval_query, k=8)
    if not results:
        print("No relevant career evidence found. Exiting without generating a resume.")
        return

    all_requirements = (
        parsed_jd["required_skills"] + parsed_jd["preferred_skills"] +
        parsed_jd["frameworks_tools"] + parsed_jd["cloud_platforms"] +
        parsed_jd["genai_ml_concepts"]
    )
    evidence_index = build_evidence_index(results, all_requirements)
    evidence = evidence_summary(evidence_index)
    report = score_job_fit(parsed_jd, results)
    _print_ats_report(report, evidence)

    gap_report = analyze_gaps(parsed_jd, results)
    _print_gap_report(gap_report)

    resume_text = "\n\n".join(result["chunk"] for result in results)
    print("\nTailoring resume using verified evidence only...")
    tailored_resume = rewrite_resume(
        resume_text, jd_text,
        verified_requirements=evidence["verified"],
        missing_requirements=evidence["unsupported"],
    )
    print("\nTailored Resume:\n")
    print(tailored_resume)

    changes = build_resume_diff(resume_text, tailored_resume)
    explained_changes = explain_changes(changes, all_requirements)
    change_summary = summarize_changes(resume_text, tailored_resume)
    print("\nRESUME CHANGE SUMMARY")
    print("=" * 48)
    print(f"Added: {change_summary['added']} | Removed: {change_summary['removed']} | Total: {change_summary['total']}")
    for change in explained_changes:
        print(f"  {change['type'].upper():7} L{change['line']}: {change['text']}")
        print(f"           Reason: {change['reason']}")

    print("\nGenerating evidence-grounded cover letter...")
    cover_letter = generate_cover_letter(
        jd_text,
        resume_text,
        verified_requirements=evidence["verified"],
        missing_requirements=evidence["unsupported"],
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    resume_path = os.path.join(OUTPUT_DIR, "tailored_resume.docx")
    cover_letter_path = os.path.join(OUTPUT_DIR, "cover_letter.txt")
    diff_path = os.path.join(OUTPUT_DIR, "resume_changes.txt")
    save_resume_to_docx(tailored_resume, resume_path)
    with open(cover_letter_path, "w", encoding="utf-8") as handle:
        handle.write(cover_letter + "\n")
    with open(diff_path, "w", encoding="utf-8") as handle:
        for change in explained_changes:
            handle.write(f"{change['type'].upper()} L{change['line']}: {change['text']}\n")
            handle.write(f"Reason: {change['reason']}\n")

    print(f"\nSaved resume: {resume_path}")
    print(f"Saved cover letter: {cover_letter_path}")
    print(f"Saved change report: {diff_path}")
    if job_url:
        auto_apply_job(job_url, resume_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(130)
