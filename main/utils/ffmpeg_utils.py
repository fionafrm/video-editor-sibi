import subprocess
import os
from django.conf import settings

def trim_video(input_path, output_path, start_time, end_time):
    """Trim a video using FFmpeg."""
    command = [
        "ffmpeg", "-i", input_path,
        "-ss", str(start_time), "-to", str(end_time),
        "-c", "copy", output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

def merge_videos(video_list, output_path):
    """Merge multiple videos using FFmpeg."""
    list_file = os.path.join(settings.MEDIA_ROOT, "merge_list.txt")
    with open(list_file, "w") as f:
        for video in video_list:
            f.write(f"file '{video}'\n")

    command = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path