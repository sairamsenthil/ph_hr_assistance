
from typing import Any


def build_chunk(
    text: str,
    metadata: dict[str, Any],
    chunking_strategy: str,
    chunk_index: int,
    page_start: int,
    page_end: int,
    parent_chunk_id: str | None = None
) -> dict:
    """
    Build a standardized chunk with document and
    structural metadata.
    """

    document_id = metadata["document_id"]

    chunk_id = (
        f"{document_id}:"
        f"{chunking_strategy}:"
        f"{chunk_index:05d}"
    )

    return {
        "chunk_id": chunk_id,
        "text": text,

        # Document metadata
        "document_id": document_id,
        "source": metadata["source"],
        "document_type": metadata["document_type"],

        # Page information
        "page_start": page_start,
        "page_end": page_end,

        # Structural metadata
        "major_section_number": metadata.get(
            "major_section_number"
        ),
        "major_section": metadata.get("major_section"),
        "policy_number": metadata.get("policy_number"),
        "policy_title": metadata.get("policy_title"),
        "subsection_number": metadata.get("subsection_number"),
        "subsection_title": metadata.get("subsection_title"),

        # Chunk information
        "chunking_strategy": chunking_strategy,
        "chunk_index": chunk_index,
        "token_count": None,
        "parent_chunk_id": parent_chunk_id
    }
