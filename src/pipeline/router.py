from pipeline.short_flow import run_short_flow
from pipeline.long_flow import run_long_flow
from pipeline.audio_summary import ytb_video_to_transcript
from utils.token_counter import estimate_tokens
from fetch_transcript.youtube_fetcher import YouTubeTranscriptFetcher



LONG_TRANSCRIPT_THRESHOLD = 1500



class VideoToTextNode:
    def __init__(self, languages=None, device="cuda"):
        self.fetcher = YouTubeTranscriptFetcher(languages=languages)

    def run(self, video_id: str):
        fetch_result = self.fetcher.fetch(video_id)
        if fetch_result.ok:
            print(fetch_result.transcript["language"])
            return fetch_result

        print(
            f"[VideoToTextNode] Fetch failed → fallback ASR "
            f"({fetch_result.status.name})"
        )

        asr_result = ytb_video_to_transcript(video_id)

        return asr_result


class TranscriptRouter:
    def __init__(self, threshold: int = LONG_TRANSCRIPT_THRESHOLD):
        self.threshold = threshold

    def route(self, transcript: str, **kwargs):
        token_count = estimate_tokens(transcript.transcript["text"])

        if token_count > self.threshold:
            return run_long_flow(
                transcript=transcript.transcript["text"],
                language=transcript.transcript["language"],
                video_duration=transcript.transcript["duration"]["seconds"],
            )
        else:
            return run_short_flow(
                transcript=transcript.transcript["text"],
                language=transcript.transcript["language"],
            )
