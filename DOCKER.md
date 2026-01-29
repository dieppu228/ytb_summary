# Docker Usage Guide

## Quick Start

### 1. Setup Environment

Create `.env` file with your API key:

```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 2. Build Docker Image

**CPU Version (default):**

```bash
docker-compose build ytb-summary
```

**GPU Version (requires NVIDIA Docker):**

```bash
docker-compose build ytb-summary-gpu
```

### 3. Run Summarization

**Basic usage:**

```bash
docker-compose run --rm ytb-summary <video_id>
```

**With options:**

```bash
# Save output to file
docker-compose run --rm ytb-summary dQw4w9WgXcQ -o /app/output/result.json

# Specify summary language
docker-compose run --rm ytb-summary dQw4w9WgXcQ -l Vietnamese

# Combined
docker-compose run --rm ytb-summary dQw4w9WgXcQ -o /app/output/result.json -l English
```

**GPU Version:**

```bash
docker-compose --profile gpu run --rm ytb-summary-gpu dQw4w9WgXcQ
```

## Command Line Options

| Option               | Short | Description             |
| -------------------- | ----- | ----------------------- |
| `--output`           | `-o`  | Output file path (JSON) |
| `--summary-language` | `-l`  | Summary output language |
| `--help`             | `-h`  | Show help message       |

## Examples

```bash
# Summarize a Vietnamese video
docker-compose run --rm ytb-summary n8jLOMSKYI8

# Summarize and save to file
docker-compose run --rm ytb-summary n8jLOMSKYI8 -o /app/output/summary.json

# Summarize Vietnamese video but output in English
docker-compose run --rm ytb-summary n8jLOMSKYI8 -l English

# Use GPU for ASR (when YouTube captions not available)
docker-compose --profile gpu run --rm ytb-summary-gpu plnfIj7dkJE
```

## Output Files

- Results saved in `./output/` directory
- Audio cache stored in `./audio_downloads/`

## Troubleshooting

**API Key not set:**

```
ERROR: GEMINI_API_KEY not set!
```

→ Make sure `.env` file exists with valid API key

**GPU not detected:**

```bash
# Check NVIDIA Docker installation
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi
```

**Permission denied:**

```bash
# Fix volume permissions
chmod -R 777 ./output ./audio_downloads
```
