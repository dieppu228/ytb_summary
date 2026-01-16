import re
from typing import List, Dict


class TranscriptSegmenter:
    """
    1. Parse transcript string with timestamps
    2. Segment transcript based on outline
    """

    TIMESTAMP_PATTERN = re.compile(r"\[(\d+(?:\.\d+)?)s\]")

    def __init__(self, transcript_text: str):
        self.raw_text = transcript_text
        self.segments = self._parse_transcript()

    # ---------- STEP 1: PARSE ----------

    def _parse_transcript(self) -> List[Dict]:
        """
        Convert:
        "[8.96s] hello [10.92s] world"
        →
        [
          {"start": 8.96, "end": 10.92, "text": "hello"},
          {"start": 10.92, "end": None, "text": "world"}
        ]
        """
        matches = list(self.TIMESTAMP_PATTERN.finditer(self.raw_text))
        segments = []

        for i, match in enumerate(matches):
            start_time = float(match.group(1))
            start_idx = match.end()

            if i + 1 < len(matches):
                end_time = float(matches[i + 1].group(1))
                end_idx = matches[i + 1].start()
            else:
                end_time = None
                end_idx = len(self.raw_text)

            text = self.raw_text[start_idx:end_idx].strip()

            if text:
                segments.append({
                    "start": start_time,
                    "end": end_time,
                    "text": text
                })

        return segments

    # ---------- STEP 2: SEGMENT BY OUTLINE ----------

    def segment_by_outline(self, outline) -> List[Dict]:
        """
        outline: List[SectionOutline]
        """
        sections = []

        for sec in outline:
            texts = []

            for seg in self.segments:
                if seg["end"] is not None and seg["end"] <= sec.start:
                    continue
                if seg["start"] >= sec.end:
                    break

                texts.append(seg["text"])

            sections.append({
                "section_id": sec.section_id,
                "title": sec.title,
                "start": sec.start,
                "end": sec.end,
                "text": " ".join(texts).strip()
            })

        return sections
