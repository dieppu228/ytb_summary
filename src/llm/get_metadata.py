import yt_dlp


def get_video_metadata(video_id: str) -> dict:
    """
    Fetch video metadata from YouTube without downloading the video.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        dict: JSON object containing video metadata
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://youtube.com/watch?v={video_id}", 
                download=False 
            )
            
            return {
                "video_id": video_id,
                "title": info.get("title"),
                "description": info.get("description"),
                "channel": info.get("channel"),
                "channel_id": info.get("channel_id"),
                "upload_date": info.get("upload_date"),
                "duration": info.get("duration"),
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "thumbnail": info.get("thumbnail"),
                "tags": info.get("tags"),
            }
    except Exception as e:
        return {
            "video_id": video_id,
            "error": str(e)
        }
