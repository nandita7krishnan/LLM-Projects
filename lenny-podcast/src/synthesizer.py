"""Synthesis and answer generation using LLM."""

from dataclasses import dataclass
from typing import List
import requests
from retriever import retrieve_chunks, RetrievalResult
from config import LLM_MODEL, SMALL_LLM_MODEL


@dataclass
class SynthesizedAnswer:
    """A synthesized answer with sources."""
    query: str
    answer: str
    sources: List[dict]


def synthesize_answer(
    query: str,
    n_chunks: int = 10,
    model: str = LLM_MODEL
) -> SynthesizedAnswer:
    """Generate a comprehensive answer from multiple sources.
    
    Args:
        query: User query
        n_chunks: Number of chunks to retrieve
        model: LLM model to use
        
    Returns:
        SynthesizedAnswer with answer and citations
    """
    # Retrieve relevant chunks
    chunks = retrieve_chunks(query, n_results=n_chunks)
    
    if not chunks:
        return SynthesizedAnswer(
            query=query,
            answer="No relevant information found.",
            sources=[]
        )
    
    # Build context from chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}] {chunk.guest_name} ({chunk.guest_role}) @ {chunk.start_timestamp}\n{chunk.text}\n"
        )
    
    context = "\n".join(context_parts)
    
    # Generate answer
    prompt = f"""Based on the following podcast transcript excerpts, answer this question: {query}

Provide a comprehensive answer that synthesizes information from multiple sources. 
Include inline citations like [Source 1] when referencing specific information.
Be specific and tactical when possible.

Context:
{context}

Answer:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code}")
    
    result = response.json()
    answer = result.get("response", "")
    
    # Build sources list
    sources = [
        {
            "guest": chunk.guest_name,
            "role": chunk.guest_role,
            "timestamp": chunk.start_timestamp,
            "text": chunk.text[:200] + "..."
        }
        for chunk in chunks
    ]
    
    return SynthesizedAnswer(
        query=query,
        answer=answer,
        sources=sources
    )


def quick_answer(query: str, model: str = SMALL_LLM_MODEL) -> str:
    """Generate a quick, concise answer using a smaller model.
    
    Args:
        query: User query
        model: LLM model to use (defaults to smaller model)
        
    Returns:
        Concise answer string
    """
    # Retrieve fewer chunks
    chunks = retrieve_chunks(query, n_results=5)
    
    if not chunks:
        return "No relevant information found."
    
    # Build brief context
    context = "\n\n".join([
        f"{chunk.guest_name}: {chunk.text[:300]}..."
        for chunk in chunks[:3]
    ])
    
    prompt = f"""Answer this question briefly based on these podcast excerpts: {query}

Context:
{context}

Provide a concise 2-3 sentence answer:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code}")
    
    result = response.json()
    return result.get("response", "")


def recommend_episodes(
    user_context: str,
    n_chunks: int = 15,
    model: str = LLM_MODEL
) -> SynthesizedAnswer:
    """Recommend episodes based on user context.
    
    Args:
        user_context: Description of user's situation/needs
        n_chunks: Number of chunks to consider
        model: LLM model to use
        
    Returns:
        SynthesizedAnswer with recommendations
    """
    # Retrieve relevant chunks
    chunks = retrieve_chunks(user_context, n_results=n_chunks)
    
    if not chunks:
        return SynthesizedAnswer(
            query=user_context,
            answer="No relevant episodes found.",
            sources=[]
        )
    
    # Group by episode
    episodes = {}
    for chunk in chunks:
        guest = chunk.guest_name
        if guest not in episodes:
            episodes[guest] = {
                "guest": guest,
                "role": chunk.guest_role,
                "topics": chunk.topics,
                "tactical_score": chunk.tactical_score,
                "summary": chunk.summary,
                "relevance": chunk.distance
            }
    
    # Build episode list
    episode_list = "\n".join([
        f"- {ep['guest']} ({ep['role']}): {ep['summary']} [Tactical: {ep['tactical_score']}/10]"
        for ep in episodes.values()
    ])
    
    prompt = f"""Based on this user's context, recommend the most relevant podcast episodes:

User Context: {user_context}

Available Episodes:
{episode_list}

Provide 3-5 episode recommendations with brief explanations of why each is relevant.
Order them from most to least relevant.

Recommendations:"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code}")
    
    result = response.json()
    answer = result.get("response", "")
    
    sources = [
        {
            "guest": ep["guest"],
            "role": ep["role"],
            "summary": ep["summary"]
        }
        for ep in episodes.values()
    ]
    
    return SynthesizedAnswer(
        query=user_context,
        answer=answer,
        sources=sources
    )

