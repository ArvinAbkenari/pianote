from django import forms

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
