from llm.gemini_client import GeminiClient
from llm.prompts import build_direct_summary_prompt
from schemas.output_format import DirectSummaryOutput


def run_short_flow(transcript: str, language: str = "English", summary_language: str = None, **kwargs):
    """
    Args:
        transcript: Video transcript text
        language: Video's original language
        summary_language: Language for summary output (defaults to video language if not provided)
    """
    gemini = GeminiClient()
    
    # Use summary_language if provided, otherwise fallback to video language
    output_language = summary_language if summary_language else language

    # Generate direct summary
    prompt = build_direct_summary_prompt(
        transcript=transcript,
        video_language=output_language
    )

    response = gemini.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
        config={
            "temperature": 0.2,
            "response_mime_type": "application/json",
            "response_json_schema": DirectSummaryOutput.model_json_schema(),
        }
    )
    summary_obj = DirectSummaryOutput.model_validate_json(response.text)

    return summary_obj
