from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

from main.models import Video

# Create your views here.
@login_required
def dashboard(request):
    # Total video count
    total_videos = Video.objects.count()
    
    # Total annotations count
    total_annotations = Video.objects.filter(is_annotated=True).count()
    
    # Calculate average video duration (sample first 20 videos for performance)
    videos_sample = Video.objects.all()[:20]  # Limit to first 20 videos for performance
    total_duration = 0
    video_count_with_duration = 0
    
    for video in videos_sample:
        try:
            video_path = video.file.path
            if os.path.exists(video_path):
                clip = VideoFileClip(video_path)
                duration = clip.duration / 60  # Convert to minutes
                total_duration += duration
                video_count_with_duration += 1
                clip.close()  # Close the clip to free memory
        except Exception:
            # Skip videos that can't be processed
            continue
    
    # Calculate average duration in minutes
    avg_duration = round(total_duration / video_count_with_duration, 1) if video_count_with_duration > 0 else 0
    
    # Get recent videos for display
    recent_videos = Video.objects.all().order_by('-created_at')[:12]
    
    context = {
        'total_videos': total_videos,
        'total_annotations': total_annotations,
        'avg_duration': avg_duration,
        'videos': recent_videos
    }
    
    return render(request, "dashboard.html", context)


@login_required
def profile(request):
    user = request.user
    
    # Calculate user-specific statistics
    user_projects = Video.objects.filter(annotated_by=user).count() if user.is_authenticated else 0
    user_annotations = Video.objects.filter(annotated_by=user, is_annotated=True).count() if user.is_authenticated else 0
    
    # Determine role
    if user.is_superuser:
        role = "Admin"
    elif user.is_staff:
        role = "Staff Annotator"
    else:
        role = "Senior Video Annotator"
    
    context = {
        'user': user,
        'role': role,
        'user_projects': user_projects,
        'user_annotations': user_annotations,
    }
    
    return render(request, "profile.html", context)