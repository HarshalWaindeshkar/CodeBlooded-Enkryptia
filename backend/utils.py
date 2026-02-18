import yt_dlp
import os
import tempfile

def download_audio(url: str) -> tuple:
    temp_dir = tempfile.mkdtemp()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{temp_dir}/%(id)s.%(ext)s',
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

    audio_file = f"{temp_dir}/{video_id}.mp3"
    if not os.path.exists(audio_file):
        for f in os.listdir(temp_dir):
            if f.startswith(video_id):
                audio_file = f"{temp_dir}/{f}"
                break

    return audio_file, title, duration