from django import forms
from .models import Auction, Bid
from django.utils import timezone


class AuctionCreateForm(forms.ModelForm):
    duration_hours = forms.IntegerField(min_value=1, initial=24, help_text='Duration in hours', label="مدت زمان (ساعت)")

    class Meta:
        model = Auction
        fields = ['title', 'description', 'image', 'starting_price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'starting_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': "عنوان",
            'description': "توضیحات",
            'image': "تصویر",
            'starting_price': "قیمت اولیه",
        }

    def save(self, seller, commit=True):
        auction = super().save(commit=False)
        auction.seller = seller
        auction.current_price = auction.starting_price
        auction.created_at = timezone.now()
        auction.expires_at = timezone.now() + timezone.timedelta(hours=self.cleaned_data.get('duration_hours', 24))
        if commit:
            auction.save()
        return auction


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control price-input', 'placeholder': 'پیشنهاد خود را وارد کنید'}),
        }

    def clean_amount(self):
        amt = self.cleaned_data.get('amount')
        if amt is None or amt <= 0:
            raise forms.ValidationError('Bid amount must be positive')
        return amt
