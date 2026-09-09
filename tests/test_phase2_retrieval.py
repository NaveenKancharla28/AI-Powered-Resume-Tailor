import unittest

from retrieval import BM25Index


class TestPhase2Retrieval(unittest.TestCase):
    def setUp(self):
        self.documents = [
            {"filename": "resume.pdf", "chunk": "Built Python FastAPI services and deployed machine learning models."},
            {"filename": "resume.pdf", "chunk": "Created Tableau dashboards and SQL reporting pipelines."},
            {"filename": "project.pdf", "chunk": "Implemented a retrieval augmented generation system with vector databases."},
        ]
        self.index = BM25Index(self.documents)

    def test_exact_terms_rank_highly(self):
        results = self.index.search("FastAPI Python machine learning", limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0][0], 0)

    def test_semantically_related_terms_are_not_required_for_bm25(self):
        results = self.index.search("RAG vector databases", limit=3)
        self.assertTrue(results)
        self.assertEqual(results[0][0], 2)

    def test_metadata_filter(self):
        results = self.index.search(
            "Python",
            limit=3,
            filters={"filename": "project.pdf"},
        )
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
