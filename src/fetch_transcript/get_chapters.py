import yt_dlp
from schemas.output_format import OutlineOutput, SectionOutline


def get_youtube_chapters(video_url: str) -> OutlineOutput | None:
    """Fetch YouTube chapters if available.
    
    Returns OutlineOutput format to match LLM segmentation output.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        chapters = info.get('chapters')
        
        if chapters:
            sections = [
                SectionOutline(
                    section_id=idx + 1,
                    title=ch.get('title', f'Section {idx + 1}'),
                    start=ch.get('start_time', 0),
                    end=ch.get('end_time', 0),
                    keywords=[]  # YouTube chapters don't have keywords
                )
                for idx, ch in enumerate(chapters)
            ]
            return OutlineOutput(sections=sections)
        return None