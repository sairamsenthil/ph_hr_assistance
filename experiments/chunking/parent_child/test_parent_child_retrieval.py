
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "parent_child"
    / "parent-child.jsonl"
)


def load_chunks(path):
    with open(path, "r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def tokenize(text):
    return set(re.findall(r"\b[a-z0-9]+\b", text.lower()))


def calculate_score(query, text):
    query_tokens = tokenize(query)
    text_tokens = tokenize(text)

    if not query_tokens:
        return 0

    matched_tokens = query_tokens.intersection(text_tokens)

    return len(matched_tokens) / len(query_tokens)


def retrieve_children(query, children, top_k=3, min_score=0.70):

    results = []

    for child in children:
        score = calculate_score(query, child["text"])

        if score >= min_score:
            results.append({
                "chunk": child,
                "score": score
            })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )[:top_k]


def main():

    print("Loading Parent-Child chunks...")

    chunks = load_chunks(CHUNKS_FILE)

    parents = {
        chunk["chunk_id"]: chunk
        for chunk in chunks
        if chunk["chunking_strategy"] == "parent"
    }

    children = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    print(f"Parents loaded: {len(parents)}")
    print(f"Children loaded: {len(children)}")

    query = "How are internal candidates selected for interview?"

    print(f"\nUser Query: {query}")

    retrieved = retrieve_children(
        query=query,
        children=children,
        top_k=3
    )

    print("\n--- CHILD-ONLY RETRIEVAL ---")

    for result in retrieved:

        child = result["chunk"]

        print(f"\nChild ID: {child['chunk_id']}")
        print(f"Score: {result['score']:.2f}")
        print(f"Policy: {child['policy_title']}")
        print(f"Text:\n{child['text']}")

    
    print("\n--- PARENT-CHILD RETRIEVAL ---")

    retrieved_parent_ids = set()
    ranked_parents = []

    for result in retrieved:

        child = result["chunk"]
        parent_id = child["parent_chunk_id"]
    
        if parent_id in parents and parent_id not in retrieved_parent_ids:
    
            retrieved_parent_ids.add(parent_id)

            ranked_parents.append({
                "parent": parents[parent_id],
                "child_score": result["score"],
                "matched_child_id": child["chunk_id"]
            })

    for result in ranked_parents:
    
        parent = result["parent"]

        print(f"\nParent ID: {parent['chunk_id']}")
        print(f"Matched Child: {result['matched_child_id']}")
        print(f"Child Match Score: {result['child_score']:.2f}")
        print(f"Policy: {parent['policy_title']}")
        print(f"Pages: {parent['page_start']}-{parent['page_end']}")
        print(f"Parent Tokens: {parent['token_count']}")
        print(f"Context:\n{parent['text']}")


        print("\n--- RETRIEVAL SUMMARY ---")  
        print(f"Matched child chunks: {len(retrieved)}")
        print(f"Unique parent chunks retrieved: {len(retrieved_parent_ids)}")

if __name__ == "__main__":
    main()