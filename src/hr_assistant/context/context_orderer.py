
class ContextOrderer:

    VALID_STRATEGIES = {
        "relevance_first",
        "relevance_last",
        "lost_middle",
    }

    def order(self, contexts, strategy="relevance_first"):

        if strategy not in self.VALID_STRATEGIES:
            raise ValueError(
                f"Unsupported ordering strategy: {strategy}"
            )

        # Lower retrieval rank means higher relevance.
        ranked_contexts = sorted(
            contexts,
            key=lambda item: item.get("retrieval_rank", float("inf")),
        )

        if strategy == "relevance_first":
            return ranked_contexts

        if strategy == "relevance_last":
            return list(reversed(ranked_contexts))

        if strategy == "lost_middle":

            ordered = []
            left = 0
            right = len(ranked_contexts) - 1

            while left <= right:

                ordered.append(ranked_contexts[left])
                left += 1

                if left <= right:
                    ordered.append(ranked_contexts[right])
                    right -= 1

            return ordered
