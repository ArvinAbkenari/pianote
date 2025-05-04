from django import forms
from .models import User
from bson import ObjectId
from django.utils import timezone

class UserSignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'rePassword', 'email', 'firstName', 'lastName', 'phoneNumber']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'نام کاربری', 'class': 'form-control', 'required': True, }),
            'password': forms.PasswordInput(attrs={'placeholder': 'رمز عبور', 'class': 'form-control', 'required': True, }),
            'rePassword': forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور', 'class': 'form-control', 'required': True,}),
            'email': forms.EmailInput(attrs={'placeholder': 'ایمیل', 'class': 'form-control', 'required': True, 'style': 'direction: rtl;'}),
            'firstName': forms.TextInput(attrs={'placeholder': 'نام', 'class': 'form-control', 'required': True, }),
            'lastName': forms.TextInput(attrs={'placeholder': 'نام خانوادگی', 'class': 'form-control', 'required': True, }),
            'phoneNumber': forms.TextInput(attrs={'placeholder': 'شماره تماس', 'class': 'form-control', 'required': True,}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = ""

    def save(self, commit=True):
        user = super().save(commit=False)
        user.id = str(ObjectId())
        user.createdDate = timezone.now()
        user.premiumDate = timezone.now()
        user.deleteFlag = False
        if commit:
            user.save()
        return user


class UserSigninForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)