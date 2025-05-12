from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from moviepy import concatenate_videoclips
from django.views.decorators.http import require_http_methods
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
import json
import csv
from .models import Video, EditedVideo
import logging

@csrf_exempt
def upload_video(request):
    """ Mengunggah video baru """
    if request.method == 'POST' and request.FILES.get('file'):
        video_file = request.FILES['file'].read()
        folder_name = request.POST.get('folder_name')
        video_title = request.POST.get('video_title')
        
        video_filename = f"{folder_name}_{video_title}.mp4"
        
        raw_video_folder = os.path.join('raw_videos', folder_name)
        video_folder = os.path.join('videos', folder_name)
        
        # Ensure the subdirectories exist
        os.makedirs(os.path.join(settings.MEDIA_ROOT, raw_video_folder), exist_ok=True)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, video_folder), exist_ok=True)
        
        raw_video_path = os.path.join(raw_video_folder, video_filename)
        raw_video_file = default_storage.save(raw_video_path, ContentFile(video_file))
        
        video_path = os.path.join(video_folder, video_filename)
        video_file_new = default_storage.save(video_path, ContentFile(video_file))

        video = Video.objects.create(title=video_filename, file=video_file_new, folder_name=folder_name)

        return JsonResponse({'message': 'Video uploaded successfully', 'video_title': video_title})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


logger = logging.getLogger(__name__)

# @csrf_exempt
# def merge_videos(request, video_title):
#     """ Menggabungkan video berdasarkan video_title yang memiliki urutan """
#     try:
#         # Get the current video based on video_title
#         video = get_object_or_404(Video, title=video_title)

#         # Extract sequence number from video_title (e.g., 'nameFolder_0001.mp4')
#         current_sequence = int(video_title.split('_')[-1].replace('.mp4', ''))

#         # Find the next video with the next sequence
#         next_video_title = f"{'_'.join(video_title.split('_')[:-1])}_{current_sequence + 1}.mp4"
#         next_video = Video.objects.filter(title=next_video_title).first()

#         if not next_video:
#             # If there is no next video, consider this as the last video
#             next_video = video
#             next_video_title = video_title

#         # Get the file paths for both videos
#         video_path1 = video.file.path
#         video_path2 = next_video.file.path

#         # Log the paths to make sure they're correct
#         logger.info(f"Merging videos: {video_path1} and {video_path2}")

#         # Concatenate video clips using moviepy
#         merged_clip = concatenate_videoclips([VideoFileClip(video_path1), VideoFileClip(video_path2)])

#         # Define the path for the merged video
#         merged_video_filename = f"merged_{video_title}_{next_video_title}.mp4"
#         merged_path = os.path.join('edited_videos', merged_video_filename)

#         # Ensure the edited_videos directory exists
#         os.makedirs(os.path.join(settings.MEDIA_ROOT, 'edited_videos'), exist_ok=True)

#         # Write the merged video to file
#         merged_clip.write_videofile(default_storage.path(merged_path), codec="libx264")

#         # Save the merged video path to the database
#         video.merged_video_path = merged_path
#         video.save()

#         # Return the URL of the merged video
#         return JsonResponse({'message': 'Videos merged successfully', 'merged_video_url': default_storage.url(merged_path), 'video_title' : video_title})

#     except Exception as e:
#         # Log any error that occurs
#         logger.error(f"Error in merging videos: {str(e)}")
#         return JsonResponse({'error': f"Error merging videos: {str(e)}"}, status=500)

@csrf_exempt
def merge_videos(request, video_title):
    """ Menggabungkan video dengan video selanjutnya (berdasarkan urutan nama) """
    try:
        # Ambil video saat ini
        video = get_object_or_404(Video, title=video_title)

        # Ekstrak sequence dari nama file, misal: "29_Januari_2020_0001.mp4"
        name_parts = video_title.replace('.mp4', '').split('_')
        current_sequence = int(name_parts[-1])
        base_title = '_'.join(name_parts[:-1])

        # Buat nama video berikutnya
        next_sequence = current_sequence + 1
        next_video_title = f"{base_title}_{next_sequence:04d}.mp4"

        # Coba ambil video berikutnya dari database
        next_video = Video.objects.filter(title=next_video_title).first()

        if not next_video:
            return JsonResponse({'error': f'Tidak ditemukan video selanjutnya: {next_video_title}'}, status=404)

        # Dapatkan path file kedua video
        path1 = video.file.path
        path2 = next_video.file.path

        logger.info(f"Merging {path1} + {path2}")

        # Gabungkan menggunakan moviepy
        clip1 = VideoFileClip(path1)
        clip2 = VideoFileClip(path2)
        merged_clip = concatenate_videoclips([clip1, clip2])

        # Simpan hasil merge
        merged_filename = f"merged_{video_title.replace('.mp4','')}_{next_video_title}"
        merged_path = os.path.join('edited_videos', merged_filename)

        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'edited_videos'), exist_ok=True)
        merged_clip.write_videofile(default_storage.path(merged_path), codec="libx264")

        # Simpan path ke model
        video.merged_video_path = merged_path
        video.save()

        return JsonResponse({
            'message': 'Video berhasil digabung.',
            'merged_video_url': default_storage.url(merged_path)
        })

    except Exception as e:
        logger.error(f"Error in merging videos: {str(e)}")
        return JsonResponse({'error': f"Error saat menggabungkan video: {str(e)}"}, status=500)


@csrf_exempt
def trim_video(request, video_title):
    if request.method == 'POST':
        video = get_object_or_404(Video, title=video_title)

        # Ambil path video mentah
        raw_path = os.path.join(settings.MEDIA_ROOT, 'raw_videos', video.folder_name, video.title)

        data = json.loads(request.body)
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time is None or end_time is None:
            return JsonResponse({'error': 'Invalid start or end time'}, status=400)

        try:
            clip = VideoFileClip(raw_path)
            duration = clip.duration

            if end_time > duration:
                end_time = duration - 0.01

            if start_time >= end_time:
                return JsonResponse({'error': 'Invalid time range'}, status=400)

            trimmed_clip = clip.subclipped(start_time, end_time)

            # Simpan ke file final (overwrite video "cleaned")
            final_output_path = video.file.path
            trimmed_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac")

            return JsonResponse({
                'message': 'Video trimmed and saved successfully.',
                'trimmed_video_url': video.file.url
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def save_transcript(request, video_title):
    if request.method == 'POST':
        data = json.loads(request.body)
        transcript = data.get('transcript')
        comments = data.get('comments')

        video = get_object_or_404(Video, title=video_title)

        if transcript is not None:
            video.transcript = transcript
        if comments is not None:
            video.comments = comments

        # ✅ Tandai sebagai sudah dianotasi
        video.is_annotated = True
        video.annotated_by = request.user
        video.save()

        # Simpan transkrip juga ke file (opsional)
        transcript_dir = os.path.join(settings.MEDIA_ROOT, 'transcripts')
        os.makedirs(transcript_dir, exist_ok=True)

        transcript_path = os.path.join(transcript_dir, f'video_{video.id}.txt')
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcript or '')

        return JsonResponse({'message': 'Transcript and comments updated successfully'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def get_video_details(request, video_title):
    """ Mengambil informasi video, transkripnya, dan komennya """
    video = get_object_or_404(Video, title=video_title)
    return JsonResponse({
        'video_url': video.file.url ,
        'transcript': video.transcript,
        'comments': video.comments
    })

def get_merged_video(request, video_title):
    video = get_object_or_404(Video, title=video_title)

    if video.merged_video_path and default_storage.exists(video.merged_video_path):
        merged_video_url = default_storage.url(video.merged_video_path)
        return JsonResponse({
            'merged_video_url': merged_video_url,
            'transcript': video.transcript,
            'comments': video.comments
        })

    # Jika belum ada hasil merge, lakukan merge dulu
    merge_response = merge_videos(request, video_title)

    # Kalau sukses (status 200), ambil ulang video dan balikan URL-nya
    if merge_response.status_code == 200:
        video.refresh_from_db()  # Pastikan ambil data terbaru dari DB
        merged_video_url = default_storage.url(video.merged_video_path)
        return JsonResponse({
            'merged_video_url': merged_video_url,
            'transcript': video.transcript,
            'comments': video.comments
        })

    # Kalau merge gagal, return responsenya langsung
    return merge_response

@csrf_exempt
def get_next_video_status(request, folder_name, current_title):
    videos = Video.objects.filter(folder_name=folder_name, is_annotated=False).order_by('title')

    for video in videos:
        if video.title != current_title:
            return JsonResponse({'has_next': True})
    
    return JsonResponse({'has_next': False})


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
                video_id_title, transcript = row[0], row[1]
                last_4_digits = f"{int(video_id_title):04d}"
                try:
                    video = get_object_or_404(Video, title__endswith=f"{last_4_digits}.mp4")
                    video.transcript = transcript
                    video.save()
                except Exception as e:
                    # Debugging: Catch any exceptions and print the error
                    print(f"Error for video_id: {video_id_title} - {str(e)}")

        return JsonResponse({'message': 'Transcript uploaded successfully.'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_video(request, video_title):
    """ Menghapus video beserta file fisiknya """
    video = get_object_or_404(Video, title=video_title)

    # Hapus file video dari storage
    if video.file and video.file.storage.exists(video.file.name):
        video.file.delete()

    # Hapus file transkrip jika ada
    transcript_path = os.path.join(settings.MEDIA_ROOT, 'transcripts', f'video_{video_title}.txt')
    if os.path.exists(transcript_path):
        os.remove(transcript_path)

    # Hapus record di database
    video.delete()

    return JsonResponse({'message': f'Video dengan ID {video_title} berhasil dihapus'})


@csrf_exempt
# @login_required
def search_videos(request, folder_name):
    # Ambil semua video dalam folder, urutkan berdasarkan nama
    videos = Video.objects.filter(folder_name=folder_name).order_by('title')

    for video in videos:
        if not video.is_annotated:
            return redirect('video_editor', video_title=video.title)

    # Jika semua sudah dianotasi, redirect ke folder_page
    messages.info(request, 'Semua video sudah dianotasi.')
    return redirect('folder_page', folder_name=folder_name)

@csrf_exempt
def get_previous_video(request, folder_name):
    user = request.user
    # Cari video yang sudah dianotasi oleh user dan urutkan mundur
    videos = Video.objects.filter(folder_name=folder_name, is_annotated=True, annotated_by=user).order_by('-created_at')

    if videos.exists():
        return JsonResponse({'previous_video_title': videos.first().title})
    return JsonResponse({'previous_video_title': None})

"""AUTENTIKASI"""

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('landing_page')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

"""KHUSUS UNTUK PAGE"""

def landing_page(request):
    """ Menampilkan halaman landing page dengan folder-folder """
    folders = set(Video.objects.values_list('folder_name', flat=True))
    
    return render(request, 'landing_page.html', {'folders': folders})

def folder_page(request, folder_name):
    """ Menampilkan halaman folder dengan daftar video di dalamnya """
    videos = Video.objects.filter(folder_name=folder_name)
    
    return render(request, 'folder_page.html', {'folder_name': folder_name, 'videos': videos})

def video_editor_page(request, video_title):
    video = get_object_or_404(Video, title=video_title)
    return render(request, 'video_editor.html', {'video': video})

def upload_video_page(request):
    return render(request, 'upload_video.html')

def upload_transcript_page(request):
    return render(request, 'upload_transcript.html')
