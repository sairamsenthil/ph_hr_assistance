
import re


class ContextDeduplicator:

    @staticmethod
    def normalize_for_comparison(text):

        return re.sub(
            r"\s+",
            " ",
            text
        ).strip().casefold()

    def deduplicate(self, context):

        paragraphs = context.split("\n\n")

        seen = set()
        unique_paragraphs = []

        duplicates_removed = 0

        for paragraph in paragraphs:

            normalized = self.normalize_for_comparison(paragraph)

            if not normalized:
                continue

            if normalized in seen:
                duplicates_removed += 1
                continue

            seen.add(normalized)
            unique_paragraphs.append(paragraph)

        deduplicated_context = "\n\n".join(unique_paragraphs)

        return {
            "context": deduplicated_context,
            "original_paragraph_count": len(paragraphs),
            "unique_paragraph_count": len(unique_paragraphs),
            "duplicates_removed": duplicates_removed,
        }
