from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.models import User
from .forms import UserSignupForm
from .forms import UserSigninForm
# Create your views here.

def homePage(request):
    signup_form = UserSignupForm()
    return render(request, "users/index.html", {"form": signup_form})




def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})  # Return JSON response on success
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)  # Return errors as JSON
    else:
        form = UserSignupForm()
    return render(request, 'users/index.html', {'form': form})




