
# from src.hr_assistant.config import (
#     PROJECT_ROOT,
#     RAW_DATA_DIR,
#     PROCESSED_DATA_DIR,
#     CHROMA_DB_DIR,
#     OLLAMA_BASE_URL,
#     GENERATION_MODEL,
#     EMBEDDING_MODEL,
# )

# print("Project root:", PROJECT_ROOT)
# print("Raw documents:", RAW_DATA_DIR)
# print("Processed documents:", PROCESSED_DATA_DIR)
# print("ChromaDB:", CHROMA_DB_DIR)
# print("Ollama:", OLLAMA_BASE_URL)
# print("Generation model:", GENERATION_MODEL)
# print("Embedding model:", EMBEDDING_MODEL)

from src.hr_assistant.ingestion.document_processor import process_pdf

documents = process_pdf("hr_policy_manual.pdf")

print("\n========== DOCUMENT STRUCTURE INSPECTION ==========\n")

for document in documents:

    text = document["cleaned_text"]

    print(f"\n--- PAGE {document['metadata']['page']} ---")

    for line in text.splitlines():

        line = line.strip()

        if line:
            print(line)