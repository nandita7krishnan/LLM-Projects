"""Embedding and vector database operations."""

import chromadb
from chromadb.config import Settings
import requests
from typing import List, Optional
from pathlib import Path
from chunker import Chunk
from classifier import EpisodeMetadata


def get_embedding(text: str, model: str = "nomic-embed-text") -> List[float]:
    """Get embedding from Ollama.
    
    Args:
        text: Text to embed
        model: Embedding model name
        
    Returns:
        Embedding vector
    """
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": model,
            "prompt": text
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama embedding error: {response.status_code}")
    
    result = response.json()
    return result.get("embedding", [])


def init_chroma_db(db_path: Path, collection_name: str = "lenny_podcast_chunks"):
    """Initialize ChromaDB client and collection.
    
    Args:
        db_path: Path to ChromaDB directory
        collection_name: Name of collection
        
    Returns:
        Tuple of (client, collection)
    """
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    return client, collection


def add_chunks_to_db(
    collection,
    chunks: List[Chunk],
    metadata_dict: dict,
    embedding_model: str = "nomic-embed-text"
) -> dict:
    """Add chunks to ChromaDB with embeddings.
    
    Args:
        collection: ChromaDB collection
        chunks: List of Chunk objects
        metadata_dict: Dict mapping guest_name to EpisodeMetadata
        embedding_model: Model to use for embeddings
        
    Returns:
        Dict with stats: added, skipped, errors
    """
    stats = {"added": 0, "skipped": 0, "errors": 0}
    
    # Get existing IDs to avoid duplicates
    existing_ids = set()
    try:
        existing = collection.get()
        if existing and existing.get('ids'):
            existing_ids = set(existing['ids'])
    except:
        pass
    
    for chunk in chunks:
        # Skip if already exists
        if chunk.chunk_id in existing_ids:
            stats["skipped"] += 1
            continue
        
        try:
            # Get embedding
            embedding = get_embedding(chunk.text, model=embedding_model)
            
            # Get episode metadata
            episode_meta = metadata_dict.get(chunk.guest_name)
            
            # Prepare metadata
            metadata = {
                "guest_name": chunk.guest_name,
                "start_timestamp": chunk.start_timestamp,
                "end_timestamp": chunk.end_timestamp,
                "speakers": ",".join(chunk.speakers),
                "token_count": chunk.token_count,
            }
            
            # Add episode metadata if available
            if episode_meta:
                metadata.update({
                    "topics": ",".join(episode_meta.topics),
                    "guest_role": episode_meta.guest_role,
                    "company_stage": episode_meta.company_stage,
                    "tactical_score": episode_meta.tactical_score,
                    "contrarian_score": episode_meta.contrarian_score,
                    "summary": episode_meta.one_line_summary
                })
            
            # Add to collection
            collection.add(
                ids=[chunk.chunk_id],
                embeddings=[embedding],
                documents=[chunk.text],
                metadatas=[metadata]
            )
            
            stats["added"] += 1
            
        except Exception as e:
            stats["errors"] += 1
            print(f"Error adding chunk {chunk.chunk_id}: {e}")
    
    return stats

