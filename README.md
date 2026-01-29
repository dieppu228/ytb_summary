# YouTube Video Summary

Công cụ tự động tóm tắt video YouTube sử dụng **Gemini 2.5 Flash** với pipeline đa bước thông minh.

## ✨ Features

- ✅ **Smart Segmentation**: Ưu tiên YouTube Chapters nếu có, fallback LLM
- ✅ **Whisper ASR**: Hỗ trợ video không có transcript (GPU accelerated)
- ✅ **Multi-language**: Hỗ trợ đa ngôn ngữ (Vietnamese, English, etc.)
- ✅ **Docker Ready**: Dễ dàng deploy với Docker Compose
- ✅ **Customizable**: Tùy chọn ngôn ngữ output

## 🚀 Quick Start

### Chạy với Docker (Khuyên dùng)

```bash
# Pull image từ Docker Hub
docker pull diep2004123/ytb-summary:latest

# Chạy với video ID
docker run -e GEMINI_API_KEY="your-key" diep2004123/ytb-summary:latest <video_id>

# Chạy với tùy chọn ngôn ngữ
docker run -e GEMINI_API_KEY="your-key" diep2004123/ytb-summary:latest <video_id> --summary-language Vietnamese
```

### Chạy Local

```bash
# Clone repo
git clone https://github.com/dieppu228/ytb_summary.git
cd ytb_summary

# Cài dependencies
pip install -r requirements.txt

# Tạo file .env
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Chạy
python main.py <video_id> --summary-language Vietnamese
```

## 📋 Cấu trúc Dự án

```
YTB_summary/
├── main.py                           # Entry point
├── src/
│   ├── fetch_transcript/
│   │   ├── youtube_fetcher.py        # Fetch transcript từ YouTube
│   │   └── get_chapters.py           # Fetch YouTube chapters
│   │
│   ├── audio_to_text/
│   │   ├── whisper_asr.py            # Whisper ASR (GPU)
│   │   └── ytb_dlp.py                # Download audio từ YouTube
│   │
│   ├── pipeline/
│   │   ├── router.py                 # Route short/long video
│   │   ├── video_segmentation.py     # Smart segmentation (chapters/LLM)
│   │   ├── short_flow.py             # Pipeline cho video ngắn
│   │   ├── long_flow.py              # Pipeline cho video dài
│   │   └── audio_summary.py          # ASR fallback pipeline
│   │
│   ├── llm/
│   │   ├── gemini_client.py          # Wrapper Gemini API
│   │   └── prompts.py                # Prompt templates
│   │
│   ├── preprocess/
│   │   └── segmenter.py              # Chia transcript theo outline
│   │
│   └── schemas/
│       └── output_format.py          # Pydantic schemas
│
├── Dockerfile                        # Docker CPU build
├── Dockerfile.gpu                    # Docker GPU build (CUDA + Whisper)
├── docker-compose.yml                # Docker Compose config
└── requirements.txt
```

## 🔄 Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    VIDEO URL INPUT                          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 1: FETCH TRANSCRIPT                       │
│  ┌─────────────────┐      ┌─────────────────────────────┐   │
│  │ YouTube API     │ OR   │ Whisper ASR (fallback)      │   │
│  │ (if available)  │      │ (download audio → transcribe)│   │
│  └─────────────────┘      └─────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 2: ROUTE (Short/Long)                     │
│  Token count < 1500 → Short Flow (direct summary)           │
│  Token count > 1500 → Long Flow (multi-step)                │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 3: VIDEO SEGMENTATION                     │
│  ┌─────────────────┐      ┌─────────────────────────────┐   │
│  │ YouTube Chapters│ OR   │ LLM Outline (fallback)      │   │
│  │ (if available)  │      │ (Gemini generates outline)  │   │
│  └─────────────────┘      └─────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 4: SUMMARIZE SECTIONS                     │
│  For each section: summarize with memory context            │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 5: GLOBAL SUMMARY                         │
│  Combine all section summaries → final output               │
└─────────────────────────────────────────────────────────────┘
```

## 🐳 Docker

### Build từ source

```bash
# Build CPU version
docker-compose build ytb-summary

# Build GPU version (CUDA + Whisper)
docker-compose build ytb-summary-gpu
```

### Run

```bash
# CPU version
docker-compose run ytb-summary <video_id> --summary-language Vietnamese

# GPU version
docker-compose --profile gpu run ytb-summary-gpu <video_id> --summary-language Vietnamese
```

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |

Tạo file `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

## 📝 CLI Options

```bash
python main.py <video_id> [OPTIONS]

Options:
  --summary-language, -l    Ngôn ngữ output (Vietnamese, English, etc.)
  --output, -o              Lưu kết quả ra file JSON
  --help                    Hiển thị help
```

## 📦 Dependencies

- `google-genai`: Gemini API client
- `youtube-transcript-api`: Fetch YouTube transcripts
- `yt-dlp`: Download YouTube audio
- `openai-whisper`: Speech-to-text (ASR)
- `pydantic`: Data validation
- `torch`: PyTorch (for Whisper GPU)

## 🛠️ Development

```bash
# Test fetch transcript
python -c "from src.fetch_transcript.youtube_fetcher import YouTubeTranscriptFetcher; print(YouTubeTranscriptFetcher().fetch('dQw4w9WgXcQ'))"

# Test với video có chapters
python main.py S4hYyLebsAw --summary-language Vietnamese

# Test với video không có transcript (cần Whisper)
python main.py 725WlG1idPc --summary-language Vietnamese
```

## 📄 License

MIT License
