
class ClaimGroundingValidator:

    def validate(self, claim_assessments):

        if not isinstance(claim_assessments, list):
            raise ValueError(
                "claim_assessments must be a list"
            )

        if not claim_assessments:
            return {
                "grounded": False,
                "status": "no_claims_provided",
                "total_claims": 0,
                "supported": 0,
                "partially_supported": 0,
                "unsupported": 0,
                "contradicted": 0,
            }

        allowed_statuses = {
            "supported",
            "partially_supported",
            "unsupported",
            "contradicted",
        }

        counts = {
            status: 0
            for status in allowed_statuses
        }

        for assessment in claim_assessments:

            status = assessment.get("status")

            if status not in allowed_statuses:
                raise ValueError(
                    f"Invalid claim status: {status}"
                )

            counts[status] += 1

        grounded = (
            counts["unsupported"] == 0
            and counts["contradicted"] == 0
            and counts["partially_supported"] == 0
        )

        return {
            "grounded": grounded,
            "status": (
                "fully_grounded"
                if grounded
                else "grounding_issues_found"
            ),
            "total_claims": len(claim_assessments),
            "supported": counts["supported"],
            "partially_supported": counts["partially_supported"],
            "unsupported": counts["unsupported"],
            "contradicted": counts["contradicted"],
        }
