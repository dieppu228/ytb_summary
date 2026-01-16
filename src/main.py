import json
from fetch_transcript.youtube_fetcher import YouTubeTranscriptFetcher


def main():
    video_id = "NdYWuo9OFAw"

    fetcher = YouTubeTranscriptFetcher(languages=["en", "vi"])
    result = fetcher.fetch(video_id)

    print(json.dumps(
        {
            "video_id": result["video_id"],
            "language": result["language"],
            "duration": result["duration"],
            "cleaned_text": result["text"]
        },
        indent=2,
        ensure_ascii=False
    ))


if __name__ == "__main__":
    main()
