from django.shortcuts import render
from users.forms import UserSignupForm
# Create your views here.

def exercise_view(request):
    signup_form = UserSignupForm()
    return render(request, "exercise/exercise.html",{"form": signup_form })
