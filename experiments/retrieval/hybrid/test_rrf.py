
from src.hr_assistant.retrieval.hybrid import reciprocal_rank_fusion

bm25_results = [
    "chunk_A",
    "chunk_B",
    "chunk_C",
    "chunk_D",
]

dense_results = [
    "chunk_B",
    "chunk_E",
    "chunk_A",
    "chunk_F",
]

results = reciprocal_rank_fusion(
    ranked_lists=[bm25_results, dense_results],
    top_k=5,
)

print("RRF RESULTS")
print("=" * 50)

for result in results:
    print(result)
