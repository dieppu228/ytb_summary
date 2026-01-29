from llm.gemini_client import GeminiClient
from preprocess.segmenter import TranscriptSegmenter
from llm.prompts import build_outline_prompt, build_section_summary_prompt, build_global_summary_prompt
from pipeline.video_segmentation import video_segmentation
from schemas.output_format import OutlineOutput, SectionSummaryOutput, GlobalSummaryOutput
import json

def run_long_flow(video_id: str, transcript: str, language: str, video_duration: float = None, summary_language: str = None, **kwargs):
    """
    Args:
        transcript: Video transcript text
        language: Video's original language
        video_duration: Duration in seconds
        summary_language: Language for summary output (defaults to video language if not provided)
    """

    # Use summary_language if provided, otherwise fallback to video language
    output_language = summary_language if summary_language else language

    # ===== STEP 1: Generate outline =====
    outline = video_segmentation(video_id, transcript, language, video_duration, summary_language)

    # ===== STEP 2: Segment transcript according to outline =====
    segmenter = TranscriptSegmenter(transcript)
    outlined_sections = segmenter.segment_by_outline(outline.sections)
    # ===== STEP 3: Summarize each section with memory =====
    gemini = GeminiClient()
    memory = ""
    section_summaries = []

    for section in outlined_sections:
        section_text = section["text"]

        prompt = build_section_summary_prompt(
            section_text=section_text,
            memory=memory,
            video_language=output_language
        )
        response = gemini.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
            "response_json_schema": SectionSummaryOutput.model_json_schema(),
        }
    )

        # ---- Parse JSON output ----
        summary_obj = SectionSummaryOutput.model_validate_json(response.text)

        # Save result
        section_summaries.append({
            "section_id": section["section_id"],
            "title": section["title"],
            "start": section["start"],
            "end": section["end"],
            "summary": summary_obj.summary,
        })

        # Update memory
        memory = summary_obj.summary
    
    print(json.dumps(section_summaries, indent=2, ensure_ascii=False))

    # ===== STEP 4: Global Summary =====
    section_summaries_text = "" 
    section_summaries_text = json.dumps(
        section_summaries,
        indent=2,
        ensure_ascii=False
    )
    prompt = build_global_summary_prompt(
        section_summaries=section_summaries_text,
        video_language=output_language   
    )
    response = gemini.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
            "response_json_schema": GlobalSummaryOutput.model_json_schema(),
        }
    )
    overall_summary = GlobalSummaryOutput.model_validate_json(response.text)

    return overall_summary
