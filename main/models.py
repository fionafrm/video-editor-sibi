from django.db import models

# Model untuk menyimpan video yang diunggah dan video preview yang diapprove
class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="videos/")
    transcript = models.TextField(blank=True, null=True)  # Menyimpan transkrip video
    comments = models.TextField(blank=True, null=True)  # Menyimpan komentar penyelarasan (kolom E)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Model untuk preview video yang telah di-edit
class EditedVideo(models.Model):
    original_video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="edited_versions")
    file = models.FileField(upload_to="edited_videos/")
    start_time = models.FloatField(null=True, blank=True)  # Waktu mulai pemotongan
    end_time = models.FloatField(null=True, blank=True)  # Waktu selesai pemotongan
    created_at = models.DateTimeField(auto_now_add=True)
    transcript = models.TextField(blank=True, null=True)  # Menyimpan transkrip video
    comments = models.TextField(blank=True, null=True)  # Menyimpan komentar penyelarasan (kolom E)

    def __str__(self):
        return f"Edited version of {self.original_video.title}"
