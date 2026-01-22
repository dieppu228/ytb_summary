import json
import os
from dotenv import load_dotenv
from fetch_transcript.youtube_fetcher import YouTubeTranscriptFetcher
from pipeline.router import TranscriptRouter

# Load environment variables
load_dotenv()


def main():
    # ===== STEP 1: Fetch transcript =====
    video_id = "Rwqx4UbKjR8"

    fetcher = YouTubeTranscriptFetcher(languages=["en", "vi"])
    result = fetcher.fetch(video_id)

    print("=" * 60)
    print("VIDEO INFORMATION")
    print("=" * 60)
    print(json.dumps(
        {
            "video_id": result["video_id"],
            "language": result["language"],
            "duration": result["duration"],
            "text_length": len(result["text"])
        },
        indent=2,
        ensure_ascii=False
    ))

    # ===== STEP 2: Route and run appropriate flow =====
    router = TranscriptRouter()
    
    print("\n" + "=" * 60)
    print("ROUTING & SUMMARIZATION")
    print("=" * 60)
    
    summary_result = router.route(
        transcript=result["text"],
        language=result["language"]
    )

    print(json.dumps(summary_result.model_dump(), indent=2, ensure_ascii=False))    
    return summary_result


if __name__ == "__main__":
    main()
