
def reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    scores = {}
    source_ranks = {}

    for ranked_list in ranked_lists:
        seen = set()

        for rank, chunk_id in enumerate(ranked_list, start=1):
            if chunk_id in seen:
                continue

            seen.add(chunk_id)

            scores[chunk_id] = (
                scores.get(chunk_id, 0.0)
                + 1 / (k + rank)
            )

            source_ranks.setdefault(chunk_id, []).append(rank)

    ranked_results = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        {
            "chunk_id": chunk_id,
            "rrf_score": score,
            "source_ranks": source_ranks[chunk_id],
        }
        for chunk_id, score in ranked_results[:top_k]
    ]
