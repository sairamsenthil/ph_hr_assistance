
import json

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "fixed_size"
    / "fixed_size_chunks.jsonl"
)

with CHUNK_FILE.open("r", encoding="utf-8") as file:
    chunks = [
        json.loads(line)
        for line in file
        if line.strip()
    ]

print("\n--- CHUNK VALIDATION REPORT ---")

print("Total chunks:", len(chunks))

# 1. Unique IDs
chunk_ids = [chunk["chunk_id"] for chunk in chunks]
print("Unique IDs:", len(set(chunk_ids)) == len(chunk_ids))

# 2. Empty chunks
empty_chunks = [
    chunk["chunk_id"]
    for chunk in chunks
    if not chunk["text"].strip()
]
print("Empty chunks:", len(empty_chunks))

# 3. Chunk size
word_counts = [
    len(chunk["text"].split())
    for chunk in chunks
]

print("Minimum words:", min(word_counts))
print("Maximum words:", max(word_counts))

# 4. Page range validation
invalid_pages = [
    chunk["chunk_id"]
    for chunk in chunks
    if chunk["page_start"] > chunk["page_end"]
    or chunk["page_start"] < 1
    or chunk["page_end"] > 98
]

print("Invalid page ranges:", len(invalid_pages))

# 5. Structural metadata
missing_sections = sum(
    chunk["major_section_number"] is None
    for chunk in chunks
)

print("Chunks without section metadata:", missing_sections)

# 6. Overlap validation
if len(chunks) >= 2:

    first_words = chunks[0]["text"].split()
    second_words = chunks[1]["text"].split()

    actual_overlap = 0

    for size in range(1, min(len(first_words), len(second_words)) + 1):
        if first_words[-size:] == second_words[:size]:
            actual_overlap = size

    print("First two chunks overlap:", actual_overlap, "words")

print("\n--- CHUNKS WITHOUT SECTION METADATA ---")

for chunk in chunks:

    if chunk["major_section_number"] is None:

        print(
            chunk["chunk_id"],
            "| Pages:",
            chunk["page_start"],
            "-",
            chunk["page_end"]
        )


print("\n--- FIRST TWO CHUNKS ---")

for chunk in chunks[:2]:

    print("\nChunk ID:", chunk["chunk_id"])
    print("Pages:", chunk["page_start"], "-", chunk["page_end"])
    print("Policy:", chunk["policy_title"])
    print("Subsection:", chunk["subsection_title"])
    print("Preview:", chunk["text"][:250])
