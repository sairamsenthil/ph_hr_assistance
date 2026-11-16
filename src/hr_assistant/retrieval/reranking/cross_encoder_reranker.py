from sentence_transformers import CrossEncoder


DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:

    def __init__(self, model_name=DEFAULT_RERANKER_MODEL):

        self.model = CrossEncoder(model_name)

    def rerank(self, query, candidates, top_k=5):

        if not candidates:
            return []

        pairs = [
            (query, item["chunk"]["text"])
            for item in candidates
        ]

        scores = self.model.predict(pairs)

        reranked_results = []

        for item, score in zip(candidates, scores):

            result = item.copy()
            result["rerank_score"] = float(score)

            reranked_results.append(result)

        reranked_results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        return reranked_results[:top_k]
