from pipeline.short_flow import run_short_flow
from pipeline.long_flow import run_long_flow
from pipeline.audio_summary import ytb_video_to_transcript
from utils.token_counter import estimate_tokens
from fetch_transcript.youtube_fetcher import YouTubeTranscriptFetcher
from llm.get_metadata import get_video_metadata


LONG_TRANSCRIPT_THRESHOLD = 1500



class VideoToTextNode:
    def __init__(self, languages=None, device="cuda"):
        self.fetcher = YouTubeTranscriptFetcher(languages=languages)

    def run(self, video_id: str):
        # Fetch transcript
        fetch_result = self.fetcher.fetch(video_id)
        
        # Fetch video metadata (title, description, etc.)
        metadata = get_video_metadata(video_id)
        fetch_result.metadata = metadata
        
        if fetch_result.ok:
            print(fetch_result.transcript["language"])
            return fetch_result

        print(
            f"[VideoToTextNode] Fetch failed → fallback ASR "
            f"({fetch_result.status.name})"
        )

        asr_result = ytb_video_to_transcript(video_id)
        asr_result.metadata = metadata  # Also attach metadata to ASR result
        
        return asr_result


class TranscriptRouter:
    def __init__(self, threshold: int = LONG_TRANSCRIPT_THRESHOLD):
        self.threshold = threshold

    def route(self, video_id: str, transcript: str, summary_language: str = None, **kwargs):
        """
        Args:
            video_id: YouTube video ID
            transcript: FetchResult object containing transcript data
            summary_language: Language for summary output (defaults to video language if not provided)
        """
        token_count = estimate_tokens(transcript.transcript["text"])

        if token_count > self.threshold:
            return run_long_flow(
                video_id=video_id,
                transcript=transcript.transcript["text"],
                language=transcript.transcript["language"],
                video_duration=transcript.transcript["duration"]["seconds"],
                summary_language=summary_language,
            )
        else:
            return run_short_flow(
                transcript=transcript.transcript["text"],
                language=transcript.transcript["language"],
                summary_language=summary_language,
            )
