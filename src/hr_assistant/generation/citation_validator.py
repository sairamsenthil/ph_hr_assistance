
import re


class CitationValidator:

    CITATION_PATTERN = re.compile(
        r"\[SOURCE\s+(\d+)\]",
        re.IGNORECASE,
    )

    def validate(self, answer, sources):

        # 1. Validate answer
        if not isinstance(answer, str) or not answer.strip():
            return {
                "valid": False,
                "status": "empty_answer",
                "citations_found": [],
                "invalid_citations": [],
                "uncited_answer": True,
            }

        # 2. Validate sources
        if not isinstance(sources, list):
            raise ValueError("sources must be a list")

        # 3. Identify valid source indexes
        valid_source_ids = set(
            range(1, len(sources) + 1)
        )

        # 4. Extract citations
        citations = [
            int(match)
            for match in self.CITATION_PATTERN.findall(answer)
        ]

        unique_citations = sorted(set(citations))

        # 5. Identify invalid citations
        invalid_citations = [
            citation
            for citation in unique_citations
            if citation not in valid_source_ids
        ]

        # 6. Check whether citations are missing
        uncited_answer = len(citations) == 0

        # 7. Determine validation status
        if uncited_answer:
            status = "missing_citations"

        elif invalid_citations:
            status = "invalid_citations_found"

        else:
            status = "valid"

        is_valid = (
            not uncited_answer
            and not invalid_citations
        )

        return {
            "valid": is_valid,
            "status": status,
            "citations_found": unique_citations,
            "invalid_citations": invalid_citations,
            "uncited_answer": uncited_answer,
        }
