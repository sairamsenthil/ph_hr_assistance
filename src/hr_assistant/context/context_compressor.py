import re

from src.hr_assistant.context.context_grouper import (
    ContextGrouper,
)


class ContextCompressor:

    STOPWORDS = {
        "a", "an", "the", "is", "are", "was", "were",
        "to", "of", "in", "on", "for", "and", "or",
        "how", "what", "when", "where", "who", "why",
        "can", "could", "should", "would", "do", "does",
        "employee", "employees"
    }

    def __init__(self):
        self.grouper = ContextGrouper()

    def tokenize(self, text):

        tokens = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

        return [
            token for token in tokens
            if token not in self.STOPWORDS
        ]

    def score_group(self, query, group):

        query_tokens = set(self.tokenize(query))
        group_tokens = set(self.tokenize(group["text"]))

        if not query_tokens or not group_tokens:
            return 0.0

        matched_tokens = query_tokens.intersection(
            group_tokens
        )

        return len(matched_tokens) / len(query_tokens)

    def compress_source(self, query, source):

        paragraphs = [
            {
                "paragraph_index": index,
                "text": paragraph.strip(),
            }
            for index, paragraph in enumerate(
                source["text"].split("\n\n")
            )
            if paragraph.strip()
        ]

        groups = self.grouper.group_paragraphs(
            paragraphs
        )

        scored_groups = []

        for index, group in enumerate(groups):

            score = self.score_group(
                query=query,
                group=group,
            )

            scored_groups.append({
                "group_index": index,
                "paragraph_indexes": group["paragraph_indexes"],
                "text": group["text"],
                "relevance_score": score,
            })

        return {
            "source_id": source["chunk_id"],
            "policy_title": source["policy_title"],
            "page_start": source["page_start"],
            "page_end": source["page_end"],
            "groups": scored_groups,
            "original_paragraph_count": len(paragraphs),
            "original_group_count": len(groups),
        }

    def filter_groups(
        self,
        compressed_source,
        min_relevance=0.2,
        top_k=None,
    ):

        groups = compressed_source["groups"]

        relevant_groups = [
            group for group in groups
            if group["relevance_score"] >= min_relevance
        ]

        if top_k is not None:

            relevant_groups = sorted(
                relevant_groups,
                key=lambda item: item["relevance_score"],
                reverse=True,
            )[:top_k]

        relevant_groups.sort(
            key=lambda item: item["group_index"]
        )

        retained_paragraph_count = sum(
            len(group["paragraph_indexes"])
            for group in relevant_groups
        )

        return {
            "source_id": compressed_source["source_id"],
            "policy_title": compressed_source["policy_title"],
            "page_start": compressed_source["page_start"],
            "page_end": compressed_source["page_end"],
            "groups": relevant_groups,
            "original_paragraph_count": (
                compressed_source["original_paragraph_count"]
            ),
            "original_group_count": (
                compressed_source["original_group_count"]
            ),
            "retained_group_count": len(relevant_groups),
            "removed_group_count": (
                compressed_source["original_group_count"]
                - len(relevant_groups)
            ),
            "retained_paragraph_count": retained_paragraph_count,
        }