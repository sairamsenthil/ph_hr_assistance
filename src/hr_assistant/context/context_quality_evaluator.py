
from src.hr_assistant.context.context_sufficiency_evaluator import (
    ContextSufficiencyEvaluator,
)

from src.hr_assistant.context.context_evidence_evaluator import (
    ContextEvidenceEvaluator,
)

from src.hr_assistant.context.semantic_evidence_evaluator import (
    SemanticEvidenceEvaluator,
)


class ContextQualityEvaluator:

    def __init__(self):

        self.structural_evaluator = ContextSufficiencyEvaluator()
        self.evidence_evaluator = ContextEvidenceEvaluator()
        self.semantic_evaluator = SemanticEvidenceEvaluator()

    def evaluate(self, context_output, required_evidence):

        # 1. Structural validation
        structural_result = self.structural_evaluator.evaluate(
            context_output
        )

        # 2. Exact evidence coverage
        evidence_result = self.evidence_evaluator.evaluate(
            context=context_output.get("context", ""),
            required_evidence=required_evidence,
        )

        # 3. Run semantic evaluation only if structure is valid
        semantic_result = None

        if structural_result["answerable"]:

            semantic_result = self.semantic_evaluator.evaluate(
                query=context_output["query"],
                context=context_output["context"],
                required_evidence=required_evidence,
            )

        # 4. Final decision
        answerable = (
            structural_result["answerable"]
            and semantic_result is not None
            and semantic_result["evaluation_status"] == "success"
            and semantic_result["answerable"]
        )

        if not structural_result["answerable"]:
            final_status = "structurally_insufficient"

        elif semantic_result["evaluation_status"] == "failed":
            final_status = "evaluation_failed"

        elif not semantic_result["answerable"]:
            final_status = "evidence_insufficient"

        else:
            final_status = "sufficient"

        return {
            "query": context_output["query"],
            "answerable": answerable,
            "final_status": final_status,

            "structural_evaluation": structural_result,
            "exact_evidence_evaluation": evidence_result,
            "semantic_evaluation": semantic_result,
        }
