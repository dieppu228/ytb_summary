from audio_to_text.ytb_dlp import YTBDlpDownloader
from audio_to_text.whisper_asr import SimpleFasterWhisperASR
import json


def ytb_video_to_transcript(video_id: str) -> dict:
    # Step 1: Download video and extract audio
    downloader = YTBDlpDownloader(
        output_dir="audio_downloads",
        audio_format="mp3",
        audio_quality="96"
    )
    result = downloader.download(video_id)
    file_path = result["file_path"]


    # Step 2: Transcribe audio to text
    model = SimpleFasterWhisperASR(model_size="small", device="cpu")
    transcript_result = model.transcribe(file_path)

    return transcript_result