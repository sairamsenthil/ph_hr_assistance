
class AbstentionController:

    def decide(
        self,
        context_quality,
        claim_grounding=None,
        citation_validation=None,
    ):
        reasons = []

        # 1. Context quality must be present and sufficient.
        if not isinstance(context_quality, dict):
            reasons.append("invalid_context_quality")
        else:
            if context_quality.get("answerable") is not True:
                reasons.append("insufficient_context")

            if context_quality.get("final_status") != "sufficient":
                reasons.append("context_quality_not_sufficient")

        # 2. Claim grounding is mandatory.
        if not isinstance(claim_grounding, dict):
            reasons.append("claim_grounding_missing")
        elif claim_grounding.get("grounded") is not True:
            reasons.append("claim_grounding_failed")

        # 3. Citation validation is mandatory.
        if not isinstance(citation_validation, dict):
            reasons.append("citation_validation_missing")
        elif citation_validation.get("valid") is not True:
            reasons.append("citation_validation_failed")

        should_abstain = bool(reasons)

        return {
            "should_abstain": should_abstain,
            "decision": (
                "abstain"
                if should_abstain
                else "answer"
            ),
            "reasons": reasons,
        }

    def get_abstention_message(self):
        return (
            "I could not find sufficient verified information "
            "in the available HR policies to answer this question "
            "reliably. Please contact Human Resources for clarification."
        )
