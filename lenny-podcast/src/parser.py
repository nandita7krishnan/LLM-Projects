"""Parse transcript files and extract structured data."""

import re
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class TranscriptSegment:
    """A segment of transcript with speaker and timestamp."""
    speaker: str
    timestamp: str
    text: str


@dataclass
class ParsedTranscript:
    """Parsed transcript with metadata."""
    guest_name: str
    segments: List[TranscriptSegment]
    
    @property
    def full_text_for_llm(self) -> str:
        """Get first ~8000 chars for LLM classification."""
        full = "\n\n".join(
            f"{seg.speaker}: {seg.text}" 
            for seg in self.segments
        )
        return full[:8000]  # Truncate for LLM context


def parse_transcript(filepath: Path) -> ParsedTranscript:
    """Parse a transcript file into structured segments.
    
    Args:
        filepath: Path to transcript .txt file
        
    Returns:
        ParsedTranscript with guest name and segments
    """
    # Extract guest name from filename
    guest_name = filepath.stem
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into segments by speaker pattern
    # Pattern: "Speaker Name (HH:MM:SS): text" or "Speaker Name: text"
    segments = []
    
    # Try to split by lines with speaker names
    lines = content.split('\n')
    current_speaker = None
    current_timestamp = "00:00:00"
    current_text = []
    
    speaker_pattern = re.compile(r'^([A-Za-z\s\'\-\.]+?)(?:\s*\((\d{2}:\d{2}:\d{2})\))?\s*:\s*(.+)$')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = speaker_pattern.match(line)
        if match:
            # Save previous segment
            if current_speaker and current_text:
                segments.append(TranscriptSegment(
                    speaker=current_speaker,
                    timestamp=current_timestamp,
                    text=' '.join(current_text)
                ))
            
            # Start new segment
            current_speaker = match.group(1).strip()
            if match.group(2):
                current_timestamp = match.group(2)
            current_text = [match.group(3).strip()]
        else:
            # Continue current segment
            if current_text:
                current_text.append(line)
    
    # Save last segment
    if current_speaker and current_text:
        segments.append(TranscriptSegment(
            speaker=current_speaker,
            timestamp=current_timestamp,
            text=' '.join(current_text)
        ))
    
    return ParsedTranscript(guest_name=guest_name, segments=segments)


def get_all_transcripts(transcripts_dir: Path) -> List[Path]:
    """Get all transcript .txt files.
    
    Args:
        transcripts_dir: Directory containing transcripts
        
    Returns:
        List of Path objects for .txt files
    """
    return sorted(transcripts_dir.glob("*.txt"))

