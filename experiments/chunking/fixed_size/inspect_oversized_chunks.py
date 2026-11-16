
import json
import re
from pathlib import Path
from collections import Counter
from tokenizers import Tokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT / "data" / "processed" / "chunks"
    / "fixed_size" / "fixed_size_chunks.jsonl"
)

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"
CONTEXT_LIMIT = 512


def main():
    with open(CHUNK_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    print("Loading tokenizer...")
    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)

    oversized_chunks = []

    for chunk in chunks:
        encoded = tokenizer.encode(chunk["text"])

        if len(encoded.ids) > CONTEXT_LIMIT:
            oversized_chunks.append((chunk, encoded))

    print("\n--- OVERSIZED CHUNK INVESTIGATION ---")
    print(f"Chunks exceeding {CONTEXT_LIMIT} tokens: {len(oversized_chunks)}")

    for chunk, encoded in oversized_chunks:
        tokens = encoded.tokens

        punctuation_tokens = [
            token for token in tokens
            if re.fullmatch(r"[^\w\s]+", token)
        ]

        print("\n" + "=" * 75)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Pages: {chunk['page_start']} - {chunk['page_end']}")
        print(f"Words: {len(chunk['text'].split())}")
        print(f"Tokens: {len(encoded.ids)}")
        print(f"Punctuation-only tokens: {len(punctuation_tokens)}")

        print("\nTEXT PREVIEW:")
        print(chunk["text"][:700].replace("\n", " "))

        print("\nMOST FREQUENT TOKENS:")
        for token, count in Counter(tokens).most_common(15):
            print(f"{repr(token)}: {count}")

    print("\n--- INVESTIGATION COMPLETE ---")


if __name__ == "__main__":
    main()
