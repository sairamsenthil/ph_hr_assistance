
from experiments.chunking.parent_child.test_retrieval_evaluation import (
    CHUNKS_FILE,
    EVALUATION_DATASET,
    load_chunks,
    retrieve_children_bm25,
)


TOP_CHILD_K = 10
TOP_PARENT_K = 5


def aggregate_by_parent(retrieved_children, parents):

    grouped = {}

    for result in retrieved_children:

        child = result["chunk"]
        parent_id = child["parent_chunk_id"]

        if parent_id not in parents:
            continue

        if parent_id not in grouped:
            grouped[parent_id] = {
                "parent": parents[parent_id],
                "best_score": result["score"],
                "matched_children": [],
            }

        grouped[parent_id]["best_score"] = max(
            grouped[parent_id]["best_score"],
            result["score"],
        )

        grouped[parent_id]["matched_children"].append({
            "chunk_id": child["chunk_id"],
            "score": result["score"],
        })

    return sorted(
        grouped.values(),
        key=lambda item: (
            item["best_score"],
            len(item["matched_children"]),
        ),
        reverse=True,
    )[:TOP_PARENT_K]


def main():

    print("Loading Parent-Child chunks...")

    chunks = load_chunks(CHUNKS_FILE)

    parents = {
        chunk["chunk_id"]: chunk
        for chunk in chunks
        if chunk["chunking_strategy"] == "parent"
    }

    children = [
        chunk
        for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    print(f"Parents loaded: {len(parents)}")
    print(f"Children loaded: {len(children)}")

    evaluation_results = []

    for test_case in EVALUATION_DATASET:

        query = test_case["query"]
        expected_policy = test_case["expected_policy"]

        print("\n" + "=" * 65)
        print(f"Query: {query}")
        print(f"Expected Policy: {expected_policy}")

        retrieved_children = retrieve_children_bm25(
            query,
            children,
            top_k=TOP_CHILD_K,
        )

        ranked_parents = aggregate_by_parent(
            retrieved_children,
            parents,
        )

        print("\n--- CHILD RETRIEVAL ---")
        print(f"Child candidates: {len(retrieved_children)}")

        print("\n--- RANKED PARENT RESULTS ---")

        relevant_ranks = []

        for rank, result in enumerate(ranked_parents, start=1):

            parent = result["parent"]

            is_relevant = (
                parent["policy_title"] == expected_policy
            )

            if is_relevant:
                relevant_ranks.append(rank)

            print(f"\nRank: {rank}")
            print(f"Parent ID: {parent['chunk_id']}")
            print(f"Policy: {parent['policy_title']}")
            print(f"Best Child Score: {result['best_score']:.2f}")
            print(
                f"Matched Children: "
                f"{len(result['matched_children'])}"
            )
            print(
                "Child IDs: "
                + ", ".join(
                    item["chunk_id"]
                    for item in result["matched_children"]
                )
            )

        hit_at_k = int(bool(relevant_ranks))
        precision_at_k = (
            len(relevant_ranks) / TOP_PARENT_K
        )
        reciprocal_rank = (
            1 / relevant_ranks[0]
            if relevant_ranks
            else 0
        )

        evaluation_results.append({
            "hit": hit_at_k,
            "precision": precision_at_k,
            "rr": reciprocal_rank,
        })

        print("\n--- METRICS ---")
        print(f"Hit@{TOP_PARENT_K}: {hit_at_k}")
        print(f"Precision@{TOP_PARENT_K}: {precision_at_k:.2f}")
        print(f"Reciprocal Rank: {reciprocal_rank:.2f}")

    total = len(evaluation_results)

    print("\n" + "=" * 65)
    print("OVERALL PARENT-LEVEL EVALUATION")

    print(
        f"Hit@{TOP_PARENT_K}: "
        f"{sum(r['hit'] for r in evaluation_results) / total:.2f}"
    )

    print(
        f"Precision@{TOP_PARENT_K}: "
        f"{sum(r['precision'] for r in evaluation_results) / total:.2f}"
    )

    print(
        f"MRR: "
        f"{sum(r['rr'] for r in evaluation_results) / total:.2f}"
    )


if __name__ == "__main__":
    main()
