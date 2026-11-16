import re
from experiments.chunking.parent_child.test_retrieval_evaluation import (
    load_chunks,
    retrieve_children_bm25,
    EVALUATION_DATASET,
)

from experiments.chunking.parent_child.test_bm25_parent_aggregation import (
    aggregate_by_parent,
)


TOP_CHILD_K = 10

QUERY_EXPANSIONS = {
    "complaint": [
        "grievance",
        "concern",
        "formal complaint",
        "workplace grievance",
    ],
    "disciplinary": [
        "misconduct",
        "warning",
        "investigation",
    ],
    "bullying": [
        "harassment",
        "intimidation",
        "victimisation",
    ],
}


def expand_query(query):

    terms = re.findall(r"\b[a-z0-9]+\b", query.lower())

    expanded_terms = list(terms)

    for term in terms:
        expanded_terms.extend(
            QUERY_EXPANSIONS.get(term, [])
        )

    return " ".join(expanded_terms)


def main():

    chunks = load_chunks(
        __import__(
            "experiments.chunking.parent_child.test_retrieval_evaluation",
            fromlist=["CHUNKS_FILE"]
        ).CHUNKS_FILE
    )

    parents = {
        chunk["chunk_id"]: chunk
        for chunk in chunks
        if chunk["chunking_strategy"] == "parent"
    }

    children = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    results = []

    for test_case in EVALUATION_DATASET:

        original_query = test_case["query"]
        expanded_query = expand_query(original_query)

        retrieved_children = retrieve_children_bm25(
            expanded_query,
            children,
            top_k=TOP_CHILD_K,
        )

        ranked_parents = aggregate_by_parent(
            retrieved_children,
            parents,
        )

        expected_policy = test_case["expected_policy"]

        relevant_ranks = [
            rank
            for rank, item in enumerate(ranked_parents, start=1)
            if item["parent"]["policy_title"] == expected_policy
        ]

        reciprocal_rank = (
            1 / relevant_ranks[0]
            if relevant_ranks else 0
        )

        results.append(reciprocal_rank)

        print("\n" + "=" * 65)
        print(f"Original Query: {original_query}")
        print(f"Expanded Query: {expanded_query}")

        print("\nParent Results:")

        for rank, item in enumerate(ranked_parents, start=1):
            parent = item["parent"]

            print(
                f"{rank}. {parent['policy_title']} | "
                f"Score: {item['best_score']:.2f}"
            )

        print(f"\nExpected Policy Rank: {relevant_ranks[0] if relevant_ranks else 'Not found'}")
        print(f"Reciprocal Rank: {reciprocal_rank:.2f}")

    print("\n" + "=" * 65)
    print("QUERY EXPANSION MRR")
    print(f"MRR: {sum(results) / len(results):.2f}")


if __name__ == "__main__":
    main()
