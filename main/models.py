from django.db import models
from django.contrib.auth.models import User
import uuid

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    folder_name = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to="videos/%Y/%m/%d/")
    
    automated_transcript = models.TextField(blank=True, null=True)
    transcript_alignment = models.TextField(blank=True, null=True)
    sibi_sentence = models.TextField(blank=True, null=True)
    potential_problem = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    transcript = models.TextField(blank=True, null=True)  # Optional field
    is_annotated = models.BooleanField(default=False)
    annotated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    merged_video_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
