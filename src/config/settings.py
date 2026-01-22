import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate required keys
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set. "
        "Please set it in your .env file or environment variables."
    )

# Model settings
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_MODEL_LITE = "gemini-2.5-flash-lite"
DEFAULT_MAX_TOKENS = 100000
DEFAULT_TEMPERATURE = 0.3

# Pipeline settings
LONG_TRANSCRIPT_THRESHOLD = 1500  # tokens

# YouTube settings
YOUTUBE_LANGUAGES = ["en", "vi"]
