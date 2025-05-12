from django.db import models
from django.contrib.auth.models import User
import uuid

# Model untuk menyimpan video yang diunggah dan video preview yang diapprove
class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    folder_name = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to=f"videos/{folder_name}/")
    transcript = models.TextField(blank=True, null=True)  # Menyimpan transkrip video
    comments = models.TextField(blank=True, null=True)  # Menyimpan komentar penyelarasan (kolom E)
    created_at = models.DateTimeField(auto_now_add=True)
    is_annotated = models.BooleanField(default=False)
    annotated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    merged_video_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

# Model untuk preview video yang telah di-edit
class EditedVideo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="edited_versions")
    folder_name = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to=f"edited_videos/{folder_name}/")
    created_at = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField(blank=True, null=True)  # Menyimpan transkrip video
    comments = models.TextField(blank=True, null=True)  # Menyimpan komentar penyelarasan (kolom E)
    is_annotated = models.BooleanField(default=False)
    annotated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Edited version of {self.original_video.title}"
