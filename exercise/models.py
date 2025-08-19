from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()
# Create your models here.
class excercise(models.Model):
    id = models.CharField(max_length=24, primary_key=True, editable=False)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    metrics = models.JSONField(default=list)
    audio = models.CharField(max_length=255, blank=True, null=True, help_text="Path to user's audio file (e.g. 'userId_filename.wav')")
    ref_audio = models.CharField(max_length=255, blank=True, null=True, help_text="Path to reference audio file (e.g. 'ref_audio_name')")
    
    
    def add_metrics(self, pitch_score, tempo_score, energy_score , final_score, createdDate, delete_flag=False):
        if hasattr(createdDate, 'isoformat'):
            createdDate = createdDate.isoformat()
        metric = {
            "pitch_score": pitch_score,
            "tempo_score": tempo_score,
            "energy_score": energy_score,
            "final_score": final_score,
            "createdAt": createdDate,
            "deleteFlag": delete_flag
        }
        self.metrics.append(metric)
        self.save()
