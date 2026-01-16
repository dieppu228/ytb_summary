from typing import List, Optional
from pydantic import BaseModel, Field

# ==================================================
# 0. Transcript Fetch Output
# ==================================================

class TranscriptMeta(BaseModel):
    video_id: str
    language: str
    language_code: str
    is_generated: bool
    is_translatable: bool
    translation_languages: List[str]
    duration: float = Field(
        ...,
        description="Total video duration in seconds"
    )


class TranscriptOutput(BaseModel):
    meta: TranscriptMeta
    raw_text: str = Field(
        ...,
        description="Original transcript text with timestamps"
    )
    cleaned_text: str = Field(
        ...,
        description="Cleaned transcript text used for LLM processing"
    )


# ==================================================
# 1. Semantic Outline (Video Segmentation)
# ==================================================

class SectionOutline(BaseModel):
    section_id: int = Field(
        ...,
        description="Incremental section index"
    )
    title: str = Field(
        ...,
        description="Short descriptive title of the section"
    )
    start: float = Field(
        ...,
        description="Start time of the section in seconds"
    )
    end: float = Field(
        ...,
        description="End time of the section in seconds"
    )
    keywords: List[str] = Field(
        ...,
        description="Key terms representing the section topic"
    )


class OutlineOutput(BaseModel):
    sections: List[SectionOutline]


# ==================================================
# 2. Chunk-level Summary
# ==================================================

class ChunkSummaryOutput(BaseModel):
    section_id: int
    chunk_index: int = Field(
        ...,
        description="Index of the chunk inside the section"
    )
    summary: str = Field(
        ...,
        description="Summary of this transcript chunk"
    )


# ==================================================
# 3. Section-level Summary
# ==================================================

class SectionSummaryOutput(BaseModel):
    section_id: int
    title: str
    start: float
    end: float
    summary: str = Field(
        ...,
        description="Final summary of the entire section"
    )



# ==================================================
# 4. Global Video Summary
# ==================================================

class GlobalSummaryOutput(BaseModel):
    global_summary: str = Field(
        ...,
        description="High-level summary of the entire video"
    )
    key_takeaways: List[str] = Field(
        ...,
        description="Important insights extracted from the video"
    )


# ==================================================
# 5. Final Client Response (API Output)
# ==================================================

class FinalSection(BaseModel):
    section_id: int
    title: str
    start: float
    end: float
    summary: str
    keywords: List[str]


class FinalVideoOutput(BaseModel):
    video_id: str
    duration: float

    language: str
    language_code: str
    is_generated: bool

    sections: List[FinalSection]

    global_summary: str
    key_takeaways: List[str]

    model_info: Optional[dict] = Field(
        default=None,
        description="Metadata about LLM models used in the pipeline"
    )
