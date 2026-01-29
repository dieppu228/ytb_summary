from audio_to_text.ytb_dlp import YTBDlpDownloader
from audio_to_text.whisper_asr import SimpleFasterWhisperASR
from fetch_transcript.youtube_fetcher import FetchResult, FetchStatus
import json
import torch

def ytb_video_to_transcript(video_id: str) -> FetchResult:
    """
    Convert YouTube video to transcript using ASR (Whisper).
    Returns FetchResult with same structure as YouTubeTranscriptFetcher.
    """
    try:
        # Step 1: Download video and extract audio
        downloader = YTBDlpDownloader(
            output_dir="audio_downloads",
            audio_format="mp3",
            audio_quality="96"
        )
        download_result = downloader.download(video_id)
        
        if download_result["status"] != "success":
            return FetchResult(
                ok=False,
                status=FetchStatus.ERROR,
                error=f"Failed to download audio: {download_result.get('message', 'Unknown error')}"
            )
        
        file_path = download_result["file_path"]

        # Step 2: Transcribe audio to text
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        model = SimpleFasterWhisperASR(model_size="small", device=device)
        whisper_result = model.transcribe(file_path)
        
        del model
        if device == "cuda":
            torch.cuda.empty_cache()
        
        print("Transcription done, building result...")
        # Step 3: Normalize output to match YouTube fetch format
        payload = {
            "video_id": video_id,
            "language": whisper_result.get("language", "unknown"),
            "language_code": whisper_result.get("language", "unknown"),
            "is_generated": False,  # ASR-generated, not official captions
            "is_translatable": False,
            "translation_languages": [],
            "duration": {
                "seconds": round(whisper_result.get("duration", 0), 2),
                "minutes": round(whisper_result.get("duration", 0) / 60, 2)
            },
            "text": whisper_result.get("text", ""),
            "raw_text": whisper_result.get("inline_text", ""),  # Include formatted segments
            "source": "ASR",  # Mark as ASR-generated
            "language_confidence": whisper_result.get("language_confidence"),
        }

        return FetchResult(
            ok=True,
            status=FetchStatus.SUCCESS,
            transcript=payload
        )
        
    except Exception as e:
        return FetchResult(
            ok=False,
            status=FetchStatus.ERROR,
            error=f"ASR failed: {str(e)}"
        )