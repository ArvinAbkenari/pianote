
# Create your models here.

from django.db import models
from bson import ObjectId

class User(models.Model):
    id = models.CharField(max_length=24, primary_key=True, editable=False)
    fullName = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    rePassword = models.CharField(max_length=128)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=20)
    premiumDate = models.DateTimeField()
    createdDate = models.DateTimeField()
    isSuperUser = models.BooleanField(default=False)
    deleteFlag = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.username

@property
def is_authenticated(self):
    return True