from django.db import models
from django.contrib.auth import get_user_model
from bson import ObjectId
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import os

User = get_user_model()



class Note(models.Model):
    LEVEL_CHOICES = [
        (1, "مبتدی"),
        (2, "متوسط"),
        (3, "پیشرفته"),
    ]
    id = models.CharField(max_length=24, primary_key=True, editable=False)
    name = models.CharField(max_length=150)
    genre = models.JSONField()
    composer = models.CharField(max_length=150)
    description = models.TextField(blank= True, null=True)
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    rate = models.FloatField()
    likes = models.IntegerField()
    views = models.IntegerField()
    voters = models.IntegerField()
    createdAt = models.DateTimeField()
    deleteFlag = models.BooleanField(default=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.JSONField(default=list)
    notesheet = models.FileField(upload_to='notesheets/', null=True, blank=True)
    audio = models.FileField(upload_to='audio/', null=True, blank=True)
    preview = models.ImageField(blank=True, null=True, upload_to='notesheets/previews/')
    def add_comment(self, user_id, text, createdDate, delete_flag=False):
        # Convert datetime to ISO string for JSON serialization
        if hasattr(createdDate, 'isoformat'):
            createdDate = createdDate.isoformat()
        comment = {
            "userID": user_id,
            "text": text,
            "createdAt": createdDate,
            "deleteFlag": delete_flag
        }
        self.comments.append(comment)
        self.save()
    @staticmethod
    def generate_pdf_preview(pdf_path, output_path):
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if images:
            image = images[0]
            image.save(output_path, 'PNG')

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Check if notesheet is being added or changed
        is_new = self._state.adding or not self.pk
        old_notesheet = None
        if not is_new and self.pk:
            try:
                old = Note.objects.get(pk=self.pk)
                old_notesheet = old.notesheet
            except Note.DoesNotExist:
                pass
        super().save(*args, **kwargs)

        # Only generate preview if notesheet is present and changed
        if self.notesheet and (is_new or self.notesheet != old_notesheet):
            pdf_path = self.notesheet.path
            # Ensure preview directory exists
            preview_dir = os.path.join('media', 'notesheets', 'previews')
            os.makedirs(preview_dir, exist_ok=True)
            preview_filename = f'{self.pk}_preview.png'
            preview_path = os.path.join(preview_dir, preview_filename)
            try:
                Note.generate_pdf_preview(pdf_path, preview_path)
                self.preview.name = os.path.join('notesheets', 'previews', preview_filename)
                super().save(update_fields=['preview'])
            except Exception as e:
                # Optionally log the error
                pass
        
    
    @property
    def level_value(self):
        return dict(self.LEVEL_CHOICES).get(self.level, "Unknown")

@property
def is_authenticated(self):
    return True
