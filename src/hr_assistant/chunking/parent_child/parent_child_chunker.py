
from tokenizers import Tokenizer

from src.hr_assistant.chunking.chunk_schema import build_chunk
from src.hr_assistant.chunking.token_aware.token_aware import (
    split_text,
    TOKENIZER_NAME,
)
from src.hr_assistant.chunking.policy_grouper import (
    group_pages_by_policy,
    combine_group_pages,
)
from src.hr_assistant.security.policy_access_config import (
    get_policy_access_level,
)


DEFAULT_PARENT_SIZE = 900
DEFAULT_CHILD_SIZE = 250
DEFAULT_CHILD_OVERLAP = 40


def build_parent_page_spans(
    page_spans: list[dict],
    parent_start: int,
    parent_end: int,
) -> list[dict]:
    """
    Convert document-level page positions into positions
    relative to an individual parent chunk.
    """

    local_spans = []

    for span in page_spans:

        overlap_start = max(
            span["start_char"],
            parent_start
        )

        overlap_end = min(
            span["end_char"],
            parent_end
        )

        if overlap_start < overlap_end:

            local_spans.append({
                "page": span["page"],
                "start_char": overlap_start - parent_start,
                "end_char": overlap_end - parent_start,
            })

    return local_spans


def create_parent_child_chunks(
    pages: list[dict],
    page_registry: dict,
    parent_size: int = DEFAULT_PARENT_SIZE,
    child_size: int = DEFAULT_CHILD_SIZE,
    child_overlap: int = DEFAULT_CHILD_OVERLAP,
):
    """
    Generate parent chunks and their linked child chunks.

    Parent chunks are created within policy boundaries.
    Child chunks are generated independently inside each parent.

    Access levels are assigned using trusted policy configuration.
    Both parent and child chunks inherit the same access level.
    """

    if parent_size <= 0 or child_size <= 0:
        raise ValueError("Chunk sizes must be positive.")

    if child_overlap < 0 or child_overlap >= child_size:
        raise ValueError("Invalid child overlap.")

    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)
    tokenizer.no_truncation()

    policy_groups = group_pages_by_policy(
        pages,
        page_registry
    )

    parents = []
    children = []

    parent_index = 0
    child_index = 0

    for group in policy_groups:

        # Ignore front matter and non-policy document regions.
        if group["policy_number"] is None:
            continue

        if not group["pages"]:
            continue

        combined = combine_group_pages(group)

        parent_parts = split_text(
            text=combined["text"],
            page_spans=combined["page_spans"],
            tokenizer=tokenizer,
            chunk_size=parent_size,
            overlap=0,
        )

        # Inherit document metadata from the source pages.
        metadata = {
            **group["pages"][0]["metadata"],
            "major_section_number": group["major_section_number"],
            "policy_number": group["policy_number"],
            "policy_title": group["policy_title"],
        }

        # Resolve permissions from trusted configuration.
        # Unknown policies fail closed with ValueError.
        access_level = get_policy_access_level(
            metadata["policy_title"]
        )

        for parent_part in parent_parts:

            parent_pages = parent_part["source_pages"]

            parent = build_chunk(
                text=parent_part["text"],
                metadata=metadata,
                chunking_strategy="parent",
                chunk_index=parent_index,
                page_start=min(parent_pages),
                page_end=max(parent_pages),
            )

            parent["token_count"] = parent_part["token_count"]
            parent["source_pages"] = parent_pages
            parent["start_char"] = parent_part["start_char"]
            parent["end_char"] = parent_part["end_char"]

            # Apply trusted access metadata.
            parent["access_level"] = access_level

            parents.append(parent)

            # Convert original page positions to parent-local positions.
            local_page_spans = build_parent_page_spans(
                page_spans=combined["page_spans"],
                parent_start=parent_part["start_char"],
                parent_end=parent_part["end_char"],
            )

            child_parts = split_text(
                text=parent_part["text"],
                page_spans=local_page_spans,
                tokenizer=tokenizer,
                chunk_size=child_size,
                overlap=child_overlap,
            )

            for child_part in child_parts:

                child_pages = child_part["source_pages"]

                child = build_chunk(
                    text=child_part["text"],
                    metadata=metadata,
                    chunking_strategy="child",
                    chunk_index=child_index,
                    page_start=min(child_pages),
                    page_end=max(child_pages),
                    parent_chunk_id=parent["chunk_id"],
                )

                child["token_count"] = child_part["token_count"]
                child["source_pages"] = child_pages

                # Child offsets are relative to its parent.
                child["start_char"] = child_part["start_char"]
                child["end_char"] = child_part["end_char"]

                # Child inherits the same access level as its parent.
                child["access_level"] = access_level

                children.append(child)
                child_index += 1

            parent_index += 1

    return {
        "parents": parents,
        "children": children,
    }
