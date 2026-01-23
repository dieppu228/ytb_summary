# src/pipeline/short_flow.py

from llm.gemini_client import GeminiClient
from llm.prompts import build_direct_summary_prompt
from schemas.output_format import DirectSummaryOutput


def run_short_flow(transcript: str, **kwargs):
    gemini = GeminiClient()
    
    # Extract optional parameters
    video_language = transcript

    # Generate direct summary
    prompt = build_direct_summary_prompt(
        transcript=transcript,
        video_language=video_language
    )

    response = gemini.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": DirectSummaryOutput.model_json_schema(),
        }
    )
    summary_obj = DirectSummaryOutput.model_validate_json(response.text)

    return summary_obj
