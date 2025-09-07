from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class Exercise(models.Model):
    id = models.CharField(max_length=24, primary_key=True, editable=False)
    title = models.CharField(max_length=255, null=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    metrics = models.JSONField(default=list)
    deleteFlag = models.BooleanField(default=False)

    def add_metrics(self, pitch_score, tempo_score, energy_score,
                    final_score, createdDate, delete_flag=False):
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
