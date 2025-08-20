from django import forms
from bson import ObjectId

class AudioUploadForm(forms.Form):
    reference_audio = forms.FileField(
        label='بارگذاری قطعه مرجع',
        required=False,
        widget=forms.ClearableFileInput(attrs={'accept': 'audio/*',  'id': 'id_reference_audio'})
    )
    user_audio = forms.FileField(
        label='بارگذاری ضبط تمرین شما',
        required=False,
        widget=forms.ClearableFileInput(attrs={'accept': 'audio/*',  'id': 'id_user_audio'})
    )
    
    
from django import forms
from .models import Exercise

class ExerciseCreateForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "عنوان تمرین",
                    "class": "auth-input",  # or form-control if that’s your CSS
                    "id": "title",
                    "dir": "auto",
                }
            )
        }
        labels = {
            "title": "",
        }
        
    def save(self, commit=True):
        exercise = super().save(commit=False)
        exercise.id = str(ObjectId())
        exercise.deleteFlag = False
        if commit:
            exercise.save()
        return exercise
