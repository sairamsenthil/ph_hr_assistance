
from src.hr_assistant.context.context_deduplicator import (
    ContextDeduplicator,
)

from src.hr_assistant.context.token_budget_manager import (
    TokenBudgetManager,
)

from src.hr_assistant.context.context_orderer import (
    ContextOrderer,
)


class ContextBuilder:

    def __init__(
        self,
        tokenizer,
        ordering_strategy="relevance_first",
    ):

        self.deduplicator = ContextDeduplicator()
        self.token_budget_manager = TokenBudgetManager(tokenizer)
        self.context_orderer = ContextOrderer()

        self.ordering_strategy = ordering_strategy

    def build(self, retrieval_output, token_budget):

        query = retrieval_output["query"]
        parent_contexts = retrieval_output["parent_contexts"]

        # 1. Order retrieved parent contexts
        ordered_contexts = self.context_orderer.order(
            contexts=parent_contexts,
            strategy=self.ordering_strategy,
        )
        formatted_contexts = []
        sources = []
        seen_source_ids = set()

        original_paragraph_count = 0
        unique_paragraph_count = 0
        duplicates_removed = 0

        # 2. Deduplicate and format each ordered source
        for parent in ordered_contexts:

            chunk_id = parent["chunk_id"]

            # Skip duplicate parent chunks
            if chunk_id in seen_source_ids:
                continue

            seen_source_ids.add(chunk_id)

            index = len(sources) + 1

            policy_title = parent["policy_title"]
            page_start = parent["page_start"]
            page_end = parent["page_end"]
            chunk_id = parent["chunk_id"]
            text = parent["text"]

            deduplication_output = self.deduplicator.deduplicate(
                text
            )

            cleaned_text = deduplication_output["context"]

            original_paragraph_count += (
                deduplication_output["original_paragraph_count"]
            )

            unique_paragraph_count += (
                deduplication_output["unique_paragraph_count"]
            )

            duplicates_removed += (
                deduplication_output["duplicates_removed"]
            )

            formatted_context = (
                f"[SOURCE {index}]\n"
                f"Policy: {policy_title}\n"
                f"Pages: {page_start}-{page_end}\n"
                f"Content:\n{cleaned_text}"
            )

            formatted_contexts.append(formatted_context)
            sources.append({
                "source_index": index,
                "source_id": chunk_id,
                "policy_title": policy_title,
                "page_start": page_start,
                "page_end": page_end,
                "source_text": cleaned_text,
                "retrieval_rank": parent.get("retrieval_rank"),
                "rerank_score": parent.get("rerank_score"),
                "rrf_score": parent.get("rrf_score"),
                "ranking_method": parent.get("ranking_method"),
            })

        # 3. Apply token budget to complete source blocks
        budget_output = self.token_budget_manager.fit_contexts(
            contexts=formatted_contexts,
            token_budget=token_budget,
        )

        selected_contexts = budget_output["selected_contexts"]

        # 4. Keep source metadata aligned with selected blocks
        selected_source_indexes = {
            int(
                context.split("\n", 1)[0]
                .replace("[SOURCE ", "")
                .replace("]", "")
            )
            for context in selected_contexts
        }

        selected_sources = [
            source
            for index, source in enumerate(sources, start=1)
            if index in selected_source_indexes
        ]

        final_context = budget_output["context"]

        # 5. Return final context and metadata
        return {
            "query": query,
            "context": final_context,
            "sources": selected_sources,
            "source_count": len(selected_sources),

            "ordering_strategy": self.ordering_strategy,

            "original_paragraph_count": original_paragraph_count,
            "unique_paragraph_count": unique_paragraph_count,
            "duplicates_removed": duplicates_removed,

            "token_count": budget_output["token_count"],
            "token_budget": budget_output["token_budget"],
            "remaining_tokens": budget_output["remaining_tokens"],
            "selected_count": budget_output["selected_count"],
            "excluded_count": budget_output["excluded_count"],
            "budget_status": budget_output["budget_status"],

            "context_status": (
                "ready" if final_context.strip() else "empty"
            ),
        }
