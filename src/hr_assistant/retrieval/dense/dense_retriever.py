
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"

QUERY_PREFIX = (
    "Represent this sentence for searching relevant passages: "
)


class DenseRetriever:

    def __init__(
        self,
        persist_directory: str,
        collection_name: str = "hr_policy_dense_children",
        model_name: str = DEFAULT_MODEL,
    ):
        self.model = SentenceTransformer(model_name)

        self.client = chromadb.PersistentClient(
            path=str(persist_directory)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def index_chunks(self, chunks, batch_size=32):

        children = [
            chunk for chunk in chunks
            if chunk.get("chunking_strategy") == "child"
        ]

        for start in range(0, len(children), batch_size):

            batch = children[start:start + batch_size]

            texts = [chunk["text"] for chunk in batch]

            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )

            metadatas = []

            for chunk in batch:
                metadata = {
                    "document_id": str(chunk["document_id"]),
                    "chunking_strategy": "child",
                    "parent_chunk_id": str(
                        chunk["parent_chunk_id"]
                    ),
                    "page_start": int(chunk["page_start"]),
                    "page_end": int(chunk["page_end"]),
                }

                if chunk.get("policy_title") is not None:
                    metadata["policy_title"] = str(
                        chunk["policy_title"]
                    )

                if chunk.get("policy_number") is not None:
                    metadata["policy_number"] = str(
                        chunk["policy_number"]
                    )

                metadatas.append(metadata)

            self.collection.upsert(
                ids=[chunk["chunk_id"] for chunk in batch],
                documents=texts,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
            )

        return {
            "total_children": len(children),
            "stored_vectors": self.collection.count(),
        }

    
    def search(
     self,
     query: str,
     top_k: int = 5,
     min_similarity: float | None = None,
     where: dict | None = None,
    ):

     total = self.collection.count()

     if total == 0:
        return []

     query_embedding = self.model.encode(
        [QUERY_PREFIX + query],
        normalize_embeddings=True,
        convert_to_numpy=True,
     )[0]

     query_args = {
        "query_embeddings": [query_embedding.tolist()],
        "n_results": top_k,
        "include": [
            "documents",
            "metadatas",
            "distances",
        ],
     }

    # Apply metadata filtering when provided
     if where is not None:
        query_args["where"] = where

     results = self.collection.query(**query_args)

     retrieved = []

     for i, chunk_id in enumerate(results["ids"][0]):

        distance = results["distances"][0][i]
        similarity = 1 - distance

        if (
             min_similarity is not None
            and similarity < min_similarity
        ):
            continue

        retrieved.append({
            "chunk_id": chunk_id,
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": distance,
            "similarity": similarity,
        })

     return retrieved

