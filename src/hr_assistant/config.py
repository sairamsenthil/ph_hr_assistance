from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Vector database directory
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"

# Local LLM models
GENERATION_MODEL = "qwen3:8b"
EMBEDDING_MODEL = "mxbai-embed-large:latest"

# ChromaDB configuration
COLLECTION_NAME = "hr_policy_chunks"
