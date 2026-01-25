"""Retrieval functions for querying the vector database."""

from dataclasses import dataclass
from typing import List, Optional
import chromadb
from pathlib import Path
from embedder import get_embedding, init_chroma_db
from config import CHROMA_DB_DIR


@dataclass
class RetrievalResult:
    """A single retrieval result."""
    chunk_id: str
    guest_name: str
    guest_role: str
    start_timestamp: str
    end_timestamp: str
    text: str
    distance: float
    topics: List[str]
    tactical_score: int
    contrarian_score: int
    summary: str


def retrieve_chunks(
    query: str,
    n_results: int = 10,
    min_tactical_score: Optional[int] = None,
    topics: Optional[List[str]] = None,
    db_path: Path = CHROMA_DB_DIR
) -> List[RetrievalResult]:
    """Retrieve relevant chunks for a query.
    
    Args:
        query: Search query
        n_results: Number of results to return
        min_tactical_score: Filter by minimum tactical score
        topics: Filter by topics
        db_path: Path to ChromaDB
        
    Returns:
        List of RetrievalResult objects
    """
    # Initialize DB
    _, collection = init_chroma_db(db_path)
    
    # Get query embedding
    query_embedding = get_embedding(query)
    
    # Build where filter
    where_filter = {}
    if min_tactical_score is not None:
        where_filter["tactical_score"] = {"$gte": min_tactical_score}
    
    # Query collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter if where_filter else None
    )
    
    # Parse results
    retrieved = []
    if results and results.get('ids') and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            
            # Filter by topics if specified
            if topics:
                chunk_topics = metadata.get('topics', '').split(',')
                if not any(t in chunk_topics for t in topics):
                    continue
            
            retrieved.append(RetrievalResult(
                chunk_id=results['ids'][0][i],
                guest_name=metadata.get('guest_name', ''),
                guest_role=metadata.get('guest_role', ''),
                start_timestamp=metadata.get('start_timestamp', ''),
                end_timestamp=metadata.get('end_timestamp', ''),
                text=results['documents'][0][i],
                distance=results['distances'][0][i],
                topics=metadata.get('topics', '').split(',') if metadata.get('topics') else [],
                tactical_score=metadata.get('tactical_score', 0),
                contrarian_score=metadata.get('contrarian_score', 0),
                summary=metadata.get('summary', '')
            ))
    
    return retrieved


def retrieve_by_guest(guest_name: str, n_results: int = 10, db_path: Path = CHROMA_DB_DIR) -> List[RetrievalResult]:
    """Retrieve chunks from a specific guest.
    
    Args:
        guest_name: Name of guest
        n_results: Number of results
        db_path: Path to ChromaDB
        
    Returns:
        List of RetrievalResult objects
    """
    _, collection = init_chroma_db(db_path)
    
    results = collection.get(
        where={"guest_name": guest_name},
        limit=n_results
    )
    
    retrieved = []
    if results and results.get('ids'):
        for i in range(len(results['ids'])):
            metadata = results['metadatas'][i]
            retrieved.append(RetrievalResult(
                chunk_id=results['ids'][i],
                guest_name=metadata.get('guest_name', ''),
                guest_role=metadata.get('guest_role', ''),
                start_timestamp=metadata.get('start_timestamp', ''),
                end_timestamp=metadata.get('end_timestamp', ''),
                text=results['documents'][i],
                distance=0.0,
                topics=metadata.get('topics', '').split(',') if metadata.get('topics') else [],
                tactical_score=metadata.get('tactical_score', 0),
                contrarian_score=metadata.get('contrarian_score', 0),
                summary=metadata.get('summary', '')
            ))
    
    return retrieved


def get_all_guests(db_path: Path = CHROMA_DB_DIR) -> List[str]:
    """Get list of all guests in database.
    
    Args:
        db_path: Path to ChromaDB
        
    Returns:
        Sorted list of guest names
    """
    _, collection = init_chroma_db(db_path)
    
    results = collection.get()
    
    if results and results.get('metadatas'):
        guests = set(m.get('guest_name', '') for m in results['metadatas'])
        return sorted(list(guests))
    
    return []


def get_episodes_by_topic(topic: str, db_path: Path = CHROMA_DB_DIR) -> List[tuple]:
    """Get episodes covering a specific topic.
    
    Args:
        topic: Topic to search for
        db_path: Path to ChromaDB
        
    Returns:
        List of (guest_name, metadata_dict) tuples
    """
    _, collection = init_chroma_db(db_path)
    
    # Get all chunks
    results = collection.get()
    
    episodes = {}
    if results and results.get('metadatas'):
        for metadata in results['metadatas']:
            topics = metadata.get('topics', '').split(',')
            if any(topic.lower() in t.lower() for t in topics):
                guest = metadata.get('guest_name', '')
                if guest not in episodes:
                    episodes[guest] = metadata
    
    return sorted(episodes.items())

