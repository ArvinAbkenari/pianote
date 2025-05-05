from django.db import models
from django.contrib.auth import get_user_model
from bson import ObjectId

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
    createdAt = models.DateTimeField()
    deleteFlag = models.BooleanField(default=False)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.JSONField(default=list)
    notesheet = models.FileField(upload_to='notesheets/', null=True, blank=True)
    audio = models.FileField(upload_to='audio/', null=True, blank=True)
    def add_comment(self, user_id, text, createdDate , delete_flag=False):
        comment = {
            "userID": user_id,
            "text": text,
            "createdAt": createdDate,
            "deleteFlag": delete_flag
        }
        self.comments.append(comment)
        self.save()

    def __str__(self):
        return self.name
    @property
    def level_value(self):
        return dict(self.LEVEL_CHOICES).get(self.level, "Unknown")

@property
def is_authenticated(self):
    return True
