
from src.hr_assistant.retrieval.pipeline.retrieval_pipeline import (
    HRRetrievalPipeline,
)


class MockDenseRetriever:

    def search(self, query, top_k=10):
        return []


def main():

    # 1. Synthetic parent documents with different access levels
    parents = {
        "parent_001": {
            "chunk_id": "parent_001",
            "policy_title": "Leave Policy",
            "text": "Employees can apply for leave.",
            "page_start": 1,
            "page_end": 2,
            "access_level": "public",
        },
        "parent_002": {
            "chunk_id": "parent_002",
            "policy_title": "Manager Guidelines",
            "text": "Managers can approve leave.",
            "page_start": 3,
            "page_end": 4,
            "access_level": "manager",
        },
        "parent_003": {
            "chunk_id": "parent_003",
            "policy_title": "Confidential HR Policy",
            "text": "Confidential HR information.",
            "page_start": 5,
            "page_end": 6,
            "access_level": "hr",
        },
        "parent_004": {
            "chunk_id": "parent_004",
            "policy_title": "Missing Access Policy",
            "text": "This document has no access level.",
            "page_start": 7,
            "page_end": 8,
        },
        "parent_005": {
            "chunk_id": "parent_005",
            "policy_title": "Invalid Access Policy",
            "text": "This document has an invalid access level.",
            "page_start": 9,
            "page_end": 10,
            "access_level": "restricted",
        },
    }

    # 2. Generate one child for each parent
    children = []

    for parent_id, parent in parents.items():

        children.append({
            "chunk_id": f"child_{parent_id}",
            "parent_chunk_id": parent_id,
            "text": parent["text"],
        })

    # 3. Initialize actual retrieval pipeline
    pipeline = HRRetrievalPipeline(
        dense_retriever=MockDenseRetriever(),
        children=children,
        parents=parents,
        use_reranking=False,
    )

    # 4. Replace hybrid retrieval with deterministic synthetic results
    pipeline.hybrid_retriever.search = lambda **kwargs: [
        {
            "chunk": child,
            "rrf_score": 1.0,
        }
        for child in children
    ]

    # 5. Expected authorized parent IDs for each role
    expected_access = {
        "employee": {
            "parent_001",
        },
        "manager": {
            "parent_001",
            "parent_002",
        },
        "hr": {
            "parent_001",
            "parent_002",
            "parent_003",
        },
        "admin": {
            "parent_001",
            "parent_002",
            "parent_003",
        },
        "unknown": set(),
    }

    # 6. Test authorization for every role
    print("\n========== RETRIEVAL AUTHORIZATION TEST ==========")

    for role, expected_ids in expected_access.items():

        result = pipeline.search(
            query="Leave policy",
            user_role=role,
        )

        actual_ids = {
            parent["chunk_id"]
            for parent in result["parent_contexts"]
        }

        print(f"\nRole: {role}")
        print(
            "Original candidates:",
            result["original_candidate_count"],
        )
        print(
            "Authorized candidates:",
            result["authorized_candidate_count"],
        )
        print("Expected parents:", expected_ids)
        print("Actual parents:", actual_ids)

        # Verify exact authorized parent IDs
        assert actual_ids == expected_ids, (
            f"Authorization failure for role {role}: "
            f"expected {expected_ids}, got {actual_ids}"
        )

        # Verify unauthorized documents never reach final contexts
        assert "parent_004" not in actual_ids
        assert "parent_005" not in actual_ids

    print("\nAll retrieval authorization tests passed.")


if __name__ == "__main__":
    main()
