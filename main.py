"""
YouTube Transcript Summarization Pipeline - Entry Point
"""
import sys
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.router import TranscriptRouter, VideoToTextNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(video_id: str, output_file: str = None, summary_language: str = None):
    """
    Main pipeline: Fetch transcript → Route → Summarize
    
    Args:
        video_id: YouTube video ID
        output_file: Optional output file path for results (JSON)
        summary_language: Language for summary output (defaults to video language)
    """
    try:
        logger.info(f"Starting pipeline for video: {video_id}")
        if summary_language:
            logger.info(f"Summary language: {summary_language}")
        
        # Step 1: Fetch transcript (YouTube or ASR)
        logger.info("Step 1: Fetching transcript...")
        video_to_text_node = VideoToTextNode()
        transcript = video_to_text_node.run(video_id)
        
        if not transcript.ok:
            logger.error(f"Failed to fetch transcript: {transcript.error}")
            return None
        
        logger.info(f"✓ Transcript fetched successfully")
        logger.info(f"  Language: {transcript.transcript['language']}")
        logger.info(f"  Duration: {transcript.transcript['duration']['minutes']:.2f} minutes")
        logger.info(f"  Source: {transcript.transcript.get('source', 'YouTube')}")
        
        # Step 2: Route & Summarize (short or long flow)
        logger.info("Step 2: Routing and summarizing...")
        transcription_router = TranscriptRouter()
        result = transcription_router.route(video_id, transcript, summary_language=summary_language)
        
        logger.info(f"✓ Summarization completed")
        
        # Step 3: Output results
        output_dict = result.model_dump()
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Results saved to: {output_file}")
        else:
            print("\n" + "="*80)
            print("SUMMARIZATION RESULTS")
            print("="*80)
            print(json.dumps(output_dict, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    import argparse
    
    # Check API key before running
    if not os.getenv("GEMINI_API_KEY"):
        logger.error(
            "ERROR: GEMINI_API_KEY not set!\n"
            "Please set it in .env file or export it as environment variable:\n"
            "  export GEMINI_API_KEY='your_api_key_here'\n"
            "Get API key from: https://ai.google.dev/"
        )
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="YouTube Transcript Summarization Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py dQw4w9WgXcQ
  python main.py dQw4w9WgXcQ --output result.json
  python main.py dQw4w9WgXcQ --summary-language Vietnamese
  python main.py dQw4w9WgXcQ -o result.json -l en
        """
    )
    parser.add_argument(
        "video_id",
        help="YouTube video ID to process (e.g., dQw4w9WgXcQ)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (JSON format)",
        default=None
    )
    parser.add_argument(
        "--summary-language", "-l",
        help="Language for summary output (e.g., Vietnamese, English). Defaults to video language.",
        default=None
    )
    
    args = parser.parse_args()
    
    result = main(
        video_id=args.video_id,
        output_file=args.output,
        summary_language=args.summary_language
    )
    
    sys.exit(0 if result else 1)
