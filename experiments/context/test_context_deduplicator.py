
from src.hr_assistant.context.context_deduplicator import (
    ContextDeduplicator,
)


def main():

    sample_context = """
[SOURCE 1]
Policy: Grievance Procedure

Employees must report complaints to HR.

All complaints must be investigated promptly.


[SOURCE 2]
Policy: Bullying and Harassment Policy

Employees must report complaints to HR.

Employees must not face retaliation for raising complaints.
"""

    deduplicator = ContextDeduplicator()

    result = deduplicator.deduplicate(sample_context)

    print("\n========== DEDUPLICATION RESULTS ==========")

    print(
        "Original paragraphs:",
        result["original_paragraph_count"],
    )

    print(
        "Unique paragraphs:",
        result["unique_paragraph_count"],
    )

    print(
        "Duplicates removed:",
        result["duplicates_removed"],
    )

    print("\n========== DEDUPLICATED CONTEXT ==========")

    print(result["context"])


if __name__ == "__main__":
    main()
