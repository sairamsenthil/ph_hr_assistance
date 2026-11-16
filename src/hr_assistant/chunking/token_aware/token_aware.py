
import re
from tokenizers import Tokenizer

DEFAULT_CHUNK_SIZE = 460
DEFAULT_OVERLAP = 50

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"

 
def find_split_boundary(
    text: str,
    start_char: int,
    hard_end_char: int,
    tokenizer: Tokenizer,
    max_tokens: int,
    minimum_tokens: int = 0
):
    """
    Priority: paragraph -> line -> sentence -> fallback.
    """

    patterns = [
        r"\n[ \t]*\n+",
        r"\n",
        r"(?<=[.!?])\s+"
    ]

    for pattern in patterns:
        valid_boundaries = []

        for match in re.finditer(pattern, text):
            if not (start_char < match.end() <= hard_end_char):
                continue

            position = match.end()
            candidate = text[start_char:position].strip()

            if not candidate:
                continue

            candidate_tokens = len(
                tokenizer.encode(candidate).ids
            )

            if minimum_tokens <= candidate_tokens <= max_tokens:
                valid_boundaries.append(position)

        if valid_boundaries:
            return valid_boundaries[-1]

    return hard_end_char


def _trim_chunk(text: str, start: int, end: int):
    """Return trimmed text and its accurate character offsets."""

    while start < end and text[start].isspace():
        start += 1

    while end > start and text[end - 1].isspace():
        end -= 1

    return text[start:end], start, end


def split_text(
    text: str,
    page_spans: list[dict],
    tokenizer: Tokenizer,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
):
    """
    Cross-page token-aware splitting with structural boundaries,
    token overlap and source-page provenance.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid overlap")

    if not text.strip():
        return []

    encoded = tokenizer.encode(text)

    offsets = [
        (start, end)
        for start, end in encoded.offsets
        if end > start
    ]

    if not offsets:
        return []

    if not page_spans:
        raise ValueError("page_spans cannot be empty")

    # Reserve two tokens for tokenizer/context safety.
    token_budget = chunk_size - 2
    minimum_chunk_tokens = token_budget // 2

    chunks = []
    start_token = 0

    while start_token < len(offsets):

        start_char = offsets[start_token][0]

        remaining_tokens = len(offsets) - start_token

        if remaining_tokens <= token_budget:
            hard_end_token = len(offsets)
            hard_end_char = len(text)

            split_char = hard_end_char

        else:
            hard_end_token = start_token + token_budget
            hard_end_char = offsets[hard_end_token - 1][1]

            split_char = find_split_boundary(
                text=text,
                start_char=start_char,
                hard_end_char=hard_end_char,
                tokenizer=tokenizer,
                max_tokens=token_budget,
                minimum_tokens=minimum_chunk_tokens
            )

        chunk_text, chunk_start, chunk_end = _trim_chunk(
            text,
            start_char,
            split_char
        )

        if not chunk_text:
            break

        token_count = len(
            tokenizer.encode(chunk_text).ids
        )

        # Final hard-limit enforcement.
        if token_count > chunk_size:
            raise ValueError(
                f"Chunk exceeded token limit: {token_count}"
            )

        # Map the actual content range to its source pages.
        overlapping_pages = sorted({
            span["page"]
            for span in page_spans
            if span["start_char"] < chunk_end
            and span["end_char"] > chunk_start
        })

        if not overlapping_pages:
            raise ValueError(
                f"Page mapping failed for characters "
                f"{chunk_start}-{chunk_end}"
            )

        chunks.append({
            "text": chunk_text,
            "token_count": token_count,
            "page_start": min(overlapping_pages),
            "page_end": max(overlapping_pages),
            "source_pages": overlapping_pages,
            "start_char": chunk_start,
            "end_char": chunk_end
        })

        # Find the first token after the current chunk boundary.
        end_token = start_token

        while (
            end_token < len(offsets)
            and offsets[end_token][1] <= split_char
        ):
            end_token += 1

        if end_token >= len(offsets):
            break

        # Maintain token-based overlap.
        next_start = max(
            start_token + 1,
            end_token - overlap
        )

        start_token = next_start

    return chunks


def split_page(
    text: str,
    tokenizer: Tokenizer,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
):
    """Backward-compatible page-independent splitter."""

    page_spans = [{
        "page": 1,
        "start_char": 0,
        "end_char": len(text)
    }]

    chunks = split_text(
        text=text,
        page_spans=page_spans,
        tokenizer=tokenizer,
        chunk_size=chunk_size,
        overlap=overlap
    )

    return [
        {
            "text": chunk["text"],
            "token_count": chunk["token_count"]
        }
        for chunk in chunks
    ]


def create_token_aware_chunks(
    pages: list[dict],
    page_registry: dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
):
    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)
    tokenizer.no_truncation()

    from src.hr_assistant.chunking.chunk_schema import build_chunk

    all_chunks = []
    chunk_index = 0

    for page in sorted(
        pages,
        key=lambda item: item["metadata"]["page"]
    ):
        page_number = page["metadata"]["page"]
        text = page.get("normalized_text", "")

        page_chunks = split_page(
            text,
            tokenizer,
            chunk_size,
            overlap
        )

        metadata = {
            **page["metadata"],
            **page_registry.get(page_number, {})
        }

        for page_chunk in page_chunks:
            chunk = build_chunk(
                text=page_chunk["text"],
                metadata=metadata,
                chunking_strategy="token_aware",
                chunk_index=chunk_index,
                page_start=page_number,
                page_end=page_number
            )

            chunk["token_count"] = page_chunk["token_count"]

            all_chunks.append(chunk)
            chunk_index += 1

    return all_chunks
