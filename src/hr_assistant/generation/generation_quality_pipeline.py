
from src.hr_assistant.generation.citation_validator import (
    CitationValidator,
)

from src.hr_assistant.generation.claim_grounding_validator import (
    ClaimGroundingValidator,
)

from src.hr_assistant.generation.abstention_controller import (
    AbstentionController,
)


class GenerationQualityPipeline:

    def __init__(self):

        self.citation_validator = CitationValidator()
        self.claim_validator = ClaimGroundingValidator()
        self.abstention_controller = AbstentionController()

    def evaluate(
        self,
        answer,
        sources,
        context_quality,
        claim_assessments,
    ):

        # 1. Validate citations
        citation_result = self.citation_validator.validate(
            answer=answer,
            sources=sources,
        )

        # 2. Validate claim assessments
        claim_result = self.claim_validator.validate(
            claim_assessments=claim_assessments,
        )

        # 3. Make final answer/abstention decision
        decision = self.abstention_controller.decide(
            context_quality=context_quality,
            claim_grounding=claim_result,
            citation_validation=citation_result,
        )

        final_answer = (
            answer
            if decision["decision"] == "answer"
            else self.abstention_controller.get_abstention_message()
        )

        return {
            "final_answer": final_answer,
            "decision": decision,
            "citation_validation": citation_result,
            "claim_grounding": claim_result,
        }
