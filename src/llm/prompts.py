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
    video_language: str = "English"
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
You are given a list of video sections in JSON format.
Each section contains:
- section_id: unique identifier for the section
- title: section title
- start: timestamp in seconds (float)
- end: timestamp in seconds (float)
- summary: text description of the section

Your tasks:
1. Write a concise global summary (2-4 sentences) that captures the main theme and purpose of the entire video.
2. For EACH section, extract 2-4 key takeaways based ONLY on that section's "summary" field.
3. Copy the "section_id", "title", "start", and "end" fields EXACTLY as provided in the input JSON.

CRITICAL RULES:
- Do NOT modify, round, or recalculate any numeric values (section_id, start, end).
- Do NOT merge, split, add, or remove sections.
- Do NOT invent timestamps or data not present in the input.
- Do NOT skip any sections from the input.
- Each takeaway should be a clear, actionable insight or key point (one sentence each).
- Output MUST be valid JSON matching the schema below.

OUTPUT SCHEMA:
{{
  "global_summary": "string (2-4 sentences summarizing the entire video)",
  "section_takeaways": [
    {{
      "section_id": number (copy exactly from input),
      "title": "string (copy exactly from input)",
      "start": number (copy exactly from input),
      "end": number (copy exactly from input),
      "takeaways": [
        "string (key point 1)",
        "string (key point 2)",
        "string (key point 3, optional)",
        "string (key point 4, optional)"
      ]
    }}
  ]
}}

VIDEO LANGUAGE: {video_language}

INPUT SECTIONS (JSON):
{section_summaries}

Now generate the output following the schema exactly.
"""


def build_global_summary_prompt(
    section_summaries: str,
    video_language: str = "English"
) -> str:
    return GLOBAL_SUMMARY_PROMPT.format(
        section_summaries=section_summaries,
        video_language=video_language
    )



# ==================================================
# 4. Direct Summary Prompt (for short videos)
# ==================================================

DIRECT_SUMMARY_PROMPT = """
You are summarizing a short YouTube video.

Language:
{video_language}

Transcript:
{transcript}

Rules:
- The language used matches the language of the video
- Write a clear, concise summary
- Correct transcription errors silently
- Capture all main points

Return the result strictly in JSON format.
{{
  "summary": "Your summary here"
}}
"""


def build_direct_summary_prompt(
    transcript: str,
    video_language: str = "English"
) -> str:
    return DIRECT_SUMMARY_PROMPT.format(
        transcript=transcript,
        video_language=video_language
    )



