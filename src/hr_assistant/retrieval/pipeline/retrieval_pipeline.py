
from src.hr_assistant.retrieval.hybrid import HybridRetriever
from src.hr_assistant.retrieval.reranking import CrossEncoderReranker
from src.hr_assistant.security.document_access_control import (
    DocumentAccessControl,
)

class HRRetrievalPipeline:

    def __init__(
        self,
        dense_retriever,
        children,
        parents,
        use_reranking=True,
    ):

        self.children = children
        self.parents = parents
        self.use_reranking = use_reranking
        self.access_control = DocumentAccessControl()

        self.hybrid_retriever = HybridRetriever(
            dense_retriever=dense_retriever,
            children=children,
        )

        self.reranker = (
            CrossEncoderReranker()
            if use_reranking
            else None
        )

    def search(
        self,
        query,
        top_k=5,
        candidate_k=10,
        user_role="employee",
    ):

        # 1. Hybrid Retrieval
        candidates = self.hybrid_retriever.search(
            query=query,
            top_k=candidate_k,
            candidate_k=candidate_k,
        )
        # 2. Authorization Filtering

        original_candidate_count = len(candidates)

        authorized_candidates = []

        for item in candidates:

            parent_id = item["chunk"]["parent_chunk_id"]

            parent = self.parents.get(parent_id)

            if parent is None:
                continue

            if self.access_control.can_access(
                user_role=user_role,
                document_access_level=parent.get("access_level"),
            ):
                authorized_candidates.append(item)

        candidates = authorized_candidates

        # 2. Optional Cross-Encoder Reranking
        if self.use_reranking:

            results = self.reranker.rerank(
                query=query,
                candidates=candidates,
                top_k=top_k,
            )

        else:
            results = candidates[:top_k]

        
        # 3. Retrieve Parent Contexts and Preserve Ranking

        parent_best_results = {}

        for rank, item in enumerate(results, start=1):

            parent_id = item["chunk"]["parent_chunk_id"]

            # First occurrence is the highest-ranked child
            # because results are already ranked.
            if parent_id not in parent_best_results:
                parent_best_results[parent_id] = {
                    "retrieval_rank": rank,
                    "rerank_score": item.get("rerank_score"),
                    "rrf_score": item.get("rrf_score"),
                }

        parent_contexts = []

        for parent_id, ranking_info in parent_best_results.items():
            parent = self.parents.get(parent_id)

            if parent is None:
             continue

        # Final authorization check before exposing parent context
            if not self.access_control.can_access(
                user_role=user_role,
                document_access_level=parent.get("access_level"),
            ):
                continue

            parent_context = parent.copy()

            parent_context.update(ranking_info)

            parent_context["ranking_method"] = (
                "cross_encoder"
                if self.use_reranking
                else "rrf"
            )

            parent_contexts.append(parent_context)

        # 4. Return Retrieval Output

        return {
            "query": query,
            "retrieved_chunks": results,
            "parent_contexts": parent_contexts,
            "retrieval_count": len(results),
            "parent_context_count": len(parent_contexts),
            "reranking_enabled": self.use_reranking,
            "requested_role": user_role,
            "original_candidate_count": original_candidate_count,
            "authorized_candidate_count": len(candidates),
        }

