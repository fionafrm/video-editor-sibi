from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from moviepy import concatenate_videoclips
from django.views.decorators.http import require_http_methods
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
import json
import csv
from .models import Video

@csrf_exempt
def upload_video(request):
    """ Mengunggah video baru """
    if request.method == 'POST' and request.FILES.get('file'):
        video_file = request.FILES['file']
        title = request.POST.get('title') or video_file.name

        file_name = default_storage.save(f'videos/{video_file.name}', ContentFile(video_file.read()))
        video = Video.objects.create(title=title, file=file_name)

        return JsonResponse({'message': 'Video uploaded successfully', 'video_id': video.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def merge_videos(request, video_id):
    """ Menggabungkan video ke-n dan ke-n+1 """
    video = get_object_or_404(Video, id=video_id)
    next_video = Video.objects.filter(id=video_id + 1).first()
    
    if not next_video:
        return JsonResponse({'error': 'Next video not found'}, status=404)
    
    video_path1 = video.file.path
    video_path2 = next_video.file.path
    
    merged_clip = concatenate_videoclips([VideoFileClip(video_path1), VideoFileClip(video_path2)])
    merged_path = f"edited_videos/merged_{video_id}_{video_id+1}.mp4"
    merged_clip.write_videofile(default_storage.path(merged_path), codec="libx264")
    
    return JsonResponse({'message': 'Videos merged successfully', 'merged_video_url': default_storage.url(merged_path)})

@csrf_exempt
def trim_video(request, video_id):
    """ Memotong video berdasarkan waktu mulai dan waktu akhir """
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id)
        input_video_path = video.file.path
        
        data = json.loads(request.body)
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time is None or end_time is None:
            return JsonResponse({'error': 'Invalid start or end time'}, status=400)

        try:
            clip = VideoFileClip(input_video_path)
            trimmed_clip = clip.subclipped(start_time, end_time)
            
            output_path = os.path.join("media/edited_videos", f"trimmed_{video_id}.mp4")
            trimmed_clip.write_videofile(output_path, codec="libx264")

            return JsonResponse({'message': 'Video trimmed successfully', 'trimmed_video_url': output_path})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def save_transcript(request, video_id):
    """ Menyimpan transkrip baru dan komentar baru ke database dan ke file """
    if request.method == 'POST':
        data = json.loads(request.body)
        transcript = data.get('transcript')
        comments = data.get('comments')
        
        video = get_object_or_404(Video, id=video_id)

        if transcript is not None:
            video.transcript = transcript
        if comments is not None:
            video.comments = comments

        video.save()

        # Simpan transcript di file (opsional)
        transcript_dir = os.path.join(settings.MEDIA_ROOT, 'transcripts')
        os.makedirs(transcript_dir, exist_ok=True)
        
        transcript_path = os.path.join(transcript_dir, f'video_{video_id}.txt')
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript or '')

        return JsonResponse({'message': 'Transcript and comments updated successfully'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_video_details(request, video_id):
    """ Mengambil informasi video, transkripnya, dan komennya """
    video = get_object_or_404(Video, id=video_id)
    return JsonResponse({
        'video_url': video.file.url,
        'transcript': video.transcript,
        'comments': video.comments
    })

@csrf_exempt
def upload_transcript_csv(request):
    """ Mengunggah transkrip dari file CSV """
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_path = default_storage.save(f"transcripts/{file.name}", file)

        with default_storage.open(file_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header

            for row in reader:
                video_id, transcript = row[0], row[1]
                video = get_object_or_404(Video, id=video_id)
                video.transcript = transcript
                video.save()

        return JsonResponse({'message': 'Transcript uploaded successfully.'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_video(request, video_id):
    """ Menghapus video beserta file fisiknya """
    video = get_object_or_404(Video, id=video_id)

    # Hapus file video dari storage
    if video.file and video.file.storage.exists(video.file.name):
        video.file.delete()

    # Hapus file transkrip jika ada
    transcript_path = os.path.join(settings.MEDIA_ROOT, 'transcripts', f'video_{video_id}.txt')
    if os.path.exists(transcript_path):
        os.remove(transcript_path)

    # Hapus record di database
    video.delete()

    return JsonResponse({'message': f'Video dengan ID {video_id} berhasil dihapus'})


"""KHUSUS UNTUK PAGE"""

def video_editor_page(request):
    return render(request, 'video_editor.html')

def upload_video_page(request):
    return render(request, 'upload_video.html')



