from django.shortcuts import render
from users.forms import UserSignupForm
# Create your views here.

def estimator_view(request):
    signup_form = UserSignupForm()
    return render(request, "estimator/estimator.html",{"form": signup_form })
