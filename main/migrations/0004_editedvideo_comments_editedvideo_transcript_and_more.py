# Generated by Django 5.1.6 on 2025-03-24 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_video_transcript'),
    ]

    operations = [
        migrations.AddField(
            model_name='editedvideo',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='editedvideo',
            name='transcript',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Transcript',
        ),
    ]
