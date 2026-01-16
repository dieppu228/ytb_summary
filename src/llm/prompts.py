"""
Prompt templates for YouTube video summarization pipeline (CASE 1)
"""

# ==================================================
# 1. Outline / Segmentation Prompt
# ==================================================

OUTLINE_PROMPT = """
You are an expert content analyst.

Given a YouTube transcript with timestamps, split the video into coherent topical sections.

Transcript:
{video_transcript}

Rules:
- Do NOT summarize content
- Only detect topic boundaries where the subject matter clearly changes
- ALL sections must be contiguous and ordered chronologically
- Cover the ENTIRE video from start to end
- Each section must include:
  - section_id (integer, starting from 1)
  - title (concise topic description)
  - start (seconds, integer)
  - end (seconds, integer)
  - keywords (3-5 relevant strings)

Return a JSON object with this exact structure:
{{
  "sections": [
    {{
      "section_id": 1,
      "title": "Introduction",
      "start": 0,
      "end": 45,
      "keywords": ["intro", "welcome", "overview"]
    }},
    {{
      "section_id": 2,
      "title": "Main Topic",
      "start": 45,
      "end": 180,
      "keywords": ["concept", "explanation", "details"]
    }}
  ]
}}

IMPORTANT: 
- Include ALL sections found in the video
- The last section's end time must match the video's total duration
- Return valid JSON only, no additional text
"""


def build_outline_prompt(video_transcript: str) -> str:
    return OUTLINE_PROMPT.format(
        video_transcript=video_transcript
    )


# ==================================================
# 2. Section Summary Prompt
# ==================================================

SECTION_SUMMARY_PROMPT = """
You are summarizing one section of a long video.

Language:
{video_language}

Global context so far:
{memory}

Current section transcript:
{section_text}

Rules:
- The language used matches the language of the video
- Write a concise and clear summary
- Correct transcription errors silently
- Avoid repeating previous content
- Focus only on NEW information in this section

Return the result strictly in JSON format.
"""


def build_section_summary_prompt(
    section_text: str,
    memory: str,
    video_language: str
) -> str:
    return SECTION_SUMMARY_PROMPT.format(
        section_text=section_text,
        memory=memory,
        video_language=video_language
    )


# ==================================================
# 3. Overall Summary Prompt
# ==================================================

GLOBAL_SUMMARY_PROMPT = """
You are summarizing the entire video.

Language:
{video_language}

All section summaries:
{section_summaries}

Rules:
- The language used matches the language of the video
- Write a concise overall summary
- Cover the main points from all sections

Return the result strictly in JSON format.
{{
  "overall_summary": "Your summary here"
}}
"""


def build_global_summary_prompt(
    section_summaries: str,
    video_language: str
) -> str:
    return GLOBAL_SUMMARY_PROMPT.format(
        section_summaries=section_summaries,
        video_language=video_language
    )


