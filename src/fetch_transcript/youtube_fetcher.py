import re
from dataclasses import dataclass
from enum import Enum, auto
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound
)




class FetchStatus(Enum):
    SUCCESS = auto()
    DISABLED = auto()
    NOT_FOUND = auto()
    ERROR = auto()


@dataclass
class FetchResult:
    ok: bool
    status: FetchStatus
    transcript: str | None = None
    error: str | None = None




class YouTubeTranscriptFetcher:
    def __init__(self, languages=None):
        self.languages = languages or ["en", "vi"]
        self.ytt_api = YouTubeTranscriptApi()

    def fetch(self, video_id: str) -> FetchResult:
        """
        Fetch transcript + metadata + duration
        Return FetchResult
        """
        try:
            transcript_list = self.ytt_api.list(video_id)

            transcript = transcript_list.find_transcript(self.languages)
            segments = transcript.fetch()

            if not segments:
                raise RuntimeError("Transcript is empty")

            last_seg = segments[-1]
            duration_seconds = last_seg.start + last_seg.duration

            raw_text = "\n".join(
                f"[{seg.start:.2f}s] {seg.text}"
                for seg in segments
            )

            cleaned_text = self._clean_transcript(raw_text)

            payload = {
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

            return FetchResult(
                ok=True,
                status=FetchStatus.SUCCESS,
                transcript=payload
            )

        except TranscriptsDisabled:
            return FetchResult(
                ok=False,
                status=FetchStatus.DISABLED,
                error="Transcripts are disabled"
            )

        except NoTranscriptFound:
            return FetchResult(
                ok=False,
                status=FetchStatus.NOT_FOUND,
                error="No transcript for given languages"
            )

        except Exception as e:
            return FetchResult(
                ok=False,
                status=FetchStatus.ERROR,
                error=str(e)
            )

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
