from moviepy import VideoFileClip

video_path = "media/videos/merged_1_2.mp4"
clip = VideoFileClip(video_path)

# Coba potong dari detik ke-2 sampai detik ke-5
trimmed_clip = clip.subclipped(2, 5)
trimmed_clip.write_videofile("output.mp4", codec="libx264")
