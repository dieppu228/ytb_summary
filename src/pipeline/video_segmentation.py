from fetch_transcript.get_chapters import get_youtube_chapters
from llm.gemini_client import GeminiClient
from llm.prompts import build_outline_prompt
from schemas.output_format import OutlineOutput

def video_segmentation(video_id: str, transcript: str, language: str, video_duration: float = None, summary_language: str = None, **kwargs):
    # Get chapters if available
    chapters = get_youtube_chapters(video_id)
    if chapters:
        return chapters
    
    # Fallback: LLM segmentation if no chapters
    # Use summary_language if provided, otherwise fallback to video language
    output_language = summary_language if summary_language else language

    # ===== LLM Outline Segmentation =====
    prompt = build_outline_prompt(
        video_transcript=transcript,
        video_language=output_language,
        video_duration=video_duration,
    )
    gemini = GeminiClient()
    response = gemini.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
        config={
            "temperature": 0.0,
            "response_mime_type": "application/json",
            "response_json_schema": OutlineOutput.model_json_schema(),
        }
    )
    outline = OutlineOutput.model_validate_json(response.text)
    return outline