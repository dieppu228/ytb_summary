import yt_dlp
import os
import re
import unicodedata
from typing import Dict


class YTBDlpDownloader:
    def __init__(
        self,
        output_dir="audio_downloads",
        audio_format="mp3",
        audio_quality="96"
    ):
        self.output_dir = output_dir
        self.audio_format = audio_format
        self.audio_quality = audio_quality

        os.makedirs(self.output_dir, exist_ok=True)

    # -----------------------
    # Filename utils
    # -----------------------
    def _sanitize_filename_ascii(self, name: str) -> str:
        """
        Unicode → ASCII, an toàn cho mọi OS
        """
        name = unicodedata.normalize("NFKD", name)
        name = name.encode("ascii", "ignore").decode("ascii")
        name = re.sub(r'[^a-zA-Z0-9\s_-]', "", name)
        name = re.sub(r'\s+', "_", name).strip("_")
        return name or "audio"

    def _build_file_and_title(self, title: str) -> Dict:
        return {
            "title": title,  # Hiển thị đẹp
            "file_safe": self._sanitize_filename_ascii(title)
        }

    # -----------------------
    # Main API
    # -----------------------
    def download(self, video_id: str) -> Dict:
        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            # Lấy metadata trước
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)

            title_data = self._build_file_and_title(
                info.get("title", "unknown")
            )

            # ÉP yt-dlp dùng filename mình build
            outtmpl = os.path.join(
                self.output_dir,
                f"{title_data['file_safe']}.%(ext)s"
            )

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": self.audio_quality,
                }],
                "quiet": True,
                "no_warnings": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            file_path = os.path.join(
                self.output_dir,
                f"{title_data['file_safe']}.{self.audio_format}"
            )

            return {
                "status": "success",
                "title": title_data["title"],
                "file_safe": title_data["file_safe"],
                "file_path": file_path,
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "url": url
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "url": url
            }
