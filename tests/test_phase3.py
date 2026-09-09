import unittest

from gap_analysis import analyze_gaps
from resume_diff import build_resume_diff, explain_changes, summarize_changes


class Phase3Tests(unittest.TestCase):
    def setUp(self):
        self.jd = {
            "required_skills": ["Python", "Azure ML"],
            "preferred_skills": ["Docker"],
            "frameworks_tools": ["FastAPI"],
            "cloud_platforms": [],
            "genai_ml_concepts": [],
        }

    def test_gap_analysis_identifies_strong_partial_and_missing(self):
        evidence = [
            {"filename": "resume.pdf", "chunk": "Built Python APIs with FastAPI and deployed machine learning models."},
            {"filename": "project.pdf", "chunk": "Worked with Azure services for cloud deployments."},
        ]
        result = analyze_gaps(self.jd, evidence)
        statuses = {item["requirement"]: item["status"] for item in result["items"]}
        self.assertEqual(statuses["Python"], "strong")
        self.assertEqual(statuses["FastAPI"], "strong")
        self.assertEqual(statuses["Azure ML"], "partial")
        self.assertEqual(statuses["Docker"], "missing")
        self.assertEqual(result["summary"]["partial"], 1)

    def test_gap_analysis_explains_missing_requirement(self):
        result = analyze_gaps(self.jd, [])
        azure = next(item for item in result["items"] if item["requirement"] == "Azure ML")
        self.assertEqual(azure["status"], "missing")
        self.assertIn("No relevant career evidence", azure["explanation"])

    def test_resume_diff_reports_added_and_removed_lines(self):
        original = "Python\nSQL\nTableau"
        tailored = "Python\nFastAPI\nSQL\nTableau"
        changes = build_resume_diff(original, tailored)
        self.assertIn({"type": "added", "text": "FastAPI"}, changes)
        summary = summarize_changes(original, tailored)
        self.assertEqual(summary["added"], 1)
        self.assertEqual(summary["removed"], 0)

    def test_resume_diff_detects_replacement(self):
        changes = build_resume_diff("Built Python scripts", "Built Python APIs")
        self.assertIn({"type": "removed", "text": "Built Python scripts"}, changes)
        self.assertIn({"type": "added", "text": "Built Python APIs"}, changes)

    def test_change_explanation_traces_requirement(self):
        changes = [{"type": "added", "text": "Built production FastAPI services"}]
        explanations = explain_changes(changes, ["FastAPI", "Python"])
        self.assertIn("FastAPI", explanations[0]["matched_requirements"])


if __name__ == "__main__":
    unittest.main()
