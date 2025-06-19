from django.urls import path
from .views import (
    upload_file,
    trim_video,
    save_transcript,
    get_video_details,
    get_merged_video,
    upload_transcript_csv,
    merge_videos,
    video_editor_page,
    delete_video,
    search_videos,
    get_previous_video,
    get_next_video_status,
    upload_video_page,
    upload_transcript_page,
    landing_page,
    folder_page,
    upload_file_page,
    landing_page_data,
    register,
    login_view,
    logout_view
)

urlpatterns = [
    # Upload file
    path('upload_file/', upload_file, name='upload_file'),

    # Trim video berdasarkan video ID
    path('trim_video/<video_title>/', trim_video, name='trim_video'),

    # Simpan transkrip untuk video tertentu
    path('save_transcript/<video_title>/', save_transcript, name='save_transcript'),

    # Ambil detail video termasuk transkripnya
    path('get_video_details/<video_title>/', get_video_details, name='get_video_details'),

    ## Ambil video yang sudah di-merge
    path('get_merged_video/<video_title>/', get_merged_video, name='get_merged_video'),

    # # Upload transkrip dalam format CSV
    # path('upload_transcript_csv/', upload_transcript_csv, name='upload_transcript_csv'),

    # Merge video
    path('merge_videos/<video_title>/', merge_videos, name='merge_videos'),

    # Delete video
    path('delete_video/<video_title>/', delete_video, name='delete_video'),

    # Halaman editor video
    path('video_editor/<video_title>/', video_editor_page, name='video_editor'),

    # Halaman Upload Video
    path('upload_video_page/', upload_video_page, name='upload_video_page'),

    # Halaman Upload Transkrip
    path('upload_transcript_page/', upload_transcript_page, name='upload_transcript_page'),

    path('', landing_page, name='landing_page'),

    path('folder/<folder_name>/', folder_page, name='folder_page'),

    path('search_video/<folder_name>/', search_videos, name='search_video'),

    path('get_previous_video/<folder_name>/', get_previous_video, name='get_previous_video'),

    path('get_next_status/<folder_name>/<current_title>/', get_next_video_status, name='get_next_status'),

    path('upload_file_page/', upload_file_page, name='upload_file_page'),

    # Data untuk halaman landing
    path('landing_page_data/', landing_page_data, name='landing_page_data'),



    # Autentikasi
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

]