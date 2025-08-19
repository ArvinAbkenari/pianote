from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from users.models import User
from .forms import UserSignupForm
from .forms import UserSigninForm
from functools import wraps


def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return render(request, 'users/index.html', {
                "show_signin_toast": True,
                "redirect_to_signin": True,
                "form": UserSignupForm()
            })
        return view_func(request, *args, **kwargs)
    return _wrapped_view


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
            user = form.user
            request.session['user_id'] = user.id 
            request.session['fullName'] = user.fullName.split()[0]
            return JsonResponse({'success': True, 'reload': True}) 
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


def logout_view(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('HomePage'))


@session_login_required
def aboutus_view(request):
    signup_form = UserSignupForm()
    return render(request, "about-us/contact.html",{"form": signup_form})