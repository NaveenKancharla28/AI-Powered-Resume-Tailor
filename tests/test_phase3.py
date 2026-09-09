import unittest

from gap_analysis import analyze_gaps
from resume_diff import build_resume_diff, summarize_changes


class Phase3Tests(unittest.TestCase):
    def test_gap_analysis_identifies_strong_partial_and_missing(self):
        jd = {
            "required_skills": ["Python", "Azure ML", "REST APIs"],
            "preferred_skills": ["Docker"],
            "frameworks_tools": ["FastAPI"],
            "cloud_platforms": [],
            "genai_ml_concepts": [],
        }
        evidence = [
            {"filename": "resume.pdf", "chunk": "Built Python APIs with FastAPI."},
            {"filename": "project.pdf", "chunk": "Built API services for internal applications."},
        ]
        result = analyze_gaps(jd, evidence)
        statuses = {item["requirement"]: item["status"] for item in result["items"]}
        self.assertEqual(statuses["Python"], "strong")
        self.assertEqual(statuses["FastAPI"], "strong")
        self.assertEqual(statuses["Azure ML"], "missing")
        self.assertEqual(statuses["REST APIs"], "partial")
        self.assertEqual(result["summary"]["total"], 5)

    def test_resume_diff_reports_added_and_removed_lines(self):
        original = "Python\nSQL\nTableau"
        tailored = "Python\nFastAPI\nSQL\nTableau"
        changes = build_resume_diff(original, tailored)
        self.assertIn({"type": "added", "text": "FastAPI", "line": "2"}, changes)
        summary = summarize_changes(original, tailored)
        self.assertEqual(summary["added"], 1)
        self.assertEqual(summary["removed"], 0)

    def test_resume_diff_normalizes_whitespace_and_case(self):
        original = "Python   Developer"
        tailored = "python developer"
        self.assertEqual(build_resume_diff(original, tailored), [])


if __name__ == "__main__":
    unittest.main()
