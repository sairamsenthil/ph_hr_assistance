class TokenBudgetManager:

    def __init__(self, tokenizer):

        self.tokenizer = tokenizer

    def count_tokens(self, text):

        return len(
            self.tokenizer.encode(
                text,
                add_special_tokens=False
            ).ids
        )

    def fit_contexts(self, contexts, token_budget):

        if token_budget <= 0:
            raise ValueError("Token budget must be positive")

        selected_contexts = []
        excluded_contexts = []

        final_context = ""

        for context in contexts:

            candidate_contexts = (
                selected_contexts + [context]
            )

            candidate_text = "\n\n".join(
                candidate_contexts
            )

            candidate_token_count = self.count_tokens(
                candidate_text
            )

            if candidate_token_count <= token_budget:

                selected_contexts.append(context)
                final_context = candidate_text

            else:

                excluded_contexts.append(context)

        return {
            "context": final_context,
            "selected_contexts": selected_contexts,
            "excluded_contexts": excluded_contexts,
            "token_count": self.count_tokens(final_context),
            "token_budget": token_budget,
            "remaining_tokens": (
                token_budget - self.count_tokens(final_context)
            ),
            "selected_count": len(selected_contexts),
            "excluded_count": len(excluded_contexts),
            "budget_status": (
                "within_budget"
                if self.count_tokens(final_context) <= token_budget
                else "exceeded"
            )
        }