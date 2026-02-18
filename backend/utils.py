import yt_dlp
import os

def download_audio(url: str, output_path: str = "data/audio") -> tuple:
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info['id']
        title = info.get('title', 'Unknown Title')
        duration = info.get('duration', 0)

    # Find the actual downloaded file
    audio_file = f"{output_path}/{video_id}.mp3"
    
    # Sometimes yt-dlp saves with different extension before conversion
    if not os.path.exists(audio_file):
        for f in os.listdir(output_path):
            if f.startswith(video_id):
                audio_file = f"{output_path}/{f}"
                break

    return audio_file, title, duration