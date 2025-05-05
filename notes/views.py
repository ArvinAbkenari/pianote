from django.shortcuts import render
from users.forms import UserSignupForm, UserSigninForm


# Create your views here.
def notes_view(request):
    signup_form = UserSignupForm()
    return render(request, "notes/sheets.html",{"form": signup_form})