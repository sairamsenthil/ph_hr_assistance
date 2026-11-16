

class ContextSufficiencyEvaluator:

    def evaluate(self, context_output):

        issues = []

        query = context_output.get("query", "")
        context = context_output.get("context", "")
        sources = context_output.get("sources", [])

        context_status = context_output.get("context_status")
        budget_status = context_output.get("budget_status")

        token_count = context_output.get("token_count", 0)
        token_budget = context_output.get("token_budget", 0)
        excluded_count = context_output.get("excluded_count", 0)

        # 1. Query validation
        if not isinstance(query, str) or not query.strip():
            issues.append("missing_query")

        # 2. Context validation
        if not isinstance(context, str) or not context.strip():
            issues.append("empty_context")

        # 3. Source validation
        if not isinstance(sources, list) or not sources:
            issues.append("missing_sources")

        # 4. Context status
        if context_status != "ready":
            issues.append("context_not_ready")

        # 5. Token budget validation
        if budget_status != "within_budget":
            issues.append("token_budget_not_respected")

        if (
            not isinstance(token_count, int)
            or not isinstance(token_budget, int)
            or token_count < 0
            or token_budget <= 0
            or token_count > token_budget
        ):
            issues.append("invalid_token_budget_metadata")

        return {
            "query": query,
            "answerable": len(issues) == 0,
            "sufficiency_status": (
                "preliminary_sufficient"
                if not issues
                else "insufficient"
            ),
            "issues": issues,
            "source_count": len(sources) if isinstance(sources, list) else 0,
            "context_token_count": token_count,
            "excluded_count": excluded_count,
        }
