
from src.hr_assistant.generation.generation_quality_pipeline import (
    GenerationQualityPipeline,
)


def main():

    pipeline = GenerationQualityPipeline()

    # --------------------------------------------------
    # SHARED TEST DATA
    # --------------------------------------------------

    sources = [
        {
            "source_id": "policy_001",
            "policy_title": "Bullying and Harassment Policy",
        }
    ]

    sufficient_context = {
        "answerable": True,
        "final_status": "sufficient",
    }

    claim_assessments = [
        {
            "claim": "Employees can contact their line manager.",
            "status": "supported",
        },
        {
            "claim": "Employees can contact Human Resources.",
            "status": "supported",
        },
    ]

    valid_answer = (
        "Employees can raise harassment complaints with their "
        "line manager or Human Resources. [SOURCE 1]"
    )

    # --------------------------------------------------
    # TEST 1: ALL CHECKS PASS
    # --------------------------------------------------

    print("\n========== TEST 1: ALL CHECKS PASS ==========")

    result = pipeline.evaluate(
        answer=valid_answer,
        sources=sources,
        context_quality=sufficient_context,
        claim_assessments=claim_assessments,
    )

    print("Decision:", result["decision"])
    print("Citation validation:", result["citation_validation"])
    print("Claim grounding:", result["claim_grounding"])
    print("Final answer:", result["final_answer"])

    assert result["decision"]["decision"] == "answer"
    assert result["citation_validation"]["valid"] is True
    assert result["claim_grounding"]["grounded"] is True

    print("TEST 1 PASSED")

    # --------------------------------------------------
    # TEST 2: INVALID CITATION
    # --------------------------------------------------

    print("\n========== TEST 2: INVALID CITATION ==========")

    result = pipeline.evaluate(
        answer="Employees can raise complaints. [SOURCE 5]",
        sources=sources,
        context_quality=sufficient_context,
        claim_assessments=claim_assessments,
    )

    print("Decision:", result["decision"])
    print("Citation validation:", result["citation_validation"])
    print("Final answer:", result["final_answer"])

    assert result["citation_validation"]["valid"] is False
    assert result["decision"]["decision"] == "abstain"

    print("TEST 2 PASSED")

    # --------------------------------------------------
    # TEST 3: UNSUPPORTED CLAIM
    # --------------------------------------------------

    print("\n========== TEST 3: UNSUPPORTED CLAIM ==========")

    unsupported_claims = [
        {
            "claim": "Employees can raise complaints.",
            "status": "unsupported",
        }
    ]

    result = pipeline.evaluate(
        answer=valid_answer,
        sources=sources,
        context_quality=sufficient_context,
        claim_assessments=unsupported_claims,
    )

    print("Decision:", result["decision"])
    print("Claim grounding:", result["claim_grounding"])
    print("Final answer:", result["final_answer"])

    assert result["claim_grounding"]["grounded"] is False
    assert result["decision"]["decision"] == "abstain"

    print("TEST 3 PASSED")

    # --------------------------------------------------
    # TEST 4: INSUFFICIENT CONTEXT
    # --------------------------------------------------

    print("\n========== TEST 4: INSUFFICIENT CONTEXT ==========")

    insufficient_context = {
        "answerable": False,
        "final_status": "insufficient",
    }

    result = pipeline.evaluate(
        answer=valid_answer,
        sources=sources,
        context_quality=insufficient_context,
        claim_assessments=claim_assessments,
    )

    print("Decision:", result["decision"])
    print("Final answer:", result["final_answer"])

    assert result["decision"]["decision"] == "abstain"

    print("TEST 4 PASSED")

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print("\n========================================")
    print("ALL 4 GENERATION QUALITY TESTS PASSED")
    print("========================================")


if __name__ == "__main__":
    main()
