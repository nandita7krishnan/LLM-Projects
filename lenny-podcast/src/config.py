"""Configuration settings for the Lenny Podcast Intelligence Engine."""

from pathlib import Path
from dotenv import load_dotenv

# Load .env file from parent llm folder
load_dotenv(Path(__file__).parent.parent.parent / ".env")

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

# Groq settings (fast cloud inference - get free key at console.groq.com)
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast and free
USE_GROQ = bool(GROQ_API_KEY)  # Auto-enable if key is set

