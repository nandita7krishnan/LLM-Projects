"""Configuration settings for the Lenny Podcast Intelligence Engine."""

from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent.parent
TRANSCRIPTS_DIR = BASE_DIR / "Lenny's Podcast Transcripts Archive [public]"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHROMA_DB_DIR = BASE_DIR / "data" / "chroma_db"

# Ensure directories exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# Model settings - using smaller/faster models
LLM_MODEL = "llama3.2:latest"  # Was llama3.1:8b - this is faster
SMALL_LLM_MODEL = "llama3.2:latest"  # For quick answers
EMBEDDING_MODEL = "nomic-embed-text"

# Chunking settings
CHUNK_SIZE = 500  # tokens
CHUNK_OVERLAP = 50  # tokens

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"

