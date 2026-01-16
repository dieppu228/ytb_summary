# YouTube Video Summary

Công cụ tự động tóm tắt video YouTube bằng Gemini 2.5 Flash với pipeline đa bước: **outline → segmentation → section summary → global summary**.

## 📋 Cấu trúc Dự án

```
YTB_summary/
│
├── src/
│   ├── config/
│   │   └── settings.py                    # Cấu hình (model, API keys, timeout...)
│   │
│   ├── fetch_transcript/
│   │   └── youtube_fetcher.py            # Fetch transcript từ YouTube API
│   │
│   ├── preprocess/
│   │   ├── cleaner.py                    # Làm sạch transcript
│   │   ├── normalizer.py                 # Chuẩn hóa text (space, punctuation)
│   │   └── segmenter.py                  # Chia transcript theo outline
│   │
│   ├── llm/
│   │   ├── gemini_client.py              # Wrapper Gemini API
│   │   └── prompts.py                    # Prompt templates
│   │
│   ├── schemas/
│   │   ├── output_format.py              # Pydantic schema cho outputs
│   │   └── summary_result.py             # Schema cho kết quả cuối
│   │
│   ├── summarizer/
│   │   ├── base.py                       # Base class
│   │   ├── gemini_summarizer.py          # Gemini implementation
│   │   └── segment_trans.py              # Segment transformation
│   │
│   ├── postprocess/
│   │   └── formatter.py                  # Format output
│   │
│   ├── pipeline/
│   │   └── summary_pipeline.py           # Main orchestration
│   │
│   ├── main.py                           # Entry point
│   └── main.ipynb                        # Jupyter notebook demo
│
├── requirements.txt
├── Prompt_AI.md
└── README.md
```

## 🔄 Pipeline Flow

```
1. FETCH TRANSCRIPT
   ↓
   YouTubeTranscriptFetcher.fetch(video_id)
   → Output: video_id, language, duration, text
   
2. GENERATE OUTLINE
   ↓
   build_outline_prompt(video_transcript)
   → Output: sections (id, title, start, end, keywords)
   
3. SEGMENT TRANSCRIPT
   ↓
   TranscriptSegmenter.segment_by_outline(outline.sections)
   → Output: segmented sections with text content
   
4. SUMMARIZE SECTIONS (with Memory)
   ↓
   build_section_summary_prompt(section_text, memory, language)
   → Lặp qua từng section, giữ memory từ section trước
   → Output: section_summaries (id, title, summary)
   
5. GLOBAL SUMMARY
   ↓
   build_global_summary_prompt(section_summaries, language)
   → Output: overall_summary (JSON)
```

## 🚀 Cách Dùng

### Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### Chạy Demo (Jupyter Notebook)

```bash
jupyter notebook src/main.ipynb
```

Notebook gồm 5 cell tương ứng với 5 bước pipeline:
1. **Fetch Transcript**: Lấy transcript từ YouTube
2. **Generate Outline**: Chia video thành các section
3. **Segment Transcript**: Phân đoạn transcript theo outline
4. **Summarize Sections**: Tóm tắt từng section (có memory)
5. **Global Summary**: Tóm tắt toàn bộ video

### Chạy Script (main.py)

```bash
python src/main.py
```

## 📝 Prompts

### 1. Outline Prompt
- **Mục đích**: Chia video thành các section có chủ đề
- **Input**: Full transcript
- **Output**: JSON với sections (id, title, start, end, keywords)

### 2. Section Summary Prompt
- **Mục đích**: Tóm tắt từng section
- **Input**: Section text, previous summary (memory), language
- **Output**: JSON với summary của section

### 3. Global Summary Prompt
- **Mục đích**: Tóm tắt toàn bộ video
- **Input**: Tất cả section summaries, language
- **Output**: JSON với overall_summary

## 🔑 Mẫu Environment

Tạo file `.env`:

```
GEMINI_API_KEY=your_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## 📦 Dependencies

- `google-generativeai`: Gemini API
- `youtube-transcript-api`: Fetch YouTube transcripts
- `pydantic`: Data validation
- `python-dotenv`: Load environment variables

## ✨ Features

- ✅ Tự động fetch transcript từ YouTube
- ✅ Phân tích outline (outline) video tự động
- ✅ Segment transcript theo outline
- ✅ Tóm tắt từng section với context memory
- ✅ Sinh global summary từ section summaries
- ✅ Support đa ngôn ngữ (tiếng Anh, Tiếng Việt, etc.)
- ✅ JSON schema validation với Pydantic

## 🛠️ Development

Để test từng module riêng lẻ:

```python
# Test fetch
from fetch_transcript.youtube_fetcher import YouTubeTranscriptFetcher
fetcher = YouTubeTranscriptFetcher()
result = fetcher.fetch("video_id")

# Test outline
from llm.prompts import build_outline_prompt
from llm.gemini_client import GeminiClient
prompt = build_outline_prompt(transcript)
# ... gọi Gemini

# Test section summary
from llm.prompts import build_section_summary_prompt
prompt = build_section_summary_prompt(section_text, memory, language)
# ... gọi Gemini

# Test global summary
from llm.prompts import build_global_summary_prompt
prompt = build_global_summary_prompt(section_summaries, language)
# ... gọi Gemini
```
