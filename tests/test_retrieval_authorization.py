import unittest
from unittest.mock import Mock

from src.hr_assistant.retrieval.pipeline.retrieval_pipeline import (
    HRRetrievalPipeline,
)


class MockReranker:

    def __init__(self):
        self.received_parent_ids = []

    def rerank(self, query, candidates, top_k=5):
        self.received_parent_ids = [
            item["chunk"]["parent_chunk_id"]
            for item in candidates
        ]
        return candidates[:top_k]


class TestRetrievalAuthorization(unittest.TestCase):

    def setUp(self):

        self.parents = {
            "parent_001": {
                "chunk_id": "parent_001",
                "access_level": "public",
                "text": "Employee leave policy.",
            },
            "parent_002": {
                "chunk_id": "parent_002",
                "access_level": "manager",
                "text": "Manager approval guidelines.",
            },
            "parent_003": {
                "chunk_id": "parent_003",
                "access_level": "hr",
                "text": "Confidential HR guidelines.",
            },
            "parent_004": {
                "chunk_id": "parent_004",
                "access_level": "admin",
                "text": "Administrator guidelines.",
            },
            "parent_005": {
                "chunk_id": "parent_005",
                "text": "Missing access level.",
            },
            "parent_006": {
                "chunk_id": "parent_006",
                "access_level": "restricted",
                "text": "Invalid access level.",
            },
        }

        self.children = [
            {
                "chunk_id": f"child_{parent_id}",
                "parent_chunk_id": parent_id,
                "text": parent["text"],
            }
            for parent_id, parent in self.parents.items()
        ]

        self.candidates = [
            {
                "chunk": child,
                "rrf_score": 1.0,
            }
            for child in self.children
        ]

        # Disable real model initialization.
        self.pipeline = HRRetrievalPipeline(
            dense_retriever=Mock(),
            children=self.children,
            parents=self.parents,
            use_reranking=False,
        )

        self.pipeline.hybrid_retriever.search = Mock(
            return_value=self.candidates
        )

        self.mock_reranker = MockReranker()
        self.pipeline.use_reranking = True
        self.pipeline.reranker = self.mock_reranker

    def test_employee_only_receives_public_documents(self):

        result = self.pipeline.search(
            query="Leave policy",
            user_role="employee",
        )

        expected = {"parent_001"}

        actual = {
            item["chunk_id"]
            for item in result["parent_contexts"]
        }

        self.assertEqual(actual, expected)

    def test_manager_receives_public_and_manager_documents(self):

        result = self.pipeline.search(
            query="Leave policy",
            user_role="manager",
        )

        expected = {"parent_001", "parent_002"}

        actual = {
            item["chunk_id"]
            for item in result["parent_contexts"]
        }

        self.assertEqual(actual, expected)

    def test_hr_receives_public_manager_and_hr_documents(self):

        result = self.pipeline.search(
            query="Leave policy",
            user_role="hr",
        )

        expected = {
            "parent_001",
            "parent_002",
            "parent_003",
        }

        actual = {
            item["chunk_id"]
            for item in result["parent_contexts"]
        }

        self.assertEqual(actual, expected)

    def test_admin_receives_all_configured_access_levels(self):

        result = self.pipeline.search(
            query="Leave policy",
            user_role="admin",
        )

        expected = {
            "parent_001",
            "parent_002",
            "parent_003",
            "parent_004",
        }

        actual = {
            item["chunk_id"]
            for item in result["parent_contexts"]
        }

        self.assertEqual(actual, expected)

    def test_unknown_role_receives_no_documents(self):

        result = self.pipeline.search(
            query="Leave policy",
            user_role="unknown",
        )

        self.assertEqual(result["parent_contexts"], [])
        self.assertEqual(result["retrieved_chunks"], [])
        self.assertEqual(result["authorized_candidate_count"], 0)

    def test_unauthorized_candidates_never_reach_reranker(self):

        self.pipeline.search(
            query="Leave policy",
            user_role="employee",
        )

        self.assertEqual(
            set(self.mock_reranker.received_parent_ids),
            {"parent_001"},
        )

        self.assertNotIn(
            "parent_002",
            self.mock_reranker.received_parent_ids,
        )

        self.assertNotIn(
            "parent_003",
            self.mock_reranker.received_parent_ids,
        )

        self.assertNotIn(
            "parent_004",
            self.mock_reranker.received_parent_ids,
        )

    def test_unauthorized_documents_never_reach_retrieval_output(self):

        result = self.pipeline.search(
            query="Leave policy",
            user_role="employee",
        )

        returned_parent_ids = {
            item["chunk"]["parent_chunk_id"]
            for item in result["retrieved_chunks"]
        }

        self.assertEqual(returned_parent_ids, {"parent_001"})

    def test_missing_and_invalid_access_levels_are_denied(self):

        result = self.pipeline.search(
            query="Leave policy",
            user_role="admin",
        )

        returned_parent_ids = {
            item["chunk"]["parent_chunk_id"]
            for item in result["retrieved_chunks"]
        }

        self.assertNotIn("parent_005", returned_parent_ids)
        self.assertNotIn("parent_006", returned_parent_ids)


if __name__ == "__main__":
    unittest.main()
