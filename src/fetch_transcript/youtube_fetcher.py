import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound
)


class YouTubeTranscriptFetcher:
    def __init__(self, languages=None):
        self.languages = languages or ["en", "vi"]
        self.ytt_api = YouTubeTranscriptApi()

    def fetch(self, video_id: str) -> dict:
        """
        Fetch transcript + metadata + duration
        Return JSON-serializable dict
        """
        try:
            transcript_list = self.ytt_api.list(video_id)

            transcript = transcript_list.find_transcript(self.languages)
            segments = transcript.fetch()

            if not segments:
                raise RuntimeError("Transcript is empty")

            # ===== duration calculation =====
            last_seg = segments[-1]
            duration_seconds = last_seg.start + last_seg.duration

            raw_text = "\n".join(
                f"[{seg.start:.2f}s] {seg.text}"
                for seg in segments
            )


            cleaned_text = self._clean_transcript(raw_text)

            return {
                "video_id": transcript.video_id,
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable,
                "translation_languages": transcript.translation_languages,
                "duration": {
                    "seconds": round(duration_seconds, 2),
                    "minutes": round(duration_seconds / 60, 2)
                },

                "text": cleaned_text,
            }

        except TranscriptsDisabled:
            raise RuntimeError(
                f"Transcripts are disabled for video: {video_id}"
            )

        except NoTranscriptFound:
            raise RuntimeError(
                f"No transcript found for languages={self.languages}"
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch transcript: {e}")

    # CLEAN LOGIC
    def _clean_transcript(self, text: str) -> str:
        lines = text.splitlines()
        cleaned = []

        for line in lines:
            line = re.sub(
                r"\[(?!\d+(\.\d+)?s\]).*?\]",
                "",
                line
            )
            line = re.sub(r"[♪]", "", line)
            line = re.sub(r"\s+", " ", line).strip()

            if re.fullmatch(r"\[\d+(\.\d+)?s\]", line):
                continue
            if not line:
                continue

            cleaned.append(line)

        text_cleaned = " ".join(cleaned)
        text_cleaned = text_cleaned.capitalize()
        text_cleaned = re.sub(
            r"([.!?]\s+)([a-z])",
            lambda m: m.group(1) + m.group(2).upper(),
            text_cleaned
        )
        return text_cleaned
