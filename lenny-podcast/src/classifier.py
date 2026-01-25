"""LLM-based episode classification."""

import json
import re
from dataclasses import dataclass, asdict
from typing import List
import requests


@dataclass
class EpisodeMetadata:
    """Metadata for a podcast episode."""
    guest_name: str
    topics: List[str]
    guest_role: str
    company_stage: str
    tactical_score: int
    contrarian_score: int
    key_quotes: List[str]
    one_line_summary: str


def classify_episode(guest_name: str, transcript_text: str, model: str = "llama3.1:8b") -> EpisodeMetadata:
    """Classify an episode using LLM.
    
    Args:
        guest_name: Name of the guest
        transcript_text: Transcript text (first ~8000 chars)
        model: Ollama model to use
        
    Returns:
        EpisodeMetadata with classification results
    """
    prompt = f"""Analyze this podcast transcript excerpt and provide structured metadata.

Guest: {guest_name}

Transcript excerpt:
{transcript_text}

Provide a JSON response with the following fields:
- guest_name: The guest's name
- topics: List of 3-5 main topics (e.g., "product-market fit", "growth", "hiring", "AI")
- guest_role: One of: founder, PM, designer, VC, exec, researcher, coach, or combination like "founder/PM"
- company_stage: One of: early-stage, growth, public, FAANG
- tactical_score: Integer 1-10 (1=philosophical, 10=highly tactical/actionable)
- contrarian_score: Integer 1-10 (1=conventional wisdom, 10=contrarian/unique perspective)
- key_quotes: List of 3 notable quotes from the transcript
- one_line_summary: One sentence summary of what this episode is about

Return ONLY valid JSON, no comments or extra text."""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code}")
    
    result = response.json()
    response_text = result.get("response", "")
    
    # Try to parse JSON response
    try:
        # Remove any markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        response_text = response_text.strip()
        
        # Remove any trailing comments (common LLM mistake)
        # Find the last } and truncate there
        last_brace = response_text.rfind('}')
        if last_brace != -1:
            response_text = response_text[:last_brace + 1]
        
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse LLM response for {guest_name}: {e}\nResponse: {response_text}")
    
    # Create EpisodeMetadata object
    return EpisodeMetadata(
        guest_name=data.get("guest_name", guest_name),
        topics=data.get("topics", []),
        guest_role=data.get("guest_role", "unknown"),
        company_stage=data.get("company_stage", "unknown"),
        tactical_score=int(data.get("tactical_score", 5)),
        contrarian_score=int(data.get("contrarian_score", 5)),
        key_quotes=data.get("key_quotes", []),
        one_line_summary=data.get("one_line_summary", "")
    )


def save_metadata(metadata_list: List[EpisodeMetadata], filepath: str):
    """Save metadata to JSON file.
    
    Args:
        metadata_list: List of EpisodeMetadata objects
        filepath: Path to save JSON file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump([asdict(m) for m in metadata_list], f, indent=2, ensure_ascii=False)


def load_metadata(filepath: str) -> List[EpisodeMetadata]:
    """Load metadata from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        List of EpisodeMetadata objects
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return [EpisodeMetadata(**item) for item in data]

