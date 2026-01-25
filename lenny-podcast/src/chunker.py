"""Chunk transcripts with timestamp preservation."""

import re
from dataclasses import dataclass
from typing import List
from parser import ParsedTranscript, TranscriptSegment


@dataclass
class Chunk:
    """A chunk of transcript with metadata."""
    guest_name: str
    chunk_id: str
    start_timestamp: str
    end_timestamp: str
    speakers: List[str]
    text: str
    token_count: int


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 chars)."""
    return len(text) // 4


def chunk_transcript(parsed: ParsedTranscript, chunk_size: int = 500, overlap: int = 50) -> List[Chunk]:
    """Chunk a transcript into segments with timestamps.
    
    Args:
        parsed: ParsedTranscript object
        chunk_size: Target chunk size in tokens
        overlap: Overlap between chunks in tokens
        
    Returns:
        List of Chunk objects
    """
    chunks = []
    current_text = []
    current_speakers = set()
    current_tokens = 0
    start_timestamp = None
    end_timestamp = None
    chunk_idx = 0
    
    for segment in parsed.segments:
        segment_text = f"{segment.speaker}: {segment.text}"
        segment_tokens = estimate_tokens(segment_text)
        
        # Initialize start timestamp
        if start_timestamp is None:
            start_timestamp = segment.timestamp
        
        # If adding this segment would exceed chunk size, create a chunk
        if current_tokens + segment_tokens > chunk_size and current_text:
            # Create chunk
            chunks.append(Chunk(
                guest_name=parsed.guest_name,
                chunk_id=f"{parsed.guest_name}_{chunk_idx:03d}",
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                speakers=sorted(list(current_speakers)),
                text="\n\n".join(current_text),
                token_count=current_tokens
            ))
            
            chunk_idx += 1
            
            # Keep overlap
            overlap_tokens = 0
            overlap_text = []
            for i in range(len(current_text) - 1, -1, -1):
                text_tokens = estimate_tokens(current_text[i])
                if overlap_tokens + text_tokens <= overlap:
                    overlap_text.insert(0, current_text[i])
                    overlap_tokens += text_tokens
                else:
                    break
            
            current_text = overlap_text
            current_tokens = overlap_tokens
            current_speakers = set()
            start_timestamp = segment.timestamp
        
        # Add segment to current chunk
        current_text.append(segment_text)
        current_speakers.add(segment.speaker)
        current_tokens += segment_tokens
        end_timestamp = segment.timestamp
    
    # Add final chunk
    if current_text:
        chunks.append(Chunk(
            guest_name=parsed.guest_name,
            chunk_id=f"{parsed.guest_name}_{chunk_idx:03d}",
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            speakers=sorted(list(current_speakers)),
            text="\n\n".join(current_text),
            token_count=current_tokens
        ))
    
    return chunks

