# YouTube Video Summary - Dev By KhacDiep

An automatic YouTube video summarization tool using **Gemini 2.5 Flash** with intelligent multi-step pipeline.

## ✨ Features

- ✅ **Smart Segmentation**: Prioritizes YouTube Chapters if available, falls back to LLM
- ✅ **Whisper ASR**: Supports videos without transcripts (GPU accelerated)
- ✅ **Multi-language**: Supports multiple languages (Vietnamese, English, etc.)
- ✅ **Docker Ready**: Easy deployment with Docker Compose
- ✅ **Customizable**: Choose output language

## 🚀 Quick Start

### Run with Docker (Recommended)

```bash
# Pull image from Docker Hub
docker pull diep2004123/ytb-summary:latest

# Run with video ID
docker run -e GEMINI_API_KEY="your-key" diep2004123/ytb-summary:latest <video_id>

# Run with language option
docker run -e GEMINI_API_KEY="your-key" diep2004123/ytb-summary:latest <video_id> --summary-language Vietnamese
```

### Run Locally

```bash
# Clone repo
git clone https://github.com/dieppu228/ytb_summary.git
cd ytb_summary

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Run
python main.py <video_id> --summary-language Vietnamese
```

## 📋 Project Structure

```
YTB_summary/
├── main.py                           # Entry point
├── src/
│   ├── fetch_transcript/
│   │   ├── youtube_fetcher.py        # Fetch transcript from YouTube
│   │   └── get_chapters.py           # Fetch YouTube chapters
│   │
│   ├── audio_to_text/
│   │   ├── whisper_asr.py            # Whisper ASR (GPU)
│   │   └── ytb_dlp.py                # Download audio from YouTube
│   │
│   ├── pipeline/
│   │   ├── router.py                 # Route short/long video
│   │   ├── video_segmentation.py     # Smart segmentation (chapters/LLM)
│   │   ├── short_flow.py             # Pipeline for short videos
│   │   ├── long_flow.py              # Pipeline for long videos
│   │   └── audio_summary.py          # ASR fallback pipeline
│   │
│   ├── llm/
│   │   ├── gemini_client.py          # Gemini API wrapper
│   │   └── prompts.py                # Prompt templates
│   │
│   ├── preprocess/
│   │   └── segmenter.py              # Segment transcript by outline
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

### Build from Source

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

| Variable         | Required | Description           |
| ---------------- | -------- | --------------------- |
| `GEMINI_API_KEY` | ✅       | Google Gemini API key |

Create `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

## 📝 CLI Options

```bash
python main.py <video_id> [OPTIONS]

Options:
  --summary-language, -l    Output language (Vietnamese, English, etc.)
  --output, -o              Save results to JSON file
  --help                    Show help
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

# Test with video that has chapters
python main.py S4hYyLebsAw --summary-language Vietnamese

# Test with video without transcript (requires Whisper)
python main.py 725WlG1idPc --summary-language Vietnamese
```


