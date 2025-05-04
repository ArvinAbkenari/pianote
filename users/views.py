from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.models import User
from .forms import UserSignupForm
from .forms import UserSigninForm

def homePage(request):
    signup_form = UserSignupForm()
    return render(request, "users/index.html", {"form": signup_form})




def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True}) 
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400) 
    else:
        form = UserSignupForm()
    return render(request, 'users/index.html', {'form': form})



def signin_view(request):
    if request.method == 'POST':
        form = UserSigninForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email, password=password)
                request.session['user_id'] = user.id  
                return JsonResponse({'success': True})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


