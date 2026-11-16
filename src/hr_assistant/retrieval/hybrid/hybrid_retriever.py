
from src.hr_assistant.retrieval.sparse import (
    retrieve_children_bm25,
)
from src.hr_assistant.retrieval.hybrid.rank_fusion import (
    reciprocal_rank_fusion,
)


class HybridRetriever:

    def __init__(self, dense_retriever, children):
        self.dense_retriever = dense_retriever
        self.children = children

        self.chunk_lookup = {
            chunk["chunk_id"]: chunk
            for chunk in children
        }

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 10,
    ):

        # 1. BM25 retrieval
        bm25_results = retrieve_children_bm25(
            query,
            self.children,
            top_k=candidate_k,
        )

        bm25_ids = [
            item["chunk"]["chunk_id"]
            for item in bm25_results
        ]

        # 2. Dense retrieval
        dense_results = self.dense_retriever.search(
            query=query,
            top_k=candidate_k,
        )

        dense_ids = [
            item["chunk_id"]
            for item in dense_results
        ]

        # 3. Reciprocal Rank Fusion
        fused_results = reciprocal_rank_fusion(
            ranked_lists=[bm25_ids, dense_ids],
            top_k=top_k,
        )

        # 4. Preserve individual retrieval ranks
        bm25_ranks = {
            chunk_id: rank
            for rank, chunk_id in enumerate(bm25_ids, start=1)
        }

        dense_ranks = {
            chunk_id: rank
            for rank, chunk_id in enumerate(dense_ids, start=1)
        }

        # 5. Return complete chunk information
        final_results = []

        for result in fused_results:

            chunk_id = result["chunk_id"]

            final_results.append({
                "chunk": self.chunk_lookup[chunk_id],
                "chunk_id": chunk_id,
                "rrf_score": result["rrf_score"],
                "bm25_rank": bm25_ranks.get(chunk_id),
                "dense_rank": dense_ranks.get(chunk_id),
            })

        return final_results
