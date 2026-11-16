
import unittest

from src.hr_assistant.generation.citation_validator import (
    CitationValidator,
)

from src.hr_assistant.generation.claim_grounding_validator import (
    ClaimGroundingValidator,
)

from src.hr_assistant.generation.abstention_controller import (
    AbstentionController,
)

from src.hr_assistant.generation.generation_quality_pipeline import (
    GenerationQualityPipeline,
)


class TestCitationValidator(unittest.TestCase):

    def setUp(self):
        self.validator = CitationValidator()

    def test_valid_sequential_citations(self):
        result = self.validator.validate(
            answer="Follow the policy [SOURCE 1].",
            sources=[{}, {}],
        )
        self.assertTrue(result["valid"])

    def test_valid_non_sequential_source_indexes(self):
        result = self.validator.validate(
            answer="Follow the policy [SOURCE 3].",
            sources=[
                {"source_index": 1},
                {"source_index": 3},
                {"source_index": 5},
            ],
        )
        self.assertTrue(result["valid"])

    def test_rejects_missing_citations(self):
        result = self.validator.validate(
            answer="Follow the HR policy.",
            sources=[{}],
        )
        self.assertEqual(result["status"], "missing_citations")

    def test_rejects_invalid_citation(self):
        result = self.validator.validate(
            answer="Follow the policy [SOURCE 4].",
            sources=[
                {"source_index": 1},
                {"source_index": 3},
            ],
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["invalid_citations"], [4])

    def test_rejects_empty_answer(self):
        result = self.validator.validate(
            answer=" ",
            sources=[{}],
        )
        self.assertEqual(result["status"], "empty_answer")

    def test_rejects_duplicate_source_indexes(self):
        with self.assertRaises(ValueError):
            self.validator.validate(
                answer="Policy [SOURCE 1].",
                sources=[
                    {"source_index": 1},
                    {"source_index": 1},
                ],
            )


class TestClaimGroundingValidator(unittest.TestCase):

    def setUp(self):
        self.validator = ClaimGroundingValidator()

    def test_all_supported_claims_are_grounded(self):
        result = self.validator.validate([
            {"status": "supported"},
            {"status": "supported"},
        ])
        self.assertTrue(result["grounded"])
        self.assertEqual(result["total_claims"], 2)

    def test_partially_supported_claim_fails_grounding(self):
        result = self.validator.validate([
            {"status": "supported"},
            {"status": "partially_supported"},
        ])
        self.assertFalse(result["grounded"])

    def test_unsupported_claim_fails_grounding(self):
        result = self.validator.validate([
            {"status": "unsupported"},
        ])
        self.assertFalse(result["grounded"])

    def test_contradicted_claim_fails_grounding(self):
        result = self.validator.validate([
            {"status": "contradicted"},
        ])
        self.assertFalse(result["grounded"])

    def test_empty_claims_fail_closed(self):
        result = self.validator.validate([])
        self.assertFalse(result["grounded"])
        self.assertEqual(result["status"], "no_claims_provided")

    def test_invalid_claim_status_is_rejected(self):
        with self.assertRaises(ValueError):
            self.validator.validate([
                {"status": "unknown"},
            ])


class TestAbstentionController(unittest.TestCase):

    def setUp(self):
        self.controller = AbstentionController()

    def test_abstains_when_claim_grounding_missing(self):
        result = self.controller.decide(
            context_quality={
                "answerable": True,
                "final_status": "sufficient",
            },
            claim_grounding=None,
            citation_validation={"valid": True},
        )
        self.assertEqual(result["decision"], "abstain")

    def test_abstains_when_context_is_insufficient(self):
        result = self.controller.decide(
            context_quality={
                "answerable": False,
                "final_status": "insufficient",
            },
            claim_grounding={"grounded": True},
            citation_validation={"valid": True},
        )
        self.assertEqual(result["decision"], "abstain")

    def test_abstains_when_citations_are_invalid(self):
        result = self.controller.decide(
            context_quality={
                "answerable": True,
                "final_status": "sufficient",
            },
            claim_grounding={"grounded": True},
            citation_validation={"valid": False},
        )
        self.assertEqual(result["decision"], "abstain")

    def test_all_valid_conditions_allow_answer(self):
        result = self.controller.decide(
            context_quality={
                "answerable": True,
                "final_status": "sufficient",
            },
            claim_grounding={"grounded": True},
            citation_validation={"valid": True},
        )
        self.assertEqual(result["decision"], "answer")


class TestGenerationQualityPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = GenerationQualityPipeline()

    def test_pipeline_abstains_when_claims_are_missing(self):
        result = self.pipeline.evaluate(
            answer="The employee can raise a grievance [SOURCE 1].",
            sources=[{"source_index": 1}],
            context_quality={
                "answerable": True,
                "final_status": "sufficient",
            },
            claim_assessments=[],
        )

        self.assertEqual(result["decision"]["decision"], "abstain")
        self.assertEqual(
            result["claim_grounding"]["status"],
            "no_claims_provided",
        )

    def test_pipeline_allows_fully_validated_answer(self):
        answer = "Employees may raise a grievance [SOURCE 1]."

        result = self.pipeline.evaluate(
            answer=answer,
            sources=[{"source_index": 1}],
            context_quality={
                "answerable": True,
                "final_status": "sufficient",
            },
            claim_assessments=[
                {"status": "supported"},
            ],
        )

        self.assertEqual(result["decision"]["decision"], "answer")
        self.assertEqual(result["final_answer"], answer)

    def test_pipeline_abstains_on_invalid_citation(self):
        result = self.pipeline.evaluate(
            answer="Policy guidance [SOURCE 5].",
            sources=[{"source_index": 1}],
            context_quality={
                "answerable": True,
                "final_status": "sufficient",
            },
            claim_assessments=[
                {"status": "supported"},
            ],
        )

        self.assertEqual(result["decision"]["decision"], "abstain")


if __name__ == "__main__":
    unittest.main()
