from django.http import JsonResponse
from django.shortcuts import render
from users.forms import UserSignupForm, UserSigninForm
from .models import Note


# Create your views here.
def notes_view(request):
    signup_form = UserSignupForm()
    notes = Note.objects.filter(deleteFlag=False)
    return render(request, "notes/sheets.html",{"form": signup_form , "notes": notes})


def ajax_search(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        from django.db.models import Q
        notes = Note.objects.filter(
            Q(name__icontains=query)
        )
        results = [{"name": note.name} for note in notes]

    return JsonResponse({"results": results})