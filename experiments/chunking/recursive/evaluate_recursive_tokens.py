
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
    / "recursive"
    / "recursive_chunks.jsonl"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "experiments"
    / "chunking"
    / "recursive"
    / "recursive_token_report.json"
)

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"
CONTEXT_LIMIT = 512
SAFETY_THRESHOLD = int(CONTEXT_LIMIT * 0.90)


def load_chunks():
    with open(CHUNK_FILE, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main():
    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)
    tokenizer.no_truncation()

    chunks = load_chunks()
    results = []

    for chunk in chunks:
        token_count = len(tokenizer.encode(chunk["text"]).ids)

        results.append({
            "chunk_id": chunk["chunk_id"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "word_count": len(chunk["text"].split()),
            "token_count": token_count
        })

    token_counts = [item["token_count"] for item in results]
    word_counts = [item["word_count"] for item in results]

    oversized = [
        item for item in results
        if item["token_count"] > CONTEXT_LIMIT
    ]

    approaching = [
        item for item in results
        if SAFETY_THRESHOLD <= item["token_count"] <= CONTEXT_LIMIT
    ]

    report = {
        "tokenizer": TOKENIZER_NAME,
        "context_limit": CONTEXT_LIMIT,
        "safety_threshold": SAFETY_THRESHOLD,
        "total_chunks": len(results),
        "minimum_tokens": min(token_counts),
        "maximum_tokens": max(token_counts),
        "average_tokens": round(statistics.mean(token_counts), 2),
        "median_tokens": statistics.median(token_counts),
        "minimum_words": min(word_counts),
        "maximum_words": max(word_counts),
        "average_words": round(statistics.mean(word_counts), 2),
        "chunks_exceeding_limit": oversized,
        "chunks_approaching_limit": approaching,
        "all_chunks": results
    }

    print("\n--- RECURSIVE TOKEN ANALYSIS ---")
    print(f"Total chunks: {len(results)}")
    print(f"Tokenizer: {TOKENIZER_NAME}")
    print(f"Context limit: {CONTEXT_LIMIT}")
    print(f"Safety threshold: {SAFETY_THRESHOLD}")

    print("\n--- TOKEN STATISTICS ---")
    print(f"Minimum tokens: {min(token_counts)}")
    print(f"Maximum tokens: {max(token_counts)}")
    print(f"Average tokens: {statistics.mean(token_counts):.2f}")
    print(f"Median tokens: {statistics.median(token_counts)}")

    print("\n--- WORD STATISTICS ---")
    print(f"Minimum words: {min(word_counts)}")
    print(f"Maximum words: {max(word_counts)}")
    print(f"Average words: {statistics.mean(word_counts):.2f}")

    print("\n--- CONTEXT LIMIT ANALYSIS ---")
    print(f"Chunks exceeding 512 tokens: {len(oversized)}")
    print(
        f"Chunks approaching limit "
        f"({SAFETY_THRESHOLD}-{CONTEXT_LIMIT}): {len(approaching)}"
    )

    print("\n--- CHUNKS EXCEEDING CONTEXT LIMIT ---")

    for item in sorted(
        oversized,
        key=lambda x: x["token_count"],
        reverse=True
    ):
        print(
            f"{item['chunk_id']} | "
            f"Words: {item['word_count']} | "
            f"Tokens: {item['token_count']} | "
            f"Pages: {item['page_start']}-{item['page_end']}"
        )

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"\nDetailed report saved: {REPORT_FILE}")


if __name__ == "__main__":
    main()
