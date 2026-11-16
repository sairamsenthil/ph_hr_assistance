import re
from experiments.chunking.parent_child.test_retrieval_evaluation import (
    CHUNKS_FILE,
    load_chunks,
    retrieve_children_bm25,
    EVALUATION_DATASET,
)

from experiments.chunking.parent_child.test_bm25_parent_aggregation import (
    aggregate_by_parent,
)

from experiments.chunking.parent_child.test_bm25_query_expansion import (
    expand_query,
)


TOP_CHILD_K = 10
TOP_PARENT_K = 5
DISPLAY_TOP_PARENTS = 3


def main():

    chunks = load_chunks(CHUNKS_FILE)

    parents = {
        chunk["chunk_id"]: chunk
        for chunk in chunks
        if chunk["chunking_strategy"] == "parent"
    }

    children = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    print("ANSWER EVIDENCE INSPECTION")
    print("=" * 75)

    for test_case in EVALUATION_DATASET:

        query = test_case["query"]
        expected_policy = test_case["expected_policy"]

        expanded_query = expand_query(query)

        retrieved_children = retrieve_children_bm25(
            expanded_query,
            children,
            top_k=TOP_CHILD_K,
        )

        ranked_parents = aggregate_by_parent(
            retrieved_children,
            parents,
        )

        if query == "How are internal candidates selected for interview?":

                    for rank, item in enumerate(ranked_parents, start=1):

                        parent = item["parent"]

                        if parent["policy_title"] == "Recruitment and Selection":

                            print("\nTOP RELEVANT PARENT")
                            print("Policy:", parent["policy_title"])
                            print("Pages:", parent["page_start"], "-", parent["page_end"])
                            print("Text:\n", parent["text"][:2000])

                            break

        print("\n" + "=" * 75)
        print(f"QUESTION: {query}")
        print(f"EXPECTED POLICY: {expected_policy}")
        print(f"EXPANDED QUERY: {expanded_query}")

        for rank, item in enumerate(
            ranked_parents[:DISPLAY_TOP_PARENTS],
            start=1,
        ):

            parent = item["parent"]

            print("\n" + "-" * 65)
            print(f"RANK: {rank}")
            print(f"PARENT ID: {parent['chunk_id']}")
            print(f"POLICY: {parent['policy_title']}")
            print(
                f"PAGES: {parent['page_start']}-"
                f"{parent['page_end']}"
            )
            print(f"BM25 SCORE: {item['best_score']:.2f}")

            print("\nPARENT TEXT:")
            text = parent["text"]

            matches = re.findall(
                    r"[^.!?\n]*\b(?:internal|interview)\b[^.!?\n]*[.!?]?",
                    text,
                    re.IGNORECASE
                )

            for sentence in matches:
                    print(sentence.strip())
            
    print("\n" + "=" * 75)
    print("EVIDENCE INSPECTION COMPLETED")


if __name__ == "__main__":
    main()
