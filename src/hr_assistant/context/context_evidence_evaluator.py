
class ContextEvidenceEvaluator:

    def evaluate(self, context, required_evidence):

        if not isinstance(context, str):
            raise ValueError("Context must be a string.")

        if not isinstance(required_evidence, list):
            raise ValueError("required_evidence must be a list.")

        if not required_evidence:
            raise ValueError("required_evidence cannot be empty.")

        normalized_context = " ".join(
            context.casefold().split()
        )

        matched_evidence = []
        missing_evidence = []

        for evidence in required_evidence:

            if not isinstance(evidence, str) or not evidence.strip():
                continue

            normalized_evidence = " ".join(
                evidence.casefold().split()
            )

            if normalized_evidence in normalized_context:
                matched_evidence.append(evidence)
            else:
                missing_evidence.append(evidence)

        total = len(matched_evidence) + len(missing_evidence)

        coverage = (
            len(matched_evidence) / total
            if total
            else 0.0
        )

        return {
            "total_evidence": total,
            "matched_count": len(matched_evidence),
            "missing_count": len(missing_evidence),
            "coverage": coverage,
            "matched_evidence": matched_evidence,
            "missing_evidence": missing_evidence,
            "evidence_complete": (
                total > 0 and len(missing_evidence) == 0
            ),
        }
