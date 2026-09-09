import unittest

from ats_scorer import requirement_match, score_job_fit
from evidence import build_evidence_index, evidence_summary


class Phase1Tests(unittest.TestCase):
    def test_alias_matching(self):
        self.assertTrue(requirement_match("Kubernetes", "Deployed services using k8s"))
        self.assertTrue(requirement_match("RAG", "Built a retrieval augmented generation pipeline"))
        self.assertFalse(requirement_match("Azure ML", "Built models with Python and Docker"))

    def test_score_and_missing_requirements(self):
        jd = {
            "required_skills": ["Python", "SQL", "FastAPI"],
            "preferred_skills": ["Kubernetes"],
            "frameworks_tools": ["Docker"],
            "cloud_platforms": ["Azure ML"],
            "genai_ml_concepts": ["RAG"],
            "seniority": "mid-level",
        }
        evidence = [
            {"filename": "experience.txt", "chunk": "Built Python APIs with FastAPI and SQL. Used Docker for deployment. Developed RAG workflows.", "distance": 0.1}
        ]
        report = score_job_fit(jd, evidence)
        self.assertGreater(report["overall_score"], 0)
        self.assertIn("Azure ML", report["missing_requirements"])
        self.assertIn("Python", report["required_matches"])

    def test_evidence_index(self):
        chunks = [{"filename": "career.txt", "chunk": "Python and Docker experience", "distance": 0.2}]
        index = build_evidence_index(chunks, ["Python", "Azure ML"])
        summary = evidence_summary(index)
        self.assertEqual(summary["verified"], ["Python"])
        self.assertEqual(summary["unsupported"], ["Azure ML"])
        self.assertEqual(summary["grounding_coverage"], 50.0)


if __name__ == "__main__":
    unittest.main()
