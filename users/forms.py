from django import forms
from .models import User
from bson import ObjectId
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

class UserSignupForm(forms.ModelForm):
    rePassword = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'تکرار رمز عبور', 'class': 'form-control', 'required': True
        })
    )

    class Meta:
        model = User
        fields = ['password', 'email', 'fullName', 'phoneNumber']
        widgets = {
            'password': forms.PasswordInput(attrs={
                'placeholder': 'رمز عبور', 'class': 'form-control', 'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'ایمیل', 'class': 'form-control', 'required': True, 'style': 'direction: rtl;'
            }),
            'fullName': forms.TextInput(attrs={
                'placeholder': 'نام', 'class': 'form-control', 'required': True
            }),
            'phoneNumber': forms.TextInput(attrs={
                'placeholder': 'شماره تماس', 'class': 'form-control', 'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = ""

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("این ایمیل قبلاً ثبت شده است.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("رمز عبور باید حداقل ۸ کاراکتر باشد.")
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("رمز عبور باید حداقل شامل یک حرف باشد.")
        if not re.search(r'\d', password):
            raise ValidationError("رمز عبور باید حداقل شامل یک عدد باشد.")
        return password

    def clean_phoneNumber(self):
        phone_number = self.cleaned_data.get('phoneNumber')
        if not re.match(r'^09\d{9}$', phone_number):
            raise ValidationError("شماره تماس باید یک شماره معتبر ایرانی باشد.")
        return phone_number
    def clean_fullName(self):
        full_name = self.cleaned_data.get('fullName')
        
        # Check if the name contains any digits
        if re.search(r'\d', full_name):
            raise ValidationError("نام نمی‌تواند شامل اعداد باشد.")

        return full_name

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("rePassword")

        if password and re_password and password != re_password:
            raise ValidationError("رمز عبور و تکرار آن یکسان نیستند.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.id = str(ObjectId())
        user.password = make_password(self.cleaned_data['password'])
        user.createdDate = timezone.now()
        user.premiumDate = timezone.now()
        user.isSuperUser = False
        user.deleteFlag = False
        if commit:
            user.save()
        return user


class UserSigninForm(forms.Form):
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("کاربری با این ایمیل یافت نشد.")

        if not check_password(password, user.password):
            raise ValidationError("رمز عبور اشتباه است.")

        self.user = user

        return cleaned_data