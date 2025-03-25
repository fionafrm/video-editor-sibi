from django.urls import path
from .views import (
    upload_video,
    trim_video,
    save_transcript,
    get_video_details,
    upload_transcript_csv,
    merge_videos
)

urlpatterns = [
    # Upload video
    path('upload_video/', upload_video, name='upload_video'),

    # Trim video berdasarkan video ID
    path('trim_video/<int:video_id>/', trim_video, name='trim_video'),

    # Simpan transkrip untuk video tertentu
    path('save_transcript/<int:video_id>/', save_transcript, name='save_transcript'),

    # Ambil detail video termasuk transkripnya
    path('get_video_details/<int:video_id>/', get_video_details, name='get_video_details'),

    # Upload transkrip dalam format CSV
    path('upload_transcript_csv/', upload_transcript_csv, name='upload_transcript_csv'),

    path('merge_videos/<int:video_id>/', merge_videos, name='merge_videos'),
]
