# 1. Outline / Segmentation Prompt

OUTLINE_PROMPT = """
You are an expert content analyst specializing in high-level video structure analysis.

Video Language: {video_language}
Video Duration: {video_duration} seconds (~{video_duration_minutes} minutes)

Given a YouTube transcript with timestamps, identify only the MOST SIGNIFICANT topical sections.

Before creating sections, think step by step about the video's overall structure and flow.

Transcript:
{video_transcript}

TARGET SECTION COUNT (strict guidelines):
- Medium videos (10-30 min): 3-5 sections maximum  
- Long videos (30-60 min): 4-7 sections maximum
- Very long videos (60-120 min): 5-8 sections maximum
- Extra long videos (>120 min): 6-10 sections maximum

CORE PRINCIPLES:
- Think "book chapters" not "article sections"
- Each section should cover 10-20 minutes of content minimum (for long videos)
- Only create a new section when there's a FUNDAMENTAL shift in topic/theme
- Merge related discussions, examples, and sub-topics into unified sections
- Prefer fewer, more comprehensive sections over many small ones
- Avoid sections shorter than 5 minutes unless video is very short

WHAT QUALIFIES AS A SECTION BOUNDARY:
Major topic change (e.g., from theory to practice, problem to solution)
Clear structural markers (intro → main content → conclusion)
Significant shift in discussion focus or context

WHAT DOES NOT QUALIFY:
Brief tangents or examples within a broader discussion
Minor sub-points or supporting arguments
Q&A variations on the same core topic
Transitional moments or recaps

Each section must include:
- section_id (integer, starting from 1)
- title (broad, encompassing theme in {video_language})
- start (seconds, integer)
- end (seconds, integer)
- keywords (3-5 core concepts in {video_language})

Return a JSON object:
{{
  "sections": [
    {{
      "section_id": 1,
      "title": "Giới thiệu và Nền tảng lý thuyết",
      "start": 0,
      "end": 300,
      "keywords": ["giới thiệu", "lý thuyết", "khái niệm cơ bản"]
    }},
    {{
      "section_id": 2,
      "title": "Ứng dụng thực tế và Case studies",
      "start": 300,
      "end": 600,
      "keywords": ["thực hành", "ví dụ", "ứng dụng"]
    }}
  ]
}}

VALIDATION:
- Total sections should be WELL BELOW the maximum for this video length
- Each section represents a major content block, not a minor point
- Last section end = {video_duration}
- When in doubt, MERGE sections rather than split them

Return ONLY valid JSON, no explanations.
"""


def build_outline_prompt(video_transcript: str, video_language: str = "English", video_duration: float = None) -> str:
    video_duration_minutes = video_duration // 60
    
    return OUTLINE_PROMPT.format(
        video_transcript=video_transcript,
        video_language=video_language,
        video_duration=video_duration,
        video_duration_minutes=video_duration_minutes
    )


# 2. Section Summary Prompt

SECTION_SUMMARY_PROMPT = """
You are summarizing one section of a long video.

Language:
{video_language}

Global context so far:
{memory}

Current section transcript:
{section_text}

Rules:
- The language used matches the language of the video is {video_language}
- Write a concise and clear summary
- Correct transcription errors silently
- Avoid repeating previous content
- Focus only on NEW information in this section
- The summary MUST be written in {video_language} only, not in any other language.

Return the result strictly in JSON format with language {video_language}.
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


# 3. Overall Summary Prompt

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
- The global summary and all takeaways MUST be written in {video_language} only.

OUTPUT SCHEMA:
{{
  "global_summary": "string (2-4 sentences summarizing the entire video in {video_language})",
  "section_takeaways": [
    {{
      "section_id": number (copy exactly from input),
      "title": "string (copy exactly from input) using {video_language}",
      "start": number (copy exactly from input),
      "end": number (copy exactly from input),
      "takeaways": [
        "string (key point 1 in {video_language})",
        "string (key point 2 in {video_language})",
        "string (key point 3, optional in {video_language})",
        "string (key point 4, optional in {video_language})"
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
    video_language: str,
) -> str:
    return GLOBAL_SUMMARY_PROMPT.format(
        section_summaries=section_summaries,
        video_language=video_language
    )



# 4. Direct Summary Prompt (for short videos)

DIRECT_SUMMARY_PROMPT = """
You are an expert content analyst summarizing a short YouTube video.

VIDEO LANGUAGE: {video_language}

TRANSCRIPT:
{transcript}

YOUR TASK:
Create a summary that is PROPORTIONAL to the video content length.

IMPORTANT LENGTH GUIDELINES:
- For music videos, lyrics, or very short content (1-3 min): Write 3-5 sentences MAX. Just describe what the song/content is about.
- For short explanatory videos (3-5 min): Write 5-7 sentences covering the main point.
- For medium content (5-10 min): Write a paragraph (8-10 sentences) with key details.

DETECT CONTENT TYPE:
- If the transcript contains mostly lyrics, repetitive phrases, or musical content → Keep summary VERY brief (1-2 sentences describing the song's theme/mood)
- If the transcript is educational/informational → Include main points but stay concise

RULES:
- Write in {video_language} ONLY
- Summary should NEVER be longer than the original transcript
- For music: Just describe the theme, mood, and what the song is about
- For tutorials: Focus on the main takeaway, not every detail
- Correct any transcription errors silently
- Preserve the speaker's original intent and tone

OUTPUT FORMAT (JSON):
{{
  "summary": "Your concise summary here. Keep it proportional to the content length."
}}

Remember: A good summary is SHORTER than the original, not longer.
"""


def build_direct_summary_prompt(
    transcript: str,
    video_language: str = "English"
) -> str:
    return DIRECT_SUMMARY_PROMPT.format(
        transcript=transcript,
        video_language=video_language
    )



