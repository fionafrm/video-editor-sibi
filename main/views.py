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
from .models import Video
import logging
from collections import defaultdict


@csrf_exempt
@login_required
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

@csrf_exempt
@login_required
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
@login_required
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
@login_required
def save_transcript(request, video_title):
    if request.method == 'POST':
        data = json.loads(request.body)
        video = get_object_or_404(Video, title=video_title)

        transcript_alignment = data.get('transcript_alignment')
        sibi_sentence = data.get('sibi_sentence')
        potential_problem = data.get('potential_problem')
        comment = data.get('comment')

        if transcript_alignment is not None:
            video.transcript_alignment = transcript_alignment
        if sibi_sentence is not None:
            video.sibi_sentence = sibi_sentence
        if potential_problem is not None:
            video.potential_problem = potential_problem
        if comment is not None:
            video.comment = comment

        video.is_annotated = True
        video.annotated_by = request.user
        video.save()

        return JsonResponse({'message': 'Data disimpan'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def get_video_details(request, video_title):
    """ Mengambil informasi video, transkripnya, dan komennya """
    video = get_object_or_404(Video, title=video_title)
    return JsonResponse({
        'video_url': video.file.url ,
        'transcript': video.transcript,
        'comment': video.comment
    })

@csrf_exempt
@login_required
def get_merged_video(request, video_title):
    video = get_object_or_404(Video, title=video_title)

    if video.merged_video_path and default_storage.exists(video.merged_video_path):
        merged_video_url = default_storage.url(video.merged_video_path)
        return JsonResponse({
            'merged_video_url': merged_video_url,
            'transcript': video.transcript,
            'comment': video.comment
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
            'comment': video.comment
        })

    # Kalau merge gagal, return responsenya langsung
    return merge_response

@csrf_exempt
@login_required
def get_next_video_status(request, folder_name, current_title):
    videos = Video.objects.filter(folder_name=folder_name, is_annotated=False).order_by('title')

    for video in videos:
        if video.title != current_title:
            return JsonResponse({'has_next': True})
    
    return JsonResponse({'has_next': False})


@csrf_exempt
@login_required
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
@login_required
def upload_file(request):
    """Mengunggah file Excel dengan link Google Drive di hyperlink kolom A"""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        ext = file.name.split('.')[-1]
        tmp_path = default_storage.save(f"temp/{file.name}", file)

        try:
            import pandas as pd
            import requests
            import re
            import openpyxl
            from io import BytesIO
            from django.contrib.auth.models import User

            file_path = default_storage.path(tmp_path)

            # Baca isi tabel ke DataFrame
            df = pd.read_excel(file_path)

            # Baca workbook untuk ambil hyperlink kolom A
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active

            # Ambil hyperlink dari kolom A (A2, A3, ...)
            drive_links = []
            for row in ws.iter_rows(min_row=2):  # skip header
                cell = row[0]  # kolom A
                link = cell.hyperlink.target if cell.hyperlink else (cell.value or "")
                drive_links.append(link)

            count = 1
            for idx, row in df.iterrows():
                try:
                    link = str(drive_links[idx]).strip()
                    video_title_raw = str(row['Nama Data']).strip()

                    if not link or 'drive.google.com' not in link or not video_title_raw:
                        print(f"[SKIP] Baris {idx+2}: link/video_title kosong atau invalid.")
                        continue

                    video_title = f"{video_title_raw}.mp4"
                    folder_name = "_".join(video_title_raw.split("_")[:-1])

                    # Ambil metadata lain
                    automated_transcript = str(row.get('Transkripsi Suara secara Otomatis oleh Sistem', '')).strip()
                    transcript_alignment = str(row.get('Penyelarasan Suara/Teks Transkripsi dan Gerakan Bahasa Isyarat', '')).strip()
                    sibi_sentence = str(row.get('Kalimat yang Diperagakan', '')).strip()
                    potential_problem = str(row.get('Potensi Masalah', '')).strip()
                    comment = str(row.get('Keterangan Annotator', '')).strip()
                    username = str(row.get('Nama Annotator', '')).strip()
                    is_annotated = str(row.get('Hasil Alignment (NEW)', '')).strip().lower() in ['1', 'true', 'yes']

                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user = None

                    # Ambil file ID dari link
                    match = re.search(r'/d/([^/]+)', link)
                    if not match:
                        print(f"[SKIP] Baris {idx+2}: Gagal ekstrak file ID dari link")
                        continue
                    file_id = match.group(1)
                    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

                    # Unduh video
                    response = requests.get(download_url)
                    if response.status_code != 200:
                        print(f"[SKIP] Baris {idx+2}: Gagal download video (status {response.status_code})")
                        continue

                    # Simpan ke folder yang sesuai
                    videos_dir = os.path.join('videos', folder_name)
                    raw_dir = os.path.join('raw_videos', folder_name)
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, videos_dir), exist_ok=True)
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, raw_dir), exist_ok=True)

                    final_video_path = os.path.join(videos_dir, video_title)
                    raw_video_path = os.path.join(raw_dir, video_title)

                    final_path = default_storage.save(final_video_path, ContentFile(response.content))
                    default_storage.save(raw_video_path, ContentFile(response.content))

                    # Simpan ke DB
                    Video.objects.create(
                        title=video_title,
                        folder_name=folder_name,
                        file=final_path,
                        automated_transcript=automated_transcript,
                        transcript_alignment=transcript_alignment,
                        sibi_sentence=sibi_sentence,
                        potential_problem=potential_problem,
                        comment=comment,
                        annotated_by=user,
                        is_annotated=is_annotated
                    )

                    count += 1

                except Exception as e:
                    print(f"[ERROR] Baris {idx+2}: {str(e)}")

            return JsonResponse({'message': f'Upload selesai. {count-1} video diproses.'})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)



@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
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
@login_required
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
@login_required
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
        referral_code = request.POST.get('referral', '').strip()

        ADMIN_CODE = 'RAHASIAADMIN2025' # Referral untuk admin

        if form.is_valid():
            user = form.save(commit=False)

            if referral_code == ADMIN_CODE:
                user.is_staff = True
                user.is_superuser = True
                role_msg = 'Admin'
            else:
                user.is_staff = False
                user.is_superuser = False
                role_msg = 'Annotator'

            user.save()
            messages.success(request, f'Akun berhasil dibuat sebagai {role_msg}!')
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

@csrf_exempt
@login_required
def landing_page(request):
    """ Menampilkan halaman landing page dengan folder-folder """
    all_videos = Video.objects.all()
    folder_dict = defaultdict(list)

    # Kelompokkan video berdasarkan folder_name
    for video in all_videos:
        folder_dict[video.folder_name].append(video)

    # Buat list folder dengan status annotasi
    folder_info = []
    for folder_name, videos in folder_dict.items():
        total = len(videos)
        annotated = sum(1 for v in videos if v.is_annotated)
        # Untuk display nama folder
        parts = folder_name.split('_')
        lembaga = parts[0]
        jenis = 'SIBI' if parts[1] == 'SB' else parts[1]
        tanggal_str = parts[2]  # e.g: 290120

        # Formating tanggal
        day = tanggal_str[0:2]
        month = tanggal_str[2:4]
        year = '20' + tanggal_str[4:6]
        tanggal_format = f"{day}/{month}/{year}"
        display_name = f'{lembaga} - {jenis} - {tanggal_format}'

        # display_name = format_folder_display(folder_name)
        all_done = (annotated == total)
        folder_info.append({
            'name': folder_name,
            'annotated': annotated,
            'total': total,
            'all_done': all_done,
            'display_name': display_name
        })

    return render(request, 'landing_page.html', {'folders': folder_info})

@csrf_exempt
@login_required
def folder_page(request, folder_name):
    """ Menampilkan halaman folder dengan daftar video di dalamnya """
    videos = Video.objects.filter(folder_name=folder_name)
    # display_name = format_folder_display(folder_name)
    
    return render(request, 'folder_page.html', {'folder_name': folder_name, 'videos': videos})

@csrf_exempt
@login_required
def video_editor_page(request, video_title):
    video = get_object_or_404(Video, title=video_title)

    context = {
        'video': video,
        'automated_transcript': video.automated_transcript,
        'transcript_alignment': video.transcript_alignment,
        'sibi_sentence': video.sibi_sentence,
        'potential_problem': video.potential_problem,
        'comment': video.comment,
        'annotated_by': video.annotated_by.username if video.annotated_by else '-',
        'is_annotated': video.is_annotated,
        'created_at': video.created_at,
    }

    return render(request, 'video_editor.html', context)

@csrf_exempt
@login_required
def upload_video_page(request):
    return render(request, 'upload_video.html')

@csrf_exempt
@login_required
def upload_transcript_page(request):
    return render(request, 'upload_transcript.html')

@csrf_exempt
@login_required
def upload_file_page(request):
    if not request.user.is_superuser:
        return redirect('landing_page')
    return render(request, 'upload_file.html')

# ENHANCED USER INTERFACE

@csrf_exempt
@login_required
def format_folder_display(name):
    """ Format nama folder untuk tampilan yang lebih user-friendly """
    try:
        parts = name.split('_')
        lembaga = parts[0]
        jenis = 'SIBI' if parts[1] == 'SB' else parts[1]
        tanggal_str = parts[2]  # e.g: 290120

        # Formating tanggal
        day = tanggal_str[0:2]
        month = tanggal_str[2:4]
        year = '20' + tanggal_str[4:6]
        tanggal_format = f"{day}/{month}/{year}"

        return f'{lembaga} - {jenis} - {tanggal_format}'
    except Exception:
        return name # Kalo misalnya format namanya ga sesuai

@csrf_exempt
@login_required
def landing_page_data(request):
    """ Menampilkan halaman landing page dengan folder-folder """
    all_videos = Video.objects.all()
    folder_dict = defaultdict(list)

    # Kelompokkan video berdasarkan folder_name
    for video in all_videos:
        folder_dict[video.folder_name].append(video)

    # Buat list folder dengan status annotasi
    folder_info = []
    for folder_name, videos in folder_dict.items():
        total = len(videos)
        annotated = sum(1 for v in videos if v.is_annotated)
        # display_name = format_folder_display(str(folder_name))
        all_done = (annotated == total)
        folder_info.append({
            'name': folder_name,
            'annotated': annotated,
            'total': total,
            'all_done': all_done,
            # 'display_name': display_name,
        })

    return JsonResponse({
        'folders': [
            {
                'name': folder['name'],
                'annotated': folder['annotated'],
                'total': folder['total'],
                'all_done': folder['all_done'],
                # 'display_name': folder['display_name'],
            } for folder in folder_info
        ]
    })