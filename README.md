youtube_summary/
│
├── src/
│   ├── config/
│   │   └── settings.py          # cấu hình model, max tokens, chunk size...
│   │
│   ├── llm/
│   │   ├── gemini_client.py     # wrapper gọi Gemini API
│   │   └── prompts.py           # prompt template cho summary
│   │
│   ├── preprocess/
│   │   ├── cleaner.py           # clean transcript (remove noise, timestamp)
│   │   └── normalizer.py        # normalize text (space, punctuation...)
│   │
│   ├── chunking/
│   │   └── text_chunker.py      # chia transcript thành chunk
│   │
│   ├── summarizer/
│   │   ├── base.py              # interface / abstract summarizer
│   │   └── gemini_summarizer.py # triển khai summary bằng Gemini
│   │
│   ├── postprocess/
│   │   └── formatter.py         # format output (bullet, paragraph...)
│   │
│   ├── pipeline/
│   │   └── summary_pipeline.py  # orchestration chính
│   │
│   └── schemas/
│       └── summary_result.py    # định nghĩa output schema
│
└── main.py                      # entrypoint test pipeline (CLI / script)
