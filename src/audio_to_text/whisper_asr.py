from faster_whisper import WhisperModel
from typing import Dict, Optional


class SimpleFasterWhisperASR:
    def __init__(
        self,
        model_size="small",
        device="cuda",
        compute_type=None,  # Auto-detect based on device
        confidence_threshold=0.6
    ):
        self.confidence_threshold = confidence_threshold
        # Auto-select compute_type: float16 for CUDA, int8 for CPU
        if compute_type is None:
            compute_type = "float16" if device == "cuda" else "int8"
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

    def _format_inline(self, segments):
        return " ".join(
            f"[{s.start:.2f}s] {s.text.strip()}" for s in segments
        )

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        mode: str = "full"   # "clean" | "full"
    ) -> Dict:

        kwargs = {
            "beam_size": 5,
            "condition_on_previous_text": True  # giúp giữ mạch xuyên qua silence
        }

        # Clean = vẫn lọc silence
        if mode == "clean":
            kwargs["vad_filter"] = True
            kwargs["vad_parameters"] = {
                "min_silence_duration_ms": 1500,
                "speech_pad_ms": 300
            }

        # Full = KHÔNG DÙNG VAD → không bao giờ dừng vì im lặng
        else:
            kwargs["vad_filter"] = False

        if language:
            kwargs["language"] = language

        segments, info = self.model.transcribe(audio_path, **kwargs)
        segments = list(segments)

        formatted_lines = []
        full_text = ""

        for s in segments:
            text = s.text.strip()
            formatted_lines.append(
                f"[{s.start:.2f}s -> {s.end:.2f}s] {text}"
            )
            full_text += text + " "

        return {
            "duration": info.duration,
            "language": info.language,
            "language_confidence": getattr(info, "language_probability", None),
            "is_confident": (
                getattr(info, "language_probability", 1.0)
                >= self.confidence_threshold
            ),
            "mode": mode,
            "segments": formatted_lines,
            "inline_text": self._format_inline(segments),
            "text": full_text.strip()
        }
