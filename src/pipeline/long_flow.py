# src/pipeline/long_flow.py

from llm.gemini_client import GeminiClient
from preprocess.segmenter import TranscriptSegmenter
from llm.prompts import build_outline_prompt, build_section_summary_prompt, build_global_summary_prompt
from schemas.output_format import OutlineOutput, SectionSummaryOutput, GlobalSummaryOutput
import json

def run_long_flow(transcript: str,language: str, video_duration: float = None, **kwargs):

    # ===== STEP 1: Generate outline =====
    video_transcript = transcript
    prompt = build_outline_prompt(
        video_transcript=transcript,
        video_language=language,
        video_duration=video_duration,
    )
    gemini = GeminiClient()
    response = gemini.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": OutlineOutput.model_json_schema(),
        }
    )
    outline = OutlineOutput.model_validate_json(response.text)

    # ===== STEP 2: Segment transcript according to outline =====
    segmenter = TranscriptSegmenter(video_transcript)
    outlined_sections = segmenter.segment_by_outline(outline.sections)
    
    # ===== STEP 3: Summarize each section with memory =====
    memory = ""
    section_summaries = []

    for section in outlined_sections:
        section_text = section["text"]

        prompt = build_section_summary_prompt(
            section_text=section_text,
            memory=memory,
            video_language=language
        )
        response = gemini.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config={
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
    

    # ===== STEP 4: Global Summary =====
    section_summaries_text = "" 
    section_summaries_text = json.dumps(
        section_summaries,
        indent=2,
        ensure_ascii=False
    )
    prompt = build_global_summary_prompt(
        section_summaries=section_summaries_text,
        video_language=language   
    )
    response = gemini.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": GlobalSummaryOutput.model_json_schema(),
        }
    )
    overall_summary = GlobalSummaryOutput.model_validate_json(response.text)

    return overall_summary
