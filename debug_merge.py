#!/usr/bin/env python
"""
Debug script untuk mengecek masalah merge video
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_editor_sibi.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from main.models import Video

def debug_merge_issue():
    video_title = "TVRI_SB_061119_0052.mp4"
    
    print(f"=== DEBUG MERGE UNTUK {video_title} ===")
    
    # Cek video yang diminta
    try:
        video = Video.objects.get(title=video_title)
        print(f"✅ Video ditemukan: {video.title} (ID: {video.id})")
        print(f"   File path: {video.file}")
        print(f"   Folder: {video.folder_name}")
        print(f"   Merged path: {video.merged_video_path}")
    except Video.DoesNotExist:
        print(f"❌ Video tidak ditemukan: {video_title}")
        return
    
    # Parse nama file
    name_parts = video_title.replace('.mp4', '').split('_')
    print(f"Name parts: {name_parts}")
    
    current_sequence = int(name_parts[-1])  # 0052
    base_title = '_'.join(name_parts[:-1])  # TVRI_SB_061119
    
    print(f"Current sequence: {current_sequence}")
    print(f"Base title: {base_title}")
    
    # Cari video berikutnya
    next_sequence = current_sequence + 1  # 0053
    next_video_title = f"{base_title}_{next_sequence:04d}.mp4"  # TVRI_SB_061119_0053.mp4
    
    print(f"Looking for next video: {next_video_title}")
    
    try:
        next_video = Video.objects.get(title=next_video_title)
        print(f"✅ Video berikutnya ditemukan: {next_video.title} (ID: {next_video.id})")
        print(f"   File path: {next_video.file}")
    except Video.DoesNotExist:
        print(f"❌ Video berikutnya tidak ditemukan: {next_video_title}")
    
    # Cek semua video dengan base yang sama
    print(f"\n=== VIDEO DENGAN BASE '{base_title}' ===")
    similar_videos = Video.objects.filter(title__startswith=base_title).order_by('title')
    for v in similar_videos:
        print(f"  - {v.title}")
    
    print(f"\n=== SEMUA VIDEO DI FOLDER '{video.folder_name}' ===")
    folder_videos = Video.objects.filter(folder_name=video.folder_name).order_by('title')
    for v in folder_videos:
        sequence_num = v.title.replace('.mp4', '').split('_')[-1]
        print(f"  - {v.title} (sequence: {sequence_num})")

if __name__ == "__main__":
    debug_merge_issue()