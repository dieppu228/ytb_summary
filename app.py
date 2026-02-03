"""
Gradio Web Interface for YouTube Transcript Summarization
Run: python app.py
Access: http://localhost:7860 (local) or public URL via share=True
"""
import sys
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import gradio as gr
from pipeline.router import TranscriptRouter, VideoToTextNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    url_or_id = url_or_id.strip()
    
    # Common YouTube URL patterns
    patterns = [
        "youtube.com/watch?v=",
        "youtu.be/",
        "youtube.com/embed/",
        "youtube.com/v/",
    ]
    
    for pattern in patterns:
        if pattern in url_or_id:
            # Extract the video ID after the pattern
            start = url_or_id.find(pattern) + len(pattern)
            video_id = url_or_id[start:start+11]  # YouTube IDs are 11 chars
            # Remove any extra parameters
            if "&" in video_id:
                video_id = video_id.split("&")[0]
            if "?" in video_id:
                video_id = video_id.split("?")[0]
            return video_id
    
    # Assume it's already a video ID
    return url_or_id[:11] if len(url_or_id) >= 11 else url_or_id


def process_video(youtube_url: str, summary_language: str, progress=gr.Progress()):
    """
    Main processing function for Gradio.
    Returns: (overall_summary, transcript_text, metadata_info, json_output)
    """
    if not youtube_url:
        return "❌ Vui lòng nhập YouTube URL hoặc Video ID", "", "", ""
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        return "❌ GEMINI_API_KEY chưa được cấu hình trong file .env", "", "", ""
    
    try:
        video_id = extract_video_id(youtube_url)
        logger.info(f"Processing video: {video_id}")
        
        # Step 1: Fetch transcript
        progress(0.1, desc="🔄 Đang tải transcript...")
        video_to_text_node = VideoToTextNode()
        transcript_result = video_to_text_node.run(video_id)
        
        if not transcript_result.ok:
            return f"❌ Không thể lấy transcript: {transcript_result.error}", "", ""
        
        transcript_data = transcript_result.transcript
        transcript_text = transcript_data.get("text", "")
        
        # Metadata info
        source = transcript_data.get("source", "YouTube")
        language = transcript_data.get("language", "Unknown")
        duration_min = transcript_data.get("duration", {}).get("minutes", 0)
        
        # Get video metadata (title, etc.)
        video_metadata = transcript_result.metadata or {}
        video_title = video_metadata.get("title", "Unknown")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        metadata = f"""🎬 **Tiêu đề:** {video_title}
🔗 **URL:** [{video_url}]({video_url})
📹 **Video ID:** {video_id}
🌐 **Ngôn ngữ:** {language}
⏱️ **Thời lượng:** {duration_min:.2f} phút
📝 **Nguồn transcript:** {source}"""
        
        # Step 2: Summarize
        progress(0.5, desc="🤖 Đang tóm tắt với AI...")
        
        # Use provided language or default to video language
        output_language = summary_language.strip() if summary_language else None
        
        transcription_router = TranscriptRouter()
        result = transcription_router.route(
            video_id=video_id,
            transcript=transcript_result,
            summary_language=output_language
        )
        
        progress(0.9, desc="✅ Hoàn thành!")
        
        # Format overall summary
        result_dict = result.model_dump()
        
        # Handle both short flow (summary) and long flow (global_summary)
        overall_summary = result_dict.get("global_summary") or result_dict.get("summary", "Không có tóm tắt")
        
        # Add section takeaways if available (long video)
        if "section_takeaways" in result_dict and result_dict["section_takeaways"]:
            sections_text = "\n\n---\n\n## 📑 Takeaways theo phần:\n\n"
            for section in result_dict["section_takeaways"]:
                title = section.get("title", "Untitled")
                section_id = section.get("section_id", 0)
                takeaways = section.get("takeaways", [])
                sections_text += f"### {section_id}. {title}\n"
                for takeaway in takeaways:
                    sections_text += f"- {takeaway}\n"
                sections_text += "\n"
            overall_summary += sections_text
        
        # Format JSON output
        json_output = json.dumps(result_dict, indent=2, ensure_ascii=False)
        
        return overall_summary, transcript_result.transcript.get("raw_text", transcript_result.transcript.get("text", "")), metadata, json_output
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        return f"❌ Lỗi xử lý: {str(e)}", "", "", ""


# Create Gradio Interface
with gr.Blocks(
    title="YouTube Summary AI",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
    ),
    css="""
    .gradio-container { max-width: 1200px !important; }
    .summary-box { min-height: 400px; }
    """
) as app:
    
    gr.Markdown("""
    # 🎬 YouTube Video Summarizer
    
    Tóm tắt video YouTube bằng AI (Gemini). Hỗ trợ cả video có/không có phụ đề.
    
    ---
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            url_input = gr.Textbox(
                label="🔗 YouTube URL hoặc Video ID",
                placeholder="Ví dụ: https://www.youtube.com/watch?v=dQw4w9WgXcQ hoặc dQw4w9WgXcQ",
                lines=1
            )
        with gr.Column(scale=1):
            language_input = gr.Textbox(
                label="🌐 Ngôn ngữ tóm tắt (tùy chọn)",
                placeholder="Vietnamese, English...",
                lines=1,
                value=""
            )
    
    submit_btn = gr.Button("🚀 Tóm tắt video", variant="primary", size="lg")
    
    # Metadata display
    metadata_output = gr.Markdown(label="📊 Thông tin video")
    
    with gr.Tabs():
        with gr.TabItem("📝 Tóm tắt tổng quan"):
            summary_output = gr.Markdown(
                label="Overall Summary",
                elem_classes=["summary-box"]
            )
        
        with gr.TabItem("📜 Transcript gốc"):
            transcript_output = gr.Textbox(
                label="Transcript",
                lines=15,
                max_lines=15,  # Fixed height with scroll
                show_copy_button=True,
                autoscroll=False
            )
        
        with gr.TabItem("🔧 Raw JSON"):
            json_output = gr.Code(
                label="Raw Summary JSON",
                language="json",
                lines=20,
            )
    
    # Event handling
    submit_btn.click(
        fn=process_video,
        inputs=[url_input, language_input],
        outputs=[summary_output, transcript_output, metadata_output, json_output]
    )
    
    # Examples
    gr.Examples(
        examples=[
            ["https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Vietnamese"],
            ["dQw4w9WgXcQ", "English"],
        ],
        inputs=[url_input, language_input],
        label="💡 Ví dụ"
    )
    
    gr.Markdown("""
    ---
    
    ### 📌 Hướng dẫn:
    1. Dán link YouTube hoặc Video ID vào ô input
    2. (Tùy chọn) Chọn ngôn ngữ cho bản tóm tắt
    3. Nhấn "Tóm tắt video" và đợi kết quả
    
    **Lưu ý:** Video không có phụ đề sẽ được chuyển đổi bằng Whisper ASR (cần GPU để nhanh hơn).
    """)


if __name__ == "__main__":
    import subprocess
    import threading
    import time
    
    PORT = 7870
    
    # Try to use ngrok for public URL
    use_ngrok = True
    ngrok_url = None
    
    if use_ngrok:
        try:
            from pyngrok import ngrok
            # Start ngrok tunnel
            public_url = ngrok.connect(PORT)
            ngrok_url = public_url.public_url
            print(f"\n🌐 Public URL (ngrok): {ngrok_url}\n")
        except ImportError:
            print("\n⚠️ pyngrok not installed. Run: pip install pyngrok")
            print("Falling back to local only...\n")
            use_ngrok = False
        except Exception as e:
            print(f"\n⚠️ ngrok error: {e}")
            print("Falling back to local only...\n")
            use_ngrok = False
    
    # Launch Gradio
    app.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        share=False,  # Disable Gradio share, use ngrok instead
        show_error=True,
    )
