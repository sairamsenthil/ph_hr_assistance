
import json
import statistics
from pathlib import Path

from tokenizers import Tokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "fixed_size"
    / "fixed_size_chunks.jsonl"
)

REPORT_FILE = (
    Path(__file__).resolve().parent
    / "fixed_size_token_report.json"
)

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"
CONTEXT_LIMIT = 512
SAFETY_THRESHOLD = int(CONTEXT_LIMIT * 0.90)


def load_chunks():
    chunks = []

    with open(CHUNK_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def main():
    print("Loading model tokenizer...")

    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)

    # Ensure that tokenization is not silently truncated.
    tokenizer.no_truncation()

    chunks = load_chunks()
    results = []

    for chunk in chunks:
        text = chunk["text"]

        # Includes special tokens added by the tokenizer.
        token_count = len(tokenizer.encode(text).ids)
        word_count = len(text.split())

        results.append({
            "chunk_id": chunk["chunk_id"],
            "word_count": word_count,
            "token_count": token_count,
            "token_to_word_ratio": round(
                token_count / word_count, 3
            ) if word_count else None,
        })

    token_counts = [
        item["token_count"] for item in results
    ]

    word_counts = [
        item["word_count"] for item in results
    ]

    total_chunks = len(results)

    exceeding_limit = [
        item for item in results
        if item["token_count"] > CONTEXT_LIMIT
    ]

    approaching_limit = [
        item for item in results
        if SAFETY_THRESHOLD <= item["token_count"] <= CONTEXT_LIMIT
    ]

    average_ratio = (
        sum(item["token_count"] for item in results)
        / sum(word_counts)
    )

    report = {
        "tokenizer": TOKENIZER_NAME,
        "context_limit": CONTEXT_LIMIT,
        "safety_threshold": SAFETY_THRESHOLD,
        "total_chunks": total_chunks,
        "minimum_tokens": min(token_counts),
        "maximum_tokens": max(token_counts),
        "average_tokens": round(statistics.mean(token_counts), 2),
        "median_tokens": statistics.median(token_counts),
        "minimum_words": min(word_counts),
        "maximum_words": max(word_counts),
        "average_words": round(statistics.mean(word_counts), 2),
        "average_token_to_word_ratio": round(average_ratio, 3),
        "chunks_exceeding_limit": len(exceeding_limit),
        "chunks_approaching_limit": len(approaching_limit),
        "chunk_details": results,
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print("\n--- FIXED-SIZE TOKEN ANALYSIS ---")
    print(f"Total chunks: {total_chunks}")
    print(f"Tokenizer: {TOKENIZER_NAME}")
    print(f"Context limit: {CONTEXT_LIMIT} tokens")
    print(f"Safety threshold (90%): {SAFETY_THRESHOLD} tokens")

    print("\n--- TOKEN STATISTICS ---")
    print(f"Minimum tokens: {report['minimum_tokens']}")
    print(f"Maximum tokens: {report['maximum_tokens']}")
    print(f"Average tokens: {report['average_tokens']}")
    print(f"Median tokens: {report['median_tokens']}")

    print("\n--- WORD STATISTICS ---")
    print(f"Minimum words: {report['minimum_words']}")
    print(f"Maximum words: {report['maximum_words']}")
    print(f"Average words: {report['average_words']}")
    print(
        "Average token-to-word ratio: "
        f"{report['average_token_to_word_ratio']}"
    )

    print("\n--- CONTEXT LIMIT ANALYSIS ---")
    print(f"Chunks exceeding 512 tokens: {len(exceeding_limit)}")
    print(
        f"Chunks approaching limit ({SAFETY_THRESHOLD}-512): "
        f"{len(approaching_limit)}"
    )

    print("\n--- CHUNKS EXCEEDING CONTEXT LIMIT ---")

    for item in exceeding_limit:
        print(
            f"{item['chunk_id']} | "
            f"Words: {item['word_count']} | "
            f"Tokens: {item['token_count']}"
        )

    print("\n--- LARGEST 10 CHUNKS BY TOKEN COUNT ---")

    largest_chunks = sorted(
        results,
        key=lambda item: item["token_count"],
        reverse=True
    )[:10]

    for item in largest_chunks:
        print(
            f"{item['chunk_id']} | "
            f"Words: {item['word_count']} | "
            f"Tokens: {item['token_count']}"
        )

    print(f"\nDetailed report saved to: {REPORT_FILE}")
    print("\n--- TOKEN ANALYSIS COMPLETE ---")


if __name__ == "__main__":
    main()
